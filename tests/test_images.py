import gzip
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from boot_image import align, newc_files, parse_boot, verify_patch
from compare_backups import compare
from inspect_pac import list_pac, safe_filename


def cpio(entries):
    output = bytearray()
    for name, data in list(entries.items()) + [("TRAILER!!!", b"")]:
        encoded = name.encode() + b"\0"
        fields = [0, 0o100644, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(encoded), 0]
        output.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields) + encoded)
        output.extend(b"\0" * (-len(output) % 4))
        output.extend(data)
        output.extend(b"\0" * (-len(output) % 4))
    return bytes(output)


def image(entries, kernel=b"Linux version test\0", extra=b"device-tree"):
    page = 2048
    ramdisk = gzip.compress(cpio(entries), mtime=0)
    header = bytearray(page)
    header[:8] = b"ANDROID!"
    struct.pack_into("<9I", header, 8, len(kernel), 0, len(ramdisk), 0, 0, 0, 0, page, len(extra))
    data = bytes(header) + kernel.ljust(align(len(kernel), page), b"\0") + ramdisk.ljust(align(len(ramdisk), page), b"\0") + extra
    return data.ljust(8192, b"\0")


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stock_files = {"init": b"stock-init", "fstab.sc8830": b"fstab", "default.prop": b"properties"}

    def write(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_valid_patch(self):
        original = self.write("original.img", image(self.stock_files))
        files = {**self.stock_files, "init": b"magisk-init", ".backup/init": b"stock-init",
                 ".backup/.magisk": b"KEEPVERITY=true\nKEEPFORCEENCRYPT=true\nRECOVERYMODE=false\n",
                 "overlay.d/sbin/magisk32.xz": b"payload"}
        patched = self.write("patched.img", image(files))
        init = self.write("magiskinit", b"magisk-init")
        self.assertEqual(verify_patch(original, patched, init, 8192).files["init"], b"magisk-init")
        changed = self.write("changed.img", image(files, kernel=b"unexpected"))
        with self.assertRaises(ValueError):
            verify_patch(original, changed, init, 8192)

    def test_truncated_and_oversize_components(self):
        data = bytearray(image(self.stock_files))
        struct.pack_into("<I", data, 8, 1000000)
        with self.assertRaises(ValueError):
            parse_boot(self.write("truncated.img", data))
        with self.assertRaises(ValueError):
            newc_files(cpio(self.stock_files)[:30])

    def test_duplicate_cpio_entry_rejected(self):
        entry = cpio({"init": b"one"})
        trailer_start = entry.index(b"070701", 6)
        with self.assertRaises(ValueError):
            newc_files(entry[:trailer_start] + entry)

    def test_full_backup_comparison(self):
        first = self.write("first.img", b"1234")
        second = self.write("second.img", b"1234")
        self.assertEqual(len(compare(first, second, 4)), 64)
        with self.assertRaises(ValueError):
            compare(first, first, 4)
        with self.assertRaises(ValueError):
            compare(first, second, 8)
        second.write_bytes(b"1235")
        with self.assertRaises(ValueError):
            compare(first, second, 4)

    def test_pac_paths_and_truncation(self):
        for name in ("../boot.img", "..", "x:boot.img", "dir\\boot.img", "boot.img."):
            self.assertFalse(safe_filename(name))
        self.assertTrue(safe_filename("boot.img"))
        with self.assertRaises(ValueError):
            list_pac(self.write("bad.pac", b"no"))

    def test_legacy_pac_directory(self):
        header = bytearray(2124)
        struct.pack_into("<II", header, 1076, 1, 2124)
        struct.pack_into("<I", header, 2116, 0xfffafffa)
        entry = bytearray(2580)
        struct.pack_into("<I", entry, 0, len(entry))
        entry[4:12] = "BOOT".encode("utf-16le")
        entry[516:532] = "boot.img".encode("utf-16le")
        struct.pack_into("<I", entry, 1540, 4)
        struct.pack_into("<I", entry, 1552, len(header) + len(entry))
        _, entries = list_pac(self.write("test.pac", header + entry + b"boot"))
        self.assertEqual(entries[0].identifier, "BOOT")
        self.assertEqual(entries[0].size, 4)


if __name__ == "__main__":
    unittest.main()
