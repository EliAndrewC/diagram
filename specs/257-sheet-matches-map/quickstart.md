# Quickstart - feature 257

From `.claude/skills/diagram/`:

```text
make pack-audit ARGS=pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg
    # ... trees_overlap: OK / matches_map: OK (or "on no map" for a sheet with no declaration)
make test-file FILE=tests/tools/test_registry.py       # every check fires on its fixture, passes every sheet
make test-file FILE=tests/tools/test_mapmatch.py       # the three directions, the grain, the refusals
make test-file FILE=tests/test_mode_a_sheets.py        # the sweep
make size-table PLAN=pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg   # before size-audit
make building-programs CHECK=1                          # the rendered tables (the site column) are current
```

To put a sheet on a map: one line in its notes,
`**On map**: legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json - religious at (392, 1074) = hall`,
then `make pack-audit` names every disagreement in both directions.
