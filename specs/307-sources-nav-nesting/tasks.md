# Tasks - feature 307, the sources nested; URLs as links; the campaign notes on GitHub

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

## Occasions

- none: no map, glyph or placement changes; the record's navigation and links are checked by tests and by eye (T04)

## Tasks

- [ ] T01 [US1] The nesting: `Catalog.by_kind`, `Build.shelves`, the sidebar's Sources group, the sources index, the one-page record and its contents, the home page, the pager and the open keys; tests in `tests/interactive/test_record_site.py` (FR-001..FR-005; plan D1-D3)
      research: rendering
- [ ] T02 [US2] `sources.linkify` and its calls in `citations.works_html` and `Build.entry_html`; unit test and the site-wide no-bare-URL test (FR-006, SC-004; plan D4)
      research: rendering
- [ ] T03 [US2] The canon rewrite (`specs/307-sources-nav-nesting/migrate/canon_links.py`) run on the 16 entries; the test that every canon entry links GitHub; the rule in `research/CLAUDE.md` (FR-007, SC-005; plan D5, D6)
      research: rendering
- [ ] T04 The site looked at in a browser (the sidebar's nested Sources, a source's page, the home page, a linked URL); `make record CHECK=1`; `make done` green; pushed
      research: rendering
