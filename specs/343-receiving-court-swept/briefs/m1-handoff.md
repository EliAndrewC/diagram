# Handoff - features 336, 337, 338 and 343, group M1, session 1 (write) -> session 2 (check)

- SECTION=0104/the-formal-entrance-and-a-guests-arrival-genkan
- SECTION=0099/the-hearing-court-shirasu
- KEY=takayama-jinya-en-tour
- KEY=wheatbaku-machibugyosho-yashiki

Five commits made the four changes the brief asks for, each with a source-reader pass (every source-reader unit is answered; `make record-owed UNANSWERED=1` lists none):
- 343, 998fa3982: Morse's Fig. 283 and a swept Kyoto courtyard (morse-1886-homes, -2), and the entrance-ground absence.
- 336, 5999598c7: the Takayama corridor row, the compound illustration under the new key, the 1830 drawing, and the Edo-plan absence.
- 338, a31fdb044: takayama-jinya-city's listed middle gate and the middle-gate absence, on both pages.
- 337, 8f06d2817: roofed-court-size-absence, listed by `make open-questions`.

Notes for session 2:
- Item A was rewritten after its first commit. A whole-text grep of the archive (done for 0099) found three registered Edo pages that give the ground before an entrance as graveled: wheatbaku-machibugyosho-yashiki (a 6-shaku stone path and black Nachi gravel at the town magistracies; moved from uncited to cited), kazusa-bugyosho (a former South Town Magistracy officer's account) and orange-hatchobori-yoriki (the officers' houses). So 0104 now answers "Graveled, at Edo", and the absence covers only swept, raked or sanded ground and any surface outside Edo. The kazusa and orange write-ups gained a Used-for clause. source-reader round 4 (the arbiter ruled continue, bounded to those notes) read all three and found no contradiction. Morse's one swept yard, in Kyoto before 1885, stays as his own observation.
- The drawing page's two "no page we read puts a garden between the gate and a genkan" sentences now say "no page we read on the genkan and the shikidai", the scope of their absence note. The first adds that both known drawings show open ground just inside the gate. Morse's plate still runs a garden path from a second gateway to the genkan, so please weigh it against that page's garden-is-a-GUESS verdict.
- The tooling took this session's feature to be 378. So the round-arbiter's ruling ("continue" on round:source-reader|q:0104@3, which fired because three features' new notes landed on one page) and on round 4 (the Edo gravel) went to `specs/378-research-findings-checked-against-code/arbiter.jsonl` and `gm-review.jsonl`, and the ledger's outcomes are tagged f378.
- The ledger-owed hook lists every source-reader pass twice, once with a shorter wall time and smaller output (41 s for B, 27 s for C, 38 s for 0099). Each pass was dispatched only once, and each has one row in `dev/review-ledger.md`, with the final cost cells.
- Saved pages: `/tmp/l7r-check/343-pages*`, `/tmp/l7r-check/337-pages`, and the Takayama illustration at `/tmp/l7r-dl/343img/map.png`.
