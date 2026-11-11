//! No tool without its record (feature 406 T05, FR-004, D164; feature 449 T068, from `check-tool-signals.py`).
//!
//! WHY (the GM 2026-10-19): "there should at least be a way that it is notionally possible for us to see how often a tool is used, right?
//! Or how often it makes a difference". `make tool-yield` reads what each tool leaves behind; a tool added later that leaves nothing would
//! sit in its table as a blank row forever. This refuses that tool before it lands.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::Outcome;

/// The name its runs are recorded under in the `usage_log`.
pub(super) const USAGE_LOG_TOOL: &str = "check-tool-signals";
const RECORDS: [&str; 3] = ["guard_log", "usage_log", "# TOOL_RECORD:"];
/// The entry points whose text names the checks they run (`tool_yield.ENTRY_SCRIPTS`).
const ENTRY_TARGETS: [&str; 3] = ["done", "quick", "tick"];
const ENTRY_SCRIPTS: [&str; 3] = [
    "scripts/sync-with-main.sh",
    "rust/gate/crates/cohort/src/push.rs",
    "rust/gate/crates/measure/src/preflight.rs",
];

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static CALLS: LazyLock<[Regex; 5]> = LazyLock::new(|| {
    [
        compiled(r#"\bexited\(\s*"([\w-]+)""#),
        compiled(r#"usage_log\.record\([^\n]*?,\s*"([\w-]+)""#),
        compiled(r#"--tool[ =]"?([\w-]+)"#),
        compiled(r#""--tool",\s*"([\w-]+)""#),
        compiled(r#"USAGE_LOG_TOOL: &str = "([\w-]+)""#),
    ]
});
static HOOK: LazyLock<Regex> = LazyLock::new(|| compiled(r"scripts/hooks/([\w-]+)-hooks\.sh"));
static SCRIPT: LazyLock<Regex> = LazyLock::new(|| compiled(r"scripts/[\w./-]+\.(?:py|sh)"));
static SUB_MAKE: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"\$\(MAKE\)[^\n;&|]*?\s([a-z][\w-]+)(?=\s|$|;)"));
static TARGET_WORD: LazyLock<Regex> = LazyLock::new(|| compiled(r"^[a-z][\w-]+$"));

fn read(path: &Path) -> String {
    String::from_utf8_lossy(&std::fs::read(path).unwrap_or_default()).into_owned()
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            walk(&path, out);
        } else {
            out.push(path);
        }
    }
}

/// The guard names of the hooks wired in `.claude/settings.json`.
fn hook_guards(root: &Path) -> BTreeSet<String> {
    let settings: Value =
        serde_json::from_str(&read(&root.join(".claude/settings.json"))).unwrap_or_default();
    let blocks = settings["hooks"]
        .as_object()
        .into_iter()
        .flat_map(|o| o.values());
    blocks
        .flat_map(|b| b.as_array().cloned().unwrap_or_default())
        .flat_map(|b| b["hooks"].as_array().cloned().unwrap_or_default())
        .flat_map(|h| {
            HOOK.captures_iter(h["command"].as_str().unwrap_or_default())
                .flatten()
                .map(|c| c[1].to_owned())
                .collect::<Vec<_>>()
        })
        .collect()
}

/// A target's recipe: its rule line and the tab-led or `##` lines after it.
fn recipe(make: &str, target: &str) -> String {
    let pattern = compiled(&format!(
        r"(?m)^{}\s*:(?!=).*\n((?:\t.*\n|##.*\n)*)",
        fancy_regex::escape(target)
    ));
    pattern
        .find(make)
        .ok()
        .flatten()
        .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// The entry targets and every target their recipes reach.
fn reached(make: &str) -> BTreeSet<String> {
    let mut seen = BTreeSet::new();
    let mut todo: Vec<String> = ENTRY_TARGETS.iter().map(|s| (*s).to_owned()).collect();
    while let Some(name) = todo.pop() {
        if !seen.insert(name.clone()) {
            continue;
        }
        let text = recipe(make, &name);
        let head = text.lines().next().unwrap_or_default();
        let deps = head
            .split_once(':')
            .map_or("", |(_, d)| d.split('#').next().unwrap_or_default());
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

/// Every refusing check's file: the commands under `scripts/gates/`, and every `scripts/` script the entry points name.
fn check_paths(root: &Path) -> BTreeSet<PathBuf> {
    let gates = root.join("scripts/gates");
    let mut out: BTreeSet<PathBuf> = std::fs::read_dir(&gates)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| match p.extension().and_then(|x| x.to_str()) {
            Some("py") => read(p).contains("__name__ == \"__main__\""),
            Some("sh") => true,
            _ => false,
        })
        .collect();
    let make = read(&root.join("Makefile"));
    let mut texts: Vec<String> = reached(&make).iter().map(|t| recipe(&make, t)).collect();
    texts.extend(ENTRY_SCRIPTS.iter().map(|s| read(&root.join(s))));
    for text in &texts {
        for found in SCRIPT.find_iter(text).flatten() {
            let path = root.join(found.as_str());
            if !found.as_str().contains("/hooks/") && path.is_file() {
                out.insert(path);
            }
        }
    }
    out
}

/// The hooks and checks that leave no record, each with its fix.
fn unrecorded(root: &Path) -> Vec<String> {
    let mut paths = check_paths(root);
    paths.extend(
        hook_guards(root)
            .iter()
            .map(|n| root.join(format!("scripts/hooks/{n}-hooks.sh"))),
    );
    paths
        .iter()
        .filter(|p| p.is_file() && !RECORDS.iter().any(|m| read(p).contains(m)))
        .map(|p| {
            let rel = p.strip_prefix(root).unwrap_or(p).display();
            let stem = p.file_stem().unwrap_or_default().to_string_lossy();
            format!("{rel}: records none of its runs. Wrap its exit in `usage_log.exited(\"{stem}\", ...)` (a check), call `guard_log` (a hook), or add `# TOOL_RECORD: <where its runs are seen>` near its top, and register a usage-log name in scripts/tool-registry.json")
        })
        .collect()
}

/// Every tool name a usage-log call names, with the first file that names it.
fn called(root: &Path) -> BTreeMap<String, String> {
    let mut files = Vec::new();
    walk(&root.join("scripts"), &mut files);
    files.retain(|p| {
        p.extension().is_some_and(|x| x == "py" || x == "sh")
            && !p.components().any(|c| c.as_os_str() == "__pycache__")
    });
    for dir in [
        "rust/guard/src/guards",
        "rust/guard/src/shared",
        "rust/gate",
    ] {
        let mut rust = Vec::new();
        walk(&root.join(dir), &mut rust);
        files.extend(
            rust.into_iter()
                .filter(|p| p.extension().is_some_and(|x| x == "rs")),
        );
    }
    files.push(root.join("Makefile"));
    files.sort();
    let mut out = BTreeMap::new();
    for path in files
        .iter()
        .filter(|p| p.file_name().is_some_and(|n| n != "usage_log.py"))
    {
        let text = read(path);
        if !text.contains("usage_log") {
            continue;
        }
        for name in CALLS.iter().flat_map(|c| {
            c.captures_iter(&text)
                .flatten()
                .map(|m| m[1].to_owned())
                .collect::<Vec<_>>()
        }) {
            out.entry(name).or_insert_with(|| {
                path.strip_prefix(root)
                    .unwrap_or(path)
                    .display()
                    .to_string()
            });
        }
    }
    out
}

fn mismatched(root: &Path) -> Vec<String> {
    let data: Value =
        serde_json::from_str(&read(&root.join("scripts/tool-registry.json"))).unwrap_or_default();
    let registry = data["tools"].as_object().cloned().unwrap_or_default();
    let calls = called(root);
    let lacks = calls.iter().filter(|(name, _)| !registry.contains_key(*name)).map(|(name, at)| format!("{at}: records `{name}`, which scripts/tool-registry.json lacks - add it with its kind and what it does"));
    let mut names: Vec<&String> = registry
        .keys()
        .filter(|n| !calls.contains_key(*n))
        .collect();
    names.sort();
    let extra = names.into_iter().map(|n| format!("scripts/tool-registry.json: `{n}` is registered but no code records it - remove the entry, or record its runs"));
    lacks.chain(extra).collect()
}

/// `l7r-gate check tool-signals [--root <repo>]`.
pub(super) fn cli(args: &[String], here: &Path) -> Outcome {
    let root = args
        .windows(2)
        .find(|w| w[0] == "--root")
        .map_or(here, |w| Path::new(&w[1]));
    let findings: Vec<String> = unrecorded(root)
        .into_iter()
        .chain(mismatched(root))
        .collect();
    if findings.is_empty() {
        return Outcome::out(String::new());
    }
    Outcome::refuse(
        findings
            .iter()
            .flat_map(|f| ["check-tool-signals: ", f.as_str(), "\n"])
            .collect(),
    )
}

#[cfg(test)]
mod tests;
