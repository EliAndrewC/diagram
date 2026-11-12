//! What the report reads beside the events (`feature_report.py`'s git and run-log readers, feature 449 T119): the feature's commits, its
//! diff's hand-written lines, its gate runs, its spec rounds and plan reviews, its tasks' starts and ticks.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::record::py_lines;
use serde_json::{Map, Value};

use super::super::events::{git, head, iso_utc, py_int, re, read_text, s, ts, Raised, Tally};

static SPEC_ROUND: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\s*-\s*Round \d+ \(.*?\):\s*([A-Z][A-Z -]+?)\s+-"));
static SPEC_ROUND_FIDELITY: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^\s*-\s*spec-fidelity[\w-]*, (?:Mode \d,|amendment \d+) round \d+ \(.*?\):\s*([A-Z][A-Z ]+?)(?=[.:]|\s+-|$)",
    )
});
static TICKED: LazyLock<Regex> = LazyLock::new(|| re(r"^\+- \[[xX]\] (T\d+[a-z]?)\b"));
static DONE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[[xX]\]"));
static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[[ xX]\]"));
/// What a session does not write by hand, and the specs' own bookkeeping, are not "the feature's own diff" (FR-009's cascade ratio):
/// measured on 372's waves 106-111, 4,252 lines of `dev/claims-index.json` and 5,057 of a regenerated `ranking.md` would have made 96
/// dispatches look like 0.02 a line (`GENERATED`).
static GENERATED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\.(svg|json|jsonl|png|webp)$|^specs/|^dev/(run-log|perf-log|bypass-log|idle-log)/|^pool/.*\.notes\.md$",
    )
});

/// A commit: (sha, UTC time, subject).
pub type Commit = (String, String, String);

/// Inside [since, until] as the report bounds a UTC time: `since[:19]` and `until[:19] + "Z"`.
fn inside(t: &str, since: &str, until: &str) -> bool {
    (since.is_empty() || t >= head(since, 19))
        && (until.is_empty() || t <= format!("{}Z", head(until, 19)).as_str())
}

/// (sha, UTC time, subject) of every commit whose message names the feature (`Feature 375`, `375 T04`, `375: ...`), in [since, until]
/// (`commits`). The colon form is the research clone's: missing it read 343's 69 dispatches over 1 changed line.
///
/// # Errors
///
/// A git line the Python could not unpack, or a time it could not read.
pub fn commits(
    root: &Path,
    feature: &str,
    since: &str,
    until: &str,
) -> Result<Vec<Commit>, Raised> {
    let n = py_int(feature)?;
    let grep = format!("--grep=(Feature|feature) {n}\\b|^{n}[ :]");
    let mut out = Vec::new();
    for raw in py_lines(&git(
        root,
        &["log", "--all", "-E", &grep, "--format=%H\x1f%aI\x1f%s"],
    )?) {
        let mut parts = raw.splitn(3, '\x1f');
        let (Some(sha), Some(t), Some(subj)) = (parts.next(), parts.next(), parts.next()) else {
            return Err("ValueError: not enough values to unpack".to_owned());
        };
        let t = iso_utc(t)?;
        if inside(&t, since, until) {
            out.push((sha.to_owned(), t, subj.to_owned()));
        }
    }
    Ok(out)
}

/// Lines added and removed by the feature's commits in hand-written files outside `specs/` (`diff_lines`).
///
/// # Errors
///
/// A git run the Python could not read.
pub fn diff_lines(root: &Path, shas: &[&str]) -> Result<u64, Raised> {
    let mut total = 0;
    for sha in shas {
        for raw in py_lines(&git(root, &["show", "--numstat", "--format=", sha])?) {
            let parts: Vec<&str> = raw.split('\t').collect();
            if parts.len() == 3
                && !parts[0].is_empty()
                && parts[0].bytes().all(|b| b.is_ascii_digit())
                && !GENERATED.is_match(parts[2]).unwrap_or(false)
            {
                total +=
                    parts[0].parse::<u64>().unwrap_or(0) + parts[1].parse::<u64>().unwrap_or(0);
            }
        }
    }
    Ok(total)
}

/// Every `*.json` under `dev/run-log/`, a symlinked directory not walked (`rglob`).
fn json_files(dir: &Path, out: &mut Vec<PathBuf>) {
    for name in super::super::events::names(dir) {
        let p = dir.join(&name);
        if std::fs::symlink_metadata(&p).is_ok_and(|m| m.is_dir()) {
            json_files(&p, out);
        }
        #[expect(
            clippy::case_sensitive_file_extension_comparisons,
            reason = "`rglob(\"*.json\")` is case-sensitive on Linux, as this is"
        )]
        let json = name.ends_with(".json");
        if json {
            out.push(p);
        }
    }
}

/// The run log's gate runs (`target` `done`) at one of the feature's commits inside its window, as (UTC, result).
fn runs(
    root: &Path,
    shas: &HashSet<&str>,
    since: &str,
    until: &str,
) -> Result<Vec<(String, Value)>, Raised> {
    let mut files = Vec::new();
    json_files(&root.join("dev").join("run-log"), &mut files);
    let mut out = Vec::new();
    for p in files {
        // an unreadable file, one that is not UTF-8 or not JSON is skipped (`except (OSError, ValueError)`); one that is JSON but no
        // object is the Python's `AttributeError`
        let Ok(text) = read_text(&p) else { continue };
        let Ok(d) = serde_json::from_str::<Value>(&text) else {
            continue;
        };
        let Some(d) = d.as_object() else {
            return Err(format!("AttributeError: {} is no object", p.display()));
        };
        let d: &Map<String, Value> = d;
        let utc = super::super::events::or_s(d, "utc");
        if d.get("target").and_then(Value::as_str) != Some("done") || !inside(&utc, since, until) {
            continue;
        }
        let commit = super::super::events::or_text(d.get("commit").unwrap_or(&Value::Null), "-");
        if shas.iter().any(|sha| sha.starts_with(&commit)) {
            out.push((utc, d.get("result").cloned().unwrap_or(Value::Null)));
        }
    }
    Ok(out)
}

/// (UTC, green|red) of the feature's gate runs in order (`gate_sequence`).
///
/// # Errors
///
/// A run record that is JSON but no object.
#[expect(clippy::implicit_hasher, reason = "the report's own set of shas")]
pub fn gate_sequence(
    root: &Path,
    shas: &HashSet<&str>,
    since: &str,
    until: &str,
) -> Result<Vec<(String, String)>, Raised> {
    let mut out: Vec<(String, String)> = runs(root, shas, since, until)?
        .into_iter()
        .filter(|(_, r)| r.as_str() != Some("already-verified"))
        .map(|(utc, r)| {
            let red = l7r_gate_core::record::bundle::py_str(&r).starts_with("failed");
            (utc, if red { "red" } else { "green" }.to_owned())
        })
        .collect();
    out.sort();
    Ok(out)
}

/// Gate runs at one of the feature's commits, inside its window, by result (`gates`).
///
/// # Errors
///
/// A run record that is JSON but no object.
#[expect(clippy::implicit_hasher, reason = "the report's own set of shas")]
pub fn gates(
    root: &Path,
    shas: &HashSet<&str>,
    since: &str,
    until: &str,
) -> Result<Tally<String>, Raised> {
    let mut out = Tally::default();
    for (_, r) in runs(root, shas, since, until)? {
        let res = super::super::events::or_text(&r, "");
        out.add(
            &if res.starts_with("failed") {
                "red".to_owned()
            } else {
                res
            },
            1.0,
        );
    }
    Ok(out)
}

/// The spec's Review history, by verdict (`spec_rounds`).
#[must_use]
pub fn spec_rounds(text: &str) -> Tally<String> {
    let mut out = Tally::default();
    for line in py_lines(text) {
        let hit = [&*SPEC_ROUND, &*SPEC_ROUND_FIDELITY]
            .into_iter()
            .find_map(|p| p.captures(line).ok().flatten());
        if let Some(c) = hit {
            out.add(
                &c[1]
                    .trim_matches(l7r_guard::shared::py_text::is_space)
                    .to_owned(),
                1.0,
            );
        }
    }
    out
}

/// How many recorded plan reviews were BLOCKED - every version of `plan-review.json` the feature's commits wrote (`plan_blocks`).
///
/// # Errors
///
/// A git run the Python could not read.
#[expect(clippy::implicit_hasher, reason = "the report's own set of shas")]
pub fn plan_blocks(root: &Path, name: &str, shas: &HashSet<&str>) -> Result<usize, Raised> {
    let file = format!("specs/{name}/plan-review.json");
    let mut n = 0;
    for sha in git(root, &["log", "--format=%H", "--", &file])?.split_whitespace() {
        if shas.contains(sha)
            && git(root, &["show", &format!("{sha}:{file}")])?.contains("\"verdict\": \"BLOCKED\"")
        {
            n += 1;
        }
    }
    Ok(n)
}

/// (ticked, boxes) of `tasks.md` (`tasks_done`).
///
/// # Errors
///
/// A `tasks.md` that cannot be read as UTF-8.
pub fn tasks_done(d: &Path) -> Result<(usize, usize), Raised> {
    let text = super::super::events::text_if_file(&d.join("tasks.md"))?;
    Ok((DONE.find_iter(&text).count(), BOX.find_iter(&text).count()))
}

/// Each task's first `make task-start`, as epoch seconds, in the order first seen (`task_starts`).
///
/// # Errors
///
/// A starts file that cannot be read, a row that is no object, or one with no time the Python could read.
pub fn task_starts(root: &Path, name: &str) -> Result<Vec<(String, f64)>, Raised> {
    let common = git(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    )?;
    let common = l7r_guard::shared::py_text::strip(&common);
    let mut out: Vec<(String, f64)> = Vec::new();
    if common.is_empty() {
        return Ok(out);
    }
    let path = Path::new(common).join("task-starts.jsonl");
    let text = super::super::events::text_if_file(&path)?;
    for raw in py_lines(&text) {
        let Ok(row) = serde_json::from_str::<Value>(raw) else {
            continue;
        };
        let Some(row) = row.as_object() else {
            return Err("AttributeError: a task start is no object".to_owned());
        };
        if row.get("feature").and_then(Value::as_str) == Some(name)
            && super::super::events::on(row, "task")
        {
            let task = s(row, "task");
            let t = ts(&l7r_gate_core::record::bundle::py_str(
                super::super::events::need(row, "utc")?,
            ))?;
            if !out.iter().any(|(k, _)| *k == task) {
                out.push((task, t));
            }
        }
    }
    Ok(out)
}

/// When each task was ticked: the first commit adding its `- [x] Txx` line to the feature's tasks.md (`task_ticks`).
///
/// # Errors
///
/// A git run the Python could not read.
pub fn task_ticks(root: &Path, name: &str) -> Result<Vec<(String, f64)>, Raised> {
    let text = git(
        root,
        &[
            "log",
            "--reverse",
            "--format=@@%ct",
            "-p",
            "--",
            &format!("specs/{name}/tasks.md"),
        ],
    )?;
    let mut out: Vec<(String, f64)> = Vec::new();
    let mut when = 0.0;
    for line in py_lines(&text) {
        let rest = line.strip_prefix("@@").unwrap_or("");
        if line.starts_with("@@") && !rest.is_empty() && rest.bytes().all(|b| b.is_ascii_digit()) {
            when = rest.parse().unwrap_or(0.0);
        } else if let Ok(Some(c)) = TICKED.captures(line) {
            if !out.iter().any(|(k, _)| *k == c[1]) {
                out.push((c[1].to_owned(), when));
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
