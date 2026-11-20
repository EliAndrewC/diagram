//! The decider on commands the suite carries (`tests/hooks/test-no-poll-hooks.sh`, replayed through the shim, is the verdict
//! against today's).

use std::path::PathBuf;

use serde_json::{json, Value};

use super::{decide, judge, local_minute, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};

fn minute() -> u64 {
    13
}

fn run_with(cmd: &str, background: bool) -> Vec<Answer> {
    crate::shared::log::quiet();
    let mut ti = json!({"command": cmd});
    if background {
        ti["run_in_background"] = Value::Bool(true);
    }
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": ".", "tool_input": ti}),
    };
    let s = Session::from_input(&json!({}));
    let scan = strip_quotes(&strip_heredocs(cmd));
    judge(&Ctx {
        event: &e,
        session: &s,
        cmd: cmd.to_owned(),
        scan,
        lib: PathBuf::from("/lib"),
        minute,
    })
}

fn run(cmd: &str) -> Vec<Answer> {
    run_with(cmd, false)
}

fn refused(a: &[Answer]) -> String {
    let [Answer::Refuse(w)] = a else {
        return String::new();
    };
    w.clone()
}

fn rewritten(a: &[Answer]) -> (Value, String) {
    let [Answer::Rewrite(v), Answer::Notice(n)] = a else {
        return (Value::Null, String::new());
    };
    (v.clone(), n.clone())
}

#[test]
fn a_busy_wait_and_a_disguised_sleep_are_refused() {
    assert!(refused(&run("while true; do echo; sleep 5; done")).contains("busy-wait loop"));
    assert!(refused(&run("command sleep 5")).contains("evades the harness"));
    assert!(run("git status").is_empty());
    assert!(run("sleep 1; for p in x; do echo; done").is_empty());
    assert!(rewritten(&[]).1.is_empty() && refused(&[]).is_empty());
}

#[test]
fn a_file_wait_is_made_safe_rather_than_refused() {
    let (v, said) = rewritten(&run("until grep -q x /tmp/a.log; do sleep 5; done"));
    assert!(
        v["run_in_background"] == true
            && said.contains("BACKGROUNDED")
            && said.contains("PROOF-OF-LIFE")
            && said.contains("CEILING")
    );
    let cmd = v["command"].as_str().unwrap_or_default().to_owned();
    assert!(cmd.contains("/lib/writer-alive.sh") && cmd.contains("WAIT TIMED OUT"));
    let (v2, said2) = rewritten(&run_with(&cmd, true));
    assert!(v2.is_null() && said2.is_empty());
    let alive = "until grep -q x /tmp/a.log || ! pgrep -f '[m]ake x'; do sleep 5; done";
    let (_, said3) = rewritten(&run_with(alive, true));
    assert!(
        said3.contains("CEILING") && !said3.contains("PROOF") && !said3.contains("BACKGROUNDED")
    );
    let ceiled = crate::shared::wait::add_ceiling(alive, crate::shared::wait::WAIT_CEILING_S)
        .unwrap_or_default();
    assert!(run_with(&ceiled, true).is_empty());
    let (_, said4) = rewritten(&run_with(
        "until grep -q x /tmp/a.log; do sleep 5; done",
        true,
    ));
    assert!(said4.contains("PROOF-OF-LIFE") && !said4.contains("BACKGROUNDED"));
    let own = "until grep -q x /tmp/a.log; do sleep 5; done; pgrep -f \"until grep\"";
    assert!(refused(&run(own)).contains("matches this command's own text"));
}

#[test]
fn a_self_matching_pattern_is_bracketed_or_refused() {
    let (v, said) = rewritten(&run("pgrep -f \"x y\" && echo up"));
    assert!(v["command"] == "pgrep -f \"[x] y\" && echo up" && said.contains("bracketed for you"));
    let (v2, said2) = rewritten(&run("pgrep -f \"make map GEN=a\" || echo gone"));
    assert!(
        v2["command"]
            .as_str()
            .unwrap_or_default()
            .contains("gates/l7r-gate.sh own-make map GEN=a")
            && said2.contains("scoped to this working tree")
    );
    let (v3, said3) = rewritten(&run("while pgrep -f \"x y\"; do :; done"));
    assert!(
        v3["command"]
            .as_str()
            .unwrap_or_default()
            .contains("WAIT TIMED OUT")
            && said3.contains("A ceiling was added")
    );
    assert!(refused(&run("pgrep -f \".x\"")).contains("matches this command's own text"));
    assert!(run("pgrep -f '[x] y'").is_empty());
}

#[test]
fn poll_ok_stands_aside_and_still_brackets_and_ceils() {
    assert!(run("curl -s x  # POLL_OK: the port is external").is_empty());
    let (v, said) = rewritten(&run(
        "until curl -s x; do sleep 5; done  # POLL_OK: the port is external",
    ));
    assert!(
        v["command"]
            .as_str()
            .unwrap_or_default()
            .contains("WAIT TIMED OUT")
            && said.contains("POLL_OK permitted this wait")
    );
    let (_, said2) = rewritten(&run(
        "pgrep -f \"x y\" && echo  # POLL_OK: the remote queue",
    ));
    assert!(
        said2.contains("POLL_OK permitted this wait, and its process-match pattern was bracketed")
    );
    assert!(refused(&run("sleep 5  # POLL_OK")).contains("POLL_OK with no reason"));
}

#[test]
fn a_periodic_report_goes_to_a_cron() {
    let r = refused(&run_with(
        "while true; do date; sleep 1800; done  # POLL_OK=\"every 30 minutes\"",
        true,
    ));
    assert!(
        r.contains("CronCreate(cron=\"*/30 * * * *\"")
            && r.contains("every 30 minutes: check the state once")
    );
    let plain = refused(&run_with("while true; do date; sleep 3600; done", true));
    assert!(plain.contains("cron=\"13 * * * *\"") && plain.contains("the periodic report: check"));
    assert!(refused(&run_with(
        "while true; do date; sleep 60; done  # CRON_OK: a one-off watch",
        true
    ))
    .contains("busy-wait"));
    assert!(
        refused(&run_with("while true; do sleep 60; done  # CRON_OK", true))
            .contains("CRON_OK with no reason")
    );
}

#[test]
fn decide_reads_the_command_and_skips_an_empty_one() {
    let s = Session::from_input(&json!({}));
    let empty = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": ""}}),
    };
    assert!(decide(&empty, &s).is_empty());
    let ls = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&ls, &s).is_empty());
    let quoted = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "''"}}),
    };
    assert!(decide(&quoted, &s).is_empty());
    assert!(local_minute() < 60);
}

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A `pgrep -f` after many `pgrep` words (feature 449 T185): unlimited, the pattern tried every one to its segment's end (18 s on 100 KB,
/// measured 2026-11-18, scratchpad t185/sizecurve.log), and at `fancy_regex`'s old limit it erred and read as no match; it now starts at its segment's first.
#[test]
fn a_pgrep_f_after_many_pgreps_is_seen_in_linear_time() {
    let command = format!("{}; pgrep -f foo", "pgrep x ".repeat(30_000));
    assert_eq!(
        within(move || super::PGREP_F.is_match(&command).ok()),
        Some(true)
    );
}

/// Whether `cmd` is refused as a detached make or cargo run (feature 451 T15, D12): the refusal names the Bash tool's background form.
fn detach_refused(cmd: &str) -> bool {
    let r = refused(&run(cmd));
    r.contains("run_in_background: true") && r.contains("DETACH_OK")
}

/// T15's cases, each by its plan line (D12, FR-008): every one that fires refused naming `run_in_background`, every quiet one passing.
#[test]
fn a_detached_make_or_cargo_run_is_refused_unless_a_wait_covers_it() {
    let firing = [
        // R4's observed run, and the forms D12 names
        "(make static > /tmp/t225-static.log 2>&1; echo END >> /tmp/t225-static.log) & sleep 1",
        "nohup make rust-test",
        "make static & echo wait",
        "make static & sleep 5 & wait $!",
        "make static & P=$!; wait $P",
        "make static & (wait)",
        "make static & false && wait",
        "make static & wait &",
        "setsid make static",
        "make static & disown",
        "make static & disown; wait",
        "make static & disown; wait $!",
        "make static & disown -h; wait",
        "make static & disown %1; wait",
        "make static & disown -a; wait",
        "make static & disown $!; wait",
        "{ make static; } &",
        "VAR=x make static &",
        "env X=1 make static &",
        // cargo, and the shapes around them
        "cargo test &",
        "nohup cargo build > /tmp/b.log 2>&1 &",
        "setsid --fork bash -c \"make static\"",
        "cd /tmp && make static > log 2>&1 &",
        "make static 2>&1 | tee /tmp/s.log &",
        "make &",
        "scripts/gates/l7r-gate.sh rust test &",
        "make static & if true; then wait; fi",
        "make static & wait | cat",
        "make static & wait -n",
        "echo $(make static &)",
        "make static & bash -c \"wait\"",
        "sleep 30 & make static & wait %1",
        "make static &\nsleep 1",
        "for t in a b; do make $t & done",
        "x() { make static & }; x",
    ];
    // every case judged before the verdict, so the check deleted shows each one red (FR-012)
    let missed: Vec<&str> = firing.into_iter().filter(|c| !detach_refused(c)).collect();
    assert_eq!(missed, Vec::<&str>::new(), "not refused");
    let quiet = [
        "for c in git setsid make; do echo $c; done",
        "make static > log 2>&1 & wait $!",
        "make static > log 2>&1 & wait \"$!\"",
        "(make static > log) & make decide F=449 T=T121 | tail -40; wait",
        "sleep 30 & make static & wait %2",
        "make static & wait",
        "make static & wait && echo done",
        "make static & wait 2>/dev/null",
        "make static\nwait",
        "for t in a b; do make $t & done; wait",
        "{ make a & make b & wait; }",
        "if true; then make static & fi; wait",
        "while read t; do make $t & done < list; wait",
        "case x in x) make static & ;; esac; wait",
        "(make static & wait) & wait",
        // a mention is never an invocation
        "git commit -m \"make static & disown\"",
        "cat > /tmp/n.md <<'EOF'\nmake static &\nnohup cargo build\nEOF",
        "echo 'nohup make static' && grep -n setsid x",
        "make quick  # lint & then make static",
        // a & that is no background
        "make static && echo ok",
        "make static &> /tmp/s.log",
        "make static > /tmp/s.log 2>&1",
        "make static |& tee /tmp/s.log",
        "make static >& /tmp/s.log",
        // a background job that is not make or cargo
        "sleep 5 & echo hi",
        "nohup resvg a.svg > /tmp/r.log 2>&1 &",
        "python3 x.py & wait $!; make static",
        "git log & make static; wait",
    ];
    let wrong: Vec<&str> = quiet.into_iter().filter(|c| !run(c).is_empty()).collect();
    assert_eq!(wrong, Vec::<&str>::new(), "refused");
}

/// The escape: a reason of two words or more stands the refusal aside and is recorded; a bare token is refused for its reason.
#[test]
fn detach_ok_with_a_reason_stands_the_refusal_aside() {
    assert!(run("make static &  # DETACH_OK: a probe of the guard").is_empty());
    assert!(run("DETACH_OK=\"two words here\" nohup make static").is_empty());
    assert!(refused(&run("make static &  # DETACH_OK")).contains("DETACH_OK with no reason"));
    let r = refused(&run("make static & disown; wait"));
    assert!(
        r.contains("disowned")
            && r.contains("run_in_background: true; its completion notice wakes you")
    );
    assert!(refused(&run("setsid make static")).contains("nohup or setsid"));
    assert!(refused(&run("make static &")).contains("lone `&`"));
    // ahead of the poll escape: POLL_OK is no second way past it
    assert!(detach_refused(
        "make static & until test -f x; do sleep 5; done  # POLL_OK: the file is external"
    ));
    assert!(detach_refused_bg("make static & sleep 1"));
}

fn detach_refused_bg(cmd: &str) -> bool {
    refused(&run_with(cmd, true)).contains("run_in_background: true")
}

/// Every command of the four frozen corpora under `tests/hooks/fixtures/`, read through `detached` (T15): the refused ones, each
/// read by hand and listed here as a real detached run (a correct refusal), so a new refusal of a corpus command fails this test.
fn the_corpora() -> Vec<String> {
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tests/hooks/fixtures/");
    let load = |f: &str| -> Value {
        serde_json::from_str(&std::fs::read_to_string(format!("{dir}{f}")).unwrap_or_default())
            .unwrap_or(Value::Null)
    };
    let text = |v: &Value| v.as_str().map(str::to_owned);
    let mut out: Vec<String> = Vec::new();
    let parse = load("bash-parse-corpus-2026-09.json");
    out.extend(
        parse["commands"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|r| text(&r["command"])),
    );
    let window = load("command-window-2026-09-13.json");
    out.extend(
        window["commands"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(text),
    );
    let refusals = load("guard-refusals-2026-09.json");
    out.extend(
        refusals
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|r| text(&r["command"])),
    );
    let main_tree = load("main-tree-refusals-2026-09.json");
    out.extend(
        main_tree["rows"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|r| text(&r["command"])),
    );
    out
}

/// 1,134 commands; 16 refused, every one a real launch of `make done` under `setsid nohup` (or `nohup`, `setsid --fork bash -c`, or
/// `setsid nohup bash -c "make done ..."`) with `&` - the gate detached before `run_in_background` (read by hand 2026-11-20, T15);
/// no mention, heredoc or commit message among them. The fifteenth (`python3 - <<'PYEOF' ... setsid nohup make done ... &`) was hidden until
/// the heredoc reader kept the words after a delimiter (the T15 review); the sixteenth (`PAIR_OK="..." \` and, on the next line,
/// `setsid nohup make done ... &`) until `POS` read `setsid` and the walk read a line continuation as a blank (T30, folded in).
#[test]
fn the_frozen_corpora_replayed() {
    let all = the_corpora();
    let refused: Vec<(&str, &str)> = all
        .iter()
        .filter_map(|c| super::detached(c).map(|r| (c.as_str(), r)))
        .collect();
    assert_eq!(all.len(), 1134);
    assert_eq!(refused.len(), 16, "{refused:#?}");
    let read: Vec<bool> = refused
        .iter()
        .map(|(c, r)| {
            let under = c.contains("nohup ") || c.contains("setsid ");
            *r == "detached-nohup" && under && c.contains(" done ")
        })
        .collect();
    assert_eq!(read, [true; 16], "{refused:#?}");
}

/// The walk over shapes a command rarely takes: a stray `)`, a trailing `\`, a line continuation, a `for` head with a pipe in it,
/// a head or a `case` cut short, a `;&` arm, a quoted job number - each read without a hang or a panic, and read right.
#[test]
fn the_walk_reads_the_rare_shapes() {
    use super::detached;
    assert_eq!(detached("make static & ) echo"), Some("detached-amp"));
    assert_eq!(detached("make static & wait \\"), Some("detached-amp"));
    assert_eq!(detached("make static \\\n  > log & wait"), None);
    assert_eq!(detached("for x in a | b; do make $x & done; wait"), None);
    assert_eq!(detached("make static & for x in a b"), Some("detached-amp"));
    assert_eq!(detached("make static & case x in"), Some("detached-amp"));
    assert_eq!(
        detached("case x in a) make static & ;& b) : ;; esac; wait"),
        None
    );
    assert_eq!(detached("make static & wait '%1'"), None);
    assert_eq!(detached("ls && echo nohup"), None);
    assert_eq!(detached("git status"), None);
    assert_eq!(detached("until make -q x; do make x & wait; done"), None);
}

/// The review's finds (T15): a heredoc with words after its delimiter is still payload, a string after `-c` that no shell runs is
/// still a string, and a `wait $!` or `wait %N` covers a job only in the job's own list - after a loop it waits for the last alone.
#[test]
fn a_payload_is_never_walked_and_a_named_wait_covers_only_its_own_list() {
    use super::detached;
    assert_eq!(
        detached("cat <<'EOF' > /tmp/n.md\nmake static &\nEOF"),
        None
    );
    assert_eq!(
        detached("python3 - <<'PY' | tee /tmp/o\nmake static & disown\nPY"),
        None
    );
    assert_eq!(
        detached("cat <<EOF > /tmp/n.md\nrun `make static & echo wait`\nEOF"),
        None
    );
    assert_eq!(detached("grep -c \"nohup make static\" /tmp/log"), None);
    assert_eq!(detached("grep -c \"make static &\" t.jsonl"), None);
    assert_eq!(detached("grep -c \"make static & \\\" x\" t.jsonl"), None);
    assert_eq!(detached("bash -lc \"make static &\""), Some("detached-amp"));
    assert_eq!(
        detached("for t in a b; do make $t & done; wait $!"),
        Some("detached-amp")
    );
    assert_eq!(
        detached("for t in a b; do make $t & done; wait %1"),
        Some("detached-amp")
    );
    assert_eq!(detached("make static & wait 2> /dev/null"), None);
    assert_eq!(detached("make static & wait $! 2> /dev/null"), None);
    // inside a string a shell runs, a quoted string it only passes is passed over, its `\"` kept inside it
    assert_eq!(detached("bash -c 'echo \"a\\\" & make x\"; true'"), None);
    assert_eq!(detached("case x in a) make static & esac; wait"), None);
    // a compound that is a pipeline's part runs in a subshell: a later `wait` covers none of its jobs (the plan review, measured
    // 2026-11-20: `for t in 1 2; do sleep 1.5 & done >/dev/null | cat; wait` returns in 0.005 s)
    let piped = [
        "for t in a b; do make $t & done | cat; wait",
        "for t in a b; do make $t & done >/dev/null | cat; wait",
        "{ make x & } | cat; wait",
        "cat list | while read t; do make $t & done; wait",
        "if true; then make x & fi | cat; wait",
        "( make x & ) | cat; wait",
    ];
    assert_eq!(piped.map(detached), [Some("detached-amp"); 6]);
    // ...while a wait inside that same part covers its own jobs
    assert_eq!(detached("{ make x & wait; } | cat"), None);
    assert_eq!(
        detached("for t in a b; do make $t & wait $!; done | cat"),
        None
    );
}
