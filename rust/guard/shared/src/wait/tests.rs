use serde_json::json;

use super::{
    add_ceiling, background, bracket_pattern, cron_for, file_watching_loop, file_watching_wait,
    periodic, poll_reason, proof_of_life, scope_make_waits, self_matching, sleep_in_loop,
    WAIT_CEILING_S,
};

#[test]
fn a_sleep_inside_a_loop_is_one_and_before_it_is_not() {
    assert!(sleep_in_loop("while true; do sleep 1; done"));
    assert!(sleep_in_loop("for p in 1 2; do echo; sleep 1; done"));
    assert!(sleep_in_loop("while x; do echo done; sleep 1; done"));
    assert!(sleep_in_loop("while x; do sleep 2"));
    assert!(!sleep_in_loop("sleep 1; for p in x; do echo; done"));
    assert!(!sleep_in_loop("echo hi"));
}

#[test]
fn the_permitted_wait_watches_a_file_and_nothing_else() {
    assert!(file_watching_loop(
        "until grep -q done /tmp/a.log; do sleep 5; done"
    ));
    assert!(file_watching_loop(
        "until grep -qE \"passed|failed\" /tmp/l.log 2>/dev/null; do sleep 5; done"
    ));
    assert!(file_watching_loop(
        "until [ -s f ] && grep -q x /tmp/f.log; do sleep 5; done"
    ));
    assert!(file_watching_loop(
        "until grep -q x /tmp/a.log || ! kill -0 $p >/dev/null; do sleep 5; done"
    ));
    assert!(file_watching_loop("while read l < /tmp/in; do :; done"));
    assert!(file_watching_loop("until grep -q x $L; do sleep 1; done"));
    assert!(!file_watching_loop("until curl -s x; do sleep 1; done"));
    assert!(!file_watching_loop(
        "until grep -q $(cat x) /tmp/a.log; do sleep 1; done"
    ));
    assert!(!file_watching_loop(
        "until cat /tmp/a.log | grep -q x; do sleep 1; done"
    ));
    assert!(!file_watching_loop(
        "until grep -q x /tmp/a.log > /tmp/o; do sleep 1; done"
    ));
    assert!(!file_watching_loop(
        "until ! pgrep -f x >/dev/null; do sleep 1; done"
    ));
    assert!(!file_watching_loop("echo no loop"));
    assert!(file_watching_wait(
        &json!({"run_in_background": true, "command": "until grep -q x /tmp/a.log; do sleep 1; done"})
    ));
    assert!(!file_watching_wait(
        &json!({"command": "until grep -q x /tmp/a.log; do sleep 1; done"})
    ));
}

#[test]
fn backgrounding_is_read_as_python_reads_truth() {
    for (v, want) in [
        (json!(true), true),
        (json!(false), false),
        (json!("yes"), true),
        (json!(""), false),
        (json!(1), true),
        (json!(0), false),
        (json!([1]), true),
        (json!({}), false),
        (json!(null), false),
    ] {
        assert_eq!(background(&json!({"run_in_background": v})), want);
    }
}

#[test]
fn a_file_wait_is_given_a_proof_of_life_where_it_lacks_one() {
    let until = proof_of_life(
        "until grep -q x /tmp/a.log; do sleep 1; done",
        "/h/writer-alive.sh",
    )
    .unwrap();
    assert!(until.contains(
        "grep -q x /tmp/a.log || { /h/writer-alive.sh \"/tmp/a.log\" || exit 3; false; }; do"
    ));
    let whiles = proof_of_life("while ! grep -q x /tmp/a.log; do sleep 1; done", "w").unwrap();
    assert!(whiles.contains(" && { w \"/tmp/a.log\" || exit 3; }; do"));
    assert_eq!(
        proof_of_life(
            "until grep -q x /tmp/a.log || ! pgrep -f y; do sleep 1; done",
            "w"
        ),
        None
    );
    assert_eq!(proof_of_life("until [ -s f ]; do sleep 1; done", "w"), None);
    assert_eq!(proof_of_life("until curl x; do sleep 1; done", "w"), None);
    assert!(proof_of_life(
        "echo \\x; until grep -q x /tmp/a.log; do sleep 1; done",
        "w"
    )
    .is_some());
    let quoted = proof_of_life(
        "bash -c \"until grep -q x /tmp/a.log; do sleep 1; done\"",
        "w",
    )
    .unwrap();
    assert!(quoted.contains("{ w \\\"/tmp/a.log\\\" || exit 3; false; }"));
    // the guard's own clause is still a file watch, and gets no second one (feature 451 T16: fed back, the wait was refused)
    for given in [&until, &whiles, &quoted] {
        assert!(file_watching_loop(given), "{given}");
        assert_eq!(proof_of_life(given, "w"), None, "{given}");
    }
    // ...and the whole command still parses: the no-poll suite's feature-295 case, which asked `hm_shape.py proof` by path until
    // feature 449 T129 deleted it (the guard reaches this shape only through `bash -c "..."`, whose quoted body it does not scan)
    let lit = proof_of_life(
        "setsid --fork bash -c \"until grep -q X /tmp/q295.log; do sleep 5; done\"",
        "/h/_writer-alive.sh",
    )
    .unwrap();
    assert!(lit.contains("writer-alive.sh \\\"/tmp/q295.log\\\""));
    let parsed = std::process::Command::new("bash")
        .args(["-n", "-c", &lit])
        .status()
        .unwrap();
    assert!(parsed.success());
}

#[test]
fn a_literal_process_pattern_is_bracketed_and_a_make_wait_scoped() {
    assert_eq!(
        bracket_pattern("pgrep -f make done").as_deref(),
        Some("pgrep -f '[m]ake done'")
    );
    assert_eq!(
        bracket_pattern("pkill -af \"run x\"").as_deref(),
        Some("pkill -af \"[r]un x\"")
    );
    assert_eq!(bracket_pattern("pgrep -f '[m]ake done'"), None);
    assert_eq!(bracket_pattern("pgrep -f \"$P\""), None);
    assert_eq!(bracket_pattern("pgrep -f ./run"), None);
    assert_eq!(bracket_pattern("pgrep make"), None);
    assert_eq!(
        scope_make_waits("pgrep -f \"make map GEN=pool/x\" || echo", "/h/own-make.sh").as_deref(),
        Some("/h/own-make.sh map GEN=pool/x || echo")
    );
    assert_eq!(scope_make_waits("pgrep -f \"make $T\"", "o"), None);
    assert_eq!(scope_make_waits("ls", "o"), None);
}

#[test]
fn a_pattern_that_matches_its_own_command_is_found() {
    assert_eq!(
        self_matching("sleep 30 & until ! pgrep -f \"sleep 30\"; do :; done"),
        ["sleep 30"]
    );
    assert!(self_matching("pgrep -f '[s]leep 30'").is_empty());
    assert!(self_matching("pgrep -f \"$X\"").is_empty());
    assert!(self_matching("pgrep -f \"(\"").is_empty());
    assert!(self_matching("pgrep -f zzz").is_empty() || !self_matching("pgrep -f zzz").is_empty());
}

#[test]
fn a_loop_gets_a_ceiling_once() {
    let until = add_ceiling("until grep -q x f; do sleep 1; done", WAIT_CEILING_S).unwrap();
    assert!(
        until.contains(" || { [ \"$SECONDS\" -ge 5400 ] && { echo \"WAIT TIMED OUT after 90 min")
    );
    let whiles = add_ceiling("while true; do sleep 1; done", 60).unwrap();
    assert!(whiles.contains(" && { [ \"$SECONDS\" -lt 60 ] || {"));
    assert_eq!(add_ceiling(&until, WAIT_CEILING_S), None);
    assert_eq!(add_ceiling("echo hi", WAIT_CEILING_S), None);
    assert!(add_ceiling("bash -c \"until x; do sleep 1; done\"", 60)
        .unwrap()
        .contains("[ \\\"\\$SECONDS\\\" -ge 60 ]"));
}

#[test]
fn a_periodic_report_has_its_period() {
    let bg = |cmd: &str| json!({"run_in_background": true, "command": cmd});
    assert_eq!(
        periodic(&json!({"command": "while true; do sleep 60; done"}), "."),
        None
    );
    for (reason, want) in [
        ("POLL_OK=\"every 30 minutes\"", 1800),
        ("POLL_OK=hourly", 3600),
        ("POLL_OK='every 20 s'", 20),
        ("POLL_OK=\"every 2h\"", 7200),
        ("POLL_OK=half-hourly", 1800),
        ("POLL_OK=daily", 86_400),
        ("POLL_OK=\"every minute\"", 60),
        ("POLL_OK=\"every half hour\"", 1800),
        ("POLL_OK=heartbeat", 3600),
    ] {
        assert_eq!(periodic(&bg(&format!("x  # {reason}")), "."), Some(want));
    }
    assert_eq!(
        periodic(
            &bg("while [ $SECONDS -lt 3600 ]; do date; sleep 60; done"),
            "."
        ),
        Some(3600)
    );
    assert_eq!(
        periodic(&bg("while true; do date; sleep 300; done"), "."),
        Some(300)
    );
    assert_eq!(
        periodic(
            &bg("while true; do grep -q x f && break; sleep 30; done"),
            "."
        ),
        None
    );
    assert_eq!(
        periodic(
            &bg("while true; do [ $SECONDS -ge 7200 ] && break; sleep 600; done"),
            "."
        ),
        Some(7200)
    );
    assert_eq!(
        periodic(&bg("while [ $SECONDS ]; do sleep 1; done  # 900"), "."),
        Some(900)
    );
    assert_eq!(
        periodic(&bg("while [ $SECONDS ]; do sleep 1; done"), "."),
        Some(3600)
    );
    let d = crate::tempdir::TempDir::new("guard-wait");
    std::fs::write(d.join("r.sh"), "while true; do date; sleep 120; done\n").unwrap();
    assert_eq!(periodic(&bg("bash r.sh"), &d.to_string_lossy()), Some(120));
    assert_eq!(periodic(&bg("./missing.sh"), ""), None);
    assert_eq!(periodic(&bg("echo once"), "."), None);
    assert_eq!(
        periodic(
            &bg("while true; do for x in 1; do echo; done; sleep 60; done"),
            "."
        ),
        Some(60)
    );
    assert_eq!(
        periodic(&bg("while true; do date; sleep 60"), "."),
        Some(60)
    );
}

#[test]
fn the_cron_keeps_the_period() {
    assert_eq!(cron_for(1800, 13), "*/30 * * * *");
    assert_eq!(cron_for(300, 13), "*/5 * * * *");
    assert_eq!(cron_for(90, 13), "*/2 * * * *");
    assert_eq!(cron_for(150, 13), "*/2 * * * *");
    assert_eq!(cron_for(30, 13), "*/1 * * * *");
    assert_eq!(cron_for(100, 13), "*/2 * * * *");
    assert_eq!(cron_for(3600, 13), "13 * * * *");
    assert_eq!(cron_for(3600, 0), "7 * * * *");
    assert_eq!(cron_for(3600, 30), "37 * * * *");
    assert_eq!(cron_for(7200, 13), "13 */2 * * *");
    assert_eq!(cron_for(100 * 3600, 13), "13 */23 * * *");
    assert_eq!(poll_reason("x # POLL_OK=bare"), "bare");
    assert_eq!(poll_reason("x"), "");
}

/// Quoted words before a wait's head are read past, quote by quote, and the proof of life lands where it would without them.
#[test]
fn quoted_words_before_a_wait_leave_its_proof_of_life_in_place() {
    let got = proof_of_life(
        "echo 'a b' \"c\"; until grep -q x /tmp/a.log; do sleep 1; done",
        "w",
    )
    .unwrap();
    assert!(got.starts_with("echo 'a b' \"c\"; until grep -q x /tmp/a.log || { w \"/tmp/a.log\" || exit 3; false; }; do"), "{got}");
}

/// A loop held by something other than the time is no period.
#[test]
fn a_loop_held_by_a_file_is_no_period() {
    let bg =
        json!({"run_in_background": true, "command": "while [ -f x ]; do date; sleep 60; done"});
    assert_eq!(periodic(&bg, "."), None);
}

/// The variable that makes a child run read the loop (451 T108).
const LOOP_CHILD: &str = "L7R_WAIT_QUOTE_IN_TIME";

/// A file-watching loop whose condition holds a quote no later quote closes, then forty escapes: 2^40 tries for the backtracking
/// search `cond_grammar` once neutralized its quotes with (`QUOTED`, the pattern shape's `quoted_spans` replaced - 451 T103).
fn unclosed_loop() -> String {
    format!(
        "until grep -q it's {} /tmp/a.log; do sleep 5; done",
        "\\n".repeat(40)
    )
}

/// 451 T108: the loop is read in a process of its own - this test run again as that process - under T103's deadline (a GUESS: the
/// fixed read answers in milliseconds). Before the fix it gave no answer in 10 s (measured 2026-11-21, the T108 plan section).
#[test]
fn a_loop_whose_quote_nothing_closes_is_read_in_time() {
    use std::time::{Duration, Instant};
    if std::env::var_os(LOOP_CHILD).is_some() {
        println!("T108 read {}", file_watching_loop(&unclosed_loop()));
        return;
    }
    let mut child = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "wait::tests::a_loop_whose_quote_nothing_closes_is_read_in_time",
            "--nocapture",
        ])
        .env(LOOP_CHILD, "1")
        .stdout(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    let deadline = Instant::now() + Duration::from_secs(10);
    let done = loop {
        let status = child.try_wait().unwrap();
        if status.is_some() || Instant::now() > deadline {
            break status;
        }
        std::thread::sleep(Duration::from_millis(20));
    };
    let _ = child.kill();
    let out = child.wait_with_output().unwrap();
    let said = String::from_utf8_lossy(&out.stdout);
    assert!(
        done.is_some_and(|s| s.success()),
        "the loop was not read in 10 s: {said}"
    );
    // the quote closes nothing, so it neutralizes nothing: the grep of a file is still the permitted watch
    assert!(said.contains("T108 read true"), "{said}");
}

/// 451 T108: a condition is neutralized as the pattern the scan replaced (`QUOTED`, built here) neutralized it - each quoted
/// string its body, its punctuation dropped - on every text to 6 characters over a double and a single quote, a backslash, a letter,
/// a pipe and a character of two bytes (none of them a ceiling's, a proof's or a discarded stderr's, which the grammar drops first).
#[test]
fn a_condition_is_neutralized_as_the_pattern_neutralized_it() {
    let quoted = crate::regex::build(r#"(?s)(["'])(?:\\.|(?!\1).)*\1"#).unwrap();
    let punct = crate::regex::build(r"[|<>;&]").unwrap();
    let (mut texts, mut longest) = (vec![String::new()], vec![String::new()]);
    for _ in 0..6 {
        longest = longest
            .iter()
            .flat_map(|t| ['"', '\'', '\\', 'a', '|', 'é'].map(|c| format!("{t}{c}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let want = quoted.replace_all(text, |c: &fancy_regex::Captures| {
            let whole = c.get(0).map_or("", |m| m.as_str());
            punct
                .replace_all(&whole[1..whole.len() - 1], "")
                .into_owned()
        });
        assert_eq!(
            super::cond_grammar(text).as_deref(),
            Some(&*want),
            "{text:?}"
        );
    }
}
