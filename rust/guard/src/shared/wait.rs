//! The shapes of a wait (`scripts/hooks/lib/hm_shape.py`'s wait half - feature 449 T009 decision (a)): a `sleep` inside a loop, the
//! one permitted wait (backgrounded, watching a file) and its proof of life, a process pattern that matches its own command and its
//! bracketing, the 90-minute ceiling, and a periodic report with the cron that keeps its schedule. Each pattern is the Python's
//! verbatim (research R8); the reasons behind each stand in `hm_shape.py`'s comments, kept in git history.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::Value;

use super::shape::strip_quotes;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

macro_rules! pattern {
    ($name:ident, $p:expr) => {
        static $name: LazyLock<Regex> = LazyLock::new(|| re($p));
    };
}

pattern!(
    FILE_TEST,
    r"(?m)(?:^|\s)(?:test|\[)\s+[^;]*-(?:e|f|s|r|d|w|x)\s+\S"
);
pattern!(
    GREP_PATH,
    r"(?m)(?:^|\s)grep\b[^|;<>]*\s(?:\$\{?\w+\}?)?(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)\s*$"
);
pattern!(
    GREP_VAR,
    r"(?m)(?:^|\s)grep\b[^|;<>]*?\s(?!-)\S+\s(?:\$\{?\w+\}?)\s*$"
);
pattern!(IN_REDIR, r"<\s*(?:\./|/|~/)?[\w./-]+");
pattern!(
    LOOP_HEAD,
    r"(?s)\b(?P<kw>until|while)\b(?P<cond>.*?)(?:;\s*do\b|\bdo\b)"
);
pattern!(
    PROOF_OF_LIFE,
    r"(?:^|\s)!?\s*(?:\S*/)?(?:pgrep|pkill|_?writer-alive\.sh)\b|(?:^|\s)!?\s*kill\s+-0\b|(?:^|\s)!?\s*ps\s+-p\b"
);
pattern!(NULL_OUT, r"\s1?>\s*/dev/null");
pattern!(
    PATH_OPERAND,
    r"(?:\$\{?\w+\}?)(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)?|(?:(?:~?[\w.-]*/)+[\w.-]+|[\w.-]+\.[\w-]+)"
);
pattern!(STDERR_NULL, r"\s2>\s*/dev/null");
pattern!(SINGLE_PIPE, r"(?<!\|)\|(?!\|)");
pattern!(JOIN, r"&&|\|\|");
pattern!(QUOTED, r#"(?s)(["'])(?:\\.|(?!\1).)*\1"#);
pattern!(QUOTE_PUNCT, r"[|<>;&]");
pattern!(
    PROCMATCH,
    r#"\b(pgrep|pkill)\b((?:\s+-[a-zA-Z]+)*\s+-[a-zA-Z]*f[a-zA-Z]*)\s+(['"]?)([^'"|;&]+)\3"#
);
pattern!(
    MAKEWAIT,
    r#"\bpgrep\b(?:\s+-[a-zA-Z]+)*\s+-[a-zA-Z]*f[a-zA-Z]*(?:\s+-[a-zA-Z]+)*\s+(['"]?)(?:\[m\]|m)ake\s+([\w][\w .=/-]*?)\1(?=[\s|;&)]|$)"#
);
pattern!(
    CEILING_CLAUSE,
    r#"\s(?:\|\||&&) \{ \[ "\$SECONDS" -(?:ge|lt) \d+ \] (?:&&|\|\|) \{ echo "WAIT TIMED OUT[^"]*"; exit 4; \}; \}"#
);
pattern!(LOOP_KW, r"(?:^|[;&|\s(])(?:while|until|for)\s");
pattern!(DO_DONE, r"(?:^|[;\n&])\s*(do|done)(?=[\s;&|)]|$)");
pattern!(
    SLEEP_CALL,
    r"(?:^|[;&|(\s])\\?(?:(?:command|env|busybox)\s+)?(?:/(?:usr/)?bin/)?sleep\s+[0-9.]"
);
pattern!(
    PERIOD_WORDS,
    r"(?i)\b(?:hourly|half-hourly|daily|periodic(?:ally)?|heartbeat|(?:progress|status)\s+(?:report|update)s?|every\s+(?:(?P<n>\d+)\s*(?P<unit>s|secs?|seconds?|m|mins?|minutes?|h|hrs?|hours?)\b|(?P<word>half[- ]hour|hour|minute)))"
);
pattern!(POLL_REASON, r#"\bPOLL_OK=(?:"([^"]*)"|'([^']*)'|(\S+))"#);
pattern!(ELAPSED, r"\$\{?SECONDS\}?|date\s+\+%s");
pattern!(LIMIT, r"-(?:ge|gt|lt|le)\s+(\d+)");
pattern!(SLEEP_N, r"\bsleep\s+(\d+)");
pattern!(
    RUNS_FILE,
    r"(?:^|[;&|\s])(?:(?:bash|sh)\s+(?:-\w+\s+)*([^\s;&|-][^\s;&|]*)|(\./[^\s;&|]+))"
);
pattern!(STMT_SEP, r"[;\n]");
pattern!(LEAVES, r"\b(?:break|exit|return)\b");
pattern!(BARE_NUMBER, r"(?<![\w./=-])(\d+)(?![\w./])");

/// The deadline a wait's ceiling sets (s).
pub const WAIT_CEILING_S: u64 = 90 * 60;
const TIMED_OUT: &str = "WAIT TIMED OUT";

fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
}

fn caps<'t>(p: &Regex, text: &'t str) -> Vec<Captures<'t>> {
    p.captures_iter(text).filter_map(Result::ok).collect()
}

fn group<'t>(c: &Captures<'t>, name: &str) -> &'t str {
    c.name(name).map_or("", |m| m.as_str())
}

fn split<'t>(p: &Regex, text: &'t str) -> Vec<&'t str> {
    let mut out = Vec::new();
    let mut at = 0;
    for m in p.find_iter(text).filter_map(Result::ok) {
        out.push(&text[at..m.start()]);
        at = m.end();
    }
    out.push(&text[at..]);
    out
}

/// The condition as the grammar tests read it - quoted text neutralized, discarded stderr dropped - or None where it carries a
/// command substitution (`_cond_grammar`).
fn cond_grammar(cond: &str) -> Option<String> {
    if cond.contains("$(") || cond.contains('`') {
        return None;
    }
    let cond = CEILING_CLAUSE.replace_all(cond, " ");
    let neutral = QUOTED.replace_all(&cond, |c: &Captures| {
        let whole = c.get(0).map_or("", |m| m.as_str());
        QUOTE_PUNCT
            .replace_all(&whole[1..whole.len() - 1], "")
            .into_owned()
    });
    Some(STDERR_NULL.replace_all(&neutral, " ").into_owned())
}

/// What one `&&`/`||` part of a condition is: a file read, a liveness test, or neither (`_part_kind`).
fn part_kind(part: &str) -> &'static str {
    let alive = found(&PROOF_OF_LIFE, part);
    let part = if alive {
        NULL_OUT.replace_all(part, " ").into_owned()
    } else {
        part.to_owned()
    };
    if found(&SINGLE_PIPE, &part) || part.contains('>') {
        return "";
    }
    if found(&FILE_TEST, &part)
        || found(&GREP_PATH, &part)
        || found(&GREP_VAR, &part)
        || found(&IN_REDIR, &part)
    {
        return "file";
    }
    if alive {
        "alive"
    } else {
        ""
    }
}

/// The neutralized condition where it is the permitted file-watching shape, else None (`_watches_a_file`).
fn watches_a_file(cond: &str) -> Option<String> {
    let c = cond_grammar(cond)?;
    let kinds: Vec<&str> = split(&JOIN, &c).into_iter().map(part_kind).collect();
    (!kinds.is_empty() && !kinds.contains(&"") && kinds.contains(&"file")).then_some(c)
}

/// The quote open at byte `pos` of `cmd`: `'`, `"` or "" for none (`_quote_state`).
fn quote_state(cmd: &str, pos: usize) -> &'static str {
    let b = cmd.as_bytes();
    let (mut state, mut i) = ("", 0);
    while i < pos.min(b.len()) {
        let c = b[i];
        if state == "'" {
            if c == b'\'' {
                state = "";
            }
        } else if c == b'\\' {
            i += 2;
            continue;
        } else if state == "\"" {
            if c == b'"' {
                state = "";
            }
        } else if c == b'\'' {
            state = "'";
        } else if c == b'"' {
            state = "\"";
        }
        i += 1;
    }
    state
}

/// A clause escaped to stand inside an open double quote (`_fit`).
fn fit(clause: &str, state: &str) -> String {
    if state == "\"" {
        clause.replace('"', "\\\"").replace('$', "\\$")
    } else {
        clause.to_owned()
    }
}

/// `cmd` with each loop head given a clause built from its keyword and condition, at the condition's end - or None where `make`
/// adds none.
fn insert_at_heads(cmd: &str, make: impl Fn(&str, &str) -> Option<String>) -> Option<String> {
    let (mut out, mut shift, mut added) = (cmd.to_owned(), 0, false);
    for c in caps(&LOOP_HEAD, cmd) {
        let Some(clause) = make(group(&c, "kw"), group(&c, "cond")) else {
            continue;
        };
        let end = c.name("cond").map_or(0, |m| m.end());
        let clause = fit(&clause, quote_state(cmd, end));
        let at = end + shift;
        out.insert_str(at, &clause);
        shift += clause.len();
        added = true;
    }
    added.then_some(out)
}

/// `cmd` with a proof-of-life clause added to each file-watching loop that lacks one, or None (`proof_of_life`).
#[must_use]
pub fn proof_of_life(cmd: &str, helper: &str) -> Option<String> {
    insert_at_heads(cmd, |kw, cond| {
        let c = watches_a_file(cond).filter(|c| !found(&PROOF_OF_LIFE, c))?;
        let last = PATH_OPERAND
            .find_iter(&c)
            .filter_map(Result::ok)
            .last()?
            .as_str()
            .to_owned();
        let check = format!("{helper} \"{last}\" || exit 3");
        Some(if kw == "until" {
            format!(" || {{ {check}; false; }}")
        } else {
            format!(" && {{ {check}; }}")
        })
    })
}

/// Would `cmd` be the permitted file-watching wait were it backgrounded (`file_watching_loop`)?
#[must_use]
pub fn file_watching_loop(cmd: &str) -> bool {
    let heads = caps(&LOOP_HEAD, cmd);
    !heads.is_empty()
        && heads
            .iter()
            .all(|c| watches_a_file(group(c, "cond")).is_some())
}

/// Is this the one permitted wait - backgrounded, and watching a file (`file_watching_wait`)?
#[must_use]
pub fn file_watching_wait(tool_input: &Value) -> bool {
    background(tool_input)
        && file_watching_loop(
            tool_input
                .get("command")
                .and_then(Value::as_str)
                .unwrap_or(""),
        )
}

/// Whether the call runs in the background (Python's truthiness of `run_in_background`).
#[must_use]
pub fn background(tool_input: &Value) -> bool {
    match tool_input.get("run_in_background") {
        Some(Value::Bool(b)) => *b,
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Number(n)) => n.as_f64() != Some(0.0),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
        _ => false,
    }
}

/// `cmd` with every literal process-match pattern bracketed, or None (`bracket_pattern`).
#[must_use]
pub fn bracket_pattern(cmd: &str) -> Option<String> {
    let mut out = cmd.to_owned();
    for c in caps(&PROCMATCH, cmd).iter().rev() {
        let pat = c.get(4).map_or("", |m| m.as_str());
        // an empty pattern reads as a space, no letter, and is left alone
        let first = pat.chars().next().unwrap_or(' ');
        if pat.trim().is_empty()
            || pat.contains('[')
            || pat.contains('$')
            || !first.is_alphanumeric()
        {
            continue;
        }
        let quoted = Some(c.get(3).map_or("", |m| m.as_str()))
            .filter(|q| !q.is_empty())
            .unwrap_or("'");
        let whole = c.get(0).map_or(0..0, |m| m.range());
        let new = format!(
            "{}{} {quoted}[{first}]{}{quoted}",
            c.get(1).map_or("", |m| m.as_str()),
            c.get(2).map_or("", |m| m.as_str()),
            &pat[first.len_utf8()..]
        );
        out.replace_range(whole, &new);
    }
    (out != cmd).then_some(out)
}

/// `cmd` with every `pgrep -f "make <target>"` replaced by `<helper> <target>`, or None (`scope_make_waits`).
#[must_use]
pub fn scope_make_waits(cmd: &str, helper: &str) -> Option<String> {
    let mut out = cmd.to_owned();
    for c in caps(&MAKEWAIT, cmd).iter().rev() {
        // the pattern's target starts with a word character and holds no `$`: the Python's empty-or-variable test cannot fire
        let target = c.get(2).map_or("", |m| m.as_str()).trim();
        out.replace_range(
            c.get(0).map_or(0..0, |m| m.range()),
            &format!("{helper} {target}"),
        );
    }
    (out != cmd).then_some(out)
}

/// Every process-match pattern in `cmd` that matches `cmd`'s own text (`self_matching`); one no dialect compiles is skipped.
#[must_use]
pub fn self_matching(cmd: &str) -> Vec<String> {
    caps(&PROCMATCH, cmd)
        .iter()
        .map(|c| c.get(4).map_or("", |m| m.as_str()))
        .filter(|pat| !pat.contains('$') && !pat.trim().is_empty())
        .filter(|pat| Regex::new(pat).is_ok_and(|p| found(&p, cmd)))
        .map(str::to_owned)
        .collect()
}

/// `cmd` with a deadline clause in every loop head, or None where there is no loop or the ceiling is there (`add_ceiling`).
#[must_use]
pub fn add_ceiling(cmd: &str, seconds: u64) -> Option<String> {
    if cmd.contains(TIMED_OUT) || !found(&LOOP_HEAD, cmd) {
        return None;
    }
    let note = format!(
        "echo \"{TIMED_OUT} after {} min (no-poll ceiling): what this waited for never came - look at the producer, and wait again if it is still working\"",
        seconds / 60
    );
    insert_at_heads(cmd, |kw, _| {
        Some(if kw == "until" {
            format!(" || {{ [ \"$SECONDS\" -ge {seconds} ] && {{ {note}; exit 4; }}; }}")
        } else {
            format!(" && {{ [ \"$SECONDS\" -lt {seconds} ] || {{ {note}; exit 4; }}; }}")
        })
    })
}

/// The loop's matching `done` from `at` (nested loops counted), or the text's end.
fn done_of(text: &str, at: usize) -> Option<(usize, usize)> {
    let mut depth = 1;
    let mut pos = at;
    while let Ok(Some(c)) = DO_DONE.captures_from_pos(text, pos) {
        let whole = c.get(0)?;
        depth += if c.get(1).map(|m| m.as_str()) == Some("do") {
            1
        } else {
            -1
        };
        if depth == 0 {
            return Some((
                c.get(1)
                    .map_or(whole.start(), |m| m.start())
                    .min(whole.start()),
                whole.end(),
            ));
        }
        pos = whole.end().max(pos + 1);
    }
    None
}

/// Does a `sleep` run inside a `while`/`until`/`for` loop of `scan`, a sanitized command (`sleep_in_loop`)?
#[must_use]
pub fn sleep_in_loop(scan: &str) -> bool {
    LOOP_KW.find_iter(scan).filter_map(Result::ok).any(|m| {
        let end = done_from(scan, m.end()).unwrap_or(scan.len());
        SLEEP_CALL
            .find_from_pos(&scan[..end], m.start())
            .is_ok_and(|f| f.is_some())
    })
}

/// The end of the `done` that closes the loop opened before `at`, counting from depth 0 (`sleep_in_loop`'s walk).
fn done_from(text: &str, at: usize) -> Option<usize> {
    let mut depth = 0;
    let mut pos = at;
    while let Ok(Some(c)) = DO_DONE.captures_from_pos(text, pos) {
        let whole = c.get(0)?;
        depth += if c.get(1).map(|m| m.as_str()) == Some("do") {
            1
        } else {
            -1
        };
        if depth == 0 {
            return Some(whole.end());
        }
        pos = whole.end().max(pos + 1);
    }
    None
}

/// The body of the loop whose `do` ends at `at`: up to its matching `done` (`_body_of`).
fn body_of(text: &str, at: usize) -> &str {
    done_of(text, at).map_or(&text[at..], |(start, _)| &text[at..start])
}

fn numbers(p: &Regex, text: &str) -> Vec<u64> {
    caps(p, text)
        .iter()
        .filter_map(|c| c.get(1))
        .map(|m| m.as_str().parse().unwrap_or(u64::MAX))
        .collect()
}

/// Seconds between reports where `text` holds a time-only or endless loop, else None (`_loop_period`).
fn loop_period(text: &str) -> Option<u64> {
    for c in caps(&LOOP_HEAD, text) {
        let cond = CEILING_CLAUSE
            .replace_all(group(&c, "cond"), " ")
            .trim()
            .trim_end_matches(';')
            .trim()
            .to_owned();
        let parts: Vec<&str> = split(&JOIN, &cond)
            .into_iter()
            .map(str::trim)
            .filter(|p| !p.is_empty())
            .collect();
        let end = c.get(0).map_or(0, |m| m.end());
        let sleeps = numbers(&SLEEP_N, &text[end..]);
        if (cond == "true" || cond == ":") && group(&c, "kw") == "while" && !sleeps.is_empty() {
            let stmts = split(&STMT_SEP, body_of(text, end));
            let leaves = stmts.iter().enumerate().any(|(i, s)| {
                found(&LEAVES, s)
                    && !found(&ELAPSED, s)
                    && !(i > 0 && found(&ELAPSED, stmts[i - 1]))
            });
            if leaves {
                continue;
            }
            let limits: Vec<u64> = stmts
                .iter()
                .filter(|s| found(&ELAPSED, s))
                .flat_map(|s| numbers(&LIMIT, s))
                .collect();
            return limits.iter().max().or(sleeps.iter().max()).copied();
        }
        if !parts.is_empty() && parts.iter().all(|p| found(&ELAPSED, p)) {
            return Some(
                parts
                    .iter()
                    .flat_map(|p| numbers(&LIMIT, p))
                    .max()
                    .unwrap_or(0),
            );
        }
    }
    None
}

/// The reason a `POLL_OK` gives in `cmd`, or "".
#[must_use]
pub fn poll_reason(cmd: &str) -> String {
    POLL_REASON
        .captures(cmd)
        .ok()
        .flatten()
        .and_then(|c| {
            (1..=3).find_map(|i| {
                c.get(i)
                    .map(|m| m.as_str().to_owned())
                    .filter(|g| !g.is_empty())
            })
        })
        .unwrap_or_default()
}

/// The report period (s) where a backgrounded command is a periodic report, else None (`periodic`); a script the command runs is
/// read from `cwd` as the Python read it.
#[must_use]
pub fn periodic(tool_input: &Value, dir: &str) -> Option<u64> {
    if !background(tool_input) {
        return None;
    }
    let cmd = tool_input
        .get("command")
        .and_then(Value::as_str)
        .unwrap_or("");
    let reason = poll_reason(cmd);
    if let Ok(Some(w)) = PERIOD_WORDS.captures(&reason) {
        if let Some(n) = w.name("n") {
            let unit = group(&w, "unit").to_lowercase();
            let mult = match unit.chars().next() {
                Some('s') => 1,
                Some('m') => 60,
                _ => 3600,
            };
            return Some(
                n.as_str()
                    .parse::<u64>()
                    .unwrap_or(u64::MAX)
                    .saturating_mul(mult),
            );
        }
        let word = w
            .name("word")
            .map_or_else(|| w.get(0).map_or("", |m| m.as_str()), |m| m.as_str())
            .to_lowercase();
        return Some(if word.contains("half") {
            1800
        } else if word.contains("minute") {
            60
        } else if word.contains("daily") {
            86_400
        } else {
            3600
        });
    }
    let bare = strip_quotes(cmd);
    let mut texts = vec![cmd.to_owned()];
    let dir = if dir.is_empty() { "." } else { dir };
    for c in caps(&RUNS_FILE, &bare) {
        let name = c.get(1).or_else(|| c.get(2)).map_or("", |m| m.as_str());
        let path = Path::new(dir).join(name);
        if path.is_file() && std::fs::metadata(&path).is_ok_and(|m| m.len() < 200_000) {
            texts.push(
                String::from_utf8_lossy(&std::fs::read(&path).unwrap_or_default()).into_owned(),
            );
        }
    }
    texts.iter().find_map(|t| loop_period(t)).map(|period| {
        let args: Vec<u64> = numbers(&BARE_NUMBER, &bare)
            .into_iter()
            .filter(|n| *n >= 60)
            .collect();
        if period > 0 {
            period
        } else {
            args.iter().max().copied().unwrap_or(3600)
        }
    })
}

/// Python's `round`: halves to even.
fn round_even(x: f64) -> u64 {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a period in minutes, small and positive"
    )]
    let floor = x.floor() as u64;
    let past = x - x.floor();
    // a half exactly goes to the even neighbor; anything else to the nearer
    if (past - 0.5).abs() < 1e-9 {
        floor + floor % 2
    } else if past > 0.5 {
        floor + 1
    } else {
        floor
    }
}

/// The recurring cron for a period: `*/m` under an hour, else the given minute every h hours (`cron_for`).
#[must_use]
pub fn cron_for(period: u64, minute: u64) -> String {
    #[expect(
        clippy::cast_precision_loss,
        reason = "a period in seconds, far below f64's exact range"
    )]
    let mins = round_even(period as f64 / 60.0).max(1);
    if mins < 60 {
        let m = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30]
            .into_iter()
            .filter(|d| *d <= mins)
            .min_by_key(|d| mins - d)
            .unwrap_or(1);
        return format!("*/{m} * * * *");
    }
    let minute = if minute == 0 || minute == 30 {
        minute + 7
    } else {
        minute
    };
    #[expect(
        clippy::cast_precision_loss,
        reason = "minutes, far below f64's exact range"
    )]
    let hours = round_even(mins as f64 / 60.0).max(1);
    if hours == 1 {
        format!("{minute} * * * *")
    } else {
        format!("{minute} */{} * * *", hours.min(23))
    }
}

#[cfg(test)]
mod tests;
