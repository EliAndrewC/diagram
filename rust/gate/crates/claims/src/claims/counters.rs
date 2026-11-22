//! The counter-only clear (feature 446, FR-003, plan D3; `scripts/record/claims_counters.py`): at `claims-owed` and `claims-triage`, a
//! claim owed a code triage only because its unit GAINED counter blocks since the version its check read is recorded cleared, with its
//! new fingerprints, and bundled nowhere. A `.rs` unit is read here (feature 449 T165, the GM 2026-11-17: the claims tools track the Rust
//! engine before S7 ports it); the `.py` unit's arm, asked of the Python (`ast`'s `if __debug__: OPS[...] +=`), left with the engine's
//! Python (feature 449 T158).
//!
//! THE RUST RULE. Cleared only when the recorded `code` is the merge base's version of the unit (its core rebuilt from the base text) and
//! the working unit is that version's tokens with counter statements only added - every counter statement of the base standing
//! unchanged, in its place. A COUNTER STATEMENT, at a statement's start (the body's first token, or after `{`, `;` or `}`):
//! - `#[cfg(feature = "counters")]` and the statement or block it gates: no map build enables the feature (the Makefile's `HAMLET_RUN`
//!   builds `rust/phases` without it; the GM 2026-11-07: "We should probably run with counters compiled out by default"), and
//!   `make counters-inert` holds every test equal in both builds - the Rust form of `if __debug__:` under `python -O`;
//! - `tally(<counts>, "<kind>@<function>", <value>);` - `tally`, `merge` or a `use ... tally as <alias>` (`hem.rs`'s `add`), by any path
//!   (`crate::counts::tally`) - and `merge(<counts>, <counts>);`, each `<counts>` a place whose last name is `counts`;
//! - `<...>.counts.add("<kind>@<function>", <value>);` (`Counts::add`).
//!
//! These calls run in every build (only their bodies compile out), so their arguments are held to what can only be read, as
//! `codeid._counter_value` held Python's (until feature 449 T247 deleted `codeid.py`): a key in the counters' `<kind>@<function>` form (feature 444 D9), and a value that is
//! numbers and places read, `.len()`, `as <integer type>`, `*`, `+` and parentheses - no other call, no indexing (it can panic), no `-`
//! (an underflow panics in a debug build). A counter that needs a new local (`tests += 1`) or a new parameter is code, and owed as before.
//! A Rust unit's core holds the value of each crate constant it reads (feature 449 T166, [`super::reads`]), so the base version's core is
//! rebuilt from the base item's tokens and the constants THOSE tokens read, at their values now: it equals the recorded code only where
//! no constant the unit read changed since its check, so a counter added beside a changed constant is never cleared, and a counter
//! reading a constant the base did not (`BINS as u64`) still clears - the Python's rule.

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::commands::Out;
use super::grammar::Claim;
use super::index::{
    body_of, live_rows, owed, save_index, Cur, Index, Store, CODE_TRIAGE, INDEX, QUESTIONS,
};
use super::units::{items, Unit};
use crate::record::repo::{git_show, read_text, Fail};
use crate::record::units::re;

/// What a claim cleared by the counter-only rule records (feature 446, FR-003).
const COUNTER_CLEARED: &str = "counter-only (feature 446)";
/// `#[cfg(feature = "counters")]`, as the lexer gives it.
const GATE: [&str; 9] = [
    "#",
    "[",
    "cfg",
    "(",
    "feature",
    "=",
    "\"counters\"",
    ")",
    "]",
];
static KEY: LazyLock<Regex> = LazyLock::new(|| re(r#"\A"[a-z_]+@[A-Za-z_][A-Za-z0-9_.]*"\z"#));
static ALIAS: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(tally|merge)\s+as\s+([A-Za-z_][A-Za-z0-9_]*)"));
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 2] = [&KEY, &ALIAS];
const INT_TYPES: [&str; 12] = [
    "u8", "u16", "u32", "u64", "u128", "usize", "i8", "i16", "i32", "i64", "i128", "isize",
];

/// At `owed` and `triage`: every claim owed a code triage only because counter blocks were added recorded cleared (feature 446, FR-003).
///
/// # Errors
///
/// Where the runner, a read or the index's write fails: the error says which and why.
pub fn counters_clear(
    root: &Path,
    cur: &Cur,
    index: Index,
    cmd: &str,
    o: &mut Out,
) -> Result<Index, Fail> {
    if cmd != "owed" && cmd != "triage" {
        return Ok(index);
    }
    let keys: Vec<String> = owed(
        cur,
        &index,
        Some(&root.join(QUESTIONS)),
        Some(&Store::new()),
    )?
    .into_iter()
    .filter(|(_, why)| why == CODE_TRIAGE)
    .map(|(k, _)| k)
    .collect();
    if keys.is_empty() {
        return Ok(index);
    }
    let base = crate::record::repo::git(root, &["merge-base", "HEAD", "origin/main"]);
    let base = l7r_shared::py_text::strip(&base).to_owned();
    if base.is_empty() {
        return Ok(index);
    }
    let mut done = Vec::new();
    let mut tables = super::context::Tables::default();
    for k in keys.iter().filter(|k| index.contains_key(*k)) {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let unit = &row.unit;
        // every unit here is a Rust item's, of a counter kind: `owed` names a line-keyed unit's change "code changed", never a
        // code triage, and a Rust item is always a function, method, class or constant (a `.py` unit's arm left with the Python,
        // feature 449 T158)
        let was = index[k].get("code").and_then(Value::as_str);
        let mut reads =
            |body: &str| super::reads::values(&mut tables, root, &unit.path, &unit.qualname, body);
        let cleared = git_show(root, &base, &unit.path).is_some_and(|old| {
            read_text(&root.join(&unit.path))
                .is_ok_and(|now| counter_only(&old, &now, unit, &row.claim, was, &mut reads))
        });
        if cleared {
            done.push(k.clone());
        }
    }
    let mut out = index;
    for k in &done {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let mut r = out
            .get(k)
            .and_then(Value::as_object)
            .cloned()
            .unwrap_or_default();
        r.insert("code".into(), json!(row.code));
        r.insert("core".into(), json!(row.unit.core));
        r.insert("body".into(), json!(body_of(root, &row.unit)?));
        super::reads::stamp(&mut r, Some(&row.unit.reads));
        r.insert("triaged".into(), json!(crate::record::bundle::today()));
        r.insert("cleared".into(), json!(COUNTER_CLEARED));
        r.shift_remove("triage");
        out.insert(k.clone(), Value::Object(r));
    }
    if !done.is_empty() {
        save_index(&root.join(INDEX), &live_rows(cur, &out))?;
        o.say(&format!("claims-{cmd}: {} claim(s) cleared without a triage - their units only gained counter blocks (feature 446, FR-003)", done.len()));
    }
    Ok(out)
}

/// Is `unit`, read from the working text `now`, the base text `old`'s version - the one `was` (its recorded code) fingerprints - with
/// counter statements only added? `reads` gives an item's constant values as its core holds them ([`super::reads::values`]).
#[must_use]
pub fn counter_only(
    old: &str,
    now: &str,
    unit: &Unit,
    claim: &Claim,
    was: Option<&str>,
    reads: &mut dyn FnMut(&str) -> String,
) -> bool {
    let find = |src: &str| {
        items(src, 0, "", false)
            .into_iter()
            .find(|it| it.0 == unit.qualname && it.1 == unit.kind)
            .map(|it| it.5)
    };
    let (Some(before), Some(after)) = (find(old), find(now)) else {
        return false;
    };
    let based = Unit {
        core: super::reads::core(&before, &reads(&before)),
        ..unit.clone()
    };
    if Some(based.code(claim).as_str()) != was {
        return false; // the recorded version is not the base's
    }
    let names = callees(&format!("{old}\n{now}"));
    let (bt, ht) = (lex(&before), lex(&after));
    let mut kept: HashMap<String, usize> = HashMap::new();
    for (a, b) in spans(&bt, &names) {
        *kept.entry(bt[a..b].join("\0")).or_default() += 1;
    }
    let mut rest: Vec<&str> = Vec::new();
    let mut at = 0;
    for (a, b) in spans(&ht, &names) {
        rest.extend(ht[at..a].iter().map(String::as_str));
        let n = kept.entry(ht[a..b].join("\0")).or_default();
        if *n > 0 {
            *n -= 1;
            rest.extend(ht[a..b].iter().map(String::as_str));
        }
        at = b;
    }
    rest.extend(ht[at..].iter().map(String::as_str));
    rest == bt
}

/// An item's tokens, comments dropped (the lexer the core is hashed from).
fn lex(body: &str) -> Vec<String> {
    let raw = crate::codeid::rust_tokens(body.as_bytes());
    String::from_utf8_lossy(&raw)
        .split('\0')
        .filter(|t| !t.is_empty())
        .map(str::to_owned)
        .collect()
}

/// The counter functions' names in a source: `tally`, `merge`, and what a `use` renames either to; each with the one it is.
fn callees(source: &str) -> HashMap<String, &'static str> {
    let mut out = HashMap::from([("tally".to_owned(), "tally"), ("merge".to_owned(), "merge")]);
    for c in ALIAS.captures_iter(source).map_while(Result::ok) {
        out.insert(
            c[2].to_owned(),
            if &c[1] == "tally" { "tally" } else { "merge" },
        );
    }
    out
}

/// Each counter statement of `t` as its token span, in order.
fn spans(t: &[String], names: &HashMap<String, &'static str>) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let mut i = 0;
    while i < t.len() {
        let start = i == 0 || matches!(t[i - 1].as_str(), "{" | ";" | "}");
        if let Some(end) = start.then(|| counter_at(t, i, names)).flatten() {
            out.push((i, end));
            i = end;
        } else {
            i += 1;
        }
    }
    out
}

/// Past the bracket that `t[open]` opens, or None where it never closes.
fn close(t: &[String], open: usize) -> Option<usize> {
    let mut depth = 0i64;
    for (k, tok) in t.iter().enumerate().skip(open) {
        match tok.as_str() {
            "(" | "[" | "{" => depth += 1,
            ")" | "]" | "}" => {
                depth -= 1;
                if depth == 0 {
                    return Some(k + 1);
                }
            }
            _ => {}
        }
    }
    None
}

/// Past the `;` ending the gated statement at `i`, its parentheses and brackets skipped; None where a brace opens first. A gated `if`,
/// `for` or `match` ends at its block with no `;`, so a scan to the next `;` would take the statement after it as gated too - in
/// `counts.rs`'s own idiom, the `#[cfg(not(feature = "counters"))]` twin, which the map build compiles in.
fn statement_end(t: &[String], i: usize) -> Option<usize> {
    let mut k = i;
    while k < t.len() {
        match t[k].as_str() {
            ";" => return Some(k + 1),
            "(" | "[" => k = close(t, k)?,
            "{" => return None,
            _ => k += 1,
        }
    }
    None
}

fn ident(tok: &str) -> bool {
    tok.starts_with(|c: char| c.is_alphabetic() || c == '_')
}

/// The counter statement at `i`, its end, or None.
fn counter_at(t: &[String], i: usize, names: &HashMap<String, &'static str>) -> Option<usize> {
    if t.len() >= i + GATE.len() && t[i..i + GATE.len()].iter().zip(GATE).all(|(a, b)| a == b) {
        let j = i + GATE.len();
        return if t.get(j).map(String::as_str) == Some("{") {
            close(t, j)
        } else {
            statement_end(t, j)
        };
    }
    // a path: names joined by `::` (the lexer's `:` `:`) or `.`
    let mut k = i;
    let mut path: Vec<&str> = Vec::new();
    loop {
        let name = t.get(k).filter(|s| ident(s))?;
        path.push(name);
        k += 1;
        match (
            t.get(k).map(String::as_str),
            t.get(k + 1).map(String::as_str),
        ) {
            (Some(":"), Some(":")) => k += 2,
            (Some("."), _) => k += 1,
            _ => break,
        }
    }
    if t.get(k).map(String::as_str) != Some("(") {
        return None;
    }
    let end = close(t, k)?;
    if t.get(end).map(String::as_str) != Some(";") {
        return None;
    }
    let args = split_args(&t[k + 1..end - 1]);
    let callee = path[path.len() - 1];
    let ok = if path.len() >= 2 && callee == "add" && path[path.len() - 2] == "counts" {
        args.len() == 2 && key(args[0]) && value(args[1])
    } else {
        match names.get(callee) {
            Some(&"tally") => args.len() == 3 && place(args[0]) && key(args[1]) && value(args[2]),
            Some(_) => args.len() == 2 && place(args[0]) && place(args[1]),
            None => false,
        }
    };
    ok.then_some(end + 1)
}

/// A call's arguments, split at their top-level commas (a trailing comma, rustfmt's, ends none).
fn split_args(t: &[String]) -> Vec<&[String]> {
    let mut out = Vec::new();
    let (mut from, mut depth) = (0, 0i64);
    for (k, tok) in t.iter().enumerate() {
        match tok.as_str() {
            "(" | "[" | "{" => depth += 1,
            ")" | "]" | "}" => depth -= 1,
            "," if depth == 0 => {
                out.push(&t[from..k]);
                from = k + 1;
            }
            _ => {}
        }
    }
    if from < t.len() {
        out.push(&t[from..]);
    }
    out
}

fn key(t: &[String]) -> bool {
    t.len() == 1 && KEY.is_match(&t[0]).unwrap_or(false)
}

/// `[&] [mut] <name>(.<name or field>)*`, its last name `counts`.
fn place(t: &[String]) -> bool {
    let mut k = usize::from(t.first().map(String::as_str) == Some("&"));
    k += usize::from(t.get(k).map(String::as_str) == Some("mut"));
    let (n, last) = path_read(t, k);
    n == t.len() && last == Some("counts")
}

/// A place read from `t[k]`: past it, and its last part.
fn path_read(t: &[String], k: usize) -> (usize, Option<&str>) {
    if !t.get(k).is_some_and(|s| ident(s) && s != "mut") {
        return (k, None);
    }
    let mut k = k + 1;
    while t.get(k).map(String::as_str) == Some(".")
        && t.get(k + 1)
            .is_some_and(|s| ident(s) || s.starts_with(|c: char| c.is_ascii_digit()))
        && t.get(k + 2).map(String::as_str) != Some("(")
    {
        k += 2;
    }
    (k, Some(t[k - 1].as_str()))
}

/// A value that can only be read: terms joined by `*` or `+`.
fn value(t: &[String]) -> bool {
    let mut k = 0;
    loop {
        let Some(next) = term(t, k) else { return false };
        k = next;
        match t.get(k).map(String::as_str) {
            None => return true,
            Some("*" | "+") => k += 1,
            Some(_) => return false,
        }
    }
}

/// A number, a place read (optionally `.len()`), or a parenthesized value; optionally cast `as` an integer type. Past it.
fn term(t: &[String], k: usize) -> Option<usize> {
    let tok = t.get(k)?;
    let mut k = if tok == "(" {
        let end = close(t, k)?;
        value(&t[k + 1..end - 1]).then_some(end)?
    } else if tok.starts_with(|c: char| c.is_ascii_digit()) {
        k + 1
    } else {
        let (n, last) = path_read(t, k);
        last?;
        let len = [".", "len", "(", ")"];
        if t.len() >= n + 4 && t[n..n + 4].iter().zip(len).all(|(a, b)| a == b) {
            n + 4
        } else {
            n
        }
    };
    if t.get(k).map(String::as_str) == Some("as") {
        INT_TYPES.contains(&t.get(k + 1)?.as_str()).then_some(())?;
        k += 2;
    }
    Some(k)
}

#[cfg(test)]
mod tests;
