"""Compare two independent full boot-partition backups, never modifying either."""
import argparse
from pathlib import Path

from common import sha256


def compare(first, second, size=12 * 1024 * 1024):
    first, second = Path(first), Path(second)
    if first.resolve() == second.resolve() or first.samefile(second):
        raise ValueError("Provide two independent files, not one file twice")
    if first.stat().st_size != size or second.stat().st_size != size:
        raise ValueError("A backup does not match the expected partition size")
    first_hash, second_hash = sha256(first), sha256(second)
    if first_hash != second_hash:
        raise ValueError("Independent backups differ")
    return first_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--size", type=int, default=12 * 1024 * 1024)
    args = parser.parse_args()
    print("Matching complete independent copies:", compare(args.first, args.second, args.size))


if __name__ == "__main__":
    main()
