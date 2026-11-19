//! The units claims sit on (`l7r/diagram/tools/claims.py`'s `Unit`, `doc_units` and `section_blocks`, and `claims_rust.py` whole, ported
//! by feature 449 T82): a Mode A procedure section, and a Rust item read from its doc comments. A `.py` unit comes from the Python's own
//! reader through the runner ([`super::scope`]), its fingerprint being `CPython`'s `ast.dump` (`ask:449-T82-claims`).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{collapse, strip};
use l7r_guard::shared::sha256;
use serde_json::Value;

use super::grammar::{claims_of, lstrip, parse_claim, Claim};
use crate::record::repo::Fail;
use crate::record::units::re;

/// `hashlib.sha256(text.encode()).hexdigest()[:16]`.
pub fn sha(text: &str) -> String {
    sha256::hex(text.as_bytes())[..16].to_owned()
}

/// A function, method, class, constant or procedure section, with its claims (own or inherited) and its code's core.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Unit {
    pub path: String,
    pub qualname: String,
    pub kind: String,
    pub lineno: usize,
    pub end_lineno: usize,
    pub claims: Vec<Claim>,
    pub inherited: bool,
    pub core: String,
    pub errors: Vec<String>,
    pub names: Vec<String>,
    pub blocks: Vec<String>,
    /// A Rust unit's constant reads as its core holds them, fingerprinted; empty where it reads none, and for any other unit (feature 449
    /// T166). A check records it on the row, so a changed value owes the claim though the unit's text is unchanged.
    pub reads: String,
}

/// A unit and its module's errors, as the Python's `all_units` yields them.
pub type Pair = (Unit, Vec<String>);

impl Unit {
    /// Its claims fingerprinted by their own line: a procedure section, and a claimed dictionary (feature 385 T83).
    pub fn line_keyed(&self) -> bool {
        self.kind == "section" || !self.blocks.is_empty()
    }

    /// `path::qualname`.
    pub fn uid(&self) -> String {
        format!("{}::{}", self.path, self.qualname)
    }

    /// The index key of one claim of this unit.
    pub fn key(&self, claim: &Claim) -> String {
        format!("{}::{}#{}", self.path, self.qualname, claim.label)
    }

    /// The code fingerprint of one claim: the core plus the normalized claim line, or a line-keyed claim's own line alone.
    pub fn code(&self, claim: &Claim) -> String {
        if self.line_keyed() {
            return sha(&format!("section-claim\x1f{}", claim.normalized()));
        }
        sha(&format!("{}\x1f{}", self.core, claim.normalized()))
    }
}

fn strings(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .map(|s| s.as_str().unwrap_or_default().to_owned())
                .collect()
        })
        .unwrap_or_default()
}

fn text(v: &Value, key: &str) -> String {
    v.get(key)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

fn number(v: &Value, key: &str) -> usize {
    v.get(key)
        .and_then(Value::as_u64)
        .and_then(|n| usize::try_from(n).ok())
        .unwrap_or_default()
}

/// A unit as `tools/claims.unit_json` gives it, with its module's errors; its claim lines parsed again (each parsed once already).
pub fn from_json(v: &Value) -> Pair {
    let claims = strings(v, "claims")
        .iter()
        .filter_map(|l| parse_claim(l).ok())
        .collect();
    (
        Unit {
            path: text(v, "path"),
            qualname: text(v, "qualname"),
            kind: text(v, "kind"),
            lineno: number(v, "lineno"),
            end_lineno: number(v, "end_lineno"),
            claims,
            inherited: v.get("inherited").and_then(Value::as_bool).unwrap_or(false),
            core: text(v, "core"),
            errors: strings(v, "errors"),
            names: strings(v, "names"),
            blocks: strings(v, "blocks"),
            reads: String::new(),
        },
        strings(v, "module_errors"),
    )
}

/// The unit as the runner's verbs take it back (`claims_counters.counter_only_json`).
pub fn to_json(u: &Unit) -> Value {
    serde_json::json!({
        "path": u.path, "qualname": u.qualname, "kind": u.kind, "lineno": u.lineno, "end_lineno": u.end_lineno,
        "claims": u.claims.iter().map(|c| c.line.clone()).collect::<Vec<_>>(), "inherited": u.inherited, "core": u.core,
        "errors": u.errors, "names": u.names, "blocks": u.blocks,
    })
}

/// The Mode A procedure documents (spec FR-003, plan D9): None takes every section; a list takes those top sections and every heading under them.
pub const PROCEDURES: [(&str, Option<&[&str]>); 2] = [
    ("docs/buildings.md", None),
    (
        "docs/building-programs.md",
        Some(&[
            "Magistrate's manor (county magistracy)",
            "Country shrine (a village district's shrine)",
        ]),
    ),
];

static MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--\s*Research:\s*(.*?)\s*-->"));
pub static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"\A(#{1,6})\s+(.*?)\s*\z"));
static LIST_ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"\A\s{0,3}(?:[-*+]|\d+[.)])\s"));

fn heading(line: &str) -> Option<(usize, String)> {
    let c = HEADING.captures(line).ok().flatten()?;
    Some((c[1].len(), c[2].to_owned()))
}

/// The sections of one procedure document as units: every `##`-`####` heading, or only those under `tops`.
pub fn doc_units(text: &str, path: &str, tops: Option<&[&str]>) -> Vec<Unit> {
    let lines: Vec<&str> = text.split('\n').collect();
    let heads: Vec<(usize, usize, String)> = lines
        .iter()
        .enumerate()
        .filter_map(|(i, l)| heading(l).map(|(level, title)| (i, level, title)))
        .collect();
    let mut units = Vec::new();
    let mut taking: Option<usize> = None;
    for (j, (i, level, title)) in heads.iter().enumerate() {
        if let Some(tops) = tops {
            if tops.contains(&title.as_str()) {
                taking = Some(*level);
            } else if taking.is_some_and(|t| *level <= t) {
                taking = None;
            }
            if taking.is_none() {
                continue;
            }
        } else if *level < 2 || *level > 4 {
            continue;
        }
        let end = heads.get(j + 1).map_or(lines.len(), |h| h.0);
        let body = lines[i + 1..end].join("\n");
        let (mut claims, mut errors) = (Vec::new(), Vec::new());
        for c in MARKER.captures_iter(&body).map_while(Result::ok) {
            match parse_claim(&c[1]) {
                Ok(claim) => claims.push(claim),
                Err(e) => errors.push(e),
            }
        }
        let core = sha(&collapse(&COMMENT.replace_all(&body, " ")));
        units.push(Unit {
            path: path.to_owned(),
            qualname: title.clone(),
            kind: "section".to_owned(),
            lineno: i + 1,
            end_lineno: end,
            claims,
            inherited: false,
            core,
            errors,
            names: Vec::new(),
            blocks: section_blocks(&body),
            reads: String::new(),
        });
    }
    units
}

/// A procedure section's blocks, each with its whitespace folded and its comments out (feature 375, FR-002).
pub fn section_blocks(body: &str) -> Vec<String> {
    let mut out: Vec<Vec<String>> = Vec::new();
    for raw in COMMENT.replace_all(body, " ").split('\n') {
        let line = strip(raw);
        if line.is_empty() || line.chars().all(|c| "|-: ".contains(c)) {
            out.push(Vec::new());
            continue;
        }
        let starts = line.starts_with(['|', '#']) || LIST_ITEM.is_match(raw).unwrap_or(false);
        let after_table = out
            .last()
            .and_then(|b| b.first())
            .is_none_or(|first| first.starts_with(['|', '#']));
        if starts || after_table {
            out.push(vec![line.to_owned()]);
        } else if let Some(last) = out.last_mut() {
            last.push(line.to_owned());
        }
    }
    out.iter()
        .filter(|b| !b.is_empty())
        .map(|b| collapse(&b.join(" ")))
        .collect()
}

static ITEM: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"\A\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:const|async|unsafe|extern\s+"C")\s+)*(fn|struct|enum|trait|impl|const|static|type|mod)\b\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)?"#,
    )
});
static IMPL_FOR: LazyLock<Regex> = LazyLock::new(|| re(r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)"));
static IMPL_OF: LazyLock<Regex> =
    LazyLock::new(|| re(r"impl\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)"));
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 7] = [
    &MARKER, &COMMENT, &HEADING, &LIST_ITEM, &ITEM, &IMPL_FOR, &IMPL_OF,
];

/// `str.splitlines(keepends=True)`.
pub fn splitlines_keep(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut chars = text.chars().peekable();
    while let Some(c) = chars.next() {
        cur.push(c);
        let ends = match c {
            '\r' => {
                if chars.peek() == Some(&'\n') {
                    cur.push('\n');
                    chars.next();
                }
                true
            }
            '\n' | '\x0b' | '\x0c' | '\x1c' | '\x1d' | '\x1e' | '\u{85}' | '\u{2028}'
            | '\u{2029}' => true,
            _ => false,
        };
        if ends {
            out.push(std::mem::take(&mut cur));
        }
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

/// `str.splitlines()`.
pub fn splitlines(text: &str) -> Vec<String> {
    const ENDS: &str = "\r\n\x0b\x0c\x1c\x1d\x1e\u{85}\u{2028}\u{2029}";
    splitlines_keep(text)
        .into_iter()
        .map(|l| {
            if let Some(s) = l.strip_suffix("\r\n") {
                return s.to_owned();
            }
            l.strip_suffix(|c: char| ENDS.contains(c))
                .map_or_else(|| l.clone(), str::to_owned)
        })
        .collect()
}

/// Past the item that opens at char `start`: its matching `}`, or the `;` ending a body-less item - strings, chars and comments skipped.
fn item_end(text: &[char], start: usize) -> usize {
    let len = text.len();
    let (mut at, mut depth, mut nest) = (start, 0i64, 0i64);
    let find = |from: usize, needle: &[char]| (from..len).find(|&k| text[k..].starts_with(needle));
    while at < len {
        let ch = text[at];
        if text[at..].starts_with(&['/', '/']) {
            at = find(at, &['\n']).unwrap_or(len);
            continue;
        }
        if text[at..].starts_with(&['/', '*']) {
            at = find(at + 2, &['*', '/']).map_or(len, |k| k + 2);
            continue;
        }
        // A raw literal (`r"..."`, `r#"..."#`, `br#"..."#`) ends at a quote followed by its own hashes, and a backslash inside
        // escapes nothing: read as a plain string, its first inner quote closed it and the unit ran on past the next items,
        // which then had no key (feature 449 T172, found by T170's claims round).
        if let Some(close) = raw_literal_end(text, at) {
            at = close;
            continue;
        }
        if ch == '"' {
            let mut k = at + 1;
            while k < len && text[k] != '"' {
                k += if text[k] == '\\' { 2 } else { 1 };
            }
            at = k + 1;
            continue;
        }
        if ch == '\'' && at + 2 < len && (text[at + 2] == '\'' || text[at + 1] == '\\') {
            at = find(at + 2, &['\'']).map_or(len, |k| k + 1);
            continue;
        }
        match ch {
            '{' => depth += 1,
            '}' => {
                depth -= 1;
                if depth == 0 {
                    return at + 1;
                }
            }
            '(' | '[' => nest += 1,
            ')' | ']' => nest -= 1,
            ';' if depth == 0 && nest == 0 => return at + 1,
            _ => {}
        }
        at += 1;
    }
    len
}

/// Past the raw string literal opening at char `at` (`r`, or `br`, then hashes and a quote), or None where none opens there - an
/// `r` ending an identifier (`for"` cannot occur, but `bar#` style tokens must not read as one) opens nothing.
fn raw_literal_end(text: &[char], at: usize) -> Option<usize> {
    let ident = |c: char| c.is_alphanumeric() || c == '_';
    if at > 0 && ident(text[at - 1]) {
        return None;
    }
    let mut k = at;
    if text.get(k) == Some(&'b') {
        k += 1;
    }
    if text.get(k) != Some(&'r') {
        return None;
    }
    k += 1;
    let hashes = text[k..].iter().take_while(|&&c| c == '#').count();
    k += hashes;
    if text.get(k) != Some(&'"') {
        return None;
    }
    let mut j = k + 1;
    while j < text.len() {
        if text[j] == '"'
            && text[j + 1..]
                .iter()
                .take(hashes)
                .filter(|&&c| c == '#')
                .count()
                == hashes
        {
            return Some(j + 1 + hashes);
        }
        j += 1;
    }
    Some(text.len())
}

/// One Rust item: (qualname, kind, first line, last line, doc, item text).
pub type Item = (String, String, usize, usize, String, String);

fn bracket_balance(line: &str) -> i64 {
    let count = |c: char| i64::try_from(line.matches(c).count()).unwrap_or(0);
    count('[') - count(']')
}

/// Each item in `text`, an `impl` block's methods inside it (`claims_rust._items`).
pub fn items(text: &str, base_line: usize, prefix: &str, in_impl: bool) -> Vec<Item> {
    let chars: Vec<char> = text.chars().collect();
    let lines = splitlines_keep(text);
    let mut offsets = vec![0usize];
    for line in &lines {
        offsets.push(offsets[offsets.len() - 1] + line.chars().count());
    }
    let mut out = Vec::new();
    let mut doc: Vec<String> = Vec::new();
    let mut k = 0;
    while k < lines.len() {
        let stripped = strip(&lines[k]);
        if let Some(rest) = stripped.strip_prefix("///") {
            doc.push(rest.strip_prefix(' ').unwrap_or(rest).to_owned());
            k += 1;
            continue;
        }
        if stripped.starts_with("#[") || stripped.starts_with("#![") {
            let mut depth = 0;
            while k < lines.len() {
                depth += bracket_balance(&lines[k]);
                k += 1;
                if depth <= 0 {
                    break;
                }
            }
            continue;
        }
        let Some(m) = ITEM.captures(&lines[k]).ok().flatten() else {
            if !stripped.is_empty() && !stripped.starts_with("//") {
                doc.clear();
            }
            k += 1;
            continue;
        };
        let start = offsets[k];
        let end = item_end(&chars, start);
        let last = (k..lines.len())
            .find(|&i| offsets[i + 1] >= end)
            .unwrap_or(lines.len() - 1);
        let body: String = chars[start..end].iter().collect();
        let (word, name) = (&m[1], m.get(2).map_or("", |g| g.as_str()));
        if word == "impl" {
            let head = body.split('{').next().unwrap_or_default();
            let target = IMPL_FOR
                .captures(head)
                .ok()
                .flatten()
                .or_else(|| IMPL_OF.captures(&body).ok().flatten())
                .map(|c| c[1].to_owned());
            let body_chars: Vec<char> = body.chars().collect();
            let inner = body_chars.iter().position(|&c| c == '{');
            if let (Some(target), Some(inner)) = (target, inner) {
                let head_lines = body_chars[..=inner].iter().filter(|&&c| c == '\n').count();
                let stop = body_chars.len().saturating_sub(1).max(inner + 1);
                let inside: String = body_chars[inner + 1..stop].iter().collect();
                out.extend(items(
                    &inside,
                    base_line + k + head_lines,
                    &format!("{prefix}{target}."),
                    true,
                ));
            }
        } else if word != "mod" && !name.is_empty() {
            let kind = match word {
                "fn" if in_impl => "method",
                "fn" => "function",
                "const" | "static" => "constant",
                _ => "class",
            };
            out.push((
                format!("{prefix}{name}"),
                kind.to_owned(),
                base_line + k + 1,
                base_line + last + 1,
                doc.join("\n"),
                body,
            ));
        }
        doc.clear();
        k = last + 1;
    }
    out
}

/// A Rust item's core: its comment-free tokens, hashed (the counter-only clear rebuilds a base version's by it, feature 449 T165).
pub fn rust_core(body: &str) -> String {
    sha(&String::from_utf8_lossy(&crate::codeid::rust_tokens(
        body.as_bytes(),
    )))
}

/// (the file's errors, its units) for one `.rs` source text: each item's own claims, else the `//!` module doc's, inherited. Each core
/// is the item's tokens alone; [`all_rust_units`] adds the constants it reads (feature 449 T166), and is the one reader outside the tests.
#[cfg(test)]
pub fn rust_units(source: &str, path: &str) -> (Vec<String>, Vec<Unit>) {
    let (errors, units) = rust_units_with_bodies(source, path);
    (errors, units.into_iter().map(|(u, _)| u).collect())
}

/// [`rust_units`], each unit with its item's text.
fn rust_units_with_bodies(source: &str, path: &str) -> (Vec<String>, Vec<(Unit, String)>) {
    let module_doc = splitlines(source)
        .iter()
        .filter_map(|l| {
            strip(l)
                .strip_prefix("//!")
                .map(|r| r.strip_prefix(' ').unwrap_or(r).to_owned())
        })
        .collect::<Vec<_>>()
        .join("\n");
    let (mod_claims, mod_errors) = claims_of(Some(&module_doc));
    let mut units = Vec::new();
    for (qual, kind, first, last, doc, body) in items(source, 0, "", false) {
        let (claims, errors) = claims_of(Some(&doc));
        let inherited = claims.is_empty() && errors.is_empty();
        let unit = Unit {
            path: path.to_owned(),
            qualname: qual,
            kind,
            lineno: first,
            end_lineno: last,
            claims: if claims.is_empty() && inherited {
                mod_claims.clone()
            } else {
                claims
            },
            inherited,
            core: rust_core(&body),
            errors,
            names: Vec::new(),
            blocks: Vec::new(),
            reads: String::new(),
        };
        units.push((unit, body));
    }
    (mod_errors, units)
}

/// Every file under `dir` whose name ends `suffix`, in the order Python's `sorted(dir.rglob(...))` gives (component by component); symlinked directories not followed.
pub fn rglob(dir: &Path, suffix: &str) -> Vec<std::path::PathBuf> {
    fn walk(dir: &Path, suffix: &str, out: &mut Vec<std::path::PathBuf>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for e in entries.flatten() {
            let p = e.path();
            let Ok(t) = e.file_type() else { continue };
            if t.is_dir() {
                walk(&p, suffix, out);
            }
            if e.file_name().to_string_lossy().ends_with(suffix) && !t.is_dir() {
                out.push(p);
            }
        }
    }
    let mut out = Vec::new();
    walk(dir, suffix, &mut out);
    out.sort_by(|a, b| a.components().cmp(b.components()));
    out
}

/// A path relative to `root`, with `/`.
pub fn rel(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

/// Whether the claims walk reads a `.rs` file at `inner`, its path under `rust/`: every crate there but `target/`, the parked stages and
/// the tooling crates - the guard, the gate, the browser program (feature 449 T146) and the embedder (T138), which hold no research
/// claims. A crate NEW under `rust/` is walked with no list to join, so the engine's slices (S7-S12) port into crates beside
/// `rust/phases` and their claims are tracked from their first commit (feature 449 T165) - and every unit of it owes a claim from that
/// commit: its own `Research:` line, or a module-level one its units inherit (`- NONE` where the file decides nothing physical), which
/// `make static`'s form check names (`claims coverage --rust`, feature 449 T169). The stale-figure check asks this same test.
pub fn walked(inner: &str) -> bool {
    let parts: Vec<&str> = inner.split('/').collect();
    !(parts.contains(&"target")
        || ["parked", "guard", "gate", "browser", "embed"].contains(&parts[0]))
}

/// Every unit of every `.rs` under `rust/` the walk reads ([`walked`]), with its file's errors. With `reads`, each core holds the value of
/// every crate constant the unit reads ([`super::reads`], feature 449 T166); without, the fingerprint before T166, which only
/// `claims refingerprint` asks for, to carry the rows still at it.
pub fn all_rust_units(root: &Path, repo_prefix: &str, reads: bool) -> Result<Vec<Pair>, Fail> {
    let base = root.join("rust");
    let mut out = Vec::new();
    let mut tables = super::context::Tables::default();
    for p in rglob(&base, ".rs") {
        if !walked(&rel(&p, &base)) {
            continue;
        }
        let text = crate::record::repo::read_text(&p)?;
        let path = rel(&p, root);
        let (errors, units) = rust_units_with_bodies(&text, &format!("{repo_prefix}{path}"));
        for (mut u, body) in units {
            if reads {
                let vals = super::reads::values(&mut tables, root, &path, &u.qualname, &body);
                u.core = super::reads::core(&body, &vals);
                if !vals.is_empty() {
                    u.reads = sha(&vals);
                }
            }
            out.push((u, errors.clone()));
        }
    }
    Ok(out)
}

/// `lstrip` re-exported for the readers of a unit's source lines.
pub fn lstripped(text: &str) -> &str {
    lstrip(text)
}

#[cfg(test)]
mod tests;
