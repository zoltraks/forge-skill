# Tests

## Purpose

> **Scope:** Index of the deterministic unit tests under `tests/`
> **Key items:** suite table, invocation

Every tool under `scripts/` carries a test file here, covering at least one
failing fixture. Synthetic skill trees are built in temporary directories - no
shipped fixtures are required.

## Suite

| File                       | Tool covered                  |
|----------------------------|-------------------------------|
| `test_audit_skill.py`      | `scripts/audit-skill.py`      |
| `test_archive_skill.py`    | `scripts/archive-skill.py`    |
| `test_convert_source.py`   | `scripts/convert-source.py`   |
| `test_render_templates.py` | `scripts/render-templates.py` |
| `test_validate_skill.py`   | `scripts/validate-skill.py`   |

## Invocation

```
python3 -m unittest discover -s tests -v
```

Part of the maintenance validation suite in `docs/MAINTENANCE.md`.
