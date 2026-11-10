use std::collections::BTreeSet;
use std::path::Path;

use serde_json::{json, Value};

use super::{
    answered_count, apply_refusal, batch_of, batch_root, changed_lines, close_dispatches, dispatch,
    dispatches_since, drop_run, edit_refusal, launched, notes_of_manifest, open_round, oscillation,
    pair_wave, record_answer, returned, running, sentences, subject_of_path, subject_of_unit,
    subjects_of_manifest, wave_key, window_start, Dispatch,
};
use crate::shared::checks::testkit::{clone_at, dir};
use crate::shared::checks::{load, save, state_path};
use crate::shared::tool::ask;

fn git(root: &Path, args: &[&str]) {
    let said = ask(root, "git", args, "");
    assert!(said.ok(), "{args:?}: {}", said.err);
}

const MANIFEST: &str = "unit: quote-check:0105.drawing#bath abc\nowed: a reason\n";

fn req<'a>(tid: &'a str, check: &'a str, text: &'a str, root: Option<&'a Path>) -> Dispatch<'a> {
    Dispatch {
        tid,
        check,
        manifest: "/m/MANIFEST.md",
        text,
        now: 1000.0,
        root,
        freeze_ok: false,
        arbiter_ok: false,
    }
}

#[test]
fn names_read_off_units_and_paths() {
    assert_eq!(subject_of_unit("0105.drawing#note"), "q:0105");
    assert_eq!(subject_of_unit("sheet/bath"), "modal:sheet/bath");
    assert_eq!(subject_of_unit("nope"), "");
    assert_eq!(subject_of_unit("1234/x"), "modal:1234/x");
    assert_eq!(subject_of_unit("1234"), "q:1234");
    assert_eq!(
        subjects_of_manifest("unit: a:0105#x f\nunit: b:sheet/bath f\nunit: c:nope f\n"),
        ["modal:sheet/bath", "q:0105"]
    );
    assert_eq!(
        subject_of_path("research/questions/0105-x.notes.html"),
        "q:0105"
    );
    assert_eq!(
        subject_of_path("/r/research/questions/0105-x.drawing.html"),
        "q:0105"
    );
    assert_eq!(
        subject_of_path("l7r/diagram/interactive/assets/modals/sheet/bath.md"),
        "modal:sheet/bath"
    );
    assert_eq!(subject_of_path("docs/a.md"), "");
    let scoped = notes_of_manifest("ONLY the notes a, b and the blocks that carry them\n");
    assert_eq!(scoped, BTreeSet::from(["a".to_owned(), "b".to_owned()]));
    assert!(notes_of_manifest("plain").is_empty());
    let source = notes_of_manifest("# Check bundle - source x\nunit: source-reader:0248#koku-1 fp\nunit: source-reader:0248.drawing#koku-2 fp\n");
    assert_eq!(source.len(), 2);
    assert_eq!(batch_root("/a/batch-1/MANIFEST.md"), "/a");
    assert_eq!(batch_root("/a/q/MANIFEST.md"), "");
    assert_eq!(wave_key("a  b"), wave_key("a b"));
    assert_eq!(
        sentences(&["One. Two!  Three".to_owned(), String::new()]),
        ["One.", "Two!", "Three"]
    );
    assert_eq!(batch_of(None), "");
}

#[test]
fn a_dispatch_is_recorded_pending_and_counted_at_launch() {
    let mut state = json!({});
    assert_eq!(
        dispatch(&mut state, &req("t1", "quote-check", MANIFEST, None)),
        ""
    );
    let d = &state["dispatches"]["t1"];
    assert_eq!(d["check"], json!("quote-check"));
    assert_eq!(d["subjects"], json!(["q:0105"]));
    assert_eq!(d["state"], json!("pending"));
    assert_eq!(d["owed"], json!(["a reason"]));
    assert_eq!(d["quote_notes"], json!({"0105.drawing#bath": "abc"}));
    assert_eq!(d["counted"], json!(["quote-check|q:0105"]));
    assert_eq!(d["prewrite"], json!(false));
    assert_eq!(d["marks"]["read"]["quote-check|q:0105"], json!(["*"]));
    assert!(running(&state, "q:0105", 1000.0).len() == 1);
    assert!(running(&state, "q:0105", 2000.0).is_empty());
    let mut other = json!({});
    assert_eq!(
        dispatch(&mut other, &req("s", "source-reader", "no unit\n", None)),
        ""
    );
    assert_eq!(other["dispatches"]["s"]["prewrite"], json!(true));
    assert_eq!(other["dispatches"]["s"]["quote_notes"], json!({}));
    assert_eq!(
        dispatch(&mut other, &req("q", "impl-drift", MANIFEST, None)),
        ""
    );
    assert_eq!(other["dispatches"]["q"]["subjects"], json!([]));
}

fn launched_one(state: &mut Value, tid: &str, aid: &str) {
    launched(state, tid, aid, true, "", None);
}

#[test]
fn a_launch_applies_its_marks_and_a_return_counts_its_round() {
    let d = dir("returned");
    let keep = d.join("replies");
    let mut state = json!({});
    assert_eq!(
        dispatch(&mut state, &req("t1", "quote-check", MANIFEST, None)),
        ""
    );
    launched(&mut state, "nope", "ag", true, "", None);
    launched_one(&mut state, "t1", "ag1");
    let row = &state["dispatches"]["t1"];
    assert!(row.get("marks").is_none());
    assert_eq!(row["state"], json!("running"));
    assert_eq!(state["notes_read"]["quote-check|q:0105"], json!(["*"]));
    assert_eq!(state["edits"]["q:0105"], json!([]));
    let reply = "quote-check\n\nEDIT research/questions/0105-x.html\n<<<\nold\n===\nnew\n>>>\n";
    returned(&mut state, "agX", reply, Some(&keep));
    returned(&mut state, "ag1", reply, Some(&keep));
    let row = &state["dispatches"]["t1"];
    assert_eq!(row["state"], json!("returned"));
    assert_eq!(state["rounds"]["quote-check|q:0105"], json!(1));
    assert_eq!(
        state["edits"]["q:0105"],
        json!([["research/questions/0105-x.html", "old", "new"]])
    );
    assert_eq!(state["own_edits"]["quote-check|q:0105"], json!(["new"]));
    assert!(std::fs::read_to_string(row["reply"].as_str().unwrap())
        .unwrap()
        .contains("EDIT"));
    returned(&mut state, "ag1", reply, Some(&keep));
    assert_eq!(
        state["rounds"]["quote-check|q:0105"],
        json!(1),
        "a reply is counted once"
    );
    let mut fg = json!({});
    dispatch(&mut fg, &req("t2", "quote-check", MANIFEST, None));
    launched(&mut fg, "t2", "ag2", false, "a reply", None);
    assert_eq!(fg["dispatches"]["t2"]["state"], json!("returned"));
    let mut quiet = json!({"dispatches": {"t": {"aid": "a", "state": "returned", "check": "x", "subjects": []}}});
    returned(&mut quiet, "a", "   ", None);
    assert_eq!(quiet["dispatches"]["t"]["state"], json!("returned"));
    assert!(quiet.get("rounds").is_none());
}

fn repeating_state(rounds: u64, n: &str) -> Value {
    json!({
        "feature": "999-x",
        "rounds": {"quote-check|q:0105": rounds},
        "notes_read": {"quote-check|q:0105": ["*"]},
        "dispatches": {"old": {"check": "quote-check", "subjects": ["q:0105"], "state": "answered", "t": 1.0, "manifest": n}}
    })
}

#[test]
fn the_cap_refuses_a_repeat_and_an_arbiter_lifts_it() {
    let root = clone_at("cap");
    let mut state = repeating_state(2, "/m/MANIFEST.md");
    let msg = dispatch(&mut state, &req("n", "quote-check", MANIFEST, Some(&root)));
    assert!(
        msg.contains("round 3 of `quote-check` on q:0105 in this feature passes its cap of 2"),
        "{msg}"
    );
    assert!(std::fs::read_to_string(root.join(".git/arbiter-owed.json"))
        .unwrap()
        .contains("round:quote-check|q:0105@3"));
    let held = clone_at("held");
    std::fs::write(
        held.join(".git/arbiter-owed.json"),
        r#"{"cascade@1": {"kind": "cascade", "feature": "999-x"}}"#,
    )
    .unwrap();
    let msg2 = dispatch(
        &mut repeating_state(0, ""),
        &req("n", "quote-check", MANIFEST, Some(&held)),
    );
    assert!(msg2.contains("cascade@1"), "{msg2}");
    let lifted = clone_at("lifted");
    std::fs::write(
        lifted.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"continue\"}\n",
    )
    .unwrap();
    assert_eq!(
        dispatch(
            &mut repeating_state(2, ""),
            &req("n", "quote-check", MANIFEST, Some(&lifted))
        ),
        ""
    );
    let shut = clone_at("shut");
    std::fs::write(
        shut.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    let no_units = dispatch(
        &mut repeating_state(2, ""),
        &req(
            "n",
            "quote-check",
            "unit: quote-check:0105.drawing#a fp\n",
            Some(&shut),
        ),
    );
    assert!(no_units.is_empty(), "{no_units}");
    let store = shut.join(".git/record-checks");
    std::fs::create_dir_all(&store).unwrap();
    std::fs::write(
        store.join("quote-check%3A0105.json"),
        r#"{"fingerprint": "fp"}"#,
    )
    .unwrap();
    let answered_case = dispatch(
        &mut repeating_state(2, ""),
        &req(
            "n",
            "quote-check",
            "unit: quote-check:0105 fp\n",
            Some(&shut),
        ),
    );
    assert!(
        answered_case.contains("the round arbiter closed"),
        "{answered_case}"
    );
    let answered_list = clone_at("answered-list");
    std::fs::write(
        answered_list.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    std::fs::create_dir_all(answered_list.join(".git/record-checks")).unwrap();
    std::fs::write(
        answered_list.join(".git/record-checks/quote-check%3A0105.json"),
        r#"{"answered": ["fp"]}"#,
    )
    .unwrap();
    assert!(dispatch(
        &mut repeating_state(2, ""),
        &req(
            "n",
            "quote-check",
            "unit: quote-check:0105 fp\n",
            Some(&answered_list)
        )
    )
    .contains("closed"));
    let rebased = clone_at("rebased");
    std::fs::write(
        rebased.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    let mut s = repeating_state(2, "");
    assert_eq!(
        dispatch(
            &mut s,
            &req(
                "n",
                "quote-check",
                "unit: quote-check:0105 moved\n",
                Some(&rebased)
            )
        ),
        ""
    );
    assert_eq!(
        s["rebased"]["quote-check|q:0105"],
        json!({"fp": "moved", "n": 2})
    );
    let mut s2 = repeating_state(3, "");
    s2["rebased"] = json!({"quote-check|q:0105": {"fp": "moved", "n": 3}});
    assert_eq!(
        dispatch(
            &mut s2,
            &req(
                "n",
                "quote-check",
                "unit: quote-check:0105 moved\n",
                Some(&rebased)
            )
        ),
        ""
    );
    let mut s3 = repeating_state(5, "");
    s3["rebased"] = json!({"quote-check|q:0105": {"fp": "moved", "n": 0}});
    assert!(dispatch(
        &mut s3,
        &req(
            "n",
            "quote-check",
            "unit: quote-check:0105 moved\n",
            Some(&rebased)
        )
    )
    .contains("passes its cap of 2"));
    let mut escaped = repeating_state(2, "");
    let mut with_escape = req("n", "quote-check", MANIFEST, Some(&root));
    with_escape.arbiter_ok = true;
    assert_eq!(dispatch(&mut escaped, &with_escape), "");
}

#[test]
fn a_later_batch_starts_its_own_count() {
    let root = clone_at("new-cause");
    git(
        &root,
        &[
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x",
        ],
    );
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let mut s = repeating_state(2, "");
    s["round_batch"] = json!({"quote-check|q:0105": "an-earlier-batch"});
    assert_eq!(
        dispatch(&mut s, &req("n", "quote-check", MANIFEST, Some(&root))),
        ""
    );
    assert_eq!(s["rebased"]["quote-check|q:0105"]["cause"], json!(true));
    let mut still = repeating_state(2, "");
    still["round_batch"] = json!({"quote-check|q:0105": "an-earlier-batch"});
    still["dispatches"]["open"] =
        json!({"check": "x", "subjects": ["q:0105"], "state": "running", "t": 1000.0});
    assert_ne!(
        dispatch(&mut still, &req("n", "quote-check", MANIFEST, Some(&root))),
        ""
    );
}

#[test]
fn a_round_running_refuses_the_same_check_and_a_batch_is_one_round() {
    let mut running_state = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0, "manifest": "/m/MANIFEST.md"}}});
    let msg = dispatch(&mut running_state, &req("n", "quote-check", MANIFEST, None));
    assert!(msg.contains("is already in q:0105's round"), "{msg}");
    let mut freeze = req("n", "quote-check", MANIFEST, None);
    freeze.freeze_ok = true;
    assert_eq!(dispatch(&mut running_state.clone(), &freeze), "");
    let mut sibling = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0, "manifest": "/r/batch-1/MANIFEST.md"}}});
    let mut second = req("n", "quote-check", MANIFEST, None);
    second.manifest = "/r/batch-2/MANIFEST.md";
    assert_eq!(dispatch(&mut sibling, &second), "");
    assert_eq!(sibling["dispatches"]["n"]["counted"], json!([]));
    let mut disjoint = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0, "manifest": "/m/M.md", "notes": ["x"]}}});
    let note_scoped =
        "ONLY the notes y and the blocks that carry them\nunit: quote-check:0105#y fp\n";
    assert_eq!(
        dispatch(&mut disjoint, &req("n", "quote-check", note_scoped, None)),
        ""
    );
    assert_eq!(disjoint["dispatches"]["n"]["notes"], json!(["y"]));
    let mut overlap = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0, "notes": ["y"]}}});
    assert_ne!(
        dispatch(&mut overlap, &req("n", "quote-check", note_scoped, None)),
        ""
    );
    let mut pending_only = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "pending", "t": 1000.0}}});
    assert_eq!(
        dispatch(&mut pending_only, &req("n", "quote-check", MANIFEST, None)),
        ""
    );
    let mut wave = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "pending", "t": 100.0, "wave": "k"}}});
    assert_eq!(open_round(&wave, "q:0105", 1000.0).len(), 1);
    assert!(open_round(&wave, "q:0105", 100_000.0).is_empty());
    wave["dispatches"]["a"]["wave"] = json!(null);
    assert!(open_round(&wave, "q:0105", 1000.0).is_empty());
}

#[test]
fn first_looks_and_fresh_readings_are_no_repeat() {
    let root = clone_at("fresh");
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    std::fs::write(
        root.join("research/questions/0105-x.html"),
        "<p>one fact. A brand new sentence.</p>",
    )
    .unwrap();
    let key = |s: &str| {
        crate::shared::sha1::hex(s.as_bytes())
            .chars()
            .take(12)
            .collect::<String>()
    };
    let mut own = json!({"seen": {"quote-check|q:0105": [key("one fact.")]}, "own_edits": {"quote-check|q:0105": ["A brand   new sentence."]}, "rounds": {"quote-check|q:0105": 2}, "notes_read": {"quote-check|q:0105": ["*"]}});
    assert_ne!(
        dispatch(&mut own, &req("n", "quote-check", MANIFEST, Some(&root))),
        ""
    );
    let mut first = json!({"seen": {"quote-check|q:0105": [key("one fact.")]}, "rounds": {"quote-check|q:0105": 2}, "notes_read": {"quote-check|q:0105": ["*"]}});
    assert_eq!(
        dispatch(&mut first, &req("n", "quote-check", MANIFEST, Some(&root))),
        ""
    );
    assert_eq!(first["dispatches"]["n"]["counted"], json!([]));
    let mut seen_all = json!({"seen": {"quote-check|q:0105": [key("one fact."), key("A brand new sentence.")]}, "rounds": {"quote-check|q:0105": 2}, "notes_read": {"quote-check|q:0105": ["*"]}});
    assert_ne!(
        dispatch(
            &mut seen_all,
            &req("n", "quote-check", MANIFEST, Some(&root))
        ),
        ""
    );
    let scoped = "ONLY the notes y and the blocks that carry them\nunit: quote-check:0105#y f\n";
    let mut read_other =
        json!({"rounds": {"quote-check|q:0105": 2}, "notes_read": {"quote-check|q:0105": ["x"]}});
    assert_eq!(
        dispatch(
            &mut read_other,
            &req("n", "quote-check", scoped, Some(&root))
        ),
        ""
    );
    let mut read_star =
        json!({"rounds": {"quote-check|q:0105": 2}, "notes_read": {"quote-check|q:0105": ["*"]}});
    assert_ne!(
        dispatch(
            &mut read_star,
            &req("n", "quote-check", scoped, Some(&root))
        ),
        ""
    );
    let mut flying_first = json!({"rounds": {"quote-check|q:0105": 2}, "dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "pending", "t": 1000.0, "notes": ["x"]}}});
    assert_eq!(
        dispatch(
            &mut flying_first,
            &req("n", "quote-check", scoped, Some(&root))
        ),
        ""
    );
    let mut flying_whole = json!({"rounds": {"quote-check|q:0105": 2}, "dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "pending", "t": 1000.0}}});
    assert_ne!(
        dispatch(
            &mut flying_whole,
            &req("n", "quote-check", scoped, Some(&root))
        ),
        ""
    );
    let mut none_read = json!({"rounds": {"quote-check|q:0105": 2}});
    assert_ne!(
        dispatch(
            &mut none_read,
            &req("n", "quote-check", scoped, Some(&root))
        ),
        ""
    );
}

#[test]
fn a_wave_agent_is_paired_by_its_prompt() {
    let d = dir("wave");
    let transcript = d.join("t.jsonl");
    let prompt = "The prompt  text page 1";
    std::fs::write(
        &transcript,
        format!(
            "not json\n{}\n{}\n{}\n{}\n",
            json!({"message": {"role": "assistant", "content": "x"}}),
            json!({"message": {"role": "user", "content": format!("frame The computed task text follows: {prompt}")}}),
            json!({"message": {"role": "user", "content": [{"text": "a"}, 3]}}),
            json!({"message": {"role": "user", "content": 5}})
        ),
    )
    .unwrap();
    let flat = "The prompt text page 1";
    let key = wave_key(flat);
    let len = flat.chars().count();
    let long = format!("{flat} and more");
    let mut state = json!({"dispatches": {
        "w1": {"wave": key, "wave_len": len, "state": "pending", "t": 2.0, "check": "c"},
        "w2": {"wave": wave_key(&long), "wave_len": long.chars().count(), "state": "pending", "t": 1.0, "check": "c"},
        "w3": {"check": "c"}
    }});
    pair_wave(&mut state, "", &transcript.to_string_lossy());
    assert!(state["dispatches"]["w1"].get("aid").is_none());
    pair_wave(&mut state, "ag1", &transcript.to_string_lossy());
    assert_eq!(state["dispatches"]["w1"]["aid"], json!("ag1"));
    assert_eq!(state["dispatches"]["w1"]["state"], json!("running"));
    pair_wave(&mut state, "ag1", &transcript.to_string_lossy());
    state["dispatches"]["w1"]["state"] = json!("returned");
    state["dispatches"]["w1"]["aid"] = json!("other");
    pair_wave(&mut state, "ag2", &transcript.to_string_lossy());
    assert_eq!(state["dispatches"]["w1"]["aid"], json!("ag2"));
    state["dispatches"]["w1"]["state"] = json!("returned");
    state["dispatches"]["w1"]["reply"] = json!("r");
    state["dispatches"]["w1"]["aid"] = json!("x");
    pair_wave(&mut state, "ag3", &transcript.to_string_lossy());
    assert_eq!(state["dispatches"]["w1"]["aid"], json!("x"));
    pair_wave(&mut state, "ag4", "/no/such/transcript");
}

#[test]
fn drop_run_and_record_answer_rewrite_the_state_under_its_lock() {
    let root = clone_at("drop");
    let cwd = root.to_string_lossy().into_owned();
    drop_run(&cwd, "wave:1");
    let path = state_path(&cwd).unwrap();
    save(&path, &json!({"dispatches": {"wave:1:a": {}, "keep": {"check": "quote-check", "subjects": ["q:0105"], "state": "running"}}})).unwrap();
    drop_run(&cwd, "wave:1");
    assert!(load(&path)["dispatches"].get("wave:1:a").is_none());
    record_answer(
        &root,
        "quote-check",
        &["quote-check:0105#a".to_owned(), "x:nothing".to_owned()],
    );
    assert_eq!(
        load(&path)["dispatches"]["keep"]["state"],
        json!("answered")
    );
    record_answer(&root, "quote-check", &[]);
    let gone = clone_at("gone");
    record_answer(&gone, "quote-check", &[]);
    drop_run("/nonexistent-l7r", "x");
    let mut research = json!({"dispatches": {"a": {"check": "modal-research", "subjects": ["s"], "state": "running"}, "b": {"check": "*", "subjects": ["s"], "state": "running"}, "c": {"check": "x", "subjects": ["other"], "state": "running"}, "d": {"check": "x", "subjects": ["s"], "state": "answered"}}});
    assert_eq!(
        answered_count(&mut research, "modal-gaps", &["s".to_owned()]),
        2
    );
    assert_eq!(answered_count(&mut research, "*", &["other".to_owned()]), 1);
    assert_eq!(answered_count(&mut json!({}), "x", &[]), 0);
}

#[test]
fn an_edit_is_frozen_while_its_checks_run() {
    let path = "research/questions/0105-x.html";
    let mut state = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0}}});
    assert_eq!(edit_refusal(&state, "docs/a.md", "o", "n", 1000.0), "");
    assert_eq!(
        edit_refusal(&state, "research/questions/0200-x.html", "o", "n", 1000.0),
        ""
    );
    assert!(edit_refusal(&state, path, "o", "n", 1000.0)
        .contains("frozen while its checks run (quote-check)"));
    assert!(
        edit_refusal(&state, path, "o", "n", 1000.0 + 90.0 * 60.0 + 1.0)
            .contains("1 silent past 90 minutes")
    );
    state["dispatches"]["a"]["state"] = json!("returned");
    assert!(edit_refusal(&state, path, "o", "n", 1000.0).contains("returned no edit"));
    state["edits"] = json!({"q:0105": [[path, "the old words", "the new words"], ["bad"]]});
    assert_eq!(edit_refusal(&state, path, "old", "new words", 1000.0), "");
    assert!(edit_refusal(&state, path, "old", "other", 1000.0).contains("none of the 1 edit(s)"));
    assert!(edit_refusal(&state, path, "", "", 1000.0).contains("none of the 1"));
    assert!(edit_refusal(&state, path, "absent", "x", 1000.0).contains("none of the"));
}

#[test]
fn make_apply_edits_is_read_from_its_reply() {
    let d = dir("apply");
    let reply = d.join("r.md");
    std::fs::write(&reply, "EDIT research/questions/0105-x.html\n<<<\nold\n===\nnew\n>>>\nEDIT docs/a.md\n<<<\na\n===\nb\n>>>\n").unwrap();
    let cmd = format!("make apply-edits FROM={}", reply.display());
    let quoted = format!("make apply-edits FROM=\"{}\"", reply.display());
    let mut state = json!({});
    assert_eq!(apply_refusal(&state, "make quick", 1000.0), "");
    assert_eq!(apply_refusal(&state, &cmd, 1000.0), "");
    state = json!({"dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0}}});
    assert!(apply_refusal(&state, &cmd, 1000.0).contains("frozen"));
    state["dispatches"]["a"]["state"] = json!("returned");
    assert!(apply_refusal(&state, &quoted, 1000.0).contains("not one its round's checks returned"));
    state["edits"] = json!({"q:0105": [["research/questions/0105-x.html", "old", "new"]]});
    assert_eq!(apply_refusal(&state, &cmd, 1000.0), "");
    state["edits"] = json!({"q:0105": [["other", "the old text", "the new text"]]});
    assert_eq!(apply_refusal(&state, &cmd, 1000.0), "");
}

#[test]
fn oscillation_finds_a_block_that_came_back() {
    let v = |x: &str| vec![x.to_owned()];
    assert_eq!(oscillation(&[v("a"), v("b")]), "");
    let a = "the first block about a bath and its water";
    let b = "another block entirely different words appear here now";
    let back = oscillation(&[v(a), v(b), v(a)]);
    assert!(back.starts_with("the first block"));
    assert_eq!(
        oscillation(&[v(b), v(b), v(a)]),
        "",
        "the block stood just before"
    );
    assert_eq!(oscillation(&[v(a), v(a), v(a)]), "");
    assert_eq!(oscillation(&[v("short"), v(b), v("short")]), "");
    let keep = vec![a.to_owned(), "z y x w v u".to_owned()];
    assert_eq!(
        oscillation(&[keep, v(&format!("{a} extra")), v(a)]),
        "",
        "it never left"
    );
}

#[test]
fn the_cascade_counts_dispatches_and_changed_lines() {
    let mut root = clone_at("cascade-lines");
    git(
        &root,
        &[
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x",
        ],
    );
    assert_eq!(window_start(&root), 0.0, "no origin yet");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    assert!(window_start(&root) > 0.0);
    std::fs::write(root.join("a.txt"), "1\n2\n").unwrap();
    std::fs::write(root.join("b.json"), "1\n").unwrap();
    git(&root, &["add", "-A"]);
    assert_eq!(changed_lines(&root), 2);
    let state = json!({"dispatches": {"a": {"t": 10.0}, "b": {"t": 1.0}, "c": {"t": 10.0, "prewrite": true}}});
    assert_eq!(dispatches_since(&state, 5.0), 1);
    root = clone_at("no-commit");
    assert_eq!(changed_lines(&root), 0);
}

#[test]
fn a_silent_check_is_closed_by_name_or_silence() {
    let mut state = json!({"dispatches": {
        "a": {"check": "c", "subjects": ["s"], "state": "running", "t": -10000.0, "aid": "ag1"},
        "b": {"check": "c", "subjects": ["s"], "state": "running", "t": 900.0, "aid": "ag2"},
        "c": {"check": "c", "subjects": ["other"], "state": "running", "t": 0.0}
    }});
    let c = close_dispatches(&mut state, "s", "reason", 3000.0, "");
    assert_eq!((c.closed, c.still_running), (1, 1));
    assert_eq!(state["dispatches"]["a"]["closed"], json!("reason"));
    let c = close_dispatches(&mut state, "s", "r2", 950.0, "ag2");
    assert_eq!((c.closed, c.still_running), (1, 0));
    let empty = close_dispatches(&mut json!({}), "s", "r", 1.0, "");
    assert_eq!((empty.closed, empty.still_running), (0, 0));
}
