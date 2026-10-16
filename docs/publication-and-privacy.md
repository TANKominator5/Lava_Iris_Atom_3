# How I prepared this publication

I organized reviewed rooting findings into `docs/`, public source into `tools/`, offline tests into `tests/`, selected evidence into `evidence/`, and the release tooling into `publishing/`. I did not create another nested clone or copy gigabytes of binaries into a second public project folder.

## What I kept local

I preserved the existing `Root/` archive and separate `Performance_Tuning/` work without moving or deleting their contents. They are ignored at the repository root. That avoids breaking local recovery paths or overwriting work from another task.

I excluded:

- Raw chat exports, embedded attachments, saved reasoning, tool caches and personal screenshots.
- Shared-storage and phone-workspace copies, contacts/messages/accounts and other personal data.
- Device serials, MAC addresses, personal email, Windows user paths and USB instance identifiers.
- Firmware/PAC/RAR archives, original and patched boot images, vendor loaders, APKs and installers.
- Third-party source/binaries bundled during experiments, dependencies, caches, failed downloads and generated certificates.
- Hard-coded historical installers and driver workarounds that should not become generic community instructions.

The public prose extracts technical results without copying the full conversation. Sanitized evidence retains device model, firmware version, public USB IDs, partition names and cryptographic artifact hashes because they are necessary to understand compatibility. The hash values identify artifacts, not an owner credential.

## Publication controls

`.gitignore` denies new top-level paths by default. `publishing/public-files.json` is the exact intended release inventory, and `publishing/commit-plan.json` assigns each file to one proposed commit. The validator rejects missing/unplanned files, binary payloads, disallowed tracked/indexed paths, suspicious identifiers, broken local Markdown links and an invalid schedule. This is defense in depth, not a guarantee against every possible secret; manual review remains necessary.

The upload script only stages named allowlisted paths. It never uses `git add .`, `git add -A`, a force push, an automatic merge or a reset. Its default is read-only preview. GitHub contact, history creation and pushing require explicit opt-ins.

## Commit dates

The history uses 15 commits in two windows, interpreted as **IST (`+05:30`)**. The nine evening/overnight entries run from October 15 at 19:04 to October 16 at 01:52; six daytime entries run October 16 from 11:07 to 16:49. All gaps are at least 30 minutes.

The script sets author and committer dates only when explicitly authorized to create the history. The commit subjects use conventional `docs:`/`feat:`/`test:` prefixes. No commits have been created merely by preparing these files.
