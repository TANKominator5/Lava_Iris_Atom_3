"""Strict parser for the legacy raw-kernel/gzip-ramdisk boot layout observed here."""
from dataclasses import dataclass
from pathlib import Path
import struct
import zlib

MAX_IMAGE = 64 * 1024 * 1024
MAX_RAMDISK = 64 * 1024 * 1024


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def newc_files(data):
    offset = 0
    files = {}
    while offset + 110 <= len(data):
        if data[offset:offset + 6] != b"070701":
            raise ValueError("Only newc archives without per-entry CRC are supported")
        try:
            fields = [int(data[offset + 6 + index * 8:offset + 14 + index * 8], 16) for index in range(13)]
        except ValueError as error:
            raise ValueError("Invalid newc numeric field") from error
        size, name_size = fields[6], fields[11]
        name_start = offset + 110
        name_end = name_start + name_size
        if not 1 <= name_size <= 4096 or name_end > len(data) or data[name_end - 1] != 0:
            raise ValueError("Invalid newc filename")
        name = data[name_start:name_end - 1].decode("utf-8")
        start = align(name_end, 4)
        end = start + size
        if end > len(data):
            raise ValueError("Truncated newc entry")
        if name == "TRAILER!!!":
            return files
        if name in files:
            raise ValueError("Duplicate newc entry")
        files[name] = data[start:end]
        offset = align(end, 4)
    raise ValueError("Missing newc trailer")


@dataclass
class BootImage:
    raw: bytes
    kernel: bytes
    extra: bytes
    files: dict
    page_size: int
    ramdisk_size: int


def parse_boot(path):
    source = Path(path)
    if not 608 <= source.stat().st_size <= MAX_IMAGE:
        raise ValueError("Image size outside supported legacy bounds")
    data = source.read_bytes()
    if data[:8] != b"ANDROID!":
        raise ValueError("Missing Android header at byte zero")
    kernel_size, _, ramdisk_size, _, second_size, _, _, page, extra_size = struct.unpack_from("<9I", data, 8)
    if page not in (2048, 4096, 8192, 16384) or second_size or not kernel_size or not ramdisk_size:
        raise ValueError("Unsupported legacy boot geometry (requires a kernel/ramdisk and no second stage)")
    # Offset 40 is the vendor legacy extra-size field here, not a modern header version.
    ramdisk_start = page + align(kernel_size, page)
    extra_start = ramdisk_start + align(ramdisk_size, page)
    if page + kernel_size > len(data) or ramdisk_start + ramdisk_size > len(data) or extra_start + extra_size > len(data):
        raise ValueError("Image components extend beyond the file")
    decompressor = zlib.decompressobj(31)
    unpacked = decompressor.decompress(data[ramdisk_start:ramdisk_start + ramdisk_size], MAX_RAMDISK + 1)
    if len(unpacked) > MAX_RAMDISK or not decompressor.eof or decompressor.unused_data:
        raise ValueError("Truncated, concatenated or oversized gzip ramdisk")
    return BootImage(data, data[page:page + kernel_size], data[extra_start:extra_start + extra_size],
                     newc_files(unpacked), page, ramdisk_size)


def verify_patch(original, patched, magisk_init, partition_size=12 * 1024 * 1024):
    stock, modified = parse_boot(original), parse_boot(patched)
    if len(stock.raw) != partition_size or len(modified.raw) > partition_size:
        raise ValueError("Original is not a full partition read or patch exceeds partition size")
    if stock.kernel != modified.kernel or stock.extra != modified.extra:
        raise ValueError("Kernel or device-tree/extra payload changed")
    # Only ramdisk size and the legacy image-ID digest should change in this header.
    before, after = bytearray(stock.raw[:stock.page_size]), bytearray(modified.raw[:modified.page_size])
    for header in (before, after):
        header[16:20] = b"\0" * 4
        header[576:608] = b"\0" * 32
    if before != after:
        raise ValueError("Unexpected boot header changes")
    for name in ("fstab.sc8830", "default.prop"):
        if name not in stock.files or modified.files.get(name) != stock.files[name]:
            raise ValueError(f"Missing or changed {name}")
    if modified.files.get(".backup/init") != stock.files.get("init") or "init" not in stock.files:
        raise ValueError("Original init was not backed up correctly")
    if modified.files.get("init") != Path(magisk_init).read_bytes() or modified.files["init"] == stock.files["init"]:
        raise ValueError("Patched init does not match the supplied Magisk init")
    if not modified.files.get("overlay.d/sbin/magisk32.xz"):
        raise ValueError("Magisk32 payload missing")
    config = modified.files.get(".backup/.magisk", b"").splitlines()
    for flag in (b"KEEPVERITY=true", b"KEEPFORCEENCRYPT=true", b"RECOVERYMODE=false"):
        if flag not in config:
            raise ValueError(f"Missing preservation/configuration flag: {flag!r}")
    return modified
