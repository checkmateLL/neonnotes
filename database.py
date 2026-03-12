import json
import os
import random

# ── PATHS ─────────────────────────────────────────────────────────────────────

def get_app_dir():
    """Return a persistent, predictable directory for app data."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.config")
    app_dir = os.path.join(base, "NeonNotes")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

APP_DIR       = get_app_dir()
SNIPPETS_FILE = os.path.join(APP_DIR, "snippets.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

def _migrate_local_files():
    """
    One-time migration: if old local JSON files exist in the script folder
    but the AppData copies don't yet, copy them over automatically.
    Skipped when running as a compiled exe — sys.frozen is set by PyInstaller
    and there are no local dev files to migrate from in that context.
    """
    import sys
    if getattr(sys, "frozen", False):
        return  # running as .exe — nothing to migrate

    import shutil
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for fname, dest in (("snippets.json", SNIPPETS_FILE), ("settings.json", SETTINGS_FILE)):
        local = os.path.join(script_dir, fname)
        if os.path.exists(local) and not os.path.exists(dest):
            shutil.copy(local, dest)

_migrate_local_files()

# ── COLOR PALETTE ─────────────────────────────────────────────────────────────

WARM_COLORS = [
    "#FF007F",  # Hot Pink
    "#FF4D4D",  # Red
    "#FFA500",  # Orange
    "#FFCC00",  # Yellow
    "#00E5FF",  # Cyan
    "#00FF88",  # Neon Green
    "#BF5FFF",  # Purple
    "#FF6B35",  # Burnt Orange
    "#FFD700",  # Gold
    "#1DE9B6",  # Teal
    "#FF3D71",  # Rose Red
    "#AEEA00",  # Lime
]

_recent_colors: list[str] = []

def pick_random_color() -> str:
    """Pick a random color, avoiding the last 4 used for visual variety."""
    global _recent_colors
    available = [c for c in WARM_COLORS if c not in _recent_colors]
    if not available:
        available = WARM_COLORS[:]
        _recent_colors = []
    color = random.choice(available)
    _recent_colors.append(color)
    if len(_recent_colors) > 4:
        _recent_colors.pop(0)
    return color

# ── JSON HELPERS ──────────────────────────────────────────────────────────────

def load_json(filename: str, default):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        save_json(filename, default)
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_json(filename, default)
        return default

def save_json(filename: str, data) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ── DATA ACCESSORS ────────────────────────────────────────────────────────────

def get_snippets() -> list[dict]:
    defaults_if_empty = [
        {
            "title": "Welcome",
            "content": "Double click to edit!",
            "color": "#FF007F",
            "category": "General",
            "usage_count": 0,
        },
        {
            "title": "Example Note",
            "content": "Click to copy this text.",
            "color": "#FF4D4D",
            "category": "General",
            "usage_count": 0,
        },
    ]
    snippets = load_json(SNIPPETS_FILE, defaults_if_empty)

    # ── Migrate old snippets that are missing new fields ──────────
    changed = False
    for s in snippets:
        if "category" not in s:
            s["category"] = "General"
            changed = True
        if "usage_count" not in s:
            s["usage_count"] = 0
            changed = True
    if changed:
        save_json(SNIPPETS_FILE, snippets)

    return snippets

def get_settings() -> dict:
    return load_json(SETTINGS_FILE, {
        "transparency": 0.85,
        "main_color": "#0D0F11",
        "auto_hide": True,
        "always_on_top": True,
        "snap_position": "right",   # left | right | top | bottom
        "window_height": 620,
    })