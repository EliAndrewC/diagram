//! Which open claims findings a Rust stage's landing answers for (`scripts/record/claims_scope.py`'s `split`, `git_diff` and
//! `changed_lines`, ported by feature 449 T82; feature 444 FR-021 as amended 2026-11-01). Its `file_left`, which only `land.py` reached
//! through the claims door and never with its filing asked for, left with `land.py` (feature 449 T121's landing commit). A Python module's units and the units a seam
//! imports are read by Python's syntax tree, through the runner (`ask:449-T82-claims`).

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::scope::Reader;
use crate::record::repo::{read_text, Fail};
use crate::record::units::re;

static FINDING: LazyLock<Regex> =
    LazyLock::new(|| re(r"\A\s+([A-Z][A-Z-]+)\s+(\S[^:]*?)::(\S+?)#"));
static HUNK: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@"));

/// The new-side line ranges a `git diff -U0` changes; a pure deletion is the line it sits after.
pub fn changed_lines(diff: &str) -> Vec<(i64, i64)> {
    HUNK.captures_iter(diff)
        .flatten()
        .map(|c| {
            let a: i64 = c[1].parse().unwrap_or(0);
            let n: i64 = c.get(2).map_or(1, |g| g.as_str().parse().unwrap_or(0));
            if n == 0 {
                (a, a)
            } else {
                (a, a + n - 1)
            }
        })
        .collect()
}

/// `git diff -U0 origin/main...HEAD -- path`.
pub fn git_diff(root: &Path, path: &str) -> String {
    crate::record::repo::git_out(root, &["diff", "-U0", "origin/main...HEAD", "--", path])
}

/// The open findings the landing answers for, and the rest in the files it changes, each a report line.
pub fn split(
    reader: &mut Reader,
    root: &Path,
    report: &str,
    changed: &[String],
    seam: &[String],
) -> Result<(Vec<String>, Vec<String>), Fail> {
    let reads: Vec<String> = reader
        .ask("claims_read_units", &json!([root.to_string_lossy(), seam]))?
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect();
    let mut spans: HashMap<String, Map<String, Value>> = HashMap::new();
    let mut ranges: HashMap<String, Vec<(i64, i64)>> = HashMap::new();
    let (mut own, mut left) = (Vec::new(), Vec::new());
    for ln in super::units::splitlines(report) {
        let Some(m) = FINDING.captures(&ln).ok().flatten() else {
            continue;
        };
        let (path, qual) = (m[2].to_owned(), m[3].to_owned());
        let head = qual.split('.').next().unwrap_or_default().to_owned();
        let line = l7r_guard::shared::py_text::strip(&ln).to_owned();
        if reads.contains(&format!("{path}::{head}")) || reads.contains(&format!("{path}::{qual}"))
        {
            own.push(line);
            continue;
        }
        if !changed.contains(&path) {
            continue;
        }
        if path.starts_with("rust/") {
            own.push(line);
            continue;
        }
        if !spans.contains_key(&path) {
            let f = root.join(&path);
            let got = if f.is_file() {
                reader
                    .ask("claims_scope_units", &json!([read_text(&f)?]))?
                    .as_object()
                    .cloned()
                    .unwrap_or_default()
            } else {
                Map::new()
            };
            spans.insert(path.clone(), got);
            ranges.insert(path.clone(), changed_lines(&git_diff(root, &path)));
        }
        let span = spans[&path].get(&qual).or_else(|| spans[&path].get(&head));
        let bounds = span
            .and_then(Value::as_array)
            .map(|a| (a[0].as_i64().unwrap_or(0), a[1].as_i64().unwrap_or(0)));
        let hit =
            bounds.is_some_and(|(lo, hi)| ranges[&path].iter().any(|(a, b)| *a <= hi && *b >= lo));
        if hit {
            own.push(line);
        } else {
            left.push(line);
        }
    }
    Ok((own, left))
}

#[cfg(test)]
mod tests;
