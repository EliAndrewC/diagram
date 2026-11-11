//! The rounds of a review and the feature's own files, for the arbiter's bundle (from `arbiter_bundle.py`): a plan review's rounds (ask:t14-plan-round4), a spec review's from the subagent transcripts (387's ruling), a review unit's verdict record (feature 374 batch 4), and the feature's `request.md` and `spec.md` (`ask:f335-garden-modal-depiction`).

use std::collections::HashSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::reply;
use l7r_guard::shared::py_text::strip;
use serde_json::{json, Map, Value};

use super::marks::{mark_rounds, transcripts};
use super::sections::{field, g, json_file, text, truthy};
use crate::record::bundle::{hit, py_str, pyre, relative, shown, sort_paths, write};
use crate::record::py_lines;
use crate::record::repo::{fail, read_text, Fail};

static SPEC_ROUND: LazyLock<Regex> = LazyLock::new(|| pyre(r"MODE (?:2|3)\b|SPECIFICATION REVIEW"));
static VERDICT: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"[Vv]erdict\W{0,6}(FAITHFUL|CHANGES REQUIRED|NOT FAITHFUL|BLOCKED|CLEAR)")
});
static REVIEWS: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r"(?:^MODE 3 \(VERIFY\) - round \d+ of (?:feature |specs/)|specs/)(\d+-[a-z0-9][a-z0-9-]*?)(?=[/,\s.']|$)",
    )
});
static FEATURE_NUMBER: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"(?:^|[^a-z0-9])f(\d{3})(?:[^0-9]|$)"));

/// A JSON file's object, or {} where it does not parse.
fn object(path: &Path) -> Map<String, Value> {
    json_file(path)
        .ok()
        .and_then(|v| v.as_object().cloned())
        .unwrap_or_default()
}

/// An ask about a plan review carries that review's rounds (ask:t14-plan-round4): (lines, the plan's path).
pub fn plan_rounds(d: &Path) -> (Vec<String>, PathBuf) {
    let review = object(&d.join("plan-review.json"));
    let rounds: Vec<&Value> = review
        .get("block_reviews")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter(|r| r.is_object())
        .collect();
    let plan = d.join("plan.md");
    let Some(last) = rounds.last() else {
        return (
            vec![
                "## The plan review's rounds\n\n- (none recorded in plan-review.json)\n".to_owned(),
            ],
            plan,
        );
    };
    let blocks = |r: &Value| -> HashSet<String> {
        r.get("blocks")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .map(py_str)
            .collect()
    };
    let subject = blocks(last);
    let mut rows = Vec::new();
    for (i, r) in rounds
        .iter()
        .filter(|r| !subject.is_disjoint(&blocks(r)))
        .enumerate()
    {
        rows.push(format!(
            "### Round {}: {} ({})\n",
            i + 1,
            field(r, "verdict", "?"),
            field(r, "reviewed", "?")
        ));
        let found: Vec<String> = r
            .get("decisions")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter(|x| x.is_object() && x.get("class").and_then(Value::as_str) != Some("within"))
            .map(|x| {
                let s = format!(
                    "- {} - {}: {} {}",
                    field(x, "id", "?"),
                    field(x, "class", "?"),
                    field(x, "summary", ""),
                    field(x, "why", "")
                );
                s.trim_end_matches(l7r_guard::shared::py_text::is_space)
                    .to_owned()
            })
            .collect();
        if found.is_empty() {
            rows.push("- every decision within".to_owned());
        } else {
            rows.extend(found);
        }
        rows.push(String::new());
    }
    (
        vec![format!(
            "## The plan review's rounds (the blocks of the newest round)\n\n{}\n",
            rows.join("\n")
        )],
        plan,
    )
}

/// The text a subagent was dispatched with: its transcript's first record.
///
/// Its first line only (feature 449 T99): the whole file was read for it, every subagent transcript on the machine - 8,696 files, 8.0 GB
/// (2026-11-11) - so one spec round's bundle took 7.6 s, and the arbiter crate's tests with it.
fn first_prompt(transcript: &Path) -> String {
    let Ok(file) = std::fs::File::open(transcript) else {
        return String::new();
    };
    let mut bytes = Vec::new();
    let _ = std::io::BufRead::read_until(&mut std::io::BufReader::new(file), b'\n', &mut bytes);
    let line = String::from_utf8_lossy(&bytes);
    let line = line.as_ref();
    let first: Value = if line.is_empty() {
        json!({})
    } else {
        match serde_json::from_str(line) {
            Ok(v) => v,
            Err(_) => return String::new(),
        }
    };
    let content = first
        .get("message")
        .filter(|m| truthy(Some(m)))
        .and_then(|m| m.get("content"));
    match content {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Array(items)) => items
            .iter()
            .filter(|b| b.is_object())
            .map(|b| text(b, "text"))
            .collect(),
        _ => String::new(),
    }
}

/// The feature a review's dispatch REVIEWS (413-money-tooltip-on-the-record#1@6).
fn reviewed_feature(prompt: &str) -> String {
    let p = prompt.trim_start_matches(l7r_guard::shared::py_text::is_space);
    REVIEWS
        .captures(p)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// A spec review's rounds, each reviewer's whole reply beside the MANIFEST and its findings marked (387's ruling).
pub fn spec_rounds(out: &Path, subject: &str) -> Result<Vec<String>, Fail> {
    spec_rounds_in(&transcripts(), out, subject)
}

/// [`spec_rounds`] over the transcripts under `base`.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the transcript names Claude Code writes, as the Python's glob matched them"
)]
fn spec_rounds_in(base: &Path, out: &Path, subject: &str) -> Result<Vec<String>, Fail> {
    let mut found: Vec<(std::time::SystemTime, PathBuf)> = Vec::new();
    let mut all: Vec<PathBuf> = Vec::new();
    for a in std::fs::read_dir(base).into_iter().flatten().flatten() {
        for b in std::fs::read_dir(a.path()).into_iter().flatten().flatten() {
            for f in std::fs::read_dir(b.path().join("subagents"))
                .into_iter()
                .flatten()
                .flatten()
            {
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
        if reviewed_feature(&prompt) == subject
            && hit(&SPEC_ROUND, &prompt)
            && !prompt.contains("MODE 4")
        {
            found.push((
                std::fs::metadata(&f)
                    .and_then(|m| m.modified())
                    .map_err(fail)?,
                f,
            ));
        }
    }
    if found.is_empty() {
        return Ok(vec!["- (no spec review dispatch found in the subagent transcripts - read the Review history)\n".to_owned()]);
    }
    found.sort_by(|a, b| {
        a.0.cmp(&b.0)
            .then_with(|| a.1.components().cmp(b.1.components()))
    });
    let replies: Vec<String> = found
        .iter()
        .map(|(_, f)| reply::reply_of(&f.to_string_lossy(), ""))
        .collect();
    let mut lines = Vec::new();
    for (i, (r, marked)) in replies.iter().zip(mark_rounds(&replies, &[])).enumerate() {
        let i = i + 1;
        let verdict = if r.is_empty() {
            "no reply (stopped)".to_owned()
        } else {
            VERDICT
                .captures(r)
                .ok()
                .flatten()
                .map_or_else(|| "no verdict".to_owned(), |c| c[1].to_owned())
        };
        lines.push(format!("### Round {i}: spec-fidelity ({verdict})\n"));
        if !r.is_empty() {
            write(&out.join(format!("round-{i}-spec-fidelity.md")), r)?;
            lines.push(format!(
                "The whole reply: `round-{i}-spec-fidelity.md` beside this file."
            ));
        }
        if marked.is_empty() {
            lines.push(
                if r.is_empty() {
                    "- (no reply)"
                } else {
                    "- (no findings it numbers or bullets - read the whole reply)"
                }
                .to_owned(),
            );
        } else {
            lines.extend(marked.iter().map(|(m, f)| format!("- {m}: {f}")));
        }
        lines.push(String::new());
    }
    Ok(vec![lines.join("\n") + "\n"])
}

/// The review ledger's rows of `check` that name `name`.
fn ledger_rows(root: &Path, check: &str, name: &str) -> Result<Vec<String>, Fail> {
    let ledger = root.join("dev").join("review-ledger.md");
    if !ledger.is_file() {
        return Ok(Vec::new());
    }
    let mark = format!("| {check} |");
    Ok(py_lines(&read_text(&ledger)?)
        .into_iter()
        .filter(|ln| ln.starts_with("| ") && ln.contains(&mark) && ln.contains(name))
        .map(str::to_owned)
        .collect())
}

/// The measurements that verify a finding of `subject`, from every feature's `measurements.json`.
fn verifying(root: &Path, subject: &str) -> Vec<String> {
    let mut measured: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path().join("measurements.json"))
        .filter(|p| p.is_file())
        .collect();
    sort_paths(&mut measured);
    measured
        .iter()
        .flat_map(|m| object(m).into_iter().collect::<Vec<_>>())
        .filter(|(_, v)| {
            v.is_object()
                && v.get("subject").and_then(Value::as_str) == Some(subject)
                && truthy(v.get("verifies"))
        })
        .map(|(k, v)| {
            format!(
                "- `{k}` verifies {}: {}",
                field(&v, "verifies", "None"),
                field(&v, "method", "")
            )
        })
        .collect()
}

/// The commits on the unit's sheet since its verdict was written, as `edits-since-verdict.diff`.
fn sheet_edits(root: &Path, out: &Path, rec: &Path, name: &str) -> Result<(), Fail> {
    #[expect(clippy::cast_possible_wrap, reason = "an epoch")]
    let since = std::fs::metadata(rec)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map_or(0, |d| d.as_secs() as i64);
    let sheet: Vec<String> = std::fs::read_dir(root.join("pool"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|t| t.path().join(name))
        .filter(|p| p.is_dir())
        .map(|p| relative(&p, root))
        .collect();
    let edits = if sheet.is_empty() {
        String::new()
    } else {
        let at = format!("--since=@{since}");
        let mut args = vec![
            "log",
            at.as_str(),
            "-p",
            "--format=--- %h %ad %s",
            "--date=iso",
            "--",
        ];
        args.extend(sheet.iter().map(String::as_str));
        g(root, &args)
    };
    write(
        &out.join("edits-since-verdict.diff"),
        if edits.is_empty() {
            "(no commit on the sheet since the verdict)\n"
        } else {
            &edits
        },
    )
}

/// A review unit's earlier rounds from its verdict record and its ledger rows, where the check state holds none (feature 374 batch 4).
pub fn review_verdicts(root: &Path, out: &Path, subject: &str) -> Result<Vec<String>, Fail> {
    let git_dir = strip(&g(root, &["rev-parse", "--absolute-git-dir"])).to_owned();
    let git_dir = if git_dir.is_empty() {
        root.join(".git")
    } else {
        PathBuf::from(git_dir)
    };
    let rec = git_dir
        .join("review-verdicts")
        .join(format!("{subject}.json"));
    if subject.is_empty() || !rec.is_file() {
        return Ok(Vec::new());
    }
    std::fs::copy(&rec, out.join("earlier-verdict.json")).map_err(fail)?;
    let (check, name) = (
        subject.split("--").next().unwrap_or(subject),
        subject.split_once("--").map_or(subject, |p| p.1),
    );
    let rows = ledger_rows(root, check, name)?;
    let dispo = git_dir
        .join("review-dispositions")
        .join(format!("{subject}.json"));
    if dispo.is_file() {
        std::fs::copy(&dispo, out.join("dispositions.json")).map_err(fail)?;
    }
    let verifies = verifying(root, subject);
    sheet_edits(root, out, &rec, name)?;
    let rows = if rows.is_empty() {
        "- (no ledger row names it)".to_owned()
    } else {
        rows.join("\n")
    };
    let verifies = if verifies.is_empty() {
        "- (no measurement verifies a finding)".to_owned()
    } else {
        verifies.join("\n")
    };
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
    if p.starts_with(root) {
        relative(p, root)
    } else {
        shown(p)
    }
}

/// Copy the feature's `request.md` and `spec.md` beside the MANIFEST and name ONLY the ones copied (`ask:f335-garden-modal-depiction`).
pub fn feature_section(
    root: &Path,
    out: &Path,
    d: Option<&Path>,
    trigger: &str,
) -> Result<String, Fail> {
    let dirs = feature_dirs(root, d, trigger);
    let (mut copied, mut missing) = (Vec::new(), Vec::new());
    for (name, what) in [("request.md", "the GM's words"), ("spec.md", "the spec")] {
        let Some(src) = dirs.iter().map(|p| p.join(name)).find(|p| p.is_file()) else {
            missing.push(name);
            continue;
        };
        std::fs::copy(&src, out.join(name)).map_err(fail)?;
        copied.push(format!(
            "`{name}` ({what}, from {})",
            under(src.parent().unwrap_or(root), root)
        ));
    }
    let mut text = "## The feature\n\n".to_owned();
    if !copied.is_empty() {
        let _ = writeln!(text, "Beside this file: {}.", copied.join("; "));
    }
    if !missing.is_empty() {
        let looked = dirs
            .iter()
            .map(|p| under(p, root))
            .collect::<Vec<_>>()
            .join(", ");
        let looked = if looked.is_empty() {
            "no feature directory resolved".to_owned()
        } else {
            looked
        };
        let _ = writeln!(
            text,
            "NOT in this bundle: {} - found in none of: {looked}. Rule from the sections above.",
            missing.join(", ")
        );
    }
    Ok(text)
}

#[cfg(test)]
mod tests;
