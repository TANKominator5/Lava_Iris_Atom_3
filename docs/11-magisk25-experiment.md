# 11. I obtained initial root with v25.2, then found an app problem

I originally selected Magisk v25.2 because v26 raised the minimum Android version to 6.0. Android-version support was only a candidate compatibility check; it did not prove the app would behave correctly on this firmware.

I flashed a checked patch of **my original March 3 boot image**. Fastboot reported successful transfer and write. Android booted with the same kernel, and `/sbin/su` pointed to Magisk. `magisk -v` reported v25.2.

The app displayed a black content area. At first the display had actually slept during an authorization attempt; I checked power state and woke it. A later screenshot still showed the status bar with black app content. I did not equate every black screen with a crashed operating system.

I reviewed ActivityManager/logcat and the upstream splash initialization path. The v25.2 manager remained unusable for approval on this setup. Calling `su` before approval timed out or returned Permission denied; the existence of `/sbin/su` alone was not my final root test.

I temporarily installed the v23 manager. It opened, recognized the running v25.2 core, and eventually let me grant Shell. The result was:

```text
uid=0(root) gid=0(root) context=u:r:magisk:s0
```

That established that the patched v25.2 core could provide root. It did **not** establish a supported, reboot-stable mixed-version configuration. I continued testing instead of stopping at the first successful `id`.

[Next: v23 and mixed-version limitations](12-magisk23-experiment.md)
