# 💿 DiscLauncher Creator

**DiscLauncher Creator** is a lightweight tool that lets you create auto-launching game discs for PC using real physical media. You can generate `autorun.inf` and `launch_game.bat` files for either Steam games or emulator setups — and optionally burn them to a disc using **ImgBurn**.

## 🧰 Features

- 🔘 Supports both **Steam** games (via AppID) and **Emulator + ROM** combos
- 🎨 Optional custom disc label and icon (`.ico`)
- 📂 Auto-generates files to burn onto CD/DVD
- 💿 One-click **burn to disc with ImgBurn** or manual mode
- 🧪 Great for game collectors, launchers, kiosks, or fun gimmick projects

---

## 📦 Requirements

- [Python 3.8+](https://www.python.org/downloads/)
- [ImgBurn](https://www.softpedia.com/get/CD-DVD-Tools/Data-CD-DVD-Burning/ImgBurn.shtml) (for burning discs automatically)

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

---

## 📸 Screenshots

*Coming soon...*


