# 13. I reached the working combination with matching Magisk v24.3

I downloaded the official **v24.3** APK, prepared its ARM tools, and patched my original boot on the same phone. I installed the matching app and flashed only the checked boot image.

The final patched image was exactly 12 MiB and had SHA-256:

```text
c9bb712c2a718c546b989baf1fa1284ae679a5c7e0c29952971c44a5a2ebd7f1
```

Android completed boot. The daemon reported **`24.3:MAGISK`**, and I could obtain `uid=0(root)` after approving Shell. I temporarily enabled USB keep-awake because the display was sleeping during approval checks, then restored normal sleep afterward.

## Completing the environment

I populated `/data/adb/magisk` with the matching v24.3 BusyBox, Magisk, MagiskInit, MagiskBoot, patch/util scripts and addon script extracted from the official APK. I did not copy a newer v25.2 magiskpolicy binary into the final environment. For this version, `magiskpolicy` was a symlink to `magiskinit`.

I applied root ownership and Magisk's restorecon operation, and saved a gzip copy of my original boot in Magisk's SHA-1-named backup directory. I retained independent PC backups as well.

`tools/finish_magisk24.sh` records a guarded form of that completion step. It checks root, matching running/tool versions, a known-size original image and expected hash, and refuses to replace an existing original backup. It does not flash or delete app directories. Because the public helper adds guards to the historical sequence, it needs review before device use and has not been hardware-retested as published.

I then rebooted again and verified root, the partition hash and SELinux. This matching core/app configuration is the result I recommend evaluating for the **same firmware**, not a recommendation to install an obsolete manager on a modern phone.

[Next: reboot verification](14-verification.md)
