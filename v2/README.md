# DiscLauncher v2 — initial foundation

This is the first incremental v2 implementation. The legacy `DiscLauncher_PLUS.py` GUI remains unchanged and usable.

## Requirements

- Python 3.9+ **on the builder computer**
- Windows on the target computer
- For emulation mode: your own portable BizHawk directory (including dependencies), and a game file you are permitted to copy

The generated disc launcher is a Windows `.cmd` file and does **not** require Python on the target computer. The disc does not automatically execute on most Windows 10/11 installations; use AutoPlay if offered or open `launch_game.cmd` manually.

## Steam shortcut disc

```powershell
python v2/disclauncher.py steam --appid 22380 --id fallout-new-vegas --label "Fallout New Vegas" --output ./out/new-vegas
```

This produces a disc with `autorun.inf`, `launch_game.cmd` and `disc.json`. It **does not** copy game files, install games, or implement its own ownership check. Steam handles its own normal launch flow.

## Self-contained BizHawk disc

```powershell
python v2/disclauncher.py bizhawk --emulator "C:\\Emulators\\BizHawk" --rom "C:\\Games\\Example.gba" --id gba-example --label "GBA Example" --config "C:\\Profiles\\bizhawk.json" --output ./out/gba-example
```

Builds:

```text
out/gba-example/
  autorun.inf
  launch_game.cmd
  disc.json
  Emulator/        # copied BizHawk folder
  Game/            # copied game file
  Config/          # configuration template
```

The on-disc launcher copies its config template on first run to `%LOCALAPPDATA%\\DiscLauncher\\<id>\\config.json`, then invokes BizHawk with the ROM stored on disc. The emulator is launched from its own folder. BizHawk's other mutable folders (save RAM, states, logs, etc.) **must** also be configured for writable local paths before using a read-only disc; merely supplying `--config` does not automatically redirect those paths. Consider first testing from a read-only mounted ISO. Some emulator distributions and plugins cannot be run read-only without extra setup.

## Current limitations and next steps

- CLI builder; new UI and emulator adapter architecture are still planned.
- No ISO creation, burning, post-burn verification, or installed-game packaging yet.
- No automatic per-emulator save-location patching yet. Make sure your emulator's config redirects saves to writable paths.
- No automatic handling of missing emulator dependencies or BIOS/firmware.
- Disc assets are user-supplied; check relevant game, emulator and firmware redistribution licenses.
- Output must be empty to prevent stale assets from prior builds entering the next disc.

## Safety

Review `launch_game.cmd` before burning. Do not encourage Windows users to disable AutoPlay security restrictions. Avoid distributing commercial game files or firmware you lack permission to distribute.
