"""Preview by default; opt-in creation/push of a checked local history."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from validate_publication import ROOT, public_files, validate, validate_plan

REMOTE = "https://github.com/TANKominator5/Lava_Iris_Atom_3.git"


def run(*arguments, env=None, check=True):
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="strict", env=env, check=check)


def file_hashes(files):
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}


def validate_published_history(commits, branch):
    body_text = json.loads((ROOT / "publishing" / "commit-plan.json").read_text(encoding="utf-8"))["commit_body"]
    if run("symbolic-ref", "--short", "HEAD").stdout.strip() != branch:
        raise RuntimeError("Current branch is not the explicitly selected publication branch")
    hashes = run("rev-list", "--reverse", "HEAD").stdout.splitlines()
    if len(hashes) != len(commits):
        raise RuntimeError("History is not exactly the 15 planned commits; inspect manually")
    for oid, planned in zip(hashes, commits):
        subject, author_date, committer_date = run("show", "-s", "--format=%s%n%aI%n%cI", oid).stdout.splitlines()
        if subject != planned["subject"] or author_date != planned["date"] or committer_date != planned["date"]:
            raise RuntimeError("Commit subject/date differs from the planned schedule")
        if run("show", "-s", "--format=%b", oid).stdout.strip() != body_text:
            raise RuntimeError("Commit body differs from the plan")
        changed = run("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", oid).stdout.splitlines()
        if set(changed) != set(planned["paths"]):
            raise RuntimeError("Commit changed files outside its assigned group")
    files = public_files()
    if set(run("ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines()) != set(files):
        raise RuntimeError("Final tree differs from exact allowlist")
    for name in files:
        # --path uses the same Git attributes/line-ending normalization as git add.
        local = run("hash-object", "--path=" + name, "--", name).stdout.strip()
        if local != run("rev-parse", "HEAD:" + name).stdout.strip():
            raise RuntimeError(f"Working file differs from committed blob: {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create-commits", action="store_true", help="Write the 15 planned commits; no push unless separately requested")
    parser.add_argument("--push", action="store_true", help="Contact GitHub and push only the exact verified history")
    parser.add_argument("--confirm-publish", action="store_true")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--author-name", default="TANKominator5")
    parser.add_argument("--author-email", default="TANKominator5@users.noreply.github.com")
    args = parser.parse_args(argv)
    files = public_files()
    plan = json.loads((ROOT / "publishing" / "commit-plan.json").read_text(encoding="utf-8"))
    commits = validate_plan(plan, files)
    summary = validate()
    print(json.dumps(summary, indent=2))
    for index, item in enumerate(commits, 1):
        print(f"{index:02}  {item['date']}  {item['subject']} ({len(item['paths'])} files)")
    if not args.create_commits and not args.push:
        print("PREVIEW ONLY: no staging, branch changes, commits, remote contact or pushes performed.")
        return
    if not args.confirm_publish:
        parser.error("Execution requires --confirm-publish")
    if plan["remote"] != REMOTE or run("remote", "get-url", "origin").stdout.strip() != REMOTE:
        raise RuntimeError("Origin differs from the approved GitHub repository")
    push_url = run("remote", "get-url", "--push", "origin").stdout.strip()
    if push_url != REMOTE:
        raise RuntimeError("Push URL differs from the approved GitHub repository")
    if run("config", "--get-all", "remote.origin.url").stdout.splitlines() != [REMOTE]:
        raise RuntimeError("Multiple origin URLs require manual review")
    if run("check-ref-format", "--branch", args.branch, check=False).returncode:
        raise RuntimeError("Invalid branch name")
    if datetime.now(timezone.utc) < datetime.fromisoformat(commits[-1]["date"]).astimezone(timezone.utc):
        raise RuntimeError("Requested publication dates are still in the future; wait or explicitly revise the plan")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    if run("diff", "--cached", "--name-only").stdout.strip():
        raise RuntimeError("Index contains staged work; refusing to include or alter it")
    if run("diff", "--name-only").stdout.strip():
        raise RuntimeError("Tracked changes require manual review before history creation or push")
    if args.create_commits:
        if run("rev-parse", "--verify", "HEAD", check=False).returncode == 0:
            raise RuntimeError("Repository already has commits; no automatic rewrite or duplicate history")
        if run("ls-files", "--cached").stdout.strip():
            raise RuntimeError("Expected an empty index on the unborn repository")
        # Read-only remote inspection happens only after explicit execution authorization.
        if run("ls-remote", "origin").stdout.strip():
            raise RuntimeError("Remote has existing refs; stop and reconcile history manually, without force push")
        if not args.author_name.strip() or not args.author_email.endswith("@users.noreply.github.com"):
            raise RuntimeError("Use a nonempty author name and a GitHub noreply address")
        snapshot = file_hashes(files)
        run("symbolic-ref", "HEAD", "refs/heads/" + args.branch)
        for item in commits:
            if file_hashes(files) != snapshot:
                raise RuntimeError("Public content changed during commit creation; stopped without resetting anything")
            run("add", "--", *item["paths"])
            staged = run("diff", "--cached", "--name-only").stdout.splitlines()
            if set(staged) != set(item["paths"]):
                raise RuntimeError("Staged paths differ from planned group; stop for manual review")
            env = os.environ.copy()
            env.update({"GIT_AUTHOR_DATE": item["date"], "GIT_COMMITTER_DATE": item["date"],
                        "GIT_AUTHOR_NAME": args.author_name, "GIT_COMMITTER_NAME": args.author_name,
                        "GIT_AUTHOR_EMAIL": args.author_email, "GIT_COMMITTER_EMAIL": args.author_email})
            body = plan["commit_body"]
            print(run("commit", "-m", item["subject"], "-m", body, env=env).stdout, end="")
        validate_published_history(commits, args.branch)
        print("Created and verified the local history. No force push or reset was used.")
    if args.push:
        validate_published_history(commits, args.branch)
        if run("status", "--porcelain", "--untracked-files=no").stdout.strip():
            raise RuntimeError("Tracked/indexed changes remain; refusing push")
        # Empty remote only: do not overwrite an existing history, even if a push could fast-forward.
        if run("ls-remote", "origin").stdout.strip():
            raise RuntimeError("Remote is no longer empty; review manually before publishing")
        print(run("push", "--set-upstream", "origin", f"HEAD:refs/heads/{args.branch}").stdout)
    elif args.create_commits:
        print("Push was NOT requested. Review the 15 local commits before running again with --push.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"STOPPED: {error}", file=sys.stderr)
        raise SystemExit(1)
