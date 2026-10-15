# 8. I handled the USB transition instead of assuming a pipe error meant no execution

After I received `SPRD3`, I connected and sent the stock FDL1 to `0x50000000` in 528-byte chunks. The transfer completed. Executing it produced a USB pipe error in one path, but a later probe received **Spreadtrum Boot Block version 1.1**. That proved the loader had executed; the host handle was stale across a USB transition.

I reopened the enumerated USB device, claimed interface 0 and reapplied the legacy control request. I then switched to the additive checksum, requested the FDL1 version, connected again, and loaded FDL2 at `0x9f000000`.

## Model-specific loader provenance

| Loader | Size | SHA-256 |
| --- | --- | --- |
| FDL1 | 20,797 bytes | `b3c6873300387bc00564248590983c13f48e9b5dbb07b65430faee3134081504` |
| FDL2 | 488,512 bytes | `ea8f7a8c15f571b254f812f8240cbb8b90e69a00d344ad779937282e2575aa54` |

These identify the files I used from the **S111_20160326 Iris Atom 3 package**. They are not trust anchors, vendor signatures, or permission to use them on another model. I do not distribute those loaders here.

## Public readback safety model

`tools/read_boot.py` requires explicit loader paths, exact hashes, an output directory and a risk acknowledgement. It waits for a fresh boot-ROM connection and handles the FDL1 re-enumeration. It only exposes boot readback, not arbitrary commands or a generic partition writer.

Its allowed operations are connect, RAM start/midst/end/execute, and partition read start/midst/end. I deliberately did not expose repartition, erase, NV write, bootloader write or normal flash-write commands. This **does not make loader execution risk-free**: the supplied vendor loader itself executes privileged hardware-initialization code.

The original successful investigation resumed from an already-running FDL1 using a separate script after a failed combined attempt. The public reader is a cleaned, integrated adaptation of that sequence. Its mocked/offline tests are not evidence of a new physical-phone test.

[Next: original boot backup](09-original-boot-backup.md)
