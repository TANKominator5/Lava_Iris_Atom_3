import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from legacy_protocol import FrameBuffer, READBACK_COMMANDS, checksum, decode_frame, encode_frame


class ProtocolTests(unittest.TestCase):
    def test_captured_bootrom_version(self):
        packet = bytes.fromhex("7e00810006535052443300570a7e")
        self.assertEqual(decode_frame(packet[1:-1]), (0x81, b"SPRD3\0"))

    def test_captured_fdl_version(self):
        packet = bytes.fromhex("7e008100225370726561647472756d20426f6f7420426c6f636b2076657273696f6e20312e3100aae97e")
        self.assertEqual(decode_frame(packet[1:-1], crc=False), (0x81, b"Spreadtrum Boot Block version 1.1\0"))

    def test_additive_ack(self):
        self.assertEqual(checksum(bytes.fromhex("00800000"), crc=False), 0xff7f)

    def test_odd_outgoing_behavior(self):
        payload = b"\x01\x02\x03"
        tx = checksum(payload, crc=False, outgoing=True)
        rx = checksum(payload, crc=False)
        self.assertEqual(rx, (tx >> 8) | ((tx & 255) << 8))

    def test_escaping_and_fragmentation(self):
        packet = encode_frame(0x81, b"abc\x7e\x7d\0")
        buffer = FrameBuffer()
        for byte in packet[:-1]:
            buffer.feed(bytes([byte]))
            self.assertIsNone(buffer.pop())
        buffer.feed(packet[-1:])
        self.assertEqual(buffer.pop(), (0x81, b"abc\x7e\x7d\0"))

    def test_reject_corruption_and_bad_escape(self):
        with self.assertRaises(ValueError):
            decode_frame(bytes.fromhex("00810006535052443300570b"))
        with self.assertRaises(ValueError):
            decode_frame(b"\x7d\x00")

    def test_concatenated_frames(self):
        buffer = FrameBuffer()
        buffer.feed(b"noise" + encode_frame(0x81, b"one") + encode_frame(0x81, b"two"))
        self.assertEqual(buffer.pop(), (0x81, b"one"))
        self.assertEqual(buffer.pop(), (0x81, b"two"))

    def test_no_flash_or_erase_commands(self):
        for command in (0x0a, 0x0b, 0x1b, 0x31, 0x32, 0x33):
            self.assertNotIn(command, READBACK_COMMANDS)


if __name__ == "__main__":
    unittest.main()
