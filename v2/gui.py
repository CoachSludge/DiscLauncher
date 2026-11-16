"""DiscLauncher Studio: guided GUI for the v2 disc builder (Python 3.9+)."""
from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from disclauncher import build_bizhawk, build_steam

BG = "#0d111a"
PANEL = "#171e2b"
CARD = "#202a3a"
TEXT = "#f2f5fa"
MUTED = "#a5afc0"
ACCENT = "#72a5ff"


class Studio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DiscLauncher Studio  •  v2")
        self.geometry("900x730")
        self.minsize(760, 620)
        self.configure(bg=BG)
        self.mode = tk.StringVar(value="steam")
        self.values = {name: tk.StringVar() for name in (
            "label", "id", "appid", "emulator", "rom", "config", "icon", "output")}
        self.values["output"].set(str(Path.home() / "Desktop" / "DiscLauncher Discs" / "My Disc"))
        self.status = tk.StringVar(value="Ready to build")
        self.events = queue.Queue()
        self.busy = False
        self.last_output = None
        styles = ttk.Style(self)
        styles.theme_use("clam")
        styles.configure("Disc.TEntry", foreground=TEXT, fieldbackground="#111925",
                         bordercolor="#334055", padding=7)
        styles.configure("Disc.Horizontal.TProgressbar", troughcolor="#111925",
                         background=ACCENT)
        self.draw()
        self.after(100, self.poll)

    def text(self, parent, value, size=11, color=TEXT, bold=False, **opts):
        return tk.Label(parent, text=value, bg=parent["bg"], fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"),
                        anchor="w", **opts)

    def section(self, parent, number, name):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(14, 8))
        self.text(bar, number + "   ", 11, ACCENT, True).pack(side="left")
        self.text(bar, name, 13, TEXT, True).pack(side="left")

    def panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL, padx=18, pady=15,
                         highlightthickness=1, highlightbackground="#334055")
        frame.pack(fill="x", pady=(0, 9))
        return frame

    def field(self, parent, label, name, browse=None, help_text=None):
        self.text(parent, label, 10, TEXT, True).pack(anchor="w", pady=(0, 5))
        line = tk.Frame(parent, bg=PANEL)
        line.pack(fill="x", pady=(0, 12))
        ttk.Entry(line, textvariable=self.values[name], style="Disc.TEntry").pack(
            side="left", fill="x", expand=True)
        if browse:
            tk.Button(line, text="Browse…", command=lambda: self.browse(name, browse),
                      bg=CARD, fg=TEXT, relief="flat", padx=12, pady=5,
                      cursor="hand2").pack(side="left", padx=(8, 0))
        if help_text:
            self.text(parent, help_text, 9, MUTED, wraplength=600).pack(
                anchor="w", pady=(0, 10))

    def draw(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=26, pady=(20, 12))
        self.text(header, "◉  DISC LAUNCHER", 11, ACCENT, True).pack(anchor="w")
        self.text(header, "Make your digital library physical.", 23, TEXT, True).pack(
            anchor="w", pady=(5, 0))
        self.text(header, "Build a personalized game disc without touching a terminal.",
                  11, MUTED).pack(anchor="w")

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=26)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=bar.set)
        body = tk.Frame(canvas, bg=BG)
        anchor = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(anchor, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            -int(e.delta / 120), "units"))

        self.section(body, "01", "Select a disc type")
        choices = tk.Frame(body, bg=BG)
        choices.pack(fill="x", pady=(0, 10))
        self.cards = {}
        for mode, title, detail in (
            ("steam", "STEAM LAUNCH DISC", "Start an existing Steam game."),
            ("bizhawk", "PORTABLE EMULATOR DISC", "Package BizHawk and your game."),
        ):
            frame = tk.Frame(choices, bg=CARD, padx=15, pady=15,
                             highlightthickness=2, highlightbackground="#334055",
                             cursor="hand2")
            frame.pack(side="left", fill="both", expand=True, padx=(0, 10) if mode == "steam" else 0)
            title_label = self.text(frame, title, 10, TEXT, True)
            title_label.pack(anchor="w")
            detail_label = self.text(frame, detail, 10, MUTED)
            detail_label.pack(anchor="w", pady=(6, 0))
            for widget in (frame, title_label, detail_label):
                widget.bind("<Button-1>", lambda _, m=mode: self.select_mode(m))
            self.cards[mode] = (frame, title_label, detail_label)

        self.section(body, "02", "Game details")
        details = self.panel(body)
        self.field(details, "Disc label", "label")
        self.field(details, "Unique game ID", "id", help_text=(
            "Use letters, numbers, underscores or dashes. Saves are associated with this ID."))
        self.mode_fields = tk.Frame(details, bg=PANEL)
        self.mode_fields.pack(fill="x")
        self.field(details, "Disc icon (.ico) — optional", "icon", browse="icon")

        self.section(body, "03", "Choose your destination")
        destination = self.panel(body)
        self.field(destination, "Empty output folder", "output", browse="directory",
                   help_text="DiscLauncher will never replace a nonempty folder.")

        self.section(body, "04", "Create your disc")
        finish = self.panel(body)
        self.text(finish, "Generate a ready-to-burn disc folder.", 12, TEXT, True).pack(anchor="w")
        self.text(finish, "ISO creation and direct disc burning are planned, not yet available.",
                  10, MUTED).pack(anchor="w", pady=(4, 12))
        row = tk.Frame(finish, bg=PANEL)
        row.pack(fill="x")
        self.build = tk.Button(row, text="BUILD DISC FOLDER  →", command=self.start,
                               bg=ACCENT, fg="#091423", relief="flat",
                               font=("Segoe UI", 11, "bold"), padx=16, pady=11,
                               cursor="hand2")
        self.build.pack(side="left")
        self.open_folder = tk.Button(row, text="Open output folder", command=self.open_output,
                                     bg=CARD, fg=TEXT, relief="flat", padx=16, pady=11,
                                     state="disabled", cursor="hand2")
        self.open_folder.pack(side="left", padx=(12, 0))
        self.progress = ttk.Progressbar(finish, mode="indeterminate",
                                        style="Disc.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(16, 7))
        self.text(finish, "", 10, MUTED, textvariable=self.status).pack(anchor="w")
        self.text(body, "Use only games, firmware, and emulator files you may legally copy.",
                  9, MUTED).pack(anchor="w", pady=(10, 25))
        self.select_mode("steam")

    def select_mode(self, mode):
        self.mode.set(mode)
        for name, (frame, title, detail) in self.cards.items():
            active = name == mode
            frame.configure(bg="#243754" if active else CARD,
                            highlightbackground=ACCENT if active else "#334055")
            title.configure(bg=frame["bg"], fg=ACCENT if active else TEXT)
            detail.configure(bg=frame["bg"])
        for child in self.mode_fields.winfo_children():
            child.destroy()
        if mode == "steam":
            self.field(self.mode_fields, "Steam AppID", "appid",
                       help_text="The game's numeric Steam AppID, e.g. 22380 for Fallout: New Vegas.")
        else:
            self.field(self.mode_fields, "BizHawk folder", "emulator", browse="directory",
                       help_text="Select the directory containing EmuHawk.exe.")
            self.field(self.mode_fields, "ROM or game file", "rom", browse="rom")
            self.field(self.mode_fields, "BizHawk JSON config — optional",
                       "config", browse="config",
                       help_text="Configure save paths to a writable local directory before burning.")

    def browse(self, name, kind):
        if kind == "directory":
            result = filedialog.askdirectory(parent=self)
        else:
            filters = {"icon": [("Icon", "*.ico")],
                       "config": [("JSON", "*.json")],
                       "rom": [("Game files", "*.*")]}
            result = filedialog.askopenfilename(parent=self, filetypes=filters[kind])
        if result:
            self.values[name].set(result)

    def start(self):
        if self.busy:
            return
        fields = {key: value.get().strip() for key, value in self.values.items()}
        if not all(fields[name] for name in ("label", "id", "output")):
            messagebox.showwarning("Missing details", "Provide a label, game ID and output folder.", parent=self)
            return
        mode = self.mode.get()
        if mode == "steam" and not fields["appid"]:
            messagebox.showwarning("Missing AppID", "Enter a Steam AppID.", parent=self)
            return
        if mode == "bizhawk" and not fields["emulator"] and not fields["rom"]:
            messagebox.showwarning("Missing game files", "Choose your emulator and game file.", parent=self)
            return
        if mode == "bizhawk" and (not fields["emulator"] or not fields["rom"]):
            messagebox.showwarning("Missing game files", "Choose both a BizHawk folder and ROM.", parent=self)
            return
        self.busy = True
        self.build.configure(state="disabled", text="BUILDING…")
        self.open_folder.configure(state="disabled")
        self.status.set("Preparing disc files…")
        self.progress.start(12)
        threading.Thread(target=self.worker, args=(mode, fields), daemon=True).start()

    def worker(self, mode, f):
        try:
            path = Path(f["output"])
            icon = Path(f["icon"]) if f["icon"] else None
            if mode == "steam":
                result = build_steam(path, f["appid"], f["id"], f["label"], icon)
            else:
                config = Path(f["config"]) if f["config"] else None
                result = build_bizhawk(path, Path(f["emulator"]), Path(f["rom"]),
                                       f["id"], f["label"], config, icon)
            self.events.put(("success", result))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        try:
            while True:
                outcome, result = self.events.get_nowait()
                self.busy = False
                self.progress.stop()
                self.build.configure(state="normal", text="BUILD DISC FOLDER  →")
                if outcome == "success":
                    self.last_output = result
                    self.open_folder.configure(state="normal")
                    self.status.set("Disc folder ready: " + str(result))
                    messagebox.showinfo("Disc ready", "Built successfully!\n\n" + str(result),
                                        parent=self)
                else:
                    self.status.set("Build failed. Fix the issue and retry.")
                    messagebox.showerror("Build failed", result, parent=self)
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def open_output(self):
        if self.last_output and Path(self.last_output).is_dir():
            if os.name == "nt":
                os.startfile(self.last_output)
            else:
                messagebox.showinfo("Output location", str(self.last_output), parent=self)


if __name__ == "__main__":
    Studio().mainloop()
