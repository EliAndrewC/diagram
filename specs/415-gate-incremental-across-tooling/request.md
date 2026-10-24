# Request - feature 415

The GM, 2026-10-24, in the session, after feature 405 T26's landing (8.8 minutes, the gate's test phase 280 s over 10,376
tests) and the four landing fixes:

"So it sounds like a landing currently takes 6 minutes. How does that break down? What might we do about that?"

After the session found the gate had run in full mode:

"Yes, that was the thing I was going to ask, which is that I thought that our landing was efficient in terms of only running tests on things that were changed. And the fact that we're running so many minutes of tests, like I would expect it to save significantly more than 2 or 3 minutes if the whole thing takes 6 to 9 minutes."

After the session proposed five items (T26's change reached 143 of 11,890 baseline tests; the gate ran everything because
`scripts/` had changed since its baseline):

"Why does an engine change that reaches more than 60% of the tests still run everything? Why would it not run the more than 60% that is touched?"

The session added a sixth item, and the GM:

"Yes, please file the feature with those 6 items, and then work the entire feature from start to finish. Thank you."

## The six items, as the session proposed them and the GM approved

1. Narrow the tooling rule: a change under `scripts/` no longer forces a full run (tooling tests are already reused per test
   on their reads); a Makefile change does only where the lines that change how tests run moved; `pyproject.toml` only in
   its pytest and coverage sections; a lockfile still does. With tests, and the gate measured on the next real landing.
2. Record the reason for every full run in the gate's run record.
3. Run the cohort's fresh block after the push instead of on the landing path.
4. Run `cover-changed` beside the gate instead of before it.
5. Record each gate phase's time in the run record.
6. Drop the 60% cutoff from landings: run what is reached, however much, and refresh the baseline in the background. First
   measure the fixed cost and the per-test cost on a few real landings, so the change rests on numbers rather than a second
   guess.
