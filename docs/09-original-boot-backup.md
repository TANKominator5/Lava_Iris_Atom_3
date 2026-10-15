# 9. I read my own boot partition twice

Android sysfs identified `mmcblk0p16` as `PARTNAME=boot`, and `/proc/partitions` reported 12,288 KiB. The firmware XML also described boot as 12 MiB. I used that agreement rather than guessing a block-device number from a tutorial.

I read **12,582,912 bytes** twice through FDL2, as separate partition-read transactions. Both complete files matched byte-for-byte and had SHA-256:

```text
ca752228581539929241493325508c0a4beb453b75b14dc3842f7c7b3cb740db
```

I then inspected the backup. Its kernel date was **March 3**, exactly matching the running phone, not March 26. The ramdisk was 635,730 bytes; the later package's ramdisk was 635,725 bytes. Even that small difference reinforced why a nearly matching filename was not a sufficient backup.

## Read framing

I selected `boot` with a 36-character UTF-16LE name field followed by the 32-bit little-endian read size. Each read-midst request carried 32-bit little-endian length and offset; the loader returned type `0x93`. I used 4,096-byte blocks and required each reply length/checksum to match. I ended the read before beginning the second independent transaction.

My public tool writes exclusive `.partial` files, renames only complete reads, and refuses to overwrite either existing backup. `tools/compare_backups.py` checks both expected size and full-file equality before reporting success.

I retain those images privately. They are examples of **my** device image hashes, not a reason for someone else to skip their own backup. My shared-storage copy was not a complete backup of private app data, messages, account settings or calibration partitions.

[Next: image patching](10-image-patching.md)
