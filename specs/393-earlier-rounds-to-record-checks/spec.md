# Feature 393: Earlier rounds to the record checks - a later round reads what the earlier rounds ruled, and why

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=393-earlier-rounds-to-record-checks`)

**Created**: 2026-10-18

**Status**: Draft

**Approved**: the GM, 2026-10-18, "Yes, please file the feature and then work it"

**Affects**: tooling, review process, research record

**Input**: `request.md` - the GM's note, the session's answer and the GM's instruction, verbatim.

## Why

The GM's note: *"give each reviewer the earlier rounds' verdicts and reasons to prevent reviewer loops"*. Three kinds of review
here already get them: `spec-fidelity` (feature 249: `review-round-hooks.sh` puts the previous verdict verbatim and the diff
since it into every later round), the map reviewers (`glyph-check`, `building-review`, `settlement-review`: the unit's previous
verdict file and the notes' "Settled by the GM" section and Review log, features 240 and 294) and the round arbiter (feature
375: every round marked NEW / REPEATED / REVERSING).

The research-record and pop-up checks do not. A bundle from `scripts/record/check_bundle.py` (quote-check, record-format,
source-reader, intro-check, translation-check, entry-drift, record-style) carries the artifact, the
prepass and THE CHANGE, and nothing an earlier round said. A bundle from `scripts/record/modal_bundle.py` (modal-form,
modal-depiction, modal-research) carries only the wording research rounds fixed (`research_held`), not any round's verdict or
its reasons. So a later round judges the pop-up afresh, and may raise again what an earlier round raised and the session
answered, or ask back for what an earlier round took out.

These checks are where the rounds pile up: of the 106 round-arbiter rulings feature 385's audit counted
(`specs/385-approach-checklist/audit.md`), 85 were on the three pop-up checks (modal-depiction 40, modal-form 23,
modal-research 22) and 18 on record checks; about 100 of the 106 ruled that the next round would re-read text already passed.
Only the arbiter, AFTER the cap, sees the earlier rounds; the round that re-raises never did.

## What "it" is, read literally

"Each reviewer" = every check whose bundle `check_bundle.py` or `modal_bundle.py` builds (the list above). "The earlier
rounds" = the earlier dispatches of the SAME check on the SAME subject (a question page `q:<n>` or a pop-up `modal:<uid>`) that
the check state (`<git common dir>/checks-open.json`, `scripts/hooks/lib/hm_checks.py`) holds. "Verdicts" = each round's
verdict line and findings, as `arbiter_bundle.py` already reads them (`el.verdict_of`, `findings_of`). "Reasons" = each
round's whole reply (the finding's own reasoning), what became of its EDIT blocks (applied or not, against the file as it
stands), and every round-arbiter ruling on the unit with its `why`.

## Requirements

- **FR-001 The bundle carries the earlier rounds.** When a bundle is built for a check that has an earlier round on a subject
  the bundle's owed units name, its MANIFEST gains an `## Earlier rounds (feature 393)` section, per check and subject: each
  earlier round's number, verdict and findings (marked NEW / REPEATED / REVERSING by `arbiter_bundle.mark_rounds`), each of
  its EDIT blocks marked APPLIED or NOT APPLIED (`arbiter_bundle.last_edits`), and the file holding its whole reply, copied
  into the bundle (`earlier/<check>-<subject>-round-<n>.md`). A round with no reply kept says so. With no earlier round, the
  section is absent and the bundle is byte-identical to today's.
- **FR-002 The arbiter's reasons travel too.** Every round-arbiter ruling recorded on that check and subject in the active
  feature's `arbiter.jsonl` (`round:<check>|<subject>@<n>`) is listed under it with its ruling and its `why` (and `what`,
  for a `continue`: what the next round must look at).
- **FR-003 The contract says what to do with them.** Each of those checks' agent files gains ONE shared paragraph, the same
  words in each (a test holds them equal): read the Earlier rounds section before the artifact; a finding an earlier round
  raised that is APPLIED is settled - confirm it holds, do not re-raise it; an item an earlier round passed is re-opened only
  where THE CHANGE lists its block or note; a NOT APPLIED finding is re-raised only with a reason the earlier reply did not
  give; a `continue` ruling's `what` bounds the round; to reverse an earlier round's verdict, say `REVERSES round <n>` with the
  reason. Nothing in it widens or narrows what the check judges.
- **FR-004 One builder, every bundle.** The section is built by one function used by every MANIFEST write in
  `check_bundle.py` (the question, key, keys and intro bundles) and `modal_bundle.py` (the per-pop-up and the batched top
  MANIFEST, which points to each pop-up's own section), reading the check state READ-ONLY. It does not change how a round is
  keyed, counted or capped (`hm_checks.py`; the Money session's round-key fix is theirs).
- **FR-005 Cheap where nothing happened.** A first round's bundle costs no extra read: no state file, or no earlier dispatch,
  writes nothing. The section's per-round text is a summary (verdict, marked findings, edit marks); the whole replies sit
  beside the MANIFEST, read only when a finding needs its reasoning.

## Out of scope

- `spec-fidelity` and the map reviewers already have this (249, 240, 294); their mechanisms are not touched.
- Round keying and counting (`hm_checks.dispatch`, `fresh_reading`, `first_look`): the Money session's planned fix (b), a
  source-reader on different new notes of one question counted as successive rounds, is theirs (agreed 2026-10-18).
- Grouping pop-ups that share a template paragraph into one unit (feature 385's proposal 1, the Diagram backlog session): it
  will build on `modal_bundle.py` after this lands.
- `source-applicability`: the check state keeps no subject for it (`hm_checks.PAGE_CHECKS` leaves it out: its unit is a
  source, not a page), so there is no earlier round to hand it; its contract is not touched, which also keeps clear of
  feature 391's edit to it (the Money session).

## Success criteria

- **SC-001** A test builds a question bundle and a pop-up bundle over a fixture check state holding two earlier rounds (one
  with an applied EDIT and one not, one arbiter `continue` ruling), and the MANIFEST lists both rounds, both edit marks, the
  ruling's `why` and `what`, and the copied replies.
- **SC-002** The same bundles over a state with no earlier round are byte-identical to the bundles built without this feature.
- **SC-003** A test holds the shared contract paragraph identical in every listed agent file.
- **SC-004** `make quick` and `make hooks-test` green; the landing's route is DIRECT (no engine code).

## Coordination (the GM's instruction)

Agreed by message on 2026-10-18 with the Money session (features 389-391) and the Diagram backlog session (feature 385): this
feature owns `check_bundle.py`, `modal_bundle.py`, a new `scripts/record/earlier_rounds.py`, their tests and the shared
contract paragraph; it does not edit `hm_checks.py`, `arbiter_bundle.py`, `page_session_runner.py`,
`agent-prefix-hooks.sh`, `record_owed.py` or `source-applicability.md`. Both sessions are told when 393 lands.
