# 3. I found an S111 archive, then checked the date mismatch

I did not have an original PAC or `boot.img`. A third-party firmware listing offered S109, S110, and **S111_20160326**. My installed S111 build was **20160303**. Matching the S111 label alone was not enough.

The MediaFire download attempts timed out. I eventually obtained a RAR from a Google Drive mirror linked by a firmware site and extracted its PAC. I used 7-Zip after Windows' bundled tar reported `Parsing filters is unsupported` for that RAR. An extractable archive and a checksum are not proof of vendor authenticity.

## What I inspected

The PAC contained boot, recovery, system, userdata, NV-related files, two RAM download loaders, a bootloader and an XML configuration. The XML specified:

| Item | Package value |
| --- | --- |
| FDL1 base | `0x50000000` |
| FDL2 base | `0x9f000000` |
| Boot partition | 12 MiB |
| Package product | SC77xx |

The package boot kernel explicitly said **March 26**, while the phone's kernel said **March 3**. That ruled out treating the package image as my original image. I did not install this full firmware. I later used its model-specific RAM loaders for readback, with that separate risk understood.

The boot image used legacy `ANDROID!` layout, 2,048-byte pages, a raw kernel, gzip ramdisk and a 51,200-byte extra/device-tree payload. I also inspected `default.prop` and `fstab.sc8830`.

## Public tooling

`tools/inspect_pac.py` lists this legacy format, including the XML entry, and can selectively extract boot/recovery/FDL files into a new local directory. It does not flash anything, execute extracted programs, or authenticate the firmware. Its format assumptions are deliberately narrow; unsupported packages should fail rather than be guessed at.

I do not redistribute the PAC or its images. The source listing and official tool links are in [references](references.md), and the observed loader hashes are in [artifact hashes](../evidence/artifact-hashes.json).

[Next: Fastboot investigation](04-fastboot-investigation.md)
