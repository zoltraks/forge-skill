#!/usr/bin/env python3
"""Convert a local source file to text for the gathering pass.

Preflights the file, locates an installed or previously approved MarkItDown,
and writes converted text into a caller-chosen scratch directory. Markdown and
plain-text sources pass through without conversion. This script never installs,
clones, or fetches anything - an absent converter is reported, not fixed.

Usage:
    python3 scripts/convert-source.py <source-file> --out <scratch-dir>
    python3 scripts/convert-source.py --check

Exit statuses:
    0  conversion succeeded, or --check found a usable path
    1  preflight or invocation failure
    2  converter unavailable (blocked, needs approval)
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

DIRECT_FORMATS = {".md", ".markdown", ".txt", ".text"}
CONVERTIBLE_FORMATS = {".pdf", ".epub", ".docx", ".pptx", ".html", ".htm", ".xlsx"}
INVISIBLE_PATTERN = re.compile(r"[​-‏‪-‮\U000E0000-\U000E007F]")
SIZE_LIMIT_BYTES = 200 * 1024 * 1024


def note(message: str) -> None:
    print(f"NOTE {message}")


def fail(message: str, status: int = 1) -> int:
    print(f"FAIL {message}")
    return status


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preflight(source: Path) -> tuple[Path | None, str | None]:
    resolved = source.resolve()
    if not resolved.is_file():
        return None, f"source file does not exist: {source}"
    if resolved.stat().st_size == 0:
        return None, f"source file is empty: {source}"
    if resolved.stat().st_size > SIZE_LIMIT_BYTES:
        return None, f"source exceeds {SIZE_LIMIT_BYTES} bytes: {source}"
    suffix = resolved.suffix.lower()
    if suffix in DIRECT_FORMATS:
        return resolved, "direct"
    if suffix in CONVERTIBLE_FORMATS:
        return resolved, "convert"
    return None, f"unsupported source format: {suffix or '(none)'}"


def find_converter() -> tuple[str, list[str]] | None:
    cli = shutil.which("markitdown")
    if cli:
        return "cli", [cli]
    probe = subprocess.run(
        [sys.executable, "-c", "import markitdown"],
        capture_output=True,
        timeout=15,
    )
    if probe.returncode == 0:
        return "module", [sys.executable, "-m", "markitdown"]
    return None


def scan_hygiene(text: str) -> list[str]:
    findings: list[str] = []
    invisible = INVISIBLE_PATTERN.findall(text)
    if invisible:
        findings.append(f"{len(invisible)} invisible/tag-range character(s) found")
    if not text.strip():
        findings.append("converter output is empty - likely a scanned or image-only source")
    if len(text.strip()) < 100:
        findings.append("converter output is suspiciously short - inspect for extraction loss")
    return findings


def convert(command: list[str], source: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*command, str(source)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", nargs="?", help="local source file to convert")
    parser.add_argument("--out", help="scratch directory for converted output")
    parser.add_argument("--check", action="store_true",
                        help="report converter availability and exit")
    args = parser.parse_args()

    if args.check:
        found = find_converter()
        if found:
            kind, command = found
            print(f"CONVERTER {kind} {' '.join(command)}")
            return 0
        print("CONVERTER none - markitdown not installed; install or clone "
              "requires approval")
        return 2

    if not args.source or not args.out:
        parser.error("a source file and --out are required unless --check")

    resolved, verdict = preflight(Path(args.source))
    if resolved is None:
        return fail(verdict or "preflight failed")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_of(resolved)
    note(f"sha256={digest}")

    if verdict == "direct":
        text = resolved.read_text(encoding="utf-8", errors="replace")
        destination = out_dir / f"{resolved.stem}.md"
        destination.write_text(text, encoding="utf-8")
        print(f"PASS direct-read {resolved.name} -> {destination}")
        return 0

    found = find_converter()
    if not found:
        return fail(
            "converter unavailable - markitdown is not installed and this script "
            "never installs it; approve an install or record the source blocked",
            status=2,
        )

    kind, command = found
    note(f"converter={kind}")
    try:
        result = convert(command, resolved)
    except subprocess.TimeoutExpired:
        return fail("converter timed out after 300s")
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines() or ["unknown converter error"]
        return fail(f"converter failed: {detail[0]}")

    text = result.stdout
    destination = out_dir / f"{resolved.stem}.md"
    destination.write_text(text, encoding="utf-8")
    for finding in scan_hygiene(text):
        note(f"extraction-quality: {finding}")
    print(f"PASS converted {resolved.name} -> {destination}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
