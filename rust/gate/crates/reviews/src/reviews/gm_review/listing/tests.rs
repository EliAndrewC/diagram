//! The listing and the explanation on a scratch queue, each expected text HEAD's `scripts/gm_review.py` printed on the same files at the
//! same width (written by `scratchpad/t91/gen_listing_tests.py`, feature 449 T91), so these pin the Python's bytes; the differential
//! (`scratchpad/t91/diff.py`) holds the real queues and the rest.

use std::path::PathBuf;

use l7r_guard::shared::tempdir::Held;

use super::super::super::tests::{dir, put};
use super::super::tests::run_with;

/// The scratch queue: every kind of row, trigger and fix, a kept question, 328's ranking with a closed row.
fn queue(name: &str) -> Held<PathBuf> {
    let d = dir(&format!("gm-listing-{}", &name[..name.len().min(12)]));
    put(
        &d,
        ".claude/agents/modal-form.md",
        "---\ndescription: Judges a map modal's FORM - run on the modals.\n---\n",
    );
    put(
        &d,
        ".claude/agents/plain.md",
        "---\ndescription:\n  wrapped onto its own line.\n---\n",
    );
    put(&d, ".claude/agents/nodesc.md", "---\nname: x\n---\n");
    put(&d, "research/questions/0094-plows.html", "x");
    put(&d, "research/questions/0094-plows.notes.html", "x");
    put(&d, "specs/500-arbiter-rows/gm-review.jsonl", "{\"trigger\": \"round:modal-form|modal:sheet/kitchen@3\", \"kind\": \"arbiter\", \"ruling\": \"accept\", \"why\": \"a reason that runs past one line - well-known-and-loved, re-read, a/long/path/with/no/spaces/at/all/to/break and\\ttabs.\", \"utc\": \"2026-10-01T10:00:00Z\"}\n{\"trigger\": \"round:modal-form|modal:sheet/hall@4\", \"kind\": \"arbiter\", \"ruling\": \"accept\", \"why\": \"a reason that runs past one line - well-known-and-loved, re-read, a/long/path/with/no/spaces/at/all/to/break and\\ttabs.\", \"utc\": \"2026-10-01T10:01:00Z\"}\n{\"trigger\": \"round:plain|q:0094@3\", \"kind\": \"arbiter\", \"ruling\": \"continue\", \"why\": \"short why\", \"utc\": \"2026-10-01T11:00:00Z\", \"asked\": \"the ask\"}\n{\"trigger\": \"round:nodesc|q:0096\", \"kind\": \"arbiter\", \"ruling\": \"process-fault\", \"why\": \"w\", \"tooling_fix\": \"fix the hook\", \"utc\": \"2026-10-02T00:00:00Z\"}\n{\"trigger\": \"round:missing|modal:a/b\", \"kind\": \"arbiter\", \"ruling\": \"odd\", \"utc\": \"2026-10-02T01:00:00Z\"}\n{\"trigger\": \"red-gate@2026-10-03T00:00:00Z\", \"kind\": \"arbiter\", \"ruling\": \"continue\", \"why\": \"w\", \"utc\": \"2026-10-03T00:00:00Z\"}\n{\"trigger\": \"reversal:/diagram/.clones/sess/l7r/diagram/x.py\", \"kind\": \"arbiter\", \"ruling\": \"continue\", \"utc\": \"2026-10-03T01:00:00Z\"}\n{\"trigger\": \"reversal:x.md\", \"kind\": \"arbiter\", \"ruling\": \"accept\", \"utc\": \"2026-10-03T02:00:00Z\"}\n{\"trigger\": \"cascade:500\", \"kind\": \"arbiter\", \"ruling\": null, \"utc\": \"2026-10-03T03:00:00Z\"}\n{\"trigger\": \"ask:500-thing\", \"kind\": \"arbiter\", \"ruling\": \"continue\", \"why\": \"asked\", \"utc\": \"2026-10-03T04:00:00Z\"}\n{\"trigger\": \"weird trigger\", \"kind\": \"arbiter\", \"ruling\": \"accept\"}\n{\"trigger\": \"ask:500-thing\", \"kind\": \"arbiter-fix-done\", \"tooling_fix\": \"the fix\", \"note\": \"made it\", \"test\": \"tests/x.sh\", \"utc\": \"2026-10-04T00:00:00Z\"}\n{\"trigger\": \"ask:500-thing\", \"kind\": \"arbiter-fix-declined\", \"tooling_fix\": \"another fix\", \"note\": \"declined it\", \"utc\": \"2026-10-04T01:00:00Z\"}\n{\"trigger\": \"ask:500-orphan\", \"kind\": \"arbiter-fix-declined\", \"tooling_fix\": \"a reason that runs past one line - well-known-and-loved, re-read, a/long/path/with/no/spaces/at/all/to/break and\\ttabs.\", \"note\": \"\", \"utc\": \"2026-10-04T02:00:00Z\"}\n{\"trigger\": \"\", \"kind\": \"arbiter-fix-done\", \"tooling_fix\": null, \"note\": \"n\", \"test\": 0, \"utc\": \"2026-10-04T03:00:00Z\"}\n{\"kind\": \"accepted\", \"finding\": \"a finding\", \"why\": \"its reason here\", \"utc\": \"2026-10-05T00:00:00Z\"}\n{\"kind\": \"accepted\", \"finding\": null, \"why\": null, \"utc\": \"2026-10-05T00:00:01Z\"}\n{\"kind\": \"known-drift\", \"claim\": \"x.rs::y#z\", \"task\": \"T01\", \"finding\": \"drift\", \"utc\": \"2026-10-06T00:00:00Z\"}\n{\"kind\": \"question\", \"status\": \"owed\", \"question\": \"Should the owed question be answered?\", \"utc\": \"2026-10-07T00:00:00Z\"}\n{\"kind\": \"question\", \"status\": \"kept\", \"question\": \"Is the kept question very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long?\", \"escalation\": \"it is his\", \"utc\": \"2026-10-07T00:00:01Z\"}\n{\"kind\": \"arbiter\", \"ruling\": \"accept\", \"why\": \"reviewed already\", \"reviewed\": \"2026-10-08\"}\n{\"kind\": \"unknown-kind\", \"ruling\": \"accept\", \"why\": \"an unknown kind\"}\n{\"ruling\": \"continue\", \"why\": \"no kind at all\"}\n");
    put(&d, "specs/500-arbiter-rows/arbiter.jsonl", "{\"trigger\": \"round:plain|q:0094@3\", \"utc\": \"2026-10-01T11:00:00Z\", \"what\": \"an older record\"}\n{\"trigger\": \"round:plain|q:0094@3\", \"utc\": \"2026-10-01T11:00:00Z\", \"what\": \"from the arbiter's own record\"}\n{}\nbad\n");
    put(&d, "specs/501-questions/gm-review.jsonl", "{\"kind\": \"question\", \"status\": \"kept\", \"question\": \"What does the kept question decide?\", \"escalation\": \"his\"}\n");
    put(
        &d,
        "specs/502-accepted/gm-review.jsonl",
        "{\"kind\": \"accepted\", \"finding\": \"f\", \"why\": \"two words\"}\n",
    );
    put(&d, "specs/503-reviewed/gm-review.jsonl", "{\"kind\": \"accepted\", \"finding\": \"f\", \"why\": \"two words\", \"reviewed\": \"x\"}\n");
    put(&d, "specs/328-match-the-research/audit/overrides.json", "{\"b-row\": {\"flag\": \"Held behind #12 - the tubs long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long \", \"fix\": \"build it\"}, \"a-row\": {\"flag\": \"Held behind: a-thing\"}, \"c-row\": {\"flag\": \"Held for the GM\"}, \"d-row\": {\"flag\": \"Held behind, closed\"}}");
    put(
        &d,
        "specs/328-match-the-research/audit/waves.json",
        "{\"d-row\": 115}",
    );
    d
}

#[test]
fn the_whole_queue() {
    let d = queue("the_whole_queue");
    let got = run_with(&d, &["list"], "", 100, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "GM REVIEW - 2 decision(s) for the GM, 1 question(s) owed escalation-check, 2 waiting on other work, 21 landed row(s) to review in 2 feature(s)\n\nNEEDS YOUR DECISION - the questions escalation-check kept (feature 432)\n  * 500#19: Is the kept question very very very very very very very very very very very very very...\n  * 501#0: What does the kept question decide?\n\nOWED ESCALATION-CHECK - the session's, not the GM's: judge each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"\n  * 500#18: Should the owed question be answered?\n\nWAITING ON OTHER WORK - held in the ranking behind another row, not on the GM\n  * a-row\n      waits on a-thing\n  * b-row\n      waits on #12 - the tubs long long long long long long long long long long long long long lo...\n\nTO REVIEW - landed; the GM may overturn any row\n  500  arbiter-rows                              20  11 rulings (4 continue, 1 process-fault, 1 o...\n  502  accepted                                   1  1 accepted\n\n  needs a decision: 2 question(s), 2 fix(es) declined to the GM - in full: make gm-review EXPLAIN=1\n  a feature's rows:  make gm-review F=NNN   (each in full: add EXPLAIN=1, one row: ROW=n)\n  reviewed:          make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS=\"<his words>\")\n");
}

#[test]
fn the_whole_queue_narrow() {
    let d = queue("the_whole_queue_narrow");
    let got = run_with(&d, &["list"], "", 30, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "GM REVIEW - 2 decision(s) for the GM, 1 question(s) owed escalation-check, 2 waiting on other work, 21 landed row(s) to review in 2 feature(s)\n\nNEEDS YOUR DECISION - the questions escalation-check kept (feature 432)\n  * 500#19: Is the kept question very very very very very very very very very...\n  * 501#0: What does the kept question decide?\n\nOWED ESCALATION-CHECK - the session's, not the GM's: judge each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"\n  * 500#18: Should the owed question be answered?\n\nWAITING ON OTHER WORK - held in the ranking behind another row, not on the GM\n  * a-row\n      waits on a-thing\n  * b-row\n      waits on #12 - the tubs long long long long long long long long long lo...\n\nTO REVIEW - landed; the GM may overturn any row\n  500  arbiter-rows                              20  11 rulings (4 continue,...\n  502  accepted                                   1  1 accepted\n\n  needs a decision: 2 question(s), 2 fix(es) declined to the GM - in full: make gm-review EXPLAIN=1\n  a feature's rows:  make gm-review F=NNN   (each in full: add EXPLAIN=1, one row: ROW=n)\n  reviewed:          make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS=\"<his words>\")\n");
}

#[test]
fn one_features_rows() {
    let d = queue("one_features_rows");
    let got = run_with(&d, &["list", "500"], "", 100, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "500-arbiter-rows: 22 row(s) - 11 rulings (4 continue, 1 process-fault, 1 odd, 1 None), 2 accepted, 2 fixes made, 2 fixes DECLINED, 1 known drifts, 1 , 2 question, 1 unknown-kind\n\n  arbiter rulings\n    [0-1] accept: modal-form sheet/hall; modal-form sheet/kitchen\n        a reason that runs past one line - well-known-and-loved, re-read, a/long/path/with/no/spa...\n    [2] continue: plain 0094\n        short why\n    [3] process-fault: nodesc 0096\n        w\n    [4] odd: missing a/b\n    [5] continue: red-gate 2026-10-03T00:00:00Z\n        w\n    [6] continue: reversal x.py\n    [7,10] accept: reversal x.md; weird trigger\n    [8] cascade 500\n    [9] continue: ask 500-thing\n        asked\n\n  findings accepted with a reason\n    [15] a finding\n        its reason here\n    [16] None\n\n  tooling fixes the arbiter asked for, made\n    [11] ask 500-thing\n        the fix\n    [14] \n\n  tooling fixes the arbiter asked for, declined to the GM\n    [12] ask 500-thing\n        another fix\n    [13] ask 500-orphan\n        a reason that runs past one line - well-known-and-loved, re-read, a/long/path/with/no/spa...\n\n  known drifts landed on their open fixing task (feature 430)\n    [17] drift\n\n  \n    [22] continue: \n        no kind at all\n\n  question\n    [18-19] \n\n  unknown-kind\n    [21] accept: \n        an unknown kind\n\n  reviewed:     make gm-reviewed F=500\n  overturn one: make gm-reviewed F=500 OVERTURN=<row> TO=<feature>\n");
}

#[test]
fn nothing_of_a_reviewed_feature() {
    let d = queue("nothing_of_a_reviewed_feature");
    let got = run_with(&d, &["list", "503"], "", 100, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(
        got.stdout,
        "gm-review: nothing of 503-reviewed waits on the GM\n"
    );
}

#[test]
fn what_needs_the_gm() {
    let d = queue("what_needs_the_gm");
    let got = run_with(&d, &["explain"], "", 100, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "WHAT NEEDS YOUR DECISION\n\n1. QUESTION 500#19 (500-arbiter-rows)\n    Is the kept question very very very very very very very very very very very very very very very\n      very very very very very very very very very very very very very very very long?\n    Why it is yours (escalation-check): it is his\n    Answered: make gm-reviewed F=500 ROW=19 WORDS=\"<your answer>\"\n\n2. QUESTION 501#0 (501-questions)\n    What does the kept question decide?\n    Why it is yours (escalation-check): his\n    Answered: make gm-reviewed F=501 ROW=0 WORDS=\"<your answer>\"\n\n3. A TOOLING FIX DECLINED TO YOU: feature 500 row [12], ask 500-thing\n    The arbiter asked: another fix\n    Declined because: declined it\n    Decide: leave it declined (make gm-reviewed F=500) or have it built (make gm-reviewed F=500\n      OVERTURN=12 TO=<an open feature>).\n\n4. A TOOLING FIX DECLINED TO YOU: feature 500 row [13], ask 500-orphan\n    The arbiter asked: a reason that runs past one line - well-known-and-loved, re-read,\n      a/long/path/with/no/spaces/at/all/to/break and     tabs.\n    Decide: leave it declined (make gm-reviewed F=500) or have it built (make gm-reviewed F=500\n      OVERTURN=13 TO=<an open feature>).\n\nWAITING ON OTHER WORK - held in the ranking until another row is done; nothing for you to decide\n\n  * a-row\n    Waits on : a-thing\n\n  * b-row\n    Waits on #12 - the tubs long long long long long long long long long long long long long long\n      long long long long long long long long long long long long long long long long long long long\n      long long long long long long long . The fix it would make: build it.\n\nThe other 19 row(s) are decisions already made that you may overturn; nothing waits on them. Each in\nfull: make gm-review F=NNN EXPLAIN=1 [ROW=n].\n");
}

#[test]
fn each_row_in_full() {
    let d = queue("each_row_in_full");
    let got = run_with(&d, &["explain", "500"], "", 90, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "500-arbiter-rows: 22 row(s) - 11 rulings (4 continue, 1 process-fault, 1 odd, 1 None), 2\n  accepted, 2 fixes made, 2 fixes DECLINED, 1 known drifts, 1 , 2 question, 1 unknown-kind\n\n[0] modal-form sheet/kitchen - 2026-10-01 10:00 UTC\n    What happened: The modal-form check (judges a map modal's FORM) was owed a round 3 on\n      sheet/kitchen. Three rounds on one thing can mean a loop, so the round arbiter rules\n      before the third runs.\n    Where: l7r/diagram/interactive/assets/modals/sheet/kitchen.md\n    The arbiter ruled: ACCEPT - stop checking; the work stands as it is now and this check\n      runs no further round on it\n    Why: a reason that runs past one line - well-known-and-loved, re-read,\n      a/long/path/with/no/spaces/at/all/to/break and   tabs.\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=0\n      TO=<an open feature> (it becomes open work there).\n\n[1] modal-form sheet/hall - 2026-10-01 10:01 UTC\n    What happened: The modal-form check (judges a map modal's FORM) was owed a round 4 on\n      sheet/hall. Three rounds on one thing can mean a loop, so the round arbiter rules\n      before the third runs.\n    Where: l7r/diagram/interactive/assets/modals/sheet/hall.md\n    The arbiter ruled: ACCEPT - stop checking; the work stands as it is now and this check\n      runs no further round on it\n    Why: a reason that runs past one line - well-known-and-loved, re-read,\n      a/long/path/with/no/spaces/at/all/to/break and   tabs.\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=1\n      TO=<an open feature> (it becomes open work there).\n\n[2] plain 0094 - 2026-10-01 11:00 UTC\n    What happened: The plain check (wrapped onto its own line) was owed a round 3 on 0094.\n      Three rounds on one thing can mean a loop, so the round arbiter rules before the\n      third runs. As it fired: the ask\n    Where: research/questions/0094-plows.html\n    The arbiter ruled: CONTINUE - allow one more round of the check\n    Why: short why\n    It set the next step: from the arbiter's own record\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=2\n      TO=<an open feature> (it becomes open work there).\n\n[3] nodesc 0096 - 2026-10-02 00:00 UTC\n    What happened: The nodesc check was owed a round 3 on 0096. Three rounds on one thing\n      can mean a loop, so the round arbiter rules before the third runs.\n    The arbiter ruled: PROCESS FAULT - the tooling, not the work, was at fault; the fix\n      below is what it asks for\n    Why: w\n    It asked for a tooling fix: fix the hook\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=3\n      TO=<an open feature> (it becomes open work there).\n\n[4] missing a/b - 2026-10-02 01:00 UTC\n    What happened: The missing check was owed a round 3 on a/b. Three rounds on one thing\n      can mean a loop, so the round arbiter rules before the third runs.\n    Where: l7r/diagram/interactive/assets/modals/a/b.md\n    The arbiter ruled: odd\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=4\n      TO=<an open feature> (it becomes open work there).\n\n[5] red-gate 2026-10-03T00:00:00Z - 2026-10-03 00:00 UTC\n    What happened: `make done` went red twice in a row: the arbiter rules on whether the\n      session is stuck.\n    The arbiter ruled: CONTINUE - nothing is stuck; the work carries on as it was\n    Why: w\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=5\n      TO=<an open feature> (it becomes open work there).\n\n[6] reversal x.py - 2026-10-03 01:00 UTC\n    What happened: An edit put back text that an earlier edit of the same file in this\n      feature had replaced (A -> B -> A): checks may be pulling the text two ways.\n    Where: l7r/diagram/x.py\n    The arbiter ruled: CONTINUE - nothing is stuck; the work carries on as it was\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=6\n      TO=<an open feature> (it becomes open work there).\n\n[7] reversal x.md - 2026-10-03 02:00 UTC\n    What happened: An edit put back text that an earlier edit of the same file in this\n      feature had replaced (A -> B -> A): checks may be pulling the text two ways.\n    Where: x.md\n    The arbiter ruled: ACCEPT - stop checking; the work stands as it is now and this check\n      runs no further round on it\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=7\n      TO=<an open feature> (it becomes open work there).\n\n[8] cascade 500 - 2026-10-03 03:00 UTC\n    What happened: Checks were dispatched faster than one per changed line: reviews may be\n      triggering reviews.\n    The arbiter ruled: None\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=8\n      TO=<an open feature> (it becomes open work there).\n\n[9] ask 500-thing - 2026-10-03 04:00 UTC\n    What happened: The session put a process question to the round arbiter instead of to\n      the GM.\n    The arbiter ruled: CONTINUE - nothing is stuck; the work carries on as it was\n    Why: asked\n    [11] the tooling fix: DONE\n    Done: made it\n    Test: tests/x.sh\n    [12] the tooling fix: DECLINED\n    Declined because: declined it\n    YOUR DECISION: should this fix be made after all? Mark it reviewed (make gm-reviewed\n      F=500) to leave it declined, or OVERTURN=12 TO=<an open feature> to have it built.\n\n[10]  weird trigger -  UTC\n    What happened: Trigger weird trigger.\n    The arbiter ruled: ACCEPT - stop checking; the work stands as it is now and this check\n      runs no further round on it\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=10\n      TO=<an open feature> (it becomes open work there).\n\n[15]  a finding - 2026-10-05 00:00 UTC\n    A session accepted this finding without fixing it: a finding\n    Its reason: its reason here\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=15\n      TO=<an open feature> (it becomes open work there).\n\n[16]  None - 2026-10-05 00:00 UTC\n    A session accepted this finding without fixing it: None\n    Its reason: None\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=16\n      TO=<an open feature> (it becomes open work there).\n\n[17]  drift - 2026-10-06 00:00 UTC\n    What happened: Trigger .\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=17\n      TO=<an open feature> (it becomes open work there).\n\n[18] - 2026-10-07 00:00 UTC\n    What happened: Trigger .\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=18\n      TO=<an open feature> (it becomes open work there).\n\n[19] - 2026-10-07 00:00 UTC\n    What happened: Trigger .\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=19\n      TO=<an open feature> (it becomes open work there).\n\n[21] -  UTC\n    What happened: Trigger .\n    The arbiter ruled: ACCEPT - stop checking; the work stands as it is now and this check\n      runs no further round on it\n    Why: an unknown kind\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=21\n      TO=<an open feature> (it becomes open work there).\n\n[22] -  UTC\n    What happened: Trigger .\n    The arbiter ruled: CONTINUE - nothing is stuck; the work carries on as it was\n    Why: no kind at all\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=500 OVERTURN=22\n      TO=<an open feature> (it becomes open work there).\n\n[13] ask 500-orphan\n    The fix asked for: a reason that runs past one line - well-known-and-loved, re-read,\n      a/long/path/with/no/spaces/at/all/to/break and     tabs.\n    [13] the tooling fix: DECLINED\n    YOUR DECISION: should this fix be made after all? Mark it reviewed (make gm-reviewed\n      F=500) to leave it declined, or OVERTURN=13 TO=<an open feature> to have it built.\n\n[14] \n    [14] the tooling fix: DONE\n    Done: n\n\n");
}

#[test]
fn one_row_with_its_fix() {
    let d = queue("one_row_with_its_fix");
    let got = run_with(&d, &["explain", "500", "12"], "", 90, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "500-arbiter-rows: 22 row(s) - 11 rulings (4 continue, 1 process-fault, 1 odd, 1 None), 2\n  accepted, 2 fixes made, 2 fixes DECLINED, 1 known drifts, 1 , 2 question, 1 unknown-kind\n\n[9] ask 500-thing - 2026-10-03 04:00 UTC\n    What happened: The session put a process question to the round arbiter instead of to\n      the GM.\n    The arbiter ruled: CONTINUE - nothing is stuck; the work carries on as it was\n    Why: asked\n    [11] the tooling fix: DONE\n    Done: made it\n    Test: tests/x.sh\n    [12] the tooling fix: DECLINED\n    Declined because: declined it\n    YOUR DECISION: should this fix be made after all? Mark it reviewed (make gm-reviewed\n      F=500) to leave it declined, or OVERTURN=12 TO=<an open feature> to have it built.\n\n");
}

#[test]
fn one_orphan_fix() {
    let d = queue("one_orphan_fix");
    let got = run_with(&d, &["explain", "500", "13"], "", 90, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "500-arbiter-rows: 22 row(s) - 11 rulings (4 continue, 1 process-fault, 1 odd, 1 None), 2\n  accepted, 2 fixes made, 2 fixes DECLINED, 1 known drifts, 1 , 2 question, 1 unknown-kind\n\n[13] ask 500-orphan\n    The fix asked for: a reason that runs past one line - well-known-and-loved, re-read,\n      a/long/path/with/no/spaces/at/all/to/break and     tabs.\n    [13] the tooling fix: DECLINED\n    YOUR DECISION: should this fix be made after all? Mark it reviewed (make gm-reviewed\n      F=500) to leave it declined, or OVERTURN=13 TO=<an open feature> to have it built.\n\n");
}

#[test]
fn no_such_row() {
    let d = queue("no_such_row");
    let got = run_with(&d, &["explain", "500", "77"], "", 90, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(
        got.stdout,
        "gm-review: no open row 77 in 500-arbiter-rows\n"
    );
}

#[test]
fn nothing_to_explain() {
    let d = queue("nothing_to_explain");
    let got = run_with(&d, &["explain", "503"], "", 90, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(
        got.stdout,
        "gm-review: nothing of 503-reviewed waits on the GM\n"
    );
}

#[test]
fn a_kept_question_in_full() {
    let d = queue("a_kept_question_in_full");
    let got = run_with(&d, &["explain", "501"], "", 200, "python3");
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    assert_eq!(got.stdout, "501-questions: 1 row(s) - 1 question\n\n[0] -  UTC\n    What happened: Trigger .\n    Your call: nothing to do if you agree. To overturn: make gm-reviewed F=501 OVERTURN=0 TO=<an open feature>\n      (it becomes open work there).\n\n");
}
