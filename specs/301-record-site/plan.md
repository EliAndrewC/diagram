# Implementation Plan: the record as a manual

**Branch**: none (main, clone `diagram-reorg`) | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

## Summary

The record stays written as fragments; what changes is what `make record` writes and who reads it. Three moves:

1. **Nothing reads a built page but the GM.** Every reader of the record - the map modals' machinery
   (`interactive/sources.py`), the citations derivation, the scripts under `scripts/`, the tests - reads the
   fragments through the in-memory assembly (`record/store.py`), which already exists and costs about a second for
   the whole record (research R1). That is what lets the built pages leave git without a fresh clone, a test or a
   map render depending on a build having run.
2. **`make record` writes a site, not pages.** Under `research/site/` (gitignored): a home page, one parent page per
   current page, one small page per question and per registry entry, and `all.html`, the single page. The old
   per-page files (`research/<page>.html`, `research/citations/`, `SOURCES.html`) are no longer written at all.
3. **Pointers name fragments.** The modal `Entry:` lines and every pointer in code, docs and specs name a fragment
   path; a script sweeps today's ~2,500 occurrences, a check fails the gate and the push on one that does not
   resolve, and `make fragment-move` moves a fragment with its pointers.

Then the landing, the user-level sudo hook, the repack, and - after the landing - the history scrub.

## Technical Context

**Language/Version**: Python 3.14 (engine, tools), bash (hooks, sync), plain HTML/CSS/JS for the site (no framework,
spec assumption).
**Primary Dependencies**: none new for the site. `git-filter-repo` installed with sudo for the scrub only (not a
project dependency; not added to the lockfiles).
**Storage**: files. Sources tracked under `research/` (fragments, `assets/record.css`, `assets/record.js`, the new
`assets/site.css` and `assets/site.js`); every output under `research/site/` (its `assets/` a copy of those four and the
derived glossary script), gitignored, as are the old outputs' paths.
**Testing**: pytest through `make quick` / `make done`; `make hooks-test` for the guards; the user-level hook's
self-test.
**Target Platform**: the container and the GM's browser opening files from disk (`file://`) - which is why the
navigation data is a `<script src>` and never a fetch (the reason `citations/<name>.js` was a script, spec 211 D1).
**Project Type**: tooling over the research record.
**Performance Goals**: `make record` under 5 s for the whole site (R1: assembly 1.15 s today); render-sync's skip
path under 0.5 s.
**Constraints**: no engine path may read `research/site/`; the build refuses rather than guesses (an unresolved link,
a duplicate id, an unknown fragment).
**Scale/Scope**: 38 pages, 473 questions, 2,127 registry entries (R3), ~3,500 notes; ~430 files carrying pointers.
**Single-artifact target**: no generator changes what it draws. The one map whose modal links are proven by hand
first is `pool/hamlets/inashiro` (the reference hamlet), then the pool through `make maps` (its pages re-render with
the new link form).

## Performance bookends

No generator is changed (no placement, no drawing): the modal machinery's input moves from page files to the same
bytes assembled in memory. The bookends are taken anyway because `interactive/sources.py` runs inside every map
render: `make perf LABEL=301-start` before the first engine edit, `make perf LABEL=301-end` before the push, and the
report read against `301-start`.

## Constitution Check

- **I, II**: N/A - no UI of the webapp's kind. The record site is a reading page, styled by the record's own sheet.
- **III**: N/A - no pool content generated.
- **IV, V**: PASS - no SOURCE block added, moved or edited. The sweep skips every `specs/*/request.md`,
  `<!-- SOURCE: GM NOTES -->` block and README (the GM's).
- **VI**: PASS - each task names its verification below; the map step is two steps (Inashiro, then `make maps`).
- **VII, VIII, IX**: N/A - no in-world content.
- **X**: PASS - ruff, ruff format, pyrefly, red-green tests, 100% coverage over the engine for every new module
  (`record/site*.py`, the pointer resolver). No file past 1,000 lines: the site builder is split by job (links,
  notes, navigation, pages, the single page) from the start. No overlap check is added.
- **XII**: N/A - nothing a map asserts about the world changes; the modal text is untouched, only its link target.
- **XIII**: the regression baseline is taken in a detached worktree before the first engine edit.
- **XIV**: defects found on the way (a broken record link the resolver finds, a pointer to a section that no longer
  exists) are fixed in this feature, each listed in research.md.
- **XVI**: no exception taken. The one judgment call - the parent page shows its page's opening and the list of its
  questions rather than every question in full - is the spec's FR-001 read literally ("a parent section", "each
  question its own small page") and is recorded as D2.

## Design

### D1. The read layer (Phase 1)

- `record/store.py` gains `page_dirs()` - the record's pages enumerated from the fragment directories (a directory
  with `_front.html`), replacing every `os.listdir(...)*.html` page enumeration (`record_pages`,
  `citations.research_pages`, `sources.collection_pages`). Once the pages are not on disk, enumerating them from
  disk finds nothing.
- `assemble_pages` derives the citations page's works block in memory: `citations.derive` takes the assembled
  citations page and the registry as strings rather than reading files. The two-pass write goes away.
- `interactive/sources.py` reads every page through one cached function, `record_text(research_dir, rel)`: the
  in-memory assembly when the page has a fragment directory, the file otherwise (the tests' fixture records are
  whole pages, and they stay valid).
- Scripts that read built pages (`_quote_verbatim.py`, `_record_prepass.py`, `_entry_owed.py`, `_hm_record.py`,
  `gate-stamp.py`'s browser key) read through the same function or the fragments; each is listed in tasks.

### D2. The site (Phase 2)

Layout under `research/site/`:

| path | what |
|---|---|
| `index.html` | home: the record's title, every parent section grouped (Research, Rendering, Cities, Rendering: cities, Sources), the single-page link |
| `<page dir>/index.html` | a parent page: the page's opening (its h1 and introduction, from `_front.html`) and its questions as a list of links, with the opening line of each |
| `<page dir>/<heading id>.html` | a small page: one question, its notes numbered from 1 at its foot, then the works its notes cite |
| `sources/index.html` | the registry's parent: its opening, then its sections (works cited, attested instances, setting canon) each with its entries listed |
| `sources/<key>.html` | one registry entry |
| `all.html` | the single page: a table of contents, every page's opening and questions in order, the citations (all notes, numbered once), the sources |
| `nav.js` | the navigation tree as data, read by `assets/site.js` |
| `assets/` | `record.css`, `record.js`, `site.css`, `site.js` copied from `research/assets/`, and `glossary.js` derived from the glossary - the site is self-contained under one directory |

- **Navigation is data plus one script** (`nav.js` + `assets/site.js`), not HTML repeated per page: the registry's
  2,127 entries in every registry page's sidebar would be ~400 MB of repeated markup (R3). A part's list is drawn
  when the part is opened, so the registry's is not drawn on every page load. Each page carries
  `data-root`, `data-part` and `data-page` on `<body>`; the script draws the tree with every parent listed, the
  current one expanded, the current page marked, and the single page linked at the top. Without scripts a page
  shows a plain "Contents" link to `index.html`.
- **Links** (`record/site_links.py`): every `href` in a fragment is resolved against the page it was written for,
  to a record path and an anchor, then looked up in one index built once - every `id` in the record mapped to the
  page and question that hold it. A question link becomes that small page (with the anchor kept when it is not the
  question's own heading); a page link becomes the parent page; a registry link (`SOURCES.html#key`) becomes
  `sources/<key>.html`; an asset link is rebased; an external link is untouched. On the single page every record
  link becomes `#id`. An `href` that resolves to nothing is a build failure naming the fragment (FR-006).
- **Notes** (`record/site_notes.py`): a small page's references are allocated with the existing `notes.allocate`
  over the question alone (numbers from 1), from the page's merged notes (a note may be written beside another
  question of the same page - it is placed where first cited, R4). The foot is `<section class="footnotes">` with
  the numbered notes and their back links, then "Works cited here": each work's line and write-ups (the existing
  `citations.works_html`), the key linking the document where it was read and the registry entry where not. In a
  note, a key links the work's entry at the foot (`#work-<key>`), which links the document - the hover rule of
  feature 292 kept. The single page allocates once over the whole record in reading order and keys notes
  `fn-<n>` uniquely; its notes stand in one "Citations" part.
- **Ids**: the build refuses a heading id used twice across the record (FR-007), and on the single page any id
  collision at all.
- **Rendering/research cross-links, "not to be confused with", absence notes, originals, passages**: produced by the
  existing modules on the assembled page before the site splits it, so each is written once and resolved by the
  link resolver like any other link.
- **What `make record` writes**: the site, built beside `research/site/` and swapped in whole, so no stale page
  lingers and a reader never meets a half-written site. The glossary script is written into the site's `assets/`;
  `make glossary` assembles and checks the committed `glossary.json` only.
- **The single page carries no glossary hover**: it is about 14 MB, and the hover wraps every term in the visible
  text at load; the footnote hover works there as everywhere. Recorded as a deliberate choice, the small pages
  carrying the glossary.
- **A part's page** lists its questions, each with the first sentence of its opening (the "Not to be confused
  with" box skipped); a registry part lists its sections, each with its entries. `CHECK=1` builds into a
  temporary directory, writes nothing, and exits 1 on any refusal - the "builds cleanly" check (FR-011). `make
  citations` stays as a name that runs `make record`, so the docs and habits that call it keep working.

### D3. The maps (Phase 3)

`research_questions` returns `../../../research/site/<page dir>/<heading id>.html` for each question. The `Entry:`
line names fragments:

    Entry: research/archetypes/120-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html, research/rendering/archetypes/050-how-our-maps-draw-dike-ponds-sangji-yutang.html

in the order the class author quotes them (spec 180 D4 kept). The parser reads paths; the heading comes from the
fragment. `check-entry-headings.py`, `_entry_owed.py`, `entry-gate.sh` and `_check_bundle.py`'s Entry reading move
to the same form. The sweep converts every `Entry:` (R5 counts them).

### D4. Out of git, onto main (Phase 4)

- `.gitignore`: `research/*.html`, `research/{cities,rendering,rendering/cities}/*.html`, `research/citations/`,
  `research/site/`, `research/assets/glossary.js`; `git rm --cached` of every assembled output (FR-009).
- `sync-with-main.sh` push block: `make record CHECK=1` (now: builds cleanly) and `make glossary CHECK=1` (its JSON
  asset is still committed and still checked) stay; the message names the new meaning.
- **render-sync** (`pipeline/render_cache.py`): after the maps, the record is built in main when a stamp differs.
  The stamp is a hash over every tracked file under `research/` (fragments and assets) and the build code
  (`interactive/record/*.py`, `interactive/citations.py`, `interactive/sources.py`, `tools/record_asset.py`,
  `tools/glossary_asset.py`, `interactive/assets/glossary.json`), stored in `research/site/.stamp` (FR-010; SC-005's
  three cases are a test).
- `record-edit-hooks.sh`: an Edit aimed at a built page - an old page path or a site page - is re-aimed at the
  fragment holding the text, as today.
- `scripts/sync-with-main.sh` refuses a clone whose history shares no commit with main's (FR-019), with the re-clone
  command - landed here so it is live before the scrub.

### D5. Pointers (Phase 5)

- **The form**: `research/<page dir>/NNN-<heading id>.html` for a question, `research/sources/NNN-<section>/NNNN-<key>.html`
  for a registry entry, and `research/<page dir>/` for a whole page.
- **The sweep** (`scripts/_pointer_sweep.py`, one-time, kept with a test), landed features' specs included: `research/<page>.html#<id>` maps through
  the id index; `research/<page>.html` followed by one or more quoted headings maps each by the record's anchor rule
  (`github_anchor`, the prefix match `_names` already uses for Entry lines); a bare `research/<page>.html` becomes the
  page directory; `SOURCES.html#<key>` becomes the entry. A match that is not exact goes to the review list
  (`specs/301-record-site/pointer-review.md`), never to a guess (FR-013). Scope: every tracked file outside
  `research/`, less `specs/*/request.md`, READMEs, SOURCE blocks, `dev/bypass-log/`, `scripts/fixtures/` (records of
  what happened), and the Python that names built outputs functionally (each file listed in tasks, edited by hand).
- **The check** (`scripts/check-research-pointers.py`, `--selftest`): every fragment-form pointer in tracked files
  resolves to a file or directory; no old-form pointer `research/<page>.html` remains outside an explicit allowlist
  (the build code and its tests, which name outputs, and the exclusions above). Run at the gate (a test calls it)
  and at the push (sync-with-main, beside `check-entry-headings.py` - a docs-only change takes the DIRECT route).
- **`make fragment-move FROM=<fragment> TO=<fragment>`** (`scripts/_fragment_move.py`): moves the fragment with its
  `.notes.html` and `.originals.html`, rewrites every pointer to it in tracked files, and refuses a move whose
  target exists (FR-015). `research/CLAUDE.md` and `CLAUDE.md` name it as the way to rename.
- **The lint judges what a push changes** (FR-027, the GM's answer of 2026-10-01): `spec-lint --delta`, for a spec
  directory present at the merge base, lints that directory as it stood there (its files read with `git show` into a
  temporary tree) and reports only the findings the push's version adds - compared with each message's `path:line:`
  prefix dropped, as a multiset, so a pointer edit that moves lines adds nothing and a new unlabeled figure is still
  caught. A new directory is linted whole, as today. Its selftest gains both cases. The review gate and the plan gate
  are passed by the sweep through `REVIEW_GATE_OK` and `PLAN_REVIEW_OK` with the reason "mechanical pointer sweep,
  feature 301", which their logs record; no guard is loosened for anything else.
- **Docs** (FR-016): `CLAUDE.md` (the Research bullets), `research/CLAUDE.md`, `docs/research-doctrine.md`, the
  constitution's wording where it names a page as the pointer's target, the skill's `CLAUDE.md`.

### D6. The sudo reminder (Phase 6)

- `~/.claude/hooks/missing-program-hook.sh`, registered in `~/.claude/settings.json` on `PostToolUse` and
  `PostToolUseFailure` with matcher `Bash`. It reads the payload (`tool_input.command`, the tool response's
  stdout/stderr/exit code, or the failure's error text), returns at once unless in a container (podman
  `/run/.containerenv`, docker `/.dockerenv`, `container` in the environment, or a container name in
  `/proc/1/cgroup`), and emits `hookSpecificOutput.additionalContext` - "This container has passwordless sudo:
  install what is missing (sudo apt-get install ..., pip install ...) rather than working around it." - when:
  the output says `command not found` / `not found` for a program / `No such file or directory` for the command's
  own program; or the command is an existence check that came up empty: `which`, `command -v`, `type`, `hash`,
  `whereis`, `dpkg -s` / `dpkg -l` / `dpkg-query`, `apt list --installed`, `apt-cache policy` (`Installed: (none)`),
  `pip show` / `pip list | grep` / `python -m pip show`, `python -c "import x"` (`ModuleNotFoundError`), `test -x` /
  `[ -x ]` / `ls` on a program path, `<program> --version` failing. Every time (FR-023).
- `~/.claude/hooks/test-missing-program-hook.sh`: feeds both payload kinds for every form, a found program, an
  unrelated failure, and every miss with the container markers absent (an environment override points the detector
  at a fixture root). `make hooks-test` runs it when present; `docs/guards.md` and the `CLAUDE.md` table gain a
  user-level row.
- The mount premise (FR-024): `podman ps` is not reachable from inside; the GM's other running containers are listed
  through the host-diagnostics client (`reference_host_diagnostics.md`) and their mounts read. A container without
  the mount is reported to the GM.

### D7. Landing, repack, scrub (Phases 7-8)

- Land: `make done` green, review ledger rows, push (GATED route: engine code changes).
- Repack: `git gc --aggressive --prune=now` on `/diagram` under `flock .clones/.sync.lock`; sizes before and after.
- Scrub (after the landing): in a scratch mirror, `git filter-repo --path-glob`-style removal by a callback that
  drops the assembled-output paths only in commits from `0fef1e6f3` on (pre-258 versions kept: they were the source).
  Verify every commit's tree equals the original's less those paths, the tip tree byte-identical, sizes measured.
  Write `docs/history-rewrite-301.md` with the old-to-new commit map. Message the live sessions (Diagram review) to
  push and pause; the GM force-pushes; then reset `/diagram` to the new main, repack, re-clone every clone under
  `.clones/` (deleting the stale ones, re-creating live sessions' clones and cherry-picking any unpushed commits),
  and confirm every clone's root commit matches main's.

## Phases and verification

| phase | done when |
|---|---|
| 1 read layer | `make quick ALL=1` green with no built page on disk (the outputs deleted first) |
| 2 site | `make record` builds; tests SC-001-SC-003 green; the site opened in the browser test harness and looked at |
| 3 maps | Inashiro regenerated and its modal links resolve (SC-004); then `make maps` |
| 4 untracked | `git ls-files` clean of outputs; render-sync's stamp test green; the record-edit guard's tests green |
| 5 pointers | sweep run, review list resolved, check green at the gate and the push, fragment-move test green |
| 6 hook | its self-test green in this container and with the markers absent; `make hooks-test` green |
| 7 land | `make done` green, pushed, `/diagram` built by render-sync, repacked |
| 8 scrub | verified history, GM force-push, clones replaced, sizes recorded |

## Complexity Tracking

None deferred.
