//! The make invocations a command makes (`scripts/hooks/lib/hm_make.py`, the parts `gate-hooks` reads - feature 449 T007 decision
//! (a)): the targets it INVOKES, a mention never one; and the quick-and-done combination. Each pattern is the Python's verbatim (research
//! R8); the rest of `hm_make.py` moves with the guards that read it (T028, T029). `classify`'s verdict through a bare pytest and the view
//! it read a command by left with pytest (feature 449 T213).

use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::shape::{strip_heredocs, strip_quotes};

/// A command position: the start, or after `;`, `|`, `&&`, `||` or a newline, past `timeout N`, `env` and `VAR=value` prefixes.
pub(crate) const POS: &str =
    r"(?:^|[\n;|]|&&|\|\|)\s*(?:timeout\s+\S+\s+|env\s+|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*";
/// A Python interpreter, by any path.
pub(crate) const PY: &str = r"(?:\S*/)?python3?";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern)
        .unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

static TARGET: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"{POS}(?:\$\(MAKE\)|make)\s+(?:-\S+(?:\s+\S+)?\s+)*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*([a-z][\w-]*)"
    ))
});
static GOALS: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"{POS}(?:\$\(MAKE\)|make)((?:\s+(?:-\S+|[A-Za-z_][A-Za-z0-9_]*=\S*|[./~]\S*|[a-z][\w-]*))*)"
    ))
});
static GOAL: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z][\w-]*$"));
static SEP: LazyLock<Regex> = LazyLock::new(|| re(r"\s*(?:&&|\|\||;|\n)\s*"));
static MAKE_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\$\(MAKE\)|make)\b"));
static QUICK: LazyLock<Regex> = LazyLock::new(|| re(r"\s+quick\b"));

/// The arguments `-C dir` and `-f file` take, never goals.
const TAKES_ARG: [&str; 8] = [
    "-C",
    "-f",
    "--directory",
    "--file",
    "--makefile",
    "-o",
    "--old-file",
    "-W",
];

/// Every make TARGET `cmd` INVOKES (`targets`): heredocs and quoted strings blanked, a target counted only at a command position,
/// past any flags and `VAR=value` prefixes - the first goal of each call.
#[must_use]
pub fn targets(cmd: &str) -> BTreeSet<String> {
    // NO `make`, NO PATTERN (T007, measured 2026-11-08): a hook call is a process, so each pattern compiles on every call - 4.6 ms
    // of a plain `ls`'s 11.4 - and a target needs `make` or `$(MAKE)` spelled in the command
    if !cmd.contains("make") && !cmd.contains("MAKE") {
        return BTreeSet::new();
    }
    let clean = strip_quotes(&strip_heredocs(cmd));
    TARGET
        .captures_iter(&clean)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// Every goal of every make call in `seg` (`_goals`), an argument of `-C`/`-f` never one.
fn goals(seg: &str) -> BTreeSet<String> {
    let clean = strip_quotes(&strip_heredocs(seg));
    let mut out = BTreeSet::new();
    for c in GOALS.captures_iter(&clean).map_while(Result::ok) {
        let mut skip = false;
        for word in c.get(1).map_or("", |m| m.as_str()).split_whitespace() {
            if std::mem::take(&mut skip) {
                continue;
            }
            if TAKES_ARG.contains(&word) {
                skip = true;
            } else if GOAL.is_match(word).unwrap_or(false) {
                out.insert(word.to_owned());
            }
        }
    }
    out
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
        || !cmd.contains("quick")
        || !cmd.contains("done")
    {
        return None;
    }
    let all = goals(cmd);
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
        let got = goals(seg);
        let makeish = MAKE_HEAD.is_match(seg.trim()).unwrap_or(false) && balanced(seg);
        if makeish && has(&got, "quick") && !has(&got, "done") {
            dropped = true;
            continue;
        }
        if makeish && has(&got, "quick") && has(&got, "done") {
            let rebuilt = QUICK.replace(seg, "").into_owned();
            let mut want = got.clone();
            want.remove("quick");
            if goals(&rebuilt) != want {
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
    let left = goals(&out);
    (!out.is_empty() && out != cmd && has(&left, "done") && !has(&left, "quick")).then_some(out)
}

#[cfg(test)]
mod tests;
