# Tasks - feature 274, leaner research sessions

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D11). Research: [`research.md`](research.md).

- [x] T01 `scripts/_brief_load.py` and its tests on real-brief fixtures (D1)
      research: rendering
      verify: DONE. test_brief_load.py 12 green: real-brief fixtures V2 9, C1 6, X1 10, S 8 refused; g1/h1 check 2; owed brief 6 on kind=check; one line of six sections 6; ranges on disk
- [x] T02 The runner counts every brief at launch and at `then:`, refuses or STOPS, `WRITE_CAP_OK` logged (D2); tests
      research: rendering
      verify: DONE. test_page_session.py green: launch refusal exits 2 before anything is made; then: refusal writes STOPPED and ends the queue; WRITE_CAP_OK needs a reason and is guard-logged
- [x] T03 Continuation: per-session `L7R_PAGE_SESSION` / `L7R_CONTINUE`, a left brief queued next (D3); tests
      research: rendering
      verify: DONE. test_page_session.py green: L7R_PAGE_SESSION/L7R_CONTINUE per session; a left continue.md is queued before the then: checks and logged continued; an over-cap one STOPS
- [x] T04 `make reserve` caps a page session at ten registry keys, `KEY_CAP_OK` logged (D4); tests
      research: rendering
      verify: DONE. test_reserve_prefix.py green: 11th registry key of a capped session refused with the continuation; glossary uncapped; per session; KEY_CAP_OK logged; runner exports L7R_KEY_CAP to write briefs only (test_page_session)
- [x] T05 `make lines` and `make append` (D5); tests
      research: rendering
      verify: DONE. test_coord.py green: lines numbered with shown-of-total and the cut count; append one line without printing, quotes kept; both through make from the clone root
- [x] T06 The slim rules file, the floor flags, the drift test (D6)
      research: rendering
      verify: DONE. floor_flags excludes both root CLAUDE.md files and appends the rules after the authorization (tested); test_page_session_rules.py maps every house-style and research bullet; the slim file gained the record-the-why bullet and the caps
- [x] T07 `brief.py` declares its kinds (D7); test
      research: rendering
      verify: DONE. test_brief_kinds.py green: every template declares its kind (assertions, check, split, check) and every call site passes it
- [x] T08 Docs: research CLAUDE.md, research-record-rules.md, root CLAUDE.md (D8)
      research: rendering
      verify: DONE. research CLAUDE.md, research-record-rules.md and root CLAUDE.md state both caps, the page-load line and its four kinds, the continuation and make lines/append with R1's figures; make quick clean
- [x] T09 The probe, recorded as research.md R2 (D9)
      research: rendering
      verify: DONE. research.md R2: probe first turn 19,642 (old) -> 13,050 (new), -34%
- [x] T10 The owed post-landing measurement in future-work/cross-cutting.md (D10)
      research: rendering
      verify: DONE. future-work/cross-cutting.md holds the owed post-landing measurement with measure/'s scripts and R1's baseline
- [ ] T11 `make done` green; land
      research: rendering
- [ ] T12 Tell the research sessions, after the landing is on main (D11)
      research: rendering
