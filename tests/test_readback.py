from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import contextlib
import io

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from common import sha256
from read_boot import dump_boot, load_ram


class FakeUSBError(Exception):
    pass


class FakeTransport:
    core = SimpleNamespace(USBError=FakeUSBError)

    def __init__(self, execution_error=None):
        self.calls = []
        self.execution_error = execution_error
        self.refreshed = False
        self.crc = True

    def request(self, command, payload=b"", **kwargs):
        self.calls.append((command, payload))
        if command == 4 and self.execution_error:
            raise self.execution_error
        if command == 0x11:
            return b"r" * 4096
        return b""

    def refresh(self):
        self.refreshed = True

    def ping(self):
        return b"Spreadtrum Boot Block version 1.1\0"


class ReadbackTests(unittest.TestCase):
    def test_ram_chunks_and_verified_first_stage_transition(self):
        transport = FakeTransport(FakeUSBError("re-enumerated"))
        with contextlib.redirect_stdout(io.StringIO()):
            load_ram(transport, b"a" * 1057, 0x50000000, first=True)
        self.assertEqual([command for command, _ in transport.calls], [1, 2, 2, 2, 3, 4])
        self.assertEqual([len(payload) for command, payload in transport.calls if command == 2], [528, 528, 1])
        self.assertTrue(transport.refreshed)
        self.assertFalse(transport.crc)

    def test_explicit_loader_rejection_is_not_hidden(self):
        transport = FakeTransport(RuntimeError("loader rejected"))
        with self.assertRaises(RuntimeError):
            load_ram(transport, b"a", 0x50000000, first=True)
        self.assertFalse(transport.refreshed)

    def test_fdl2_usb_errors_stop_instead_of_guessing(self):
        with self.assertRaises(FakeUSBError):
            load_ram(FakeTransport(FakeUSBError("lost")), b"a", 0x9f000000, first=False)

    def test_complete_dump_does_not_expose_a_writer(self):
        with tempfile.TemporaryDirectory() as directory, patch("read_boot.PARTITION_SIZE", 8192), \
             contextlib.redirect_stdout(io.StringIO()):
            target = Path(directory) / "boot.img"
            transport = FakeTransport()
            digest = dump_boot(transport, target)
            self.assertEqual(target.stat().st_size, 8192)
            self.assertEqual(digest, sha256(target))
            self.assertFalse(target.with_suffix(".img.partial").exists())
            self.assertEqual([command for command, _ in transport.calls], [0x10, 0x11, 0x11, 0x12])
            with self.assertRaises(FileExistsError):
                dump_boot(transport, target)
            self.assertEqual(digest, sha256(target))

    def test_existing_partial_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "boot.img"
            partial = target.with_suffix(".img.partial")
            partial.write_bytes(b"prior attempt")
            transport = FakeTransport()
            with self.assertRaises(FileExistsError):
                dump_boot(transport, target)
            self.assertFalse(transport.calls)
            self.assertEqual(partial.read_bytes(), b"prior attempt")


if __name__ == "__main__":
    unittest.main()
