"""Read-only publication checks: exact file set, privacy, links, Git index and schedule."""
import argparse
import ast
from datetime import datetime, timedelta
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = ("docs", "tools", "tests", "evidence", "publishing")
ALLOWED_SUFFIXES = {".md", ".py", ".ps1", ".sh", ".json", ".cfg", ".txt"}
MAX_FILE_BYTES = 512 * 1024
PRIVACY_PATTERNS = {
    "device-specific serial": re.compile(r"\bIATOM[0-9A-Z]{6,}\b"),
    "personal Windows home path": re.compile(r"(?i)[A-Z]:[\\/]+Users[\\/]+(?!Public\b|Default\b|<)[^\s\\/<>]+"),
    "MAC address": re.compile(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b"),
    "personal USB instance": re.compile(r"(?i)USB[\\/]+VID_[0-9a-f]{4}&PID_[0-9a-f]{4}[\\/]+[0-9A-Z&]+"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def public_files():
    value = json.loads((ROOT / "publishing" / "public-files.json").read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value or len(set(value)) != len(value):
        raise ValueError("Public inventory must be a nonempty unique list")
    for name in value:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or path.as_posix() != name:
            raise ValueError(f"Unsafe manifest path: {name}")
        if name not in ("README.md", ".gitignore", ".gitattributes") and path.parts[0] not in PUBLIC_DIRS:
            raise ValueError(f"Path is outside public source roots: {name}")
    return value


def validate_plan(plan, files):
    commits = plan.get("commits", [])
    if len(commits) != 15 or plan.get("timezone") != "+05:30" or not plan.get("commit_body", "").strip():
        raise ValueError("Expected 15 commits in IST with a commit body")
    dates = [datetime.fromisoformat(item["date"]) for item in commits]
    if any(date.utcoffset() != timedelta(hours=5, minutes=30) for date in dates):
        raise ValueError("Every commit must explicitly use +05:30")
    if any(second - first < timedelta(minutes=30) for first, second in zip(dates, dates[1:])):
        raise ValueError("Commit gap is shorter than 30 minutes or order is invalid")
    first_start = datetime.fromisoformat("2026-10-15T19:00:00+05:30")
    first_end = datetime.fromisoformat("2026-10-16T02:00:00+05:30")
    second_start = datetime.fromisoformat("2026-10-16T11:00:00+05:30")
    second_end = datetime.fromisoformat("2026-10-16T17:00:00+05:30")
    if not all(first_start <= date <= first_end for date in dates[:9]) or not all(second_start <= date <= second_end for date in dates[9:]):
        raise ValueError("Commit counts/windows do not match the requested 9+6 schedule")
    planned = [path for item in commits for path in item["paths"]]
    if len(set(planned)) != len(planned) or set(planned) != set(files):
        raise ValueError("Commit plan must assign each public file exactly once")
    if any(not item["paths"] or not re.match(r"^(?:docs|feat|test): \S", item["subject"]) for item in commits):
        raise ValueError("Each commit requires files and a conventional docs/feat/test subject")
    return commits


def scan_text(name, text):
    errors = []
    for label, pattern in PRIVACY_PATTERNS.items():
        if pattern.search(text):
            errors.append(f"{name}: possible {label}")
    for email in EMAIL.findall(text):
        if not email.endswith("@users.noreply.github.com"):
            errors.append(f"{name}: non-noreply email needs manual removal/review")
    return errors


def validate(check_git=True):
    files = public_files()
    allowed = set(files)
    plan = json.loads((ROOT / "publishing" / "commit-plan.json").read_text(encoding="utf-8"))
    validate_plan(plan, files)
    errors = []
    found = set()
    for directory in PUBLIC_DIRS:
        for path in (ROOT / directory).rglob("*"):
            if "__pycache__" in path.parts:
                continue
            if path.is_symlink():
                errors.append(f"Symlink not allowed: {path.relative_to(ROOT)}")
            elif path.is_file():
                found.add(path.relative_to(ROOT).as_posix())
    expected_nested = {name for name in files if "/" in name}
    if found != expected_nested:
        errors.append(f"Public directories differ from allowlist; extra={sorted(found - expected_nested)}, missing={sorted(expected_nested - found)}")
    for name in files:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"Missing file or unsafe link: {name}")
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"Oversized publication file: {name}")
            continue
        if path.suffix not in ALLOWED_SUFFIXES and name not in (".gitignore", ".gitattributes"):
            errors.append(f"Non-source extension: {name}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"Non-UTF8/binary content: {name}")
            continue
        if "\0" in text:
            errors.append(f"NUL/binary content: {name}")
        errors.extend(scan_text(name, text))
        if path.suffix == ".py":
            ast.parse(text, filename=name)
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".md":
            for link in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", text):
                if re.match(r"[a-zA-Z]+:", link) or link.startswith("#"):
                    continue
                destination = (path.parent / unquote(link.split("#", 1)[0])).resolve()
                if not destination.is_relative_to(ROOT) or destination.relative_to(ROOT).as_posix() not in allowed:
                    errors.append(f"Unpublished or broken Markdown link in {name}: {link}")
    if check_git:
        top = Path(git("rev-parse", "--show-toplevel").strip()).resolve()
        if top != ROOT.resolve():
            errors.append("Nested/wrong Git repository root")
        indexed = set(git("ls-files", "--cached").splitlines())
        if not indexed <= allowed:
            errors.append(f"Private/unplanned files are already in the Git index: {sorted(indexed - allowed)}")
        # NUL-delimited binary input avoids Windows text-mode CRLF rewriting path names.
        ignored = subprocess.run(["git", "check-ignore", "--stdin", "-z"], cwd=ROOT,
                                 input=("\0".join(files) + "\0").encode("utf-8"), capture_output=True)
        if ignored.returncode not in (0, 1):
            errors.append("git check-ignore failed")
        elif ignored.stdout:
            errors.append("A public file is ignored: " + repr(ignored.stdout.decode("utf-8")))
    if errors:
        raise ValueError("\n".join(errors))
    return {"public_files": len(files), "bytes": sum((ROOT / name).stat().st_size for name in files),
            "planned_commits": 15, "private_source_roots_excluded": ["Root/", "Performance_Tuning/", "_local/"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-git", action="store_true", help="For an exported source tree without .git")
    args = parser.parse_args()
    print(json.dumps(validate(check_git=not args.no_git), indent=2))
    print("Publication validation passed. Manual content review remains necessary.")


if __name__ == "__main__":
    main()
