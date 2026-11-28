//! THE HALVING end to end (feature 461 T24, plan D6 steps 3 and 5 and its table): a red the gate's record cannot place is halved
//! over the batch in hand-in order, each green half pushed at once, a red half halved again, the change left last after every other
//! landed ejected without a run of its own (`inferred`), one ejected after its own one-change red run `red`. n = 4 and n = 6 with the
//! bad change in each half land the good ones within ceil(log2 n) + 1 further runs; the tripwire by task stays quiet through the
//! n = 6 halving whose bad change is C and fires when a task left last by one halving is left last again by a later batch's.

use super::*;

/// A red no change's delta touches (the crate `lib/none`): the record cannot place it, so the batch is halved.
const UNPLACED: &str = r#"{"ev":"Phase","src":"rust","step":"test","t0":"@T@","t1":"@T@","code":101,"clone":"@TREE@","crates":["lib/none"]}"#;

/// `task`'s landing red from now on, wherever it runs, as a red the record cannot place.
fn bad(w: &World, task: &str) {
    std::fs::write(
        w.common.join(format!("phase-{task}")),
        format!("{UNPLACED}\n"),
    )
    .unwrap();
}

/// One hand-in a task of `tasks`, each its own file, in that order; their commits.
fn hand_ins(w: &World, tasks: &[&str]) -> Vec<String> {
    tasks
        .iter()
        .map(|t| w.hand_in("461", t, &format!("f/{t}.txt"), &format!("{t}\n")))
        .collect()
}

/// Each `run` line of batch `b`'s set, as its tasks (`shas` and `tasks` side by side), in the order run.
fn sets(w: &World, b: &str, shas: &[String], tasks: &[&str]) -> Vec<String> {
    w.lane()
        .iter()
        .filter(|x| x["event"] == "run" && x["batch"] == b)
        .map(|x| {
            let set: Vec<&str> = x["set"]
                .as_array()
                .unwrap()
                .iter()
                .map(|s| {
                    let s = s.as_str().unwrap();
                    tasks[shas.iter().position(|c| c.starts_with(s)).unwrap()]
                })
                .collect();
            set.join(" ")
        })
        .collect()
}

/// Batch `b`'s `eject` lines: each change's task and `why`.
fn ejects(w: &World, b: &str, shas: &[String], tasks: &[&str]) -> Vec<(String, String)> {
    w.lane()
        .iter()
        .filter(|x| x["event"] == "eject" && x["batch"] == b)
        .map(|x| {
            let c = x["change"].as_str().unwrap();
            let i = shas.iter().position(|s| s == c).unwrap();
            (tasks[i].to_owned(), x["why"].as_str().unwrap().to_owned())
        })
        .collect()
}

/// US4's bound on the runs after the batch's first red run.
fn bound(n: u32) -> usize {
    (n.next_power_of_two().trailing_zeros() + 1) as usize
}

/// A batch of `tasks` whose change `culprit` alone is red, run: the sets its runs took and its ejections.
fn halved(tag: &str, tasks: &[&str], culprit: &str) -> (World, Vec<String>, Vec<(String, String)>) {
    let w = world(tag);
    let shas = hand_ins(&w, tasks);
    bad(&w, culprit);
    assert_eq!(step(&lane_of(&w)), Ok(true));
    let (runs, out) = (
        sets(&w, "461-1", &shas, tasks),
        ejects(&w, "461-1", &shas, tasks),
    );
    for (t, sha) in tasks.iter().zip(&shas) {
        let landed = w.lane().iter().any(|x| {
            x["event"] == "landed" && x["landed"].as_array().unwrap().contains(&json!(sha))
        });
        assert_eq!(landed, *t != culprit, "{t}: {runs:?}");
    }
    (w, runs, out)
}

#[test]
fn n_4_with_the_bad_change_in_either_half_lands_the_good_ones_within_the_bound() {
    let tasks = ["T01", "T02", "T03", "T04"];
    let (w, runs, out) = halved("lane-halve-4-first", &tasks, "T02");
    assert_eq!(
        runs,
        ["T01 T02 T03 T04", "T01 T02", "T01", "T03 T04"],
        "D6's table: [A B] red, [A] green, [C D] green; B ejected"
    );
    assert!(runs.len() - 1 <= bound(4));
    assert_eq!(out, [("T02".to_owned(), "inferred".to_owned())]);
    assert_eq!(w.origin_holds("f/T04.txt"), "T04");
    let entries = repairs::read(&w.common);
    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0]["why"], "inferred");
    assert_eq!(entries[0]["tasks"], json!(["T02"]));
    // the inference rests on the red half [A B], the batch's second attempt
    assert!(entries[0]["attempt"]
        .as_str()
        .unwrap()
        .ends_with("461-1-2.log"));
    let (_, runs, out) = halved("lane-halve-4-second", &tasks, "T04");
    assert_eq!(runs, ["T01 T02 T03 T04", "T01 T02", "T03"]);
    assert!(runs.len() - 1 <= bound(4));
    assert_eq!(out, [("T04".to_owned(), "inferred".to_owned())]);
    // the bad change's sibling run first and red: it is ejected after its own one-change run, the other runs on
    let (_, runs, out) = halved("lane-halve-4-third", &tasks, "T03");
    assert_eq!(runs, ["T01 T02 T03 T04", "T01 T02", "T03", "T04"]);
    assert!(runs.len() - 1 <= bound(4));
    assert_eq!(out, [("T03".to_owned(), "red".to_owned())]);
}

#[test]
fn n_6_with_the_bad_change_in_either_half_lands_the_good_ones_and_the_tripwire_stays_quiet() {
    let tasks = ["T01", "T02", "T03", "T04", "T05", "T06"];
    let (w, runs, out) = halved("lane-halve-6-first", &tasks, "T03");
    assert_eq!(
        runs,
        [
            "T01 T02 T03 T04 T05 T06",
            "T01 T02 T03",
            "T01",
            "T02",
            "T04 T05 T06"
        ],
        "D6's table: [A B C] red, [A] green, [B] green, [D E F] green; C ejected"
    );
    assert!(runs.len() - 1 <= bound(6));
    assert_eq!(out, [("T03".to_owned(), "inferred".to_owned())]);
    // two reds in a row that pin no task: no stop, no ask, one repair
    assert!(!w.events().contains(&"stop".to_owned()));
    assert!(!w.common.join("asked").exists());
    assert_eq!(repairs::read(&w.common).len(), 1);
    let (_, runs, out) = halved("lane-halve-6-second", &tasks, "T06");
    assert_eq!(
        runs,
        ["T01 T02 T03 T04 T05 T06", "T01 T02 T03", "T04", "T05"]
    );
    assert!(runs.len() - 1 <= bound(6));
    assert_eq!(out, [("T06".to_owned(), "inferred".to_owned())]);
}

#[test]
fn a_task_left_last_by_one_halving_and_again_by_a_later_batch_s_stops_the_lane_for_the_arbiter() {
    let tasks = ["T01", "T02", "T03", "T04", "T05", "T06"];
    let (w, _, _) = halved("lane-halve-trip", &tasks, "T03");
    let first = w
        .lane()
        .iter()
        .filter(|x| x["event"] == "run" && x["batch"] == "461-1")
        .nth(1)
        .and_then(|x| x["attempt"].as_str())
        .unwrap()
        .to_owned();
    // its repair handed in after another task's, still red: the halving leaves it last again
    let again = [
        w.hand_in("461", "T07", "f/T07.txt", "T07\n"),
        w.hand_in("461", "T03", "g/T03.txt", "T03 again\n"),
    ];
    let err = step(&lane_of(&w)).unwrap_err();
    let lines = w.lane();
    let runs: Vec<&Value> = lines
        .iter()
        .filter(|x| x["event"] == "run" && x["batch"] == "461-2")
        .collect();
    assert_eq!(runs.len(), 2, "[T07 T03] red, [T07] green");
    let second = runs[0]["attempt"].as_str().unwrap().to_owned();
    let held = lines
        .iter()
        .find(|x| x["event"] == "eject" && x["batch"] == "461-2")
        .unwrap();
    assert_eq!(held["change"], json!(again[1]));
    assert_eq!(held["why"], "inferred");
    assert_eq!(held["repair"], Value::Null);
    assert_eq!(held["arbiter"], "ask:lane-T03");
    let stop = lines.iter().find(|x| x["event"] == "stop").unwrap();
    assert_eq!(stop["batch"], "461-2");
    assert_eq!(stop["held"], json!([again[1]]));
    assert!(
        err.contains("the round arbiter is owed ask:lane-T03"),
        "{err}"
    );
    // no second repair; one ask with the two attempt files the two inferences rest on
    assert_eq!(repairs::read(&w.common).len(), 1);
    let said: Vec<String> = std::fs::read_to_string(w.common.join("asked"))
        .unwrap()
        .lines()
        .map(str::to_owned)
        .collect();
    assert_eq!(said.len(), 2);
    assert_eq!(
        said[0],
        format!("SUBJECT=lane-T03 FILES={first} {second} spec=461-x dir=specs/461-x")
    );
    // T07 landed before the trip
    assert_eq!(w.origin_holds("f/T07.txt"), "T07");
}
