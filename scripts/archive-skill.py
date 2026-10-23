#!/usr/bin/env python3
"""Snapshot, list, and restore skill-directory archives - staged-write.

Never deletes anything. Snapshot copies the target (or a --files subset) into
<archive-dir>/<name>-<utc-timestamp>/ with a MANIFEST.json recording the
source. Restore copies a snapshot back to its recorded source, preserving any
conflicting existing file as <name>.conflict-<timestamp> instead of
overwriting it.

Every mutating action is a dry run until --apply is passed.

Usage:
  python3 scripts/archive-skill.py snapshot <path> --archive-dir <dir> [--files f ...] [--apply]
  python3 scripts/archive-skill.py list --archive-dir <dir>
  python3 scripts/archive-skill.py restore <snapshot-id> --archive-dir <dir> [--into <dir>] [--apply]

Exit statuses: 0 = action completed or dry-run reported, 1 = failure,
2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = "MANIFEST.json"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def unique_snapshot_dir(archive_dir: Path, name: str, stamp: str) -> Path:
    candidate = archive_dir / f"{name}-{stamp}"
    suffix = 2
    while candidate.exists():
        candidate = archive_dir / f"{name}-{stamp}-{suffix}"
        suffix += 1
    return candidate


def planned_files(source: Path, only: list[str] | None) -> list[Path]:
    if only is not None:
        files = [source / rel for rel in only]
        missing = [str(p) for p in files if not p.is_file()]
        if missing:
            raise FileNotFoundError(f"requested files missing: {', '.join(missing)}")
        return files
    return sorted(p for p in source.rglob("*") if p.is_file()
                  and ".git" not in p.relative_to(source).parts)


def cmd_snapshot(args: argparse.Namespace) -> int:
    source = Path(args.path).resolve()
    archive_dir = Path(args.archive_dir).expanduser().resolve()
    if not source.is_dir():
        print(f"FAIL source directory does not exist: {source}")
        return 1
    try:
        files = planned_files(source, args.files)
    except FileNotFoundError as error:
        print(f"FAIL {error}")
        return 1

    stamp = utc_stamp()
    target = unique_snapshot_dir(archive_dir, source.name, stamp)
    if not args.apply:
        print(f"DRY-RUN snapshot {source} -> {target}")
        for path in files:
            print(f"  copy={path.relative_to(source)}")
        print(f"STATUS DRY-RUN files={len(files)} - rerun with --apply to snapshot")
        return 0

    target.mkdir(parents=True)
    copied = 0
    for path in files:
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied += 1
    manifest = {
        "source": str(source),
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": [p.relative_to(source).as_posix() for p in files],
    }
    (target / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"snapshot={target.name} files={copied} restore_path={target}")
    print("STATUS SNAPSHOT")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    archive_dir = Path(args.archive_dir).expanduser().resolve()
    if not archive_dir.is_dir():
        print(f"STATUS EMPTY archive_dir={archive_dir}")
        return 0
    snapshots = sorted(p for p in archive_dir.iterdir()
                       if p.is_dir() and (p / MANIFEST).is_file())
    for snapshot in snapshots:
        manifest = json.loads((snapshot / MANIFEST).read_text(encoding="utf-8"))
        print(f"snapshot={snapshot.name} source={manifest.get('source', '?')} "
              f"created={manifest.get('created', '?')} files={len(manifest.get('files', []))}")
    print(f"STATUS LIST snapshots={len(snapshots)}")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    archive_dir = Path(args.archive_dir).expanduser().resolve()
    snapshot = archive_dir / args.snapshot_id
    manifest_path = snapshot / MANIFEST
    if not manifest_path.is_file():
        print(f"FAIL snapshot not found: {snapshot}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    destination_root = (Path(args.into).resolve() if args.into
                        else Path(manifest["source"]))
    stamp = utc_stamp()

    moves: list[tuple[Path, Path]] = []
    preserved: list[tuple[Path, Path]] = []
    for relative in manifest.get("files", []):
        source = snapshot / relative
        if not source.is_file():
            print(f"FAIL snapshot is missing recorded file: {relative}")
            return 1
        destination = destination_root / relative
        if destination.exists() and destination.read_bytes() != source.read_bytes():
            preserved.append((destination,
                              destination.with_name(f"{destination.name}.conflict-{stamp}")))
        moves.append((source, destination))

    if not args.apply:
        print(f"DRY-RUN restore {snapshot.name} -> {destination_root}")
        for _src, dest in moves:
            print(f"  restore={dest}")
        for existing, backup in preserved:
            print(f"  preserve={existing} -> {backup.name}")
        print(f"STATUS DRY-RUN files={len(moves)} conflicts={len(preserved)} "
              "- rerun with --apply to restore")
        return 0

    for existing, backup in preserved:
        existing.rename(backup)
        print(f"preserved={existing} -> {backup.name}")
    restored = 0
    for source, destination in moves:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored += 1
    print(f"STATUS RESTORED files={restored} conflicts_preserved={len(preserved)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)

    snap = sub.add_parser("snapshot", help="copy a directory into the archive")
    snap.add_argument("path", help="directory to snapshot")
    snap.add_argument("--archive-dir", required=True, help="archive root directory")
    snap.add_argument("--files", nargs="*", default=None,
                      help="snapshot only these relative paths")
    snap.add_argument("--apply", action="store_true", help="perform the copy")
    snap.set_defaults(func=cmd_snapshot)

    listing = sub.add_parser("list", help="list snapshots in the archive")
    listing.add_argument("--archive-dir", required=True)
    listing.set_defaults(func=cmd_list)

    restore = sub.add_parser("restore", help="restore a snapshot to its source")
    restore.add_argument("snapshot_id", help="snapshot directory name from list")
    restore.add_argument("--archive-dir", required=True)
    restore.add_argument("--into", default=None,
                         help="restore into this directory instead of the recorded source")
    restore.add_argument("--apply", action="store_true", help="perform the restore")
    restore.set_defaults(func=cmd_restore)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
