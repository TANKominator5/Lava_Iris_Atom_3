# 14. I verified more than a root icon

After a subsequent normal reboot, I checked boot completion, a real Shell root command, the running Magisk version, the flashed partition hash, and SELinux.

Sanitized observed output:

```text
Android boot completed
uid=0(root) gid=0(root) context=u:r:magisk:s0
24.3:MAGISK
c9bb712c2a718c546b989baf1fa1284ae679a5c7e0c29952971c44a5a2ebd7f1  /dev/block/mmcblk0p16
Enforcing
sprdemand
1300000
```

I confirmed the installed app version was 24.3 and the build was still `Lava_iris_Atom_3_S111_20160303`. I restored `stay_on_while_plugged_in` to `0`. I did not tune the governor, change thermal settings, or claim improved performance as part of rooting.

## Verification outline

```powershell
$serial = '<YOUR_ADB_SERIAL>'
adb -s $serial shell getprop sys.boot_completed
adb -s $serial shell "su -c id"
adb -s $serial shell /sbin/magisk -v
adb -s $serial shell "su -c getenforce"
```

For the hash, I first confirmed the block device's `PARTNAME=boot` and size, then used root BusyBox SHA-256. `tools/verify_root.py` performs these queries with an explicit serial and an expected image hash. It does not set permissions automatically; I grant Shell interactively through the manager.

The old linker printed warnings about `DT_FLAGS_1` and unused DT entries. I retained that caveat rather than presenting the run as warning-free. The commands still returned successful root results.

## Limits of this verification

I did not comprehensively validate every application, calls/SMS, camera, Bluetooth, notifications, deep sleep or long-duration operation. A SIM was absent/not ready in one snapshot and Wi-Fi was not connected. I do not call those historical states new faults caused by rooting. I also do not claim root hiding, banking-app compatibility, certification bypass, or a secure daily-driver platform.

[Next: recovery and reproduction](15-recovery-and-reproduction.md)
