//! The pace of a main-session wait (feature 451 T16, D13, FR-008): on the two permitted paths - a POLL_OK-escaped wait and the
//! file-watching wait - a loop whose longest `sleep` is over `POLL_CHECK_S`, or whose length cannot be read, from a payload with no
//! `agent_id`, is refused naming the same loop at the knob; `SLOW_POLL_OK` escapes. Split from `no_poll_hooks.rs` at the 1,000-line
//! bar (constitution X clause 13).

use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{re, Ctx};
use crate::protocol::Answer;
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::shape::{quoted_spans, strip_heredocs, strip_quotes};
use crate::shared::state::field;

// A `sleep` at a command position and its words, redirections left out: numbers (`8m`, `60.5`, `1m 30s`) or a variable (`$N`,
// `${N}`, `"$N"`) worked out where the command sets it; any other word - a variable set nowhere in the command, an arithmetic, a
// substitution, `infinity` - is a length that cannot be read, judged as endless (the plan-blocks review, as D12 refuses `wait $P`).
static SLEEP_ARGS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[;&|(\s])\\?(?:(?:command|env|busybox)\s+)?(?:/(?:usr/)?bin/)?sleep((?:[ \t]+(?![0-9]*[<>])(?:"[^"]*"|'[^']*'|[^\s;&|)<>"'])+(?=[\s;&|)]|$))+)"#,
    )
});
// A variable set to a sleep's number at a command position (`N=480`, `export N=8m`, `N="480"`, `N=480 cmd`).
static NUMBER_SET: LazyLock<Regex> = LazyLock::new(|| {
    re(r#"(?:^|[;&|(\s])([A-Za-z_][A-Za-z0-9_]*)=(["']?)([0-9.]+[smhd]?)\2(?=[\s;&|)]|$)"#)
});
// `"$N"` unquoted, so the sanitized form keeps the variable a sleep is given.
static QUOTED_VAR: LazyLock<Regex> = LazyLock::new(|| re(r#""(\$\{?[A-Za-z_][A-Za-z0-9_]*\}?)""#));
// A loop's keyword at a command position, and the `do` and `done` words that close it (`shared::wait`'s `LOOP_KW` and `DO_DONE`).
static LOOP_AT: LazyLock<Regex> = LazyLock::new(|| re(r"(?:^|[;&|\s(])(?:while|until|for)\s"));
// A shell and its flags before the string it runs from its `-c` (`SHELL_C`'s shell and flags), through the string's opening quote;
// the string is read by `shell_strings`.
static SHELL_AT: LazyLock<Regex> = LazyLock::new(|| {
    re(r#"(?:^|[\s/;&|(])(?:ba|da|z|k)?sh\s+(?:-[A-Za-z-]*\s+)*-[A-Za-z]*c\s+["']"#)
});
static DO_DONE: LazyLock<Regex> = LazyLock::new(|| re(r"(?:^|[;\n&])\s*(do|done)(?=[\s;&|)]|$)"));

/// How slowly the main session's wait may check, at most (s): GUESS (feature 451 D13, FR-008) - research R5's waits slept 300 to
/// 1,500 s between checks of an agent's output, so an agent gone idle sat unnoticed for minutes; a minute is the spec's knob, retuned
/// from the waits FR-004's data records.
pub(super) const POLL_CHECK_S: u64 = 60;

/// A main-session wait loop slower than its check refused, or stood aside by `SLOW_POLL_OK` and its reason (D13); None where the
/// wait may go on - a subagent's, one at the knob or quicker, or one whose loop has no sleep a number gives.
pub(super) fn slow_poll(cx: &Ctx) -> Option<Vec<Answer>> {
    if !field(&cx.event.input, "agent_id").is_empty() {
        return None;
    }
    let longest = longest_wait_sleep(cx).filter(|&s| s > knob())?;
    match escape_or_refuse(&cx.cmd, "SLOW_POLL_OK") {
        Escape::Refused(text) => {
            cx.log("blocked", "SLOW_POLL_OK-no-reason");
            Some(vec![Answer::Refuse(text)])
        }
        Escape::Escaped(why) => {
            fire(
                "no-poll",
                "escaped",
                &why,
                "slow-poll-ok",
                &cx.event.input,
                cx.session,
            );
            None
        }
        Escape::None => {
            cx.log("blocked", "slow-poll");
            Some(vec![Answer::Refuse(slow_refusal(
                longest,
                &at_the_check(&cx.cmd),
            ))])
        }
    }
}

/// The knob in the seconds a sleep is read in.
fn knob() -> f64 {
    f64::from(u32::try_from(POLL_CHECK_S).unwrap_or(u32::MAX))
}

/// The numbers the command sets its variables to, each name's largest (a sleep given `$N` is read as the longest it can be).
pub(super) type Set = std::collections::HashMap<String, f64>;

/// One of a `sleep`'s numbers in seconds (`8m` 480, `60.5`), or None where it is no number.
fn amount(a: &str) -> Option<f64> {
    let (n, unit) = match a.as_bytes().last() {
        Some(b's') => (&a[..a.len() - 1], 1.0),
        Some(b'm') => (&a[..a.len() - 1], 60.0),
        Some(b'h') => (&a[..a.len() - 1], 3600.0),
        Some(b'd') => (&a[..a.len() - 1], 86_400.0),
        _ => (a, 1.0),
    };
    n.parse::<f64>().ok().map(|v| v * unit)
}

/// The seconds a `sleep`'s numbers add up to (`1m 30s` 90), a variable read from `set`, or None where one cannot be read.
pub(super) fn sleep_seconds(args: &str, set: &Set) -> Option<f64> {
    args.split_whitespace()
        .map(|a| {
            let a = a.trim_matches(['"', '\'']);
            a.strip_prefix('$').map_or_else(
                || amount(a),
                |name| set.get(name.trim_matches(['{', '}'])).copied(),
            )
        })
        .sum()
}

/// What `text` sets its variables to, where it sets one to a sleep's number.
fn numbers_set(text: &str) -> Set {
    let mut set = Set::new();
    for c in NUMBER_SET.captures_iter(text).map_while(Result::ok) {
        let (Some(name), Some(v)) = (c.get(1), c.get(3).and_then(|m| amount(m.as_str()))) else {
            continue;
        };
        let at = set.entry(name.as_str().to_owned()).or_insert(v);
        *at = at.max(v);
    }
    set
}

/// The longest `sleep` inside a loop of the command, or of a string a shell runs from its `-c` - which the sanitized form blanks, and
/// the ceiling still reaches - a variable worked out where the command sets it, or None.
pub(super) fn longest_wait_sleep(cx: &Ctx) -> Option<f64> {
    let body = strip_heredocs(&cx.cmd);
    let set = numbers_set(&body);
    let body = QUOTED_VAR.replace_all(&body, "$1");
    let inner: Vec<f64> = shell_strings(&body)
        .into_iter()
        .filter_map(|(at, end)| longest_loop_sleep(&strip_quotes(&body[at + 1..end]), &set))
        .collect();
    longest_loop_sleep(&strip_quotes(&body), &set)
        .into_iter()
        .chain(inner)
        .reduce(f64::max)
}

/// Each string a shell runs from its `-c` in `body`, its opening and its closing quote's byte, in order - as the pattern it replaced,
/// `SHELL_STRING` (`SHELL_AT` then `((?:\\.|(?!\1).)*)\1`, the quote's own kind), found them: the string is shape's `quoted_spans`
/// first span of the line from its opening quote, where that span opens there (the pattern's `.` never crossed a newline), and where
/// none does the search goes on from the character after the match's start. Read by the scan (451 T113): the pattern took a
/// backslash with the character after it or alone, so its backtracking search tried 2^n readings of the n backslashes after a quote
/// nothing on its line closes, and the guard gave no answer in 10 s on forty (measured 2026-11-21, the T113 plan section). A test
/// holds the two equal on every text of up to 5 pieces (`tests.rs`).
pub(super) fn shell_strings(body: &str) -> Vec<(usize, usize)> {
    let (mut found, mut from) = (Vec::new(), 0);
    while let Ok(Some(m)) = SHELL_AT.find_from_pos(body, from) {
        let at = m.end() - 1;
        let line = body[at..].find('\n').map_or(body.len(), |n| at + n);
        if let Some(&(0, end)) = quoted_spans(&body[at..line]).first() {
            found.push((at, at + end));
            from = at + end + 1;
        } else {
            from = m.start() + body[m.start()..].chars().next().map_or(1, char::len_utf8);
        }
    }
    found
}

/// The longest `sleep` inside a loop of `scan`, a sanitized command - in its head or its body, a nested loop's counted - or None.
pub(super) fn longest_loop_sleep(scan: &str, set: &Set) -> Option<f64> {
    let loops: Vec<(usize, usize)> = LOOP_AT
        .find_iter(scan)
        .map_while(Result::ok)
        .map(|m| (m.start(), loop_end(scan, m.end())))
        .collect();
    SLEEP_ARGS
        .captures_iter(scan)
        .map_while(Result::ok)
        .filter(|c| {
            c.get(0)
                .is_some_and(|m| loops.iter().any(|&(a, b)| a <= m.start() && m.start() < b))
        })
        .map(|c| sleep_seconds(c.get(1).map_or("", |m| m.as_str()), set).unwrap_or(f64::INFINITY))
        .reduce(f64::max)
}

/// The end of the `done` that closes the loop whose keyword ends at `at`, or the text's end.
fn loop_end(text: &str, at: usize) -> usize {
    let mut depth = 0;
    let words = DO_DONE
        .captures_iter(&text[at..])
        .map_while(Result::ok)
        .filter_map(|c| c.get(1));
    for word in words {
        if word.as_str() == "do" {
            depth += 1;
        } else {
            depth -= 1;
            if depth <= 0 {
                return at + word.end();
            }
        }
    }
    text.len()
}

/// `cmd` with every `sleep` over the knob at the knob: the form the slow-poll refusal names.
pub(super) fn at_the_check(cmd: &str) -> String {
    let set = numbers_set(&strip_heredocs(cmd));
    let found: Vec<(std::ops::Range<usize>, Option<f64>)> = SLEEP_ARGS
        .captures_iter(cmd)
        .map_while(Result::ok)
        .filter_map(|c| {
            let args = c.get(1)?;
            Some((args.range(), sleep_seconds(args.as_str(), &set)))
        })
        .collect();
    let mut out = cmd.to_owned();
    for (range, secs) in found.into_iter().rev() {
        if secs.is_none_or(|s| s > knob()) {
            out.replace_range(range, &format!(" {POLL_CHECK_S}"));
        }
    }
    out
}

fn slow_refusal(longest: f64, form: &str) -> String {
    let pace = if longest.is_finite() {
        format!("sleeps up to {longest} s between its checks")
    } else {
        "sleeps for a length the guard cannot read (a variable the command does not set, an arithmetic, a substitution)"
            .to_owned()
    };
    format!(
        "BLOCKED (no-poll): this wait {pace}, from the main session - over POLL_CHECK_S, {POLL_CHECK_S} s (feature 451 FR-008: the main session's waits checked every 420 to 600 s, so an agent gone idle sat unnoticed for \
minutes, research R5).\n\nDo this instead: the same loop with every sleep at {POLL_CHECK_S} s or less:\n\n  {form}\n\nA subagent's \
wait is not held to this. Escape: SLOW_POLL_OK=\"<reason>\" in the command.\n"
    )
}
