#!/usr/bin/env python3
"""Check whether the skill's own git repository has incoming updates.

Runs against the skill repository itself - never against the audited or
edited subject. Prints a STATUS verdict line plus key=value detail lines
and always exits 0.

Verdicts:

- NO-REPO          the skill directory is not inside a git work tree
- GIT-MISSING      the git executable is not available
- NO-UPSTREAM      the current branch has no upstream configured
- FETCH-FAILED     the fetch could not complete (offline, auth, timeout)
- CHECK-FAILED     an unexpected git query failed after a successful fetch
- UP-TO-DATE       no incoming commits on the upstream branch
- UPDATE-AVAILABLE incoming commits exist, with behind/ahead/dirty details

Verdicts after upstream resolution also carry tip detail lines:

- tip_sha=<sha>     the full commit hash of the fetched upstream tip
- tip_date=<date>   its committer date - a tag-free review anchor for
                    deciding whether to pull

UPDATE-AVAILABLE also carries review detail lines:

- incoming_total=<n>          commit count in the HEAD..@{u} range
- incoming_<n>=<sha> <subj>   the first ten incoming commits
- incoming_truncated=yes      present only when more than ten commits arrive
- changed_files=<n>           files touched by the incoming range
- changed_scripts=yes|no      whether any scripts/ path changes
- changed_skill=yes|no        whether SKILL.md itself changes

Usage: python scripts/check-update.py [skill-directory]
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

FETCH_TIMEOUT = 20
GIT_TIMEOUT = 15


def git(root: Path, *args: str, timeout: int = GIT_TIMEOUT) -> subprocess.CompletedProcess | None:
    env = dict(os.environ)
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return None


def verdict(status: str, **details: str) -> int:
    print(f"STATUS {status}")
    for key, value in details.items():
        print(f"{key}={value}")
    return 0


def incoming_details(root: Path, cap: int = 10) -> dict[str, str]:
    details: dict[str, str] = {}
    log = git(root, "log", "--format=%h %s", "HEAD..@{u}")
    if log is not None and log.returncode == 0:
        commits = [line.strip() for line in log.stdout.splitlines() if line.strip()]
        details["incoming_total"] = str(len(commits))
        for index, entry in enumerate(commits[:cap], start=1):
            details[f"incoming_{index}"] = entry
        if len(commits) > cap:
            details["incoming_truncated"] = "yes"
    names = git(root, "diff", "--name-only", "HEAD..@{u}")
    if names is not None and names.returncode == 0:
        files = [line.strip() for line in names.stdout.splitlines() if line.strip()]
        details["changed_files"] = str(len(files))
        details["changed_scripts"] = "yes" if any(f.startswith("scripts/") for f in files) else "no"
        details["changed_skill"] = "yes" if "SKILL.md" in files else "no"
    return details


def tip_details(root: Path) -> dict[str, str]:
    tip = git(root, "log", "-1", "--format=%H %cs", "@{u}")
    if tip is None or tip.returncode != 0:
        return {}
    parts = tip.stdout.strip().split()
    if len(parts) != 2:
        return {}
    return {"tip_sha": parts[0], "tip_date": parts[1]}


def main() -> int:
    if len(sys.argv) > 2:
        print(__doc__.strip().splitlines()[-1])
        return 0

    if len(sys.argv) == 2:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path(__file__).resolve().parent.parent

    try:
        inside = git(root, "rev-parse", "--is-inside-work-tree")
    except FileNotFoundError:
        return verdict("GIT-MISSING")
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        return verdict("NO-REPO")

    upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if upstream is None or upstream.returncode != 0:
        return verdict("NO-UPSTREAM")
    upstream_ref = upstream.stdout.strip()

    fetch = git(root, "fetch", "--quiet", timeout=FETCH_TIMEOUT)
    if fetch is None or fetch.returncode != 0:
        return verdict("FETCH-FAILED", upstream=upstream_ref)

    tip = tip_details(root)
    counts = git(root, "rev-list", "--left-right", "--count", "HEAD...@{u}")
    if counts is None or counts.returncode != 0:
        return verdict("CHECK-FAILED", upstream=upstream_ref, **tip)
    parts = counts.stdout.split()
    if len(parts) != 2:
        return verdict("CHECK-FAILED", upstream=upstream_ref, **tip)
    ahead, behind = parts

    if behind == "0":
        return verdict("UP-TO-DATE", upstream=upstream_ref, **tip)

    status = git(root, "status", "--porcelain")
    dirty = "yes" if status is not None and status.stdout.strip() else "no"
    return verdict(
        "UPDATE-AVAILABLE",
        upstream=upstream_ref,
        behind=behind,
        ahead=ahead,
        dirty=dirty,
        **tip,
        **incoming_details(root),
    )


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
