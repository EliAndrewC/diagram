//! The record and review tooling's leaf pieces that Python still calls, each one implementation here and reached through a verb (feature 449 T81, slice 1): `hm_record.py`'s routing of an edit aimed at an assembled page and its listing of a question's fragments (`record edit-route`, `record fragments`, feature 258), `reviews/moves.py` (`record moved-only`, the Rust is `checks/moves.rs`), and `hm_house.py`'s `americanize` (`record americanize`, the Rust is the guard's). Python's door is `scripts/record_door.py`, one process a run.

use std::collections::BTreeMap;
use std::io::Read;
use std::path::{Component, Path};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::house_style_hooks::americanize;
use serde_json::{json, Map, Value};

use crate::logs::{one_line, one_line_utf8};
use crate::Reply;

use super::{flag, reply};

const RECORD: &str = "research";
const QUESTIONS: &str = "questions";
const REGISTRY: &str = "SOURCES.html";
const SITE: &str = "site";
const GLOSSARY: &str = "l7r/diagram/interactive/assets/glossary.json";

static STEM: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(\d{4})-[^.]+(?:\.drawing)?\.html$").unwrap_or_else(|e| unreachable!("{e}"))
});

fn number_of(name: &str) -> Option<u64> {
    let caught = STEM.captures(name).ok().flatten()?;
    caught.get(1)?.as_str().parse().ok()
}

/// `os.path.abspath`: `path` made absolute against `cwd` and normalized in its text alone, a symlink left as it stands.
fn abspath(path: &str, cwd: &Path) -> Vec<String> {
    let mut parts = Vec::new();
    for part in cwd.join(path).components() {
        match part {
            Component::ParentDir => {
                parts.pop();
            }
            Component::Normal(name) => parts.push(name.to_string_lossy().into_owned()),
            _ => {}
        }
    }
    parts
}

/// `os.path.relpath(os.path.abspath(path), root)`.
fn relpath(path: &str, root: &str, cwd: &Path) -> String {
    let (to, from) = (abspath(path, cwd), abspath(root, cwd));
    let same = to.iter().zip(&from).take_while(|(a, b)| a == b).count();
    let mut out = vec!["..".to_owned(); from.len() - same];
    out.extend_from_slice(&to[same..]);
    if out.is_empty() {
        ".".to_owned()
    } else {
        out.join("/")
    }
}

/// Where the fragments behind a built or assembled page are, or None if this path is not one.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the Python tests the suffix case-sensitively, and a page is named in lower case"
)]
pub(super) fn page_dir_for(rel: &str) -> Option<String> {
    if let Some(stem) = rel
        .strip_suffix(".json")
        .filter(|_| rel.ends_with(GLOSSARY))
    {
        return Some(stem.to_owned());
    }
    let mark = format!("{RECORD}/");
    if !format!("{rel}/").contains(&mark) || !rel.ends_with(".html") {
        return None;
    }
    let (before, inside) = rel.split_once(&mark)?;
    let root = format!("{before}{mark}");
    if inside.starts_with(&format!("{SITE}/")) {
        let is_source = inside.starts_with(&format!("{SITE}/sources/"));
        return Some(root + if is_source { "sources" } else { QUESTIONS });
    }
    if inside == REGISTRY {
        return Some(root + "sources");
    }
    if inside
        .strip_prefix("citations/")
        .unwrap_or(inside)
        .contains('/')
    {
        return None;
    }
    Some(root + QUESTIONS)
}

/// A file's text as Python's text mode reads it, a line end of any kind a `\n`; None where it is not UTF-8.
fn read_universal(path: &Path) -> Option<String> {
    let text = std::fs::read_to_string(path).ok()?;
    Some(if text.contains('\r') {
        text.replace("\r\n", "\n").replace('\r', "\n")
    } else {
        text
    })
}

fn walk_holders(dir: &Path, needle: &str, found: &mut Vec<std::path::PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let (path, name) = (entry.path(), entry.file_name());
        let name = name.to_string_lossy();
        if entry.file_type().is_ok_and(|t| t.is_dir()) {
            if name != SITE && !name.starts_with(".site-") {
                walk_holders(&path, needle, found);
            }
        } else if !path.is_dir()
            && !needle.is_empty()
            && read_universal(&path).is_some_and(|t| t.contains(needle))
        {
            found.push(path);
        }
    }
}

/// Every fragment of this page whose text contains `needle`, as repository-relative paths: the build's own directories are not the record.
fn fragments_holding(page_dir: &str, needle: &str, root: &str, cwd: &Path) -> Vec<String> {
    let mut found = Vec::new();
    walk_holders(&Path::new(root).join(page_dir), needle, &mut found);
    let mut out: Vec<String> = found
        .iter()
        .map(|p| relpath(&p.to_string_lossy(), root, cwd))
        .collect();
    out.sort();
    out
}

/// The files a check should read for the questions `q` names: each page and its notes, nothing else. `q` names a question by its number or a page by its file name, comma- or space-separated.
pub(crate) fn fragments_for(q: &str, root: &Path) -> Vec<String> {
    let here = root.join(RECORD).join(QUESTIONS);
    let mut names: Vec<String> = std::fs::read_dir(&here)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| number_of(n).is_some())
        .collect();
    names.sort();
    let mut out = Vec::new();
    let is_space = |c: char| c == ',' || c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c);
    for term in q.split(is_space).filter(|t| !t.is_empty()) {
        let wanted = term
            .bytes()
            .all(|b| b.is_ascii_digit())
            .then(|| term.parse::<u64>().ok())
            .flatten();
        let picked: Vec<&String> = if names.iter().any(|n| n == term) {
            names.iter().filter(|n| *n == term).collect()
        } else {
            names
                .iter()
                .filter(|n| wanted.is_some() && number_of(n) == wanted)
                .collect()
        };
        for name in picked {
            let notes = format!("{}.notes.html", name.trim_end_matches(".html"));
            for file in [name.as_str(), notes.as_str()] {
                let rel = format!("{RECORD}/{QUESTIONS}/{file}");
                if here.join(file).is_file() && !out.contains(&rel) {
                    out.push(rel);
                }
            }
        }
    }
    out
}

/// What rebuilds this assembled file: named in a refusal, because a refusal a session cannot act on costs the same round trip as none.
fn rebuild(rel: &str) -> &'static str {
    if rel.ends_with("glossary.json") {
        "make glossary"
    } else {
        "make record"
    }
}

fn refused(rule: &str, page: &str, dir: &str, message: &str) -> Value {
    json!({"verdict": "refuse", "rule": rule, "page": page, "dir": dir, "message": message})
}

/// What Python's `str()` makes of a payload's field.
fn py_str(value: Option<&Value>) -> String {
    match value {
        None => String::new(),
        Some(Value::String(text)) => text.clone(),
        Some(Value::Null) => "None".to_owned(),
        Some(other) => other.to_string(),
    }
}

/// `{"verdict": "pass"}`, or a rewrite carrying the fragment, or a refusal carrying its message.
pub(super) fn decide(tool: &str, input: &Value, root: &str, cwd: &Path) -> Value {
    let file_path = py_str(input.get("file_path"));
    if !matches!(tool, "Edit" | "Write") || file_path.is_empty() {
        return json!({"verdict": "pass"});
    }
    let rel = relpath(&file_path, root, cwd);
    let Some(dir) = page_dir_for(&rel).filter(|d| Path::new(root).join(d).is_dir()) else {
        return json!({"verdict": "pass", "reason": "not an assembled page, or its stage has not landed"});
    };
    let fix = rebuild(&rel);
    if tool == "Write" {
        return refused("write-to-assembled-page", &rel, &dir, &format!(
            "{rel} is ASSEMBLED from {dir}/ and is never written by hand - the next `make record` would overwrite it, and the fragments a session and every checking agent read would still say the old thing. A whole-file write cannot be routed to a fragment: edit the fragments, then run `{fix}` at the repository root."
        ));
    }
    let old = py_str(input.get("old_string"));
    let holders = fragments_holding(&dir, &old, root, cwd);
    if let [only] = holders.as_slice() {
        return json!({"verdict": "rewrite", "rule": "edit-moved-to-fragment", "page": rel, "fragment": only});
    }
    if holders.is_empty() {
        let why = if rel.ends_with("glossary.json") {
            "Either it is JSON the assembly WRITES - the object's braces, its one-space indentation, a term's own key - which no term file carries; or the file is stale"
        } else {
            "Either it is text the assembly WRITES - a footnote number, a reference id, a back link, the derived works block - which is not edited at all; or the page is stale"
        };
        return refused("text-in-no-fragment", &rel, &dir, &format!(
            "{rel} is ASSEMBLED from {dir}/, and the text this edit replaces is in none of its fragments. {why}, and `{fix}` will restore it."
        ));
    }
    refused("text-in-several-fragments", &rel, &dir, &format!(
        "{rel} is ASSEMBLED from {dir}/, and the text this edit replaces stands in {} fragments:\n  {}\nThe guard will not choose between them - aim the edit at the one you mean.",
        holders.len(),
        holders.join("\n  ")
    ))
}

/// The hook's rewrite: the Edit re-aimed at the one fragment holding its text.
fn rewrite_hook(verdict: &Value, input: &Value, root: &str) -> Value {
    let fragment = verdict["fragment"].as_str().unwrap_or("");
    let page = verdict["page"].as_str().unwrap_or("");
    let mut updated = input.as_object().cloned().unwrap_or_default();
    let target = Path::new(root).join(fragment);
    updated.insert("file_path".to_owned(), json!(target.to_string_lossy()));
    let holder = Path::new(fragment)
        .parent()
        .map_or(String::new(), |p| p.to_string_lossy().into_owned());
    json!({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": updated,
        "additionalContext": format!("{page} is assembled from {holder}/ and is never hand-edited, so this edit was re-aimed at the one fragment holding that text: {fragment}. Run `make record` at the repository root afterwards to rebuild the site (research/site/) from it."),
    }})
}

fn is_falsy(value: &Value) -> bool {
    match value {
        Value::Null => true,
        Value::Bool(b) => !b,
        Value::Number(n) => n.as_f64() == Some(0.0),
        Value::String(s) => s.is_empty(),
        Value::Array(a) => a.is_empty(),
        Value::Object(o) => o.is_empty(),
    }
}

fn read_all(stdin: &mut dyn Read) -> String {
    let mut text = String::new();
    // Input that is not UTF-8 stays as read so far, and fails as JSON does.
    let _ = stdin.read_to_string(&mut text);
    text
}

/// `record edit-route`: the hook's payload on stdin, the verdict as one `json.dumps` line, its `hook` key carrying a rewrite.
pub(super) fn edit_route(stdin: &mut dyn Read, cwd: &Path) -> Reply {
    let text = read_all(stdin);
    let Some(payload) = serde_json::from_str::<Value>(&text)
        .ok()
        .filter(Value::is_object)
    else {
        return reply(
            String::new(),
            "record edit-route: the payload is not a JSON object\n".to_owned(),
            1,
        );
    };
    let empty = Value::Object(Map::new());
    let input = payload
        .get("tool_input")
        .filter(|v| !is_falsy(v))
        .unwrap_or(&empty);
    if !input.is_object() {
        return reply(
            String::new(),
            "record edit-route: tool_input is not an object\n".to_owned(),
            1,
        );
    }
    let here = cwd.to_string_lossy();
    let root = payload
        .get("cwd")
        .and_then(Value::as_str)
        .filter(|c| !c.is_empty())
        .unwrap_or(&here);
    let tool = payload
        .get("tool_name")
        .and_then(Value::as_str)
        .unwrap_or("");
    let mut verdict = decide(tool, input, root, cwd);
    if verdict["verdict"] == "rewrite" {
        let hook = rewrite_hook(&verdict, input, root);
        verdict["hook"] = hook;
    }
    reply(one_line(&verdict) + "\n", String::new(), 0)
}

/// `record fragments [--root <dir>]`: a JSON list of questions on stdin, `{q: [files]}` on stdout, every question of a run in the one call.
pub(super) fn fragments_cli(args: &[String], stdin: &mut dyn Read, cwd: &Path) -> Reply {
    let root = Some(flag(args, "--root"))
        .filter(|r| !r.is_empty())
        .map_or_else(|| cwd.to_path_buf(), |r| cwd.join(r));
    let Ok(asked) = serde_json::from_str::<Vec<String>>(&read_all(stdin)) else {
        return reply(
            String::new(),
            "record fragments: stdin is a JSON list of questions\n".to_owned(),
            1,
        );
    };
    let found: BTreeMap<&str, Vec<String>> = asked
        .iter()
        .map(|q| (q.as_str(), fragments_for(q, &root)))
        .collect();
    let body = serde_json::to_value(found).unwrap_or_default();
    reply(one_line_utf8(&body) + "\n", String::new(), 0)
}

/// `record moved-only --root <dir> --base <rev>`: the names on stdin, one a line, whose content stood at the base; the moved ones, one a line.
pub(super) fn moved_only_cli(args: &[String], stdin: &mut dyn Read, cwd: &Path) -> Reply {
    let (root, base) = (flag(args, "--root"), flag(args, "--base"));
    if root.is_empty() {
        return reply(
            String::new(),
            "usage: l7r-gate record moved-only --root <dir> --base <rev>\n".to_owned(),
            2,
        );
    }
    let names: Vec<String> = read_all(stdin).lines().map(str::to_owned).collect();
    let moved = crate::checks::moves::moved_only(&cwd.join(root), base, &names);
    let body: String = moved.into_iter().map(|n| n + "\n").collect();
    reply(body, String::new(), 0)
}

/// The leaf verbs by name.
pub(super) fn cli(verb: &str, args: &[String], stdin: &mut dyn Read, cwd: &Path) -> Reply {
    match verb {
        "edit-route" => edit_route(stdin, cwd),
        "fragments" => fragments_cli(args, stdin, cwd),
        "moved-only" => moved_only_cli(args, stdin, cwd),
        _ => americanize_cli(stdin),
    }
}

fn styled(value: &Value) -> Value {
    match value {
        Value::String(text) => Value::String(americanize(text)),
        Value::Array(items) => Value::Array(items.iter().map(styled).collect()),
        Value::Object(map) => {
            Value::Object(map.iter().map(|(k, v)| (k.clone(), styled(v))).collect())
        }
        other => other.clone(),
    }
}

/// `record americanize`: any JSON on stdin, the same JSON with every string value in the house style; keys are as written.
pub(super) fn americanize_cli(stdin: &mut dyn Read) -> Reply {
    let Ok(value) = serde_json::from_str::<Value>(&read_all(stdin)) else {
        return reply(
            String::new(),
            "record americanize: stdin is not JSON\n".to_owned(),
            1,
        );
    };
    reply(one_line_utf8(&styled(&value)) + "\n", String::new(), 0)
}

#[cfg(test)]
mod tests;
