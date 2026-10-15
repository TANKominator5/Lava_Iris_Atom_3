"""Small local-only helpers shared by the reviewed public tools."""
import hashlib
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
PUBLIC_DIRECTORIES = {"docs", "tools", "tests", "evidence", "publishing", ".git"}


def sha256(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def private_output(path):
    """Keep generated captures/binaries outside publication source directories."""
    target = Path(path).resolve()
    if target.is_relative_to(REPOSITORY):
        relative = target.relative_to(REPOSITORY)
        if len(relative.parts) < 2 or relative.parts[0] in PUBLIC_DIRECTORIES:
            raise ValueError("Write generated material under _local/ or outside the repository")
    return target


def require_hash(value):
    normalized = value.lower()
    if len(normalized) != 64 or any(character not in "0123456789abcdef" for character in normalized):
        raise ValueError("Expected a complete SHA-256 hex digest")
    return normalized
