"""DiscLauncher v2: build physical-disc folders without bundling copyrighted games.

Requires Python 3.9+. No third-party dependencies for the builder.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

APP_ID = re.compile(r"^[0-9]+$")
SLUG = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def require_directory(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"{label} must be an existing directory: {path}")
    return path


def require_file(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"{label} must be an existing file: {path}")
    return path


def safe_id(value: str) -> str:
    if not SLUG.fullmatch(value):
        raise ValueError("Disc ID must be 1-64 letters, numbers, underscores or hyphens")
    return value


def disc_label(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 32 or any(c in value for c in "\r\n[]=;"):
        raise ValueError("Disc label must be 1-32 characters without control/INI characters")
    return value


def prepare_output(output: Path) -> Path:
    output = output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output folder must be empty (will not overwrite): {output}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_autoplay(output: Path, label: str, icon: Path | None) -> None:
    data = ["[autorun]", f"label={label}"]
    if icon:
        shutil.copy2(require_file(icon, "Icon"), output / "disc.ico")
        data.append("icon=disc.ico")
    data += ["action=Launch game with DiscLauncher", "open=launch_game.cmd",
             "shell\\play=Play game", "shell\\play\\command=launch_game.cmd"]
    (output / "autorun.inf").write_text("\r\n".join(data) + "\r\n", encoding="utf-8")


def write_launcher(output: Path, mode: str) -> None:
    # Generated launcher stays on the disc. Only per-user config/save paths are writable.
    if mode == "steam":
        lines = [
            "@echo off", "setlocal", "cd /d \"%~dp0\"",
            "if not exist \"%ProgramFiles(x86)%\\Steam\\steam.exe\" if not exist \"%ProgramFiles%\\Steam\\steam.exe\" (",
            "  echo Steam may not be installed. Attempting Steam protocol launch...",
            ")",
            "start \"\" \"steam://rungameid/APPID_TOKEN\"",
            "exit /b 0",
        ]
    else:
        lines = [
            "@echo off", "setlocal", "cd /d \"%~dp0\"",
            "set \"DL_ROOT=%~dp0\"",
            "set \"DL_USER=%LOCALAPPDATA%\\DiscLauncher\\DISC_ID_TOKEN\"",
            "if not exist \"%DL_USER%\" mkdir \"%DL_USER%\"",
            "if errorlevel 1 (echo Cannot create local save folder. & exit /b 1)",
            "if not exist \"%DL_USER%\\config.json\" (",
            "  if exist \"%DL_ROOT%Config\\config.json\" copy /y \"%DL_ROOT%Config\\config.json\" \"%DL_USER%\\config.json\" >nul",
            ")",
            "if not exist \"%DL_ROOT%Emulator\\EmuHawk.exe\" (echo Missing BizHawk executable. & exit /b 1)",
            "pushd \"%DL_ROOT%Emulator\"",
            "\"%DL_ROOT%Emulator\\EmuHawk.exe\" --config=\"%DL_USER%\\config.json\" \"%DL_ROOT%Game\\ROM_TOKEN\"",
            "set \"DL_RESULT=%ERRORLEVEL%\"",
            "popd",
            "exit /b %DL_RESULT%",
        ]
    (output / "launch_game.cmd").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


def build_steam(output: Path, appid: str, game_id: str, label: str, icon: Path | None) -> Path:
    if not APP_ID.fullmatch(appid):
        raise ValueError("Steam AppID must contain digits only")
    safe_id(game_id)
    output = prepare_output(output)
    write_autoplay(output, disc_label(label), icon)
    write_launcher(output, "steam")
    launcher = output / "launch_game.cmd"
    launcher.write_text(launcher.read_text(encoding="utf-8").replace("APPID_TOKEN", appid), encoding="utf-8")
    manifest = {"schema": 1, "id": game_id, "label": label, "mode": "steam", "steam_appid": appid}
    (output / "disc.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def build_bizhawk(output: Path, emulator: Path, rom: Path, game_id: str,
                  label: str, config: Path | None, icon: Path | None) -> Path:
    safe_id(game_id)
    emulator = require_directory(emulator, "BizHawk folder")
    rom = require_file(rom, "Game/ROM")
    if not (emulator / "EmuHawk.exe").is_file():
        raise ValueError("BizHawk folder must contain EmuHawk.exe")
    if any(ch in rom.name for ch in '%"!^&|<>'):
        raise ValueError("ROM filename contains CMD-special characters; rename the file")
    if config is not None:
        config = require_file(config, "BizHawk JSON config")
        json.loads(config.read_text(encoding="utf-8"))
    output = output.expanduser().resolve()
    if output == emulator or output in emulator.parents or emulator in output.parents:
        raise ValueError("Output must not overlap the emulator folder")
    if output == rom.parent or output in rom.parents:
        raise ValueError("Output must not overlap the ROM folder")
    output = prepare_output(output)
    write_autoplay(output, disc_label(label), icon)
    shutil.copytree(emulator, output / "Emulator")
    (output / "Game").mkdir()
    shutil.copy2(rom, output / "Game" / rom.name)
    (output / "Config").mkdir()
    if config:
        shutil.copy2(config, output / "Config" / "config.json")
    else:
        (output / "Config" / "config.json").write_text("{}\n", encoding="utf-8")
    write_launcher(output, "bizhawk")
    launcher = output / "launch_game.cmd"
    script = launcher.read_text(encoding="utf-8").replace("DISC_ID_TOKEN", game_id).replace("ROM_TOKEN", rom.name)
    launcher.write_text(script, encoding="utf-8")
    manifest = {"schema": 1, "id": game_id, "label": label, "mode": "bizhawk",
                "emulator": "BizHawk", "rom": f"Game/{rom.name}",
                "config": "Config/config.json", "saves": "per-user-local"}
    (output / "disc.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Create DiscLauncher v2 disc folders")
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ("steam", "bizhawk"):
        p = sub.add_parser(mode)
        p.add_argument("--output", required=True, type=Path)
        p.add_argument("--id", required=True, dest="game_id")
        p.add_argument("--label", required=True)
        p.add_argument("--icon", type=Path)
        if mode == "steam":
            p.add_argument("--appid", required=True)
        else:
            p.add_argument("--emulator", required=True, type=Path, help="Folder containing EmuHawk.exe")
            p.add_argument("--rom", required=True, type=Path)
            p.add_argument("--config", type=Path, help="Optional BizHawk JSON config")
    args = parser.parse_args()
    try:
        if args.mode == "steam":
            result = build_steam(args.output, args.appid, args.game_id, args.label, args.icon)
        else:
            result = build_bizhawk(args.output, args.emulator, args.rom, args.game_id,
                                   args.label, args.config, args.icon)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Disc folder created: {result}")
    print("Review files, then create an ISO/burn using your preferred disc-burning program.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
