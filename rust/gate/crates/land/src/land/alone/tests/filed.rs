//! 451 T180: a task the landing's section files lands its tasks.md line, never its builder's section or verdict. 449's T351 and T358
//! bundles landed alone with T377's filled section and BLOCKED verdict uncommitted in the clone (T351's section files T377); the
//! land-alone step committed both, so the landed tree held T377's block, and the landing's tick refused on it (observed 2026-11-23,
//! 832cedd0fc, `/tmp/land351/land1.log`).

use serde_json::{json, Value};

use super::{alone, edited, put, sh, world};

/// The review record: the preamble's verdict and each `(task, heading, verdict)`'s block, block review and task verdict.
fn review(tasks: &[(&str, &str, &str)]) -> String {
    let mut v = json!({"feature": "451-x", "blocks": {"preamble": {"verdict": "CLEAR"}}, "block_reviews": [], "tasks": {}});
    for (t, heading, verdict) in tasks {
        v["blocks"][*heading] = json!({"verdict": verdict});
        v["block_reviews"]
            .as_array_mut()
            .unwrap()
            .push(json!({"blocks": [heading]}));
        v["tasks"][*t] = json!({"verdict": verdict});
    }
    serde_json::to_string_pretty(&v).unwrap().replace("  ", " ") + "\n"
}

#[test]
fn a_filed_task_lands_its_line_but_never_its_builder_s_section_or_verdict() {
    let (dir, c) = world("alone-filed");
    put(&c, "specs/451-x/plan-review.json", &review(&[]));
    sh(&c, "git add -A && git commit -qm 'the review record' && git push -q origin HEAD:main 2>/dev/null");
    // two started tasks, all uncommitted: T1 (the landing's) files T3 from its section; T3's builder filled T3's section, its
    // heading naming T1 as T377's named T351, and its review came back BLOCKED
    let t1 = "### T1 the real why\n\nT1's words. Not fixed here: a leak. Filed as T3; lands before T2.\n\n";
    let t2 = "### T2 another builder's section\n\nT2's words.\n";
    let t3 = "\n### T3 (filed by T1's section)\n\nT3's builder's words.\n";
    put(&c, "specs/451-x/plan.md", &format!("{t1}{t2}{t3}"));
    let lines = "- [ ] T1 one\n- [ ] T2 two\n- [ ] T3 three, filed by T1\n";
    put(&c, "specs/451-x/tasks.md", lines);
    let verdicts = [
        ("T1", "### T1 the real why", "CLEAR"),
        ("T3", "### T3 (filed by T1's section)", "BLOCKED"),
    ];
    put(&c, "specs/451-x/plan-review.json", &review(&verdicts));
    for (task, rel) in [
        ("T1", "specs/451-x/plan.md"),
        ("T3", "specs/451-x/plan.md"),
        ("T3", "specs/451-x/plan-review.json"),
    ] {
        edited(&dir, &c, task, rel);
    }
    // the landing refused after the commit apart, as 449's tick refused: the clone's HEAD is that commit
    let (rc, said) = alone(&dir, &c, &[("STUB_RC", "2")]);
    assert_eq!(rc, 2, "{said}");
    let head = |rel: &str| sh(&c, &format!("git show HEAD:specs/451-x/{rel}"));
    assert_eq!(head("plan.md") + "\n", format!("{t1}{t2}"));
    assert_eq!(head("tasks.md") + "\n", lines);
    let staged: Value = serde_json::from_str(&head("plan-review.json")).unwrap();
    let mine: Value = serde_json::from_str(&review(&verdicts[..1])).unwrap();
    assert_eq!(staged, mine);
    assert_eq!(
        sh(&c, "git log -1 --format=%s"),
        "451-x T1: their own plan sections, tasks.md lines and verdicts and the tasks.md lines of the tasks they file (T3), apart from the other open tasks' (land-alone, 451 T101)"
    );
    // the clone keeps T3's builder's work, uncommitted
    let read = |rel: &str| std::fs::read_to_string(c.join(rel)).unwrap();
    assert_eq!(read("specs/451-x/plan.md"), format!("{t1}{t2}{t3}"));
    assert_eq!(read("specs/451-x/plan-review.json"), review(&verdicts));
}
