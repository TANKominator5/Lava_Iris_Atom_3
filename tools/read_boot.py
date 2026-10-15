"""Experimental Iris Atom 3 double boot readback; runs vendor RAM loaders, never flashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct

from common import private_output, sha256

PARTITION_SIZE = 12 * 1024 * 1024
LOADERS = (
    ("fdl1", 0x50000000, 20797, "b3c6873300387bc00564248590983c13f48e9b5dbb07b65430faee3134081504"),
    ("fdl2", 0x9f000000, 488512, "ea8f7a8c15f571b254f812f8240cbb8b90e69a00d344ad779937282e2575aa54"),
)


def load_ram(transport, data, address, *, first):
    transport.request(1, struct.pack(">II", address, len(data)))
    for offset in range(0, len(data), 528):
        transport.request(2, data[offset:offset + 528])
    transport.request(3)
    try:
        transport.request(4, expected=(0x80, 0x96), seconds=15)
    except (TimeoutError, transport.core.USBError):
        if not first:
            raise  # Do not treat arbitrary FDL2 failures as permission to continue.
        # FDL1 execution can invalidate the old USB handle. Its new version must verify below.
    if first:
        transport.refresh()
        transport.crc = False
        version = transport.ping()
        if version != b"Spreadtrum Boot Block version 1.1\0":
            raise RuntimeError("Unexpected FDL1 identity; stopping before FDL2")
        print("Verified FDL1 version 1.1", flush=True)


def dump_boot(transport, target):
    partial = target.with_suffix(".img.partial")
    if target.exists() or partial.exists():
        raise FileExistsError("Readback output or partial output already exists")
    transport.request(0x10, "boot".encode("utf-16le").ljust(72, b"\0") + struct.pack("<I", PARTITION_SIZE))
    digest = hashlib.sha256()
    with partial.open("xb") as output:
        for offset in range(0, PARTITION_SIZE, 4096):
            data = transport.request(0x11, struct.pack("<II", 4096, offset), expected=(0x93,))
            if len(data) != 4096:
                raise RuntimeError("Short boot read; incomplete data retained as .partial")
            output.write(data)
            digest.update(data)
            if offset % (1024 * 1024) == 0:
                print(f"{target.name}: {offset // 1024} / {PARTITION_SIZE // 1024} KiB", flush=True)
        output.flush()
        os.fsync(output.fileno())
    transport.request(0x12)
    if target.exists():
        raise FileExistsError("Another process created the target; keeping .partial")
    # An exclusive destination copy prevents overwriting a backup even on POSIX.
    with partial.open("rb") as source, target.open("xb") as destination:
        while data := source.read(1024 * 1024):
            destination.write(data)
        destination.flush()
        os.fsync(destination.fileno())
    if sha256(target) != digest.hexdigest():
        raise RuntimeError("Readback copy hash mismatch; retain both files for inspection")
    partial.unlink()
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fdl1", required=True, type=Path)
    parser.add_argument("--fdl2", required=True, type=Path)
    parser.add_argument("--libusb", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New private directory")
    parser.add_argument("--wait", type=int, default=180)
    parser.add_argument("--acknowledge-loader-risk", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_loader_risk:
        parser.error("Loading a vendor FDL runs privileged code. Read docs/08-ram-loaders.md and acknowledge the risk")
    if not 1 <= args.wait <= 3600:
        parser.error("--wait must be between 1 and 3600 seconds")
    loader_data = []
    for name, address, size, expected in LOADERS:
        path = getattr(args, name)
        if path.stat().st_size != size or sha256(path) != expected:
            parser.error(f"{name} does not match the model-specific loader used in this investigation")
        loader_data.append((path.read_bytes(), address))
    output = private_output(args.output)
    output.mkdir(parents=True, exist_ok=False)
    from usb_transport import LegacyUSB
    transport = LegacyUSB(args.libusb)
    try:
        transport.wait_fresh(args.wait)
        if transport.ping() != b"SPRD3\0":
            raise RuntimeError("Unexpected boot ROM")
        transport.request(0)
        load_ram(transport, *loader_data[0], first=True)
        transport.request(0)
        load_ram(transport, *loader_data[1], first=False)
        first = dump_boot(transport, output / "original_boot.img")
        second = dump_boot(transport, output / "original_boot_verify.img")
        if first != second:
            raise RuntimeError("Independent readbacks differ; DO NOT PATCH OR FLASH")
        with (output / "readback-result.json").open("x", encoding="utf-8") as target:
            json.dump({"bytes_per_read": PARTITION_SIZE, "sha256": first, "matching_independent_reads": True}, target, indent=2)
        print(f"Two matching complete boot reads: {first}")
        print("No flash-write command issued. Disconnect and cold-restart the removable-battery unit normally.")
    finally:
        transport.close()


if __name__ == "__main__":
    main()
