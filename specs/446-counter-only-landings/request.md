# Request - lighter landings for counter-only changes (feature 446)

<!-- SOURCE: GM NOTES -->
## The GM's words, verbatim (dictated), 2026-10-28

"If the day's main cost has been process overhead, then we should ask whether we actually need that overhead for the work that we are currently doing. Like, is there a way to temporarily remove some of that overhead that we think doesn't matter during the transition to Rust, and then turn it back on once it will be once again relevant? like a 5-minute landing right now seems like it is too long given that what we are doing is landing experimental changes that are not yet finalized, you know? most of those procedures are to the fidelity of things that are already well established to be working as we want them.     things, then it seems like disabling a lot of that process is probably okay. Whereas the types of process that we very much want are the checklists and the things that exist around making sure that our transition to Rust is good, and our spec fidelity reviews, and making sure that our tasks are completed as they should be, etc. What do you think?"

"I realize it's possible that these processes might be more valuable than ever now, instead of less valuable!  That's why I'm asking - I'm genuinely not sure."

"Yes, those two changes seem good. So please make them. Thank you."

"And then they should probably be prioritized after you're done with whatever you're in the middle of, so that future things can be faster right away."
<!-- END SOURCE -->

## The two changes he accepted (the session's answer, 2026-10-28)

1. Skip the 48-seed landing cohort and the fresh 48-seed block after the push when a landing provably moves no map - the proof
   mechanical, never a judgment. Any landing that moves a map, every 444 rebuild among them, keeps both.
2. Clear counter-only hunks in the claims triage mechanically: on top of claims at `report` (an owed claim still refuses), a claim
   owed only because its code gained `if __debug__:` counter lines is cleared without an agent dispatch.

Kept unchanged: the full suite on every engine landing (it caught two real defects on 2026-10-28), spec fidelity, the part-A
checklists and tick rules, escalation-check, the round arbiter, 444's phase checklist and budget review, a rebuilt phase's claims
round.
