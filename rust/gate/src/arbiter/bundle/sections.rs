//! The arbiter bundle's sections (from `arbiter_bundle.py`, feature 375 FR-011): what owes a capped round, the cascade and the oscillation, the round counters, the red gates, the cited evidence, the claims a question names. The review and plan rounds and the feature's own files are [`super::reviews`].

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::log_path;
use l7r_guard::shared::checks::rounds::ROUND_CAP;
use l7r_guard::shared::checks::state_path;
use l7r_guard::shared::log::civil;
use l7r_guard::shared::py_text::strip;
use serde_json::{json, Value};

use crate::record::bundle::{findall, head, hit, py_str, pyre, shown, sort_paths, write, Run};
use crate::record::owed::unanswered;
use crate::record::py_lines;
use crate::record::repo::{fail, git, git_out, Fail};
use crate::record::units::Unit;

/// A diff between two reds past this many lines is shown by its stat alone (the round arbiter's fix on red-gate@2026-10-19T02:31:38Z).
const BETWEEN_DIFF_LINES: usize = 1500;

static ROUTES: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?i)\broutes?\b|\bregress"));
static MAP_WORDS: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r"(?i)\bmaps?\b|\bseeds?\b|\bcohorts?\b|\bpool\b|\binashiro\b|\.gen\.py|l7r/diagram/|\bhamlets?\b|\bvillages?\b",
    )
});
static NAMED: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"`([A-Za-z_]\w*)`|\b([A-Z][A-Z0-9_]{3,})\b"));
static LOOSE: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"(?i)\b\d[\d,]*(?:\.\d+)?\s*(?:ft|feet|acres?|px|sq ft|degrees?|%|households?)\b")
});
static VALUE_UNIT: LazyLock<Regex> = LazyLock::new(|| pyre(r"^([\d,.]+)\s*(.*)"));
static MODAL_KEY: LazyLock<Regex> = LazyLock::new(|| pyre(r"^[+-]([A-Z][A-Za-z]*):"));
static PAGE_IN: LazyLock<Regex> = LazyLock::new(|| pyre(r"research/questions/([^ ]+?\.html)"));

/// `_git`: stdout on success, else "".
pub(crate) fn g(root: &Path, args: &[&str]) -> String {
    git(root, args)
}

pub(crate) fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v.get(k).and_then(Value::as_str).unwrap_or("")
}

/// Whether a value is what Python reads as true.
pub(crate) fn truthy(v: Option<&Value>) -> bool {
    !l7r_guard::shared::checks::falsy(v)
}

/// `str(v.get(k, default))`.
pub(crate) fn field(v: &Value, k: &str, default: &str) -> String {
    v.get(k).map_or_else(|| default.to_owned(), py_str)
}

/// The commits touching `files`, oldest first, as cascade lines (feature 374's bridgehead ruling).
fn git_flow(root: &Path, files: &[String]) -> Vec<String> {
    let mut args = vec!["log", "--reverse", "--format=%cI %h %s", "--"];
    args.extend(files.iter().map(String::as_str));
    py_lines(&g(root, &args))
        .into_iter()
        .filter_map(|ln| {
            ln.split_once(' ').map(|(_, rest)| {
                format!(
                    "{} commit {rest}",
                    ln.chars().skip(11).take(8).collect::<String>()
                )
            })
        })
        .collect()
}

/// Whether the round's diff shows what owes a unit (feature 374 wave 122).
pub(crate) fn owe_evidence(slug: &str, diff: &str) -> String {
    let name = slug
        .split_once('#')
        .map_or_else(|| slug.split_once(':').map_or(slug, |p| p.1), |p| p.1);
    let lines = py_lines(diff);
    let changed = lines.iter().any(|ln| {
        (ln.starts_with('+') || ln.starts_with('-'))
            && !ln.starts_with("+++")
            && !ln.starts_with("---")
            && ln.contains(name)
    });
    if matches!(name, "unfootnoted" | "gloss") || changed {
        return "a changed line in `owes-round.diff` names it".to_owned();
    }
    if !slug.contains('#')
        && lines.iter().any(|ln| {
            (ln.starts_with("diff --git") || ln.starts_with("+++ ") || ln.starts_with("--- "))
                && ln.contains(&format!("/{name}-"))
        })
    {
        return format!("`owes-round.diff` changes a file of {name}");
    }
    if name.contains('/') {
        let keys = modal_changed_keys(name, &lines);
        if !keys.is_empty() {
            return format!("`owes-round.diff` changes its {} line(s)", keys.join(", "));
        }
    }
    format!("NO changed line in `owes-round.diff` names `{name}` - its cause is not in this round's change; say so in the ruling")
}

/// The keyed lines a diff changes in the modal file of `name`, and each research page it touches.
pub(crate) fn modal_changed_keys(name: &str, lines: &[&str]) -> Vec<String> {
    let (mut keys, mut in_modal): (Vec<String>, bool) = (Vec::new(), false);
    for ln in lines {
        if ln.starts_with("diff --git") || ln.starts_with("+++ ") || ln.starts_with("--- ") {
            if ln.starts_with("+++ ") || ln.starts_with("diff --git") {
                in_modal = ln.contains(&format!("modals/{name}.md"));
                if let Some(c) = PAGE_IN.captures(ln).ok().flatten() {
                    let label = format!("the page {}", &c[1]);
                    if !keys.contains(&label) {
                        keys.push(label);
                    }
                }
            }
            continue;
        }
        if in_modal && (ln.starts_with('+') || ln.starts_with('-')) {
            let label = MODAL_KEY
                .captures(ln)
                .ok()
                .flatten()
                .map_or_else(|| "a continuation".to_owned(), |c| c[1].to_owned());
            if !keys.contains(&label) {
                keys.push(label);
            }
        }
    }
    keys
}

/// The earliest of each owing note's OWN last read (the round arbiter's fix on round:source-reader|q:0262@8).
fn key_since(rounds: &[Value], owing: &[Unit], since: f64) -> f64 {
    let mut starts = Vec::new();
    for u in owing {
        let key = u.subject().split_once('#').map_or("", |p| p.1);
        if key.is_empty() {
            continue;
        }
        let mine: Vec<f64> = rounds
            .iter()
            .filter(|r| {
                !truthy(r.get("notes"))
                    || r.get("notes")
                        .and_then(Value::as_array)
                        .is_some_and(|n| n.iter().any(|x| x.as_str() == Some(key)))
            })
            .map(|r| r.get("t").and_then(Value::as_f64).unwrap_or(0.0))
            .collect();
        if let Some(m) = mine.into_iter().reduce(f64::max) {
            starts.push(m);
        }
    }
    if since == 0.0 {
        return since;
    }
    starts.into_iter().fold(since, f64::min)
}

/// `int(x)` of an epoch.
#[expect(clippy::cast_possible_truncation, reason = "`int(since)`, an epoch")]
fn int(x: f64) -> i64 {
    x.trunc() as i64
}

/// `args`, then `--` and the files.
fn with_files<'a>(mut args: Vec<&'a str>, files: &'a [String]) -> Vec<&'a str> {
    args.push("--");
    args.extend(files.iter().map(String::as_str));
    args
}

/// What owes the CAPPED round itself (feature 374 wave 120): the record's owed reason now, and the commits since the last round.
pub(crate) fn capped_round_cause(
    root: &Path,
    out: &Path,
    (check, subject): (&str, &str),
    files: &[String],
    since: f64,
    rounds: &[Value],
) -> Result<Vec<String>, Fail> {
    let name = subject.split_once(':').map_or(subject, |p| p.1);
    let checks: Vec<&str> = if check == "modal-research" {
        vec!["modal-accuracy", "modal-references", "modal-gaps"]
    } else {
        vec![check]
    };
    let mut owed: Vec<String> = Vec::new();
    let owing: Vec<Unit> = match unanswered(root) {
        Ok(all) => all
            .into_iter()
            .filter(|u| {
                checks.contains(&u.check())
                    && [name.to_owned(), format!("{name}.drawing")]
                        .iter()
                        .any(|n| n == u.subject().split('#').next().unwrap_or(""))
            })
            .collect(),
        Err(e) => {
            owed = vec![format!("- (the record's owed list could not be read: {e})")];
            Vec::new()
        }
    };
    let since = key_since(rounds, &owing, since);
    let at = format!("--since=@{}", int(since));
    let log = if since != 0.0 && !files.is_empty() {
        g(
            root,
            &with_files(vec!["log", &at, "--format=%h %ad %s", "--date=iso"], files),
        )
    } else {
        String::new()
    };
    let hunks = if strip(&log).is_empty() {
        String::new()
    } else {
        g(
            root,
            &with_files(
                vec!["log", &at, "-p", "--format=--- %h %ad %s", "--date=iso"],
                files,
            ),
        )
    };
    let diff = hunks + &g(root, &with_files(vec!["diff"], files));
    write(
        &out.join("owes-round.diff"),
        if diff.is_empty() {
            "(no change since the last round)\n"
        } else {
            &diff
        },
    )?;
    if !owing.is_empty() {
        owed = owing
            .iter()
            .map(|u| {
                format!(
                    "- `{}`: {} - {}",
                    u.slug,
                    u.occasion,
                    owe_evidence(&u.slug, &diff)
                )
            })
            .collect();
    }
    let owed = if owed.is_empty() {
        "- (nothing listed as owed)".to_owned()
    } else {
        owed.join("\n")
    };
    let commits: Vec<String> = py_lines(&log).iter().map(|ln| format!("- {ln}")).collect();
    let commits = if commits.is_empty() {
        "- none; the working tree only".to_owned()
    } else {
        commits.join("\n")
    };
    Ok(vec![
        "## What owes the capped round\n".to_owned(),
        format!("The record owes it now:\n{owed}\n"),
        format!("Commits on the unit's files since the last round's dispatch (`owes-round.diff` beside this file holds their hunks and the working tree):\n{commits}\n"),
    ])
}

/// `json.loads` of each line of a JSONL file, a line that does not parse skipped (`event_log.read_jsonl`).
fn read_jsonl(path: &Path) -> Vec<Value> {
    let bytes = std::fs::read(path).unwrap_or_default();
    String::from_utf8_lossy(&bytes)
        .split('\n')
        .map(strip)
        .filter(|l| !l.is_empty())
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

/// (path, time) of every Edit that put back a passage an earlier Edit of the same file had replaced (`feature_report.reversals`, which T83 takes from here).
pub(crate) fn reversals(events: &[Value]) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = Vec::new();
    let mut replaced: HashMap<String, HashSet<String>> = HashMap::new();
    for e in events {
        if text(e, "ev") != "PreToolUse" || text(e, "tool") != "Edit" || !truthy(e.get("old")) {
            continue;
        }
        let path = e.get("path").map_or_else(|| "None".to_owned(), py_str);
        let seen = replaced.entry(path.clone()).or_default();
        if e.get("new")
            .and_then(Value::as_str)
            .is_some_and(|n| seen.contains(n))
        {
            out.push((
                path.clone(),
                e.get("t").map_or_else(|| "None".to_owned(), py_str),
            ));
        }
        seen.insert(e.get("old").map_or_else(String::new, py_str));
    }
    out
}

/// The cascade and the oscillation - for a unit, only the edits and reversals on its own files (343's rulings).
pub(crate) fn flow_sections(
    root: &Path,
    out: &Path,
    d: Option<&Path>,
    files: &[String],
) -> Result<Vec<String>, Fail> {
    let log = d.map(|d| log_path(root, &d.file_name().unwrap_or_default().to_string_lossy()));
    let events = log
        .filter(|l| l.is_file())
        .map_or_else(Vec::new, |l| read_jsonl(&l));
    let mine = |p: Option<&Value>| {
        let p = p
            .filter(|v| truthy(Some(v)))
            .map_or_else(String::new, py_str);
        files.is_empty() || files.iter().any(|f| p.ends_with(f.as_str()))
    };
    let mut flow: Vec<String> = events
        .iter()
        .filter(|e| {
            text(e, "ev") == "PreToolUse"
                && ((text(e, "cat") == "edit" && mine(e.get("path")))
                    || (text(e, "tool") == "Agent" && files.is_empty()))
        })
        .map(|e| {
            let t: String = e
                .get("t")
                .map(py_str)
                .unwrap_or_default()
                .chars()
                .skip(11)
                .take(8)
                .collect();
            let what = ["path", "agent", "make"]
                .iter()
                .find_map(|k| e.get(*k).filter(|v| truthy(Some(v))))
                .map_or_else(String::new, py_str);
            format!("{t} {} {what}", field(e, "tool", "None"))
        })
        .collect();
    let mut source = "";
    if !files.is_empty() && flow.is_empty() {
        flow = git_flow(root, files);
        source = " (from the git log - the event log held no edit on them)";
    }
    let tail = &flow[flow.len().saturating_sub(200)..];
    write(&out.join("cascade.txt"), &(tail.join("\n") + "\n"))?;
    let scope = format!(
        "{}{source}",
        if files.is_empty() {
            "the feature"
        } else {
            "the unit's files"
        }
    );
    let rev: Vec<String> = reversals(&events)
        .into_iter()
        .filter(|(p, _)| files.is_empty() || files.iter().any(|f| p.ends_with(f.as_str())))
        .map(|(p, t)| {
            format!(
                "- {p} at {}: an edit put back text an earlier edit replaced",
                t.chars().skip(11).take(8).collect::<String>()
            )
        })
        .collect();
    let rev = if rev.is_empty() {
        format!("- none on {scope} in the event log")
    } else {
        rev.join("\n")
    };
    Ok(vec![
        format!(
            "## The cascade\n\n`cascade.txt`: the last {} edits{} on {scope}, in order.\n",
            flow.len().min(200),
            if files.is_empty() {
                " and dispatches"
            } else {
                ""
            }
        ),
        format!("## Oscillation\n\n{rev}\n"),
    ])
}

pub(crate) fn json_file(path: &Path) -> Result<Value, ()> {
    let t = std::fs::read_to_string(path).map_err(|_| ())?;
    serde_json::from_str(&t).map_err(|_| ())
}

/// What the record checks' guard counted for a record check's `unit` (feature 374 batch 7); none where it holds nothing.
fn record_round_counter(root: &Path, unit: &str) -> Vec<String> {
    let state = match state_path(&root.to_string_lossy()) {
        Some(p) => match json_file(&p) {
            Ok(v) => v,
            Err(()) => return Vec::new(),
        },
        None => json!({}),
    };
    let n = state
        .get("rounds")
        .and_then(|r| r.get(unit))
        .and_then(Value::as_u64)
        .unwrap_or(0);
    if n == 0 {
        return Vec::new();
    }
    let base = state
        .get("rebased")
        .and_then(|r| r.get(unit))
        .filter(|b| truthy(Some(b)));
    let since = base.map_or_else(String::new, |b| {
        format!(
            "; a new change rebased the count at round {}",
            field(b, "n", "0")
        )
    });
    vec![format!("## The round counter\n\nrecord check `{unit}`: {n} round(s) counted in this feature{since} (`hm_checks.py`, the cap ROUND_CAP = {ROUND_CAP} past the rebase).\n")]
}

/// What the pair guard counted for `unit`'s round cap (feature 374 batch 5); a record check's from `hm_checks.py`.
pub(crate) fn round_counter(root: &Path, unit: &str) -> Vec<String> {
    let record = record_round_counter(root, unit);
    if !record.is_empty() {
        return record;
    }
    let (Ok(feature), Ok(rounds)) = (
        json_file(&root.join(".specify").join("feature.json")),
        json_file(&root.join(".git").join("review-rounds.json")),
    ) else {
        return Vec::new();
    };
    let feature = feature
        .get("feature_directory")
        .filter(|v| truthy(Some(v)))
        .map_or_else(|| "none".to_owned(), py_str);
    let kept: Vec<String> = rounds
        .get(&feature)
        .and_then(|f| f.get(unit))
        .and_then(Value::as_array)
        .map(|a| a.iter().map(py_str).collect())
        .unwrap_or_default();
    let landed: i64 = strip(&g(
        root,
        &[
            "log",
            "-1",
            "--format=%ct",
            "origin/main",
            "--",
            &format!("{feature}/tasks.md"),
        ],
    ))
    .parse()
    .unwrap_or(0);
    let live: Vec<&String> = kept
        .iter()
        .filter(|k| {
            k.rsplit_once('@')
                .map_or(0, |p| p.1.parse::<i64>().unwrap_or(0))
                >= landed
        })
        .collect();
    let when = if landed == 0 {
        "never (nothing landed)".to_owned()
    } else {
        let (y, mo, d, h, mi, s) = civil(u64::try_from(landed).unwrap_or(0));
        format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
    };
    let names = if live.is_empty() {
        "none".to_owned()
    } else {
        live.iter()
            .map(|s| s.as_str())
            .collect::<Vec<_>>()
            .join(", ")
    };
    vec![format!("## The round counter\n\nepoch: {when} (the feature's tasks.md last landed on origin/main). Rounds counted after it: {} of the {} kept - {names}.\n", live.len(), kept.len())]
}

/// The commits on HEAD's first-parent line, or None outside a repository.
fn own_line(root: &Path) -> Option<HashSet<String>> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-list", "--first-parent", "HEAD"])
        .output()
        .ok()?;
    done.status.success().then(|| {
        String::from_utf8_lossy(&done.stdout)
            .split_whitespace()
            .map(str::to_owned)
            .collect()
    })
}

/// What changed between two counted reds (feature 385 T49).
fn between(root: &Path, a: &Value, b: &Value) -> Vec<String> {
    let commit = |v: &Value| {
        v.get("commit")
            .filter(|c| truthy(Some(c)))
            .map_or_else(String::new, py_str)
    };
    let (ca, cb) = (commit(a), commit(b));
    if ca.is_empty() || cb.is_empty() {
        return vec!["  (between these two: a run without a commit - no diff)".to_owned()];
    }
    if ca == cb {
        return vec!["  (between these two: the same commit; uncommitted edits between them are not recorded)".to_owned()];
    }
    let stat = strip(&git_out(root, &["diff", "--stat", &ca, &cb])).to_owned();
    let diff = git_out(root, &["diff", &ca, &cb])
        .trim_end_matches(l7r_guard::shared::py_text::is_space)
        .to_owned();
    if stat.is_empty() && diff.is_empty() {
        return vec![format!("  (between these two: no diff from {ca} to {cb} - a commit is not in this clone, or nothing changed)")];
    }
    if diff.matches('\n').count() > BETWEEN_DIFF_LINES {
        return vec![format!("  between {ca} and {cb} (the diff runs past {BETWEEN_DIFF_LINES} lines - its stat alone):"), String::new(), "```".to_owned(), stat, "```".to_owned(), String::new()];
    }
    vec![
        format!("  between {ca} and {cb}:"),
        String::new(),
        "```".to_owned(),
        stat,
        String::new(),
        diff,
        "```".to_owned(),
        String::new(),
    ]
}

/// A red-gate trigger's evidence: the last four red `make done` runs of this feature's line, each with its own failed tests (feature 374 batch 10, 385).
pub(crate) fn red_gate_runs(root: &Path) -> Vec<String> {
    let mut files: Vec<PathBuf> = Vec::new();
    for d in std::fs::read_dir(root.join("dev").join("run-log"))
        .into_iter()
        .flatten()
        .flatten()
    {
        files.extend(
            std::fs::read_dir(d.path())
                .into_iter()
                .flatten()
                .flatten()
                .map(|e| e.path())
                .filter(|p| p.extension().is_some_and(|x| x == "json")),
        );
    }
    sort_paths(&mut files);
    let mut runs: Vec<Value> = files
        .iter()
        .filter_map(|f| json_file(f).ok())
        .filter(|r| {
            let result = field(r, "result", "");
            r.get("target").and_then(Value::as_str) == Some("done")
                && result.starts_with("failed")
                && result != "failed: tree moved"
        })
        .collect();
    if let Some(line) = own_line(root) {
        runs.retain(|r| {
            let c = r
                .get("commit")
                .filter(|c| truthy(Some(c)))
                .map_or_else(|| "-".to_owned(), py_str);
            !truthy(r.get("commit"))
                || line
                    .iter()
                    .any(|l| c.starts_with(head(l, c.chars().count())))
        });
    }
    let shown_runs = &runs[runs.len().saturating_sub(4)..];
    let mut lines = Vec::new();
    for (k, r) in shown_runs.iter().enumerate() {
        if k > 0 {
            lines.extend(between(root, &shown_runs[k - 1], r));
        }
        lines.push(format!(
            "- {} at {}: {}, {} test(s) failed",
            field(r, "utc", "?"),
            field(r, "commit", "?"),
            field(r, "result", "None"),
            field(r, "failed_tests", "?")
        ));
        lines.extend(
            r.get("failed_names")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .map(|n| format!("  - {}", py_str(n))),
        );
    }
    let body = if lines.is_empty() {
        "- (no red make done in the run log)".to_owned()
    } else {
        lines.join("\n")
    };
    vec![format!(
        "## The red gates counted, each with its own failed tests\n\n{body}\n"
    )]
}

/// Copy each file a question cites into `evidence/` beside the MANIFEST and name each (ask:b13-w149-strip-route).
pub(crate) fn evidence_section(out: &Path, files: &[String]) -> Result<Vec<String>, Fail> {
    if files.is_empty() {
        return Ok(Vec::new());
    }
    let ev = out.join("evidence");
    if !ev.is_dir() {
        std::fs::create_dir(&ev).map_err(fail)?;
    }
    let mut rows = Vec::new();
    for f in files {
        let src = crate::record::bundle::py_path(f);
        if src.is_file() {
            let (stem, suffix) = (
                src.file_stem()
                    .map_or_else(String::new, |s| s.to_string_lossy().into_owned()),
                src.extension()
                    .map_or_else(String::new, |s| format!(".{}", s.to_string_lossy())),
            );
            let mut dst = ev.join(src.file_name().unwrap_or_default());
            let mut n = 2;
            while dst.exists() {
                dst = ev.join(format!("{stem}-{n}{suffix}"));
                n += 1;
            }
            std::fs::copy(&src, &dst).map_err(fail)?;
            rows.push(format!(
                "- `evidence/{}` (from `{f}`)",
                dst.file_name().unwrap_or_default().to_string_lossy()
            ));
        } else {
            rows.push(format!(
                "- MISSING: `{f}` - cited, not found when the bundle was built"
            ));
        }
    }
    Ok(vec![format!(
        "## The evidence the question cites\n\n{}\n",
        rows.join("\n")
    )])
}

/// What a route or regression question leaves unstated about the POOL (ask:b13-w149-route-matrix); none where nothing is owed.
pub(crate) fn pool_unstated(why: &str, files: &[String]) -> Vec<String> {
    if !hit(&ROUTES, why) || !hit(&MAP_WORDS, why) {
        return Vec::new();
    }
    let mut texts: Vec<(String, String)> = Vec::new();
    for f in files {
        let p = crate::record::bundle::py_path(f);
        if p.is_file() && !texts.iter().any(|(k, _)| k == f) {
            texts.push((
                f.clone(),
                String::from_utf8_lossy(&std::fs::read(&p).unwrap_or_default()).into_owned(),
            ));
        }
    }
    let mut gaps: Vec<String> = texts
        .iter()
        .filter(|(f, t)| {
            crate::record::bundle::py_path(f)
                .file_name()
                .is_some_and(|n| n.to_string_lossy().to_lowercase().starts_with("route"))
                && !t.to_lowercase().contains("pool")
        })
        .map(|(f, _)| format!("{f}: a route's evidence states no pool result"))
        .collect();
    if !why.to_lowercase().contains("pool")
        && !texts.iter().any(|(_, t)| t.to_lowercase().contains("pool"))
    {
        gaps.insert(
            0,
            "the question names a route or a regression and states no pool result".to_owned(),
        );
    }
    gaps
}

/// Each research claim on a name the question or its evidence cites, with its class and last verdict (ask:t06-scattered-single-file); the rows and index through the runner (Q1a, to Rust in T82).
pub(crate) fn claims_section(
    run: &mut Run,
    root: &Path,
    texts: &[String],
) -> Result<Vec<String>, Fail> {
    let names: HashSet<String> = texts
        .iter()
        .flat_map(|t| {
            NAMED
                .captures_iter(t)
                .flatten()
                .map(|c| {
                    c.get(1)
                        .or_else(|| c.get(2))
                        .map_or_else(String::new, |m| m.as_str().to_owned())
                })
                .collect::<Vec<_>>()
        })
        .collect();
    let numbers: BTreeSet<String> = texts
        .iter()
        .flat_map(|t| findall(&LOOSE, t, 0))
        .map(|n| l7r_guard::shared::py_text::split(&n).join(" "))
        .collect();
    if names.is_empty() && numbers.is_empty() {
        return Ok(Vec::new());
    }
    let index = run.door.ask("load_index", &json!([shown(root)]))?;
    let cur = run.door.ask("claims_rows", &json!([shown(root)]))?;
    let mut keys: Vec<&String> = cur
        .as_object()
        .map(|m| m.keys().collect())
        .unwrap_or_default();
    keys.sort();
    let line = |key: &str| {
        let row = &cur[key];
        let backing = text(row, "backing");
        let kind = if backing == "POINTER" {
            "a research page"
        } else {
            backing
        };
        let verdict = index
            .get(key)
            .and_then(|r| r.get("verdict"))
            .map_or_else(|| "none".to_owned(), py_str);
        format!(
            "`{key}` - {kind}: `{}` (last verdict {verdict})",
            text(row, "line")
        )
    };
    let cited = |k: &str| {
        let after = k.split_once("::").map_or("", |p| p.1);
        let unit = after.split_once('#').map_or(after, |p| p.0);
        names.contains(unit.rsplit_once('.').map_or(unit, |p| p.1))
    };
    let mut rows: Vec<String> = keys
        .iter()
        .filter(|k| cited(k))
        .map(|k| format!("- {}", line(k)))
        .collect();
    for n in &numbers {
        let c = VALUE_UNIT.captures(n).ok().flatten();
        let (value, unit) = c.as_ref().map_or(("", ""), |c| {
            (
                c.get(1).map_or("", |m| m.as_str()),
                c.get(2).map_or("", |m| m.as_str()),
            )
        });
        let pat = pyre(&format!(
            r"(?i)(?<![\d.]){}\s*{}",
            fancy_regex::escape(&value.replace(',', "")),
            fancy_regex::escape(head(unit, 2))
        ));
        let hits: Vec<String> = keys
            .iter()
            .filter(|k| hit(&pat, &text(&cur[k.as_str()], "line").replace(',', "")))
            .take(4)
            .map(|k| line(k))
            .collect();
        rows.push(format!(
            "- `{n}`: {}",
            if hits.is_empty() {
                "no claim states it - a measurement, or a value derived from others".to_owned()
            } else {
                hits.join("; ")
            }
        ));
    }
    if rows.is_empty() {
        return Ok(Vec::new());
    }
    Ok(vec![format!(
        "## The numbers it names, as the code claims them (research, ours or a convention)\n\n{}\n",
        rows.join("\n")
    )])
}

#[cfg(test)]
mod tests;
