# 12. I rejected the v23 and mixed-version paths after reboot tests

The working v23 manager did not solve the whole problem. After reboot, the v25.2 manager reappeared. At one point Android still had an inactive v25.2 APK directory alongside the installed package; later, the v25.2 core also restored its corresponding manager. I could not assume that downgrading only the UI would remain stable.

I tried a matching v23 boot/core image, still based on my original firmware. Android booted, but the subsequent daemon/root test failed: the session showed a connection reset followed by **`No daemon is currently running!`**. I restored the previously working v25.2 boot before moving on.

I did not identify a definitive low-level cause for the v23 daemon failure. It may be tempting to attribute it to the kernel, saved environment or installation state; I do not present any of those as proven.

## My useful conclusions

- An app that opens is not proof that the root daemon will survive reboot.
- A one-time Shell grant is not proof of persistent authorization.
- An older manager with a newer core is not a reliable long-term solution.
- Manager/package state can change during boot; I rechecked package version and path instead of relying on what I had installed earlier.
- Exact original and patched hashes made returning to a known working boot possible.

An experimental local installer included tightly hash-checked inactive-APK cleanup. I have kept it private as historical evidence rather than publishing deletion of `/data/app` directories as a generic fix. I did not modify unrelated applications or erase their data for this result.

[Next: matching v24.3](13-magisk24-solution.md)
