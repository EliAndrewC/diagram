//! ONE FEATURE'S ROWS (feature 395's step-back, hour:395@1): `--write specs/395-.../checks.md` from the main session wrote rows for every
//! owed pass in the clone - 396's and 397's spec reviews among them - each claiming 395's checks file as where it was acted on. A write
//! that names a feature's specs directory now writes only the passes that feature's work can be traced to: a subject naming the feature,
//! one of its questions (the claims sheet, its implementation check, its briefs' SECTION= lines), or a `key-<key>` bundle of a source
//! those questions cite. The rest stay owed for the feature that ran them.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::reply::py_lines;
use l7r_guard::shared::py_text::strip;
use serde_json::Value;

use super::{py_path, text, Env, Pass};
use crate::record::bundle::py_str;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FEATURE_DIR: LazyLock<Regex> = LazyLock::new(|| re(r"specs/(\d{3})-"));
static QUESTION: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\d.])(\d{4})(?!\d)"));
static CHECKED: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- (\d{4}):"));
static SECTION: LazyLock<Regex> = LazyLock::new(|| re(r"SECTION=(\d{4})"));
/// A CLAIMS ROUND'S PASS IS THE ACTIVE FEATURE'S (feature 405 T39, D13): its bundle is the clone's own (`make claims-bundle`, `make
/// claims-triage`) and its prompt names no feature - T14's landing refused once on three impl-drift passes for that. A WORK-BUDGET PASS
/// IS THE ACTIVE FEATURE'S TOO (feature 444 FR-015): its bundle (`make work-budget-bundle`) is the clone's own and its prompt names only
/// the bundle - nine greenfield passes stayed owed under a WRITE naming the feature.
static OWN_BUNDLE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"l7r-check/(?:claims-(?:owed|triage)|work-budget-(?:budget|audit|table)-)")
});
static KEY: LazyLock<Regex> = LazyLock::new(|| re(r"/key-([\w-]+?)(?:-whole)?/"));
const DEFAULT_SHEET: &str = "/diagram/.clones/RESEARCH-CLAIMS.md";

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// Every group-1 match.
fn all(pattern: &Regex, text: &str) -> BTreeSet<String> {
    pattern
        .captures_iter(text)
        .flatten()
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .collect()
}

/// The first match's group 1 (`re.search(...).group(1)`).
fn first_group(pattern: &Regex, text: &str) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

/// The feature number a `--write` names by its specs directory, if any.
#[must_use]
pub fn feature_of(write: &str) -> Option<String> {
    first_group(&FEATURE_DIR, write)
}

/// A file read as `read_text(encoding="utf-8")`: the raise where it is not UTF-8.
fn read(path: &Path) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))
}

/// The entries of `dir` whose name `keep` takes (one level of `Path.glob`), in listing order.
fn entries(dir: &Path, keep: &dyn Fn(&str) -> bool) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| keep(&p.file_name().unwrap_or_default().to_string_lossy()))
        .collect()
}

/// The question numbers feature `num` worked: its claims on the sheet and the numbers its own files name (`feature_questions`).
///
/// # Errors
///
/// Where a file read is not UTF-8 (the Python's raise).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "fnmatch on Linux is case-sensitive, as the Python's globs of `*.md` and `*.html` were"
)]
pub fn feature_questions(num: &str, repo: &Path, env: &Env) -> Result<BTreeSet<String>, String> {
    let mut out = BTreeSet::new();
    let sheet = env.cwd.join(py_path(
        env.claims_sheet.as_deref().unwrap_or(DEFAULT_SHEET),
    ));
    if sheet.is_file() {
        let named = re(&format!(r"\b{num}\b"));
        for line in py_lines(&read(&sheet)?) {
            let parts: Vec<&str> = line.split('|').map(strip).collect();
            if parts.len() > 2 && found(&named, parts[1]) {
                out.extend(all(&QUESTION, parts[2]));
            }
        }
    }
    let prefix = format!("{num}-");
    for d in entries(&repo.join("specs"), &|n| n.starts_with(&prefix)) {
        let mut files = vec![d.join("implementation-check.md")];
        files.extend(entries(&d.join("briefs"), &|n| n.ends_with(".md")));
        for f in files.iter().filter(|f| f.is_file()) {
            let body = read(f)?;
            out.extend(all(&CHECKED, &body));
            out.extend(all(&SECTION, &body));
        }
    }
    Ok(out)
}

/// Every `agent-<id>.jsonl` under `dir` and the directories below it, not through a link, as `**` walks.
fn walk(dir: &Path, name: &str, out: &mut Vec<PathBuf>) {
    for path in std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
    {
        let is_dir = std::fs::symlink_metadata(&path).is_ok_and(|m| m.is_dir());
        if is_dir {
            walk(&path, name, out);
        }
        if path.file_name().is_some_and(|n| n == name) {
            out.push(path);
        }
    }
}

/// The first five lines of a transcript read as JSON, the ones that are not skipped (`_lines_of`).
fn lines_of(path: Option<&Path>) -> Result<Vec<Value>, String> {
    let Some(path) = path.filter(|p| p.is_file()) else {
        return Ok(Vec::new());
    };
    let body = read(path)?;
    Ok(py_lines(&body)
        .into_iter()
        .take(5)
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

/// A check-wave unit's own prompt: its logged subject is the workflow's framing ("[Workflow harness - computed task] ..."), so the prompt
/// naming its bundle is read from the agent's transcript (its first user message) (`_unit_prompt`). A wave's agents are kept under
/// `subagents/workflows/<run>/`, one level below where `review_cost.transcript` looks.
fn unit_prompt(p: &Pass, transcripts: &Path) -> Result<String, String> {
    let agent = text(p, "agent");
    let mut hits = Vec::new();
    if !agent.is_empty() {
        let name = format!("agent-{agent}.jsonl");
        for project in entries(transcripts, &|_| true) {
            for session in entries(&project, &|_| true) {
                walk(&session.join("subagents"), &name, &mut hits);
            }
        }
    }
    hits.sort();
    let no_get = |v: &Value| format!("AttributeError: {v} has no attribute 'get'");
    for d in lines_of(hits.last().map(PathBuf::as_path))? {
        let rec = d.as_object().ok_or_else(|| no_get(&d))?;
        if rec.get("type").and_then(Value::as_str) != Some("user") {
            continue;
        }
        let content = match rec.get("message") {
            Some(m) if !l7r_guard::shared::checks::falsy(Some(m)) => {
                m.as_object().ok_or_else(|| no_get(m))?.get("content")
            }
            _ => None,
        };
        match content {
            None => {}
            c if l7r_guard::shared::checks::falsy(c) => {}
            Some(Value::String(s)) => return Ok(s.clone()),
            Some(Value::Array(items)) => {
                let mut said = Vec::new();
                for c in items.iter().filter_map(Value::as_object) {
                    match c.get("text") {
                        None => said.push(String::new()),
                        Some(Value::String(s)) => said.push(s.clone()),
                        Some(other) => return Err(format!("TypeError: a text part is {other}")),
                    }
                }
                return Ok(said.join(" "));
            }
            Some(Value::Object(_)) => return Ok(String::new()),
            Some(other) => return Err(format!("TypeError: {other} is not iterable")),
        }
    }
    Ok(String::new())
}

/// The number of the feature `.specify/feature.json` names (the clone's active feature), or "" (`_active_feature`).
fn active_feature(repo: &Path) -> Result<String, String> {
    let Some(rec) = std::fs::read_to_string(repo.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return Ok(String::new());
    };
    let rec = rec
        .as_object()
        .ok_or_else(|| "AttributeError: the feature record has no attribute 'get'".to_owned())?;
    let fd = rec
        .get("feature_directory")
        .map_or_else(String::new, py_str);
    Ok(feature_of(&format!("{fd}-")).unwrap_or_default())
}

/// Whether feature `num`'s work can be traced to this pass (`belongs`).
///
/// # Errors
///
/// Where a file read is not UTF-8 or a transcript's first lines made the Python raise.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "fnmatch on Linux is case-sensitive, as the Python's globs of `*.md` and `*.html` were"
)]
pub fn belongs(
    p: &Pass,
    num: &str,
    questions: &BTreeSet<String>,
    repo: &Path,
    transcripts: &Path,
) -> Result<bool, String> {
    let mut subject = text(p, "subject").to_owned();
    if subject.starts_with("[Workflow harness") {
        let prompt = unit_prompt(p, transcripts)?;
        if !prompt.is_empty() {
            subject = prompt;
        }
    }
    let named = re(&format!(r"(?:feature |specs/|\b){num}-|feature {num}\b"));
    if found(&named, &subject) {
        return Ok(true);
    }
    // A SUBJECT IS LOGGED CUT AT 100 CHARACTERS: a prompt naming its feature after that (feature 443's MODE 2, "MODE 2: SPECIFICATION
    // REVIEW. Clone: ... Request (the GM's words verba") stayed owed under every WRITE, so read the whole prompt
    if subject.chars().count() >= 100 && found(&named, &unit_prompt(p, transcripts)?) {
        return Ok(true);
    }
    if !questions.is_disjoint(&all(&QUESTION, &subject)) {
        return Ok(true);
    }
    if found(&OWN_BUNDLE, &subject) && active_feature(repo)? == num {
        return Ok(true);
    }
    let Some(key) = first_group(&KEY, &subject) else {
        return Ok(false);
    };
    for q in questions {
        let prefix = format!("{q}-");
        let pages = entries(&repo.join("research/questions"), &|n| {
            n.starts_with(&prefix) && n.ends_with(".html")
        });
        for page in pages {
            if read(&page)?.contains(&key) {
                return Ok(true);
            }
        }
    }
    Ok(false)
}

#[cfg(test)]
mod tests;
