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
    run_as(cmd, background, None)
}

/// `cmd` judged from the main session (`agent` None: no `agent_id` in the payload) or from the subagent `agent`.
fn run_as(cmd: &str, background: bool, agent: Option<&str>) -> Vec<Answer> {
    crate::shared::log::quiet();
    let mut ti = json!({"command": cmd});
    if background {
        ti["run_in_background"] = Value::Bool(true);
    }
    let mut input = json!({"tool_name": "Bash", "cwd": ".", "tool_input": ti});
    if let Some(a) = agent {
        input["agent_id"] = Value::String(a.to_owned());
    }
    let e = Event {
        name: "PreToolUse".to_owned(),
        input,
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
    // 451 T177 (message-check): the fix names the Bash parameter and the escape its form; the busy-wait takes no why (its second
    // round), and the disguised sleep keeps its first line, its why cut (the round arbiter's ask:guard-wordings-sleep-and-slot)
    let busy = refused(&run("while true; do echo; sleep 5; done"));
    for kept in [
        "BLOCKED (no-poll): this is a busy-wait loop (a loop containing `sleep`).\n\nDo this instead: ",
        "run the work as a Bash call with run_in_background: true and act on its completion notification.",
        "put POLL_OK=\"<what you are waiting for, two words or more>\" in the command.",
    ] {
        assert!(busy.contains(kept), "{kept}: {busy}");
    }
    let why = ["burns wall-clock", "re-invokes you", "notifies you"];
    let cut = why.iter().all(|w| !busy.contains(w));
    assert!(cut, "{busy}");
    let disguised = refused(&run("command sleep 5"));
    let head = "BLOCKED (no-poll): `sleep` was invoked in a form that evades the harness's foreground-sleep block.\n\nDo this instead: ";
    let why_cut = !disguised.contains("wearing a hat") && !disguised.contains("better signal");
    assert!(disguised.starts_with(head) && why_cut, "{disguised}");
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
    // fed back, it is permitted as it stands: no answer at all - `rewritten()` reads a refusal as no rewrite too, and hid one here
    // (feature 451 T16)
    assert_eq!(run_with(&cmd, true), Vec::new());
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

/// Whether `a` is the slow-poll refusal (feature 451 T16, D13): it names the escape and the 60 s form.
fn slow_refusal(a: &[Answer]) -> bool {
    let r = refused(a);
    r.contains("SLOW_POLL_OK") && r.contains("every sleep at 60 s or less")
}

/// The command the slow-poll refusal offers in its place.
fn offered(a: &[Answer]) -> String {
    let r = refused(a);
    r.split_once("60 s or less:\n\n  ")
        .and_then(|(_, rest)| rest.split_once("\n\nA subagent"))
        .map_or_else(String::new, |(form, _)| form.to_owned())
}

/// Research R5's observed wait, verbatim from the main session's transcript (a backgrounded Bash call): the agent's output file
/// checked every 60 s and, when it has not grown, 420 s more before the agent is called idle, escaped with `POLL_OK`.
const R5: &str = "POLL_OK=\"the resumed T227 agent's report\"; \
f=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/tasks/a32196d5562b60215.output; s=$(stat -c %s $f); while true; \
do sleep 60; n=$(stat -c %s $f); if [ \"$n\" = \"$s\" ]; then sleep 420; m=$(stat -c %s $f); [ \"$m\" = \"$n\" ] && break; s=$m; \
else s=$n; fi; done; echo \"agent output idle\"";

/// T16's cases, each by its plan line (D13, FR-008): from the main session a wait loop on the `POLL_OK` or the file-watching path
/// whose longest `sleep` is over 60 s is refused naming the 60 s form, foreground and backgrounded alike.
#[test]
fn a_main_session_wait_slower_than_its_check_is_refused() {
    let firing = [
        R5,
        "until test -s /tmp/a.out; do sleep 480; done  # POLL_OK: the agent's file",
        "while sleep 480; do grep -q DONE /tmp/a.log && break; done  # POLL_OK: the agent's log",
        "until grep -q DONE /tmp/a.log; do sleep 480; done",
        "until grep -q DONE /tmp/a.log; do sleep 8m; done",
        "until grep -q DONE /tmp/a.log; do sleep 60.5; done",
        "until grep -q DONE /tmp/a.log; do sleep 1m 30s; done",
        "until grep -q DONE /tmp/a.log; do sleep 2h; done",
        "until grep -q DONE /tmp/a.log; do sleep 1d; done",
        "until grep -q DONE /tmp/a.log; do sleep 30; sleep 90s; done",
        "until grep -q DONE /tmp/a.log; do for i in 1 2; do sleep 120; done; done",
        "until curl -s x; do /bin/sleep 300; done  # POLL_OK: the port is external",
    ];
    // every case judged before the verdict, so the check deleted shows each one red (FR-012)
    let missed: Vec<(&str, bool)> = firing
        .into_iter()
        .flat_map(|c| [(c, false), (c, true)])
        .filter(|&(c, bg)| !slow_refusal(&run_with(c, bg)))
        .collect();
    assert_eq!(missed, Vec::<(&str, bool)>::new(), "not refused");
    let r = refused(&run(R5));
    assert!(r.contains("420 s") && r.contains("POLL_CHECK_S"), "{r}");
    assert!(offered(&run(R5)).contains("then sleep 60; m="), "{r}");
}

/// The quiet side (D13): a loop at 60 s or less, a subagent's slow loop, a sleep outside every loop, a quoted mention - none refused
/// for its pace, each answered as before T16.
#[test]
fn a_wait_at_its_check_or_a_subagents_passes() {
    let quiet = [
        // R5's wait at 60 s throughout
        "POLL_OK=\"the resumed T227 agent's report\"; f=/tmp/a.out; s=$(stat -c %s $f); while true; do sleep 60; \
n=$(stat -c %s $f); if [ \"$n\" = \"$s\" ]; then sleep 60; m=$(stat -c %s $f); [ \"$m\" = \"$n\" ] && break; s=$m; else s=$n; fi; \
done; echo \"agent output idle\"",
        "until grep -q DONE /tmp/a.log; do sleep 60; done",
        "until grep -q DONE /tmp/a.log; do sleep 1m; done",
        "until grep -q DONE /tmp/a.log; do sleep 0.5; done",
        "until grep -q \"sleep 480\" /tmp/a.log; do sleep 30; done",
        "sleep 480; cat /tmp/a.out  # POLL_OK: the agent's file once",
        "until grep -q DONE /tmp/a.log; do sleep 30; done; sleep 480; tail /tmp/a.log",
    ];
    let wrong: Vec<(&str, bool)> = quiet
        .into_iter()
        .flat_map(|c| [(c, false), (c, true)])
        .filter(|&(c, bg)| !refused(&run_with(c, bg)).is_empty())
        .collect();
    assert_eq!(wrong, Vec::<(&str, bool)>::new(), "refused");
    // a builder (a payload with an agent_id) is not held to it: the slow loop answered as it was before T16
    let sub: Vec<(&str, bool)> = [R5, "until grep -q DONE /tmp/a.log; do sleep 480; done"]
        .into_iter()
        .flat_map(|c| [(c, false), (c, true)])
        .filter(|&(c, bg)| {
            let a = run_as(c, bg, Some("a1b2c3"));
            let said = rewritten(&a).1;
            let ceiled = said.contains("WAIT TIMED OUT") || said.contains("CEILING");
            !(refused(&a).is_empty() && ceiled)
        })
        .collect();
    assert_eq!(sub, Vec::<(&str, bool)>::new(), "a subagent held");
    // the periodic report keeps its cron refusal, ahead of the pace
    assert!(
        refused(&run_with("while true; do date; sleep 1800; done", true)).contains("CronCreate")
    );
}

/// The escape (FR-012): `SLOW_POLL_OK` and a reason stands the refusal aside, a bare token is refused for its reason; and it is
/// no `POLL_OK` - the longer token never reads as the shorter one's escape.
#[test]
fn slow_poll_ok_with_a_reason_stands_the_refusal_aside() {
    let (v, said) = rewritten(&run(
        "until grep -q DONE /tmp/a.log; do sleep 480; done  # SLOW_POLL_OK: the producer writes hourly",
    ));
    assert!(v["run_in_background"] == true && said.contains("BACKGROUNDED"));
    let (_, said2) = rewritten(&run(
        "POLL_OK=\"the remote queue\" SLOW_POLL_OK=\"a nightly job checked slowly\" until curl -s x; do sleep 480; done",
    ));
    assert!(said2.contains("POLL_OK permitted this wait"), "{said2}");
    assert!(refused(&run(
        "until grep -q DONE /tmp/a.log; do sleep 480; done  # SLOW_POLL_OK"
    ))
    .contains("SLOW_POLL_OK with no reason"));
    // SLOW_POLL_OK alone grants nothing POLL_OK grants: a busy-wait stays refused, a file wait stays on its own path
    assert!(refused(&run(
        "while ! nc -z localhost 8080; do sleep 2; done  # SLOW_POLL_OK: a slow port here"
    ))
    .contains("busy-wait loop"));
    let (_, said3) = rewritten(&run(
        "until grep -q x /tmp/a.log; do sleep 5; done  # SLOW_POLL_OK: two words here",
    ));
    assert!(said3.contains("BACKGROUNDED") && said3.contains("PROOF-OF-LIFE"));
    assert!(refused(&run(
        "while ! nc -z localhost 8080; do sleep 2; done  # SLOW_POLL_OK"
    ))
    .contains("busy-wait loop"));
    // both tokens, in either order
    let (_, said4) = rewritten(&run(
        "until curl -s x; do sleep 480; done  # SLOW_POLL_OK: a slow remote job; POLL_OK: the port is external",
    ));
    assert!(said4.contains("POLL_OK permitted this wait"), "{said4}");
}

/// What the guard emits never trips its own refusal: each rewrite of a main-session wait (the file wait's proof and ceiling, the
/// `POLL_OK` ceiling, the bracketed pattern, the make wait scoped to this tree) and the 60 s form the refusal offers, fed back.
#[test]
fn the_guards_own_rewrites_and_offer_pass_its_pace_check() {
    // each rewrite with the backgrounding it was emitted with
    let emitted: Vec<(String, bool)> = [
        ("until grep -q x /tmp/a.log; do sleep 60; done", false),
        ("until curl -s x; do sleep 60; done  # POLL_OK: the port is external", false),
        ("while pgrep -f \"x y\"; do sleep 60; done  # POLL_OK: the remote queue", false),
        ("until ! pgrep -f \"make done\" >/dev/null; do sleep 60; done  # POLL_OK: a detached gate", true),
    ]
    .into_iter()
    .map(|(c, bg)| {
        let v = rewritten(&run_with(c, bg)).0;
        let cmd = v["command"].as_str().unwrap_or_default().to_owned();
        (cmd, bg || v["run_in_background"] == true)
    })
    .collect();
    assert!(emitted.iter().all(|(c, _)| c.contains("WAIT TIMED OUT")));
    // none is refused for anything: the file wait's was, as a busy-wait, until `file_watching_loop` read past its own proof clause
    let refused_again: Vec<&(String, bool)> = emitted
        .iter()
        .filter(|(c, bg)| !refused(&run_with(c, *bg)).is_empty())
        .collect();
    assert_eq!(refused_again, Vec::<&(String, bool)>::new());
    let emitted: Vec<String> = emitted.into_iter().map(|(c, _)| c).collect();
    let offers: Vec<String> = [
        R5,
        "until grep -q DONE /tmp/a.log; do sleep 8m; done",
        "until grep -q DONE /tmp/a.log; do sleep 1m 30s; done",
    ]
    .into_iter()
    .map(|c| offered(&run(c)))
    .collect();
    assert!(offers.iter().all(|c| !c.is_empty()), "{offers:#?}");
    // none of it is refused for its pace, in the foreground or the background
    let tripped: Vec<&String> = emitted
        .iter()
        .chain(&offers)
        .filter(|c| {
            [false, true]
                .iter()
                .any(|&bg| slow_refusal(&run_with(c, bg)))
        })
        .collect();
    assert_eq!(tripped, Vec::<&String>::new(), "refused its own output");
    // and an offer is refused for nothing at all: the R5 offer is still a POLL_OK wait, the file waits made safe in the background
    let offer_refused: Vec<&String> = offers
        .iter()
        .filter(|c| !refused(&run_with(c, true)).is_empty())
        .collect();
    assert_eq!(offer_refused, Vec::<&String>::new(), "an offer refused");
}

/// The pace reader's edges (D13): a sleep no number gives is unreadable, read as endless, a loop left open runs to the text's end, a nested loop's
/// sleep is its outer loop's too, and a sleep after the loop's `done` is outside it.
#[test]
fn the_pace_reader_reads_its_edges() {
    use super::pace::{at_the_check, longest_loop_sleep, sleep_seconds, Set};
    let none = Set::new();
    assert_eq!(sleep_seconds(" 1m 30s", &none), Some(90.0));
    assert_eq!(sleep_seconds(" 1.5h", &none), Some(5400.0));
    assert_eq!(sleep_seconds(" .", &none), None);
    assert_eq!(
        longest_loop_sleep("until x; do sleep .; done", &none),
        Some(f64::INFINITY)
    );
    assert_eq!(
        longest_loop_sleep("until x; do sleep 480", &none),
        Some(480.0)
    );
    assert_eq!(
        longest_loop_sleep("until x; do sleep 5; done; sleep 480", &none),
        Some(5.0)
    );
    assert_eq!(longest_loop_sleep("sleep 480; echo", &none), None);
    assert_eq!(
        longest_loop_sleep(
            "until x; do for i in 1 2; do sleep 120; done; sleep 5; done",
            &none
        ),
        Some(120.0)
    );
    // a redirection is no length
    assert_eq!(
        longest_loop_sleep(
            "until x; do sleep 30 2>/dev/null; sleep 20 >/dev/null; done",
            &none
        ),
        Some(30.0)
    );
    assert_eq!(
        at_the_check("sleep 30; /bin/sleep 8m"),
        "sleep 30; /bin/sleep 60"
    );
    // a loop a shell runs from its `-c` string is read; a quoted mention is not
    let c =
        "bash -c \"until grep -q X /tmp/a.log; do sleep 480; done\"  # POLL_OK: the agent's log";
    assert!(slow_refusal(&run(c)), "{:?}", run(c));
    assert_eq!(
        longest_loop_sleep(
            &strip_quotes("until x; do echo \"sleep 480\"; sleep 5; done"),
            &none
        ),
        Some(5.0)
    );
}

/// The four frozen corpora through the pace check (T16): every command judged from the main session, foreground and backgrounded,
/// none refused for its pace. A raw grep finds 3 commands with a loop word and a `sleep` over 60 s, read by hand 2026-11-20: each a
/// heredoc's payload (a Python script, a shell script written to a file), never a wait of the session's.
#[test]
fn the_frozen_corpora_through_the_pace_check() {
    let all = the_corpora();
    let slow: Vec<(&str, bool)> = all
        .iter()
        .flat_map(|c| [(c.as_str(), false), (c.as_str(), true)])
        .filter(|&(c, bg)| slow_refusal(&run_with(c, bg)))
        .collect();
    assert_eq!(slow.len(), 0, "{slow:#?}");
}

/// The plan reviews' notes (T16): a sleep whose number the command itself sets is worked out and judged, and one whose length is
/// still unreadable - a variable set nowhere in the command, an arithmetic or a command substitution - is refused as D12 refuses an
/// unreadable `wait $P`, naming the literal `sleep 60` form.
#[test]
fn a_sleep_set_in_the_command_is_judged() {
    let firing = [
        "N=480; until grep -q DONE /tmp/a.log; do sleep $N; done",
        "export N=8m; until grep -q DONE /tmp/a.log; do sleep ${N}; done",
        "N=480; until grep -q DONE /tmp/a.log; do sleep \"$N\"; done",
        "N=30; N=480; until grep -q DONE /tmp/a.log; do sleep $N; done",
        "N=480 bash -c 'until grep -q DONE /tmp/a.log; do sleep $N; done'  # POLL_OK: the agent's log",
        "N=\"480\"; until test -s /tmp/a.out; do sleep $N; done  # POLL_OK: the agent's file",
        "until grep -q DONE /tmp/a.log; do sleep $N; done",
        "until grep -q DONE /tmp/a.log; do sleep $WAIT; done",
        "M=480; until grep -q DONE /tmp/a.log; do sleep $N; done",
        "until grep -q DONE /tmp/a.log; do sleep \"$((N * 2))\"; done",
        "until grep -q DONE /tmp/a.log; do sleep $(cat /tmp/n); done",
        "until curl -s x; do sleep infinity; done  # POLL_OK: the port is external",
    ];
    let missed: Vec<(&str, bool)> = firing
        .into_iter()
        .flat_map(|c| [(c, false), (c, true)])
        .filter(|&(c, bg)| !slow_refusal(&run_with(c, bg)))
        .collect();
    assert_eq!(missed, Vec::<(&str, bool)>::new());
    // the offer sets the sleep at the knob, and passes its pace check fed back
    let offer = offered(&run(firing[0]));
    assert!(offer.contains("do sleep 60; done"));
    assert!(!slow_refusal(&run_with(&offer, true)));
    // a busy-wait whose sleep takes a variable is one too, for anyone (the digit the patterns asked for once let it through)
    assert!(refused(&run_as(
        "until curl -s x; do sleep $N; done",
        false,
        Some("a1")
    ))
    .contains("busy-wait loop"));
    // ...and an unreadable one's offer is the literal form
    let unread = refused(&run("until grep -q DONE /tmp/a.log; do sleep $N; done"));
    assert!(unread.contains("cannot read") && unread.contains("do sleep 60; done"));
    let quiet = [
        "N=30; until grep -q DONE /tmp/a.log; do sleep $N; done",
        "N=5; until grep -q DONE /tmp/a.log; do sleep \"$N\"; done",
    ];
    let wrong: Vec<(&str, bool)> = quiet
        .into_iter()
        .flat_map(|c| [(c, false), (c, true)])
        .filter(|&(c, bg)| !refused(&run_with(c, bg)).is_empty())
        .collect();
    assert_eq!(wrong, Vec::<(&str, bool)>::new());
}

/// A `SLOW_POLL_OK` whose reason is empty or one word is refused for its reason (the plan review's note, T16): a pin, the shared
/// escape reader refusing each before T16's check was asked.
#[test]
fn a_thin_slow_poll_ok_is_refused_for_its_reason() {
    let thin = [
        "SLOW_POLL_OK=\"\" until grep -q DONE /tmp/a.log; do sleep 480; done",
        "SLOW_POLL_OK=\"hourly\" until grep -q DONE /tmp/a.log; do sleep 480; done",
        "SLOW_POLL_OK=hourly until grep -q DONE /tmp/a.log; do sleep 480; done",
        "until grep -q DONE /tmp/a.log; do sleep 480; done  # SLOW_POLL_OK: hourly",
    ];
    let let_through: Vec<&str> = thin
        .into_iter()
        .filter(|c| !refused(&run(c)).contains("SLOW_POLL_OK with no reason"))
        .collect();
    assert_eq!(let_through, Vec::<&str>::new());
}

/// 451 T113: a string a shell runs from its `-c` that nothing closes on its line, forty escapes in it, beside a main-session wait
/// `POLL_OK` lets through - `SHELL_STRING`, which `slow_poll` read the string with, took a backslash with the character after it or
/// alone, so its backtracking search tried 2^40 readings, and the guard gave no answer in 10 s (measured 2026-11-21,
/// `/tmp/t113/probe-before.txt`). Judged in a child under a deadline, the string unclosed and closed on the next line.
#[test]
fn a_shell_string_nothing_closes_on_its_line_is_judged_in_time() {
    const CHILD: &str = "L7R_NO_POLL_SHELL_STRING_IN_TIME";
    let esc = "\\n".repeat(40);
    let cmds = [
        format!("while :; do sleep 600; done; bash -c 'it {esc}  # POLL_OK: the probe of 451 T113"),
        format!(
            "while :; do sleep 600; done; bash -c 'it {esc}\n'  # POLL_OK: the probe of 451 T113"
        ),
    ];
    if std::env::var_os(CHILD).is_some() {
        for cmd in &cmds {
            println!("T113 slow {}", slow_refusal(&run(cmd)));
        }
        return;
    }
    let (passed, said) = crate::guards::passes_in_time(
        "guards::no_poll_hooks::tests::a_shell_string_nothing_closes_on_its_line_is_judged_in_time",
        CHILD,
        10,
    );
    assert!(passed, "the guard did not answer in 10 s: {said}");
    assert_eq!(said.matches("T113 slow true").count(), 2, "{said}");
}

/// 451 T113: the scan finds the strings the pattern it replaced (`SHELL_STRING`, built here) found, its opening and its closing quote,
/// on every text of up to 5 pieces of `sh -c `, the same after a no-break space (a start of two bytes), ` -c `, a double and a single
/// quote, a backslash, a letter, a newline, a character of two bytes and a `;` (111,111 texts).
#[test]
fn the_shell_strings_are_the_ones_the_pattern_found() {
    let pattern = crate::shared::regex::build(
        r#"(?:^|[\s/;&|(])(?:ba|da|z|k)?sh\s+(?:-[A-Za-z-]*\s+)*-[A-Za-z]*c\s+(["'])((?:\\.|(?!\1).)*)\1"#,
    )
    .unwrap();
    let pieces = [
        "sh -c ",
        "\u{a0}sh -c ",
        " -c ",
        "\"",
        "'",
        "\\",
        "a",
        "\n",
        "é",
        ";",
    ];
    for text in crate::guards::texts_of(&pieces, 5) {
        let found: Vec<(usize, usize)> = pattern
            .captures_iter(&text)
            .map_while(Result::ok)
            .filter_map(|c| Some((c.get(1)?.start(), c.get(0)?.end() - 1)))
            .collect();
        assert_eq!(super::pace::shell_strings(&text), found, "{text:?}");
    }
}

#[test]
fn each_rewrite_notice_says_what_was_done_and_what_to_do_in_few_words() {
    // 451 T170: a builder's file wait carried BACKGROUNDED, PROOF and CEILING together, 1,071 characters 201 times, measured
    // 2026-11-23 over the coordinator's subagents; the history behind each rewrite is the code's, not the reader's
    for (said, words, most) in [
        (super::BRACKETED, "bracketed for you", 160),
        (
            super::ESCAPED_BRACKET,
            "POLL_OK permitted this wait, and its process-match pattern was bracketed",
            230,
        ),
        (super::ESCAPED_CEILING, "POLL_OK permitted this wait", 130),
        (super::SCOPED, "scoped to this working tree", 230),
        (super::BACKGROUNDED, "BACKGROUNDED", 200),
        (super::PROOF, "PROOF-OF-LIFE", 340),
        (super::CEILING, "CEILING", 150),
    ] {
        let (fits, n) = (said.contains(words) && said.len() <= most, said.len());
        assert!(fits, "{n} > {most}: {said}");
    }
}
