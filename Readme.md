# ⚡ Neon.Notes

![Version](https://img.shields.io/badge/version-1.0.0-FF007F?style=for-the-badge&logo=semantic-release&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-1E90FF?style=for-the-badge&logo=tkinter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge&logo=open-source-initiative&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-555555?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> Snippet manager that lives on the edge of your screen - copy anything in one click.

---

## ✨ Features

| Feature                     | Description                                                         |
| --------------------------- | ------------------------------------------------------------------- |
| 🖱️ **One-Click Copy**       | Click any tile to instantly copy its content to clipboard           |
| 🌊 **Slide-In Hover**       | Tiles animate left on hover with neon border highlight              |
| 📌 **PIN / Always-on-Top**  | Neon green toggle keeps the app above all other windows             |
| 👁️ **Auto-Hide**            | Panel collapses to a 5px edge strip when mouse leaves               |
| 🎨 **Neon Tile Colors**     | Each snippet gets a unique warm neon accent from a 12-color palette |
| ✏️ **Double-Click to Edit** | Full editor window opens on double-click                            |
| ➕ **Add & Delete**         | Manage notes via toolbar buttons with confirmation prompts          |
| ⚙️ **Settings Panel**       | Adjust opacity (0.2–1.0) and auto-hide behavior at runtime          |
| 💾 **Persistent Storage**   | All snippets and settings saved to local JSON automatically         |
| 🪟 **Borderless Window**    | Frameless dark UI snapped to the right edge of your screen          |

---

## 🚀 Getting Started

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

---

## 📁 Project Structure

```
neonnotes/
├── main.py          # UI logic — windows, tiles, animations
├── database.py      # JSON read/write, color palette
├── snippets.json    # Auto-generated — your saved notes
├── settings.json    # Auto-generated — persisted preferences
└── README.md
```

---

## 🎮 Usage

| Action               | How                                       |
| -------------------- | ----------------------------------------- |
| Copy a snippet       | Single click on any tile                  |
| Edit a snippet       | Double-click on the tile                  |
| Add new snippet      | Click **+** in the toolbar                |
| Delete a snippet     | Click the **×** on the right of the tile  |
| Toggle always-on-top | Use the **PIN** switch (neon green)       |
| Auto-hide on/off     | Open **⚙ Settings**                       |
| Adjust transparency  | Open **⚙ Settings** → drag opacity slider |
| Close the app        | Click **✕** in the toolbar                |

---

## ⚙️ Settings

Settings are saved automatically to `settings.json`:

```json
{
  "transparency": 0.85,
  "main_color": "#0D0F11",
  "auto_hide": true,
  "always_on_top": true
}
```

---

## 🎨 Color Palette

Tile accent colors are randomly assigned from a 12-color warm neon palette. The picker avoids repeating the last 4 used colors for maximum visual variety:

`#FF007F` `#FF4D4D` `#FFA500` `#FFCC00` `#FF6347` `#FF3399` `#FFD700` `#E91E63` `#FF5500` `#FF1493` `#F4A261` `#FF6B6B`

---

## 🛠️ Dependencies

| Package                                                         | Version | Purpose                         |
| --------------------------------------------------------------- | ------- | ------------------------------- |
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | 5.x     | Modern dark UI widgets          |
| [pyperclip](https://github.com/asweigart/pyperclip)             | 1.x     | Cross-platform clipboard access |

---

## 📄 License

```
MIT License

Copyright (c) 2024 NeonNotes Contributors

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

## 🤝 Contributing

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
