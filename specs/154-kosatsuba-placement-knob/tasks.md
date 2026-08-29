# Tasks: the kosatsuba's placement is a knob

Spec: [`spec.md`](spec.md) - `spec-fidelity` FAITHFUL at round 3 (2026-08-29).

Every task carries its research class (CLAUDE.md, constitution v2.12.0). A **physical** task is about
how a place was built or lived in and carries three boxes; "the record already answers it" ticks the
research-pass box WITH the pointer, which is the case throughout here - the GM's whole correction was
that this question is already researched.

---

- [x] **T01 - the placement registry and its affordance rule.** Register
      `Knob("kosatsuba_seat", ["center", "entrance", "frontage"], default="center", typing_rule=...)`
      in `settlement/_knobs.py`. The typing rule IS the affordance test (FR-003): `center` always
      holds; `entrance` needs a recorded connector; `frontage` needs a house carrying
      `role == "headman"`. Reads the manifest the validator reads, never assumes.
      `research: physical`
      - [x] research pass - the record already answers it: `research/urban-features.md`, the
            kosatsuba bullets, sources READ 2026-08-26 (feature 133 T13)
      - [x] source-reader confirmed - `fuchu-kosatsuba`, `ogose-kosatsuba`, `kosatsu-jawiki`,
            `adachi-kosatsu`, all READ under feature 133 T13; this feature adds none (FR-007)
      - [x] recorded and cited - the registration carries the attesting sentence and the reason each
            withheld placement is withheld

- [x] **T02 - the anchor per placement.** A pure function from the manifest to the point (or points)
      a placement is measured to: the dwelling centroid for `center`, the connector's mouth at the
      cluster for `entrance`, the headman's house for `frontage`. Lifted and testable with plain
      dicts (GM 2026-08-28), because that is what makes T06 possible without rolling a map.
      `research: physical`
      - [x] research pass - `research/urban-features.md`: "the entrances and centers", "before the
            gate of the village officials' houses", "the place where villagers assembled"
      - [x] source-reader confirmed - same four sources, READ
      - [x] recorded and cited

- [x] **T03 - the objective becomes the anchor.** `place_kosatsuba` scores candidate seats by the
      selected placement's anchor instead of the single busiest-node objective. Everything that makes
      a seat LEGAL is untouched (FR-004): the verge distance, `_fits`, `off_every_bed`, the roadside
      preference and the caption machinery. The placement chooses which way and where along it.
      `research: rendering`

- [x] **T04 - tier scope, with Hirameki pinned.** The knob applies at `scale in ("hamlet", "village")`
      only (FR-009); towns and cities keep their present seats. `pool/towns/hirameki.gen.py` calls
      `place_kosatsuba()`, so this is a requirement and not an assumption, and its board position is
      asserted byte-identical (SC-005). `research: rendering`

- [x] **T05 - the map states which placement it took.** Record it in the manifest (FR-005) so the
      checks, a later reader and the interactive map can all name it, with its accurate / deviation /
      guess class and its sources. `research: rendering`

- [x] **T06 - unit tests over plain inputs.** The affordance rule (each placement offered exactly
      where its evidence is present), the roll's determinism (same seed, same placement - FR-002,
      SC-004), and each anchor. No map rolled.  `research: rendering`

- [x] **T07 - one map per knob VALUE, not a cohort.** Three values, so three maps (CLAUDE.md: "a
      feature adding a KNOB owes one map per knob VALUE - three, not forty-eight"). Measure SC-001
      (Sawada's board off the spur), SC-002 (two materially different seats), SC-003 (the pool gates
      green), SC-004 (re-roll reproduces), SC-005 (Hirameki unmoved) and SC-006 (the chosen seat holds
      the board AND its caption, or the fallback is taken and reported). `research: rendering`

- [x] **T08 - close the record.** `sawada.notes.md`'s OPEN entry closed with the measured outcome;
      the pointer to the knob added at `research/urban-features.md`'s placement bullet and at
      `settlements/urban-features.md` (FR-008). `research: rendering`

- [x] **T09 - independent review before it ships.** `settlement-review` on the maps whose board moved
      - the author is not a reliable reviewer of their own visual output. `research: rendering`

- [x] **T10 - GM acceptance.** The GM sees the maps and rules. `research: rendering`


---

## Closing note

All ten tasks done. T09's review ran four times across three maps and earned it: it caught a knob that
was RECORDED but not DRAWN (the frame guard silently overriding the placement on two of three maps,
fingerprinted by verge signature - 5.99/5.97 ft from `frame.py` against 4.01/4.05/3.95 from
`place_kosatsuba`), a real 40 ft hole punched in Kashikawa's shelter belt, and a caption-side rule that
could not fire on the path most boards take.

T07 owed one map per knob VALUE. Two of the three are exercised on live maps - `center` on Kuwabata,
`entrance` on the other four. **`frontage` is exercised only in unit tests**, and honestly so: it is
gated on a house carrying `role == "headman"`, which every pool VILLAGE records exactly once and no
hamlet records at all, and every village is a frozen legacy map that does not re-roll. Recorded rather
than papered over.

T10, the GM's acceptance, was given in conversation - and with a correction worth keeping. They pushed
back on the framing twice: *"literally every place that you have ever described the notice board as
being put as specified by these different tunable knobs is all fine ... none of the problems that you
have described recently sound like actual problems to me."* They were right. They then asked whether
the automated checks were too strict, and the audit says they are not: seven live gate checks name the
board, five only assert it exists, and the two substantive ones require it within ~12 ft of a lane and
facing the way it fronts - exactly the historical requirement. No board check failed at any point in
the feature. The noise was in how three unlike things - a real map defect, a legibility issue and a
manifest-labelling bug - were reported in one register.
