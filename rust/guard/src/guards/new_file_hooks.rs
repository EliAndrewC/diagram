//! `new-file-hooks` (feature 265 FR-010; ported from the shell of the same name and `lib/hm_new_file.py`, feature 449 T047): A NEW GLOSSARY FILE,
//! REGISTRY ENTRY OR QUESTION TAKES A RESERVED PREFIX. Each takes "the highest + 10", so two queues at once take the same number; `make reserve`
//! allocates under a host-wide lock and writes the stub, and this makes it the only way a new such file appears. A Write creating one, or a shell
//! redirect or `tee` naming one that does not exist yet, whose prefix and key the ledger does not hold, is refused. `RESERVE_OK` with a reason is
//! the escape.

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "new-file-hooks",
    events: &["PreToolUse"],
    matcher: "Write|Bash",
    decide,
};

/// The directory a path names and its kind (`KIND_OF`).
const KIND_OF: [(&str, &str); 3] = [
    ("assets/glossary", "glossary"),
    ("sources/010-works-cited", "registry"),
    ("research/questions", "question"),
];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// Registry prefixes passed 9990 on 2026-09-27, so a prefix is four OR five digits; the lookbehind keeps a five-digit name from being read as its
// last four.
static TARGET: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:>>?|\btee\s+(?:-a\s+)?)\s*["']?([^\s"'<>|;&]*?(?<!\d)(\d{4,5})-([^\s"'<>|;&/]+?)\.(json|html))["']?(?=[\s;|&)]|$)"#,
    )
});
static NAME: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d+)-(.+)\.(json|html)$"));
// Feature 383 amendment 5: a variable the command itself assigns is resolved before the path is judged - a fixture record built under
// `D=$(mktemp -d)` was refused as a new question of this repository, twice in one session (2026-10-17).
static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[\s;&|(])([A-Za-z_]\w*)=(?:"([^"$]*)"|'([^']*)'|(\$\(mktemp\b[^)]*\))|([^\s;&|"'$()]+))"#,
    )
});
static LEADING_VAR: LazyLock<Regex> = LazyLock::new(|| re(r"^\$\{?([A-Za-z_]\w*)\}?(/.*)$"));

/// One file a call would create: its path where the command makes it knowable.
struct Target {
    kind: &'static str,
    path: Option<PathBuf>,
    key: String,
    prefix: u64,
}

fn kind_of_path(path: &str) -> Option<&'static str> {
    KIND_OF
        .iter()
        .find(|(d, _)| path.contains(&format!("/{d}/")))
        .map(|(_, k)| *k)
}

/// How many directories below the repository a kind's files sit (`reserve-prefix.py`'s `DIRS`).
fn depth(kind: &str) -> usize {
    match kind {
        "glossary" => 5,
        "registry" => 3,
        _ => 2,
    }
}

/// Each variable the command assigns a literal (its value) or a `$(mktemp ...)` (None).
fn assigned(cmd: &str) -> HashMap<String, Option<String>> {
    ASSIGN
        .captures_iter(cmd)
        .flatten()
        .filter_map(|m| {
            let name = m.get(1)?.as_str().to_owned();
            let value = (m.get(4).is_none())
                .then(|| [2, 3, 5].iter().find_map(|g| m.get(*g)))
                .map(|g| g.map_or_else(String::new, |v| v.as_str().to_owned()));
            Some((name, value))
        })
        .collect()
}

/// `raw` with a leading variable the command assigned replaced by its value; None under a mktemp directory.
fn resolved(raw: &str, names: &HashMap<String, Option<String>>) -> Option<String> {
    let Ok(Some(m)) = LEADING_VAR.captures(raw) else {
        return Some(raw.to_owned());
    };
    let name = m.get(1).map_or("", |g| g.as_str());
    let tail = m.get(2).map_or("", |g| g.as_str());
    match names.get(name) {
        None => Some(raw.to_owned()),
        Some(value) => value.as_ref().map(|v| format!("{v}{tail}")),
    }
}

/// The repository a path is in, else the path itself.
fn top(p: &Path) -> PathBuf {
    let real = realpath(p);
    real.ancestors()
        .find(|a| a.join(".git").exists())
        .map_or_else(|| p.to_path_buf(), Path::to_path_buf)
}

fn shell_targets(cmd: &str, base: &Path) -> Vec<Target> {
    // a target is a redirect's or `tee`'s (T052: compiling these for a command with neither was 1.8 ms)
    if !cmd.contains('>') && !cmd.contains("tee") {
        return Vec::new();
    }
    let names = assigned(cmd);
    let mut out = Vec::new();
    for m in TARGET.captures_iter(cmd).flatten() {
        let group = |n: usize| m.get(n).map_or("", |g| g.as_str());
        let Some(raw) = resolved(group(1), &names) else {
            continue;
        };
        let known = !raw.contains('$');
        let joined = base.join(&raw);
        let found = kind_of_path(&format!("/{}", joined.display()));
        if known && (found.is_none() || top(&joined) != top(base)) {
            continue;
        }
        let by_ext = if group(4) == "json" {
            "glossary"
        } else {
            "registry"
        };
        out.push(Target {
            kind: found.unwrap_or(by_ext),
            path: known.then_some(joined),
            key: group(3).to_owned(),
            prefix: group(2).parse().unwrap_or_default(),
        });
    }
    out
}

fn write_target(file: &str) -> Option<Target> {
    let kind = kind_of_path(file)?;
    let name = Path::new(file).file_name()?.to_string_lossy().into_owned();
    let m = NAME.captures(&name).ok()??;
    Some(Target {
        kind,
        path: Some(PathBuf::from(file)),
        key: m.get(2)?.as_str().to_owned(),
        prefix: m.get(1)?.as_str().parse().ok()?,
    })
}

/// Whether another file of this stem is on file: a question's notes or drawing page beside a question that exists.
fn stem_exists(dir: &Path, prefix: u64, key: &str) -> bool {
    let stem = format!("{prefix:04}-{key}.");
    std::fs::read_dir(dir).is_ok_and(|d| {
        d.filter_map(Result::ok)
            .any(|e| e.file_name().to_string_lossy().starts_with(&stem))
    })
}

fn mirror_of(root: PathBuf) -> PathBuf {
    match root.parent().and_then(|p| Some((p, p.parent()?))) {
        Some((p, up)) if p.file_name().is_some_and(|n| n == ".clones") => up.to_path_buf(),
        _ => root,
    }
}

/// Whether the ledger holds this prefix for this kind and this key: a number taken by hand that collides is another key on a reserved prefix.
fn reserved(kind: &str, prefix: u64, mirror: &Path, key: &str) -> bool {
    let text = std::fs::read_to_string(mirror.join(".specify/prefixes.jsonl")).unwrap_or_default();
    text.lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .any(|row| {
            field(&row, "kind") == kind
                && row.get("prefix").and_then(Value::as_u64) == Some(prefix)
                && field(&row, "key") == key
        })
}

fn strip_companion(key: &str) -> &str {
    let key = key
        .strip_suffix(".notes")
        .or_else(|| key.strip_suffix(".originals"))
        .unwrap_or(key);
    key.strip_suffix(".drawing").unwrap_or(key)
}

/// The kind and key of a target that takes a reservation it does not hold.
fn unreserved(target: Target, base: &Path) -> Option<(&'static str, String)> {
    let Target {
        kind,
        path,
        mut key,
        prefix,
    } = target;
    if let Some(p) = &path {
        if p.exists() {
            return None;
        }
    }
    if kind == "question" {
        key = strip_companion(&key).to_owned();
        if path
            .as_deref()
            .and_then(Path::parent)
            .is_some_and(|d| stem_exists(d, prefix, &key))
        {
            return None;
        }
    }
    let root = path
        .as_deref()
        .and_then(|p| p.ancestors().nth(depth(kind) + 1))
        .unwrap_or(base);
    let plain = key.replace("%2F", "/").replace("%25", "%");
    (!reserved(kind, prefix, &mirror_of(top(root)), &plain)).then_some((kind, plain))
}

/// The kind and key the refusal's `make reserve` names, or None.
pub(crate) fn verdict(event: &Event, here: &Path) -> Option<(&'static str, String)> {
    let input = event.input.get("tool_input")?;
    let given = field(&event.input, "cwd");
    let base = if given.is_empty() {
        here
    } else {
        Path::new(given)
    };
    let targets = match event.tool() {
        "Write" => write_target(field(input, "file_path"))
            .into_iter()
            .collect(),
        "Bash" => shell_targets(field(input, "command"), base),
        _ => Vec::new(),
    };
    targets.into_iter().find_map(|t| unreserved(t, base))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let Some((kind, key)) = verdict(event, &std::env::current_dir().unwrap_or_default()) else {
        return Vec::new();
    };
    let input = event.input.get("tool_input");
    let cmd = input.map_or("", |t| field(t, "command"));
    let text: String = Some(cmd)
        .filter(|c| !c.is_empty())
        .unwrap_or_else(|| input.map_or("", |t| field(t, "file_path")))
        .chars()
        .take(200)
        .collect();
    match escape_or_refuse(cmd, "RESERVE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "new-file",
                "escaped",
                &why,
                "unreserved",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(refusal) => {
            log::fire(
                "new-file",
                "blocked",
                &text,
                "RESERVE_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(refusal)];
        }
        Escape::None => {}
    }
    log::fire(
        "new-file",
        "blocked",
        &text,
        "unreserved",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "BLOCKED: a new {kind} file takes a RESERVED prefix, so parallel queues never collide:\n    make reserve KIND={kind} KEY=\"{key}\"   (at the repository root) - it writes the stub; then fill that file"
    ))]
}

#[cfg(test)]
mod tests;
