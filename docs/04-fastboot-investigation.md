# 4. I tested Fastboot instead of assuming modern features existed

I rebooted with `adb reboot bootloader`. The phone displayed Fastboot, but Windows initially failed USB enumeration. After fixing its driver, `fastboot devices` listed it.

## Findings and failed approaches

- `getvar all`, `secure`, `unlocked`, `product`, `partition-size:boot` and other queries returned blank values. I could not infer lock status or a zero-sized boot partition from these responses.
- `fastboot fetch boot` failed because the bootloader did not support fetch/max-fetch-size.
- `fastboot oem help` timed out; I did not use that as a reason to send speculative unlock or erase commands.
- I patched the available March 26 image on the phone and tried **RAM boot**, not a partition flash. The transfer completed, but `fastboot boot` returned **`bad boot image header`**.

That rejection did not prove Magisk could never work. Nor did it justify directly flashing the mismatched image. I returned to normal Android and looked for a way to read my actual boot partition.

Later, with my original boot image backed up and patched, `fastboot flash boot` succeeded. Fastboot printed an AVB-footer warning with partition size zero because this bootloader did not report the size. I had independently established the size as 12 MiB from Android sysfs/partition information and the readback. I did not disable verification or introduce a modern `vbmeta` procedure into an Android 5.1 device.

My historical successful flash output is excerpted in [sanitized evidence](../evidence/observed-results.md). Flash instructions remain manual and explicitly destructive in [recovery/reproduction](15-recovery-and-reproduction.md).

[Next: Windows drivers](05-windows-drivers.md)
