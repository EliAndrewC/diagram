# Plan - feature 290, the perceptual label order

Spec: [`spec.md`](spec.md) (FAITHFUL, round 1). Request: [`request.md`](request.md).

## Decisions

- **D1 - the order** (FR-001). `labels/standard.py` `POSITIONS` is PerceptPPO's eight in its order: above, below,
  right, upper right, lower right, left, upper left, lower left; the comment cites the study and its Table 1, and says
  it replaced feature 289's deviation. The two "slightly" positions go: the study leaves them out as a relic of grid
  printing (its own words, quoted in the record).
- **D2 - the fallback's sides** (FR-002). `_extended_cands` walks above, below, right, left again.
- **D3 - the record** (FR-003). The research entry's "Which side" paragraph says the maps follow the readers' order,
  cited to the study (nearly 800 readers; the preference for above; its order; why no "slightly" places - one new
  note); the textbooks' order and the other published orders stay as context; the deviation's grounds note and the
  absence note on small drawn objects go (nothing rests on them now). Evidence comment and the registry entry's
  "Used for" updated. Checked by `quote-check`, `record-format` and `source-applicability`.
- **D4 - the maps** (FR-004). The four hand sheets regenerated (`make map`); tests updated with the order.
- **D5 - verification**: `make quick`, then `make done`.

## Constitution Check

- XVI: the published order as published, nothing appended (spec review round 1).
- XII: the record calls it the order followed and cites it; no deviation remains to label.
