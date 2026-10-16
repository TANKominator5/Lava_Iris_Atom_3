import copy
import contextlib
import io
from pathlib import Path
import json
import subprocess
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "publishing"))
from validate_publication import public_files, scan_text, validate, validate_plan


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "publishing" / "commit-plan.json").read_text(encoding="utf-8"))

    def test_exact_schedule(self):
        commits = validate_plan(self.plan, public_files())
        self.assertEqual(len(commits), 15)

    def test_short_gap_and_duplicate_paths_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["commits"][1]["date"] = "2026-10-15T19:10:00+05:30"
        with self.assertRaises(ValueError):
            validate_plan(plan, public_files())
        plan = copy.deepcopy(self.plan)
        plan["commits"][1]["paths"].append(plan["commits"][0]["paths"][0])
        with self.assertRaises(ValueError):
            validate_plan(plan, public_files())

    def test_privacy_patterns(self):
        # Synthetic examples are assembled rather than storing identifiers in the public corpus.
        self.assertTrue(scan_text("sample", "IATOM" + "000000TEST"))
        self.assertTrue(scan_text("sample", "C:" + "\\Users\\" + "example\\file"))
        self.assertTrue(scan_text("sample", ":".join(["aa", "bb", "cc", "dd", "ee", "ff"])))
        self.assertTrue(scan_text("sample", "person" + "@" + "example.org"))
        self.assertFalse(scan_text("sample", "owner@users.noreply.github.com"))

    def test_public_corpus(self):
        self.assertEqual(validate(check_git=False)["planned_commits"], 15)

    def test_default_preview_never_calls_mutating_git_or_network(self):
        import publish_history
        def forbidden(*args, **kwargs):
            raise AssertionError(f"Preview attempted execution: {args}")
        with patch.object(publish_history, "validate", return_value={"planned_commits": 15}), \
             patch.object(publish_history, "run", side_effect=forbidden), \
             patch.object(subprocess, "run", side_effect=forbidden), \
             contextlib.redirect_stdout(io.StringIO()):
            publish_history.main([])

    def test_creation_requires_confirmation_before_git_mutation(self):
        import publish_history
        with patch.object(publish_history, "validate", return_value={}), \
             patch.object(publish_history, "run", side_effect=AssertionError("Unconfirmed Git mutation")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                publish_history.main(["--create-commits"])
            self.assertEqual(error.exception.code, 2)

    def test_create_branch_is_mocked_and_uses_exact_groups_and_dates(self):
        import publish_history
        calls = []
        pending = []

        def fake_git(*arguments, **kwargs):
            calls.append((arguments, kwargs))
            if arguments[:3] == ("remote", "get-url", "origin") or arguments[:4] == ("remote", "get-url", "--push", "origin"):
                return SimpleNamespace(stdout=publish_history.REMOTE + "\n", returncode=0)
            if arguments[:3] == ("config", "--get-all", "remote.origin.url"):
                return SimpleNamespace(stdout=publish_history.REMOTE + "\n", returncode=0)
            if arguments == ("rev-parse", "--verify", "HEAD"):
                return SimpleNamespace(stdout="", returncode=1)
            if arguments[:1] == ("add",):
                pending[:] = arguments[2:]
            if arguments == ("diff", "--cached", "--name-only"):
                return SimpleNamespace(stdout="\n".join(pending), returncode=0)
            if arguments[:1] == ("commit",):
                pending.clear()
            return SimpleNamespace(stdout="", returncode=0)

        with patch.object(publish_history, "validate", return_value={}), \
             patch.object(publish_history, "run", side_effect=fake_git), \
             patch.object(publish_history, "file_hashes", return_value={"unchanged": "snapshot"}), \
             patch.object(publish_history, "validate_published_history"), \
             patch.object(publish_history.subprocess, "run", return_value=SimpleNamespace(returncode=0)), \
             patch.object(publish_history, "datetime") as clock, \
             contextlib.redirect_stdout(io.StringIO()):
            from datetime import datetime, timezone
            clock.now.return_value = datetime(2026, 11, 1, tzinfo=timezone.utc)
            clock.fromisoformat.side_effect = datetime.fromisoformat
            publish_history.main(["--create-commits", "--confirm-publish"])
        additions = [arguments[2:] for arguments, _ in calls if arguments[:1] == ("add",)]
        self.assertEqual(additions, [tuple(item["paths"]) for item in self.plan["commits"]])
        commits = [(arguments, options) for arguments, options in calls if arguments[:1] == ("commit",)]
        self.assertEqual(len(commits), 15)
        for (_, options), item in zip(commits, self.plan["commits"]):
            self.assertEqual(options["env"]["GIT_AUTHOR_DATE"], item["date"])
            self.assertEqual(options["env"]["GIT_COMMITTER_DATE"], item["date"])
            self.assertTrue(options["env"]["GIT_AUTHOR_EMAIL"].endswith("@users.noreply.github.com"))
        self.assertFalse(any(arguments[:1] == ("push",) for arguments, _ in calls))


if __name__ == "__main__":
    unittest.main()
