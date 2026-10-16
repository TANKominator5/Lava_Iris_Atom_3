# Attribution and licensing boundaries

I carried out this investigation with AI-assisted diagnostics and script development. I distinguish the observed physical-device results from the cleaned public source prepared afterward.

I consulted Magisk, ilyakurdyukov's Spreadtrum dumper, sharkalaka, pacextractor, PyUSB, libusb, libwdi/Zadig, Google platform-tools and 7-Zip. Their authors retain credit and their projects retain their own licenses. The protocol/layout implementations here were informed by those sources and the captured device responses; see [references](references.md).

- Magisk is GPL-licensed upstream; I do not bundle its binaries, scripts or APKs. The extraction helper operates on a separately acquired official APK.
- The reviewed Spreadtrum dumper repository publishes its source under the Unlicense. I link to it and acknowledge the protocol research instead of including its complete C source or release ZIP.
- I do not include sharkalaka's source, a PyUSB/libusb distribution, Zadig executable, 7-Zip binaries or vendor firmware.
- Generated driver packages, certificates, images and application binaries stay private/local.

No blanket license has been selected for this publication. I have not silently applied an open-source license to the owner's content or claimed rights over vendor/upstream materials. Before distributing derivatives or accepting community code, I should select and document appropriate licensing explicitly.
