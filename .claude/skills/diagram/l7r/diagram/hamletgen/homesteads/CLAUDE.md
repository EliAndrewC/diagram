# `homesteads/` - the homesteads and what stands among them

Split from the 1,330-line `homesteads.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.

## Look here when

| file | look here when |
|---|---|
| `seats.py` (162) | where a homestead may sit - the front row, the lane frontage that fronts it, the cluster's aspect ratio, and whether a seat is allowed at all |
| `bamboo.py` (144) | the household bamboo strip: whether a strip is blocked, and the per-household placement |
| `fixtures.py` (410) | what stands in a farmstead's yard - the privy/well/heap/coop pass, its weighted roll, and the two ownership and trunk probes it leans on |
| `wells.py` (314) | the public wells - how many a settlement of this size wants, and the pass that seats them |
| `stages.py` (334) | STAGES 5 and 6 - the homesteads themselves and what stands among them. Read this first |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |
