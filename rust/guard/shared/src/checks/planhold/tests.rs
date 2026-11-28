use std::path::Path;

use serde_json::{json, Value};

use super::{hold, launched, live, purge, refusal, restore, returned, snapshot, tree_key};
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
    hold(&mut state, "t0", "no bundle", 1.0, None);
    assert_eq!(state, json!({}));
    let prompt = format!("Read {}/MANIFEST.md", bundle.display());
    hold(&mut state, "t1", &prompt, 1.5, None);
    assert_eq!(
        state["plan_holds"]["t1"],
        json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1.5, "state": "pending"})
    );
    // a task's bundle keyed by its tree (451 T288): `plan-<feature>-<task>-<8 hex>` takes the same hold
    let keyed = format!("Read {}/plan-900-a-T01-0123abcd/MANIFEST.md", d.display());
    hold(&mut state, "t5", &keyed, 1.5, None);
    assert_eq!(
        state["plan_holds"]["t5"],
        json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1.5, "state": "pending"})
    );
    // the tree its call ran in, the one its write-back runs in (451 T123)
    hold(&mut state, "t4", &prompt, 1.5, Some(&d));
    let root = state["plan_holds"]["t4"]["root"].clone();
    assert_eq!(root, json!(d.to_string_lossy()));
    let blocks = d.join("plan-900-a-blocks-x");
    std::fs::create_dir_all(&blocks).unwrap();
    // the key as plan.md holds it, a quote, a backslash and a non-ASCII letter kept (461 T70); a comment with no digest is no key
    let sha = "0123abcd".repeat(8);
    let text = format!("<!-- block \"## A \"q\"\" sha256 {sha} -->\nnot one\n<!-- block \"x\" sha256\n<!-- block \"k\\z caf\u{e9}\" sha256 {sha} -->\n");
    std::fs::write(blocks.join("blocks.md"), text).unwrap();
    hold(
        &mut state,
        "t2",
        &format!("x {}/MANIFEST.md y", blocks.display()),
        2.0,
        None,
    );
    assert_eq!(
        state["plan_holds"]["t2"]["blocks"],
        json!(["## A \"q\"", "k\\z caf\u{e9}"])
    );
    hold(
        &mut state,
        "t3",
        &format!("{}-gone/plan-900-a-blocks-y/MANIFEST.md", d.display()),
        2.0,
        None,
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
    let mut state = json!({"plan_holds": {"a": {"state": "pending", "t": 0.0}, "b": {"state": "pending", "t": 950.0}, "c": {"state": "running", "t": 0.0}, "d": {"state": "running", "t": -1000.0}}});
    purge(&mut state, 1000.0);
    // a running hold past HOLD_MAX_S goes too (451 T489)
    let keys: Vec<&String> = state["plan_holds"].as_object().unwrap().keys().collect();
    assert_eq!(keys, ["b", "c"]);
    purge(&mut json!({}), 1.0);
}

#[test]
fn a_snapshot_is_written_back_when_held_text_changes() {
    let root = clone_at("restore");
    feature(&root);
    let mut state = json!({"plan_holds": {"h1": running("T01", &[], 900.0), "dead": running("T01", &[], 0.0), "p": {"feature": "x", "state": "pending", "t": 999.0}}});
    snapshot(&mut state, None, 1000.0);
    assert!(state.get("plan_snaps").is_none());
    snapshot(&mut state, Some(&root), 1000.0);
    assert!(state["plan_snaps"][tree_key(&root)]["h1"][0]
        .as_str()
        .unwrap()
        .contains("held body"));
    assert_eq!(state["plan_holds"].as_object().unwrap().len(), 3);
    // kept once a hold and tree (451 T387): a later call's start takes nothing, and an unchanged end keeps it while the hold is open
    let kept = state["plan_snaps"].clone();
    snapshot(&mut state, Some(&root), 1500.0);
    assert_eq!(state["plan_snaps"], kept);
    assert_eq!(restore(&mut state, Some(&root), "unrelated"), "");
    let unchanged = restore(&mut state, Some(&root), "call");
    assert_eq!(unchanged, "");
    assert_eq!(state["plan_snaps"], kept);
    snapshot(&mut state, Some(&root), 1000.0);
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
    snapshot(&mut state, Some(&root), 1000.0);
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
    snapshot(&mut one_same, Some(&root), 1000.0);
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
    snapshot(&mut renamed, Some(&root), 1000.0);
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
    let check = |tool: &str, ti: Value, at: f64| refusal(&state, Some(&root), tool, &ti, at);
    assert_eq!(refusal(&state, None, "Edit", &json!({}), 1.0), "");
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        1000.0
    )
    .contains("(agent ag)"));
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "body of the"}),
        1000.0
    )
    .contains("running"));
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": "other text"}),
            1000.0
        ),
        ""
    );
    assert_eq!(
        check("Edit", json!({"file_path": plan, "old_string": ""}), 1000.0),
        ""
    );
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": "/elsewhere", "old_string": "held body"}),
            1000.0
        ),
        ""
    );
    let writes = check(
        "Write",
        json!({"file_path": plan, "content": "new"}),
        1000.0,
    );
    assert!(writes.contains("T01's section"));
    let keep = format!("x{PLAN}");
    assert_eq!(
        check("Write", json!({"file_path": plan, "content": keep}), 1000.0),
        ""
    );
    assert!(check(
        "MultiEdit",
        json!({"file_path": plan, "old_string": "held body"}),
        1000.0
    )
    .contains("running"));
    assert_eq!(check("Bash", json!({"command": "ls"}), 1000.0), "");
    assert_eq!(
        check(
            "Bash",
            json!({"command": "sed -i s/a/b/ specs/900-a/plan.md"}),
            1000.0
        ),
        ""
    );
    assert!(check(
        "Bash",
        json!({"command": "sed -i 's/## T01 the bath/x/' specs/900-a/plan.md"}),
        1000.0
    )
    .contains("running"));
    assert!(check(
        "Bash",
        json!({"command": "tee specs/900-a/plan.md # held body of the section stands here"}),
        1000.0
    )
    .contains("running"));
    assert!(check("Bash", json!({"command": "python3 -c 'open(\"x\", \"w\")' specs/900-a/plan.md \"held body of the\""}), 1000.0).contains("running"));
    assert_eq!(check("Read", json!({"file_path": plan}), 1000.0), "");
    let late = check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        3000.0,
    );
    // a dead hold refuses nothing and offers no escape: `purge` drops it at a hooked call's start (451 T489, T496)
    assert_eq!(late, "");
    let pending = json!({"plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 999.0, "state": "pending"}}});
    let said = refusal(
        &pending,
        Some(&root),
        "Edit",
        &json!({"file_path": plan, "old_string": "held body"}),
        1000.0,
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
    )
    .contains("1 block(s)"));
    assert_eq!(
        refusal(&json!({}), Some(&root), "Edit", &json!({}), 1.0),
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
        (dead, shared.as_str(), false, false),
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
            refusal(&state, Some(&root), "Bash", &ti, 1000.0).is_empty() == *refused
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
    snapshot(&mut state, Some(&root), 1000.0);
    if let Some(b) = before {
        state["plan_snaps"][tree_key(&root)]["h"] = b;
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

/// A hold is the tree's it was taken in (451 T123): a clone's worktrees share its check state, so a hold taken in the clone was
/// snapshotted, written back and refused on a worktree's own plan, and a snapshot under no id taken in one tree was written over the
/// other's plan (measured 2026-11-21, `/tmp/t123/measure.sh`). A hold that recorded no root, taken before T123, reaches every tree.
#[test]
fn a_hold_is_written_back_and_refused_in_its_own_tree_alone() {
    let clone = clone_at("tree-clone");
    let other = clone_at("tree-other");
    let budget = "8. **The budget.** One landing.";
    let ours = format!("# plan\n\n## T01 the bath\n\nheld body of the section stands here\n\n{budget}\n\n## T02 other\n\nother text\n\n{budget}\n");
    let theirs = ours.replace("held body", "the other tree's body");
    for (root, plan) in [(&clone, &ours), (&other, &theirs)] {
        std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
        std::fs::write(root.join("specs/900-a/plan.md"), plan).unwrap();
    }
    let read = |root: &Path| std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap();
    let mut rooted = running("T01", &[], 900.0);
    rooted["root"] = json!(clone.to_string_lossy());
    let legacy = running("T01", &[], 900.0);
    // the snapshot: none in the other tree, one in the clone
    let mut state = json!({"plan_holds": {"h": rooted}});
    snapshot(&mut state, Some(&other), 1000.0);
    let none_there = state.get("plan_snaps").is_none();
    assert!(none_there, "{state}");
    snapshot(&mut state, Some(&clone), 1000.0);
    let taken = state["plan_snaps"][tree_key(&clone)]["h"][0]
        .as_str()
        .unwrap_or("")
        .contains("held body");
    assert!(taken, "{state}");
    // the write-back: the clone's snapshot under no id is not written over the other tree's plan, and is in the clone
    let mut cross = state.clone();
    let said = restore(&mut cross, Some(&other), "");
    let there = read(&other);
    assert!(said.is_empty() && there == theirs, "{said}");
    std::fs::write(
        clone.join("specs/900-a/plan.md"),
        ours.replace("held body", "CHANGED body"),
    )
    .unwrap();
    let said = restore(&mut state, Some(&clone), "");
    let restored = said.contains("the held text is written back") && read(&clone) == ours;
    assert!(restored, "{said}");
    // a hold with no root, today's: snapshotted and written back in the other tree
    let mut old = json!({"plan_holds": {"h": legacy}});
    snapshot(&mut old, Some(&other), 1000.0);
    std::fs::write(
        other.join("specs/900-a/plan.md"),
        theirs.replace("the other", "CHANGED other"),
    )
    .unwrap();
    let said = restore(&mut old, Some(&other), "l");
    let restored = said.contains("the held text is written back") && read(&other) == theirs;
    assert!(restored, "{said}");
    // the refusal judges the plan of the hold's tree: the other tree's own plan is not held, the clone's is from any tree
    let rooted_state = json!({"plan_holds": {"h": state["plan_holds"]["h"].clone()}});
    let edit = |root: &Path, old: &str| json!({"file_path": root.join("specs/900-a/plan.md"), "old_string": old});
    let own = refusal(
        &rooted_state,
        Some(&other),
        "Edit",
        &edit(&other, "the other tree's body"),
        1000.0,
    );
    let held = refusal(
        &rooted_state,
        Some(&other),
        "Edit",
        &edit(&clone, "held body"),
        1000.0,
    );
    let today = refusal(
        &old,
        Some(&other),
        "Edit",
        &edit(&other, "the other tree's body"),
        1000.0,
    );
    let judged = own.is_empty() && !held.is_empty() && !today.is_empty();
    assert!(judged, "{own} | {held} | {today}");
    // a shell write in the clone: a held heading refuses it and shared text passes, the write-back behind it; one from another tree
    // the clone's hold does not judge - by a relative path it writes that tree's own plan
    let shared =
        json!({"command": format!("printf '%s\\n' '{budget}' | tee -a specs/900-a/plan.md")});
    let heading = json!({"command": "sed -i '/## T01 the bath/a x' specs/900-a/plan.md"});
    let shell = |root: &Path, ti: &Value| refusal(&rooted_state, Some(root), "Bash", ti, 1000.0);
    let (here_heading, here_shared) = (shell(&clone, &heading), shell(&clone, &shared));
    let (there_heading, there_shared) = (shell(&other, &heading), shell(&other, &shared));
    let in_clone = !here_heading.is_empty() && here_shared.is_empty();
    assert!(in_clone, "{here_heading} | {here_shared}");
    let in_other = there_heading.is_empty() && there_shared.is_empty();
    assert!(in_other, "{there_heading} | {there_shared}");
}

/// A hold is the tree's its bundle was built from (451 T295): a builder's dispatch runs with the session's clone as its cwd while
/// its bundle is built from its worktree's plan, so the hold took the clone as its tree - a `make task-add` in the clone was blamed
/// for changing the worktree's reviewed section and the clone's own text of it written back over the clone's plan (seen
/// 2026-11-26, T292's review; the MANIFEST's `Built from the tree` line is 451 T257's). A bundle naming no tree keeps the call's.
#[test]
fn a_hold_is_the_tree_its_bundle_was_built_from() {
    let clone = clone_at("built-clone");
    let tree = clone_at("built-tree");
    let ours = PLAN.to_owned();
    let theirs = PLAN.replace("held body", "the worktree's body");
    for (root, plan) in [(&clone, &ours), (&tree, &theirs)] {
        std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
        std::fs::write(root.join("specs/900-a/plan.md"), plan).unwrap();
    }
    let d = dir("built-bundle");
    let bundle = d.join("plan-900-a-T01");
    std::fs::create_dir_all(&bundle).unwrap();
    let prompt = format!("Read {}/MANIFEST.md", bundle.display());
    let manifest = |text: &str| std::fs::write(bundle.join("MANIFEST.md"), text).unwrap();
    // no MANIFEST, or one naming no tree: the call's tree
    let mut state = json!({});
    hold(&mut state, "a", &prompt, 990.0, Some(&clone));
    manifest("# Plan review bundle\n\nno tree named\n");
    hold(&mut state, "b", &prompt, 990.0, Some(&clone));
    let want = json!(clone.to_string_lossy());
    for id in ["a", "b"] {
        assert_eq!(state["plan_holds"][id]["root"], want, "{id}");
    }
    // the tree the bundle was built from, whatever tree the dispatch ran in - and with none
    manifest(&format!(
        "# Plan review bundle\n\nBuilt from the tree `{}`: record the verdict there, by the command below (451 T257).\n",
        tree.display()
    ));
    let mut state = json!({});
    hold(&mut state, "h", &prompt, 990.0, Some(&clone));
    hold(&mut state, "n", &prompt, 990.0, None);
    let want = json!(tree.to_string_lossy());
    for id in ["h", "n"] {
        assert_eq!(state["plan_holds"][id]["root"], want, "{id}");
    }
    state["plan_holds"]
        .as_object_mut()
        .unwrap()
        .shift_remove("n");
    launched(&mut state, "h", "ag");
    // a call in the clone that changes the clone's own section: nothing snapshotted, nothing blamed, nothing written back
    snapshot(&mut state, Some(&clone), 1000.0);
    assert!(state.get("plan_snaps").is_none(), "{state}");
    let changed = ours.replace("held body", "the clone's own edit");
    std::fs::write(clone.join("specs/900-a/plan.md"), &changed).unwrap();
    let said = restore(&mut state, Some(&clone), "c");
    let kept = std::fs::read_to_string(clone.join("specs/900-a/plan.md")).unwrap();
    assert!(said.is_empty() && kept == changed, "{said}");
    // a call in the worktree that changes the reviewed section is written back there
    snapshot(&mut state, Some(&tree), 1000.0);
    std::fs::write(
        tree.join("specs/900-a/plan.md"),
        theirs.replace("the worktree's body", "CHANGED"),
    )
    .unwrap();
    let said = restore(&mut state, Some(&tree), "w");
    let back = std::fs::read_to_string(tree.join("specs/900-a/plan.md")).unwrap();
    let restored = said.contains("the held text is written back") && back == theirs;
    assert!(restored, "{said}");
}
