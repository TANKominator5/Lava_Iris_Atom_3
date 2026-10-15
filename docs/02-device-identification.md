# 2. I identified the firmware, not just the ADB model

ADB called my phone `A3`. The installed build identified it more precisely as **Lava Iris Atom 3**. I avoided searching for generic Lava A3 images because that name also appears on unrelated products.

| Field | What I observed |
| --- | --- |
| Manufacturer | Lava |
| Product/model/device | A3 |
| Build | `Lava_iris_Atom_3_S111_20160303` |
| Fingerprint | `Lava/A3/A3:5.1/LMY47D/123:user/release-keys` |
| Android/security patch | 5.1 / 2015-11-01 |
| Platform / ABI | sc8830 / armeabi-v7a |
| CPU | Four Cortex-A7 cores present, up to 1.3 GHz |
| GPU/API | Mali-400 MP / OpenGL ES 2.0 |
| Display | 480 × 854, 240 dpi; SurfaceFlinger reported about 57 Hz |
| Linux-visible RAM | 467,972 KiB, approximately 457 MiB |
| Kernel | 3.10.65, GCC 4.8, build dated March 3, 2016 |

I saw SC77xx/SC7731 naming in the later firmware package while Android reported `sc8830`. I kept those observations separate instead of assuming one label alone was a reliable compatibility check.

## Initial checks I used

```powershell
$serial = '<YOUR_ADB_SERIAL>'
adb -s $serial shell getprop ro.build.display.id
adb -s $serial shell getprop ro.build.fingerprint
adb -s $serial shell getprop ro.product.cpu.abi
adb -s $serial shell cat /proc/version
adb -s $serial shell cat /proc/partitions
```

My original ADB shell was UID 2000, `ro.debuggable=0`, and `ro.secure=1`. SELinux was Enforcing. Modern lock-status properties returned empty values. Empty is **unknown**, not evidence that the bootloader is unlocked.

Only one core was online in an idle, screen-off snapshot, although four were present. I did not mistake that power-management behavior for missing cores. I collected memory information for context, but this publication describes rooting rather than a performance modification.

[Next: firmware research](03-firmware-research.md)
