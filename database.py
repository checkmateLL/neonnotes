import json
import os

SNIPPETS_FILE = "snippets.json"
SETTINGS_FILE = "settings.json"

# Expanded, truly varied warm neon palette — each color is visually distinct
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

# Track recently used colors to avoid repetition
_recent_colors = []

def pick_random_color():
    """Pick a random color, avoiding the last 4 used ones for variety."""
    global _recent_colors
    available = [c for c in WARM_COLORS if c not in _recent_colors]
    if not available:
        available = WARM_COLORS
        _recent_colors = []
    color = __import__('random').choice(available)
    _recent_colors.append(color)
    if len(_recent_colors) > 4:
        _recent_colors.pop(0)
    return color

def load_json(filename, default):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        save_json(filename, default)
        return default
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        save_json(filename, default)
        return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_snippets():
    return load_json(SNIPPETS_FILE, [
        {"title": "Welcome", "content": "Double click to edit!", "color": "#FF007F"},
        {"title": "Example Note", "content": "Click to copy this text.", "color": "#FF4D4D"},
    ])

def get_settings():
    return load_json(SETTINGS_FILE, {
        "transparency": 0.85,
        "main_color": "#0D0F11",
        "auto_hide": True,
        "always_on_top": True
    })