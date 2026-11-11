//! The arbiter bundle's sections (from `arbiter_bundle.py`, feature 375 FR-011): what owes a capped round, the cascade and the oscillation, the round counters, the red gates, the cited evidence, the claims a question names, the review and plan rounds, the feature's request and spec.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::log_path;
use l7r_guard::shared::checks::reply;
use l7r_guard::shared::checks::rounds::ROUND_CAP;
use l7r_guard::shared::checks::state_path;
use l7r_guard::shared::log::civil;
use l7r_guard::shared::py_text::strip;
use serde_json::{json, Map, Value};

use super::marks::{mark_rounds, transcripts};
use crate::record::bundle::{findall, head, hit, py_str, pyre, relative, shown, sort_paths, write, Run};
use crate::record::owed::unanswered;
use crate::record::py_lines;
use crate::record::repo::{fail, git, git_out, read_text, Fail};
use crate::record::units::Unit;

/// A diff between two reds past this many lines is shown by its stat alone (the round arbiter's fix on red-gate@2026-10-19T02:31:38Z).
const BETWEEN_DIFF_LINES: usize = 1500;

static ROUTES: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?i)\broutes?\b|\bregress"));
static MAP_WORDS: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"(?i)\bmaps?\b|\bseeds?\b|\bcohorts?\b|\bpool\b|\binashiro\b|\.gen\.py|l7r/diagram/|\bhamlets?\b|\bvillages?\b")
});
static NAMED: LazyLock<Regex> = LazyLock::new(|| pyre(r"`([A-Za-z_]\w*)`|\b([A-Z][A-Z0-9_]{3,})\b"));
static LOOSE: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"(?i)\b\d[\d,]*(?:\.\d+)?\s*(?:ft|feet|acres?|px|sq ft|degrees?|%|households?)\b")
});
static VALUE_UNIT: LazyLock<Regex> = LazyLock::new(|| pyre(r"^([\d,.]+)\s*(.*)"));
static SPEC_ROUND: LazyLock<Regex> = LazyLock::new(|| pyre(r"MODE (?:2|3)\b|SPECIFICATION REVIEW"));
static VERDICT: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"[Vv]erdict\W{0,6}(FAITHFUL|CHANGES REQUIRED|NOT FAITHFUL|BLOCKED|CLEAR)"));
static REVIEWS: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"(?:^MODE 3 \(VERIFY\) - round \d+ of (?:feature |specs/)|specs/)(\d+-[a-z0-9][a-z0-9-]*?)(?=[/,\s.']|$)")
});
static FEATURE_NUMBER: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?:^|[^a-z0-9])f(\d{3})(?:[^0-9]|$)"));
static MODAL_KEY: LazyLock<Regex> = LazyLock::new(|| pyre(r"^[+-]([A-Z][A-Za-z]*):"));
static PAGE_IN: LazyLock<Regex> = LazyLock::new(|| pyre(r"research/questions/([^ ]+?\.html)"));

/// `_git`: stdout on success, else "".
pub(crate) fn g(root: &Path, args: &[&str]) -> String {
    git(root, args)
}

fn text<'a>(v: &'a Value, k: &str) -> &'a str {
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
        .filter_map(|ln| ln.split_once(' ').map(|(_, rest)| format!("{} commit {rest}", ln.chars().skip(11).take(8).collect::<String>())))
        .collect()
}

/// Whether the round's diff shows what owes a unit (feature 374 wave 122).
pub(crate) fn owe_evidence(slug: &str, diff: &str) -> String {
    let name = slug.split_once('#').map_or_else(|| slug.split_once(':').map_or(slug, |p| p.1), |p| p.1);
    let lines = py_lines(diff);
    let changed = lines.iter().any(|ln| (ln.starts_with('+') || ln.starts_with('-')) && !ln.starts_with("+++") && !ln.starts_with("---") && ln.contains(name));
    if matches!(name, "unfootnoted" | "gloss") || changed {
        return "a changed line in `owes-round.diff` names it".to_owned();
    }
    if !slug.contains('#') && lines.iter().any(|ln| (ln.starts_with("diff --git") || ln.starts_with("+++ ") || ln.starts_with("--- ")) && ln.contains(&format!("/{name}-"))) {
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
            let label = MODAL_KEY.captures(ln).ok().flatten().map_or_else(|| "a continuation".to_owned(), |c| c[1].to_owned());
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
                !truthy(r.get("notes")) || r.get("notes").and_then(Value::as_array).is_some_and(|n| n.iter().any(|x| x.as_str() == Some(key)))
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

/// What owes the CAPPED round itself (feature 374 wave 120): the record's owed reason now, and the commits since the last round.
pub(crate) fn capped_round_cause(root: &Path, out: &Path, (check, subject): (&str, &str), files: &[String], since: f64, rounds: &[Value]) -> Result<Vec<String>, Fail> {
    let name = subject.split_once(':').map_or(subject, |p| p.1);
    let checks: Vec<&str> = if check == "modal-research" { vec!["modal-accuracy", "modal-references", "modal-gaps"] } else { vec![check] };
    let mut owed: Vec<String> = Vec::new();
    let owing: Vec<Unit> = match unanswered(root) {
        Ok(all) => all
            .into_iter()
            .filter(|u| checks.contains(&u.check()) && [name.to_owned(), format!("{name}.drawing")].iter().any(|n| n == u.subject().split('#').next().unwrap_or("")))
            .collect(),
        Err(e) => {
            owed = vec![format!("- (the record's owed list could not be read: {e})")];
            Vec::new()
        }
    };
    let since = key_since(rounds, &owing, since);
    let at = format!("--since=@{}", int(since));
    fn with_files<'a>(mut args: Vec<&'a str>, files: &'a [String]) -> Vec<&'a str> {
        args.push("--");
        args.extend(files.iter().map(String::as_str));
        args
    }
    let log = if since != 0.0 && !files.is_empty() { g(root, &with_files(vec!["log", &at, "--format=%h %ad %s", "--date=iso"], files)) } else { String::new() };
    let hunks = if strip(&log).is_empty() { String::new() } else { g(root, &with_files(vec!["log", &at, "-p", "--format=--- %h %ad %s", "--date=iso"], files)) };
    let diff = hunks + &g(root, &with_files(vec!["diff"], files));
    write(&out.join("owes-round.diff"), if diff.is_empty() { "(no change since the last round)\n" } else { &diff })?;
    if !owing.is_empty() {
        owed = owing.iter().map(|u| format!("- `{}`: {} - {}", u.slug, u.occasion, owe_evidence(&u.slug, &diff))).collect();
    }
    let owed = if owed.is_empty() { "- (nothing listed as owed)".to_owned() } else { owed.join("\n") };
    let commits: Vec<String> = py_lines(&log).iter().map(|ln| format!("- {ln}")).collect();
    let commits = if commits.is_empty() { "- none; the working tree only".to_owned() } else { commits.join("\n") };
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
    let (mut out, mut replaced): (Vec<(String, String)>, HashMap<String, HashSet<String>>) = (Vec::new(), HashMap::new());
    for e in events {
        if text(e, "ev") != "PreToolUse" || text(e, "tool") != "Edit" || !truthy(e.get("old")) {
            continue;
        }
        let path = e.get("path").map_or_else(|| "None".to_owned(), py_str);
        let seen = replaced.entry(path.clone()).or_default();
        if e.get("new").and_then(Value::as_str).is_some_and(|n| seen.contains(n)) {
            out.push((path.clone(), e.get("t").map_or_else(|| "None".to_owned(), py_str)));
        }
        seen.insert(e.get("old").map_or_else(String::new, py_str));
    }
    out
}

/// The cascade and the oscillation - for a unit, only the edits and reversals on its own files (343's rulings).
pub(crate) fn flow_sections(root: &Path, out: &Path, d: Option<&Path>, files: &[String]) -> Result<Vec<String>, Fail> {
    let log = d.map(|d| log_path(root, &d.file_name().unwrap_or_default().to_string_lossy()));
    let events = log.filter(|l| l.is_file()).map_or_else(Vec::new, |l| read_jsonl(&l));
    let mine = |p: Option<&Value>| {
        let p = p.filter(|v| truthy(Some(v))).map_or_else(String::new, py_str);
        files.is_empty() || files.iter().any(|f| p.ends_with(f.as_str()))
    };
    let mut flow: Vec<String> = events
        .iter()
        .filter(|e| text(e, "ev") == "PreToolUse" && ((text(e, "cat") == "edit" && mine(e.get("path"))) || (text(e, "tool") == "Agent" && files.is_empty())))
        .map(|e| {
            let t: String = e.get("t").map(py_str).unwrap_or_default().chars().skip(11).take(8).collect();
            let what = ["path", "agent", "make"].iter().find_map(|k| e.get(*k).filter(|v| truthy(Some(v)))).map_or_else(String::new, py_str);
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
    let scope = format!("{}{source}", if files.is_empty() { "the feature" } else { "the unit's files" });
    let rev: Vec<String> = reversals(&events)
        .into_iter()
        .filter(|(p, _)| files.is_empty() || files.iter().any(|f| p.ends_with(f.as_str())))
        .map(|(p, t)| format!("- {p} at {}: an edit put back text an earlier edit replaced", t.chars().skip(11).take(8).collect::<String>()))
        .collect();
    let rev = if rev.is_empty() { format!("- none on {scope} in the event log") } else { rev.join("\n") };
    Ok(vec![
        format!("## The cascade\n\n`cascade.txt`: the last {} edits{} on {scope}, in order.\n", flow.len().min(200), if files.is_empty() { " and dispatches" } else { "" }),
        format!("## Oscillation\n\n{rev}\n"),
    ])
}

fn json_file(path: &Path) -> Result<Value, ()> {
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
    let n = state.get("rounds").and_then(|r| r.get(unit)).and_then(Value::as_u64).unwrap_or(0);
    if n == 0 {
        return Vec::new();
    }
    let base = state.get("rebased").and_then(|r| r.get(unit)).filter(|b| truthy(Some(b)));
    let since = base.map_or_else(String::new, |b| format!("; a new change rebased the count at round {}", field(b, "n", "0")));
    vec![format!("## The round counter\n\nrecord check `{unit}`: {n} round(s) counted in this feature{since} (`hm_checks.py`, the cap ROUND_CAP = {ROUND_CAP} past the rebase).\n")]
}

/// What the pair guard counted for `unit`'s round cap (feature 374 batch 5); a record check's from `hm_checks.py`.
pub(crate) fn round_counter(root: &Path, unit: &str) -> Vec<String> {
    let record = record_round_counter(root, unit);
    if !record.is_empty() {
        return record;
    }
    let (Ok(feature), Ok(rounds)) = (json_file(&root.join(".specify").join("feature.json")), json_file(&root.join(".git").join("review-rounds.json"))) else {
        return Vec::new();
    };
    let feature = feature.get("feature_directory").filter(|v| truthy(Some(v))).map_or_else(|| "none".to_owned(), py_str);
    let kept: Vec<String> = rounds.get(&feature).and_then(|f| f.get(unit)).and_then(Value::as_array).map(|a| a.iter().map(py_str).collect()).unwrap_or_default();
    let landed: i64 = strip(&g(root, &["log", "-1", "--format=%ct", "origin/main", "--", &format!("{feature}/tasks.md")])).parse().unwrap_or(0);
    let live: Vec<&String> = kept.iter().filter(|k| k.rsplit_once('@').map_or(0, |p| p.1.parse::<i64>().unwrap_or(0)) >= landed).collect();
    let when = if landed == 0 {
        "never (nothing landed)".to_owned()
    } else {
        let (y, mo, d, h, mi, s) = civil(u64::try_from(landed).unwrap_or(0));
        format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
    };
    let names = if live.is_empty() { "none".to_owned() } else { live.iter().map(|s| s.as_str()).collect::<Vec<_>>().join(", ") };
    vec![format!("## The round counter\n\nepoch: {when} (the feature's tasks.md last landed on origin/main). Rounds counted after it: {} of the {} kept - {names}.\n", live.len(), kept.len())]
}

/// The commits on HEAD's first-parent line, or None outside a repository.
fn own_line(root: &Path) -> Option<HashSet<String>> {
    let done = Command::new("git").arg("-C").arg(root).args(["rev-list", "--first-parent", "HEAD"]).output().ok()?;
    done.status.success().then(|| String::from_utf8_lossy(&done.stdout).split_whitespace().map(str::to_owned).collect())
}

/// What changed between two counted reds (feature 385 T49).
fn between(root: &Path, a: &Value, b: &Value) -> Vec<String> {
    let commit = |v: &Value| v.get("commit").filter(|c| truthy(Some(c))).map_or_else(String::new, py_str);
    let (ca, cb) = (commit(a), commit(b));
    if ca.is_empty() || cb.is_empty() {
        return vec!["  (between these two: a run without a commit - no diff)".to_owned()];
    }
    if ca == cb {
        return vec!["  (between these two: the same commit; uncommitted edits between them are not recorded)".to_owned()];
    }
    let stat = strip(&git_out(root, &["diff", "--stat", &ca, &cb])).to_owned();
    let diff = git_out(root, &["diff", &ca, &cb]).trim_end_matches(l7r_guard::shared::py_text::is_space).to_owned();
    if stat.is_empty() && diff.is_empty() {
        return vec![format!("  (between these two: no diff from {ca} to {cb} - a commit is not in this clone, or nothing changed)")];
    }
    if diff.matches('\n').count() > BETWEEN_DIFF_LINES {
        return vec![format!("  between {ca} and {cb} (the diff runs past {BETWEEN_DIFF_LINES} lines - its stat alone):"), String::new(), "```".to_owned(), stat, "```".to_owned(), String::new()];
    }
    vec![format!("  between {ca} and {cb}:"), String::new(), "```".to_owned(), stat, String::new(), diff, "```".to_owned(), String::new()]
}

/// A red-gate trigger's evidence: the last four red `make done` runs of this feature's line, each with its own failed tests (feature 374 batch 10, 385).
pub(crate) fn red_gate_runs(root: &Path) -> Vec<String> {
    let mut files: Vec<PathBuf> = Vec::new();
    for d in std::fs::read_dir(root.join("dev").join("run-log")).into_iter().flatten().flatten() {
        files.extend(std::fs::read_dir(d.path()).into_iter().flatten().flatten().map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "json")));
    }
    sort_paths(&mut files);
    let mut runs: Vec<Value> = files
        .iter()
        .filter_map(|f| json_file(f).ok())
        .filter(|r| {
            let result = field(r, "result", "");
            r.get("target").and_then(Value::as_str) == Some("done") && result.starts_with("failed") && result != "failed: tree moved"
        })
        .collect();
    if let Some(line) = own_line(root) {
        runs.retain(|r| {
            let c = r.get("commit").filter(|c| truthy(Some(c))).map_or_else(|| "-".to_owned(), py_str);
            !truthy(r.get("commit")) || line.iter().any(|l| c.starts_with(head(l, c.chars().count())))
        });
    }
    let shown_runs = &runs[runs.len().saturating_sub(4)..];
    let mut lines = Vec::new();
    for (k, r) in shown_runs.iter().enumerate() {
        if k > 0 {
            lines.extend(between(root, &shown_runs[k - 1], r));
        }
        lines.push(format!("- {} at {}: {}, {} test(s) failed", field(r, "utc", "?"), field(r, "commit", "?"), field(r, "result", "None"), field(r, "failed_tests", "?")));
        lines.extend(r.get("failed_names").and_then(Value::as_array).into_iter().flatten().map(|n| format!("  - {}", py_str(n))));
    }
    let body = if lines.is_empty() { "- (no red make done in the run log)".to_owned() } else { lines.join("\n") };
    vec![format!("## The red gates counted, each with its own failed tests\n\n{body}\n")]
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
                src.file_stem().map_or_else(String::new, |s| s.to_string_lossy().into_owned()),
                src.extension().map_or_else(String::new, |s| format!(".{}", s.to_string_lossy())),
            );
            let mut dst = ev.join(src.file_name().unwrap_or_default());
            let mut n = 2;
            while dst.exists() {
                dst = ev.join(format!("{stem}-{n}{suffix}"));
                n += 1;
            }
            std::fs::copy(&src, &dst).map_err(fail)?;
            rows.push(format!("- `evidence/{}` (from `{f}`)", dst.file_name().unwrap_or_default().to_string_lossy()));
        } else {
            rows.push(format!("- MISSING: `{f}` - cited, not found when the bundle was built"));
        }
    }
    Ok(vec![format!("## The evidence the question cites\n\n{}\n", rows.join("\n"))])
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
            texts.push((f.clone(), String::from_utf8_lossy(&std::fs::read(&p).unwrap_or_default()).into_owned()));
        }
    }
    let mut gaps: Vec<String> = texts
        .iter()
        .filter(|(f, t)| crate::record::bundle::py_path(f).file_name().is_some_and(|n| n.to_string_lossy().to_lowercase().starts_with("route")) && !t.to_lowercase().contains("pool"))
        .map(|(f, _)| format!("{f}: a route's evidence states no pool result"))
        .collect();
    if !why.to_lowercase().contains("pool") && !texts.iter().any(|(_, t)| t.to_lowercase().contains("pool")) {
        gaps.insert(0, "the question names a route or a regression and states no pool result".to_owned());
    }
    gaps
}

/// Each research claim on a name the question or its evidence cites, with its class and last verdict (ask:t06-scattered-single-file); the rows and index through the runner (Q1a, to Rust in T82).
pub(crate) fn claims_section(run: &mut Run, root: &Path, texts: &[String]) -> Result<Vec<String>, Fail> {
    let names: HashSet<String> = texts
        .iter()
        .flat_map(|t| NAMED.captures_iter(t).flatten().map(|c| c.get(1).or_else(|| c.get(2)).map_or_else(String::new, |m| m.as_str().to_owned())).collect::<Vec<_>>())
        .collect();
    let numbers: BTreeSet<String> = texts.iter().flat_map(|t| findall(&LOOSE, t, 0)).map(|n| l7r_guard::shared::py_text::split(&n).join(" ")).collect();
    if names.is_empty() && numbers.is_empty() {
        return Ok(Vec::new());
    }
    let index = run.door.ask("load_index", json!([shown(root)]))?;
    let cur = run.door.ask("claims_rows", json!([shown(root)]))?;
    let mut keys: Vec<&String> = cur.as_object().map(|m| m.keys().collect()).unwrap_or_default();
    keys.sort();
    let line = |key: &str| {
        let row = &cur[key];
        let backing = text(row, "backing");
        let kind = if backing == "POINTER" { "a research page" } else { backing };
        let verdict = index.get(key).and_then(|r| r.get("verdict")).map_or_else(|| "none".to_owned(), py_str);
        format!("`{key}` - {kind}: `{}` (last verdict {verdict})", text(row, "line"))
    };
    let named = |k: &str| {
        let after = k.split_once("::").map_or("", |p| p.1);
        let unit = after.split_once('#').map_or(after, |p| p.0);
        names.contains(unit.rsplit_once('.').map_or(unit, |p| p.1))
    };
    let mut rows: Vec<String> = keys.iter().filter(|k| named(k)).map(|k| format!("- {}", line(k))).collect();
    for n in &numbers {
        let c = VALUE_UNIT.captures(n).ok().flatten();
        let (value, unit) = c.as_ref().map_or(("", ""), |c| (c.get(1).map_or("", |m| m.as_str()), c.get(2).map_or("", |m| m.as_str())));
        let pat = pyre(&format!(r"(?i)(?<![\d.]){}\s*{}", fancy_regex::escape(&value.replace(',', "")), fancy_regex::escape(head(unit, 2))));
        let hits: Vec<String> = keys.iter().filter(|k| hit(&pat, &text(&cur[k.as_str()], "line").replace(',', ""))).take(4).map(|k| line(k)).collect();
        rows.push(format!("- `{n}`: {}", if hits.is_empty() { "no claim states it - a measurement, or a value derived from others".to_owned() } else { hits.join("; ") }));
    }
    if rows.is_empty() {
        return Ok(Vec::new());
    }
    Ok(vec![format!("## The numbers it names, as the code claims them (research, ours or a convention)\n\n{}\n", rows.join("\n"))])
}

/// A JSON file's object, or {} where it does not parse.
fn object(path: &Path) -> Map<String, Value> {
    json_file(path).ok().and_then(|v| v.as_object().cloned()).unwrap_or_default()
}

/// An ask about a plan review carries that review's rounds (ask:t14-plan-round4): (lines, the plan's path).
pub(crate) fn plan_rounds(d: &Path) -> (Vec<String>, PathBuf) {
    let review = object(&d.join("plan-review.json"));
    let rounds: Vec<&Value> = review.get("block_reviews").and_then(Value::as_array).into_iter().flatten().filter(|r| r.is_object()).collect();
    let plan = d.join("plan.md");
    let Some(last) = rounds.last() else {
        return (vec!["## The plan review's rounds\n\n- (none recorded in plan-review.json)\n".to_owned()], plan);
    };
    let blocks = |r: &Value| -> HashSet<String> { r.get("blocks").and_then(Value::as_array).into_iter().flatten().map(py_str).collect() };
    let subject = blocks(last);
    let mut rows = Vec::new();
    for (i, r) in rounds.iter().filter(|r| !subject.is_disjoint(&blocks(r))).enumerate() {
        rows.push(format!("### Round {}: {} ({})\n", i + 1, field(r, "verdict", "?"), field(r, "reviewed", "?")));
        let found: Vec<String> = r
            .get("decisions")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter(|x| x.is_object() && x.get("class").and_then(Value::as_str) != Some("within"))
            .map(|x| {
                let s = format!("- {} - {}: {} {}", field(x, "id", "?"), field(x, "class", "?"), field(x, "summary", ""), field(x, "why", ""));
                s.trim_end_matches(l7r_guard::shared::py_text::is_space).to_owned()
            })
            .collect();
        if found.is_empty() {
            rows.push("- every decision within".to_owned());
        } else {
            rows.extend(found);
        }
        rows.push(String::new());
    }
    (vec![format!("## The plan review's rounds (the blocks of the newest round)\n\n{}\n", rows.join("\n"))], plan)
}

/// The text a subagent was dispatched with: its transcript's first record.
fn first_prompt(transcript: &Path) -> String {
    let Ok(bytes) = std::fs::read(transcript) else {
        return String::new();
    };
    let all = String::from_utf8_lossy(&bytes);
    let line = all.split_inclusive('\n').next().unwrap_or("");
    let first: Value = if line.is_empty() { json!({}) } else {
        match serde_json::from_str(line) {
            Ok(v) => v,
            Err(_) => return String::new(),
        }
    };
    let content = first.get("message").filter(|m| truthy(Some(m))).and_then(|m| m.get("content"));
    match content {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Array(items)) => items.iter().filter(|b| b.is_object()).map(|b| text(b, "text")).collect(),
        _ => String::new(),
    }
}

/// The feature a review's dispatch REVIEWS (413-money-tooltip-on-the-record#1@6).
fn reviewed_feature(prompt: &str) -> String {
    let p = prompt.trim_start_matches(l7r_guard::shared::py_text::is_space);
    REVIEWS.captures(p).ok().flatten().and_then(|c| c.get(1)).map_or_else(String::new, |m| m.as_str().to_owned())
}

/// A spec review's rounds, each reviewer's whole reply beside the MANIFEST and its findings marked (387's ruling).
pub(crate) fn spec_rounds(out: &Path, subject: &str) -> Result<Vec<String>, Fail> {
    let mut found: Vec<(std::time::SystemTime, PathBuf)> = Vec::new();
    let mut all: Vec<PathBuf> = Vec::new();
    for a in std::fs::read_dir(transcripts()).into_iter().flatten().flatten() {
        for b in std::fs::read_dir(a.path()).into_iter().flatten().flatten() {
            for f in std::fs::read_dir(b.path().join("subagents")).into_iter().flatten().flatten() {
                let n = f.file_name().to_string_lossy().into_owned();
                if n.starts_with("agent-") && n.ends_with(".jsonl") {
                    all.push(f.path());
                }
            }
        }
    }
    sort_paths(&mut all);
    for f in all {
        let prompt = first_prompt(&f);
        if reviewed_feature(&prompt) == subject && hit(&SPEC_ROUND, &prompt) && !prompt.contains("MODE 4") {
            found.push((std::fs::metadata(&f).and_then(|m| m.modified()).map_err(fail)?, f));
        }
    }
    if found.is_empty() {
        return Ok(vec!["- (no spec review dispatch found in the subagent transcripts - read the Review history)\n".to_owned()]);
    }
    found.sort_by(|a, b| a.0.cmp(&b.0).then_with(|| a.1.components().cmp(b.1.components())));
    let replies: Vec<String> = found.iter().map(|(_, f)| reply::reply_of(&f.to_string_lossy(), "")).collect();
    let mut lines = Vec::new();
    for (i, (r, marked)) in replies.iter().zip(mark_rounds(&replies, &[])).enumerate() {
        let i = i + 1;
        let verdict = if r.is_empty() { "no reply (stopped)".to_owned() } else { VERDICT.captures(r).ok().flatten().map_or_else(|| "no verdict".to_owned(), |c| c[1].to_owned()) };
        lines.push(format!("### Round {i}: spec-fidelity ({verdict})\n"));
        if !r.is_empty() {
            write(&out.join(format!("round-{i}-spec-fidelity.md")), r)?;
            lines.push(format!("The whole reply: `round-{i}-spec-fidelity.md` beside this file."));
        }
        if marked.is_empty() {
            lines.push(if r.is_empty() { "- (no reply)" } else { "- (no findings it numbers or bullets - read the whole reply)" }.to_owned());
        } else {
            lines.extend(marked.iter().map(|(m, f)| format!("- {m}: {f}")));
        }
        lines.push(String::new());
    }
    Ok(vec![lines.join("\n") + "\n"])
}

/// A review unit's earlier rounds from its verdict record and its ledger rows, where the check state holds none (feature 374 batch 4).
pub(crate) fn review_verdicts(root: &Path, out: &Path, subject: &str) -> Result<Vec<String>, Fail> {
    let git_dir = strip(&g(root, &["rev-parse", "--absolute-git-dir"])).to_owned();
    let git_dir = if git_dir.is_empty() { root.join(".git") } else { PathBuf::from(git_dir) };
    let rec = git_dir.join("review-verdicts").join(format!("{subject}.json"));
    if subject.is_empty() || !rec.is_file() {
        return Ok(Vec::new());
    }
    std::fs::copy(&rec, out.join("earlier-verdict.json")).map_err(fail)?;
    let (check, name) = (subject.split("--").next().unwrap_or(subject), subject.split_once("--").map_or(subject, |p| p.1));
    let ledger = root.join("dev").join("review-ledger.md");
    let rows: Vec<String> = if ledger.is_file() {
        py_lines(&read_text(&ledger)?).into_iter().filter(|ln| ln.starts_with("| ") && ln.contains(&format!("| {check} |")) && ln.contains(name)).map(str::to_owned).collect()
    } else {
        Vec::new()
    };
    let dispo = git_dir.join("review-dispositions").join(format!("{subject}.json"));
    if dispo.is_file() {
        std::fs::copy(&dispo, out.join("dispositions.json")).map_err(fail)?;
    }
    let mut measured: Vec<PathBuf> = std::fs::read_dir(root.join("specs")).into_iter().flatten().flatten().map(|e| e.path().join("measurements.json")).filter(|p| p.is_file()).collect();
    sort_paths(&mut measured);
    let verifies: Vec<String> = measured
        .iter()
        .flat_map(|m| object(m).into_iter().collect::<Vec<_>>())
        .filter(|(_, v)| v.is_object() && v.get("subject").and_then(Value::as_str) == Some(subject) && truthy(v.get("verifies")))
        .map(|(k, v)| format!("- `{k}` verifies {}: {}", field(&v, "verifies", "None"), field(&v, "method", "")))
        .collect();
    #[expect(clippy::cast_possible_wrap, reason = "an epoch")]
    let since = std::fs::metadata(&rec).and_then(|m| m.modified()).ok().and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok()).map_or(0, |d| d.as_secs() as i64);
    let mut sheet: Vec<String> = Vec::new();
    for tree in std::fs::read_dir(root.join("pool")).into_iter().flatten().flatten() {
        let p = tree.path().join(name);
        if p.is_dir() {
            sheet.push(relative(&p, root));
        }
    }
    let edits = if sheet.is_empty() {
        String::new()
    } else {
        let at = format!("--since=@{since}");
        let mut args = vec!["log", at.as_str(), "-p", "--format=--- %h %ad %s", "--date=iso", "--"];
        args.extend(sheet.iter().map(String::as_str));
        g(root, &args)
    };
    write(&out.join("edits-since-verdict.diff"), if edits.is_empty() { "(no commit on the sheet since the verdict)\n" } else { &edits })?;
    let rows = if rows.is_empty() { "- (no ledger row names it)".to_owned() } else { rows.join("\n") };
    let verifies = if verifies.is_empty() { "- (no measurement verifies a finding)".to_owned() } else { verifies.join("\n") };
    Ok(vec![
        "## The earlier rounds (from the verdict record and the ledger; the check state kept none)\n".to_owned(),
        format!("`earlier-verdict.json` beside this file is the unit's last verdict record. Its ledger rows:\n\n{rows}\n"),
        "## What was done about the last round\n".to_owned(),
        format!("Each finding's disposition: `dispositions.json` (the review-accept rows, where there are any) and the measurements that verify a finding:\n\n{verifies}\n\nThe sheet's edits since the verdict: `edits-since-verdict.diff`.\n"),
    ])
}

/// Where the feature's `request.md` and `spec.md` may be: the active feature, then the feature a trigger names by number.
fn feature_dirs(root: &Path, d: Option<&Path>, trigger: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = d.map(Path::to_path_buf).into_iter().collect();
    if let Some(c) = FEATURE_NUMBER.captures(trigger).ok().flatten() {
        let prefix = format!("{}-", &c[1]);
        let mut named: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
            .into_iter()
            .flatten()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix) && e.path().is_dir())
            .map(|e| e.path())
            .collect();
        sort_paths(&mut named);
        out.extend(named);
    }
    let mut seen: Vec<PathBuf> = Vec::new();
    for p in out {
        if !seen.contains(&p) && p.is_dir() {
            seen.push(p);
        }
    }
    seen
}

fn under(p: &Path, root: &Path) -> String {
    if p.starts_with(root) { relative(p, root) } else { shown(p) }
}

/// Copy the feature's `request.md` and `spec.md` beside the MANIFEST and name ONLY the ones copied (`ask:f335-garden-modal-depiction`).
pub(crate) fn feature_section(root: &Path, out: &Path, d: Option<&Path>, trigger: &str) -> Result<String, Fail> {
    let dirs = feature_dirs(root, d, trigger);
    let (mut copied, mut missing) = (Vec::new(), Vec::new());
    for (name, what) in [("request.md", "the GM's words"), ("spec.md", "the spec")] {
        let Some(src) = dirs.iter().map(|p| p.join(name)).find(|p| p.is_file()) else {
            missing.push(name);
            continue;
        };
        std::fs::copy(&src, out.join(name)).map_err(fail)?;
        copied.push(format!("`{name}` ({what}, from {})", under(src.parent().unwrap_or(root), root)));
    }
    let mut text = "## The feature\n\n".to_owned();
    if !copied.is_empty() {
        text += &format!("Beside this file: {}.\n", copied.join("; "));
    }
    if !missing.is_empty() {
        let looked = dirs.iter().map(|p| under(p, root)).collect::<Vec<_>>().join(", ");
        let looked = if looked.is_empty() { "no feature directory resolved".to_owned() } else { looked };
        text += &format!("NOT in this bundle: {} - found in none of: {looked}. Rule from the sections above.\n", missing.join(", "));
    }
    Ok(text)
}

#[cfg(test)]
mod tests;
