# 10. I patched the original image on the same phone

With the original boot safely copied to my PC, I restarted Android and transferred that original image back into a task-owned temporary directory. I extracted the ARM patching tools from official Magisk APKs and ran the upstream `boot_patch.sh` **on this phone**, not a boot image downloaded from another rooted unit.

I preserved these flags:

```text
BOOTMODE=true
KEEPVERITY=true
KEEPFORCEENCRYPT=true
ASH_STANDALONE=1
```

The original fstab used `encryptable=footer`; preserving force-encryption flags did not encrypt or decrypt userdata. These flags were preservation choices, not an instruction to retrofit modern AVB/vbmeta onto this legacy phone.

## On-device patching outline

I first extracted an official APK locally with `tools/prepare_magisk.py`, copied its output and my original boot image into a new phone workspace, set BusyBox executable, and used:

```text
BOOTMODE=true KEEPVERITY=true KEEPFORCEENCRYPT=true ASH_STANDALONE=1 \
  <WORKSPACE>/busybox sh <WORKSPACE>/boot_patch.sh <WORKSPACE>/original_boot.img
```

These placeholders must be replaced intentionally. I never substitute an unverified block-device path as patch input. The public extraction helper targets official **v24.3** only and verifies its recorded APK hash before writing files. I do not bundle upstream Magisk scripts or execute them during extraction.

## What I checked before flashing

- Legacy boot header and 2,048-byte alignment were parseable.
- The image fit the known 12 MiB partition.
- Original kernel and extra/device-tree bytes were unchanged.
- `fstab.sc8830` was unchanged.
- `.backup/init` matched the original `init`.
- New `init` matched the extracted Magisk init, not the stock init.
- `overlay.d/sbin/magisk32.xz` was present.
- The backup configuration retained both preservation flags and `RECOVERYMODE=false`.

`tools/verify_boot.py` makes those checks explicit, without using Python assertions for safety checks. I also keep the pre-flash verification separate from the physical flash: the helper never writes a device.

[Next: the v25.2 experiment](11-magisk25-experiment.md)
