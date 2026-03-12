import customtkinter as ctk
import pyperclip
import database
import json
import shutil
import sys
import os
from tkinter import messagebox, filedialog

ctk.set_appearance_mode("dark")

def _get_icon_path() -> str | None:
    """
    Resolve icon.ico whether running from source or as a PyInstaller exe.
    PyInstaller unpacks bundled data to sys._MEIPASS at runtime.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "icon.ico")
    return path if os.path.exists(path) else None

PANEL_W_DEFAULT = 220
PANEL_W_MIN     = 160
PANEL_W_MAX     = 420
SNAP_THIN       = 5    # collapsed edge strip thickness
SNAP_THRESHOLD  = 40   # px from edge to trigger snap on drag-release


# ══════════════════════════════════════════════════════════════════════════════
#  TOASTS
# ══════════════════════════════════════════════════════════════════════════════

class _BaseToast(ctk.CTkToplevel):
    """Shared fade logic for all toasts."""

    def _fade(self, start: float, end: float, step_ms: int, callback=None):
        steps = 14
        delta = (end - start) / steps

        def tick(alpha: float, step: int):
            alpha = round(alpha + delta, 3)
            try:
                self.attributes("-alpha", max(0.0, min(1.0, alpha)))
            except Exception:
                return
            if step < steps:
                self.after(step_ms, lambda: tick(alpha, step + 1))
            elif callback:
                callback()

        tick(start, 0)

    def _close(self):
        try:
            self.destroy()
        except Exception:
            pass

    def _place_near(self, parent):
        self.update_idletasks()
        tw = max(self.winfo_width(), 1)
        tx = parent.winfo_x() + parent.winfo_width() // 2 - tw // 2
        ty = parent.winfo_y() + 38
        self.geometry(f"+{tx}+{ty}")


class Toast(_BaseToast):
    """Subtle, self-dismissing notification."""

    def __init__(self, parent, message: str, duration: int = 1100):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#1C1E20")
        self.resizable(False, False)

        ctk.CTkLabel(
            self, text=message,
            font=("Consolas", 10), text_color="#888888",
            padx=14, pady=5
        ).pack()

        self._place_near(parent)
        self._fade(0.0, 0.72, 18,
                   lambda: self.after(duration, lambda: self._fade(0.72, 0.0, 28, self._close)))


class UndoToast(_BaseToast):
    """Delete notification with a clickable UNDO action."""

    def __init__(self, parent, on_undo, duration: int = 4000):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#1C1E20")
        self._triggered = False

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=14, pady=7)

        ctk.CTkLabel(row, text="Deleted",
                     font=("Consolas", 10), text_color="#606060").pack(side="left", padx=(0, 10))

        undo_lbl = ctk.CTkLabel(row, text="UNDO",
                                font=("Consolas", 10, "bold"),
                                text_color="#FF007F", cursor="hand2")
        undo_lbl.pack(side="left")
        undo_lbl.bind("<Button-1>", lambda _e: self._undo(on_undo))

        self._place_near(parent)
        self._fade(0.0, 0.88, 18, None)
        self.after(duration, self._auto_dismiss)

    def _undo(self, callback):
        if not self._triggered:
            self._triggered = True
            callback()
            self._close()

    def _auto_dismiss(self):
        if not self._triggered:
            self._fade(0.88, 0.0, 28, self._close)


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent: "QuickNotesApp"):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("310x460")
        self.attributes("-topmost", True)
        self.configure(fg_color="#1A1C1E")
        self.resizable(False, False)

        # ── Opacity ──────────────────────────────────────────────
        ctk.CTkLabel(self, text="Opacity", font=("Segoe UI", 12)).pack(pady=(18, 0))
        self.slider = ctk.CTkSlider(
            self, from_=0.2, to=1.0,
            button_color="#FF007F", command=self._update_opacity
        )
        self.slider.set(parent.settings.get("transparency", 0.85))
        self.slider.pack(pady=(4, 12), padx=20)

        # ── Auto-hide ─────────────────────────────────────────────
        self.hide_sw = ctk.CTkSwitch(
            self, text="Auto-hide to edge",
            progress_color="#FF007F", command=self._toggle_hide
        )
        if parent.settings.get("auto_hide"):
            self.hide_sw.select()
        self.hide_sw.pack(pady=4)

        # ── Snap Position ─────────────────────────────────────────
        _sep(self)
        ctk.CTkLabel(self, text="Snap Position",
                     font=("Segoe UI", 11), text_color="#888888").pack(pady=(0, 4))
        snap_row = ctk.CTkFrame(self, fg_color="transparent")
        snap_row.pack()
        self.snap_var = ctk.StringVar(value=parent.settings.get("snap_position", "right"))
        # "top" removed; "floating" added
        for pos in ("left", "right", "floating"):
            ctk.CTkRadioButton(
                snap_row, text=pos.capitalize(),
                variable=self.snap_var, value=pos,
                fg_color="#FF007F",
                border_color="#555555",
                hover_color="#CC005F",
                command=self._update_snap
            ).pack(side="left", padx=5)

        # ── Export / Import ───────────────────────────────────────
        _sep(self)
        ctk.CTkLabel(self, text="Data",
                     font=("Segoe UI", 11), text_color="#888888").pack(pady=(0, 6))
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="Export Snippets", width=126,
                      fg_color="#2D2F31", hover_color="#3A3C3E",
                      command=self._export).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Import Snippets", width=126,
                      fg_color="#2D2F31", hover_color="#3A3C3E",
                      command=self._import).pack(side="left", padx=5)

        ctk.CTkButton(self, text="Close", fg_color="#2D2F31",
                      height=30, command=self.destroy).pack(pady=22)

    # ── callbacks ─────────────────────────────────────────────────
    def _update_opacity(self, value):
        v = float(value)
        self.parent.settings["transparency"] = v
        self.parent.attributes("-alpha", v)
        database.save_json(database.SETTINGS_FILE, self.parent.settings)

    def _toggle_hide(self):
        self.parent.settings["auto_hide"] = bool(self.hide_sw.get())
        database.save_json(database.SETTINGS_FILE, self.parent.settings)

    def _update_snap(self):
        pos = self.snap_var.get()
        self.parent.settings["snap_position"] = pos
        database.save_json(database.SETTINGS_FILE, self.parent.settings)
        self.parent.apply_snap(pos)

    def _export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="neon_notes_backup.json",
            title="Export Snippets"
        )
        if path:
            try:
                shutil.copy(database.SNIPPETS_FILE, path)
                Toast(self.parent, "Exported ✓")
            except Exception as exc:
                messagebox.showerror("Export Error", str(exc))

    def _import(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Snippets"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("File is not a snippet list.")
            database.save_json(database.SNIPPETS_FILE, data)
            self.parent.refresh_ui()
            Toast(self.parent, "Imported ✓")
        except Exception as exc:
            messagebox.showerror("Import Error", str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  EDIT WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class EditWindow(ctk.CTkToplevel):
    def __init__(self, parent: "QuickNotesApp", snippet_data: dict,
                 index: int, is_new: bool = False):
        super().__init__(parent)
        self.parent  = parent
        self.index   = index
        self.is_new  = is_new
        self.title("New Note" if is_new else "Edit Note")
        self.geometry("360x430")
        self.attributes("-topmost", True)
        self.configure(fg_color="#1A1C1E")
        self.resizable(False, False)

        _field_label(self, "Title")
        self.e_title = _entry(self, "Note title", snippet_data.get("title", ""))

        _field_label(self, "Category")
        self.e_cat = _entry(self, "e.g. Work, SQL, Personal",
                            snippet_data.get("category", "General"))

        _field_label(self, "Content")
        self.textbox = ctk.CTkTextbox(self, fg_color="#2D2F31", border_width=0,
                                      font=("Consolas", 11))
        self.textbox.insert("1.0", snippet_data.get("content", ""))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(4, 10))

        ctk.CTkButton(
            self,
            text="Create" if is_new else "Save",
            fg_color="#FF007F", hover_color="#CC005F",
            command=self._save
        ).pack(pady=(0, 16))

    def _save(self):
        snippets = database.get_snippets()
        existing = {} if self.is_new else snippets[self.index]
        new_data = {
            "title":       self.e_title.get().strip() or "Untitled",
            "content":     self.textbox.get("1.0", "end-1c"),
            "category":    self.e_cat.get().strip() or "General",
            "color":       database.pick_random_color() if self.is_new else existing["color"],
            "usage_count": 0 if self.is_new else existing.get("usage_count", 0),
        }
        if self.is_new:
            snippets.append(new_data)
        else:
            snippets[self.index] = new_data
        database.save_json(database.SNIPPETS_FILE, snippets)
        self.parent.refresh_ui()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  SNIPPET TILE
# ══════════════════════════════════════════════════════════════════════════════

class SnippetTile(ctk.CTkFrame):
    def __init__(self, master, data: dict, index: int, app: "QuickNotesApp"):
        super().__init__(master, fg_color="#16181A", corner_radius=8, height=52)
        self.pack_propagate(False)
        self.data, self.index, self.app = data, index, app
        self._hover        = False
        self._drag_target  = None
        self._drag_start_y = None

        # ── Left accent bar ───────────────────────────────────────
        self.accent = ctk.CTkFrame(self, width=3, fg_color=data["color"], corner_radius=0)
        self.accent.pack(side="left", fill="y")

        # ── Drag handle ───────────────────────────────────────────
        self.handle = ctk.CTkLabel(self, text="⠿", text_color="#262626",
                                   font=("Arial", 13), cursor="fleur", width=12)
        self.handle.pack(side="left", padx=(3, 0))

        # ── Delete × — packed RIGHT before inner so it always gets space ──
        self.del_lbl = ctk.CTkLabel(self, text="×", text_color="#282828",
                                    font=("Arial", 20, "bold"), cursor="hand2", width=20)
        self.del_lbl.pack(side="right", padx=(0, 6))

        # ── Inner content area ────────────────────────────────────
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True)
        self._inner = inner

        # Usage badge — RIGHT side, packed before title so it claims space first
        usage = data.get("usage_count", 0)
        if usage > 0:
            ctk.CTkLabel(inner, text=str(usage),
                         font=("Consolas", 8), text_color="#383838",
                         width=14).pack(side="right", padx=(0, 2))

        # Category tag — RIGHT side, packed before title
        cat = data.get("category", "General")
        if cat and cat.lower() != "general":
            ctk.CTkLabel(inner, text=cat[:6].upper(),
                         font=("Consolas", 8), text_color="#444444",
                         width=30).pack(side="right", padx=(0, 2))

        # Title — fills remaining space, will truncate naturally
        self.title_lbl = ctk.CTkLabel(
            inner, text=data["title"],
            font=("Consolas", 12, "bold"), anchor="w",
            text_color="#C8C8C8"
        )
        self.title_lbl.pack(side="left", padx=(8, 2), fill="x", expand=True)

        # ── Bindings ──────────────────────────────────────────────
        for w in (self, inner, self.title_lbl):
            w.bind("<Enter>",           self._on_hover)
            w.bind("<Leave>",           self._on_leave)
            w.bind("<Button-1>",        self._on_click)
            w.bind("<Double-Button-1>", self._on_dbl)

        self.del_lbl.bind("<Button-1>", lambda _: self.app.delete_note(self.index))

        self.handle.bind("<ButtonPress-1>",   self._drag_start)
        self.handle.bind("<B1-Motion>",       self._drag_motion)
        self.handle.bind("<ButtonRelease-1>", self._drag_end)

    # ── hover ─────────────────────────────────────────────────────
    def _on_hover(self, _e):
        if not self._hover:
            self._hover = True
            self.configure(fg_color="#1E2124", border_width=1, border_color="#3A3A3A")
            self.accent.configure(width=4)
            self.del_lbl.configure(text_color="#585858")
            self.title_lbl.configure(text_color="#FFFFFF")
            self.handle.configure(text_color="#363636")
            self._slide(0, 5)

    def _on_leave(self, _e):
        try:
            mx, my = self.winfo_pointerxy()
            rx, ry = self.winfo_rootx(), self.winfo_rooty()
            if rx <= mx <= rx + self.winfo_width() and ry <= my <= ry + self.winfo_height():
                return
        except Exception:
            pass
        if self._hover:
            self._hover = False
            self.configure(fg_color="#16181A", border_width=0)
            self.accent.configure(width=3)
            self.del_lbl.configure(text_color="#282828")
            self.title_lbl.configure(text_color="#C8C8C8")
            self.handle.configure(text_color="#262626")
            self._slide(5, 0)

    def _slide(self, frm: int, to: int, step: int = 0):
        if step > 6:
            return
        t  = 1 - (1 - step / 6) ** 3
        px = int(8 + frm + (to - frm) * t)
        try:
            self.title_lbl.pack_configure(padx=(px, 2))
            self.after(16, lambda: self._slide(frm, to, step + 1))
        except Exception:
            pass

    # ── click / copy ──────────────────────────────────────────────
    def _on_click(self, _e):
        pyperclip.copy(self.data["content"])
        snippets = database.get_snippets()
        if self.index < len(snippets):
            snippets[self.index]["usage_count"] = snippets[self.index].get("usage_count", 0) + 1
            database.save_json(database.SNIPPETS_FILE, snippets)
        orig = self.accent.cget("fg_color")
        self.accent.configure(fg_color="#FFFFFF")
        self.after(110, lambda: self.accent.configure(fg_color=orig))
        Toast(self.app, "Copied!")

    def _on_dbl(self, _e):
        EditWindow(self.app, self.data, self.index)

    # ── tile drag-to-reorder ──────────────────────────────────────
    def _drag_start(self, e):
        self._drag_start_y = e.y_root
        self._drag_target  = self.index
        self.configure(border_width=1, border_color=self.data["color"])
        self.lift()

    def _drag_motion(self, e):
        for tile in self.master.winfo_children():
            if not isinstance(tile, SnippetTile) or tile is self:
                continue
            ty, th = tile.winfo_rooty(), tile.winfo_height()
            if ty <= e.y_root <= ty + th:
                self._drag_target = tile.index
                break

    def _drag_end(self, _e):
        self.configure(border_width=0)
        if self._drag_target is not None and self._drag_target != self.index:
            snippets = database.get_snippets()
            item = snippets.pop(self.index)
            snippets.insert(self._drag_target, item)
            database.save_json(database.SNIPPETS_FILE, snippets)
            self.app.refresh_ui()
        self._drag_target  = None
        self._drag_start_y = None


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

class QuickNotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings         = database.get_settings()
        self._hidden          = False
        self._active_category = "All"
        self._sort_by_usage   = False
        self._search_text     = ""
        self._undo_data       = None
        self._undo_toast      = None
        self._resize_start_y  = None
        self._resize_start_h  = None
        self._resize_start_x  = None
        self._resize_start_w  = None
        self._window_h        = int(self.settings.get("window_height", 620))
        self._window_w        = int(self.settings.get("window_width",  PANEL_W_DEFAULT))

        # Window drag state
        self._drag_win_x = None
        self._drag_win_y = None

        self._setup_window()
        self._build_ui()
        self.refresh_ui()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind_all("<Control-f>", lambda _e: self.search_entry.focus_set())
        self.bind("<Key>", self._global_key)

    # ── window setup ──────────────────────────────────────────────

    def _setup_window(self):
        self.overrideredirect(True)
        self.attributes("-topmost", self.settings.get("always_on_top", True))
        self.attributes("-alpha",   self.settings.get("transparency",  0.85))
        self.configure(fg_color="#0D0F11")
        icon = _get_icon_path()
        if icon:
            self.iconbitmap(icon)
        self.apply_snap(self.settings.get("snap_position", "right"), initial=True)

    def apply_snap(self, position: str, initial: bool = False):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h   = self._window_w, self._window_h
        positions = {
            "right":    f"{w}x{h}+{sw - w - 10}+50",
            "left":     f"{w}x{h}+10+50",
            "floating": f"{w}x{h}+{sw // 2 - w // 2}+{sh // 2 - h // 2}",
        }
        self.geometry(positions.get(position, positions["right"]))
        self._hidden = False

    # ── UI construction ───────────────────────────────────────────

    def _build_ui(self):
        # TOP BAR — background acts as drag handle for moving the whole window
        bar = ctk.CTkFrame(self, fg_color="transparent", height=34)
        bar.pack(fill="x", padx=6, pady=(4, 1))
        bar.pack_propagate(False)

        self.app_name = ctk.CTkLabel(
            bar, text="NEON.NOTES",
            font=("Consolas", 11, "bold"), text_color="#FF007F", cursor="fleur"
        )
        self.app_name.pack(side="left", padx=(4, 0))

        ex = ctk.CTkLabel(bar, text="✕", text_color="#404040",
                          cursor="hand2", font=("Arial", 13, "bold"))
        ex.pack(side="right", padx=(0, 2))
        ex.bind("<Button-1>", lambda _: self.quit())
        ex.bind("<Enter>",    lambda _: ex.configure(text_color="#FF4444"))
        ex.bind("<Leave>",    lambda _: ex.configure(text_color="#404040"))

        ctk.CTkButton(bar, text="⚙", width=24, height=24,
                      fg_color="transparent", text_color="#505050",
                      hover_color="#1E2022",
                      command=self.open_settings).pack(side="right", padx=1)

        ctk.CTkButton(bar, text="+", width=24, height=24,
                      fg_color="#1E2022", hover_color="#FF007F",
                      text_color="#AAAAAA",
                      command=self.add_note).pack(side="right", padx=1)

        self._sort_btn = ctk.CTkButton(
            bar, text="↕", width=24, height=24,
            fg_color="transparent", text_color="#505050",
            hover_color="#1E2022",
            command=self._toggle_sort
        )
        self._sort_btn.pack(side="right", padx=1)

        # Bind window drag to bar background and the app name label
        for widget in (bar, self.app_name):
            widget.bind("<ButtonPress-1>",   self._drag_win_start)
            widget.bind("<B1-Motion>",       self._drag_win_motion)
            widget.bind("<ButtonRelease-1>", self._drag_win_end)

        # SEPARATOR
        ctk.CTkFrame(self, height=1, fg_color="#1E2022").pack(fill="x", padx=8, pady=(0, 4))

        # SEARCH BAR
        s_row = ctk.CTkFrame(self, fg_color="transparent", height=28)
        s_row.pack(fill="x", padx=8, pady=(0, 3))
        s_row.pack_propagate(False)

        ctk.CTkLabel(s_row, text="⌕", text_color="#404040",
                     font=("Arial", 15)).pack(side="left", padx=(4, 2))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        self.search_entry = ctk.CTkEntry(
            s_row, textvariable=self._search_var,
            placeholder_text="search...",
            fg_color="#131517", border_width=0,
            font=("Consolas", 10), text_color="#888888", height=22
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 3))

        clr = ctk.CTkLabel(s_row, text="×", text_color="#333333",
                           font=("Arial", 13), cursor="hand2")
        clr.pack(side="right", padx=(0, 2))
        clr.bind("<Button-1>", lambda _: self._search_var.set(""))

        # CATEGORY BAR
        self._cat_bar = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=26,
            orientation="horizontal",
            scrollbar_button_color="#181818",
            scrollbar_button_hover_color="#282828"
        )
        self._cat_bar.pack(fill="x", padx=8, pady=(0, 4))

        # PIN ROW
        pin_row = ctk.CTkFrame(self, fg_color="transparent", height=22)
        pin_row.pack(fill="x", padx=8, pady=(0, 4))
        pin_row.pack_propagate(False)

        self.pin = ctk.CTkSwitch(
            pin_row, text="PIN",
            font=("Consolas", 9, "bold"), width=36, height=16,
            progress_color="#00FF88", button_color="#00CC66",
            button_hover_color="#00FF88", text_color="#404040",
            command=self._toggle_pin
        )
        if self.settings.get("always_on_top"):
            self.pin.select()
        self.pin.pack(side="left")

        # BOTTOM RESIZE GRIP (height) — must be packed before scroll
        grip_h = ctk.CTkFrame(self, height=6, fg_color="#0F1113",
                              cursor="sb_v_double_arrow")
        grip_h.pack(fill="x", side="bottom")
        grip_h.bind("<ButtonPress-1>",   self._resize_h_start)
        grip_h.bind("<B1-Motion>",       self._resize_h_motion)
        grip_h.bind("<ButtonRelease-1>", self._resize_h_end)

        # RIGHT-SIDE RESIZE GRIP (width) — must be packed before scroll
        grip_w = ctk.CTkFrame(self, width=6, fg_color="#0F1113",
                              cursor="sb_h_double_arrow")
        grip_w.pack(fill="y", side="right")
        grip_w.bind("<ButtonPress-1>",   self._resize_w_start)
        grip_w.bind("<B1-Motion>",       self._resize_w_motion)
        grip_w.bind("<ButtonRelease-1>", self._resize_w_end)

        # TILES — packed last so grips claim their edges first
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color="#2A2A2A",
            scrollbar_button_hover_color="#FF007F"
        )
        self.scroll.pack(fill="both", expand=True)

    def _rebuild_cat_bar(self, categories: list[str]):
        for w in self._cat_bar.winfo_children():
            w.destroy()
        for cat in categories:
            active = (cat == self._active_category)
            ctk.CTkButton(
                self._cat_bar, text=cat,
                width=max(36, len(cat) * 7 + 14), height=18,
                font=("Consolas", 9),
                fg_color="#FF007F" if active else "#1E2022",
                hover_color="#FF007F",
                text_color="#FFFFFF" if active else "#666666",
                corner_radius=4,
                command=lambda c=cat: self._set_category(c)
            ).pack(side="left", padx=(0, 3))

    # ── refresh ───────────────────────────────────────────────────

    def refresh_ui(self):
        snippets = database.get_snippets()

        cats = ["All"] + sorted({s.get("category", "General") for s in snippets})
        if self._active_category not in cats:
            self._active_category = "All"
        self._rebuild_cat_bar(cats)

        visible: list[tuple[int, dict]] = []
        for i, s in enumerate(snippets):
            if self._active_category != "All" and s.get("category", "General") != self._active_category:
                continue
            q = self._search_text
            if q and q not in s["title"].lower() and q not in s["content"].lower():
                continue
            visible.append((i, s))

        if self._sort_by_usage:
            visible.sort(key=lambda x: x[1].get("usage_count", 0), reverse=True)

        for w in self.scroll.winfo_children():
            w.destroy()
        for i, s in visible:
            SnippetTile(self.scroll, s, i, self).pack(fill="x", padx=8, pady=3)

        self._sort_btn.configure(
            text_color="#FF007F" if self._sort_by_usage else "#505050"
        )

    # ── actions ───────────────────────────────────────────────────

    def open_settings(self):
        SettingsWindow(self)

    def add_note(self):
        EditWindow(self, {"title": "", "content": "", "category": "General"}, -1, is_new=True)

    def delete_note(self, index: int):
        snippets = database.get_snippets()
        if index >= len(snippets):
            return
        removed = snippets.pop(index)
        database.save_json(database.SNIPPETS_FILE, snippets)
        self._undo_data = (index, removed)

        if self._undo_toast:
            try:
                self._undo_toast.destroy()
            except Exception:
                pass
        self._undo_toast = UndoToast(self, on_undo=self._undo_delete)
        self.refresh_ui()

    def _undo_delete(self):
        if self._undo_data:
            idx, snippet = self._undo_data
            snippets = database.get_snippets()
            snippets.insert(idx, snippet)
            database.save_json(database.SNIPPETS_FILE, snippets)
            self._undo_data = None
            self.refresh_ui()
            Toast(self, "Restored ✓")

    # ── filter / sort ─────────────────────────────────────────────

    def _set_category(self, cat: str):
        self._active_category = cat
        self.refresh_ui()

    def _on_search_change(self, *_):
        self._search_text = self._search_var.get().lower()
        self.refresh_ui()

    def _toggle_sort(self):
        self._sort_by_usage = not self._sort_by_usage
        self.refresh_ui()

    def _global_key(self, event):
        focused  = self.focus_get()
        is_input = isinstance(focused, (ctk.CTkEntry, ctk.CTkTextbox))
        if not is_input and event.char and event.char.isprintable() and not (event.state & 0x4):
            self.search_entry.focus_set()

    # ── pin ───────────────────────────────────────────────────────

    def _toggle_pin(self):
        self.settings["always_on_top"] = bool(self.pin.get())
        self.attributes("-topmost", self.settings["always_on_top"])
        database.save_json(database.SETTINGS_FILE, self.settings)

    # ── window drag-to-move ───────────────────────────────────────

    def _drag_win_start(self, e):
        self._drag_win_x = e.x_root - self.winfo_x()
        self._drag_win_y = e.y_root - self.winfo_y()

    def _drag_win_motion(self, e):
        if self._drag_win_x is None:
            return
        self.geometry(f"+{e.x_root - self._drag_win_x}+{e.y_root - self._drag_win_y}")

    def _drag_win_end(self, _e):
        if self._drag_win_x is None:
            return
        self._drag_win_x = None
        self._drag_win_y = None

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y   = self.winfo_x(), self.winfo_y()
        w, h   = self._window_w, self._window_h

        if x <= SNAP_THRESHOLD:
            new_pos = "left"
        elif x + w >= sw - SNAP_THRESHOLD:
            new_pos = "right"
        else:
            # Freely placed — stay exactly where dropped
            self.settings["snap_position"] = "floating"
            database.save_json(database.SETTINGS_FILE, self.settings)
            return

        self.settings["snap_position"] = new_pos
        database.save_json(database.SETTINGS_FILE, self.settings)
        self.apply_snap(new_pos)

    # ── auto-hide ─────────────────────────────────────────────────

    def _on_enter(self, _e):
        if self._hidden:
            self._show_panel()

    def _on_leave(self, _e):
        self.after(150, self._check_leave)

    def _check_leave(self):
        try:
            mx, my = self.winfo_pointerxy()
            rx, ry = self.winfo_rootx(), self.winfo_rooty()
            if rx <= mx <= rx + self.winfo_width() and ry <= my <= ry + self.winfo_height():
                return
        except Exception:
            pass
        if self.settings.get("auto_hide") and not self._hidden:
            self._hide_panel()

    def _hide_panel(self):
        # Floating windows don't auto-hide — no sensible edge to collapse to
        if self.settings.get("snap_position") == "floating":
            return
        self._hidden = True
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        pos    = self.settings.get("snap_position", "right")
        h      = self._window_h
        geoms  = {
            "right": f"{SNAP_THIN}x{h}+{sw - SNAP_THIN}+50",
            "left":  f"{SNAP_THIN}x{h}+0+50",
        }
        self.geometry(geoms.get(pos, geoms["right"]))

    def _show_panel(self):
        self._hidden = False
        self.apply_snap(self.settings.get("snap_position", "right"))

    # ── resize ────────────────────────────────────────────────────

    # ── height resize ────────────────────────────────────────────

    def _resize_h_start(self, e):
        self._resize_start_y = e.y_root
        self._resize_start_h = self.winfo_height()

    def _resize_h_motion(self, e):
        if self._resize_start_y is None:
            return
        dy    = e.y_root - self._resize_start_y
        new_h = max(300, self._resize_start_h + dy)
        self._window_h = new_h
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        pos    = self.settings.get("snap_position", "right")
        w      = self._window_w
        if pos == "floating":
            self.geometry(f"{w}x{new_h}+{self.winfo_x()}+{self.winfo_y()}")
            return
        geoms = {
            "right": f"{w}x{new_h}+{sw - w - 10}+50",
            "left":  f"{w}x{new_h}+10+50",
        }
        self.geometry(geoms.get(pos, geoms["right"]))

    def _resize_h_end(self, _e):
        self._resize_start_y = None
        self.settings["window_height"] = self._window_h
        database.save_json(database.SETTINGS_FILE, self.settings)

    # ── width resize ──────────────────────────────────────────────

    def _resize_w_start(self, e):
        self._resize_start_x = e.x_root
        self._resize_start_w = self.winfo_width()

    def _resize_w_motion(self, e):
        if self._resize_start_x is None:
            return
        dx    = e.x_root - self._resize_start_x
        pos   = self.settings.get("snap_position", "right")
        # Right-snapped and floating: dragging right = wider
        # Left-snapped: dragging right = narrower (grip is on the right edge)
        if pos == "left":
            new_w = max(PANEL_W_MIN, min(PANEL_W_MAX, self._resize_start_w + dx))
        else:
            new_w = max(PANEL_W_MIN, min(PANEL_W_MAX, self._resize_start_w + dx))
        self._window_w = new_w
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        h      = self._window_h
        if pos == "floating":
            self.geometry(f"{new_w}x{h}+{self.winfo_x()}+{self.winfo_y()}")
            return
        geoms = {
            "right": f"{new_w}x{h}+{sw - new_w - 10}+50",
            "left":  f"{new_w}x{h}+10+50",
        }
        self.geometry(geoms.get(pos, geoms["right"]))

    def _resize_w_end(self, _e):
        self._resize_start_x = None
        self.settings["window_width"] = self._window_w
        database.save_json(database.SETTINGS_FILE, self.settings)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _sep(parent):
    ctk.CTkFrame(parent, height=1, fg_color="#2A2A2A").pack(fill="x", padx=16, pady=(12, 8))

def _field_label(parent, text: str):
    ctk.CTkLabel(parent, text=text, font=("Segoe UI", 10),
                 text_color="#606060").pack(anchor="w", padx=22, pady=(10, 0))

def _entry(parent, placeholder: str, value: str) -> ctk.CTkEntry:
    e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                     fg_color="#2D2F31", border_width=0, font=("Consolas", 11))
    e.insert(0, value)
    e.pack(fill="x", padx=20, pady=(3, 0))
    return e


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    QuickNotesApp().mainloop()