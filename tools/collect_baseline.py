"""Read Android identity/boot diagnostics; never reboot or change settings."""
import argparse
import json
from pathlib import Path
import subprocess

from common import private_output

QUERIES = {
    "build": "getprop ro.build.display.id",
    "fingerprint": "getprop ro.build.fingerprint",
    "abi": "getprop ro.product.cpu.abi",
    "kernel": "cat /proc/version",
    "boot_completed": "getprop sys.boot_completed",
    "partitions": "cat /proc/partitions",
    "boot_identity": "cat /sys/class/block/mmcblk0p16/uevent /sys/class/block/mmcblk0p16/size",
    "memory": "cat /proc/meminfo /proc/swaps",
    "selinux": "getenforce",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="Explicit serial from adb devices")
    parser.add_argument("--output", type=Path, required=True, help="New private JSON file, e.g. _local/baseline.json")
    parser.add_argument("--root", action="store_true", help="Also request interactive Shell root permission for id")
    args = parser.parse_args()
    output = private_output(args.output)
    if output.exists():
        parser.error("Refusing to overwrite an existing baseline")
    records = {}
    for name, command in {**QUERIES, **({"root": "su -c id"} if args.root else {})}.items():
        result = subprocess.run(["adb", "-s", args.serial, "shell", command], capture_output=True,
                                text=True, errors="replace", timeout=60)
        records[name] = {"command": command, "returncode": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as target:
        json.dump(records, target, indent=2)
    print(f"Saved private baseline to {output}; review query exit codes before relying on results")


if __name__ == "__main__":
    main()
