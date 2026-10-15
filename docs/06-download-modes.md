# 6. I learned that one USB VID/PID did not identify one protocol stage

I tried Volume Down, both volume buttons, Volume Up, and a software `autodloader` reboot. Some connections briefly showed a charging icon and then a black screen. A black screen alone was not confirmation of download readiness.

## Important observations

- I saw `1782:4D00` with revision **2427** during earlier, misleading download/serial connections.
- A cold **Volume Up** connection exposed revision **0202**, interface 0, bulk IN `0x85`, bulk OUT `0x06`.
- After FDL1 ran, I saw revision **ffff** and the loader's own version string.
- I saw `1782:5D03` as USB mass storage/charging behavior after unsuccessful timing attempts.

Those revisions are observations from my unit, not a universal detection standard. I verified the protocol using a checksum-valid version response rather than trusting a friendly name.

## Cold connection that worked here

1. I started the waiting tool first.
2. I disconnected USB and removed the **user-removable** battery for about ten seconds.
3. I reinserted it without pressing Power.
4. I held **Volume Up only** while reconnecting USB, continuing for about fifteen seconds.

I do not suggest opening sealed devices or shorting pins. The removable battery also gave me a way to exit a hung RAM-loader state.

I found `autodloader` strings in the kernel/bootloader and tried `adb reboot autodloader`. It briefly exposed a download connection but was not a reliable path in this investigation. A no-button cold connection did not give the reader a usable interface. I stopped treating repeated button combinations as a substitute for diagnosing the driver and handshake.

[Next: protocol](07-legacy-protocol.md)
