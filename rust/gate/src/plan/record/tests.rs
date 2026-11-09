//! A verdict derived, kept per block, and declined without its reviewer.

use serde_json::{json, Value};

use super::super::sections::{block_digest, blocks, digest, task_sections};
use super::super::status::{owed, task_current};
use super::super::tests::{current, feature, git, narrow_bad, narrow_ok, within, PLAN, PLAN_TASKS};
use super::{
    arbiter_accept, derive_verdict, house_style, record, record_blocks, record_task, slim_record,
    Stop,
};

fn read(dir: &std::path::Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(dir.join("plan-review.json")).unwrap()).unwrap()
}

fn refusal<T: std::fmt::Debug>(got: Result<T, Stop>) -> String {
    match got.unwrap_err() {
        Stop::Refused(why) | Stop::Declined(why) => why,
    }
}

#[test]
fn a_malformed_decision_is_refused() {
    for (decision, why) in [
        (
            json!({"id": "P1", "summary": "s", "class": "maybe"}),
            "class must be",
        ),
        (
            json!({"id": "P1", "summary": "s", "class": "narrowing"}),
            "needs a ruling",
        ),
        (
            json!({"id": "P1", "summary": "s", "class": "within", "ruling": "LEGITIMATE"}),
            "carries no ruling",
        ),
        (
            json!({"summary": "s", "class": "within"}),
            "id and a summary",
        ),
    ] {
        assert!(refusal(derive_verdict(&[decision])).contains(why));
    }
}

#[test]
fn the_verdict_is_derived_from_the_rulings() {
    assert_eq!(derive_verdict(&[]), Ok("CLEAR"));
    assert_eq!(derive_verdict(&[within(), narrow_ok()]), Ok("CLEAR"));
    assert_eq!(derive_verdict(&[within(), narrow_bad()]), Ok("BLOCKED"));
}

#[test]
fn recording_declines_without_the_reviewer_and_refuses_what_it_cannot_trust() {
    let dir = feature(Some(PLAN), None);
    let sf = "spec-fidelity";
    assert!(
        refusal(record(&dir, &current(&[], "CLEAR", PLAN), "main", None))
            .contains("only the `spec-fidelity` subagent")
    );
    assert!(refusal(record(
        &dir,
        &current(&[], "CLEAR", "another plan"),
        sf,
        None
    ))
    .contains("plan changed while it was being reviewed"));
    assert!(refusal(record(
        &dir,
        &current(&[narrow_bad()], "CLEAR", PLAN),
        sf,
        None
    ))
    .contains("says CLEAR but its rulings make it BLOCKED"));
    assert!(refusal(record(
        &dir,
        &json!({"plan_sha256": digest(PLAN.as_bytes())}),
        sf,
        None
    ))
    .contains("decisions must be a list"));
    assert!(refusal(record(
        &feature(None, None),
        &current(&[], "CLEAR", PLAN),
        sf,
        None
    ))
    .contains("no plan.md"));
    assert!(!dir.join("plan-review.json").exists());
    let out = record(
        &dir,
        &json!({"plan_sha256": digest(PLAN.as_bytes()), "decisions": [narrow_bad()]}),
        sf,
        Some("2026-09-13"),
    )
    .unwrap();
    assert!(
        out["verdict"] == "BLOCKED" && out["reviewed"] == "2026-09-13" && out["declared"] == sf
    );
    assert_eq!(owed(&dir).unwrap().0, "plan-review-blocked");
    record(&dir, &current(&[within()], "CLEAR", PLAN), sf, None).unwrap();
    assert_eq!(owed(&dir), None);
}

#[test]
fn a_task_section_carries_its_own_decision_verdict() {
    let dir = feature(Some(PLAN_TASKS), None);
    let sf = "spec-fidelity";
    record(&dir, &current(&[within()], "CLEAR", PLAN_TASKS), sf, None).unwrap();
    let secs = task_sections(PLAN_TASKS);
    assert!(
        secs.keys().eq(["T05", "T06"])
            && secs["T05"].starts_with("## T05")
            && !secs["T05"].contains("a well")
    );
    let sha = digest(secs["T05"].as_bytes());
    assert!(matches!(
        record_task(
            &dir,
            "T05",
            &json!({"section_sha256": sha, "decisions": []}),
            "main",
            None
        ),
        Err(Stop::Declined(_))
    ));
    assert!(refusal(record_task(
        &dir,
        "T09",
        &json!({"section_sha256": sha, "decisions": []}),
        sf,
        None
    ))
    .contains("no section naming T09"));
    assert!(refusal(record_task(
        &dir,
        "T05",
        &json!({"section_sha256": "x", "decisions": []}),
        sf,
        None
    ))
    .contains("changed while"));
    assert!(refusal(record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha}),
        sf,
        None
    ))
    .contains("must be a list"));
    assert_eq!(
        record_task(
            &dir,
            "T05",
            &json!({"section_sha256": sha, "decisions": [within()]}),
            sf,
            None
        )
        .unwrap()["verdict"],
        "CLEAR"
    );
    assert_eq!(
        record_task(
            &dir,
            "T05",
            &json!({"plan_sha256": sha, "decisions": [within()]}),
            sf,
            None
        )
        .unwrap()["verdict"],
        "CLEAR"
    );
    let review = read(&dir);
    assert!(
        task_current(&review, PLAN_TASKS, "T05", None)
            && !task_current(&review, PLAN_TASKS, "T06", None)
    );
    let grown = PLAN_TASKS.replace(
        "- the bath 10 x 8 ft (GUESS)\n",
        "- the bath 10 x 8 ft (GUESS)\n- a second bath for guests\n",
    );
    std::fs::write(dir.join("plan.md"), &grown).unwrap();
    assert_eq!(owed(&dir).unwrap().0, "plan-review-stale");
    record_task(&dir, "T05", &json!({"section_sha256": digest(task_sections(&grown)["T05"].as_bytes()), "decisions": [within()]}), sf, None).unwrap();
    assert_eq!(owed(&dir), None);
    record(&dir, &current(&[within()], "CLEAR", &grown), sf, None).unwrap();
    assert!(read(&dir)["tasks"].get("T05").is_some());
}

#[test]
fn a_clear_task_section_records_its_blocks_reviewed() {
    let dir = feature(Some(PLAN_TASKS), None);
    let grown = PLAN_TASKS.replace(
        "- the bath 10 x 8 ft (GUESS)\n",
        "- the bath 10 x 8 ft (GUESS)\n- a second bath\n",
    );
    std::fs::write(dir.join("plan.md"), &grown).unwrap();
    let sha = digest(task_sections(&grown)["T05"].as_bytes());
    let narrowing = json!({"id": "P2", "summary": "a module", "class": "narrowing", "ruling": "NOT LEGITIMATE"});
    record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha, "decisions": [narrowing]}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert!(read(&dir).get("blocks").is_none());
    record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha, "decisions": [within()]}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    let recorded = read(&dir)["blocks"].as_object().unwrap().clone();
    let expect: Vec<String> = blocks(&grown)
        .into_iter()
        .map(|(k, ..)| k)
        .filter(|k| k.contains("T05"))
        .collect();
    assert_eq!(recorded.keys().cloned().collect::<Vec<_>>(), expect);
    assert!(recorded.values().all(|v| v["verdict"] == "CLEAR"));
}

#[test]
fn a_verdict_s_free_text_is_written_in_the_house_style_its_keys_as_given() {
    let brit = format!("gr{}", "ey");
    let got = house_style(Some(&json!([{"id": format!("D1-{brit}"), "class": "within", "why": format!("a {brit} band, <q>a {brit} quoted</q>"), "n": 3}, "stray"]))).unwrap();
    assert_eq!(
        got[0],
        json!({"id": format!("D1-{brit}"), "class": "within", "why": format!("a gray band, <q>a {brit} quoted</q>"), "n": 3})
    );
    assert_eq!(got[1], "stray");
    assert_eq!(house_style(None), None);
}

#[test]
fn a_block_review_names_each_block_and_a_removal_leaves_the_record() {
    let plan = "# p\n\n## A\n\nx\n\n## B\n\ny\n";
    let dir = feature(Some(plan), None);
    let sf = "spec-fidelity";
    let sha = block_digest("## A\n\nx\n\n");
    assert!(matches!(
        record_blocks(
            &dir,
            &json!({"blocks": {"## A": sha}, "decisions": []}),
            "main",
            None
        ),
        Err(Stop::Declined(_))
    ));
    assert!(
        refusal(record_blocks(&dir, &json!({"blocks": {}}), sf, None))
            .contains("must name each block")
    );
    assert!(refusal(record_blocks(
        &dir,
        &json!({"blocks": {"## Z": "x"}, "decisions": []}),
        sf,
        None
    ))
    .contains("no block '## Z'"));
    assert!(refusal(record_blocks(
        &dir,
        &json!({"blocks": {"## A": "abcdefabcdefabcdef"}, "decisions": []}),
        sf,
        None
    ))
    .contains("its digest is not abcdefabcdef"));
    assert!(refusal(record_blocks(
        &dir,
        &json!({"blocks": {"## A": sha}}),
        sf,
        None
    ))
    .contains("decisions must be a list"));
    let got = record_blocks(
        &dir,
        &json!({"blocks": {"## A": sha}, "decisions": []}),
        sf,
        Some("2026-01-01"),
    )
    .unwrap();
    assert!(got["verdict"] == "CLEAR" && got["blocks"] == json!(["## A"]));
    assert_eq!(read(&dir)["block_reviews"][0]["reviewed"], "2026-01-01");
    let blocked = record_blocks(
        &dir,
        &json!({"blocks": {"(removed) ## A": "removed"}, "decisions": [narrow_bad()]}),
        sf,
        None,
    )
    .unwrap();
    assert_eq!(blocked["verdict"], "BLOCKED");
    assert!(
        read(&dir)["blocks"].get("## A").is_some(),
        "a blocked removal leaves it"
    );
    record_blocks(
        &dir,
        &json!({"blocks": {"(removed) ## A": "removed"}, "decisions": []}),
        sf,
        None,
    )
    .unwrap();
    assert!(read(&dir)["blocks"].get("## A").is_none());
}

#[test]
fn a_changed_decisions_block_owes_the_approach_answered_again() {
    let dir = feature(
        Some("# p\n\n### T05 Decisions\n\n**D1 - x.** first\n"),
        None,
    );
    let root = dir.parent().unwrap().parent().unwrap().to_owned();
    git(&root, &["init", "-q", "-b", "main"]);
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(
        root.join("docs/approach-checklist.md"),
        "## A. x\n\n1. one\n",
    )
    .unwrap();
    let key = "### T05 Decisions";
    let first = block_digest("### T05 Decisions\n\n**D1 - x.** first\n");
    let once = record_blocks(
        &dir,
        &json!({"blocks": {key: first}, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert!(
        once.get("approach_owed").is_none(),
        "a first review owes nothing"
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "reviewed"]);
    let changed = "### T05 Decisions\n\n**D1 - x.** a wholly different rule stated here\n";
    std::fs::write(dir.join("plan.md"), format!("# p\n\n{changed}")).unwrap();
    let again = record_blocks(
        &dir,
        &json!({"blocks": {key: block_digest(changed)}, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert!(again["approach_owed"][0]
        .as_str()
        .unwrap()
        .contains("re-decided:### T05 Decisions"));
    let typo = "### T05 Decisions\n\n**D1 - x.** a wholly different rule stated heer\n";
    std::fs::write(dir.join("plan.md"), format!("# p\n\n{typo}")).unwrap();
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(plan.contains("heer"));
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    let reanswered = json!({"blocks": {key: block_digest(typo), "### T05 Approach (re-answered 2026-01-01T00:00Z)": "removed"}, "decisions": []});
    assert!(record_blocks(&dir, &reanswered, "spec-fidelity", None).is_err());
}

#[test]
fn the_arbiter_s_accept_is_the_plan_s_verdict() {
    let plan = "# p\n\n## A\n\nx\n";
    let dir = feature(Some(plan), None);
    let trigger = "round:spec-fidelity|plan:243-x#T01@3";
    assert!(refusal(arbiter_accept(&dir, "not-a-plan-round", None))
        .contains("is not a plan review's round trigger"));
    assert!(matches!(
        arbiter_accept(&dir, trigger, None),
        Err(Stop::Declined(_))
    ));
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!("\n{}\n", json!({"trigger": trigger, "ruling": "continue"})),
    )
    .unwrap();
    assert!(matches!(
        arbiter_accept(&dir, trigger, None),
        Err(Stop::Declined(_))
    ));
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!("{}\n", json!({"trigger": trigger, "ruling": "accept"})),
    )
    .unwrap();
    let named = arbiter_accept(&dir, trigger, Some("2026-01-01")).unwrap();
    assert_eq!(named, ["## A", "preamble"]);
    let review = read(&dir);
    assert_eq!(review["blocks"]["## A"]["declared"], "round-arbiter");
    assert_eq!(review["block_reviews"][0]["decisions"][0]["id"], trigger);
    assert_eq!(owed(&dir), None);
    let asked = "ask:449-plan";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": asked, "ruling": "process-fault", "review": "plan"})
        ),
    )
    .unwrap();
    std::fs::write(dir.join("plan.md"), "# p\n").unwrap();
    assert_eq!(arbiter_accept(&dir, asked, None).unwrap(), ["preamble"]);
    assert!(
        read(&dir)["blocks"].get("## A").is_none(),
        "a block deleted by hand leaves the record"
    );
}

#[test]
fn a_record_from_before_block_verdicts_is_slimmed_its_verdicts_kept() {
    let review = json!({"plan_text": "# p\n", "verdict": "CLEAR", "reviewed": "2026-01-01", "tasks": {"T1": {"verdict": "CLEAR", "section_text": "x"}}});
    let slim = slim_record(&review);
    assert!(slim.get("plan_text").is_none() && slim["tasks"]["T1"].get("section_text").is_none());
    assert_eq!(slim["blocks"]["preamble"]["reviewed"], "2026-01-01");
    assert_eq!(slim_record(&json!({"blocks": {}})), json!({"blocks": {}}));
}
