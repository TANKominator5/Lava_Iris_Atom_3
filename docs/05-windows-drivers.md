# 5. I separated USB enumeration from driver binding

The most time-consuming failures were Windows USB states, not a single volume-key choice.

| Windows observation | What I concluded |
| --- | --- |
| Device Descriptor Request Failed | Windows could not enumerate the phone; a driver label alone could not fix that state |
| `fastboot Gadget`, `18D1:0FFF`, Code 28 | Fastboot enumerated but lacked a driver |
| Android Bootloader Interface, Code 10 | Driver was selected but could not start |
| `1782:4D00` with no service/INF | Download connection had no usable binding |
| Installer said success for a disconnected device | Installation might only have been deferred |

## What I tried and what I corrected

I initially manually selected Google's Android Bootloader Interface. That worked for Fastboot on my unit. I also forced it onto download-mode `1782:4D00`, but its INF did not list that ID. Device Manager could say success while SetupAPI said it had marked a **non-present** device for reinstallation. The binding did not persist reliably. I do not recommend repeating that workaround as the final download driver solution.

I then used official **Zadig 2.9**, verified its Authenticode signature, and generated an exact-ID **WinUSB** package for `1782:4D00`. That package appeared in the Windows driver store. This avoided editing Google's signed INF or disabling signature enforcement.

In Zadig I selected only the phone's download connection or a preset with VID `1782`, PID `4D00`, and **MI blank**. Changing an unrelated keyboard, mouse, hub or storage driver can break the host. The preset in `tools/lava-download.cfg` encodes only those public IDs, not a personal USB instance path.

## Code 10 on Fastboot

Reconnecting and changing ports sometimes helped. On one attempt, restarting the exact phone device entry with elevated `pnputil /restart-device` cleared Code 10. I never restarted every USB device or deleted arbitrary driver packages.

For another machine, first inspect Device Manager and confirm its exact instance ID. I have not published a hard-coded instance-ID restart script; that path is machine-specific and includes private identifiers.

[Next: boot modes](06-download-modes.md)
