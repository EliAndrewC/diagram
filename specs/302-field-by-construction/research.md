# Research - feature 302, the comb field built by construction

## R1. Where the current field's time goes (observed 2026-10-01, method: `harness.py` `timed_fit`, fastest of three, load ~7)

`fit_field` on the captured arguments of each recorded input, every carve and finish step timed inclusively:

| input | fit s | close_seams | planted_area | _carve | dry & beans | trial carves | plots |
|---|---|---|---|---|---|---|---|
| inashiro | 1.047 | 0.496 | 0.190 | 0.164 | 0.123 | 3 | 600 |
| kashikawa | 1.104 | 0.688 | 0.167 | 0.141 | 0.035 | 3 | 775 |
| mizuguchi | 0.573 | 0.344 | 0.062 | 0.047 | 0.094 | 2 | 436 |
| sawada | 2.392 | 1.666 | 0.307 | 0.265 | 0.046 | 3 | 1052 |
| inashiro at 10 households | 0.817 | 0.407 | 0.145 | 0.112 | 0.093 | 4 | 379 |
| inashiro at 20 households | 1.264 | 0.556 | 0.227 | 0.194 | 0.197 | 3 | 793 |

The skeleton (`_comb_skeleton`, `_comb_threads`, `_comb_march`, `_comb_drain`, `_comb_canal_pieces`, `round_channel_joints`)
is under 0.04 s on every input. The seam repair and the prediction - what the redesign removes - are 64-82% of the fit.
