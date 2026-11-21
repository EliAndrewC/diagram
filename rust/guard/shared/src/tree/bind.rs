//! What a command's own text binds its variables to (451 T79's second round; its plan review, BLOCKED 2026-11-21, found the walk
//! reading a write word of which it knew nothing as not the mirror's, which let `echo x > $n.txt` and `for i in 1 2; do echo x >
//! $i.txt; done` write the mirror standing in it). Before the walk reads a command, each variable it reads is bound as bash binds
//! it where the text says how: a loop's literal values, each in a binding of its own; a name the command assigns twice, each value
//! in a binding of its own; a name no one assigns, empty (its value in the environment where that sets it; `CLAUDE_PROJECT_DIR`
//! and `OLDPWD` are unset in the Bash tool's shell, read 2026-11-21). A name given its value where the walk cannot read it - by
//! `read`, a loop over a substitution, a function's parameter, a sourced file - stays unknown, so the walk's one rule reads it
//! where the shell was last known (spec 204's D6). A single quote and a `\$` keep a `$` literal, as bash does.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{expand, re, strip_quote_chars, Env, ASSIGN};
use crate::shape::shlex;

/// The most bindings the walk reads one command in: past it, the names that would multiply them further are unknown (a loop's
/// nine values inside another's, 81, is past it).
const MAX_BINDINGS: usize = 64;

/// A value the walk cannot know: a name no command assigns, so every word holding it is unresolved.
pub(super) const UNREAD: &str = "$__unread__";

/// The words that lead a loop's, an `if`'s or a `while`'s body without being its command (451 T79's second round: `for f in a; do
/// cp /tmp/a <mirror>/x; done` and `if true; then touch <mirror>/y; fi` passed from `/tmp` at HEAD, their writes unseen).
pub(super) const KEYWORDS: [&str; 8] = ["do", "then", "else", "elif", "if", "while", "until", "!"];

/// A segment from its command on, its leading `KEYWORDS` dropped, so a guard reading a target's segment reads its command first
/// (451 T79's third round: `for F in a; do make append FILE=$F LINE=b; done` in a gated tree showed `do` as its head, and gate-write
/// refused a make it leaves to its target rule - 38 of the ux replay's commands, measured 2026-11-21).
pub(super) fn from_command(seg: &str) -> &str {
    let mut rest = seg.trim_start();
    while let Some((word, after)) = rest.split_once(char::is_whitespace) {
        if !KEYWORDS.contains(&word) {
            break;
        }
        rest = after.trim_start();
    }
    rest
}

/// Names bash sets itself as it runs, whatever the environment holds: unknown, never empty.
const BASH_SETS: [&str; 18] = [
    "BASHPID",
    "BASH_REMATCH",
    "BASH_SOURCE",
    "BASH_SUBSHELL",
    "DIRSTACK",
    "EPOCHREALTIME",
    "EPOCHSECONDS",
    "EUID",
    "FUNCNAME",
    "LINENO",
    "MAPFILE",
    "OPTARG",
    "OPTIND",
    "PIPESTATUS",
    "PPID",
    "RANDOM",
    "REPLY",
    "SECONDS",
];

/// A `NAME+=`, which appends to a value: unknown.
static APPEND: LazyLock<Regex> = LazyLock::new(|| re(r"(?:^|[^\w$])([A-Za-z_]\w*)\+="));
/// The next assignment of a chain after an assignment (`A=1 B=2`): `ASSIGN` reads only the first, so the rest are unknown. A
/// `NAME=` after a command's first word is its argument, never the shell's (`make plan-verdict F=413`, bx#31033's, measured
/// 2026-11-21: read as an assignment, it made the scratch `$F` before it unknown).
static CHAIN: LazyLock<Regex> =
    LazyLock::new(|| re(r#"^[ \t]+([A-Za-z_]\w*)=(?:"[^"\n]*"|'[^'\n]*'|[^\s;&|)]*)"#));
/// The words after `read`, `mapfile`, `readarray` and `getopts`, each name among them bound from input.
static READS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:^|[^\w-])(?:read|mapfile|readarray|getopts)\s([^;&|\n)]*)"));
static PRINTF_V: LazyLock<Regex> = LazyLock::new(|| re(r"\bprintf\s+-v\s+([A-Za-z_]\w*)"));
/// A `for` or `select` header: its name, and its word list where it has one (none iterates `"$@"`).
static LOOP: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(?:for|select)\s+([A-Za-z_]\w*)(?:\s+in\b([^;\n]*))?"));
/// A file sourced or a string evaluated: any name may be set there.
static SOURCED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:^|[;&|\n({]|\b(?:do|then|else))\s*(?:source|\.|eval)\s"));

/// How a read name is bound.
#[derive(Debug, Clone)]
enum Bound {
    /// Left for the walk: the command assigns it once (`env_from`), or the walk sets it (`HOME`, `PWD`, `OLDPWD`, a placeholder).
    Kept,
    /// Each of a loop's literal values, word-safe.
    Values(Vec<String>),
    /// Assigned more than once: each assignment (its name's offset) a binding of its own, the reads renamed to it.
    Assigned(Vec<usize>),
    Unknown,
    /// No one assigns it: the environment's value, or empty.
    Unset(String),
}

/// One `$NAME` or `${NAME...}` the shell expands: its span, its name and, braced, what follows the name inside the braces.
struct Read {
    start: usize,
    end: usize,
    name: String,
    op: Option<String>,
}

/// The spans of every name the shell expands in `text`: past a single-quoted span, a `\`-escaped character and `$$`.
fn reads(text: &str) -> Vec<Read> {
    let b = text.as_bytes();
    let (mut out, mut i, mut single, mut double) = (Vec::new(), 0, false, false);
    while i < b.len() {
        match b[i] {
            b'\'' if !double => single = !single,
            b'"' if !single => double = !double,
            b'\\' if !single => i += 1,
            b'$' if b.get(i + 1) == Some(&b'$') && !single => i += 1,
            b'$' if !single => {
                let braced = b.get(i + 1) == Some(&b'{');
                let at = (i + 1 + usize::from(braced)).min(b.len());
                let len = b[at..]
                    .iter()
                    .take_while(|c| c.is_ascii_alphanumeric() || **c == b'_')
                    .count();
                if len > 0 && !b[at].is_ascii_digit() {
                    let close = if braced {
                        text[at..].find('}').map_or(b.len(), |k| at + k)
                    } else {
                        at + len
                    };
                    let end = (close + usize::from(braced)).min(b.len());
                    let op = braced.then(|| text[at + len..close].to_owned());
                    out.push(Read {
                        start: i,
                        end,
                        name: text[at..at + len].to_owned(),
                        op,
                    });
                    i = end;
                    continue;
                }
            }
            _ => {}
        }
        i += 1;
    }
    out
}

/// A value as one word of a path: its blanks and shell characters `_` (a loop's `"sweet potato"` is one word), cut at a glob or a
/// brace, past which the walk knows only that it goes on.
fn word_safe(value: &str) -> String {
    let safe: String = value
        .chars()
        .map(|c| {
            if c.is_whitespace() || ";&|<>()'\"`".contains(c) {
                '_'
            } else {
                c
            }
        })
        .collect();
    match safe.find(['*', '?', '[', '{']) {
        Some(k) => format!("{}{UNREAD}", &safe[..k]),
        None => safe,
    }
}

/// A loop's word list as its values, or None where a word is a substitution or the list does not split.
fn loop_values(list: &str) -> Option<Vec<String>> {
    let words = shlex(list).filter(|w| !w.is_empty())?;
    words
        .iter()
        .map(|w| (!w.contains("$(") && !w.contains('`')).then(|| word_safe(w)))
        .collect()
}

/// How each name `text` reads is bound.
fn bindings(text: &str, read: &[Read]) -> HashMap<String, Bound> {
    let names = |p: &Regex| -> Vec<(String, usize)> {
        p.captures_iter(text)
            .map_while(Result::ok)
            .filter_map(|c| c.get(1).map(|m| (m.as_str().to_owned(), m.start())))
            .collect()
    };
    let clean = names(&ASSIGN);
    let mut unknown: HashSet<String> = names(&APPEND)
        .into_iter()
        .chain(names(&PRINTF_V))
        .map(|(n, _)| n)
        .collect();
    for c in ASSIGN.captures_iter(text).map_while(Result::ok) {
        let mut at = c.get(0).map_or(text.len(), |m| m.end());
        while let Some(m) = CHAIN.captures(&text[at..]).ok().flatten() {
            unknown.extend(m.get(1).map(|n| n.as_str().to_owned()));
            at += m.get(0).map_or(text.len() - at, |m| m.end());
        }
    }
    for (words, _) in names(&READS) {
        unknown.extend(words.split_whitespace().map(|w| {
            w.trim_matches(|c: char| !c.is_alphanumeric() && c != '_')
                .to_owned()
        }));
    }
    let mut values: HashMap<String, Vec<String>> = HashMap::new();
    for c in LOOP.captures_iter(text).map_while(Result::ok) {
        let name = c.get(1).map_or("", |m| m.as_str()).to_owned();
        if let Some(v) = c.get(2).and_then(|l| loop_values(l.as_str())) {
            values.entry(name).or_default().extend(v);
        } else {
            unknown.insert(name);
        }
    }
    let sourced = SOURCED.is_match(text).unwrap_or(false);
    let mut out = HashMap::new();
    for r in read {
        let n = r.name.as_str();
        let all: Vec<usize> = clean
            .iter()
            .filter(|(m, _)| m == n)
            .map(|(_, at)| *at)
            .collect();
        // an assignment that reads its own name gives it no value of its own: it follows the one before, as the walk's assignments
        // read in order (451 T79's third round: `S=/tmp/q; S=$S/sub; touch $S/f` read S from itself in the binding picking it)
        let at: Vec<usize> = all
            .iter()
            .copied()
            .filter(|k| !reads_itself(text, *k, n))
            .collect();
        let bound = if n.starts_with("__") || matches!(n, "HOME" | "PWD" | "OLDPWD") {
            Bound::Kept
        } else if unknown.contains(n) || BASH_SETS.contains(&n) {
            Bound::Unknown
        } else if let Some(v) = values.get(n) {
            // a loop's variable also assigned takes each literal value it is assigned beside its loop's (451 T79's third round:
            // ux#752's `f=research/...; sed -i ... $f` beside a `for f in ...` was read as unknown, its write of a gated tree unseen)
            let assigned: Option<Vec<String>> =
                all.iter().map(|k| literal_value(text, *k, n)).collect();
            assigned.map_or(Bound::Unknown, |a| {
                Bound::Values(v.iter().cloned().chain(a).collect())
            })
        } else if at.len() > 1 && distinct_values(text, &at) {
            Bound::Assigned(at)
        } else if !all.is_empty() {
            Bound::Kept
        } else if sourced {
            Bound::Unknown
        } else {
            Bound::Unset(crate::env::opt(n).map_or_else(String::new, |v| word_safe(&v)))
        };
        out.insert(r.name.clone(), bound);
    }
    out
}

/// Each assignment in a segment whose value reads `$PWD` or `$OLDPWD`, read where the walk stands at it, not at the command's start
/// (451 T79's third round: `cd <clone> && WT=$PWD; touch $WT/f` standing in the mirror was refused at HEAD, measured 2026-11-21).
pub(super) fn read_where_it_stands(seg: &str, env: &mut Env, home: &str) {
    for c in ASSIGN.captures_iter(seg).map_while(Result::ok) {
        let value = (2..=4).find_map(|i| c.get(i)).map_or("", |v| v.as_str());
        if let (Some(name), true) = (c.get(1), value.contains("PWD")) {
            if let Some(v) = expand(value, env, home) {
                env.insert(name.as_str().to_owned(), v);
            }
        }
    }
}

/// The value the assignment of `name` at this offset gives as written, its quotes off, where it is literal; None where it holds
/// a variable, a substitution, a glob, a brace, a quote inside or a blank.
fn literal_value(text: &str, at: usize, name: &str) -> Option<String> {
    let token = text[at..]
        .split(|c: char| c.is_whitespace() || c == ';')
        .next()
        .unwrap_or("");
    let v = token.get(name.len() + 1..)?;
    let inner = ['"', '\'']
        .iter()
        .find_map(|q| v.strip_prefix(*q).and_then(|w| w.strip_suffix(*q)))
        .unwrap_or(v);
    (!inner.contains([
        '$', '`', '*', '?', '[', '{', '"', '\'', '(', ')', '&', '|', '<', '>',
    ]))
    .then(|| inner.to_owned())
}

/// Whether the assignment of `name` at this offset reads the name itself (`S=$S/sub`, `S=${S}/a`, a prefix `S=$S cmd`).
fn reads_itself(text: &str, at: usize, name: &str) -> bool {
    let token = text[at..]
        .split(|c: char| c.is_whitespace() || c == ';')
        .next()
        .unwrap_or("");
    let value = token.get(name.len()..).unwrap_or("");
    [format!("${name}"), format!("${{{name}")].iter().any(|r| {
        value.match_indices(r.as_str()).any(|(i, _)| {
            !value[i + r.len()..].starts_with(|c: char| c.is_alphanumeric() || c == '_')
        })
    })
}

/// Whether the assignments at these offsets give their name more than one value as written.
fn distinct_values(text: &str, at: &[usize]) -> bool {
    let value = |k: usize| {
        text[k..]
            .split(|c: char| c.is_whitespace() || c == ';')
            .next()
            .unwrap_or("")
    };
    at.iter().any(|k| value(*k) != value(at[0]))
}

/// What a read becomes in one binding, `pick` the index of its name's value or assignment there; None where it stays as written.
/// `${NAME:?}` is NAME; `${NAME:-WORD}` WORD where no one assigns NAME; `${NAME%SUFFIX}`, a literal suffix holding no `/`, lies in
/// NAME's directory (bx#31289's `"${f%.xls}.txt"`, measured 2026-11-21); any other expansion is unknown.
fn replaced(r: &Read, bound: &Bound, pick: usize, text: &str) -> Option<String> {
    let op = r.op.as_deref().unwrap_or("");
    let plain = op.is_empty() || op.starts_with('?') || op.starts_with(":?");
    let default = ["-", ":-", "=", ":="]
        .iter()
        .find_map(|p| op.strip_prefix(p));
    let cut = op
        .strip_prefix('%')
        .is_some_and(|p| !p.contains(['/', '*', '?', '[']));
    let value = match bound {
        Bound::Values(v) => Some(v[pick].clone()),
        Bound::Unset(v) => Some(v.clone()),
        _ => None,
    };
    let name = match bound {
        Bound::Assigned(_) => format!("__v_{}", r.name),
        _ => r.name.clone(),
    };
    let new = match (bound, value) {
        (Bound::Unknown, _) => UNREAD.to_owned(),
        (_, Some(v)) if v.is_empty() => default.map_or_else(
            || {
                if plain || cut {
                    String::new()
                } else {
                    UNREAD.to_owned()
                }
            },
            |d| strip_quote_chars(d).to_owned(),
        ),
        _ if !plain && !cut && default.is_none() => UNREAD.to_owned(),
        (_, Some(v)) if cut => v
            .rsplit_once('/')
            .map_or_else(|| UNREAD.to_owned(), |(d, _)| format!("{d}/{UNREAD}")),
        (_, Some(v)) => v,
        _ if cut => format!("$(dirname ${{{name}}})/{UNREAD}"),
        (Bound::Kept, _) if op.is_empty() => return None,
        _ => format!("${{{name}}}"),
    };
    (new != text[r.start..r.end]).then_some(new)
}

/// The command's text once a binding: each many-valued name it reads at one of its values (every combination, up to
/// `MAX_BINDINGS`), each name no one assigns empty, each it cannot know `UNREAD`. One text where nothing it reads is many-valued.
pub(super) fn bound_texts(text: &str) -> Vec<String> {
    let read = reads(text);
    if read.is_empty() {
        return vec![text.to_owned()];
    }
    let mut bound = bindings(text, &read);
    let mut radix: Vec<(String, usize)> = Vec::new();
    for r in &read {
        let size = match &bound[&r.name] {
            Bound::Values(v) => v.len(),
            Bound::Assigned(a) => a.len(),
            _ => continue,
        };
        if radix.iter().any(|(n, _)| *n == r.name) {
        } else if radix.iter().map(|(_, s)| s).product::<usize>() * size > MAX_BINDINGS {
            bound.insert(r.name.clone(), Bound::Unknown);
        } else {
            radix.push((r.name.clone(), size));
        }
    }
    let total: usize = radix.iter().map(|(_, s)| s).product();
    (0..total)
        .map(|mut k| {
            let mut pick = HashMap::new();
            for (n, s) in &radix {
                pick.insert(n.as_str(), k % s);
                k /= s;
            }
            let mut edits: Vec<(usize, usize, String)> = read
                .iter()
                .filter_map(|r| {
                    let p = pick.get(r.name.as_str()).copied().unwrap_or(0);
                    replaced(r, &bound[&r.name], p, text).map(|new| (r.start, r.end, new))
                })
                .collect();
            for (n, p) in &pick {
                if let Bound::Assigned(at) = &bound[*n] {
                    edits.push((at[*p], at[*p] + n.len(), format!("__v_{n}")));
                }
            }
            edits.sort_by_key(|e| e.0);
            let mut out = String::with_capacity(text.len());
            let mut from = 0;
            for (s, e, new) in edits {
                out.push_str(&text[from..s]);
                out.push_str(&new);
                from = e;
            }
            out.push_str(&text[from..]);
            out
        })
        .collect()
}

/// Where `$(dirname X)` or `$(basename X [SUFFIX])` lands, X known whole (451 T79's second round: `mkdir -p $(dirname $F)` with F a
/// scratch path, bx#31033, #33626 and #55610, was read as nothing known); None for any other text or an X the walk cannot resolve.
pub(super) fn dir_base(inner: &str, env: &Env, home: &str) -> Option<String> {
    let words: Vec<&str> = inner.split_whitespace().collect();
    let base_of = match *words.first()? {
        "dirname" => false,
        "basename" => true,
        _ => return None,
    };
    if words.len() > 2 + usize::from(base_of) || words[1..].iter().any(|w| w.starts_with('-')) {
        return None;
    }
    let x = expand(strip_quote_chars(words.get(1)?), env, home).filter(|x| !x.is_empty())?;
    let t = x.trim_end_matches('/');
    if t.is_empty() {
        return Some("/".to_owned()); // `dirname /` and `basename /` alike
    }
    let (dir, base) = match t.rfind('/') {
        Some(k) => (if k == 0 { "/" } else { &t[..k] }, &t[k + 1..]),
        None => (".", t),
    };
    if !base_of {
        return Some(dir.to_owned());
    }
    let suffix = words.get(2).map_or("", |s| strip_quote_chars(s));
    Some(
        base.strip_suffix(suffix)
            .filter(|b| !b.is_empty())
            .unwrap_or(base)
            .to_owned(),
    )
}
