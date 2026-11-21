use std::path::Path;

use serde_json::{json, Value};

use super::{hold, launched, live, purge, refusal, restore, returned, snapshot};
use crate::checks::testkit::{clone_at, dir};

const PLAN: &str = "# plan\n\n## T01 the bath\n\nheld body of the section stands here\n\n## T02 other\n\nother text\n";

fn feature(root: &Path) {
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(root.join("specs/900-a/plan.md"), PLAN).unwrap();
}

fn running(task: &str, blocks: &[&str], t: f64) -> Value {
    json!({"feature": "900-a", "task": task, "blocks": blocks, "t": t, "state": "running", "aid": "ag"})
}

#[test]
fn a_dispatch_takes_a_hold() {
    let d = dir("hold");
    let bundle = d.join("plan-900-a-T01");
    std::fs::create_dir_all(&bundle).unwrap();
    let mut state = json!({});
    hold(&mut state, "t0", "no bundle", 1.0);
    assert_eq!(state, json!({}));
    hold(
        &mut state,
        "t1",
        &format!("Read {}/MANIFEST.md", bundle.display()),
        1.5,
    );
    assert_eq!(
        state["plan_holds"]["t1"],
        json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1.5, "state": "pending"})
    );
    let blocks = d.join("plan-900-a-blocks-x");
    std::fs::create_dir_all(&blocks).unwrap();
    std::fs::write(blocks.join("blocks.md"), "<!-- block \"## A \\\"q\\\"\" sha256\nnot one\n<!-- block \"k\\\\z\\n\\t\\r\\a\\b\\f\\v\\'\\q\u{e9}\" sha256\n").unwrap();
    hold(
        &mut state,
        "t2",
        &format!("x {}/MANIFEST.md y", blocks.display()),
        2.0,
    );
    assert_eq!(
        state["plan_holds"]["t2"]["blocks"],
        json!([
            "## A \"q\"",
            "k\\z\n\t\r\u{7}\u{8}\u{c}\u{b}'\\q\u{c3}\u{a9}"
        ])
    );
    hold(
        &mut state,
        "t3",
        &format!("{}-gone/plan-900-a-blocks-y/MANIFEST.md", d.display()),
        2.0,
    );
    assert_eq!(state["plan_holds"]["t3"]["blocks"], json!([]));
    launched(&mut state, "t1", "ag1");
    launched(&mut state, "nope", "ag1");
    launched(&mut json!({}), "x", "y");
    assert_eq!(state["plan_holds"]["t1"]["state"], json!("running"));
    returned(&mut state, "ag1");
    returned(&mut json!({}), "ag1");
    assert!(state["plan_holds"].get("t1").is_none());
}

#[test]
fn a_hold_is_live_or_dead_by_its_age() {
    assert!(live(&running("T01", &[], 100.0), 1000.0));
    assert!(!live(&running("T01", &[], 0.0), 5000.0));
    assert!(!live(&json!({"state": "pending", "t": 0.0}), 10.0));
    let mut state = json!({"plan_holds": {"a": {"state": "pending", "t": 0.0}, "b": {"state": "pending", "t": 950.0}, "c": {"state": "running", "t": 0.0}}});
    purge(&mut state, 1000.0);
    let keys: Vec<&String> = state["plan_holds"].as_object().unwrap().keys().collect();
    assert_eq!(keys, ["b", "c"]);
    purge(&mut json!({}), 1.0);
}

#[test]
fn a_snapshot_is_written_back_when_held_text_changes() {
    let root = clone_at("restore");
    feature(&root);
    let mut state = json!({"plan_holds": {"h1": running("T01", &[], 900.0), "dead": running("T01", &[], 0.0), "p": {"feature": "x", "state": "pending", "t": 999.0}}});
    snapshot(&mut state, None, "call", 1000.0);
    assert!(state.get("plan_snaps").is_none());
    snapshot(&mut state, Some(&root), "call", 1000.0);
    assert!(state["plan_snaps"]["call"]["h1"][0]
        .as_str()
        .unwrap()
        .contains("held body"));
    assert_eq!(state["plan_holds"].as_object().unwrap().len(), 3);
    snapshot(&mut state, Some(&root), "empty", 100_000.0);
    assert!(state["plan_snaps"].get("empty").is_none());
    assert_eq!(restore(&mut state, Some(&root), "unrelated"), "");
    let unchanged = restore(&mut state, Some(&root), "call");
    assert_eq!(unchanged, "");
    assert!(state.get("plan_snaps").is_none());
    snapshot(&mut state, Some(&root), "again", 1000.0);
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("held body", "CHANGED body"),
    )
    .unwrap();
    let msg = restore(&mut state, Some(&root), "again");
    assert!(msg.contains("T01's section of specs/900-a/plan.md") && msg.contains("(agent ag)"));
    assert!(std::fs::read_to_string(root.join("specs/900-a/plan.md"))
        .unwrap()
        .contains("held body"));
    let mut none = json!({"plan_snaps": {"x": {"gone": ["a"]}}, "plan_holds": {"h1": running("T01", &[], 1.0)}});
    assert_eq!(restore(&mut none, None, "x"), "");
    assert!(none.get("plan_snaps").is_none());
    let mut other_snap = json!({"plan_snaps": {"keep": {"h1": []}, "drop": {"gone": []}}, "plan_holds": {"h1": running("T01", &[], 1.0)}});
    restore(&mut other_snap, None, "absent");
    assert!(
        other_snap["plan_snaps"].get("keep").is_some()
            && other_snap["plan_snaps"].get("drop").is_none()
    );
    assert_eq!(restore(&mut json!({}), Some(&root), "x"), "");
    let mut gone_hold = json!({"plan_snaps": {"x": {"gone": ["a"]}}});
    assert_eq!(restore(&mut gone_hold, Some(&root), "x"), "");
}

#[test]
fn a_held_block_is_written_back() {
    let root = clone_at("blocks");
    feature(&root);
    let mut state =
        json!({"plan_holds": {"h": running("", &["## T01 the bath", "## T02 other"], 900.0)}});
    snapshot(&mut state, Some(&root), "c", 1000.0);
    let edited = PLAN
        .replace("held body", "X body")
        .replace("other text", "Y text");
    std::fs::write(root.join("specs/900-a/plan.md"), &edited).unwrap();
    let msg = restore(&mut state, Some(&root), "c");
    assert!(msg.contains("2 block(s) of specs/900-a/plan.md"));
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
    let mut one_same =
        json!({"plan_holds": {"h": running("", &["## T01 the bath", "## T02 other"], 900.0)}});
    snapshot(&mut one_same, Some(&root), "c", 1000.0);
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("other text", "Y text"),
    )
    .unwrap();
    assert!(!restore(&mut one_same, Some(&root), "c").is_empty());
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
    // a held block's heading renamed (451 T80): HEAD paired the blocks left by order and wrote T01's old text over T02's block
    let mut renamed =
        json!({"plan_holds": {"h": running("", &["## T01 the bath", "## T02 other"], 900.0)}});
    snapshot(&mut renamed, Some(&root), "c", 1000.0);
    let tub = PLAN.replace("## T01 the bath", "## T01 the tub");
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        tub.replace("other text", "Y text"),
    )
    .unwrap();
    let msg = restore(&mut renamed, Some(&root), "c");
    let renamed_plan = std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap();
    assert_eq!(renamed_plan, tub, "{msg}");
    let named = msg.contains(
        "written back: `## T02 other`; NOT written back: `## T01 the bath` (gone from the plan)",
    );
    assert!(named, "{msg}");
    std::fs::write(root.join("specs/900-a/plan.md"), PLAN).unwrap();
    let mut missing_plan = json!({"plan_holds": {"h": {"feature": "no", "task": "T01", "t": 1.0, "state": "running"}}, "plan_snaps": {"c": {"h": ["old"]}}});
    assert_eq!(restore(&mut missing_plan, Some(&root), "c"), "");
    let mut gone_task =
        json!({"plan_holds": {"h": running("T09", &[], 1.0)}, "plan_snaps": {"c": {"h": ["old"]}}});
    let msg = restore(&mut gone_task, Some(&root), "c");
    let gone = msg.contains("T09's section")
        && msg.contains("NOTHING of it is written back: `old` (gone from the section)");
    assert!(gone, "{msg}");
    let mut empty_before =
        json!({"plan_holds": {"h": running("T01", &[], 1.0)}, "plan_snaps": {"c": {"h": []}}});
    let msg = restore(&mut empty_before, Some(&root), "c");
    let added = msg.contains("T01's section") && msg.contains("NOTHING of it is written back: `## T01 the bath` (new to the section since the call began)");
    assert!(added, "{msg}");
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one hold walked through every way a write can reach it"
)]
fn a_write_to_held_text_is_refused() {
    let root = clone_at("refusal");
    feature(&root);
    let plan = root
        .join("specs/900-a/plan.md")
        .to_string_lossy()
        .into_owned();
    let state = json!({"plan_holds": {"h": running("T01", &[], 900.0)}});
    let check = |tool: &str, ti: Value, escaped: bool, at: f64| {
        refusal(&state, Some(&root), tool, &ti, at, escaped)
    };
    assert_eq!(refusal(&state, None, "Edit", &json!({}), 1.0, false), "");
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        1000.0
    )
    .contains("(agent ag)"));
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "body of the"}),
        false,
        1000.0
    )
    .contains("running"));
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": "other text"}),
            false,
            1000.0
        ),
        ""
    );
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": ""}),
            false,
            1000.0
        ),
        ""
    );
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": "/elsewhere", "old_string": "held body"}),
            false,
            1000.0
        ),
        ""
    );
    let writes = check(
        "Write",
        json!({"file_path": plan, "content": "new"}),
        false,
        1000.0,
    );
    assert!(writes.contains("T01's section"));
    let keep = format!("x{PLAN}");
    assert_eq!(
        check(
            "Write",
            json!({"file_path": plan, "content": keep}),
            false,
            1000.0
        ),
        ""
    );
    assert!(check(
        "MultiEdit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        1000.0
    )
    .contains("running"));
    assert_eq!(check("Bash", json!({"command": "ls"}), false, 1000.0), "");
    assert_eq!(
        check(
            "Bash",
            json!({"command": "sed -i s/a/b/ specs/900-a/plan.md"}),
            false,
            1000.0
        ),
        ""
    );
    assert!(check(
        "Bash",
        json!({"command": "sed -i 's/## T01 the bath/x/' specs/900-a/plan.md"}),
        false,
        1000.0
    )
    .contains("running"));
    assert!(check(
        "Bash",
        json!({"command": "tee specs/900-a/plan.md # held body of the section stands here"}),
        false,
        1000.0
    )
    .contains("running"));
    assert!(check("Bash", json!({"command": "python3 -c 'open(\"x\", \"w\")' specs/900-a/plan.md \"held body of the\""}), false, 1000.0).contains("running"));
    assert_eq!(check("Read", json!({"file_path": plan}), false, 1000.0), "");
    let late = check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        3000.0,
    );
    assert!(late.contains("its dispatch looks dead"));
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": "held body"}),
            true,
            3000.0
        ),
        ""
    );
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        true,
        1000.0
    )
    .contains("running"));
    let pending = json!({"plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 999.0, "state": "pending"}}});
    let said = refusal(
        &pending,
        Some(&root),
        "Edit",
        &json!({"file_path": plan, "old_string": "held body"}),
        1000.0,
        false,
    );
    assert!(said.contains("a dispatch not yet launched"));
    let never = json!({"plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 0.0, "state": "pending"}}});
    assert_eq!(
        refusal(
            &never,
            Some(&root),
            "Edit",
            &json!({"file_path": plan, "old_string": "held body"}),
            1000.0,
            false
        ),
        ""
    );
    let empty_block = json!({"plan_holds": {"h": {"feature": "900-a", "blocks": ["## nope"], "t": 999.0, "state": "running"}}});
    assert_eq!(
        refusal(
            &empty_block,
            Some(&root),
            "Edit",
            &json!({"file_path": plan, "old_string": "held body"}),
            1000.0,
            false
        ),
        ""
    );
    let block = json!({"plan_holds": {"h": running("", &["## T01 the bath"], 999.0)}});
    assert!(refusal(
        &block,
        Some(&root),
        "Edit",
        &json!({"file_path": plan, "old_string": "held body"}),
        1000.0,
        false
    )
    .contains("1 block(s)"));
    assert_eq!(
        refusal(&json!({}), Some(&root), "Edit", &json!({}), 1.0, false),
        ""
    );
}

/// An Edit is refused when its text overlaps the held section, the section's end exclusive (451 T77, found by T73's builder on
/// 2026-11-21: an edit of the next section's heading counted as inside the held one, the log's 3 Edit refusals of that shape).
#[test]
fn an_edit_is_held_only_where_it_overlaps_the_section() {
    let root = clone_at("boundary");
    feature(&root);
    let plan = root
        .join("specs/900-a/plan.md")
        .to_string_lossy()
        .into_owned();
    let state = json!({"plan_holds": {"h": running("T01", &[], 900.0)}});
    let edit = |old: &str| {
        refusal(
            &state,
            Some(&root),
            "Edit",
            &json!({"file_path": plan, "old_string": old}),
            1000.0,
            false,
        )
    };
    // (old_string, refused): the end and the start themselves are outside; the last held byte, a start before it running in, a start
    // inside running past it, and the heading itself are inside
    let cases = [
        ("## T02 other", false),
        ("# plan\n\n", false),
        ("# plan\n\n## T01 the bath", true),
        ("\n## T02 other", true),
        ("here\n\n## T02", true),
        ("## T01 the bath", true),
    ];
    let misjudged: Vec<&(&str, bool)> = cases
        .iter()
        .filter(|(old, refused)| edit(old).contains("T01's section") != *refused)
        .collect();
    assert_eq!(misjudged, Vec::<&(&str, bool)>::new());
}

/// A shell write is refused on text standing only in the held section where the write-back would catch the rest - a live hold and a
/// foreground call - and on any held text otherwise (451 T78, found by T77 on 2026-11-21: 7 of 18 replayed refusals matched only
/// text every section shares, each a live hold and a foreground call, so a write to another section was refused).
#[test]
fn a_shell_write_on_shared_text_is_refused_only_where_nothing_writes_it_back() {
    let root = clone_at("shared");
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    let budget = "8. **The budget.** One landing.";
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        format!("# plan\n\n## T01 the bath\n\nheld body of the section stands here\n\n{budget}\n\n## T02 other\n\nother text\n\n{budget}\n"),
    )
    .unwrap();
    let shared = format!("printf '%s\\n' '{budget}' | tee -a specs/900-a/plan.md");
    let unique = "tee specs/900-a/plan.md # held body of the section stands here";
    let heading = "sed -i 's/## T01 the bath/x/' specs/900-a/plan.md";
    let pending = json!({"feature": "900-a", "task": "T01", "t": 990.0, "state": "pending"});
    let dead = running("T01", &[], -1000.0);
    // (hold, command, run_in_background, refused)
    let cases = [
        (running("T01", &[], 900.0), shared.as_str(), false, false),
        (
            running("", &["## T01 the bath"], 900.0),
            shared.as_str(),
            false,
            false,
        ),
        (running("T01", &[], 900.0), shared.as_str(), true, true),
        (pending.clone(), shared.as_str(), false, true),
        (dead, shared.as_str(), false, true),
        (running("T01", &[], 900.0), unique, false, true),
        (
            running("", &["## T01 the bath"], 900.0),
            unique,
            false,
            true,
        ),
        (running("T01", &[], 900.0), heading, false, true),
        (pending, unique, true, true),
    ];
    // the cases misjudged, by their place in `cases`
    let misjudged: Vec<usize> = (0..cases.len())
        .filter(|&i| {
            let (h, cmd, bg, refused) = &cases[i];
            let state = json!({"plan_holds": {"h": h}});
            let ti = json!({"command": cmd, "run_in_background": bg});
            refusal(&state, Some(&root), "Bash", &ti, 1000.0, false).is_empty() == *refused
        })
        .collect();
    assert_eq!(misjudged, Vec::<usize>::new());
    // a task's own headings apart in the plan: its joined section stands nowhere whole, so nothing is read as outside it - refused
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        format!("# plan\n\n## T01 the bath\n\nheld body\n\n{budget}\n\n## T02 other\n\n{budget}\n\n## T01 notes\n\nmore\n"),
    )
    .unwrap();
    let state = json!({"plan_holds": {"h": running("T01", &[], 900.0)}});
    assert!(!refusal(
        &state,
        Some(&root),
        "Bash",
        &json!({"command": shared}),
        1000.0,
        false
    )
    .is_empty());
    std::fs::remove_file(root.join("specs/900-a/plan.md")).unwrap();
    assert!(super::outside(&root.join("specs/900-a/plan.md"), &[]).is_none());
}

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A write past a million steps of command (feature 449 T185): `WRITE` erred at `fancy_regex`'s old limit and read as no write, so a
/// held plan's `tee` went unseen.
#[test]
fn a_write_past_a_million_steps_is_seen() {
    let command = format!(
        "{}| tee plan.md",
        "plain words of a long text ".repeat(50_000)
    );
    assert_eq!(
        within(move || super::WRITE.is_match(&command).ok()),
        Some(true)
    );
}

/// T01's section stands in two places: its own heading and Approach together, its part B past T02 (451 T80).
const SPLIT: &str = "# plan\n\n## T01 the bath\n\nheld body of the section stands here\n\n### T01 Approach\n\nthe approach held too\n\n## T02 other\n\nother text\n\n## T01 part B\n\nthe far part of the held section\n";

/// The plan after `edit` of SPLIT under a live T01 hold, and the write-back's answer.
fn split_after(
    name: &str,
    edit: impl Fn(&str) -> String,
    before: Option<Value>,
) -> (String, String) {
    let root = clone_at(name);
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    let plan = root.join("specs/900-a/plan.md");
    std::fs::write(&plan, SPLIT).unwrap();
    let mut state = json!({"plan_holds": {"h": running("T01", &[], 900.0)}});
    snapshot(&mut state, Some(&root), "c", 1000.0);
    if let Some(b) = before {
        state["plan_snaps"]["c"]["h"] = b;
    }
    std::fs::write(&plan, edit(SPLIT)).unwrap();
    let msg = restore(&mut state, Some(&root), "c");
    (std::fs::read_to_string(&plan).unwrap(), msg)
}

/// A task whose own headings stand apart is written back in each place it stands, and the answer says what it restored (451 T80:
/// HEAD replaced the joined section, which stands nowhere, so it restored nothing and still said "the held text is written back").
#[test]
fn a_split_section_is_written_back_in_each_place() {
    let far = |p: &str| p.replace("the far part", "CHANGED far part");
    let near = |p: &str| p.replace("the approach held", "CHANGED approach");
    let both = |p: &str| far(&near(p));
    for (name, edit) in [
        ("split-far", &far as &dyn Fn(&str) -> String),
        ("split-near", &near),
        ("split-both", &both),
    ] {
        let (plan, msg) = split_after(name, edit, None);
        assert_eq!(plan, SPLIT, "{name}: {msg}");
        let says = msg.contains("the held text is written back") && msg.contains("T01's section");
        assert!(says, "{name}: {msg}");
    }
    let (plan, msg) = split_after(
        "split-name",
        |p| p.replace("## T01 part B", "## T01 part C"),
        None,
    );
    assert_eq!(plan, SPLIT, "{msg}");
    let (plan, msg) = split_after(
        "split-gone-near",
        |p| p.replace("### T01 Approach\n\n", ""),
        None,
    );
    assert_eq!(plan, SPLIT, "{msg}");
    let named = msg.contains("in `## T01 the bath`") && msg.contains("1 of its 2 places");
    assert!(named, "{msg}");
}

/// The first held heading gone leaves the text under it outside the section, and the next heading heads the place: writing the old
/// text over that place would stand the held body twice, so nothing is written back and the answer says so (451 T80).
#[test]
fn a_first_heading_gone_is_not_written_twice() {
    let cut = |p: &str| p.replace("## T01 the bath\n\n", "");
    let (plan, msg) = split_after("split-gone-first", cut, None);
    let kept = cut(SPLIT);
    assert_eq!(plan, kept, "{msg}");
    let nothing =
        msg.contains("NOTHING of it is written back: `## T01 the bath` (gone from the section)");
    assert!(nothing, "{msg}");
}

/// A held heading gone from the plan restores the places still standing and names the one it could not, and a write that restores
/// nothing says so: no text is dropped or duplicated (451 T80).
#[test]
fn a_place_no_write_back_can_find_is_named() {
    let cut = |p: &str| {
        p.replace("## T01 part B\n\n", "")
            .replace("held body", "CHANGED body")
    };
    let (plan, msg) = split_after("split-gone-far", cut, None);
    let kept = cut(SPLIT).replace("CHANGED body", "held body");
    assert_eq!(plan, kept, "{msg}");
    let partial = msg.contains("written back: `## T01 the bath`")
        && msg.contains("NOT written back: `## T01 part B` (gone from the section)");
    assert!(partial, "{msg}");
    let legacy = Some(json!([crate::plan_text::task_sections(SPLIT)["T01"]]));
    let (plan, msg) = split_after(
        "split-legacy",
        |p| p.replace("the far part", "CHANGED far part"),
        legacy,
    );
    let unchanged = SPLIT.replace("the far part", "CHANGED far part");
    assert_eq!(plan, unchanged, "{msg}");
    let nothing = msg.contains("NOTHING of it is written back")
        && !msg.contains("the held text is written back");
    assert!(nothing, "{msg}");
}
