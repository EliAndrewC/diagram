//! No tool without its record (feature 406 T05, FR-004, D164; feature 449 T068, from `check-tool-signals.py`).
//!
//! WHY (the GM 2026-10-19): "there should at least be a way that it is notionally possible for us to see how often a tool is used, right?
//! Or how often it makes a difference". `make tool-yield` reads what each tool leaves behind; a tool added later that leaves nothing would
//! sit in its table as a blank row forever. This refuses that tool before it lands.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::measure::tool_inventory::{check_paths, hook_guards, registry};

use super::Outcome;

/// The name its runs are recorded under in the `usage_log`.
pub(super) const USAGE_LOG_TOOL: &str = "check-tool-signals";
/// What a file that records its runs names: the guard log, the usage log by name (a Rust caller's `USAGE_LOG_TOOL`) or by its command
/// (`l7r-gate log usage`, the one writer's door since `usage_log.py` left, feature 449 T129), or a stated record.
const RECORDS: [&str; 4] = ["guard_log", "usage_log", "log usage", "# TOOL_RECORD:"];
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

/// The hooks and checks that leave no record, each with its fix: the hooks and checks `tool_yield`'s inventory lists, read through
/// the one inventory (`core`'s `measure::tool_inventory`, feature 449 T120), so a settings file, Makefile or gate script it cannot read
/// fails the check as `check-tool-signals.py`'s import of `tool_yield` failed it.
fn unrecorded(root: &Path) -> Result<Vec<String>, String> {
    let mut paths = check_paths(root)?;
    paths.extend(
        hook_guards(root)?
            .iter()
            .map(|n| root.join(format!("scripts/hooks/{n}-hooks.sh"))),
    );
    Ok(paths
        .iter()
        .filter(|p| p.is_file() && !RECORDS.iter().any(|m| read(p).contains(m)))
        .map(|p| {
            let rel = p.strip_prefix(root).unwrap_or(p).display();
            let stem = p.file_stem().unwrap_or_default().to_string_lossy();
            format!("{rel}: records none of its runs. Record its exit with `l7r-gate.sh log usage --tool {stem} --kind check --outcome <passed|refused>` (a check), call `guard_log` (a hook), or add `# TOOL_RECORD: <where its runs are seen>` near its top, and register a usage-log name in scripts/tool-registry.json")
        })
        .collect())
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
        // a test module records nothing: its fixtures name tools by the same `--tool` words (feature 449 T129, whose door's tests
        // record scratch tools `a` to `h`)
        files.extend(rust.into_iter().filter(|p| {
            p.extension().is_some_and(|x| x == "rs")
                && !p
                    .file_name()
                    .is_some_and(|n| n.to_string_lossy().ends_with("tests.rs"))
        }));
    }
    files.push(root.join("Makefile"));
    files.sort();
    let mut out = BTreeMap::new();
    for path in &files {
        let text = read(path);
        if !RECORDS[1..3].iter().any(|m| text.contains(m)) {
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

fn mismatched(root: &Path) -> Result<Vec<String>, String> {
    let registry = registry(root)?;
    let calls = called(root);
    let lacks = calls.iter().filter(|(name, _)| !registry.contains_key(*name)).map(|(name, at)| format!("{at}: records `{name}`, which scripts/tool-registry.json lacks - add it with its kind and what it does"));
    let mut names: Vec<&String> = registry
        .keys()
        .filter(|n| !calls.contains_key(*n))
        .collect();
    names.sort();
    let extra = names.into_iter().map(|n| format!("scripts/tool-registry.json: `{n}` is registered but no code records it - remove the entry, or record its runs"));
    Ok(lacks.chain(extra).collect())
}

/// `l7r-gate check tool-signals [--root <repo>]`.
pub(super) fn cli(args: &[String], here: &Path) -> Outcome {
    let root = args
        .windows(2)
        .find(|w| w[0] == "--root")
        .map_or(here, |w| Path::new(&w[1]));
    let findings: Vec<String> = match unrecorded(root).and_then(|mut found| {
        found.extend(mismatched(root)?);
        Ok(found)
    }) {
        Ok(found) => found,
        Err(why) => return Outcome::refuse(format!("check-tool-signals: {why}\n")),
    };
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
