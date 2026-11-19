//! The drawing pages still stating a changed constant's OLD figure (feature 385 T62, plan D81; `scripts/record/claims_stale.py`), which
//! `make claims-owed` prints as a flag, never a refusal. A `.py` constant is read by the Python (its value is `ast`'s), asked only when
//! the delta changed a `.py` file under `l7r/`; a `.rs` constant is read here (feature 449 T165, the GM 2026-11-17: the claims tools
//! track the Rust engine before S7 ports it), so a research number changed in `rust/phases` - or in a crate the engine's slices add -
//! names the pages still stating its old figure at the edit, as T10's dike-pond inset would have been (`ask:t10-findings-at-landing`).
//!
//! THE RUST RULE, `claims_stale.stale`'s on a Rust item: a `const` or `static` (an `impl`'s associated one too, as the claims walk keys
//! it) whose own `///` doc holds `Research:` and whose value's tokens or doc differ between the merge base with origin/main and the
//! working tree is CHANGED; its old figures are the number literals of its base value written as Python writes the value's numbers
//! (`43_560.0` as `43560`, `0.35f64` as `0.35`, `0x10` as `16`), 0 and 1 left out; and each drawing page that states one as a whole
//! number and IS, or links, a question the claim cites is named, in Python's line.

#![expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, which this port keeps, is case-sensitive"
)]

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{collapse, strip};
use l7r_guard::shared::pyjson::py_float;
use serde_json::json;

use super::scope::Reader;
use super::units::{items, walked};
use crate::record::repo::{git_out, read_text, Fail};
use crate::record::units::re;

const QUESTIONS: &str = "research/questions";
static CITED: LazyLock<Regex> = LazyLock::new(|| re(r"research/questions/(\d{4})-"));
static SUFFIX: LazyLock<Regex> = LazyLock::new(|| re(r"(?:[iu](?:8|16|32|64|128|size)|f32|f64)\z"));
/// A hexadecimal literal's suffix is an integer type's alone: `0x1f32` is the number 0x1f32, not 0x1 as an `f32`.
static INT_SUFFIX: LazyLock<Regex> = LazyLock::new(|| re(r"[iu](?:8|16|32|64|128|size)\z"));
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 3] = [&CITED, &SUFFIX, &INT_SUFFIX];

/// One drawing page: its path from the root, its file name, its text.
pub type Page = (String, String, String);

/// One line per drawing page still stating a changed constant's old figure: the `.py` constants' (the Python's), then the `.rs` ones'.
///
/// # Errors
///
/// Where the runner or a read fails: the error says which and why.
pub fn stale(reader: &mut Reader, root: &Path) -> Result<Vec<String>, Fail> {
    let base = git_out(root, &["merge-base", "HEAD", "origin/main"]);
    let base = strip(&base);
    if base.is_empty() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    let changed = git_out(root, &["diff", "--name-only", base, "--", "l7r"]);
    if changed
        .split_whitespace()
        .any(|p| p.ends_with(".py") && root.join(p).is_file())
    {
        let got = reader.ask("claims_stale", &json!([root.to_string_lossy()]))?;
        out.extend(
            got.as_array()
                .into_iter()
                .flatten()
                .map(|v| v.as_str().unwrap_or_default().to_owned()),
        );
    }
    let changed = git_out(root, &["diff", "--name-only", base, "--", "rust"]);
    let rs: Vec<&str> = changed
        .split_whitespace()
        .filter(|p| {
            p.strip_prefix("rust/")
                .is_some_and(|inner| p.ends_with(".rs") && walked(inner))
                && root.join(p).is_file()
        })
        .collect();
    if rs.is_empty() {
        return Ok(out);
    }
    let pages = drawing_pages(root)?;
    for path in rs {
        // a file new since the base has no old figure: `git show` fails, as the Python's `_git` gave it "" (feature 449 T165)
        let old = git_out(root, &["show", &format!("{base}:{path}")]);
        let head = read_text(&root.join(path))?;
        out.extend(rust_stale(path, &old, &head, &pages));
    }
    Ok(out)
}

/// Every `research/questions/*.drawing.html` in name order, read as the Python reads them (`errors="replace"`).
fn drawing_pages(root: &Path) -> Result<Vec<Page>, Fail> {
    let dir = root.join(QUESTIONS);
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .map(|d| {
            d.flatten()
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .filter(|n| n.ends_with(".drawing.html"))
                .collect()
        })
        .unwrap_or_default();
    names.sort();
    names
        .into_iter()
        .map(|n| {
            let bytes = std::fs::read(dir.join(&n)).map_err(|e| format!("{n}: {e}"))?;
            Ok((
                format!("{QUESTIONS}/{n}"),
                n,
                String::from_utf8_lossy(&bytes).into_owned(),
            ))
        })
        .collect()
}

/// One Rust file's stale-figure lines, its base text `old` against its working text `head` (`claims_stale.stale`'s loop).
#[must_use]
pub fn rust_stale(path: &str, old: &str, head: &str, pages: &[Page]) -> Vec<String> {
    let now = constants(head);
    let mut out = Vec::new();
    for (name, value, doc) in constants(old) {
        let Some((_, now_value, now_doc)) = now.iter().find(|c| c.0 == name) else {
            continue;
        };
        let both = format!("{doc}{now_doc}");
        if (tokens(&value), &doc) == (tokens(now_value), now_doc) || !both.contains("Research:") {
            continue;
        }
        let cited: BTreeSet<String> = CITED
            .captures_iter(&both)
            .map_while(Result::ok)
            .map(|c| c[1].to_owned())
            .collect();
        let links: Vec<Regex> = cited.iter().map(|q| re(&format!(r"\b{q}-[a-z]"))).collect();
        for fig in figures(&value) {
            let pat = re(&format!(
                r"(?<![\d.]){}(?!\d|\.\d)",
                fancy_regex::escape(&fig)
            ));
            for (rel, file, text) in pages {
                let named = cited.contains(file.get(..4).unwrap_or(file))
                    || links.iter().any(|l| l.is_match(text).unwrap_or(false));
                if named && pat.is_match(text).unwrap_or(false) {
                    out.push(format!("stale figure: {rel} states {fig} ({name} was {} in {path}) - reword it, or check it still holds", collapse(&value)));
                }
            }
        }
    }
    out
}

fn tokens(value: &str) -> Vec<u8> {
    crate::codeid::rust_tokens(value.as_bytes())
}

/// (name, value text, doc) for each constant item of `source`, in source order; a name given twice keeps its first place and its last
/// value, as a Python dict's assignment does.
fn constants(source: &str) -> Vec<(String, String, String)> {
    let mut out: Vec<(String, String, String)> = Vec::new();
    for (name, kind, _, _, doc, body) in items(source, 0, "", false) {
        let Some(value) = value_of(&body).filter(|_| kind == "constant") else {
            continue;
        };
        if let Some(at) = out.iter_mut().find(|c| c.0 == name) {
            *at = (name, value, doc);
        } else {
            out.push((name, value, doc));
        }
    }
    out
}

/// The value of `const X: T = <value>;`: past the item's first lone `=` (its type holds none), its `;` dropped.
fn value_of(body: &str) -> Option<String> {
    let chars: Vec<char> = body.chars().collect();
    let at = (0..chars.len()).find(|&i| {
        chars[i] == '='
            && !matches!(chars.get(i + 1), Some('=' | '>'))
            && !matches!(
                i.checked_sub(1).map(|j| chars[j]),
                Some('=' | '<' | '>' | '!')
            )
    })?;
    let rest: String = chars[at + 1..].iter().collect();
    let rest = rest.trim();
    Some(rest.strip_suffix(';').unwrap_or(rest).trim().to_owned())
}

/// The numbers of a value as a page writes them (`claims_stale.figures`): each number literal's value, a whole one without its `.0`, the
/// rest as Python's `repr`; 0 and 1 left out; sorted as text. The literals are read from the value's tokens, so a string's or a
/// comment's digits are none.
#[must_use]
pub fn figures(value: &str) -> Vec<String> {
    let raw = tokens(value);
    let toks: Vec<&str> = std::str::from_utf8(&raw)
        .unwrap_or_default()
        .split('\0')
        .collect();
    let mut out = BTreeSet::new();
    let mut i = 0;
    while i < toks.len() {
        let mut lit = toks[i].to_owned();
        i += 1;
        if !lit.starts_with(|c: char| c.is_ascii_digit()) {
            continue;
        }
        // the lexer splits a float at its point and its exponent's sign: `2.5f64` is `2` `.` `5f64`, `1.5e-3` is `1` `.` `5e` `-` `3`
        if toks.get(i) == Some(&".")
            && toks
                .get(i + 1)
                .is_some_and(|t| t.starts_with(|c: char| c.is_ascii_digit()))
            && !lit.starts_with("0x")
        {
            lit = format!("{lit}.{}", toks[i + 1]);
            i += 2;
        }
        if lit.ends_with(['e', 'E'])
            && !lit.starts_with("0x")
            && matches!(toks.get(i), Some(&("+" | "-")))
            && toks
                .get(i + 1)
                .is_some_and(|t| t.starts_with(|c: char| c.is_ascii_digit()))
        {
            lit = format!("{lit}{}{}", toks[i], toks[i + 1]);
            i += 2;
        }
        if let Some(fig) = figure(&lit) {
            out.insert(fig);
        }
    }
    out.into_iter().collect()
}

/// One number literal as Python writes its value, or None for 0, 1 and what does not read as a number.
fn figure(lit: &str) -> Option<String> {
    let plain = lit.replace('_', "");
    let radix = [("0x", 16), ("0o", 8), ("0b", 2)]
        .into_iter()
        .find(|(p, _)| plain.starts_with(p));
    if let Some((prefix, radix)) = radix {
        let digits = INT_SUFFIX.replace(&plain[prefix.len()..], "").into_owned();
        let v = u128::from_str_radix(&digits, radix).ok()?;
        return (v > 1).then(|| v.to_string());
    }
    let float = plain.ends_with("f32") || plain.ends_with("f64") || plain.contains(['.', 'e', 'E']);
    let digits = SUFFIX.replace(&plain, "").into_owned();
    if !float {
        // a decimal integer's figure is its digits, leading zeros dropped: Python's `str` of an int of any size
        let digits = digits.trim_start_matches('0');
        return (digits.len() > 1 || digits > "1").then(|| digits.to_owned());
    }
    let v: f64 = digits.parse().ok()?;
    #[expect(
        clippy::float_cmp,
        reason = "Python's `v not in (0, 1)` is an exact comparison"
    )]
    if v == 0.0 || v == 1.0 {
        return None;
    }
    Some(if v.is_finite() && v.fract() == 0.0 {
        whole(v)
    } else {
        py_float(v)
    })
}

/// A whole, finite, non-negative float as `str(int(v))` prints it: the integer it is, exactly, past an `i128`'s range too.
fn whole(v: f64) -> String {
    if v < 1e38 {
        #[expect(
            clippy::cast_possible_truncation,
            reason = "a whole float under 1e38 fits an i128 exactly"
        )]
        return (v as i128).to_string();
    }
    // v = m * 2^e: the mantissa's decimal digits (least first) doubled e times
    let bits = v.to_bits();
    let m = (bits & ((1 << 52) - 1)) | (1 << 52);
    let e = ((bits >> 52) & 0x7ff) - 1075;
    let mut digits: Vec<u8> = m.to_string().bytes().rev().map(|b| b - b'0').collect();
    for _ in 0..e {
        let mut carry = 0;
        for d in &mut digits {
            let x = *d * 2 + carry;
            *d = x % 10;
            carry = x / 10;
        }
        if carry > 0 {
            digits.push(carry);
        }
    }
    digits.iter().rev().map(|d| char::from(b'0' + d)).collect()
}

#[cfg(test)]
mod tests;
