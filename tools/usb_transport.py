"""Explicit, bounded legacy USB access; imported PyUSB only when used."""
import time

from legacy_protocol import FrameBuffer, READBACK_COMMANDS, encode_frame

VID, PID, INCOMING, OUTGOING = 0x1782, 0x4d00, 0x85, 0x06


class LegacyUSB:
    def __init__(self, library=None):
        import usb.core
        import usb.util
        import usb.backend.libusb1
        self.core, self.util = usb.core, usb.util
        self.backend = usb.backend.libusb1.get_backend(find_library=(lambda _: str(library.resolve())) if library else None)
        if self.backend is None:
            raise RuntimeError("No libusb backend; install it separately or pass --libusb")
        self.device = None
        self.crc = True
        self.buffer = FrameBuffer()

    def close(self):
        if self.device is not None:
            self.util.dispose_resources(self.device)
            self.device = None

    def candidate(self):
        devices = list(self.core.find(find_all=True, idVendor=VID, idProduct=PID, backend=self.backend))
        if len(devices) > 1:
            raise RuntimeError("Multiple download-mode phones found; connect only the intended unit")
        return devices[0] if devices else None

    def wait_fresh(self, seconds):
        deadline = time.monotonic() + seconds
        print("Waiting for the existing download connection to disconnect, then for a fresh boot ROM", flush=True)
        while self.candidate() is not None:
            if time.monotonic() >= deadline:
                raise TimeoutError("Disconnect the old loader session before making a cold connection")
            time.sleep(0.05)
        self.acquire(deadline, bootrom=True)

    def acquire(self, deadline, *, bootrom=False):
        last_error = None
        while time.monotonic() < deadline:
            candidate = self.candidate()
            if candidate is not None:
                try:
                    configuration = candidate.get_active_configuration()
                    interface = configuration[(0, 0)]
                    endpoints = {(endpoint.bEndpointAddress, endpoint.bmAttributes & 3) for endpoint in interface}
                    if (INCOMING, 2) not in endpoints or (OUTGOING, 2) not in endpoints:
                        raise RuntimeError("Unexpected interface endpoints; refusing to guess")
                    if bootrom and candidate.bcdDevice != 0x0202:
                        raise RuntimeError("Not the observed revision-0202 boot ROM; refusing a different stage")
                    self.util.claim_interface(candidate, 0)
                    candidate.ctrl_transfer(0x21, 34, 0x601, 0, None, timeout=500)
                    self.device = candidate
                    self.buffer = FrameBuffer()
                    print(f"Opened download interface, revision {candidate.bcdDevice:04x}", flush=True)
                    return
                except (self.core.USBError, NotImplementedError) as error:
                    last_error = str(error)
                    self.util.dispose_resources(candidate)
                except Exception:
                    self.util.dispose_resources(candidate)
                    raise
            time.sleep(0.05)
        raise TimeoutError(f"No usable download connection; last driver error: {last_error}")

    def refresh(self):
        self.close()
        time.sleep(0.2)
        self.acquire(time.monotonic() + 15)

    def receive(self, seconds=5):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            frame = self.buffer.pop(crc=self.crc)
            if frame is not None:
                if frame[0] == 0xff:
                    # Loader logs are not accepted as an operation acknowledgement.
                    continue
                return frame
            try:
                self.buffer.feed(bytes(self.device.read(INCOMING, 65536, timeout=max(1, int((deadline - time.monotonic()) * 1000)))))
            except self.core.USBTimeoutError:
                continue
        raise TimeoutError("No complete protocol reply before deadline")

    def ping(self):
        self.device.write(OUTGOING, b"\x7e" if self.crc else b"\x7e" * 4, timeout=1000)
        command, payload = self.receive()
        if command != 0x81:
            raise RuntimeError(f"Expected version response, received {command:04x}")
        return payload

    def request(self, command, payload=b"", *, expected=(0x80,), seconds=5):
        if command not in READBACK_COMMANDS:
            raise ValueError("Command forbidden by the boot-only readback tool")
        frame = encode_frame(command, payload, crc=self.crc)
        written = self.device.write(OUTGOING, frame, timeout=int(seconds * 1000))
        if written != len(frame):
            raise RuntimeError("Short USB write")
        response, data = self.receive(seconds)
        if response not in expected:
            raise RuntimeError(f"Command {command:04x} rejected with response {response:04x}")
        return data
