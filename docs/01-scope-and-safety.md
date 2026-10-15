# 1. I defined the scope before changing the phone

I wanted root on a Lava Iris Atom 3 without needlessly replacing the operating system or erasing personal data. I started with authorized ADB access and an unprivileged shell. My end result was root on the existing Android 5.1 installation, not a custom ROM or an overclocked kernel.

## What I verified

- I kept `Lava_iris_Atom_3_S111_20160303` and its March 3 kernel.
- I independently read the 12 MiB boot partition twice before flashing.
- I verified the final partition against my checked Magisk 24.3 image.
- I obtained `uid=0(root)` again after a subsequent normal reboot.
- I left SELinux Enforcing and did not issue a bootloader unlock or factory-reset command.

## What I do not claim

I did not demonstrate universal support for every Iris Atom 3 revision. I did not comprehensively test calls, messaging, banking applications, long-term security, or every peripheral. I did not establish a guaranteed unbrick procedure or prove that the bootloader was officially unlocked. Successful `flash boot` only demonstrates that this unit accepted that write.

## My safety boundaries

I used device-owned backups, checked firmware identities, and kept the original boot image. I did not disable thermal protection, repartition storage, write NV/calibration partitions, or publish a ready-made image for strangers to flash. Loading an FDL into RAM is still risky: a model-incompatible loader initializes hardware and can hang or damage a phone even if my protocol never issues a flash-write command.

Android 5.1 and this firmware's 2015 security patch are obsolete. Root expands the impact of malicious applications. I treat a working root shell as a compatibility result, not a security improvement.

[Next: device identification](02-device-identification.md)
