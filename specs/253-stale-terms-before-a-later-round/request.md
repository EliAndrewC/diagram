# Where this feature comes from

Asked whether the spec review process had been audited, the session split every recorded `spec-fidelity`
run by review type (2026-09-19): later rounds are 274 of 425 runs and about 61% of the process's cost,
a later round costs nearly what a first reading does, and in features 251 and 252 most later-round
findings were text the session had left STALE - after a tier changed, other passages of the spec, a
results table and a success criterion still said the old thing. The session suggested:

> a tooling change that costs no model tokens. Before dispatching a later round after a tier, figure or decision changes, the session would grep the feature directory for the old value and fix every hit first. That targets the 61%. I haven't built or tested it.

## The GM's words (2026-09-19)

> That does seem like a good idea so please implement that suggestion, thanks.

(The same message asked for a wider audit of how the checks could be split or tightened; that is analysis
reported to the GM, not part of this feature.)
