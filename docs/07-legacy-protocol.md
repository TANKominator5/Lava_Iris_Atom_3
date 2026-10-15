# 7. I validated the legacy Spreadtrum handshake

I compared the protocol implemented by upstream Spreadtrum tools and the older sharkalaka implementation. The useful transport on my boot ROM was:

```text
VID:PID       1782:4D00
Interface     0
Bulk IN       0x85
Bulk OUT      0x06
Control       bmRequestType=0x21, bRequest=34, wValue=0x601, wIndex=0
Version ping  0x7e
```

My checksum-verified response was:

```text
7e 00 81 00 06 53 50 52 44 33 00 57 0a 7e
                    S  P  R  D  3 \0
```

The packet type is `0x0081`, payload length is six, payload is `SPRD3\0`, and checksum is `0x570a` (CRC-16/XMODEM with initial value zero, matching `binascii.crc_hqx`). Frames use `0x7e` delimiters and escape `0x7d`/`0x7e` with `0x7d` and XOR `0x20`.

FDL1 uses a different additive checksum. Its version payload was **`Spreadtrum Boot Block version 1.1\0`**; I independently checked the captured checksum `0xaae9`. I did not classify a valid FDL1 frame as a bad boot-ROM packet once I understood the stage transition.

`tools/legacy_protocol.py` isolates the checksums and framing, with offline tests. `tools/probe_usb.py` performs only version/control requests; it does not load code or write partitions. A version probe can consume the first response or alter session state, so I used a fresh cold connection before a complete readback attempt.

The public tools explicitly accept a libusb library path instead of bundling a DLL. PyUSB is an optional dependency required only for USB tools.

[Next: loaders and re-enumeration](08-ram-loaders.md)
