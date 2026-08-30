# The GM's request, verbatim and unedited

This file is the authority for `spec.md`. Nothing here is paraphrased.

Session opened with `/rename Diagram tooling`, then:

---

I notice I've been seeing a lot of this in the output of my claude code sessions over time:

> Error: PreToolUse:Bash hook error: [/diagram/scripts/measure-hooks.sh pretool]: BLOCKED: that is the third EXPENSIVE measurement in a row with no engine change and no commit between.

Given how expensive that is, should we make it so we start blocking at 2 in a row instead of 3 in a row?  And possibly add some other automated checks as well?  Like should the output of the FIRST successful expensive measurement emit a reminder about this so that you don't need to wait until the first failure to get this reminder message about how you should make multiple changes or big changes before running this again rather than run it after every change, etc.  That might inform future sessions before they see the failure.

I also see a lot of comments like

> Error: PreToolUse:Bash hook error: [/diagram/scripts/gate-hooks.sh pretool]: BLOCKED: `make quick` and `make done` in ONE command. `quick` is a subset of `done` (~70 s with scope locked), so this re-runs ~30 s of the same tests for nothing (measured 2026-08-26: 3 times in one task, 1.5 min). Run `make quick` while iterating, `make done` ONCE when you think it is finished - never both. (GATE_OK with a reason if you truly need both.)

So does mean our tooling should detect when both are being run and then combine them into `make done` automatically instead of rejecting?  Also I think those numbers for `make quick` are wrong and outdated, though the attempt to get a savings is still worthwhile.  We could also have `make quick` save off its results so that if it succeeds and then `make done` runs immediately after it then `make done` just skips the quick tests instead of having to bounce this back, since bouncing back a command forces another pass through the LLM engine, which also takes time.
