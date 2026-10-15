"""Legacy Spreadtrum framing/checksums, informed by the upstream references in docs/."""
import binascii
import struct

MAX_PAYLOAD = 65535
READBACK_COMMANDS = frozenset((0, 1, 2, 3, 4, 0x10, 0x11, 0x12))


def checksum(data, *, crc=True, outgoing=False):
    if crc:
        return binascii.crc_hqx(data, 0)
    total = sum(data[index] | ((data[index + 1] if index + 1 < len(data) else 0) << 8)
                for index in range(0, len(data), 2))
    total = (total & 0xffff) + (total >> 16)
    total += total >> 16
    result = ~total & 0xffff
    # Matches the legacy reader's fixzero TX versus original RX odd-byte behavior.
    return result if outgoing and len(data) % 2 else ((result >> 8) | ((result & 255) << 8))


def encode_frame(command, payload=b"", *, crc=True):
    if not 0 <= command <= 65535 or len(payload) > MAX_PAYLOAD:
        raise ValueError("Protocol field outside 16-bit bounds")
    data = struct.pack(">HH", command, len(payload)) + payload
    data += struct.pack(">H", checksum(data, crc=crc, outgoing=True))
    return b"\x7e" + data.replace(b"\x7d", b"\x7d\x5d").replace(b"\x7e", b"\x7d\x5e") + b"\x7e"


def decode_frame(escaped, *, crc=True):
    raw = bytearray()
    escape = False
    for byte in escaped:
        if escape:
            if byte not in (0x5d, 0x5e):
                raise ValueError("Invalid escaped byte")
            raw.append(byte ^ 0x20)
            escape = False
        elif byte == 0x7d:
            escape = True
        elif byte == 0x7e:
            raise ValueError("Unexpected delimiter inside frame")
        else:
            raw.append(byte)
    if escape or len(raw) < 6:
        raise ValueError("Incomplete protocol frame")
    command, length = struct.unpack_from(">HH", raw)
    if len(raw) != length + 6 or length > MAX_PAYLOAD:
        raise ValueError("Protocol payload length mismatch")
    if checksum(raw[:-2], crc=crc) != struct.unpack_from(">H", raw, len(raw) - 2)[0]:
        raise ValueError("Protocol checksum mismatch")
    return command, bytes(raw[4:-2])


class FrameBuffer:
    def __init__(self):
        self.data = bytearray()

    def feed(self, data):
        if len(self.data) + len(data) > 4 * (MAX_PAYLOAD + 8):
            raise ValueError("Unbounded/invalid protocol input")
        self.data.extend(data)

    def pop(self, *, crc=True):
        while 0x7e in self.data:
            start = self.data.index(0x7e)
            del self.data[:start]
            try:
                end = self.data.index(0x7e, 1)
            except ValueError:
                return None
            packet = self.data[1:end]
            del self.data[:end]
            if packet:
                return decode_frame(packet, crc=crc)
        self.data.clear()
        return None
