# Feature Specification: Hamlet labels in the zoomed-out hit map (found by feature 267, 2026-09-27; unmeasured)

**Status**: Filed - from future-work/cross-cutting.md, "Hamlet labels in the zoomed-out hit map (found by feature 267, 2026-09-27; unmeasured)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

A small label's blended glyph edges can answer the hit map as the kind one palette step away. It is fixed for magistracy
pages only (`interactive/raster.py` `id_map(crisp_text=)`, used on a Mode A sheet's page; the hamlet pages are held
unchanged). Sketch: measure a hamlet page's hit map at the smallest label size first; if it misreads, pass `crisp_text`
there too and re-measure the page's size and build time.
