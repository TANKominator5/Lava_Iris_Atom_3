# Selected observations I retained

These are reviewed excerpts from saved command results, not a fresh run and not the full raw chat. I removed personal serials, usernames, USB instance paths, screenshots and unrelated output. I preserve errors and distinguish them from the final result.

## Failed RAM boot

```text
Sending 'boot.img' (9550 KB) OKAY
Booting FAILED (remote: 'bad boot image header')
```

## Actual host diagnostic timestamp and boot-ROM frame

The retained host log contains the following technical sequence dated **2026-10-15 00:01:21–00:01:22**.

```text
Found USB 1782:4D00, revision 0202
Interface 0, alternate 0: endpoints [(133, 2), (6, 2)]
Reply (14 bytes): 7e00810006535052443300570a7e
Validated version: SPRD3\0
Loading fdl1.bin into RAM at 50000000: 20797 bytes
RAM transfer of fdl1.bin complete; executing it
Interface probe failed: [Errno 32] Pipe error
```

## Resuming the running loader and completing the backup

```text
Reopened loader USB, revision ffff
FDL1: Spreadtrum Boot Block version 1.1\0
Loading fdl2.bin into RAM at 9f000000: 488512 bytes
RAM transfer of fdl2.bin complete; executing it
Reading boot: 0 / 12288 KiB
...
Reading boot: 11264 / 12288 KiB
First complete boot read SHA256:
ca752228581539929241493325508c0a4beb453b75b14dc3842f7c7b3cb740db
Second complete boot read SHA256:
ca752228581539929241493325508c0a4beb453b75b14dc3842f7c7b3cb740db
```

## Original-image inspection

```text
Boot header offset=0, page=2048, kernel=8859448, ramdisk=635730
Linux version 3.10.65 ... #1 SMP PREEMPT Thu Mar 3 21:38:43 CST 2016
```

## Successful final Fastboot write

```text
Warning: skip copying boot image avb footer (boot partition size: 0, boot image size: 12582912).
Sending 'boot' (12288 KB) OKAY
Writing 'boot' OKAY
Rebooting OKAY
```

The warning reflects the bootloader's missing size response; I had a separate partition-size check and full-size readback. It is not blanket permission to ignore size warnings on other devices.

## Final verification after a subsequent normal reboot

```text
Android boot completed
uid=0(root) gid=0(root) context=u:r:magisk:s0
24.3:MAGISK
c9bb712c2a718c546b989baf1fa1284ae679a5c7e0c29952971c44a5a2ebd7f1  /dev/block/mmcblk0p16
Enforcing
sprdemand
1300000
```

The raw output also contained old-linker warnings. I verified the result despite those warnings rather than representing the output as warning-free.

My phone clock reset to January 2012 after battery removal, so phone logcat wall-clock dates are not a trustworthy chronology. I did not comprehensively test phone calls or all applications as part of this result.
