//! The make invocations a command makes (`scripts/hooks/lib/hm_make.py`, the parts `gate-hooks` reads - feature 449 T007 decision
//! (a)): the targets it INVOKES, a mention never one; and the quick-and-done combination. `invoked` is the ONE reading of which make
//! targets a command runs (feature 451 D1, FR-001): the event log's writer and every guard asking "does this command run target T" read
//! it, so a timed, locked, backgrounded or subshelled run is read the same by all of them - two detectors disagreed before it (research
//! R1: `timeout 2400 make static` logged no target, `(make static) &` was invisible to the guards). `classify`'s verdict through a bare
//! pytest and the view it read a command by left with pytest (feature 449 T213).

use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::shape::{strip_heredocs, strip_quotes};

/// A command position: the start, or after `;`, `|`, `&`, `&&`, `||`, `(`, `{ `, a newline or the quote opening a shell's `-c` string, past the words that run the command after
/// them - a further `(` or `{`, a shell keyword (`if`, `then`, `do`, `else`, `elif`, `while`, `until`, `!`), `timeout [opts] N`, `flock
/// [opts] <file>`, `nice [-n N]`, `nohup`, `setsid [opts]`, `time [-p]`, `env [opts]` and `VAR=value` (feature 451 D1: the event log's
/// writer took `(`, the keywords and `time`, the guards `timeout`, `env` and `VAR=`; `flock`, `nice`, `nohup`, `{` and a lone `&`
/// neither; `setsid` added by T15).
pub const POS: &str = concat!(
    r#"(?:^|[\n;|&(]|\{\s|(?:^|[\s/])(?:ba|da|z)?sh\s+(?:-[a-z]+\s+)*-[a-z]*c\s+["'])\s*(?:"#,
    r"[({]\s*",
    r"|(?:if|then|do|else|elif|while|until|!)\s+",
    r"|timeout\s+(?:-[ks]\s*\S+\s+|--?[a-z][\w-]*(?:=\S+)?\s+)*\S+\s+",
    r"|flock\s+(?:-[wE]\s*\S+\s+|-\S+\s+)*\S+\s+",
    r"|nice\s+(?:-n\s*\S+\s+|-\S+\s+)*",
    r"|nohup\s+",
    r"|setsid\s+(?:-\S+\s+)*",
    r"|time\s+(?:-p\s+)?",
    r"|env\s+(?:-u\s*\S+\s+|-\S+\s+)*",
    r"|[A-Za-z_][A-Za-z0-9_]*=\S*\s+",
    r")*"
);
/// A Python interpreter, by any path.
pub const PY: &str = r"(?:\S*/)?python3?";

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

// A call: make (or `$(MAKE)`) at a command position, its words read after it; or the gate's crate-scoped form
// `l7r-gate.sh rust <cmd>`, which `make rust-<cmd>` runs (feature 451 D1).
static CALL: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"{POS}(?:(?:\$\(MAKE\)|make)(?=[\s;&|)`]|$)|(?:\S*/)?l7r-gate\.sh\s+rust\s+([a-z][\w-]*))"
    ))
});
// The gate's path quoted whole (`"$root/scripts/gates/l7r-gate.sh" rust test`), unquoted before the quotes are blanked.
static GATE_QUOTED: LazyLock<Regex> = LazyLock::new(|| re(r#""[^"\n]*/l7r-gate\.sh""#));
static GOAL: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z][\w-]*$"));
static SEP: LazyLock<Regex> = LazyLock::new(|| re(r"\s*(?:&&|\|\||;|\n)\s*"));
static MAKE_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\$\(MAKE\)|make)\b"));
static QUICK: LazyLock<Regex> = LazyLock::new(|| re(r"\s+quick\b"));
// A lone `&` (a job backgrounded, not `&&`, `>&` or `&>`): `POS` reads a call after it but `SEP` does not split there, so
// `make quick & make done` would be rebuilt as a bare `make & make done` (feature 451 T02).
static LONE_AMP: LazyLock<Regex> = LazyLock::new(|| re(r"(?:^|[^&>])&(?:[^&>]|$)"));

/// The arguments `-C dir`, `-f file`, `-I dir`, `-o file` and `-W file` take, never goals.
const TAKES_ARG: [&str; 10] = [
    "-C",
    "-f",
    "--directory",
    "--file",
    "--makefile",
    "-I",
    "--include-dir",
    "-o",
    "--old-file",
    "-W",
];
/// The flags whose argument is optional, taken only when it is a number (`-j 4 done`).
const TAKES_NUMBER: [&str; 4] = ["-j", "--jobs", "-l", "--load-average"];

/// The goals of one make call, read from the words after `make` up to the end of its simple command: a flag, its argument and a
/// `VAR=value` passed over, a path word too (`hm_make._goals`); any other word (a redirect, a stray number) ends the call. True where
/// the word that ended it may name a goal this reading cannot (`make $T`), so the call is not read as goal-less.
fn goals_of(rest: &str, out: &mut Vec<String>) -> bool {
    let end = rest
        .find([';', '|', '&', '\n', ')', '`'])
        .unwrap_or(rest.len());
    let mut words = rest[..end].split_whitespace().peekable();
    while let Some(word) = words.next() {
        if TAKES_ARG.contains(&word) {
            words.next();
        } else if TAKES_NUMBER.contains(&word) {
            words.next_if(|w| w.bytes().all(|b| b.is_ascii_digit()));
        } else if let Some(goal) =
            Some(word.trim_end_matches(['"', '\''])).filter(|w| GOAL.is_match(w).unwrap_or(false))
        {
            // the last goal of a `-c` string carries its closing quote
            out.push(goal.to_owned());
        } else if !(word.starts_with(['-', '.', '/', '~']) || is_assignment(word)) {
            // a redirection, or the quote closing a `-c` string, ends the words; anything else may be a goal unread
            return !(word.contains(['<', '>']) || word.trim_matches(['"', '\'']).is_empty());
        }
    }
    false
}

/// What a make call with no goal runs: the Makefile's default goal, named as make names it (feature 451 T15, T30 folded in - `make &`
/// read as no invocation at all, so a detached goal-less make was invisible to every guard).
pub const DEFAULT_GOAL: &str = ".DEFAULT_GOAL";

fn is_assignment(word: &str) -> bool {
    word.split_once('=').is_some_and(|(name, _)| {
        name.starts_with(|c: char| c.is_ascii_alphabetic() || c == '_')
            && name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
    })
}

/// Every make target `cmd` RUNS, in command order (feature 451 D1): heredocs and quoted strings blanked (the string after `-c`, which
/// an interpreter runs, kept), a call counted only at a command position (`POS`), every goal of each call, and `l7r-gate.sh rust <cmd>`
/// read as `rust-<cmd>`. A mention is never one (constitution XVIII).
#[must_use]
pub fn invoked(cmd: &str) -> Vec<String> {
    // NO `make`, NO PATTERN (T007, measured 2026-11-08): a hook call is a process, so each pattern compiles on every call - 4.6 ms
    // of a plain `ls`'s 11.4 - and a target needs `make`, `$(MAKE)` or the gate spelled in the command
    if !cmd.contains("make") && !cmd.contains("MAKE") && !cmd.contains("l7r-gate") {
        return Vec::new();
    }
    let unquoted = GATE_QUOTED.replace_all(cmd, "l7r-gate.sh");
    let clean = strip_quotes(&strip_heredocs(&unquoted));
    let mut out = Vec::new();
    for c in CALL.captures_iter(&clean).map_while(Result::ok) {
        if let Some(gate) = c.get(1) {
            out.push(format!("rust-{}", gate.as_str()));
        } else {
            let (end, before) = (c.get(0).map_or(clean.len(), |m| m.end()), out.len());
            if !goals_of(&clean[end..], &mut out) && out.len() == before {
                out.push(DEFAULT_GOAL.to_owned());
            }
        }
    }
    out
}

/// The set of make targets `cmd` runs (`targets`): `invoked`'s, order and repeats dropped.
#[must_use]
pub fn targets(cmd: &str) -> BTreeSet<String> {
    invoked(cmd).into_iter().collect()
}

fn balanced(text: &str) -> bool {
    let n = |c: char| text.matches(c).count();
    n('(') == n(')') && n('"') % 2 == 0 && n('\'') % 2 == 0
}

/// `cmd` with its `make quick` work removed, where it invokes both quick and done (`combine`, feature 162): None leaves it alone,
/// a shape that cannot be rebuilt exactly going through unchanged rather than guessed at.
#[must_use]
pub fn combine(cmd: &str) -> Option<String> {
    let has = |g: &BTreeSet<String>, k: &str| g.contains(k);
    if cmd.is_empty()
        || cmd.contains("GATE_OK")
        || cmd.contains("<<")
        || LONE_AMP.is_match(cmd).unwrap_or(false)
        || !cmd.contains("quick")
        || !cmd.contains("done")
    {
        return None;
    }
    let all = targets(cmd);
    if !has(&all, "quick") || !has(&all, "done") {
        return None;
    }
    // the segments and the separators between them (`re.split` with its group kept)
    let (mut segs, mut joints, mut at) = (Vec::new(), Vec::new(), 0);
    for m in SEP.find_iter(cmd).map_while(Result::ok) {
        segs.push(&cmd[at..m.start()]);
        joints.push(m.as_str());
        at = m.end();
    }
    segs.push(&cmd[at..]);
    let (mut kept, mut dropped): (Vec<(String, &str)>, bool) = (Vec::new(), false);
    for (i, seg) in segs.iter().enumerate() {
        let sep = joints.get(i).copied().unwrap_or("");
        let got = targets(seg);
        let makeish = MAKE_HEAD.is_match(seg.trim()).unwrap_or(false) && balanced(seg);
        if makeish && has(&got, "quick") && !has(&got, "done") {
            dropped = true;
            continue;
        }
        if makeish && has(&got, "quick") && has(&got, "done") {
            let rebuilt = QUICK.replace(seg, "").into_owned();
            let mut want = got.clone();
            want.remove("quick");
            if targets(&rebuilt) != want {
                return None;
            }
            kept.push((rebuilt, sep));
            dropped = true;
            continue;
        }
        kept.push(((*seg).to_owned(), sep));
    }
    if !dropped {
        return None;
    }
    let last = kept.len().saturating_sub(1);
    let out: String = kept
        .iter()
        .enumerate()
        .map(|(j, (s, p))| {
            if j < last {
                format!("{s}{p}")
            } else {
                s.clone()
            }
        })
        .collect();
    let out = out
        .trim()
        .trim_end_matches(['&', '|', ';', ' ', '\n'])
        .trim()
        .to_owned();
    let left = targets(&out);
    (!out.is_empty() && out != cmd && has(&left, "done") && !has(&left, "quick")).then_some(out)
}

/// The run a process is part of (feature 451 T153, moved here from the landing's `phase.rs`, T06, so every Phase line's writer reads it
/// one way): the outermost `make` above `pid` under `proc_root` (`/proc`), its first goal; None where no `make` is above it or its
/// command line names no goal. A word holding a space (`NOTE=two words`) is an assignment, as the event log's writer reads a command
/// (D1); a goal-less make (`invoked`'s `.DEFAULT_GOAL`, 451 T15) names none.
#[must_use]
pub fn outermost_goal(proc_root: &std::path::Path, pid: u32) -> Option<String> {
    let mut outer = None;
    let mut at = pid;
    while let Ok(stat) = std::fs::read_to_string(proc_root.join(at.to_string()).join("stat")) {
        let comm = std::fs::read_to_string(proc_root.join(at.to_string()).join("comm"))
            .unwrap_or_default();
        if ["make", "gmake"].contains(&comm.trim()) {
            outer = Some(at);
        }
        // the fields after the command's `)`: the state, then the parent
        at = stat
            .rfind(')')
            .and_then(|i| stat[i + 1..].split_whitespace().nth(1)?.parse().ok())
            .unwrap_or(0);
        if at <= 1 {
            break;
        }
    }
    let cmdline = |p: u32| std::fs::read(proc_root.join(p.to_string()).join("cmdline"));
    outer.and_then(|p| goal_of(&cmdline(p).unwrap_or_default()))
}

/// A make's first goal from its NUL-separated command line ([`outermost_goal`]).
fn goal_of(cmdline: &[u8]) -> Option<String> {
    let words: Vec<String> = cmdline
        .split(|b| *b == 0)
        .filter(|w| !w.is_empty())
        .map(|w| String::from_utf8_lossy(w).into_owned())
        .map(|w| {
            if w.contains(char::is_whitespace) {
                "QUOTED=1".to_owned()
            } else {
                w
            }
        })
        .collect();
    invoked(&words.join(" "))
        .into_iter()
        .next()
        .filter(|t| t != DEFAULT_GOAL)
}

#[cfg(test)]
mod tests;
