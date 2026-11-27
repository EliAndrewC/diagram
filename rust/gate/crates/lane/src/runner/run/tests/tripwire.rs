//! THE TRIPWIRE BY TASK end to end (feature 461 T18, plan D6 step 4, D7's table): an ejected task's repair handed in red again in a
//! later batch stops the lane - no second repair, the arbiter asked with the two attempt files, one owed line; the task held off every
//! batch until the ruling, the rest of the lane's work landing meanwhile; the ruling's repair filed once (`why` `arbiter`); a third pin
//! asked again under a subject of its own, the stale ruling filing nothing for it.

use super::*;

/// The common directory's `asked` file: each ask's words line, then its WHY.
fn asked(w: &World) -> Vec<String> {
    std::fs::read_to_string(w.common.join("asked"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

/// The round arbiter's ruling on `trigger`, recorded where `make arbiter-ruled` run in the clone records it.
fn rule(w: &World, trigger: &str, ruling: &str, what: &str) {
    let row = json!({"trigger": trigger, "kind": "ask", "unit": "", "asked": "q", "ruling": ruling, "why": "w", "what": what});
    let file = w.clone.join("specs/461-x/arbiter.jsonl");
    let mut text = std::fs::read_to_string(&file).unwrap_or_default();
    let _ = writeln!(text, "{row}");
    std::fs::write(&file, text).unwrap();
}

/// T02's landing red in `lib/two` from now on: its Phase line WITH its newline, as the event log's writer ends every line, so the
/// batches' lines are each their own.
fn red(w: &World) {
    std::fs::write(w.common.join("phase-T02"), format!("{PHASE}\n")).unwrap();
}

fn attempt_of(lines: &[Value], batch: &str) -> String {
    lines
        .iter()
        .find(|x| x["event"] == "run" && x["batch"] == batch)
        .and_then(|x| x["attempt"].as_str())
        .unwrap()
        .to_owned()
}

/// T02 pinned twice: ejected red in batch 461-1 (repair r1), its repair handed in red again in batch 461-2; the world, the repair's
/// commit and the second step's error.
fn tripped(tag: &str) -> (World, String, String) {
    let w = world(tag);
    w.hand_in("461", "T02", "lib/two/x.rs", "x\n");
    red(&w);
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(repairs::read(&w.common).len(), 1);
    let again = w.hand_in("461", "T02", "lib/two/y.rs", "y\n");
    let err = step(&l).unwrap_err();
    (w, again, err)
}

#[test]
fn a_repair_handed_in_red_again_stops_the_lane_files_no_second_repair_and_owes_the_arbiter_one_line(
) {
    let (w, again, err) = tripped("lane-trip");
    let lines = w.lane();
    let before = lines
        .iter()
        .position(|x| x["event"] == "batch" && x["batch"] == "461-2")
        .unwrap();
    let new: Vec<&str> = lines[before..]
        .iter()
        .map(|x| x["event"].as_str().unwrap())
        .collect();
    assert_eq!(
        new,
        [
            "batch",
            "carry",
            "run",
            "attribute",
            "eject",
            "stop",
            "owed"
        ]
    );
    let (one, two) = (attempt_of(&lines, "461-1"), attempt_of(&lines, "461-2"));
    let eject = &lines[before + 4];
    assert_eq!(eject["change"], json!(again));
    assert_eq!(eject["repair"], Value::Null);
    assert_eq!(eject["why"], "red");
    assert_eq!(eject["arbiter"], "ask:lane-T02");
    assert_eq!(eject["attempt"], json!(two));
    let stop = &lines[before + 5];
    assert_eq!(stop["batch"], "461-2");
    assert_eq!(stop["why"], "arbiter");
    assert_eq!(stop["trigger"], "ask:lane-T02");
    assert_eq!(stop["spec"], "461-x");
    assert_eq!(stop["tasks"], json!(["T02"]));
    assert_eq!(stop["held"], json!([again]));
    assert_eq!(open_or_none(&w), None);
    // no second repair; the arbiter asked in the lane's tree, under the feature, with the two attempt files
    assert_eq!(repairs::read(&w.common).len(), 1);
    let said = asked(&w);
    assert_eq!(
        said[0],
        format!("SUBJECT=lane-T02 FILES={one} {two} spec=461-x dir=specs/461-x")
    );
    assert_eq!(
        said[1],
        "461 T02 was ejected red by the landing lane again (pin 2): batch 461-1, then batch 461-2 at attempt 1 (red: lib/two test). The lane filed no second repair. Rule: continue (the work its repair then does), accept, or a process fault."
    );
    // one owed line, the runner's own stop, which is the step's error
    let owed = &lines[before + 6];
    assert_eq!(owed["line"], err);
    assert_eq!(owed[crate::wake::STOPPED], true);
    assert_eq!(
        err,
        "lane: batch 461-2 stopped at attempt 1 - 461 T02 red again (red: lib/two test; pinned before in batch 461-1), no repair filed: the round arbiter is owed ask:lane-T02 - dispatch round-arbiter on /tmp/arbiter-lane-T02/MANIFEST.md; once make arbiter-ruled records its ruling, make lane-start files its repair (why arbiter)"
    );
}

#[test]
fn the_held_task_waits_on_its_ruling_whose_repair_is_filed_once_and_a_third_pin_asks_anew() {
    let (w, again, _) = tripped("lane-trip-ruled");
    let l = lane_of(&w);
    let two = attempt_of(&w.lane(), "461-2");
    // held off every batch until the ruling, the lane's other work landing meanwhile
    std::fs::remove_file(w.common.join("phase-T02")).unwrap();
    assert_eq!(step(&l), Ok(false));
    w.hand_in("461", "T01", "a.txt", "a\n");
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.lane().last().unwrap()["line"],
        "lane: batch 461-3 landed - 461 T01 (1 change(s), 1 run(s), 0 minutes)"
    );
    // a ruling on another trigger files nothing
    rule(&w, "ask:lane-T09", "continue", "x");
    let before = w.lane().len();
    assert_eq!(step(&l), Ok(false));
    assert_eq!(w.lane().len(), before);
    // the ruling recorded: its repair filed once, why arbiter, the attempt naming the ruling
    rule(&w, "ask:lane-T02", "continue", "fix the test");
    assert_eq!(step(&l), Ok(true));
    let lines = w.lane();
    let new: Vec<&str> = lines[before..]
        .iter()
        .map(|x| x["event"].as_str().unwrap())
        .collect();
    assert_eq!(new, ["eject", "owed"]);
    assert_eq!(lines[before]["change"], json!(again));
    assert_eq!(lines[before]["repair"], "r2");
    assert_eq!(lines[before]["why"], "arbiter");
    assert_eq!(lines[before]["of_batch"], "461-2");
    assert_eq!(lines[before]["batch"], Value::Null);
    assert_eq!(
        lines[before + 1]["line"],
        "lane: the round arbiter ruled ask:lane-T02 continue - 461 T02 of batch 461-2 filed as repair r2 (arbiter: continue: fix the test) - make builder-next hands it to a fresh builder"
    );
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 2);
    let mut entry = entries[1].clone();
    entry.as_object_mut().unwrap().remove("utc");
    assert_eq!(
        entry,
        json!({"repair": "r2", "feature": "461-x", "tasks": ["T02"], "kind": "fix", "ejected": [again], "batch": "461-2",
            "why": "arbiter", "units": ["continue: fix the test"], "attempt": "ask:lane-T02"})
    );
    assert_eq!(log::repairs_open(&lines, &[]), ["r1", "r2"]);
    // filed once: the next step writes nothing
    let before = w.lane().len();
    assert_eq!(step(&l), Ok(false));
    assert_eq!(w.lane().len(), before);
    // the ruling's repair handed in red again: a third pin, asked under a subject of its own; the stale ruling files nothing for it
    red(&w);
    let third = w.hand_in("461", "T02", "lib/two/z.rs", "z\n");
    let err = step(&l).unwrap_err();
    assert!(
        err.contains("the round arbiter is owed ask:lane-T02-3 - "),
        "{err}"
    );
    let lines = w.lane();
    let four = attempt_of(&lines, "461-4");
    assert_eq!(
        asked(&w)[2],
        format!("SUBJECT=lane-T02-3 FILES={two} {four} spec=461-x dir=specs/461-x")
    );
    let stop = lines.iter().rev().find(|x| x["event"] == "stop").unwrap();
    assert_eq!(stop["held"], json!([third]));
    let before = w.lane().len();
    assert_eq!(step(&l), Ok(false));
    assert_eq!(w.lane().len(), before);
    assert_eq!(repairs::read(&w.common).len(), 2);
}

#[test]
fn an_ask_the_arbiter_refuses_still_stops_the_batch_and_its_line_names_the_ask_to_run_by_hand() {
    let w = world("lane-trip-ask-fails");
    w.hand_in("461", "T02", "lib/two/x.rs", "x\n");
    red(&w);
    std::fs::write(w.common.join("ask-fails"), "").unwrap();
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    w.hand_in("461", "T02", "lib/two/y.rs", "y\n");
    let err = step(&l).unwrap_err();
    let lines = w.lane();
    let (one, two) = (attempt_of(&lines, "461-1"), attempt_of(&lines, "461-2"));
    assert_eq!(
        err,
        format!("lane: batch 461-2 stopped at attempt 1 - 461 T02 red again (red: lib/two test; pinned before in batch 461-1), no repair filed: the round arbiter is owed ask:lane-T02 - make arbiter-ask SUBJECT=lane-T02 FILES=\"{one} {two}\" failed (exit 2: refused), its output {two}.arbiter.log: ask it by hand, then dispatch round-arbiter on its bundle; once make arbiter-ruled records its ruling, make lane-start files its repair (why arbiter)")
    );
    assert_eq!(
        lines.iter().rev().find(|x| x["event"] == "stop").unwrap()["trigger"],
        "ask:lane-T02"
    );
    assert_eq!(repairs::read(&w.common).len(), 1);
}

#[test]
fn an_ask_that_cannot_start_is_exit_minus_one_its_error_the_stderr() {
    let gone = std::process::Command::new("/nonexistent/l7r-no-such-make").output();
    let (code, out, err) = super::super::outcome(gone);
    assert_eq!((code, out.as_str()), (-1, ""));
    assert!(!err.is_empty());
}

/// The open batch, where one is.
fn open_or_none(w: &World) -> Option<String> {
    log::batches(&w.lane())
        .pop()
        .filter(Batch::open)
        .map(|b| b.id)
}
