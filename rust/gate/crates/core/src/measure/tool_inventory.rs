//! The project's tools listed from the code (feature 406 D163; feature 449 T120, `tool_yield.py`'s inventory under `ask:449-T83-scope`):
//! the guards wired in `.claude/settings.json`, the refusing checks, the Makefile's targets and the registered steps. ONE implementation
//! (FR-003): `l7r-gate check tool-signals` (`checks/tool_signals.rs`, which held its own copy since T068) and `l7r-gate measure
//! tool-yield` and `fix-yield` (`measure/tool_yield.rs`) all read it, and it lives here because `checks` and `measure` cannot build on
//! each other and both build on `core`.
//!
//! Each reader fails where `tool_yield.py` raised (a missing or broken settings file, Makefile or registry, a gate script that is not
//! UTF-8), so the commands fail where the Python failed; the error is the text its traceback named.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

/// The entry targets whose recipes name the checks they run (`tool_yield.ENTRY_TARGETS`).
pub const ENTRY_TARGETS: [&str; 3] = ["done", "quick", "tick"];
/// The entry scripts whose text names the checks they run (`tool_yield.ENTRY_SCRIPTS`).
pub const ENTRY_SCRIPTS: [&str; 3] = [
    "scripts/sync-with-main.sh",
    "rust/gate/crates/cohort/src/push.rs",
    "rust/gate/crates/measure/src/preflight.rs",
];

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static HOOK: LazyLock<Regex> = LazyLock::new(|| compiled(r"scripts/hooks/([\w-]+)-hooks\.sh"));
static TARGET: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^([a-z][\w-]*)\s*:(?!=)"));
static SCRIPT: LazyLock<Regex> = LazyLock::new(|| compiled(r"scripts/[\w./-]+\.(?:py|sh)"));
static SUB_MAKE: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"\$\(MAKE\)[^\n;&|]*?\s([a-z][\w-]+)(?=\s|$|;)"));
static TARGET_WORD: LazyLock<Regex> = LazyLock::new(|| compiled(r"^[a-z][\w-]+$"));

/// Text as Python's text mode reads it: `\r\n` and a lone `\r` both end a line.
fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// `path.read_text(encoding="utf-8")`.
///
/// # Errors
///
/// The file cannot be read or is not UTF-8: the Python's `OSError` or `UnicodeDecodeError`.
pub fn read_text(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("OSError: {}: {e}", path.display()))?;
    String::from_utf8(bytes)
        .map(|t| universal(&t))
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))
}

/// `path.read_text(encoding="utf-8", errors="replace")`, "" where it cannot be read.
#[must_use]
pub fn read_lossy(path: &Path) -> String {
    universal(&String::from_utf8_lossy(
        &std::fs::read(path).unwrap_or_default(),
    ))
}

/// What `for x in value` walks in Python: a list's items, an object's keys, a string's characters; anything else is the `TypeError`.
///
/// # Errors
///
/// The value is not iterable.
pub fn py_iter(value: &Value) -> Result<Vec<Value>, String> {
    match value {
        Value::Array(items) => Ok(items.clone()),
        Value::Object(m) => Ok(m.keys().map(|k| Value::String(k.clone())).collect()),
        Value::String(s) => Ok(s.chars().map(|c| Value::String(c.to_string())).collect()),
        _ => Err("TypeError: the value is not iterable".to_owned()),
    }
}

/// `value.get(key, default)`: the `AttributeError` where the value is no object.
///
/// # Errors
///
/// The value is no object.
pub fn py_get<'a>(value: &'a Value, key: &str, default: &'a Value) -> Result<&'a Value, String> {
    value
        .as_object()
        .map(|m| m.get(key).unwrap_or(default))
        .ok_or_else(|| format!("AttributeError: no .get({key:?}) on a value that is no object"))
}

/// The guard names of the hooks wired in `.claude/settings.json` (`<name>-hooks.sh` -> `<name>`).
///
/// # Errors
///
/// The settings file is missing, not JSON, or not shaped as the Python walked it.
pub fn hook_guards(root: &Path) -> Result<BTreeSet<String>, String> {
    let text = read_text(&root.join(".claude/settings.json"))?;
    let settings: Value =
        serde_json::from_str(&text).map_err(|e| format!("JSONDecodeError: {e}"))?;
    let empty = Value::Object(Map::new());
    let none = Value::Array(Vec::new());
    let hooks = py_get(&settings, "hooks", &empty)?;
    let Value::Object(by_event) = hooks else {
        return Err("AttributeError: the settings' hooks are no object".to_owned());
    };
    let mut names = BTreeSet::new();
    for blocks in by_event.values() {
        for block in py_iter(blocks)? {
            for hook in py_iter(py_get(&block, "hooks", &none)?)? {
                let empty_text = Value::String(String::new());
                let Value::String(command) = py_get(&hook, "command", &empty_text)? else {
                    return Err("TypeError: a hook's command is no text".to_owned());
                };
                names.extend(
                    HOOK.captures_iter(command)
                        .flatten()
                        .map(|c| c[1].to_owned()),
                );
            }
        }
    }
    Ok(names)
}

/// Every target a Makefile's text defines.
#[must_use]
pub fn targets_of(make: &str) -> BTreeSet<String> {
    TARGET
        .captures_iter(make)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect()
}

/// Every target the Makefile defines.
///
/// # Errors
///
/// The Makefile cannot be read.
pub fn targets(root: &Path) -> Result<BTreeSet<String>, String> {
    Ok(targets_of(&read_text(&root.join("Makefile"))?))
}

/// A target's recipe: its rule line and the tab-led or `##` lines after it.
#[must_use]
pub fn recipe(make: &str, target: &str) -> String {
    compiled(&format!(
        r"(?m)^{}\s*:(?!=).*\n((?:\t.*\n|##.*\n)*)",
        fancy_regex::escape(target)
    ))
    .find(make)
    .ok()
    .flatten()
    .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// The entry targets and every target their recipes reach: each prerequisite and each `$(MAKE) <target>` followed to its own recipe.
#[must_use]
pub fn reached(make: &str) -> BTreeSet<String> {
    let mut seen = BTreeSet::new();
    let mut todo: Vec<String> = ENTRY_TARGETS.iter().map(|s| (*s).to_owned()).collect();
    while let Some(name) = todo.pop() {
        if !seen.insert(name.clone()) {
            continue;
        }
        let text = recipe(make, &name);
        // the rule line's prerequisites, `[^\n#]*` after `<name>:` as the Python's match reads them
        let head = compiled(&format!(
            r"^{}\s*:(?!=)([^\n#]*)",
            fancy_regex::escape(&name)
        ));
        let deps = head
            .captures(&text)
            .ok()
            .flatten()
            .map(|c| c[1].to_owned())
            .unwrap_or_default();
        let subs: Vec<String> = SUB_MAKE
            .captures_iter(&text)
            .flatten()
            .map(|c| c[1].to_owned())
            .collect();
        todo.extend(
            deps.split_whitespace()
                .map(str::to_owned)
                .chain(subs)
                .filter(|d| TARGET_WORD.is_match(d).unwrap_or(false)),
        );
    }
    seen
}

/// `root / rel` as pathlib joins it: `.` and empty components dropped.
#[must_use]
pub fn py_join(root: &Path, rel: &str) -> PathBuf {
    root.join(Path::new(rel).components().collect::<PathBuf>())
}

/// The entries of a directory whose names end in `suffix`, as a pathlib glob `*<suffix>` lists them (a dot file too), none where it
/// cannot be read.
#[must_use]
pub fn ending(dir: &Path, suffix: &str) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().ends_with(suffix))
        .map(|e| e.path())
        .collect()
}

/// Every refusing check's file: the commands under `scripts/gates/`, and every `scripts/` script the entry points name.
///
/// # Errors
///
/// A gate script, the Makefile or an entry script cannot be read.
pub fn check_paths(root: &Path) -> Result<BTreeSet<PathBuf>, String> {
    let gates = root.join("scripts/gates");
    let mut out = BTreeSet::new();
    for p in ending(&gates, ".py") {
        if read_text(&p)?.contains("__name__ == \"__main__\"") {
            out.insert(p);
        }
    }
    out.extend(ending(&gates, ".sh"));
    let make = read_text(&root.join("Makefile"))?;
    let mut texts: Vec<String> = reached(&make).iter().map(|t| recipe(&make, t)).collect();
    for s in ENTRY_SCRIPTS {
        let path = root.join(s);
        if path.is_file() {
            texts.push(read_text(&path)?);
        }
    }
    for text in &texts {
        for found in SCRIPT.find_iter(text).flatten() {
            let path = py_join(root, found.as_str());
            if !found.as_str().contains("/hooks/") && path.is_file() {
                out.insert(path);
            }
        }
    }
    Ok(out)
}

/// `scripts/tool-registry.json`'s `tools`: none where the file is missing.
///
/// # Errors
///
/// The file cannot be read, is not JSON, or its `tools` is no object.
pub fn registry(root: &Path) -> Result<Map<String, Value>, String> {
    let path = root.join("scripts/tool-registry.json");
    if !path.is_file() {
        return Ok(Map::new());
    }
    let data: Value =
        serde_json::from_str(&read_text(&path)?).map_err(|e| format!("JSONDecodeError: {e}"))?;
    let empty = Value::Object(Map::new());
    match py_get(&data, "tools", &empty)? {
        Value::Object(m) => Ok(m.clone()),
        _ => Err("AttributeError: the registry's tools are no object".to_owned()),
    }
}

#[cfg(test)]
mod tests;
