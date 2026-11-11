//! The units claims sit on (`l7r/diagram/tools/claims.py`'s `Unit`, `doc_units` and `section_blocks`, and `claims_rust.py` whole, ported
//! by feature 449 T82): a Mode A procedure section, and a Rust item read from its doc comments. A `.py` unit comes from the Python's own
//! reader through the runner ([`super::scope`]), its fingerprint being CPython's `ast.dump` (`ask:449-T82-claims`).

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
pub(crate) fn sha(text: &str) -> String {
    sha256::hex(text.as_bytes())[..16].to_owned()
}

/// A function, method, class, constant or procedure section, with its claims (own or inherited) and its code's core.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Unit {
    pub(crate) path: String,
    pub(crate) qualname: String,
    pub(crate) kind: String,
    pub(crate) lineno: usize,
    pub(crate) end_lineno: usize,
    pub(crate) claims: Vec<Claim>,
    pub(crate) inherited: bool,
    pub(crate) core: String,
    pub(crate) errors: Vec<String>,
    pub(crate) names: Vec<String>,
    pub(crate) blocks: Vec<String>,
}

/// A unit and its module's errors, as the Python's `all_units` yields them.
pub(crate) type Pair = (Unit, Vec<String>);

impl Unit {
    /// Its claims fingerprinted by their own line: a procedure section, and a claimed dictionary (feature 385 T83).
    pub(crate) fn line_keyed(&self) -> bool {
        self.kind == "section" || !self.blocks.is_empty()
    }

    /// `path::qualname`.
    pub(crate) fn uid(&self) -> String {
        format!("{}::{}", self.path, self.qualname)
    }

    /// The index key of one claim of this unit.
    pub(crate) fn key(&self, claim: &Claim) -> String {
        format!("{}::{}#{}", self.path, self.qualname, claim.label)
    }

    /// The code fingerprint of one claim: the core plus the normalized claim line, or a line-keyed claim's own line alone.
    pub(crate) fn code(&self, claim: &Claim) -> String {
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
pub(crate) fn from_json(v: &Value) -> Pair {
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
        },
        strings(v, "module_errors"),
    )
}

/// The unit as the runner's verbs take it back (`claims_counters.counter_only_json`).
pub(crate) fn to_json(u: &Unit) -> Value {
    serde_json::json!({
        "path": u.path, "qualname": u.qualname, "kind": u.kind, "lineno": u.lineno, "end_lineno": u.end_lineno,
        "claims": u.claims.iter().map(|c| c.line.clone()).collect::<Vec<_>>(), "inherited": u.inherited, "core": u.core,
        "errors": u.errors, "names": u.names, "blocks": u.blocks,
    })
}

/// The Mode A procedure documents (spec FR-003, plan D9): None takes every section; a list takes those top sections and every heading under them.
pub(crate) const PROCEDURES: [(&str, Option<&[&str]>); 2] = [
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
pub(crate) static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"\A(#{1,6})\s+(.*?)\s*\z"));
static LIST_ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"\A\s{0,3}(?:[-*+]|\d+[.)])\s"));

fn heading(line: &str) -> Option<(usize, String)> {
    let c = HEADING.captures(line).ok().flatten()?;
    Some((c[1].len(), c[2].to_owned()))
}

/// The sections of one procedure document as units: every `##`-`####` heading, or only those under `tops`.
pub(crate) fn doc_units(text: &str, path: &str, tops: Option<&[&str]>) -> Vec<Unit> {
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
        for c in MARKER.captures_iter(&body).flatten() {
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
        });
    }
    units
}

/// A procedure section's blocks, each with its whitespace folded and its comments out (feature 375, FR-002).
pub(crate) fn section_blocks(body: &str) -> Vec<String> {
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
    re(r#"\A\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:const|async|unsafe|extern\s+"C")\s+)*(fn|struct|enum|trait|impl|const|static|type|mod)\b\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)?"#)
});
static IMPL_FOR: LazyLock<Regex> = LazyLock::new(|| re(r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)"));
static IMPL_OF: LazyLock<Regex> =
    LazyLock::new(|| re(r"impl\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)"));

/// `str.splitlines(keepends=True)`.
pub(crate) fn splitlines_keep(text: &str) -> Vec<String> {
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
            '\n' | '\x0b' | '\x0c' | '\x1c' | '\x1d' | '\x1e' | '\u{85}' | '\u{2028}' | '\u{2029}' => {
                true
            }
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
pub(crate) fn splitlines(text: &str) -> Vec<String> {
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
fn item_end(s: &[char], start: usize) -> usize {
    let n = s.len();
    let (mut i, mut depth, mut nest) = (start, 0i64, 0i64);
    let find = |from: usize, needle: &[char]| {
        (from..n).find(|&j| s[j..].starts_with(needle))
    };
    while i < n {
        let c = s[i];
        if s[i..].starts_with(&['/', '/']) {
            i = find(i, &['\n']).unwrap_or(n);
            continue;
        }
        if s[i..].starts_with(&['/', '*']) {
            i = find(i + 2, &['*', '/']).map_or(n, |j| j + 2);
            continue;
        }
        if c == '"' {
            let mut j = i + 1;
            while j < n && s[j] != '"' {
                j += if s[j] == '\\' { 2 } else { 1 };
            }
            i = j + 1;
            continue;
        }
        if c == '\'' && i + 2 < n && (s[i + 2] == '\'' || s[i + 1] == '\\') {
            i = find(i + 2, &['\'']).map_or(n, |j| j + 1);
            continue;
        }
        match c {
            '{' => depth += 1,
            '}' => {
                depth -= 1;
                if depth == 0 {
                    return i + 1;
                }
            }
            '(' | '[' => nest += 1,
            ')' | ']' => nest -= 1,
            ';' if depth == 0 && nest == 0 => return i + 1,
            _ => {}
        }
        i += 1;
    }
    n
}

/// One Rust item: (qualname, kind, first line, last line, doc, item text).
pub(crate) type Item = (String, String, usize, usize, String, String);

fn bracket_balance(line: &str) -> i64 {
    let count = |c: char| i64::try_from(line.matches(c).count()).unwrap_or(0);
    count('[') - count(']')
}

/// Each item in `text`, an `impl` block's methods inside it (`claims_rust._items`).
pub(crate) fn items(text: &str, base_line: usize, prefix: &str, in_impl: bool) -> Vec<Item> {
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

/// (the file's errors, its units) for one `.rs` source text: each item's own claims, else the `//!` module doc's, inherited.
pub(crate) fn rust_units(source: &str, path: &str) -> (Vec<String>, Vec<Unit>) {
    let module_doc = splitlines(source)
        .iter()
        .filter_map(|l| strip(l).strip_prefix("//!").map(|r| r.strip_prefix(' ').unwrap_or(r).to_owned()))
        .collect::<Vec<_>>()
        .join("\n");
    let (mod_claims, mod_errors) = claims_of(Some(&module_doc));
    let mut units = Vec::new();
    for (qual, kind, first, last, doc, body) in items(source, 0, "", false) {
        let (claims, errors) = claims_of(Some(&doc));
        let inherited = claims.is_empty() && errors.is_empty();
        let tokens = crate::codeid::rust_tokens(body.as_bytes());
        units.push(Unit {
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
            core: sha(&String::from_utf8_lossy(&tokens)),
            errors,
            names: Vec::new(),
            blocks: Vec::new(),
        });
    }
    (mod_errors, units)
}

/// Every file under `dir` whose name ends `suffix`, in the order Python's `sorted(dir.rglob(...))` gives (component by component); symlinked directories not followed.
pub(crate) fn rglob(dir: &Path, suffix: &str) -> Vec<std::path::PathBuf> {
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
pub(crate) fn rel(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

/// Every unit of every `.rs` under `rust/` (`target/`, the parked stages and the tooling crates pruned), with its file's errors.
pub(crate) fn all_rust_units(root: &Path, repo_prefix: &str) -> Result<Vec<Pair>, Fail> {
    let base = root.join("rust");
    let mut out = Vec::new();
    for p in rglob(&base, ".rs") {
        let inner = rel(&p, &base);
        let parts: Vec<&str> = inner.split('/').collect();
        if parts.contains(&"target") || ["parked", "guard", "gate"].contains(&parts[0]) {
            continue;
        }
        let text = crate::record::repo::read_text(&p)?;
        let (errors, units) = rust_units(&text, &format!("{repo_prefix}{}", rel(&p, root)));
        out.extend(units.into_iter().map(|u| (u, errors.clone())));
    }
    Ok(out)
}

/// `lstrip` re-exported for the readers of a unit's source lines.
pub(crate) fn lstripped(text: &str) -> &str {
    lstrip(text)
}

#[cfg(test)]
mod tests;
