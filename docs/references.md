# Sources I consulted

I used these upstream projects and reference pages while investigating. Third-party firmware listings are discovery sources, not vendor authentication or endorsements. Links and available downloads can change.

| Source | How I used it |
| --- | --- |
| [Magisk official repository](https://github.com/topjohnwu/Magisk) | Authoritative source and release binaries |
| [Official v24.3 release](https://github.com/topjohnwu/Magisk/releases/tag/v24.3) | Final tested version |
| [Official v25.2 release](https://github.com/topjohnwu/Magisk/releases/tag/v25.2) | Initial experiment |
| [Official v23.0 release](https://github.com/topjohnwu/Magisk/releases/tag/v23.0) | Earlier manager/core experiment |
| [Magisk changelog](https://topjohnwu.github.io/Magisk/changes.html) | Android 6 minimum introduced in v26 |
| [Magisk installation](https://topjohnwu.github.io/Magisk/install.html) | Patch-my-own-image guidance; current instructions need version/device context |
| [Spreadtrum flash/dumper](https://github.com/ilyakurdyukov/spreadtrum_flash) | Loader protocol, checksum/readback behavior and source review |
| [Dumper release used](https://github.com/ilyakurdyukov/spreadtrum_flash/releases/tag/1.20260403) | Historical Windows native-reader attempt |
| [sharkalaka](https://github.com/fxsheep/sharkalaka) | Legacy endpoints/control/ping comparison |
| [pacextractor](https://github.com/divinebird/pacextractor) | Legacy PAC structure research |
| [Zadig/libwdi](https://github.com/pbatard/libwdi/releases/tag/v1.5.1) | Zadig 2.9 exact-ID WinUSB setup |
| [Google USB driver](https://developer.android.com/studio/run/win-usb) | Fastboot driver package; not a generic match for every download-mode ID |
| [7-Zip official downloads](https://www.7-zip.org/download.html) | RAR extraction after bundled tar limitations |
| [FirmwareFile Iris Atom 3 listing](https://firmwarefile.com/lava-iris-atom-3) | Located S109/S110/S111 package names; MediaFire attempts timed out |
| [PhoneFirmware listing](https://phonefirmware.com/lava-iris-atom-3-flash-file-firmware/) | Located the Google Drive mirror used in my investigation |
| [MobileGuru4 listing](https://www.mobileguru4.com/lava-iris-atom-3-flash-file/) | Alternate package and download-mode reference |

I found generic device-named rooting pages that mixed MediaTek/SP Flash Tool advice into a Spreadtrum phone guide. I did not treat those as validated device-specific procedures. I also avoided unaudited one-click root APKs.

I do not publish expiring download tokens, account links, my serial, or local user paths. Hashes identify the particular public release/firmware artifacts I inspected; matching a recorded hash is not a substitute for evaluating source trust.
