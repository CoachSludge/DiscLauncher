"""Run with: python -m unittest discover -s v2/tests -v"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "disclauncher.py"
spec = importlib.util.spec_from_file_location("disclauncher_v2", SOURCE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuilderTests(unittest.TestCase):
    def test_steam_manifest_and_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            builder.build_steam(output, "22380", "fallout-new-vegas", "Fallout New Vegas", None)
            data = json.loads((output / "disc.json").read_text())
            self.assertEqual(data["steam_appid"], "22380")
            self.assertIn("steam://rungameid/22380", (output / "launch_game.cmd").read_text())
            self.assertTrue((output / "autorun.inf").is_file())

    def test_never_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            (output / "important.txt").write_text("keep")
            with self.assertRaises(ValueError):
                builder.build_steam(output, "22380", "fnv", "New Vegas", None)
            self.assertEqual((output / "important.txt").read_text(), "keep")

    def test_reject_invalid_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                builder.build_steam(Path(tmp) / "out", "22380 & calc", "bad", "Game", None)
            with self.assertRaises(ValueError):
                builder.build_steam(Path(tmp) / "out", "22380", "bad&name", "Game", None)

    def test_bizhawk_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            emulator = base / "bizhawk"
            emulator.mkdir()
            (emulator / "EmuHawk.exe").write_bytes(b"fake executable")
            rom = base / "game.gba"
            rom.write_bytes(b"fake rom")
            output = base / "output"
            builder.build_bizhawk(output, emulator, rom, "my-game", "My Game", None, None)
            self.assertEqual((output / "Game" / "game.gba").read_bytes(), b"fake rom")
            self.assertTrue((output / "Emulator" / "EmuHawk.exe").is_file())
            self.assertIn("my-game", (output / "launch_game.cmd").read_text())
            self.assertEqual(json.loads((output / "disc.json").read_text())["mode"], "bizhawk")


if __name__ == "__main__":
    unittest.main()
