# Publication preparation and explicit execution

I prepared an exact public-file allowlist and a 15-entry narrative history. **Preparing or previewing this package does not stage, commit or push anything.** `Root/`, `Performance_Tuning/` and `_local/` are private/local and excluded.

## Review first

```powershell
python -m unittest discover -s tests -v
python publishing/validate_publication.py
powershell -NoProfile -File publishing/Publish-RootingHistory.ps1
git diff --cached --name-only
git status --short --branch
```

The preview only reads the current repository and public files. It does not contact GitHub. The validator reports public file count/size, checks links and privacy patterns, and rejects any indexed file outside the allowlist. It cannot detect every possible secret; I still manually review the content.

## Commit dates

The exact schedule is in `commit-plan.json`. I interpreted the requested times as **IST (`+05:30`)**: nine entries from October 15 19:04 into the early hours of October 16, followed by six on October 16 from 11:07 to 16:49. All gaps are at least thirty minutes. Both author and committer dates are set only during explicit creation, and the script refuses future-dated execution.

## Create local commits later — requires separate authorization

Only after I explicitly decide to create the history:

```powershell
powershell -NoProfile -File publishing/Publish-RootingHistory.ps1 -CreateCommits -ConfirmPublish
```

The script requires an unborn repository, an empty index, an empty remote, the exact configured origin and a clean tracked working tree. It runs the offline tests, uses only allowlisted paths, and creates `main` without changing global Git identity. It defaults to the public GitHub username and a GitHub noreply email instead of exposing a personal configured email. I should confirm the exact noreply address in GitHub settings if verified contribution attribution matters; it can be overridden with `-AuthorEmail`.

The schedule is additive: each file belongs to exactly one commit. Earlier commits are narrative checkpoints, not complete releases; some README links become available later. The final tree is the reviewable release.

If anything fails partway, the tool stops **without reset, deletion, amend, rebase or automatic retry**. It will not silently continue a partial history; inspect it manually and decide what to do. Existing index changes are never discarded.

## Push later — separate explicit opt-in

After reviewing all local commits:

```powershell
powershell -NoProfile -File publishing/Publish-RootingHistory.ps1 -Push -ConfirmPublish
```

Or, if both operations are explicitly authorized at the same time, supply both `-CreateCommits` and `-Push`. The script verifies all 15 subjects, dates, path groups, commit bodies and the final blob contents before a push. It sets the upstream to `origin/main` using an ordinary non-forced push.

The intended origin is:

```text
https://github.com/TANKominator5/Lava_Iris_Atom_3.git
```

Git/Git Credential Manager must already have suitable authentication; the script never asks for a token in a file or writes credentials. The tool refuses a nonempty remote rather than overwriting even an initial README. It never creates a second clone or nested repository, and it never force-pushes. A race that creates conflicting remote history should make Git reject the normal push.

## Updating the package

If I add/remove public files, I update both `public-files.json` and the commit path groups. Every file must appear exactly once. Public payloads must be small UTF-8 source/docs, not firmware or raw captures. Generated review reports belong in ignored `_local/`.

Licensing is intentionally undecided in this preparation; see `docs/attribution.md`. I should choose a suitable license before inviting redistribution as an open-source project.
