import customtkinter as ctk
import pyperclip
import database
import random
import time
from tkinter import messagebox

ctk.set_appearance_mode("dark")

# Snow/grain texture via canvas overlay
SNOW_CHARS = "·∙•⋅"

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("280x220")
        self.attributes("-topmost", True)
        self.configure(fg_color="#1A1C1E")

        ctk.CTkLabel(self, text="Opacity", font=("Segoe UI", 12)).pack(pady=(15, 0))
        self.slider = ctk.CTkSlider(self, from_=0.2, to=1.0, button_color="#FF007F", command=self.update_opacity)
        self.slider.set(parent.settings.get("transparency", 0.85))
        self.slider.pack(pady=10)

        self.hide_switch = ctk.CTkSwitch(self, text="Auto-hide to side", progress_color="#FF007F", command=self.toggle_hide)
        if parent.settings.get("auto_hide"): self.hide_switch.select()
        self.hide_switch.pack(pady=10)

        ctk.CTkButton(self, text="Close", fg_color="#2D2F31", height=28, command=self.destroy).pack(pady=15)

    def update_opacity(self, value):
        self.parent.settings["transparency"] = value
        self.parent.attributes("-alpha", value)
        database.save_json(database.SETTINGS_FILE, self.parent.settings)

    def toggle_hide(self):
        self.parent.settings["auto_hide"] = bool(self.hide_switch.get())
        database.save_json(database.SETTINGS_FILE, self.parent.settings)


class EditWindow(ctk.CTkToplevel):
    def __init__(self, parent, snippet_data, index, is_new=False):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.is_new = is_new
        self.title("Edit Note")
        self.geometry("350x350")
        self.attributes("-topmost", True)
        self.configure(fg_color="#1A1C1E")

        self.entry_title = ctk.CTkEntry(self, placeholder_text="Title", fg_color="#2D2F31", border_width=0)
        self.entry_title.insert(0, snippet_data.get("title", ""))
        self.entry_title.pack(fill="x", padx=20, pady=(20, 10))

        self.textbox = ctk.CTkTextbox(self, fg_color="#2D2F31", border_width=0)
        self.textbox.insert("1.0", snippet_data.get("content", ""))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=10)

        btn_text = "Create" if is_new else "Save"
        ctk.CTkButton(self, text=btn_text, fg_color="#FF007F", command=self.save).pack(pady=15)

    def save(self):
        snippets = database.get_snippets()
        new_data = {
            "title": self.entry_title.get(),
            "content": self.textbox.get("1.0", "end-1c"),
            "color": random.choice(database.WARM_COLORS) if self.is_new else snippets[self.index]["color"]
        }

        if self.is_new:
            snippets.append(new_data)
        else:
            snippets[self.index] = new_data

        database.save_json(database.SNIPPETS_FILE, snippets)
        self.parent.refresh_ui()
        self.destroy()


class SnippetTile(ctk.CTkFrame):
    def __init__(self, master, data, index, app):
        super().__init__(master, fg_color="#16181A", corner_radius=8, height=52)
        self.pack_propagate(False)
        self.data, self.index, self.app = data, index, app
        self._hover = False

        # Neon accent bar (left side)
        self.accent = ctk.CTkFrame(self, width=3, fg_color=data["color"], corner_radius=0)
        self.accent.pack(side="left", fill="y")

        # Inner content frame for slide animation
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(side="left", fill="both", expand=True)

        self.label = ctk.CTkLabel(self.inner, text=data["title"], font=("Consolas", 12, "bold"), anchor="w",
                                  text_color="#C8C8C8")
        self.label.pack(side="left", padx=(12, 8), fill="x", expand=True)

        # Language/type tag (derived from title words as mock tag)
        tag_text = self._get_tag(data.get("title", ""))
        self.tag_label = ctk.CTkLabel(self.inner, text=tag_text, font=("Consolas", 9),
                                      text_color="#505050", anchor="e")
        self.tag_label.pack(side="right", padx=(0, 6))

        self.del_btn = ctk.CTkLabel(self, text="×", text_color="#303030", font=("Arial", 20, "bold"), cursor="hand2")
        self.del_btn.pack(side="right", padx=(0, 8))

        # Slide offset
        self._slide_x = 0

        for widget in [self, self.inner, self.label, self.tag_label]:
            widget.bind("<Enter>", self.on_hover)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.handle_click)
            widget.bind("<Double-Button-1>", self.handle_double_click)

        self.del_btn.bind("<Button-1>", lambda e: self.app.delete_note(self.index))

    def _get_tag(self, title):
        """Generate a fake language tag from title keywords."""
        mapping = {
            "python": "PY", "js": "JS", "javascript": "JS", "typescript": "TS",
            "css": "CSS", "html": "HTML", "sql": "SQL", "bash": "SH",
            "shader": "GLSL", "next": "TS", "tailwind": "CSS", "postgres": "SQL",
            "boto": "PY", "api": "TS", "config": "CFG", "query": "SQL",
        }
        title_lower = title.lower()
        for key, val in mapping.items():
            if key in title_lower:
                return val
        return "TXT"

    def on_hover(self, event):
        if not self._hover:
            self._hover = True
            self.configure(fg_color="#1E2124", border_width=1, border_color="#3A3A3A")
            self.accent.configure(width=4)
            self.del_btn.configure(text_color="#606060")
            self.label.configure(text_color="#FFFFFF")
            self._animate_slide(0, 6)

    def on_leave(self, event):
        # Only trigger if truly leaving the entire tile
        try:
            x, y = self.winfo_pointerxy()
            wx, wy = self.winfo_rootx(), self.winfo_rooty()
            ww, wh = self.winfo_width(), self.winfo_height()
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return
        except:
            pass
        if self._hover:
            self._hover = False
            self.configure(fg_color="#16181A", border_width=0)
            self.accent.configure(width=3)
            self.del_btn.configure(text_color="#303030")
            self.label.configure(text_color="#C8C8C8")
            self._animate_slide(6, 0)

    def _animate_slide(self, from_x, to_x, step=0):
        steps = 6
        if step > steps:
            return
        progress = step / steps
        # Ease out cubic
        t = 1 - (1 - progress) ** 3
        current = from_x + (to_x - from_x) * t
        try:
            self.label.pack_configure(padx=(int(12 + current), 8))
            self.after(16, lambda: self._animate_slide(from_x, to_x, step + 1))
        except:
            pass

    def handle_click(self, event):
        if event.num == 1:
            pyperclip.copy(self.data["content"])
            orig = self.accent.cget("fg_color")
            self.accent.configure(fg_color="white")
            self.after(120, lambda: self.accent.configure(fg_color=orig))

    def handle_double_click(self, event):
        EditWindow(self.app, self.data, self.index)


class QuickNotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = database.get_settings()
        self._hidden = False
        self._mouse_inside = False
        self.setup_window()
        self._build_ui()
        self.refresh_ui()

        # Auto-hide tracking
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def setup_window(self):
        self.overrideredirect(True)
        self.attributes("-topmost", self.settings.get("always_on_top", True))
        self.attributes("-alpha", self.settings.get("transparency", 0.85))
        self.configure(fg_color="#0D0F11")
        sw = self.winfo_screenwidth()
        self.geometry(f"220x620+{sw - 230}+50")
        self._expanded_geom = f"220x620+{sw - 230}+50"
        self._hidden_geom = f"5x620+{sw - 8}+50"

    def _build_ui(self):
        # ── TOP BAR ──────────────────────────────────────────────
        self.bar = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self.bar.pack(fill="x", pady=(4, 2), padx=6)
        self.bar.pack_propagate(False)

        # App name label
        self.app_name = ctk.CTkLabel(
            self.bar, text="NEON.NOTES",
            font=("Consolas", 11, "bold"),
            text_color="#FF007F"
        )
        self.app_name.pack(side="left", padx=(4, 0))

        # Exit button
        self.exit_btn = ctk.CTkLabel(self.bar, text="✕", text_color="#404040", cursor="hand2",
                                     font=("Arial", 13, "bold"))
        self.exit_btn.pack(side="right", padx=(0, 2))
        self.exit_btn.bind("<Button-1>", lambda e: self.quit())
        self.exit_btn.bind("<Enter>", lambda e: self.exit_btn.configure(text_color="#FF4444"))
        self.exit_btn.bind("<Leave>", lambda e: self.exit_btn.configure(text_color="#404040"))

        # Settings
        ctk.CTkButton(self.bar, text="⚙", width=24, height=24, fg_color="transparent",
                      text_color="#505050", hover_color="#1E2022", command=self.open_settings).pack(side="right", padx=2)

        # Add note
        ctk.CTkButton(self.bar, text="+", width=24, height=24, fg_color="#1E2022",
                      hover_color="#FF007F", text_color="#AAAAAA", command=self.add_note).pack(side="right", padx=2)

        # ── SEPARATOR ────────────────────────────────────────────
        sep = ctk.CTkFrame(self, height=1, fg_color="#1E2022")
        sep.pack(fill="x", padx=8, pady=(0, 4))

        # ── PIN TOGGLE ───────────────────────────────────────────
        pin_row = ctk.CTkFrame(self, fg_color="transparent")
        pin_row.pack(fill="x", padx=8, pady=(0, 6))

        self.pin = ctk.CTkSwitch(
            pin_row, text="PIN",
            font=("Consolas", 9, "bold"),
            width=36, height=18,
            progress_color="#00FF88",       # neon green
            button_color="#00CC66",
            button_hover_color="#00FF88",
            text_color="#404040",
            command=self.toggle_pin
        )
        if self.settings.get("always_on_top"):
            self.pin.select()
        self.pin.pack(side="left")

        # ── SCROLLABLE TILES ─────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#2A2A2A",
                                              scrollbar_button_hover_color="#FF007F")
        self.scroll.pack(fill="both", expand=True, pady=(0, 4))

    def refresh_ui(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        for i, s in enumerate(database.get_snippets()):
            tile = SnippetTile(self.scroll, s, i, self)
            tile.pack(fill="x", padx=8, pady=3)

    def open_settings(self):
        SettingsWindow(self)

    def toggle_pin(self):
        self.settings["always_on_top"] = bool(self.pin.get())
        self.attributes("-topmost", self.settings["always_on_top"])
        database.save_json(database.SETTINGS_FILE, self.settings)

    def add_note(self):
        EditWindow(self, {"title": "", "content": ""}, -1, is_new=True)

    def delete_note(self, index):
        if messagebox.askyesno("Delete", "Are you sure?"):
            snippets = database.get_snippets()
            snippets.pop(index)
            database.save_json(database.SNIPPETS_FILE, snippets)
            self.refresh_ui()

    # ── AUTO-HIDE LOGIC ──────────────────────────────────────────
    def _on_enter(self, event):
        self._mouse_inside = True
        if self._hidden:
            self._show_panel()

    def _on_leave(self, event):
        # Verify pointer truly left the window
        self.after(150, self._check_leave)

    def _check_leave(self):
        try:
            px, py = self.winfo_pointerxy()
            wx, wy = self.winfo_rootx(), self.winfo_rooty()
            ww, wh = self.winfo_width(), self.winfo_height()
            if wx <= px <= wx + ww and wy <= py <= wy + wh:
                # Still inside
                return
        except:
            pass
        self._mouse_inside = False
        if self.settings.get("auto_hide") and not self._hidden:
            self._hide_panel()

    def _hide_panel(self):
        self._hidden = True
        sw = self.winfo_screenwidth()
        self.geometry(f"5x620+{sw - 6}+50")

    def _show_panel(self):
        self._hidden = False
        sw = self.winfo_screenwidth()
        self.geometry(f"220x620+{sw - 230}+50")


if __name__ == "__main__":
    QuickNotesApp().mainloop()