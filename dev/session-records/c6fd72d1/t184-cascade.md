# T184's 63 owed pop-up units: why the cascade rules sent them all on (read-only diagnosis, 2026-11-23)

**Bottom line.** The tooling that landed did run. The split's verbatim moves were all recognized: 15 blocks moved to 0332 and 9 to 0333 were counted as moved. All 21 pop-ups still fired, on a T185 defect: a note key that moved to the pointer's target page still counts as "gone". Fixing that leaves 12 pop-ups. A second defect, in the echo filter, accounts for 3 of those. That leaves **9 pop-ups (27 units) owed under the rules**. One of the 9 is owed only because a one-word gloss was added to a moved sentence, so **8 pop-ups (24 units) are owed on substance**.

## 1. Which tooling ran
- There were 3 triage runs, all in the T184 session (times local, from the 451 event log):
  - 14:49: the `check-bundle` agent, 81 units, recorded 14:58.
  - 15:11: `make modal-triage`, 57 units, agent run, recorded 15:14.
  - 16:35: `make modal-triage`, 63 units, agent run, `make modal-triaged` 16:37.
- The first two runs came before T185 and T186 were committed (604541c046, 15:27) and landed (a2999b96fa, 15:31). They ran on work-in-progress code in this clone (`triage/change.rs` was untracked then).
- The 16:35 run used the landed rules. Its `l7r-gate` was built at 15:55:45 from the committed sources (triage.rs mtime 15:09, change.rs 15:48; the owed crate is clean against HEAD), so it includes T185, T186 and T191.
- The mechanical clears and the echo filter ran before the agent. They cleared 0 units (`/tmp/t184/mt.log`).
- The baseline every unit diffed against is main's page (0009 f365914ec4, 0059 1334409fc9).
- The 4 "cleared by the tool" records on intake_place and intake_siting were written by T187's session at 15:24.

## 2. The current filter re-run, read-only
- Method: a `--shared` scratch clone at 31310c2b1b with the uncommitted change applied, and a copy of the answer store with the 63 marks removed. The bundle reproduced the live MANIFEST exactly. Then a debug build printed each unit's `fires` inputs. The scratch clone, build and store copies have been deleted. Logs: `tmp/t184-dbg-cur.log` and `tmp/t184-dbg-fix.log`.
- **All 21 fire on rule C first** ("its Sources key X is gone from the page"). Every such key is still on 0332 or 0333: kotobank-warazuka, kotobank-nimosaku, nimosaku-jawiki and hirogawa-genryu-noka on 0332; suido-ishizue-iseki, shimane-toshuko-lecture, hrr-agagawa-dento, kotobank-shigarami, suido-ishizue-manyoshu, mizu-shiba-izeki and kotobank-jakago on 0333.
- Echo as landed, with key-gone set aside:
  - **Fires on 12:** hamlet/paddy, hamlet/barley, hamlet/irrigation-ditch, hamlet/weir, choice/intake--open, --weir, choice/weir_form--crib, --fence, --frame, --gabion, choice/winter_crop--barley, --none.
  - **Clears 9:** town_nearness--near and --far, and the seven water_source_position pop-ups.
  - No pop-up states a single case, so the new-finding arm never fires.
- Echo with its nearest-sentence search widened to the pointer's target (the fix below): **fires on 9.** Each pop-up and the sentence it fires on:

| pop-up | sentence it fires on | class |
|---|---|---|
| hamlet/barley, winter_crop--barley | "the paddy was ... drained in winter" | (b) |
| winter_crop--barley, winter_crop--none | "barley is weak to damp." | (b) |
| winter_crop--none | "a wet one lay to its single crop of rice" | (c) |
| intake--open, intake--weir | "in old Japan a weir mostly closed only half the river" | (b) |
| intake--weir | "the prototype of the weir ... Yayoi" | (b) |
| intake--weir, crib | "the frames were built as the old intakes were ..." | (c) |
| hamlet/weir, gabion | "Diversion weirs of the Edo period were built of timber frames ..." | (c) |
| hamlet/weir, frame, gabion | "The first weirs were built of whatever wood ..." | moved, plus a gloss |

  The last row's sentence moved to 0333 as "The first weirs (seki) were built ...". It is the only hit for weir_form--frame.

## 3. The page diffs against main
- **(a) Moved verbatim, cleared correctly:**
  - 0009 to 0332: the lead, the warazuka li, the straw uses, the rick on a barley paddy, the back crops, the Heian, Edo and prewar-line items, the medieval manuring, kanden, the rape lead and its 4 items (15 blocks).
  - 0059 to 0333: the lead, Itazuke stakes, shigarami, Kawaharazono, frames/gabions/brushwood, the oblique weir, the gabion size, the gabions on small streams, the thickness (9 blocks).
- **(b) Restored, back to the wording before cce80ca436:**
  - On 0009: "already lets the water out", the 1975-76 survey, "period was long", "a drain in the growing season ...", "So every depth above is modern", "present-day guide".
  - Restored in the moved blocks on 0332: "the water was let off", "cannot be grown in a wet paddy".
  - On 0059: "half-river closures", "A Japanese engineering lecture".
  - Restored in the moved blocks on 0333: "Held back with nearby wood", "so weirs have been built for", "Japan began to modernize in 1868", "works says intake works ...".
- **(c) Other edits:**
  - The two pointers and two split comments.
  - On 0332: "a wet one could not carry the barley" (a quote-check EDIT), and "no page we cite says".
  - On 0333: "A Japanese encyclopedia, after an older work" (replacing "An official handbook"), the Edo item restated as "Some flood-dividing weirs ... frames weighted with stone", and "(seki)" added to the first-weirs sentence.
- **Pop-ups firing on (a) alone:** none, once the defects are fixed. weir_form--frame fires only on a moved sentence whose one change is the inserted gloss "(seki)". The echo rule as written marks an insertion, so this is the rule, not a code fault, but it is not a claim change.

## 4. Report
- **Owed:** all 63 units (21 pop-ups) were sent on.
  - Under the landed rules with both defects fixed: **27 units (9 pop-ups)** are owed.
  - On substance, **24 units (8 pop-ups)**: hamlet/barley, hamlet/weir, choice/intake--open, --weir, choice/weir_form--crib, --gabion, choice/winter_crop--barley, --none.
- **Sent on wrongly: 36 units (12 pop-ups).**
  - All 9 town_nearness and water_source_position pop-ups. Only defect 1 sent these.
  - hamlet/paddy, hamlet/irrigation-ditch and weir_form--fence. Defect 2 sent these too.
  - Arguably also weir_form--frame (the gloss only).
- **Defect 1 (T185):** `rust/gate/crates/owed/src/record/triage.rs:359-360`. `c.keys_gone` is filtered only by the pop-up's Sources. It is never checked against the marks on the other pages in `all`, which includes the pointer's target. `page_change` builds `keys_gone` from the source page alone (`triage/change.rs:153-159`). So every note a split carries with its sentences reads as "gone", and rule C fires before echo is consulted. The MANIFEST then prints "Note keys no longer on the page", which the agent relied on.
- **Defect 2 (T186):** `rust/gate/crates/owed/src/record/triage/change.rs:379`. In `echo`, `near` is chosen from the source page's sentences only (`fresh`), not from `reached_now`. A block that moved with any edit is diffed against an unrelated 0009 or 0059 sentence, so every word counts as changed. The pop-up then fires on words that did not change.
- **Also in T186:** `replay_landing` (`triage.rs:453-470`) passes empty reached sets and never follows pointers. So `replay --landing` cannot model a split. Given that, I re-ran the filter through the bundle path rather than the replay verb.
- **Did the triage agent override a mechanical clear? No.** The tool cleared nothing. The agent's 21 TOUCHES cite rule C on the note keys the tool wrongly listed as gone, plus "removed" blocks that it could not see now stand on 0332 and 0333.
