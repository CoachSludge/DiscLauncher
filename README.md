# 💿 DiscLauncher Creator

**DiscLauncher Creator** is a lightweight tool that lets you create auto-launching game discs for PC using real physical media. You can generate `autorun.inf` and `launch_game.bat` files for either Steam games or emulator setups — and optionally burn them to a disc using **ImgBurn**.

---

##Demo

[![Watch the demo](https://img.youtube.com/vi/NmyrBc6criQ/hqdefault.jpg)](https://www.youtube.com/watch?v=NmyrBc6criQ)

---

## 🧰 Features

- 🔘 Supports both **Steam** games (via AppID) and **Emulator + ROM** combos
- 🎨 Optional custom disc label and icon (`.ico`)
- 📂 Auto-generates files to burn onto CD/DVD
- 💿 One-click **burn to disc with ImgBurn** or manual mode
- 🧪 Great for game collectors, launchers, kiosks, or fun gimmick projects
- Great for frontends such as [Playnite](https://playnite.link) or [Launchbox](https://www.launchbox-app.com) for that authentic home console experiance with retro physcial media.
---

## 📦 Requirements

- [Python 3.8+](https://www.python.org/downloads/)
- [ImgBurn](https://www.softpedia.com/get/CD-DVD-Tools/Data-CD-DVD-Burning/ImgBurn.shtml) (for burning discs automatically)(for manual burns use whatever burner you like)

---

## 🚀 How to Use

1. **Clone or Download** this repo:
    ```bash
    git clone https://github.com/yourusername/disclauncher.git
    cd disclauncher
    ```

2. **Install Python if needed**, then run the tool:
    ```bash
    python DiscLauncher_PLUS.py
    ```

3. In the app:
    - Select either `Steam Game` or `Emulator + ROM`
    - Fill in the relevant fields (AppID or Emulator/Game paths)
    - Optionally choose a `.ico` and label
    - Select burn mode or just generate files manually
    - Click `Generate Files Only` or `Generate & Burn`

4. If burning:
    - Insert a blank CD/DVD into your drive
    - Make sure ImgBurn path and drive letter are set correctly

---

## 📝 Notes

- `autorun.inf` works best with **physical discs**. Autorun is mostly disabled on USB drives.
- Windows 10/11 will prompt for permission when autorun triggers — this is normal and expected.
- You can edit `launch_game.bat` or `autorun.inf` manually if needed.
- Use [steamdb](https://steamdb.info) for getting steam app ids, or use steam themselves.
- Use [The Cover Project](https://www.thecoverproject.net/index.php) for getting sick images to print out for your new physical game collection.

---

## Common Issues

- "Why does the disk not autolaunch/autoplay/autorun"? Windows 8 and up removed this for security reasons, however you can turn it back on.
ControlPanel/Hardware and Sound/ AutoPlay/ Software and games/ Select Install or run program from your media
- "Where is my generated files?" Your desktop, it creates a folder for you.

---

## New features coming soon
- Other launcher support. Itch, GOG, EPIC, EA, and Ubisoft.
- Burn roms to disks to autolaunch without games and emulators on the pc.
- Better UI

---

## 📸 Screenshots

![image](https://github.com/user-attachments/assets/4e4e433d-581d-4f5e-82c3-5cd29a20bb61)




