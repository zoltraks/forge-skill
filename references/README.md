# References

## Purpose

> **Scope:** Index of the evidence and convention references under `references/`
> **Key items:** load triggers, authority levels

Load a reference only when the pipeline phase that needs it runs - phase 0 loads
the two contract files, later phases load on demand.

## Index

| File                      | Load when                                                 |
|---------------------------|-----------------------------------------------------------|
| `astra-conventions.md`    | Phase 0 and the phase 2 compatibility matrix              |
| `skills-spec.md`          | Phase 0 and frontmatter writing or validation             |
| `skill-anatomy.md`        | Phase 2 - deciding what the generated skill contains      |
| `trigger-design.md`       | Phase 2 - writing descriptions, keywords, and near misses |
| `markitdown-reference.md` | Phase 1 - any binary or markup source conversion          |
| `research-methods.md`     | Phase 1 - classifying the research and picking depth      |
| `source-integrity.md`     | Phase 1 - every external source, also phase 3 fill review |

## Authority

`astra-conventions.md` and `skills-spec.md` are contractual - generated output
must satisfy them. The rest are methodological guidance the agent applies with
judgment.
