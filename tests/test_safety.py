import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from common import private_output, require_hash


class SafetyTests(unittest.TestCase):
    def test_private_output_boundary(self):
        with self.assertRaises(ValueError):
            private_output(ROOT / "evidence" / "device.json")
        self.assertEqual(private_output(ROOT / "_local" / "device.json"), ROOT / "_local" / "device.json")

    def test_hash_input(self):
        self.assertEqual(require_hash("A" * 64), "a" * 64)
        with self.assertRaises(ValueError):
            require_hash("1234")

    def test_imports_do_not_contact_device(self):
        with patch.object(subprocess, "run", side_effect=AssertionError("Device command on import")):
            for module in ("collect_baseline", "inspect_pac", "probe_usb", "read_boot", "verify_boot", "verify_root", "prepare_magisk"):
                importlib.reload(importlib.import_module(module))

    def test_usb_cli_requires_ack_before_importing_pyusb(self):
        for script, arguments in (
            ("probe_usb.py", []),
            ("read_boot.py", ["--fdl1", "unused", "--fdl2", "unused", "--output", "unused"]),
        ):
            result = subprocess.run([sys.executable, str(ROOT / "tools" / script), *arguments], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("acknowledge", result.stderr.lower())

    def test_prepare_rejects_wrong_apk_without_creating_output(self):
        from prepare_magisk import extract
        with tempfile.TemporaryDirectory() as temporary:
            source, output = Path(temporary) / "bad.apk", Path(temporary) / "output"
            source.write_bytes(b"not an official APK")
            with self.assertRaises(ValueError):
                extract(source, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
