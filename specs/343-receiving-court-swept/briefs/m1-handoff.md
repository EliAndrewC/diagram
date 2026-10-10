# Handoff - features 336, 337, 338 and 343, group M1, session 1 (write) -> session 2 (check)

- SECTION=0104/the-formal-entrance-and-a-guests-arrival-genkan
- SECTION=0099/the-hearing-court-shirasu
- KEY=takayama-jinya-en-tour

Five commits made the four changes the brief asks for, each with a source-reader pass (every source-reader unit is answered; `make record-owed UNANSWERED=1` lists none):
- 343, 998fa3982: Morse's Fig. 283 and a swept Kyoto courtyard (morse-1886-homes, -2), and the entrance-ground absence.
- 336, 5999598c7: the Takayama corridor row, the compound illustration under the new key, the 1830 drawing, and the Edo-plan absence.
- 338, a31fdb044: takayama-jinya-city's listed middle gate and the middle-gate absence, on both pages.
- 337, 8f06d2817: roofed-court-size-absence, listed by `make open-questions`.

Notes for session 2:
- Reading Morse in full turned up one swept yard that the brief did not mention. Inside the gateway of an old Kyoto house, "The yard was well swept, and quite free from weeds". 0104 records it as Morse's own observation from before 1885, at a yard no formal entrance is said to face, so the claim of silence before 1868 stands.
- The "Was the ground before the entrance ever a garden?" bullet now says that both known drawings show open ground inside the gate. But Morse's plate also runs a garden path from a second gateway to the genka, which sits uneasily with the drawing page's verdict that a garden in place of the court is a GUESS. Please weigh that.
- The tooling took this session's feature to be 378. So the round-arbiter's ruling ("continue" on round:source-reader|q:0104@3, which fired because three features' new notes landed on one page) went to `specs/378-research-findings-checked-against-code/arbiter.jsonl` and `gm-review.jsonl`, and the ledger's outcomes are tagged f378.
- The ledger-owed hook lists every source-reader pass twice, once with a shorter wall time and smaller output (41 s for B, 27 s for C, 38 s for 0099). Each pass was dispatched only once, and each has one row in `dev/review-ledger.md`, with the final cost cells.
- Saved pages: `/tmp/l7r-check/343-pages*`, `/tmp/l7r-check/337-pages`, and the Takayama illustration at `/tmp/l7r-dl/343img/map.png`.
