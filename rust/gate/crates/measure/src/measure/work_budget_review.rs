//! `make work-budget-review` - the push's ratchet on the work budget (feature 443 FR-006, plan D7; feature 444 FR-022; feature 449
//! T224, which replaced the recipe that printed "suspended ... T42" and passed every push while six stages stood accepted).
//!
//! On a push carrying engine code (the GATED routes), every ACCEPTED hamlet stage is held at 40 and 80 households (a form's own
//! `sizes` where it has them, the polder's 10 and 20) to its accepted figure and to twice its budget (FR-022 rule 1: an accepted figure
//! is at most twice the budget, and LEEWAY carries nothing past that); every pool-sheet stage of Mode A (`sheet_stages`, T201) - none
//! accepted, as acceptance of a pool-sheet stage is not built (`budget_change/sheets.rs`) - is held on each sheet to twice its budget,
//! the line its phase landed under (T202, T152). A stage the counting runs do not reach is printed as such, never passed in silence: a
//! stage on `NOT_ON_REFERENCE` with its reason, a pool-sheet stage with no counter (`SHEET_COUNTERS`) as UNCOUNTED, and an accepted
//! stage missing from a run that should hold it refuses. No round-arbiter accept clears a refusal; the GM's words do.
//!
//! The counts are re-counted only when what they read moved (the GM's push cost, T224): each counting run is keyed on its crate's
//! sources, the workspace manifests and the inputs it reads (`delta::worktree_key`), its output kept under the git directory; a push
//! whose engine delta touches neither keeps both. Growth (FR-022 rule 3) is the MODE AUDIT's to judge at acceptance, not this ratchet's:
//! the deleted Python review held the two figures above and no exponent, and a stage's growth is bounded here by its held sizes.
//!
//! Research: plumbing - NONE: holds counted work against the budgets the work-budget agent judged

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

use super::commas;
use super::work_budget::{budget_at, parse};
use crate::codeid::common_git_dir;
use l7r_gate_tree::delta::worktree_key;

/// The sizes an accepted stage is held at, where its entry names none (443 FR-006).
///
/// Research: plumbing - NONE: the sizes the feature's rule names
const HELD: [i64; 2] = [40, 80];

/// An accepted figure may stand at up to twice its budget and no further (444 FR-022 rule 1, the GM 2026-11-03: "I would frankly be
/// okay with things that are 50% higher or even twice as high").
///
/// Research: plumbing - NONE: the GM's band for an estimate's leeway
const LEEWAY: f64 = 2.0;

/// Accepted stages the reference roll never runs, each with why (checked against the run: a stage named here that the run DOES count
/// is held like any other).
const NOT_ON_REFERENCE: [(&str, &str); 1] = [(
    "waterward",
    "the reference roll is a comb with a pond, where no waterward runs (accepted at 0); its one form that runs, the polder's, is held as waterward.polder",
)];

/// The pool-sheet stages a counting command reaches, and the command (`l7r-mode-a`'s counting build). A counter in a crate outside
/// `MODE_A_READS` extends those reads, or its counts are kept past a change to its code.
const SHEET_COUNTERS: [(&str, &str); 2] = [
    ("placer", "caption-counts"),
    ("compound", "compound-counts"),
];

/// What the hamlet driver's counts read: its crate and the workspace's manifests.
const HAMLET_READS: [&str; 3] = ["rust/phases/", "rust/Cargo.toml", "rust/Cargo.lock"];

/// What `l7r-mode-a`'s counts read: its crate, the crates it builds on by path, the manifests, the pool sheets and the building types.
const MODE_A_READS: [&str; 9] = [
    "rust/mode_a/",
    "rust/gate/crates/core/",
    "rust/gate/crates/registry/",
    "rust/gate/crates/research/",
    "rust/guard/",
    "rust/Cargo.toml",
    "rust/Cargo.lock",
    "pool/",
    "l7r/diagram/buildings/",
];

/// Bumped when what a kept count holds changes, so an older one is never read as this one.
const KEPT_FORM: &str = "1";

/// A counting run's kept output, or a fresh run's when its key moved: (the output, whether it was kept). The key is what the run reads
/// and `asked`, what it is asked to count - a sheet or a counted stage added to the table re-counts, where a key of the code alone
/// read the old output, which lacks it.
fn kept_or_run(
    root: &Path,
    group: &str,
    reads: &[&str],
    asked: &str,
    count: impl FnOnce() -> Result<String, String>,
) -> Result<(String, bool), String> {
    // a `.py` under the reads (a pool `.gen.py`) is read by no counting run, and keying it would start Python
    let key = worktree_key(root, "python3", reads, &|p| {
        Path::new(p).extension().is_none_or(|e| e != "py")
    })?;
    let dir = common_git_dir(root)
        .ok_or("work-budget-review: no git directory to keep the counts in")?
        .join("work-budget-review");
    let key = l7r_guard::shared::sha256::hex(format!("{KEPT_FORM}\0{key}\0{asked}").as_bytes());
    let file = dir.join(format!("{group}-{}.txt", &key[..16]));
    if let Ok(text) = std::fs::read_to_string(&file) {
        return Ok((text, true));
    }
    let text = count()?;
    let _ = std::fs::create_dir_all(&dir);
    // one kept output a group: the older keys go
    for old in std::fs::read_dir(&dir).into_iter().flatten().flatten() {
        if old
            .file_name()
            .to_string_lossy()
            .starts_with(&format!("{group}-"))
        {
            let _ = std::fs::remove_file(old.path());
        }
    }
    // a count that cannot be kept is counted again next time, never a refusal
    let _ = std::fs::write(&file, &text);
    Ok((text, false))
}

/// One counting run through the wrapper: `l7r-gate.sh rust hamlet --crate <crate>` with the counters on.
fn wrapped(root: &Path, krate: &str, args: &str, envs: &[(&str, &str)]) -> Result<String, String> {
    let done = Command::new(root.join("scripts/gates/l7r-gate.sh"))
        .args(["rust", "hamlet", "--crate"])
        .arg(root.join(krate))
        .env("HAMLET_ARGS", args)
        .env("HAMLET_FEATURES", "counters")
        .envs(envs.iter().copied())
        .current_dir(root)
        .output()
        .map_err(|e| format!("work-budget-review: the counting run `{args}` did not start: {e}"))?;
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    if done.status.success() {
        Ok(stdout)
    } else {
        Err(format!(
            "work-budget-review: the counting run `{args}` on {krate} failed - fix what it names, then push again:\n{stdout}{}",
            String::from_utf8_lossy(&done.stderr)
        ))
    }
}

/// The hamlet driver's two budget runs, the reference comb's and the polder's.
fn hamlet_counts(root: &Path) -> Result<String, String> {
    let comb = wrapped(root, "rust/phases", "--budget", &[])?;
    let polder = wrapped(root, "rust/phases", "--budget polder", &[])?;
    let both = comb + &polder;
    // read before it is kept, so a run that printed nonsense is never kept as this code's counts
    parse(&both)?;
    Ok(both)
}

/// The file a sheet is counted from: its program where it is generated, else its hand-drawn svg; None where the pool holds neither.
fn sheet_source(root: &Path, sheet: &str) -> Option<String> {
    let mut tiers: Vec<PathBuf> = std::fs::read_dir(root.join("pool"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    tiers.sort();
    [".compound.json", ".svg"].iter().find_map(|end| {
        tiers.iter().find_map(|tier| {
            let file = tier.join(sheet).join(format!("{sheet}{end}"));
            file.is_file().then(|| {
                file.strip_prefix(root)
                    .unwrap_or(&file)
                    .to_string_lossy()
                    .into_owned()
            })
        })
    })
}

/// What the sheet counts are asked for: each counted stage's command and sheets.
fn asked_sheets(sheets: &Value) -> String {
    SHEET_COUNTERS
        .iter()
        .map(|(stage, command)| {
            let named: Vec<&str> = sheets
                .get(stage)
                .and_then(|s| s.get("sheets"))
                .and_then(Value::as_object)
                .map(|m| m.keys().map(String::as_str).collect())
                .unwrap_or_default();
            format!("{stage} {command} {}", named.join(" "))
        })
        .collect::<Vec<_>>()
        .join("\n")
}

/// Each counted pool-sheet stage's total on each of its sheets, one `stage sheet total` line each; a sheet with no source is
/// `stage sheet -`.
fn sheet_counts(root: &Path, sheets: &Value) -> Result<String, String> {
    let mut out = String::new();
    for (stage, command) in SHEET_COUNTERS {
        let Some(Value::Object(by_sheet)) = sheets.get(stage).and_then(|s| s.get("sheets")) else {
            continue;
        };
        for sheet in by_sheet.keys() {
            let Some(source) = sheet_source(root, sheet) else {
                let _ = writeln!(out, "{stage}\t{sheet}\t-");
                continue;
            };
            let said = wrapped(
                root,
                "rust/mode_a",
                &format!("{command} {source}"),
                &[("HAMLET_BIN", "l7r-mode-a"), ("HAMLET_DEV", "1")],
            )?;
            // the report is the one JSON line; the wrapper adds its own `rust-checks:` line after it
            let total = said
                .lines()
                .find_map(|l| {
                    serde_json::from_str::<Value>(l)
                        .ok()?
                        .get("total")?
                        .as_i64()
                })
                .ok_or_else(|| {
                    format!(
                        "work-budget-review: `l7r-mode-a {command} {source}` printed no total:\n{}",
                        said.chars().take(400).collect::<String>()
                    )
                })?;
            let _ = writeln!(out, "{stage}\t{sheet}\t{total}");
        }
    }
    Ok(out)
}

/// What the review found: the lines it prints, and the refusals.
#[derive(Default)]
struct Held {
    lines: Vec<String>,
    refused: Vec<String>,
}

/// Each accepted hamlet stage against the counts.
#[expect(
    clippy::cast_precision_loss,
    reason = "counted operations, far inside f64's exact range"
)]
fn hold_hamlet(stages: &Value, counts: &Means, held: &mut Held) {
    for (name, st) in stages.as_object().into_iter().flatten() {
        if st.get("status").and_then(Value::as_str) != Some("accepted") {
            continue;
        }
        let Some(per) = counts.get(name) else {
            if let Some((_, why)) = NOT_ON_REFERENCE.iter().find(|(n, _)| n == name) {
                held.lines.push(format!("  {name}: not counted - {why}"));
            } else {
                held.refused.push(format!(
                    "{name}: accepted, but no counting run counts it - a stage of the cut must be counted by `hamlet --budget` (or named in NOT_ON_REFERENCE, work_budget_review.rs, with why)"
                ));
            }
            continue;
        };
        let sizes: Vec<i64> = st.get("sizes").and_then(Value::as_array).map_or_else(
            || HELD.to_vec(),
            |a| a.iter().filter_map(Value::as_i64).collect(),
        );
        let mut cells = Vec::new();
        for h in sizes {
            let Some(&(ops, rolled)) = per.get(&h) else {
                held.refused.push(format!(
                    "{name}: the counting run rolled no {name} at {h} households to hold it to - a refused roll? (`make work-budget` shows the run)"
                ));
                continue;
            };
            let accepted = st
                .get("accepted")
                .and_then(|a| a.get(h.to_string()))
                .and_then(Value::as_f64);
            let budget = budget_at(st, h);
            let mut figures = Vec::new();
            if let Some(b) = budget {
                figures.push(format!("{} its budget {}", ratio(ops, b), whole(b)));
            }
            if let Some(a) = accepted {
                figures.push(format!("accepted {}", whole(a)));
                if ops as f64 > a {
                    held.refused.push(format!(
                        "{name}: {} counted operations at {h} households, over its accepted {}",
                        commas(ops),
                        whole(a)
                    ));
                }
            }
            if let Some(t) = budget.map(|b| LEEWAY * b) {
                if ops as f64 > t {
                    held.refused.push(format!("{name}: {} counted operations at {h} households, past twice its budget ({})", commas(ops), whole(t)));
                }
            }
            if figures.is_empty() {
                held.refused.push(format!("{name}: accepted with no accepted figure and no budget at {h} households to hold it to"));
            }
            // a refused roll prints nothing, so a size whose costly seeds stopped rolling reads cheaper: say how many rolled
            if rolled < SEEDS {
                figures.push(format!("{rolled} of {SEEDS} seeds rolled"));
            }
            cells.push(format!("{} at {h} ({})", commas(ops), figures.join("; ")));
        }
        held.lines.push(format!("  {name}: {}", cells.join("; ")));
    }
}

/// Each pool-sheet stage against its counts per sheet.
#[expect(
    clippy::cast_precision_loss,
    reason = "counted operations, far inside f64's exact range"
)]
fn hold_sheets(sheets: &Value, counted: &str, held: &mut Held) {
    let mut totals: BTreeMap<(&str, &str), Option<i64>> = BTreeMap::new();
    for line in counted.lines() {
        if let [stage, sheet, n] = line.split('\t').collect::<Vec<_>>()[..] {
            totals.insert((stage, sheet), n.parse().ok());
        }
    }
    for (stage, st) in sheets.as_object().into_iter().flatten() {
        let by_sheet = st.get("sheets").and_then(Value::as_object);
        if !SHEET_COUNTERS.iter().any(|(s, _)| s == stage) {
            held.lines.push(format!(
                "  UNCOUNTED {stage}: budgeted per sheet ({}), but nothing counts it - its code is not built or has no counter; the landing that builds it adds its counting command to SHEET_COUNTERS (work_budget_review.rs)",
                by_sheet.map_or(0, serde_json::Map::len)
            ));
            continue;
        }
        let mut cells = Vec::new();
        for (sheet, b) in by_sheet.into_iter().flatten() {
            let budget = b.get("budget").and_then(Value::as_f64).unwrap_or(0.0);
            let twice = LEEWAY * budget;
            match totals.get(&(stage.as_str(), sheet.as_str())) {
                Some(Some(ops)) => {
                    if *ops as f64 > twice {
                        held.refused.push(format!(
                            "{stage} on {sheet}: {} counted operations, past twice its budget ({})",
                            commas(*ops),
                            whole(twice)
                        ));
                    }
                    cells.push(format!(
                        "{sheet} {} ({} its budget {})",
                        commas(*ops),
                        ratio(*ops, budget),
                        whole(budget)
                    ));
                }
                _ => held.refused.push(format!(
                    "{stage} on {sheet}: no count - the pool holds no {sheet}.compound.json or {sheet}.svg to count it from (a sheet renamed? its budget in dev/work-budget.json names it)"
                )),
            }
        }
        held.lines.push(format!("  {stage}: {}", cells.join("; ")));
    }
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a budget's size, far inside i64"
)]
fn whole(x: f64) -> String {
    commas(x.round() as i64)
}

/// Each stage's (mean counted operations, seeds rolled) by size.
type Means = BTreeMap<String, BTreeMap<i64, (i64, i64)>>;

/// The seeds the driver's budget run rolls at each size (`hamlet --budget`: 4, 25, 39, 47).
const SEEDS: i64 = 4;

/// Each stage's mean counted operations by size, from the driver's lines.
fn means(text: &str) -> Result<Means, String> {
    let (counts, _) = parse(text)?;
    Ok(counts
        .into_iter()
        .map(|(stage, per)| (stage, per.into_iter().collect()))
        .collect())
}

/// `ops` as a multiple of `budget`, as `make work-budget`'s ratio column prints it.
#[expect(
    clippy::cast_precision_loss,
    reason = "counted operations, far inside f64's exact range"
)]
fn ratio(ops: i64, budget: f64) -> String {
    if budget > 0.0 {
        format!("{:.2}x", ops as f64 / budget)
    } else {
        "-".to_owned()
    }
}

fn review(route: &str, root: &Path) -> Result<(i32, String), String> {
    let file = root.join("dev/work-budget.json");
    let table: Value = std::fs::read_to_string(&file)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .ok_or_else(|| format!("work-budget-review: {} does not read", file.display()))?;
    let accepted = table["stages"]
        .as_object()
        .is_some_and(|s| s.values().any(|st| st["status"] == "accepted"));
    let sheets = table["sheet_stages"]
        .as_object()
        .is_some_and(|s| !s.is_empty());
    if !accepted && !sheets {
        return Ok((
            0,
            "work-budget-review: no stage is accepted or budgeted per sheet - nothing to hold\n"
                .to_owned(),
        ));
    }
    // a bare `make work-budget-review` (no ROUTE) holds, as a GATED push does: only the push's DIRECT route has nothing to hold
    if !route.is_empty() && route != "GATED" && route != "GATED-LOCAL" {
        return Ok((0, format!("work-budget-review: the push carries no engine code (route {route}) - nothing to hold\n")));
    }
    let mut held = Held::default();
    let mut how = Vec::new();
    if accepted {
        let (text, kept) = kept_or_run(
            root,
            "hamlet",
            &HAMLET_READS,
            "--budget, --budget polder",
            || hamlet_counts(root),
        )?;
        how.push(format!(
            "the hamlet stages {}",
            if kept {
                "kept (their code unmoved)"
            } else {
                "re-counted"
            }
        ));
        hold_hamlet(&table["stages"], &means(&text)?, &mut held);
    }
    if sheets {
        let asked = asked_sheets(&table["sheet_stages"]);
        let (text, kept) = kept_or_run(root, "mode-a", &MODE_A_READS, &asked, || {
            sheet_counts(root, &table["sheet_stages"])
        })?;
        how.push(format!(
            "the pool-sheet stages {}",
            if kept {
                "kept (their code and sheets unmoved)"
            } else {
                "re-counted"
            }
        ));
        hold_sheets(&table["sheet_stages"], &text, &mut held);
    }
    let body = held.lines.join("\n");
    if held.refused.is_empty() {
        return Ok((
            0,
            format!(
                "work-budget-review: every held stage within its figures ({}):\n{body}\n",
                how.join(", ")
            ),
        ));
    }
    let mut out = format!(
        "work-budget-review: REFUSED - a held stage is past its figure or cannot be held ({}):\n",
        how.join(", ")
    );
    for r in &held.refused {
        let _ = writeln!(out, "  {r}");
    }
    let _ = write!(
        out,
        "{body}\n  fix: make the stage do less work (`make work-budget` for a hamlet stage, `make budget-sheets PHASE=<stage> COUNTS=...` for a pool sheet show the counts), or raise its figure with the GM's own words: make budget-change PHASE=<stage> TO=<per thing> WORDS=\"<the GM's words>\" (a pool-sheet stage's change is not built yet - its counts above go to the GM); no round-arbiter accept clears this (feature 443 FR-006)\n"
    );
    Ok((1, out))
}

/// `l7r-gate measure work-budget-review <ROUTE>`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let route = args.first().map_or("", String::as_str);
    match review(route, root) {
        Ok((code, out)) => crate::Reply {
            stdout: if code == 0 {
                out.clone()
            } else {
                String::new()
            },
            stderr: if code == 0 { String::new() } else { out },
            code,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: why + "\n",
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
