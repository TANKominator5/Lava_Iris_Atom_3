"""List/selectively extract the specific legacy Spreadtrum PAC format; no device access."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import struct

from common import private_output, sha256


def uint32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def text(data):
    return data.decode("utf-16le").split("\0", 1)[0]


@dataclass
class Entry:
    identifier: str
    filename: str
    size: int
    offset: int


def list_pac(path):
    source = Path(path)
    total = source.stat().st_size
    with source.open("rb") as stream:
        header = stream.read(2124)
        if len(header) != 2124 or uint32(header, 2116) != 0xfffafffa:
            raise ValueError("Not the supported legacy PAC header")
        count, directory = uint32(header, 1076), uint32(header, 1080)
        if not 0 < count < 1024 or directory != 2124:
            raise ValueError("Unsupported PAC directory")
        stream.seek(directory)
        entries = []
        for _ in range(count):
            prefix = stream.read(4)
            if len(prefix) != 4:
                raise ValueError("Truncated PAC directory")
            length = uint32(prefix, 0)
            if not 1584 <= length <= 65536:
                raise ValueError("Unexpected PAC record size")
            record = prefix + stream.read(length - 4)
            if len(record) != length:
                raise ValueError("Truncated PAC record")
            size = (uint32(record, 1532) << 32) | uint32(record, 1540)
            offset = (uint32(record, 1536) << 32) | uint32(record, 1552)
            if offset + size > total:
                raise ValueError("PAC payload extends beyond file")
            entries.append(Entry(text(record[4:516]), text(record[516:1028]), size, offset))
        if any(entry.size and entry.offset < stream.tell() for entry in entries):
            raise ValueError("PAC payload overlaps its directory")
    return {"product": text(header[52:564]), "version": text(header[564:1076])}, entries


def safe_filename(name):
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{number}" for number in range(1, 10)), *(f"LPT{number}" for number in range(1, 10))}
    return (bool(name) and name not in (".", "..") and not any(character in name for character in '/\\:<>"|?*')
            and not name.endswith((".", " ")) and name.split(".", 1)[0].upper() not in reserved
            and not any(ord(character) < 32 for character in name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pac", type=Path)
    parser.add_argument("--extract", nargs="+", metavar="ID", help="Select IDs, e.g. FDL FDL2 BOOT Recovery; no default extraction")
    parser.add_argument("--output", type=Path, help="New private directory, e.g. _local/stock")
    args = parser.parse_args()
    metadata, entries = list_pac(args.pac)
    print(metadata)
    for entry in entries:
        print(f"{entry.identifier:18} {entry.size:12} {entry.offset:12} {entry.filename}")
    if not args.extract:
        return
    if args.output is None:
        parser.error("--extract requires --output")
    wanted = {name.lower() for name in args.extract}
    allowed = {"fdl", "fdl1", "fdl2", "boot", "recovery"}
    if not wanted <= allowed:
        parser.error("Only FDL/FDL1/FDL2/BOOT/Recovery extraction is exposed")
    selected = [entry for entry in entries if entry.identifier.lower() in wanted and entry.size]
    if {entry.identifier.lower() for entry in selected} != wanted:
        parser.error("An exact requested ID was not found")
    names = [entry.filename.casefold() for entry in selected]
    if len(set(names)) != len(names) or any(not safe_filename(entry.filename) for entry in selected):
        parser.error("Unsafe or duplicate output filenames")
    output = private_output(args.output)
    output.mkdir(parents=True, exist_ok=False)
    with args.pac.open("rb") as source:
        for entry in selected:
            source.seek(entry.offset)
            target = output / entry.filename
            remaining = entry.size
            with target.open("xb") as destination:
                while remaining:
                    data = source.read(min(1024 * 1024, remaining))
                    if not data:
                        raise ValueError("Truncated PAC extraction")
                    destination.write(data)
                    remaining -= len(data)
            print(f"Extracted {entry.filename}: {sha256(target)}")
    print("Local extraction only; PAC CRC/authenticity was NOT independently verified")


if __name__ == "__main__":
    main()
