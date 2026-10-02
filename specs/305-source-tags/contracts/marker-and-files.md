# Contract - the marker, the files, the tools

## The marker (last line of a registry entry file)

    <!-- tags: period=<id>[,<id>...]; region=<id>[,<id>...]; kind=<id>[,<id>...] -->

Each facet once, in any order; the first value of each facet is primary. A canon entry (citation line names `l7r.md`
or `budgets.md`) carries none.

## `research/source-sections.json`

    {"sections": [
      {"id": "works-canon", "title": "Setting canon", "description": "...", "canon": true},
      {"id": "works-premodern-japan", "title": "Premodern Japan", "description": "...",
       "takes": [{"period": "premodern", "region": "japan"}]},
      ...
    ]}

## Tools

- `make reserve KIND=registry KEY=<k> [URL=<u>] [TAGS="period=..; region=..; kind=.."]` - the stub ends with the
  marker; without TAGS, a placeholder marker the build refuses.
- `make record CHECK=1` - refuses every FR-010 case, all named in one run.
- `make source-tags-contract` - rewrites the derived vocabulary block in `.claude/agents/source-applicability.md`.

## Rendering (the built site)

- Under each work's heading: `<p class="srctags"><span class="srctag srctag-period" data-def="..." title="...">Premodern</span> ...</p>`.
- A works list: `<h3 class="works-section" id="...">Title</h3><p class="works-section-desc"><em>...</em></p>` then the
  works as `<h4 id="work-<key>">` (question foot) or the entry's own heading demoted to `<h4>` (single page).
