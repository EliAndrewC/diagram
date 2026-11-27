//! `pool-idle-hooks` (feature 451 T313): a coordinator's stop over a free pool tree and a READY entry is held, and each case where
//! it must not be - a subagent, no clone, no pool, the count reached, a waiting queue, an unread queue, the escape - passes.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{judge, refusal, Said, GUARD};
use crate::protocol::{run, Event};
use crate::shared::builder_queue::Idle;
use crate::shared::tempdir::TempDir;

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// A clone whose pool has one tree held (451 T5) and one free, and whose feature 451 queues `queue`.
fn world(tag: &str, queue: &str) -> (TempDir, PathBuf) {
    let dir = TempDir::new(&format!("guard-pool-idle-{tag}"));
    let clone = dir.join("c");
    put(&clone.join("specs/451-x/tasks.md"), "- [ ] T3 open\n");
    put(&clone.join("specs/451-x/queue.txt"), queue);
    std::fs::create_dir_all(dir.join("c-b1")).unwrap();
    let pool = json!({"trees": [
        {"tree": dir.join("c-b0"), "feature": "451", "tasks": ["T5"], "since": ""},
        {"tree": dir.join("c-b1"), "feature": "", "tasks": [], "since": ""},
    ]});
    put(&clone.join(".git/builder-pool.json"), &pool.to_string());
    (dir, clone)
}

fn stop(message: &str) -> Value {
    json!({"hook_event_name": "Stop", "last_assistant_message": message})
}

#[test]
fn a_stop_over_a_free_tree_and_a_ready_entry_is_held_with_the_one_command() {
    let (dir, clone) = world("held", "T3 fix crates=rust/guard files=-\n");
    let said = judge(&stop("Two builders are running."), Some(&clone), 3);
    let idle = Idle {
        tree: dir.join("c-b1"),
        tasks: "451 T3".to_owned(),
        command: "make builder-brief T=T3 F=451 KIND=fix CRATE=\"rust/guard\" ENTRY=1".to_owned(),
        flag: String::new(),
        unlisted: Vec::new(),
    };
    assert_eq!(said, Said::Held(idle));
    let want = format!(
        "pool-idle: {} is free and 451 T3 is READY, overlapping no task in flight. Hand it out before this turn ends:\n  make builder-brief T=T3 F=451 KIND=fix CRATE=\"rust/guard\" ENTRY=1\nOr start a line of your final message with: POOL_IDLE_OK: <why not, two words or more>\n",
        dir.join("c-b1").display()
    );
    assert_eq!(refusal(&said), Some(want));
}

#[test]
fn a_subagent_no_clone_the_count_reached_and_a_waiting_or_unread_queue_pass() {
    let (_dir, clone) = world("quiet", "T3 fix crates=rust/guard files=-\n");
    // a builder or any subagent
    let mut sub = stop("done");
    sub["agent_id"] = json!("a1");
    assert_eq!(judge(&sub, Some(&clone), 3), Said::Quiet);
    // a session with no clone, and a clone with no pool
    assert_eq!(judge(&stop("done"), None, 3), Said::Quiet);
    assert_eq!(
        judge(&stop("done"), Some(&clone.join("specs")), 3),
        Said::Quiet
    );
    // the settled count reached: one tree is held
    assert_eq!(judge(&stop("done"), Some(&clone), 1), Said::Quiet);
    // the queue's one entry waits on the GM; the one READY entry runs alone and a tree is held
    for waits in ["GM", "alone"] {
        put(
            &clone.join("specs/451-x/queue.txt"),
            &format!("T3 fix files=- waits={waits}\n"),
        );
        assert_eq!(judge(&stop("done"), Some(&clone), 3), Said::Quiet);
    }
    // a malformed line holds nobody: said for the record
    put(&clone.join("specs/451-x/queue.txt"), "T3 mend files=-\n");
    let said = judge(&stop("done"), Some(&clone), 3);
    assert_eq!(refusal(&said), None);
    assert!(
        format!("{said:?}").starts_with("Unread(\"specs/451-x/queue.txt line 1: `mend` is no kind")
    );
}

#[test]
fn the_escape_is_a_line_of_the_final_message_with_a_reason() {
    let (_dir, clone) = world("escape", "T3 fix crates=rust/guard files=-\n");
    let escaped = judge(
        &stop("Stopping here.\n  POOL_IDLE_OK: the next entries wait on the GM\n"),
        Some(&clone),
        3,
    );
    assert_eq!(
        escaped,
        Said::Escaped("the next entries wait on the GM".to_owned())
    );
    assert_eq!(refusal(&escaped), None);
    let quoted = judge(
        &stop("POOL_IDLE_OK=\"held for a measurement\""),
        Some(&clone),
        3,
    );
    assert_eq!(quoted, Said::Escaped("held for a measurement".to_owned()));
    // no reason, or one word: held, with the form
    for bare in ["POOL_IDLE_OK:", "POOL_IDLE_OK: later"] {
        let said = judge(&stop(bare), Some(&clone), 3);
        assert_eq!(said, Said::NoReason);
        assert!(refusal(&said).unwrap().starts_with(
            "pool-idle: POOL_IDLE_OK with no reason. Start a line with: POOL_IDLE_OK: <why"
        ));
    }
    // a mention in a sentence is no escape
    let mention = judge(
        &stop("I did not write POOL_IDLE_OK: the tree is simply free"),
        Some(&clone),
        3,
    );
    assert!(matches!(mention, Said::Held(_)));
    // the token starts its line: after a bullet or in backticks it is not taken, as the block says
    for marked in [
        "- POOL_IDLE_OK: the next entries wait on the GM",
        "`POOL_IDLE_OK: the next entries wait on the GM`",
    ] {
        let said = judge(&stop(marked), Some(&clone), 3);
        assert!(matches!(said, Said::Held(_)));
        assert!(refusal(&said)
            .unwrap()
            .contains("Or start a line of your final message with: POOL_IDLE_OK: "));
    }
}

#[test]
fn the_guard_blocks_a_stop_and_records_each_verdict() {
    crate::shared::log::quiet();
    let (_dir, clone) = world("run", "T3 fix crates=rust/guard files=-\n");
    crate::shared::env::set("POOL_IDLE_ROOT", &clone);
    let ask = |message: &str| {
        let mut event = Event {
            name: "Stop".to_owned(),
            input: stop(message),
        };
        run(&mut event, &[GUARD]).stdout
    };
    let held = ask("done");
    assert!(
        held.contains("\"decision\":\"block\"")
            && held.contains("make builder-brief T=T3 F=451 KIND=fix")
    );
    assert!(ask("POOL_IDLE_OK:").contains("POOL_IDLE_OK with no reason"));
    assert_eq!(ask("POOL_IDLE_OK: the count is held for a measurement"), "");
    put(&clone.join("specs/451-x/queue.txt"), "T3 mend files=-\n");
    assert_eq!(ask("done"), "");
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 fix files=- waits=GM\n",
    );
    assert_eq!(ask("done"), "");
    crate::shared::env::unset("POOL_IDLE_ROOT");
}

/// 451 T313's round-3 ruling (T421): an open performance task with no queue line is named FIRST, with the command that writes its
/// line, whether or not an entry is READY; a line for it, `waits=` among them, quiets it.
#[test]
fn an_open_performance_task_with_no_queue_line_is_named_first() {
    let (dir, clone) = world("unlisted", "T3 fix crates=rust/guard files=-\n");
    put(
        &clone.join("specs/451-x/tasks.md"),
        "- [ ] T3 open\n- [ ] T6 [perf] the faster gate\n- [ ] T7 [perf] the faster suite\n",
    );
    put(
        &clone.join(".git/task-starts.jsonl"),
        "{\"feature\": \"451-x\", \"task\": \"T3\", \"utc\": \"2026-11-27T01:00:00Z\"}\n",
    );
    let tree = dir.join("c-b1");
    let block = refusal(&judge(&stop("done"), Some(&clone), 3)).unwrap();
    let want = format!("pool-idle: {} is free. FIRST, 451 T6 is open performance work with no queue line (1 more: make builder-next names them). Write its line - CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it:\n  make queue-add F=451 T=T6 KIND=fix\nThen 451 T3 is READY, overlapping no task in flight. Hand it out before this turn ends:\n  make builder-brief T=T3 F=451 KIND=fix CRATE=\"rust/guard\" ENTRY=1\nOr start a line of your final message with: POOL_IDLE_OK: <why not, two words or more>\n", tree.display());
    assert_eq!(block, want);
    // T7 lined, waiting; T6 alone unlisted and nothing READY: named alone
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 fix files=- waits=GM\nT7 fix files=- waits=GM\n",
    );
    let block = refusal(&judge(&stop("done"), Some(&clone), 3)).unwrap();
    let want = format!("pool-idle: {} is free. FIRST, 451 T6 is open performance work with no queue line. Write its line - CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it:\n  make queue-add F=451 T=T6 KIND=fix\nOr start a line of your final message with: POOL_IDLE_OK: <why not, two words or more>\n", tree.display());
    assert_eq!(block, want);
    // its line written with waits=: quiet
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 fix files=- waits=GM\nT7 fix files=- waits=GM\nT6 fix files=- waits=GM\n",
    );
    assert_eq!(judge(&stop("done"), Some(&clone), 3), Said::Quiet);
}

/// RED FIRST (451 T481): a READY fix entry whose task line names a new mechanism is a command `make builder-brief` refuses, so the
/// block says the flag `make queue` and `make builder-next` say (451 T412) under it - the build-half command and the misread route;
/// an entry of another kind, or a line naming none, is said as before.
#[test]
fn a_ready_fix_entry_whose_line_names_a_mechanism_is_flagged_in_the_block() {
    let (dir, clone) = world("flag", "T3 fix crates=rust/guard files=-\n");
    put(
        &clone.join("specs/451-x/tasks.md"),
        "- [ ] T3 a new guard over the queue\n",
    );
    let block = refusal(&judge(&stop("done"), Some(&clone), 3)).unwrap();
    let want = format!("pool-idle: {} is free and 451 T3 is READY, overlapping no task in flight. Hand it out before this turn ends:\n  make builder-brief T=T3 F=451 KIND=fix CRATE=\"rust/guard\" ENTRY=1\n  FLAG: T3 (line 1) is typed fix, but T3's line names a new mechanism (\"a new guard\"), which make builder-brief refuses KIND=fix for: retype the line build-half and add its closing-half line after it, then\n    make builder-brief T=T3 F=451 KIND=build-half CRATE=\"rust/guard\" ENTRY=1\n    or, where the test misreads the line (a quoted refusal phrase, `make -C`), the fix command as printed with SIZING_OK=\"<reason>\"\nOr start a line of your final message with: POOL_IDLE_OK: <why not, two words or more>\n", dir.join("c-b1").display());
    assert_eq!(block, want);
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 build-half crates=rust/guard files=-\n",
    );
    let block = refusal(&judge(&stop("done"), Some(&clone), 3)).unwrap();
    assert!(!block.contains("FLAG"), "{block}");
}
