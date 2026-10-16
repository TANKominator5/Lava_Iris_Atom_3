"""Verify the recorded rooting outcome through explicit ADB/root queries; no writes."""
import argparse
import re
import subprocess

from common import require_hash


def query(serial, command):
    result = subprocess.run(["adb", "-s", serial, "shell", command], capture_output=True,
                            text=True, errors="replace", timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"Query failed: {command}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--expected-boot-sha256", required=True, type=require_hash)
    args = parser.parse_args()
    if query(args.serial, "getprop sys.boot_completed") != "1":
        raise RuntimeError("Wait for Android boot completion before verifying root")
    build = query(args.serial, "getprop ro.build.display.id")
    if build != "Lava_iris_Atom_3_S111_20160303":
        raise RuntimeError("Installed build differs from this investigation")
    identity = query(args.serial, "su -c id")
    if "uid=0(root)" not in identity or "u:r:magisk:s0" not in identity:
        raise RuntimeError("Root or expected SELinux root context not verified")
    version = query(args.serial, "/sbin/magisk -v")
    if version.splitlines()[-1] != "24.3:MAGISK":
        raise RuntimeError("Magisk core is not the tested v24.3")
    metadata = query(args.serial, "cat /sys/class/block/mmcblk0p16/uevent /sys/class/block/mmcblk0p16/size")
    if "PARTNAME=boot" not in metadata.splitlines() or metadata.splitlines()[-1] != "24576":
        raise RuntimeError("Boot identity/sector count differs; refusing to hash a guessed partition")
    hash_output = query(args.serial, "su -c '/data/adb/magisk/busybox sha256sum /dev/block/mmcblk0p16'")
    if not re.search(r"(?m)^" + args.expected_boot_sha256 + r"\s+/dev/block/mmcblk0p16\s*$", hash_output):
        raise RuntimeError("Installed boot hash does not match the expected checked image")
    enforcing = query(args.serial, "su -c getenforce")
    if enforcing.splitlines()[-1] != "Enforcing":
        raise RuntimeError("SELinux is not Enforcing")
    package = query(args.serial, "dumpsys package com.topjohnwu.magisk")
    if "versionName=24.3" not in package:
        raise RuntimeError("Manager version differs from tested core")
    print(identity)
    print("Matching v24.3 core/app, original build, checked boot image and SELinux Enforcing verified")
    print("For persistence, repeat this check after a normal reboot; this tool does not reboot for you")


if __name__ == "__main__":
    main()
