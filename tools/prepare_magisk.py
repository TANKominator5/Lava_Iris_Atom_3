"""Extract only reviewed ARM tools from a separately acquired official Magisk v24.3 APK."""
import argparse
from pathlib import Path
import zipfile

from common import private_output, sha256

EXPECTED_APK = "8e37f8119b03a2d3289cb8dd5b484ca67dd9e76c84b29fc9d6fe5f741a1b8916"
MEMBERS = {
    "assets/boot_patch.sh": "boot_patch.sh",
    "assets/util_functions.sh": "util_functions.sh",
    "assets/addon.d.sh": "addon.d.sh",
    "lib/armeabi-v7a/libmagiskboot.so": "magiskboot",
    "lib/armeabi-v7a/libmagiskinit.so": "magiskinit",
    "lib/armeabi-v7a/libmagisk32.so": "magisk32",
    "lib/armeabi-v7a/libbusybox.so": "busybox",
}


def extract(apk, output):
    if sha256(apk) != EXPECTED_APK:
        raise ValueError("APK does not match the official v24.3 artifact recorded here")
    with zipfile.ZipFile(apk) as archive:
        content = {}
        for member, filename in MEMBERS.items():
            info = archive.getinfo(member)
            if not 0 < info.file_size < 8 * 1024 * 1024:
                raise ValueError("Unexpected member size")
            content[filename] = archive.read(member)
    target = private_output(output)
    target.mkdir(parents=True, exist_ok=False)
    for filename, data in {**content, "magisk": content["magisk32"]}.items():
        with (target / filename).open("xb") as stream:
            stream.write(data)
    print("Extracted v24.3 ARM tools only; no binary has been executed or installed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    extract(args.apk, args.output)


if __name__ == "__main__":
    main()
