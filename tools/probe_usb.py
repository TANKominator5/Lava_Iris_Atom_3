"""Request a checksum-valid version only; does not load FDLs or write partitions."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--libusb", type=Path, help="Explicit separately acquired libusb shared-library path")
    parser.add_argument("--wait", type=int, default=180)
    parser.add_argument("--acknowledge-usb-session", action="store_true", help="A version probe consumes a fresh boot-ROM session")
    args = parser.parse_args()
    if not args.acknowledge_usb_session:
        parser.error("Review docs/06-download-modes.md and pass --acknowledge-usb-session to contact USB")
    if not 1 <= args.wait <= 3600:
        parser.error("--wait must be between 1 and 3600 seconds")
    from usb_transport import LegacyUSB
    transport = LegacyUSB(args.libusb)
    try:
        transport.wait_fresh(args.wait)
        version = transport.ping()
        if version != b"SPRD3\0":
            raise RuntimeError("Version does not match this investigation's boot ROM")
        print("Checksum-verified boot-ROM version: SPRD3")
    finally:
        transport.close()


if __name__ == "__main__":
    main()
