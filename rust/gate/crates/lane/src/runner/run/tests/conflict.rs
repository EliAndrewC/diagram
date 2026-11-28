//! A CARRY THAT STOPS (feature 461 T25, D7's table) end to end: a hand-in conflicting with a newer `origin/main` is ejected as one
//! repair entry (kind `integrate`, `why` `conflict`) with the lane's tree put back, and the other change lands; a batch whose every
//! carry conflicts runs no landing; a change conflicting with an earlier one of its own batch is ejected and the earlier lands; a
//! conflict in a halving's set ends the halving and the rest runs as one; a carry of one change that fails with no conflicting path
//! ejects it (`why` `carry`); a carry refused on the lane's own tree still stops the runner with the batch open.

use super::*;

/// The lane's tree as the pool's registry holds it.
fn lane_tree(w: &World) -> PathBuf {
    w.dir.path().join("repo-land")
}

#[test]
fn a_hand_in_conflicting_with_a_newer_main_is_one_conflict_entry_and_the_other_change_lands() {
    let w = world("lane-run-conflict");
    let one = w.hand_in("461", "T01", "a.txt", "one\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    // main moved after the hand-in: T01's a.txt is now another landing's
    w.origin_moves("a.txt");
    let l = lane_of(&w);
    assert_eq!(step(&l), Ok(true));
    assert_eq!(
        w.events(),
        ["batch", "eject", "owed", "carry", "run", "push", "landed", "owed"]
    );
    let lines = w.lane();
    assert_eq!(
        lines[1],
        json!({"utc": lines[1]["utc"], "event": "eject", "batch": "461-1", "change": one, "repair": "r1", "why": "conflict"})
    );
    let carried = repairs::read(&w.common)[0]["attempt"]
        .as_str()
        .unwrap()
        .to_owned();
    assert!(carried.ends_with(&format!("l7r-lane/attempts/461-1-carry-{}.log", &one[..10])));
    assert!(std::fs::read_to_string(&carried).unwrap().contains("a.txt"));
    assert_eq!(lines[2].get(crate::wake::STOPPED), None);
    assert_eq!(
        lines[2]["line"],
        format!("lane: batch 461-1's carry of {} stopped in conflict - 461 T01 ejected as repair r1 (integrate, conflict: a.txt) - make builder-next hands it to a fresh builder; the rest of the batch goes on: {carried}", &one[..10])
    );
    assert_eq!(lines[3]["code"], 0);
    assert_eq!(lines[3]["conflict"], json!(["a.txt"]));
    assert_eq!(lines[4]["set"], json!([&two[..10]]));
    assert_eq!(lines[6]["landed"], json!([two]));
    assert_eq!(lines[6]["ejected"], json!([one]));
    assert_eq!(
        lines[7]["line"],
        "lane: batch 461-1 landed - 461 T02 (1 change(s), 1 ejected, 1 run(s), 0 minutes)"
    );
    let mut entry = repairs::read(&w.common)[0].clone();
    entry.as_object_mut().unwrap().remove("utc");
    assert_eq!(
        entry,
        json!({"repair": "r1", "feature": "461-x", "tasks": ["T01"], "kind": "integrate", "ejected": [one],
            "batch": "461-1", "why": "conflict", "units": ["a.txt"], "attempt": carried})
    );
    assert_eq!(w.origin_holds("b.txt"), "b");
    assert_eq!(w.origin_holds("a.txt"), "moved");
    // the ejected change's ref kept for its repair, the landed one's deleted; no pick left in the lane's tree
    assert_eq!(w.refs(), "refs/l7r/done/461-T01");
    assert_eq!(git(&lane_tree(&w), &["status", "--porcelain"]), "");
    // a conflict pins nothing (data-model.md), and the batch is closed: no batch formed again
    assert!(!log::batches(&w.lane()).iter().any(Batch::open));
    assert_eq!(step(&l), Ok(false));
}

#[test]
fn a_batch_whose_every_change_conflicts_ejects_each_and_runs_no_landing() {
    let w = world("lane-run-conflict-all");
    let one = w.hand_in("461", "T01", "a.txt", "one\n");
    let two = w.hand_in("461", "T02", "b.txt", "two\n");
    w.origin_moves("a.txt");
    w.origin_moves("b.txt");
    assert_eq!(step(&lane_of(&w)), Ok(true));
    assert_eq!(
        w.events(),
        ["batch", "eject", "owed", "eject", "owed", "carry", "landed", "owed"]
    );
    let lines = w.lane();
    assert_eq!(
        (&lines[1]["change"], &lines[1]["repair"]),
        (&json!(one), &json!("r1"))
    );
    assert_eq!(
        (&lines[3]["change"], &lines[3]["repair"]),
        (&json!(two), &json!("r2"))
    );
    assert_eq!(lines[5]["conflict"], json!(["a.txt", "b.txt"]));
    assert_eq!(lines[6]["runs"], 0);
    assert_eq!(
        lines[7]["line"],
        "lane: batch 461-1 ended - nothing landed, 2 ejected (0 run(s), 0 minutes)"
    );
    assert_eq!(repairs::read(&w.common).len(), 2);
}

#[test]
fn a_change_conflicting_with_an_earlier_one_of_its_batch_is_ejected_and_the_earlier_lands() {
    let w = world("lane-run-conflict-batch");
    let one = w.hand_in("461", "T01", "a.txt", "one\n");
    let two = w.hand_in("461", "T02", "a.txt", "two\n");
    assert_eq!(step(&lane_of(&w)), Ok(true));
    let lines = w.lane();
    assert_eq!(
        (&lines[1]["event"], &lines[1]["change"], &lines[1]["why"]),
        (&json!("eject"), &json!(two), &json!("conflict"))
    );
    assert_eq!(lines[6]["landed"], json!([one]));
    assert_eq!(w.origin_holds("a.txt"), "one");
    // a conflict ejection pins nothing for the tripwire (data-model.md)
    let hand_ins = super::super::all_hand_ins(&w.common);
    let entries = repairs::read(&w.common);
    assert!(crate::tripwire::pins(&lines, &entries, &hand_ins, "461", "T02").is_empty());
}

/// A red no change's delta touches (the crate `lib/none`): the record cannot place it, so the batch is halved.
const UNPLACED: &str = r#"{"ev":"Phase","src":"rust","step":"test","t0":"@T@","t1":"@T@","code":101,"clone":"@TREE@","crates":["lib/none"]}"#;

#[test]
fn a_conflict_in_a_halving_s_set_ends_the_halving_and_the_rest_runs_as_one() {
    let w = world("lane-run-conflict-halving");
    let shas: Vec<String> = ["T01", "T02", "T03"]
        .iter()
        .map(|t| w.hand_in("461", t, &format!("f/{t}.txt"), &format!("{t}\n")))
        .collect();
    // T03 red wherever it runs, as a red the record cannot place; T02's carry conflicts from its second on (the halving's)
    std::fs::write(w.common.join("phase-T03"), format!("{UNPLACED}\n")).unwrap();
    std::fs::write(w.common.join(format!("clash-{}", shas[1])), "1").unwrap();
    assert_eq!(step(&lane_of(&w)), Ok(true));
    assert_eq!(
        w.events(),
        [
            "batch",
            "carry",
            "run",
            "attribute",
            "carry",
            "run",
            "push",
            "eject",
            "owed",
            "carry",
            "carry",
            "run",
            "attribute",
            "eject",
            "owed",
            "landed",
            "owed"
        ]
    );
    let lines = w.lane();
    assert_eq!(lines[5]["set"], json!([&shas[0][..10]]));
    assert_eq!(
        (&lines[7]["change"], &lines[7]["why"]),
        (&json!(shas[1]), &json!("conflict"))
    );
    assert_eq!(lines[9]["conflict"], json!(["f/T02.txt"]));
    // the rest - T03 alone - runs as one, red alone, and is ejected `red` after its own run
    assert_eq!(lines[11]["set"], json!([&shas[2][..10]]));
    assert_eq!(
        (&lines[13]["change"], &lines[13]["why"]),
        (&json!(shas[2]), &json!("red"))
    );
    assert_eq!(lines[15]["landed"], json!([shas[0]]));
    assert_eq!(lines[15]["ejected"], json!([shas[1], shas[2]]));
    assert_eq!(git(&lane_tree(&w), &["status", "--porcelain"]), "");
}

#[test]
fn a_carry_of_one_change_that_fails_with_no_conflicting_path_ejects_it_and_the_other_lands() {
    let w = world("lane-run-carry-fails");
    let one = w.hand_in("461", "T01", "a.txt", "one\n");
    let two = w.hand_in("461", "T02", "b.txt", "b\n");
    // T01's carry fails with no conflicting path, as one whose verified end failed: the change's own
    std::fs::write(w.common.join(format!("carry-fails-{one}")), "").unwrap();
    assert_eq!(step(&lane_of(&w)), Ok(true));
    assert_eq!(
        w.events(),
        ["batch", "eject", "owed", "carry", "run", "push", "landed", "owed"]
    );
    let lines = w.lane();
    assert_eq!(
        (&lines[1]["change"], &lines[1]["why"]),
        (&json!(one), &json!("carry"))
    );
    let entry = &repairs::read(&w.common)[0];
    assert_eq!(
        (&entry["kind"], &entry["why"]),
        (&json!("integrate"), &json!("carry"))
    );
    assert_eq!(
        entry["units"],
        json!(["land: the carry did not end verified"])
    );
    let attempt = entry["attempt"].as_str().unwrap();
    assert_eq!(
        lines[2]["line"],
        format!("lane: batch 461-1's carry of {} stopped - 461 T01 ejected as repair r1 (integrate, carry: land: the carry did not end verified) - make builder-next hands it to a fresh builder; the rest of the batch goes on: {attempt}", &one[..10])
    );
    assert_eq!(lines[3]["conflict"], json!([]));
    assert_eq!(lines[6]["landed"], json!([two]));
    assert_eq!(git(&lane_tree(&w), &["status", "--porcelain"]), "");
}

#[test]
fn a_carry_refused_on_the_lane_s_own_tree_leaves_the_batch_open() {
    let w = world("lane-run-carry-refused");
    w.hand_in("461", "T01", "a.txt", "one\n");
    std::fs::write(w.common.join("carry-refused"), "").unwrap();
    let stopped = step(&lane_of(&w)).unwrap_err();
    assert!(stopped.contains("the carry of"), "{stopped}");
    assert!(
        stopped.contains("on the lane's own tree, no change named"),
        "{stopped}"
    );
    let carry = w.lane().pop().unwrap();
    assert_eq!(carry["event"], "carry");
    assert_eq!(carry["conflict"], json!([]));
    assert_ne!(carry["code"], 0);
    assert!(open(&w).open());
    assert!(repairs::read(&w.common).is_empty());
}
