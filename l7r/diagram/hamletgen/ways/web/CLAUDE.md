# `ways/web/` - the lane web (STAGE 4b)

Split from the 1,001-line `ways/web.py` by feature 405 T57 at the 1,000-line bar (the GM 2026-10-21: split into submodules of
about 650 lines, never trim to just under). `__init__.py` re-exports every name the module had, so no importer changed; a test
that monkeypatches a name patches the submodule that looks it up (`web.skeleton`, `web.tidy`, `web.stage`). **Load only the file
the task calls for.**

| file | look here when |
|---|---|
| `skeleton.py` | the cluster's SKELETON, laid after the houses (`_lay_skeleton`, `served_arm`, the rolled shape and the water side) and the web's cut lines (`_web_cut_lines`) |
| `tidy.py` | the web's END TRIMS: `tidy_lane_ends`, a connector's kept end (`kept_connector`) |
| `stage.py` | `stage_web` itself - read it first to see the order the passes run in - and the runs it lays and resettles |
| `__init__.py` | the re-exports only; never add logic here |
