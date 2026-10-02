# Tasks - feature 307, the sources nested; URLs as links; the campaign notes on GitHub

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

## Occasions

- none: no map, glyph or placement changes; the record's navigation and links are checked by tests and by eye (T04)

## Tasks

- [x] T01 [US1] The nesting: `Catalog.by_kind`, `Build.shelves`, the sidebar's Sources group, the sources index, the one-page record and its contents, the home page, the pager and the open keys; tests in `tests/interactive/test_record_site.py` (FR-001..FR-005; plan D1-D3)
      research: rendering
      verify: DONE. Catalog.by_kind, Build.shelves, source_nodes; sidebar Sources = 9 works sections directly under the heading, kinds beneath, canon lists its works directly; index/all.html/home nested; pager and open keys; test_the_sources_nest_by_section_then_kind... passes (SC-001..003)
- [x] T02 [US2] `sources.linkify` and its call on every page's content (`site_pages.shell`), with the citation-line calls in `citations.works_html` and `Build.entry_html`; unit test and the site-wide no-bare-URL test (FR-006, SC-004; plan D4)
      research: rendering
      verify: DONE. sources.linkify called on every page's content in site_pages.shell (scripts/styles/tags/comments/links skipped); unit test; test_no_page_of_the_built_site_shows_a_bare_url over 2,000+ pages passes (SC-004)
- [x] T03 [US2] The canon rewrite (`specs/307-sources-nav-nesting/migrate/canon_links.py`) run on the 16 entries; the test that every canon entry links GitHub; the rule in `research/CLAUDE.md` (FR-007, SC-005; plan D5, D6)
      research: rendering
      verify: DONE. canon_links.py: 16 entries, 36 of 36 quoted sections matched to GitHub headings (plain text or unique prefix, anchors by sources.github_anchor); canon keys keep their registry link in link_target; test_every_canon_entry_links_its_notes_on_github passes (SC-005); rule in research/CLAUDE.md
- [x] T04 The site looked at in a browser (the sidebar's nested Sources, a source's page, the home page, a linked URL); `make record CHECK=1`; `make done` green; pushed
      research: rendering
      verify: DONE. Chromium: nested Sources sidebar, l7r-median-domain linking each section on GitHub, a kotobank URL clickable; make record CHECK=1 clean; make done green (141 s, 10,429 tests)
