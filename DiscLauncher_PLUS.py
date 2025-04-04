
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from pathlib import Path

output_dir = Path(__file__).parent / "DiscLauncherOutput"
output_dir.mkdir(parents=True, exist_ok=True)

class DiscLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disc Launcher Creator")
        self.root.geometry("540x620")
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value="steam")
        self.burn_enabled = tk.BooleanVar(value=False)
        self.imgburn_path = tk.StringVar(value="C:\\Program Files (x86)\\ImgBurn\\ImgBurn.exe")
        self.burn_speed = tk.StringVar(value="4x")
        self.drive_letter = tk.StringVar(value="E:")

        tk.Label(root, text="💿 Disc Launcher Creator", font=("Segoe UI", 16, "bold")).pack(pady=10)

        mode_frame = tk.LabelFrame(root, text="Select Mode", padx=10, pady=5)
        mode_frame.pack(fill="x", padx=20)
        tk.Radiobutton(mode_frame, text="Steam Game", variable=self.mode, value="steam", command=self.update_mode).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Emulator + ROM", variable=self.mode, value="emulator", command=self.update_mode).pack(anchor="w")

        # Steam AppID
        self.appid_frame = tk.Frame(root)
        self.appid_label = tk.Label(self.appid_frame, text="Steam AppID:")
        self.appid_entry = tk.Entry(self.appid_frame, width=40)
        self.appid_label.pack(side="left")
        self.appid_entry.pack(side="left", padx=10)
        self.appid_frame.pack(pady=5)

        # Emulator + ROM
        self.emulator_frame = tk.Frame(root)
        self.emu_path_label = tk.Label(self.emulator_frame, text="Emulator Path:")
        self.emu_path_entry = tk.Entry(self.emulator_frame, width=40)
        self.emu_path_browse = tk.Button(self.emulator_frame, text="Browse", command=self.browse_emulator)
        self.emu_path_label.grid(row=0, column=0, sticky="w")
        self.emu_path_entry.grid(row=0, column=1, padx=5)
        self.emu_path_browse.grid(row=0, column=2)

        self.rom_path_label = tk.Label(self.emulator_frame, text="ROM/Game Path:")
        self.rom_path_entry = tk.Entry(self.emulator_frame, width=40)
        self.rom_path_browse = tk.Button(self.emulator_frame, text="Browse", command=self.browse_rom)
        self.rom_path_label.grid(row=1, column=0, sticky="w")
        self.rom_path_entry.grid(row=1, column=1, padx=5)
        self.rom_path_browse.grid(row=1, column=2)

        # Disc Label
        tk.Label(root, text="Disc Label:").pack()
        self.label_entry = tk.Entry(root)
        self.label_entry.pack(padx=20, fill="x", pady=5)

        # Icon
        tk.Label(root, text="Icon File (.ico):").pack()
        self.icon_path_entry = tk.Entry(root, width=50)
        self.icon_path_entry.pack(padx=20, fill="x")
        tk.Button(root, text="Browse Icon", command=self.browse_icon).pack(pady=5)

        # ImgBurn Settings
        burn_frame = tk.LabelFrame(root, text="Burn to Disc with ImgBurn", padx=10, pady=5)
        burn_frame.pack(fill="x", padx=20, pady=10)
        tk.Checkbutton(burn_frame, text="Burn after generating files", variable=self.burn_enabled).pack(anchor="w")
        tk.Label(burn_frame, text="ImgBurn Path:").pack(anchor="w")
        tk.Entry(burn_frame, textvariable=self.imgburn_path, width=60).pack()
        tk.Button(burn_frame, text="Browse for ImgBurn", command=self.browse_imgburn).pack(pady=2)
        tk.Label(burn_frame, text="Drive Letter (e.g., E:):").pack(anchor="w")
        tk.Entry(burn_frame, textvariable=self.drive_letter).pack()
        tk.Label(burn_frame, text="Burn Speed (e.g., 4x):").pack(anchor="w")
        tk.Entry(burn_frame, textvariable=self.burn_speed).pack()

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=15)
        tk.Button(button_frame, text="Generate Files Only", font=("Segoe UI", 10, "bold"), command=self.generate_files).pack(side="left", padx=10)
        tk.Button(button_frame, text="Generate & Burn", font=("Segoe UI", 10, "bold"), command=lambda: self.generate_files(burn=True)).pack(side="left", padx=10)

        self.update_mode()

    def update_mode(self):
        if self.mode.get() == "steam":
            self.appid_frame.pack(pady=5)
            self.emulator_frame.pack_forget()
        else:
            self.appid_frame.pack_forget()
            self.emulator_frame.pack(pady=5)

    def browse_icon(self):
        icon_path = filedialog.askopenfilename(filetypes=[("ICO files", "*.ico")])
        if icon_path:
            self.icon_path_entry.delete(0, tk.END)
            self.icon_path_entry.insert(0, icon_path)

    def browse_imgburn(self):
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if path:
            self.imgburn_path.set(path)

    def browse_rom(self):
        rom_path = filedialog.askopenfilename()
        if rom_path:
            self.rom_path_entry.delete(0, tk.END)
            self.rom_path_entry.insert(0, rom_path)

    def browse_emulator(self):
        emu_path = filedialog.askopenfilename()
        if emu_path:
            self.emu_path_entry.delete(0, tk.END)
            self.emu_path_entry.insert(0, emu_path)

    def generate_files(self, burn=False):
        label = self.label_entry.get().strip() or "Game Launcher"
        icon_file = self.icon_path_entry.get().strip()
        icon_name = Path(icon_file).name if icon_file else "default.ico"

        autorun_path = output_dir / "autorun.inf"
        bat_path = output_dir / "launch_game.bat"

        if icon_file and Path(icon_file).exists():
            icon_dest = output_dir / icon_name
            with open(icon_file, "rb") as src, open(icon_dest, "wb") as dst:
                dst.write(src.read())

        if self.mode.get() == "steam":
            appid = self.appid_entry.get().strip()
            if not appid.isdigit():
                messagebox.showerror("Error", "Invalid Steam AppID.")
                return
            bat_path.write_text(f"@echo off\nstart steam://rungameid/{appid}\nexit\n")
        else:
            emu_path = self.emu_path_entry.get().strip()
            rom_path = self.rom_path_entry.get().strip()
            if not os.path.exists(emu_path) or not os.path.exists(rom_path):
                messagebox.showerror("Error", "Emulator or ROM path is invalid.")
                return
            bat_path.write_text(
                f'@echo off\ncd /d "{os.path.dirname(emu_path)}"\nstart "" "{emu_path}" "{rom_path}"\nexit\n'
            )

        autorun_path.write_text(f"[autorun]\nlabel={label}\nicon={icon_name}\nopen=launch_game.bat\n")
        messagebox.showinfo("Success", f"Files generated in:\n{output_dir}")

        if burn:
            self.run_imgburn()

    def run_imgburn(self):
        exe = self.imgburn_path.get().strip()
        if not Path(exe).exists():
            messagebox.showerror("Error", "ImgBurn path is invalid.")
            return

        speed = self.burn_speed.get().strip()
        drive = self.drive_letter.get().strip()

        args = [
            exe,
            "/MODE", "BUILD",
            "/SRC", str(output_dir),
            "/DEST", drive,
            "/FILESYSTEM", "ISO9660+Joliet",
            "/SPEED", speed,
            "/START",
            "/CLOSE"
        ]

        try:
            subprocess.run(args, check=True)
            messagebox.showinfo("Burning Started", "ImgBurn is now burning the disc.")
        except Exception as e:
            messagebox.showerror("Burning Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscLauncherApp(root)
    root.mainloop()
