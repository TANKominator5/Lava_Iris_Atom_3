# 15. I kept a recovery route and a reproducibility checklist

I retained two independently matching original boot images on my PC and an on-device compressed original backup. I did not upload those images: another owner should obtain their own exact backup rather than flash mine.

## Before anyone repeats this

1. I would confirm ownership, exact firmware/board identity, battery condition and cable reliability.
2. I would copy personal data and acknowledge that shared storage is not a complete app/NV backup.
3. I would obtain a credible recovery source and test host access before changing anything.
4. I would verify the model-specific loader hashes/addresses, cold connection and checksum-valid stage responses.
5. I would read boot twice, compare full-size copies, inspect the original kernel/fstab and preserve off-device copies.
6. I would extract the official v24.3 APK, patch that original on the same phone, and check unchanged kernel/device tree/fstab and image size.
7. I would flash only after confirming the device serial, partition identity, backup and patched hashes.
8. I would use a matching manager/core, complete the environment if necessary, approve only trusted root requests and verify after a normal reboot.

The public tools never automatically execute a Fastboot flash. I deliberately leave that decision manual.

## Original-boot restoration outline — destructive, not executed by this document

**Writing boot changes the installed kernel/ramdisk partition.** These commands are examples with placeholders, not a recovery guarantee. The boot device/size on another phone may differ. Preserve the originals somewhere other than the device you are repairing.

```powershell
$serial = '<YOUR_ADB_SERIAL>'
$original = '<FULL_PATH_TO_YOUR_VERIFIED_ORIGINAL_BOOT.img>'
Get-FileHash -Algorithm SHA256 -LiteralPath $original
adb -s $serial reboot bootloader
# I reconnect USB if enumeration fails, then verify exactly the intended device.
fastboot devices -l
# I check the expected original hash myself BEFORE the following write.
fastboot -s $serial flash boot $original
# I reboot only if the flash reports success.
fastboot -s $serial reboot
```

Restoring original boot removes boot-based Magisk startup; it does not automatically erase `/data/adb` or uninstall the manager. I do not suggest deleting those blindly during troubleshooting. On a bootloop with working Fastboot, ADB may be unavailable and the hardware key sequence must be established separately.

## If download mode hangs

On my user-removable-battery unit I could disconnect USB, remove/reinsert the battery and boot normally. This is not advice to open a sealed battery or short test points. Loader execution may have effects I cannot reverse; a known original boot does not guarantee recovery from a damaged bootloader, calibration area or hardware.

## Reviewable local sequence

```powershell
python tools/inspect_pac.py '<LOCAL_FIRMWARE.pac>'
python tools/compare_backups.py '<FIRST_READ.img>' '<SECOND_READ.img>'
python tools/prepare_magisk.py '<OFFICIAL_v24.3.apk>' --output _local/magisk24
python tools/verify_boot.py '<ORIGINAL.img>' --patched '<PATCHED.img>' --magisk-init _local/magisk24/magiskinit
```

Downloads, extraction outputs, phone captures and images belong in ignored `_local/`, not in Git. USB readback requirements and risks are detailed in the preceding chapters. No future reader should mistake this ordered narrative for a universal automated installer.
