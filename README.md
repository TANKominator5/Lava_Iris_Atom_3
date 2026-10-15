# How I rooted my Lava Iris Atom 3

I documented my investigation of an Android 5.1 **Lava Iris Atom 3**: the misleading `A3` identifier, failed approaches, Windows USB problems, original-boot readback, and the Magisk combination that finally survived reboot.

**My verified result:** matching **Magisk 24.3 core and app**, original `Lava_iris_Atom_3_S111_20160303` firmware/kernel, root verified after a normal reboot, no factory reset, and SELinux still Enforcing.

> This is a single-device research report, not a universal one-click root. Rooting can cause data loss, break applications, and make a phone unbootable. I do not supply firmware or ready-to-flash images. Back up your own device and establish recovery before changing partitions.

## Read my findings

1. [Scope, safety, and verified outcome](docs/01-scope-and-safety.md)
2. [Exact hardware and firmware identification](docs/02-device-identification.md)
3. [Firmware mismatch and image inspection](docs/03-firmware-research.md)
4. [Fastboot limitations and failed RAM boot](docs/04-fastboot-investigation.md)
5. [Windows drivers and USB errors](docs/05-windows-drivers.md)
6. [Boot-ROM versus other download interfaces](docs/06-download-modes.md)
7. [Legacy Spreadtrum handshake](docs/07-legacy-protocol.md)
8. [RAM loaders and USB re-enumeration](docs/08-ram-loaders.md)
9. [Two independent original-boot backups](docs/09-original-boot-backup.md)
10. [Patching my original boot image](docs/10-image-patching.md)
11. [Initial root and the v25.2 app problem](docs/11-magisk25-experiment.md)
12. [Why v23 and a mixed installation did not work](docs/12-magisk23-experiment.md)
13. [The matching v24.3 installation](docs/13-magisk24-solution.md)
14. [Post-reboot verification](docs/14-verification.md)
15. [Recovery and reproducibility checklist](docs/15-recovery-and-reproduction.md)

I separate observations from assumptions throughout. I used AI-assisted diagnostics and scripts alongside upstream tools; I credit those sources in [references](docs/references.md). I have not tested these public refactorings on another phone.

## Public tools

| Tool | Purpose | Device/host side effects |
| --- | --- | --- |
| `tools/collect_baseline.py` | Explicitly serial-targeted hardware/root diagnostics | ADB queries only; root request is optional |
| `tools/inspect_pac.py` | List a legacy PAC and selectively extract files | Local files only; no bundled firmware |
| `tools/probe_usb.py` | Check the documented boot-ROM version exchange | USB control/version requests; consumes a boot-ROM session |
| `tools/read_boot.py` | Experimental, boot-only double readback | Executes model-specific loaders in RAM; explicit acknowledgement required |
| `tools/compare_backups.py` | Compare full-size independent readbacks | Local reads only |
| `tools/prepare_magisk.py` | Extract a hash-checked official v24.3 APK | Local files only; does not install or execute binaries |
| `tools/verify_boot.py` | Check legacy boot layout and preserved patch components | Local reads only |
| `tools/finish_magisk24.sh` | Documented environment/backup completion helper | Root writes to Magisk directories; explicit apply flag; **not** a flasher |
| `tools/verify_root.py` | Check build, Magisk, SELinux and boot hash | Root requests; read-only diagnostics |

The protocol is documented for review. I deliberately did **not** publish the trial installer that deleted an inactive APK directory or the obsolete forced-Google-driver helper as recommended tools. Public scripts are guarded, parameterized adaptations, not the exact historical scripts.

## Local layout and privacy

```text
README.md
docs/          # Reviewed first-person research and recovery instructions
tools/         # Parameterized, reviewable source; no binary payloads
tests/         # Offline tests; never contact a phone
evidence/      # Sanitized excerpts and published artifact hashes
publishing/    # Exact allowlist, proposed history and opt-in upload tooling

Root/                # Ignored: original private rooting/recovery archive
Performance_Tuning/  # Ignored: separate local work, not this publication
_local/              # Ignored: future images, captures, reports and environments
```

I preserved my private archive rather than deleting original evidence or breaking its paths. I excluded personal storage, raw chat, screenshots, account details, serials, USB instance paths, installers and firmware. See [publication/privacy decisions](docs/publication-and-privacy.md).

## Check the public package offline

From the repository root, with Python **3.11 or newer**:

```powershell
python -m unittest discover -s tests -v
python publishing/validate_publication.py
powershell -NoProfile -File publishing/Publish-RootingHistory.ps1
```

The last command is a **preview**, not a commit or upload. It validates the proposed 15-commit schedule and displays the path groups. It does not stage files, create a branch, contact GitHub, commit, or push. The publication script requires separate explicit switches for those operations.

## Commit schedule

The repository history uses **IST (`+05:30`)**: nine commits from October 15, 2026 at 19:04 into the early hours of October 16, then six commits on October 16 from 11:07 through 16:49. Every gap is at least 30 minutes; the exact times are recorded in `publishing/commit-plan.json`.

No Git commits or pushes are required to read, test, or review this working tree. See [publishing instructions](publishing/README.md) before executing the opt-in script.

## Reuse

I have not selected a blanket license for this publication yet. Do not assume that the presence of this source grants a particular open-source license. Upstream projects retain their own licenses; I link to them rather than redistributing their binaries or bundled scripts. See [attribution and licensing boundaries](docs/attribution.md).
