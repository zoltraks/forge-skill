#!/usr/bin/env python3
"""Report evals.json compaction candidates for one or more targets - read-only.

Accepts a skill directory (reads its evals/evals.json) or a direct path to an
evals JSON file. Both evals schema shapes are read: the astra dict form
(`{"skill_name": ..., "evals": [...]}`) and the bare list form where entries
carry `query` instead of `prompt`. Reports suite metrics and candidate findings
the optimization
procedure classifies per references/optimization-patterns.md:

  dup_prompt          - identical normalized prompt carried by two entries
  similar_prompt      - prompt pair over the merge threshold, a semantic
                        merge candidate (flag-variant and near-duplicate runs)
  dup_expectation     - the same normalized check twice inside one entry
  similar_expectation - near-verbatim check pair inside one entry
  shared_expectation  - identical check spanning entries, informational only
  id_sequence         - duplicate or out-of-order eval ids

Never writes, never executes target code, never fetches.

Usage:
  python3 scripts/compact-evals.py <skill-dir-or-evals.json> [...] [--json]

Exit statuses: 0 = inspection completed (findings may exist), 1 = no target
could be inspected, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROMPT_MERGE_THRESHOLD = 0.55
EXPECTATION_MERGE_THRESHOLD = 0.70


def normalize(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def tokens(text: str) -> set[str]:
    return set(normalize(text).split())


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def resolve_evals_file(raw: str) -> Path | None:
    path = Path(raw)
    if path.is_dir():
        path = path / "evals" / "evals.json"
    return path if path.is_file() and path.suffix == ".json" else None


def find_prompt_candidates(evals: list[dict]) -> list[dict]:
    findings = []
    keyed = [(entry.get("id"), normalize(entry_prompt(entry)))
             for entry in evals]
    seen: dict[str, list] = {}
    for eval_id, normalized in keyed:
        seen.setdefault(normalized, []).append(eval_id)
    for ids in seen.values():
        if len(ids) > 1:
            findings.append({"kind": "dup_prompt", "ids": ids,
                             "confidence": "HIGH"})
    tok = {eval_id: tokens(entry_prompt(entry))
           for (eval_id, _), entry in zip(keyed, evals)}
    for i in range(len(evals)):
        for j in range(i + 1, len(evals)):
            left, right = evals[i].get("id"), evals[j].get("id")
            score = jaccard(tok[left], tok[right])
            if PROMPT_MERGE_THRESHOLD <= score < 1.0:
                findings.append({"kind": "similar_prompt", "ids": [left, right],
                                 "jaccard": round(score, 2), "confidence": "MEDIUM"})
    return findings


def find_expectation_candidates(evals: list[dict]) -> list[dict]:
    findings = []
    owners: dict[str, list] = {}
    for entry in evals:
        eval_id = entry.get("id")
        seen: dict[str, int] = {}
        checks = [str(item) for item in entry.get("expectations", [])]
        for item in checks:
            normalized = normalize(item)
            if normalized in seen:
                findings.append({"kind": "dup_expectation", "id": eval_id,
                                 "check": normalized[:80], "confidence": "HIGH"})
            seen[normalized] = seen.get(normalized, 0) + 1
            owners.setdefault(normalized, []).append(eval_id)
        for i in range(len(checks)):
            for j in range(i + 1, len(checks)):
                score = jaccard(tokens(checks[i]), tokens(checks[j]))
                if EXPECTATION_MERGE_THRESHOLD <= score < 1.0:
                    findings.append({"kind": "similar_expectation", "id": eval_id,
                                     "jaccard": round(score, 2),
                                     "confidence": "MEDIUM"})
    for check, ids in owners.items():
        unique = sorted({i for i in ids if i is not None})
        if len(unique) > 1:
            findings.append({"kind": "shared_expectation", "ids": unique,
                             "check": check[:80], "confidence": "INFO"})
    return findings


def entry_prompt(entry: dict) -> str:
    return str(entry.get("prompt") or entry.get("query") or "")


def analyze_file(path: Path) -> dict:
    record: dict = {"file": str(path), "error": None, "findings": []}
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        record["error"] = f"unreadable or invalid JSON: {error}"
        return record
    if isinstance(data, list):
        evals, record["schema"] = data, "list"
    elif isinstance(data, dict) and isinstance(data.get("evals"), list):
        evals, record["schema"] = data["evals"], "dict"
    else:
        record["error"] = "no evals array at top level"
        return record

    record["entries"] = len(evals)
    record["expectations"] = sum(len(entry.get("expectations", []))
                                 for entry in evals if isinstance(entry, dict))
    record["bytes"] = len(raw)

    findings = find_prompt_candidates(evals)
    findings += find_expectation_candidates(evals)

    ids = [entry.get("id") for entry in evals]
    if len(ids) != len(set(ids)) or (
            all(isinstance(i, int) for i in ids) and ids != sorted(ids)):
        findings.append({"kind": "id_sequence", "ids": ids,
                         "confidence": "ADVISORY"})

    merged_into: dict = {}
    for finding in findings:
        if finding["kind"] in ("dup_prompt", "similar_prompt"):
            merged_into.setdefault(finding["ids"][-1], finding["ids"][0])
    saved = sum(len(json.dumps(entry, ensure_ascii=False)) + 6
                for entry in evals if entry.get("id") in merged_into)
    record["est_savings_bytes"] = saved
    record["findings"] = findings
    return record


def print_record(record: dict) -> None:
    if record.get("error"):
        print(f"file={record['file']} error={record['error']}")
        return
    print(f"file={record['file']} entries={record['entries']} "
          f"expectations={record['expectations']} bytes={record['bytes']} "
          f"schema={record.get('schema', 'dict')}")
    for finding in record["findings"]:
        if finding["kind"] in ("dup_prompt", "similar_prompt"):
            extra = f" jaccard={finding['jaccard']}" if "jaccard" in finding else ""
            print(f"  {finding['kind']} ids={','.join(str(i) for i in finding['ids'])}"
                  f"{extra} confidence={finding['confidence']}")
        elif finding["kind"] in ("dup_expectation", "similar_expectation"):
            extra = f" jaccard={finding['jaccard']}" if "jaccard" in finding else ""
            print(f"  {finding['kind']} id={finding['id']}{extra} "
                  f"confidence={finding['confidence']}")
        elif finding["kind"] == "shared_expectation":
            print(f"  shared_expectation ids={','.join(str(i) for i in finding['ids'])} "
                  f"check=\"{finding['check']}\"")
        elif finding["kind"] == "id_sequence":
            print("  id_sequence out-of-order-or-duplicate")
    print(f"  est_savings_bytes={record['est_savings_bytes']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*",
                        help="skill directories or evals JSON files")
    parser.add_argument("--json", action="store_true",
                        help="emit JSON instead of key=value lines")
    args = parser.parse_args()

    if not args.targets:
        parser.print_usage(sys.stderr)
        return 2

    records = []
    for raw in args.targets:
        path = resolve_evals_file(raw)
        if path is None:
            records.append({"file": raw, "error": "no evals.json found",
                            "findings": []})
            continue
        records.append(analyze_file(path))

    if args.json:
        print(json.dumps({"targets": records}, indent=2, sort_keys=True))
    else:
        for record in records:
            print_record(record)
        print(f"STATUS OK files={len(records)}")

    inspected = sum(1 for r in records if not r.get("error"))
    return 0 if inspected else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.exit(main())
