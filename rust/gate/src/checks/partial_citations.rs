//! A footnote citing a source no one can wholly read stands only on a confirmed passage (feature 312, FR-019, FR-020; feature 449 T80, from `check-partial-citations.py`).
//!
//! WHY (the GM, 2026-10-02): *"if we cannot find these sources because we cited something that is paywalled, then we must, as part of this feature, update our research
//! findings to remove those as sources"* - and the record's rule, "a source that cannot be read is not cited". A footnote may still quote a passage from the part that IS
//! readable (an open abstract, the GM's partial copy): it stands when `quote-check` confirmed that passage there, a confirmation recorded per footnote in
//! `research/partial-confirmations.jsonl` (`{"key", "note": "<notes file>#<note id>", "where", "date"}`). A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{py_lines, Outcome};
use crate::record::access_tags;
use crate::record::read_text;

pub(super) const USAGE_LOG_TOOL: &str = "check-partial-citations";
const ACCESS: &str = "research/source-access.json";
const CONFIRMED_NAME: &str = "partial-confirmations.jsonl";
const UNREADABLE: [&str; 3] = ["paywalled", "gm-partial", "never-read"];

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static NOTE: LazyLock<Regex> =
    LazyLock::new(|| compiled(r#"(?s)<li data-note="([^"]+)">(.*?)</li>"#));
static KEY: LazyLock<Regex> = LazyLock::new(|| compiled(r"<code>([a-z0-9][a-z0-9-]*)</code>"));

fn unreadable_keys(root: &Path) -> Result<HashMap<String, String>, String> {
    if !root.join(ACCESS).is_file() {
        return Ok(HashMap::new()); // a tree with no access states (a push fixture) names no unreadable source
    }
    Ok(access_tags::every(&access_tags::load(root)?)
        .into_iter()
        .filter(|(k, t)| UNREADABLE.contains(&t.state.as_str()) && !k.starts_with("download:"))
        .map(|(k, t)| (k, t.state))
        .collect())
}

fn confirmed(root: &Path) -> HashSet<(String, String)> {
    let text = read_text(&root.join("research").join(CONFIRMED_NAME)).unwrap_or_default();
    py_lines(&text)
        .filter_map(|line| serde_json::from_str::<Value>(line).ok())
        .map(|x| {
            (
                x["key"].as_str().unwrap_or("").to_owned(),
                x["note"].as_str().unwrap_or("").to_owned(),
            )
        })
        .collect()
}

fn notes_files(root: &Path) -> Vec<PathBuf> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(root.join("research/questions"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.to_string_lossy().ends_with(".notes.html"))
        .collect();
    files.sort();
    files
}

fn findings(
    root: &Path,
    keys: &HashMap<String, String>,
    ok: &HashSet<(String, String)>,
) -> Vec<String> {
    let mut out = Vec::new();
    for file in notes_files(root) {
        let name = file
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        let text = read_text(&file).unwrap_or_default();
        for note in NOTE.captures_iter(&text).flatten() {
            let mut seen = HashSet::new();
            for found in KEY.captures_iter(&note[2]).flatten() {
                let key = found[1].to_owned();
                let place = format!("{name}#{}", &note[1]);
                if seen.insert(key.clone())
                    && keys.contains_key(&key)
                    && !ok.contains(&(key.clone(), place.clone()))
                {
                    out.push(format!(
                        "{place}: cites `{key}` ({}) with no confirmed passage - confirm it from the readable part (make quote-verbatim, then quote-check) and record it in {CONFIRMED_NAME}, or make the note an absence note",
                        keys[&key]
                    ));
                }
            }
        }
    }
    out
}

/// `check partial-citations [ROOT]`.
pub(super) fn cli(args: &[String]) -> Outcome {
    let given = args.first().map_or(".", String::as_str);
    let root = std::fs::canonicalize(given).unwrap_or_else(|_| PathBuf::from(given));
    let found = match unreadable_keys(&root) {
        Ok(keys) => findings(&root, &keys, &confirmed(&root)),
        Err(why) => return Outcome::refuse(format!("check-partial-citations: {why}\n")),
    };
    if found.is_empty() {
        return Outcome::out(String::new());
    }
    let lines: Vec<String> = found
        .iter()
        .map(|l| format!("check-partial-citations: {l}\n"))
        .collect();
    Outcome::refuse(lines.concat())
}

#[cfg(test)]
mod tests;
