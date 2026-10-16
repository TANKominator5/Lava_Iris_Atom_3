"""Inspect/check legacy boot images locally. Never flashes or contacts a phone."""
import argparse
from pathlib import Path
import re

from boot_image import parse_boot, verify_patch
from common import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("--patched", type=Path)
    parser.add_argument("--magisk-init", type=Path, help="Required when verifying a patch")
    parser.add_argument("--partition-size", type=int, default=12 * 1024 * 1024)
    args = parser.parse_args()
    image = parse_boot(args.original)
    version = re.search(rb"Linux version [^\x00\n]+", image.kernel)
    print("Original SHA-256:", sha256(args.original))
    print("Kernel:", version.group().decode(errors="replace") if version else "not found in raw kernel")
    print("Page size:", image.page_size, "Ramdisk bytes:", image.ramdisk_size, "Extra bytes:", len(image.extra))
    if args.patched:
        if args.magisk_init is None:
            parser.error("--patched requires --magisk-init")
        verify_patch(args.original, args.patched, args.magisk_init, args.partition_size)
        print("Verified unchanged kernel/device tree/fstab/default properties and expected Magisk init/configuration")
        print("Patched SHA-256:", sha256(args.patched))


if __name__ == "__main__":
    main()
