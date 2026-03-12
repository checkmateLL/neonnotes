# ⚡ Neon.Notes

![Version](https://img.shields.io/badge/version-2.0.0-FF007F?style=for-the-badge&logo=semantic-release&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-1E90FF?style=for-the-badge&logo=tkinter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge&logo=open-source-initiative&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-555555?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> Snippet manager that lives on the edge of your screen — copy anything in one click.

---

## Features

| Feature                  | Description                                                                  |
| ------------------------ | ---------------------------------------------------------------------------- |
| **One-Click Copy**       | Click any tile to instantly copy its content to clipboard                    |
| **Slide-In Hover**       | Tiles animate on hover with neon border highlight                            |
| **PIN / Always-on-Top**  | Neon green toggle keeps the app above all other windows                      |
| **Auto-Hide**            | Panel collapses to a 5px edge strip when mouse leaves (disabled in floating) |
| **Neon Tile Colors**     | Each snippet gets a unique accent from a 12-color warm neon palette          |
| **Double-Click to Edit** | Full editor window opens on double-click                                     |
| **Add & Delete**         | Manage notes via toolbar buttons; delete shows an UNDO toast for 4 seconds   |
| **Search / Filter**      | Live search bar filters by title or content; `Ctrl+F` or just start typing   |
| **Categories**           | Tag each snippet; filter by category using the tab bar at the top            |
| **Usage Counter**        | Tracks how many times each snippet has been copied                           |
| **Sort by Usage**        | `↕` button in the toolbar sorts tiles by most-copied first                   |
| **Drag to Reorder**      | Grab the `⠿` handle on any tile and drag it to a new position                |
| **Drag to Move**         | Drag the top bar to reposition the window anywhere on screen                 |
| **Edge Snapping**        | Drop near left or right edge to snap; drop anywhere else to float freely     |
| **Snap Position**        | Choose Left, Right, or Floating from Settings                                |
| **Resizable**            | Drag the bottom grip to resize height; drag the right grip to resize width   |
| **Settings Panel**       | Adjust opacity, auto-hide, snap position, export and import snippets         |
| **Export / Import**      | Back up or share your snippets as a JSON file from the Settings panel        |
| **Persistent Storage**   | All data saved to `%APPDATA%\NeonNotes\` — never lost between sessions       |
| **Borderless Window**    | Frameless dark UI with custom icon support                                   |

---

## Getting Started

### Prerequisites

- Python **3.10** or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/checkmateLL/neonnotes.git
cd neonnotes

# 2. Install dependencies
pip install customtkinter pyperclip

# 3. Run the app
python main.py
```

Data files (`snippets.json`, `settings.json`) are created automatically on first run inside `%APPDATA%\NeonNotes\`. They are never stored next to the script.

---

## Building an Executable

To share the app or run it without Python installed:

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build
pyinstaller --noconfirm --onefile --windowed \
  --icon=icon.ico \
  --collect-data customtkinter \
  --add-data "icon.ico;." \
  --name="NeonNotes" \
  main.py
```

The output is `dist/NeonNotes.exe`. No Python installation required to run it.

> **Note:** When running the exe for the first time, fresh default snippets are generated automatically. The exe never reads or copies any local JSON files from the project folder.

---

## Project Structure

```
neonnotes/
├── main.py          # UI logic — windows, tiles, animations, drag, resize
├── database.py      # JSON read/write, color palette, AppData paths
├── icon.ico         # Custom app icon (used by both script and exe)
└── README.md
```

`snippets.json` and `settings.json` live in `%APPDATA%\NeonNotes\` and are never committed to the repository.

---

## Usage

| Action               | How                                                        |
| -------------------- | ---------------------------------------------------------- |
| Copy a snippet       | Single click on any tile                                   |
| Edit a snippet       | Double-click on the tile                                   |
| Add new snippet      | Click **+** in the toolbar                                 |
| Delete a snippet     | Click **×** on the tile — an UNDO toast appears for 4s     |
| Search snippets      | Type anywhere, or press `Ctrl+F` to focus the search bar   |
| Filter by category   | Click a category button in the tab bar                     |
| Sort by usage        | Click **↕** in the toolbar (lights up pink when active)    |
| Reorder tiles        | Drag the **⠿** handle on the left of any tile              |
| Move the window      | Drag the **NEON.NOTES** label or top bar background        |
| Snap to edge         | Drag and drop within 40px of the left or right screen edge |
| Float freely         | Drop the window away from any edge                         |
| Resize height        | Drag the grip strip at the bottom                          |
| Resize width         | Drag the grip strip on the right side                      |
| Toggle always-on-top | Use the **PIN** switch                                     |
| Change snap position | Open **⚙ Settings** → Snap Position                        |
| Auto-hide on/off     | Open **⚙ Settings** → Auto-hide to edge                    |
| Adjust transparency  | Open **⚙ Settings** → drag the opacity slider              |
| Export snippets      | Open **⚙ Settings** → Export Snippets                      |
| Import snippets      | Open **⚙ Settings** → Import Snippets                      |
| Close the app        | Click **✕** in the toolbar                                 |

---

## Settings

Settings are saved automatically to `%APPDATA%\NeonNotes\settings.json`:

```json
{
  "transparency": 0.85,
  "main_color": "#0D0F11",
  "auto_hide": true,
  "always_on_top": true,
  "snap_position": "right",
  "window_height": 620,
  "window_width": 220
}
```

`snap_position` accepts `"left"`, `"right"`, or `"floating"`.

---

## Color Palette

Tile accent colors are randomly assigned from a 12-color warm neon palette. The picker avoids repeating the last 4 used colors for maximum visual variety:

`#FF007F` `#FF4D4D` `#FFA500` `#FFCC00` `#00E5FF` `#00FF88` `#BF5FFF` `#FF6B35` `#FFD700` `#1DE9B6` `#FF3D71` `#AEEA00`

---

## Dependencies

| Package                                                         | Version | Purpose                         |
| --------------------------------------------------------------- | ------- | ------------------------------- |
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | 5.x     | Modern dark UI widgets          |
| [pyperclip](https://github.com/asweigart/pyperclip)             | 1.x     | Cross-platform clipboard access |

---

## .gitignore

```
build/
dist/
*.spec
__pycache__/
snippets.json
settings.json
```

---

## License

```
MIT License

Copyright (c) 2026 NeonNotes Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with ❤️ and neon pink — <b>Neon.Notes</b>
</p>
