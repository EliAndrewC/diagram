//! The report: the features by state, grouped by stage or by tag, an open feature a session clone holds differently shown as the clone
//! holds it (feature 375 amendment 1, FR-016 - DISPLAY ONLY: `--holding`, `--closed-by-status`, `--check` and `make tick` never read a
//! clone), and feature 444's row followed by the work budget's standing record (feature 443 FR-007, plan D8). Ported from
//! `speckit-todo.py`'s `report`, `in_clones` and `budget_under_444` (feature 449 T118).

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use l7r_guard::shared::py_text::split;
use l7r_guard::shared::speckit::{
    feature, feature_dirs, features, py_name, py_parent, vocabulary, Feature, STAGES, STATES,
};

/// An ACTIVE clone's session wrote its event log (a line per tool call) within this many hours (feature 375 amendment 1, D22).
const ACTIVE_HOURS: f64 = 12.0;

/// One feature's line: name, title, its ticks while open, the tags, the clone it is read from, and `extra`.
fn line(f: &Feature, extra: &str) -> String {
    let mut parts = vec![f.name.clone(), f.title.clone()];
    if f.total > 0 && f.state != "closed" {
        parts.push(format!("{}/{}", f.ticked, f.total));
    }
    if f.no_spec {
        parts.push("(no spec.md)".to_owned());
    }
    if !f.affects.is_empty() && f.state != "closed" {
        parts.push(format!("[{}]", f.affects.join(", ")));
    }
    if !f.clone.is_empty() {
        parts.push(format!("[in {}, not landed]", f.clone));
    }
    if !extra.is_empty() {
        parts.push(extra.to_owned());
    }
    format!("  {}", parts.join("  "))
}

fn by_stage(group: &[&Feature], out: &mut Vec<String>) {
    for stage in STAGES.iter().copied().chain([""]) {
        let staged: Vec<&&Feature> = group.iter().filter(|f| f.owed == stage).collect();
        if staged.is_empty() {
            continue;
        }
        let named = if stage.is_empty() {
            "NO STAGE (make speckit-todo CHECK=1 says how to set it)"
        } else {
            stage
        };
        out.push(format!("  owed at {named} ({})", staged.len()));
        out.extend(staged.iter().map(|f| format!("  {}", line(f, ""))));
    }
}

fn by_affects(group: &[&Feature], tags: &[String], out: &mut Vec<String>) {
    for tag in tags.iter().map(String::as_str).chain([""]) {
        let tagged: Vec<&&Feature> = group
            .iter()
            .filter(|f| {
                if tag.is_empty() {
                    f.affects.is_empty()
                } else {
                    f.affects.iter().any(|a| a == tag)
                }
            })
            .collect();
        if tagged.is_empty() {
            continue;
        }
        let named = if tag.is_empty() {
            "NOTHING NAMED (make speckit-todo CHECK=1 says how to set it)"
        } else {
            tag
        };
        out.push(format!("  affects {named} ({})", tagged.len()));
        out.extend(tagged.iter().map(|f| format!("  {}", line(f, ""))));
    }
}

/// The features by state, grouped by stage or by tag; `only` keeps the features carrying any of those tags.
///
/// # Errors
/// A file the Python raised on.
pub fn report(
    root: &Path,
    show_closed: bool,
    group_by_tag: bool,
    only: &[String],
) -> Result<String, String> {
    let fs: Vec<Feature> = features(&root.join("specs"))?
        .into_iter()
        .filter(|f| only.is_empty() || f.affects.iter().any(|a| only.contains(a)))
        .collect();
    let held = in_clones(root, &fs)?;
    let fs: Vec<Feature> = fs
        .into_iter()
        .flat_map(|f| {
            held.iter()
                .find(|(n, _)| *n == f.name)
                .map_or_else(|| vec![f.clone()], |(_, rows)| rows.clone())
        })
        .collect();
    let tags: Vec<String> = vocabulary(root)?
        .stage
        .into_iter()
        .map(|(t, _)| t)
        .collect();
    let mut out: Vec<String> = if only.is_empty() {
        Vec::new()
    } else {
        vec![format!("affects {}", only.join(", ")), String::new()]
    };
    for state in STATES {
        let group: Vec<&Feature> = fs.iter().filter(|f| f.state == state).collect();
        out.push(format!("{} ({})", state.to_uppercase(), group.len()));
        if group_by_tag {
            by_affects(&group, &tags, &mut out);
        } else {
            by_stage(&group, &mut out);
        }
        out.push(String::new());
    }
    let closed: Vec<&Feature> = fs.iter().filter(|f| f.state == "closed").collect();
    if show_closed {
        out.push(format!("CLOSED ({})", closed.len()));
        out.extend(closed.iter().map(|f| line(f, &f.why)));
        out.push(String::new());
    }
    budget_under_444(&mut out, root)?;
    let n = |s: &str| fs.iter().filter(|f| f.state == s).count();
    let scope = if only.is_empty() {
        String::new()
    } else {
        format!(" (affects {})", only.join(", "))
    };
    out.push(format!(
        "open: {} filed, {} planned, {} in progress; closed: {}{scope}",
        n("filed"),
        n("planned"),
        n("in progress"),
        closed.len()
    ));
    Ok(out.join("\n") + "\n")
}

/// Feature 444's row followed, in place, by the work budget's standing record (feature 443 FR-007, plan D8).
fn budget_under_444(out: &mut Vec<String>, root: &Path) -> Result<(), String> {
    let Some(at) = out.iter().position(|l| {
        l.trim_start_matches(l7r_guard::shared::py_text::is_space)
            .starts_with("444-")
    }) else {
        return Ok(());
    };
    let view: Vec<String> = super::work_budget_view::lines(root)?
        .into_iter()
        .map(|l| format!("      {l}"))
        .collect();
    out.splice(at + 1..=at, view);
    Ok(())
}

/// The `.clones/` directory beside this tree: its parent when the tree is itself a session clone, else its own.
fn clones_dir(root: &Path) -> PathBuf {
    let parent = py_parent(root);
    if py_name(&parent) == ".clones" {
        parent
    } else {
        root.join(".clones")
    }
}

/// `Path.resolve()`: the real path of what exists, the rest joined as given.
fn resolve(path: &Path) -> PathBuf {
    std::fs::canonicalize(path).unwrap_or_else(|_| std::path::absolute(path).unwrap_or_default())
}

/// Has the clone's session written its event log (`.git/l7r-events/`) within [`ACTIVE_HOURS`]?
fn active(clone: &Path) -> bool {
    let newest = std::fs::read_dir(clone.join(".git/l7r-events"))
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .filter_map(|e| std::fs::metadata(e.path()).and_then(|m| m.modified()).ok())
        .map(|t| {
            t.duration_since(UNIX_EPOCH)
                .map_or(0.0, |d| d.as_secs_f64())
        })
        .fold(0.0, f64::max);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64());
    now - newest < ACTIVE_HOURS * 3600.0
}

/// The feature directories under `specs/` with work in the clone that its main does not hold: committed past `origin/main` or not yet
/// committed. A clone BEHIND main differs from it too, and is not shown (the first run listed two abandoned clones' older copies).
fn unlanded(clone: &Path) -> Vec<String> {
    let names = |args: &[&str]| -> Vec<String> {
        let text = Command::new("git")
            .arg("-C")
            .arg(clone)
            .args(args)
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
            .unwrap_or_default();
        split(&text)
            .into_iter()
            .filter(|p| p.starts_with("specs/") && p.matches('/').count() >= 2)
            .filter_map(|p| p.split('/').nth(1).map(str::to_owned))
            .collect()
    };
    let mut got = names(&["diff", "--name-only", "origin/main...HEAD", "--", "specs"]);
    got.extend(names(&["diff", "--name-only", "HEAD", "--", "specs"]));
    got
}

/// {feature name: its state as each session clone holds it, where that differs from this tree's} for every open feature; a clone's row
/// carries its clone's name.
fn in_clones(root: &Path, fs: &[Feature]) -> Result<Vec<(String, Vec<Feature>)>, String> {
    let cdir = clones_dir(root);
    let here = resolve(root);
    // only the clones whose session is active (measured: ~0.14 s against ~0.9 s for every clone, the same rows,
    // m:375-a1-speckit-todo-clones)
    let clones: Vec<PathBuf> = feature_dirs(&cdir)
        .into_iter()
        .filter(|c| resolve(c) != here && active(c))
        .collect();
    let vocab = vocabulary(root)?;
    let work: Vec<Vec<String>> = clones.iter().map(|c| unlanded(c)).collect();
    let mut out: Vec<(String, Vec<Feature>)> = Vec::new();
    for f in fs {
        for (c, work) in clones.iter().zip(&work) {
            let there = c.join("specs").join(&f.name);
            if !work.contains(&f.name) || !there.is_dir() {
                continue;
            }
            let cf = feature(&there, &vocab)?;
            if f.state == "closed" && cf.state == "closed" {
                continue; // closed on main and in the clone: nothing open to show
            }
            // a feature closed on main and REOPENED in the clone (an amendment in progress) is shown too (the plan review); one
            // closed in the clone but not landed is still open on main: shown IN PROGRESS, marked done there
            let done_there = cf.state == "closed";
            let row = Feature {
                state: if done_there {
                    "in progress".to_owned()
                } else {
                    cf.state.clone()
                },
                clone: py_name(c) + if done_there { " (done there)" } else { "" },
                ..cf
            };
            match out.iter_mut().find(|(n, _)| *n == f.name) {
                Some((_, rows)) => rows.push(row),
                None => out.push((f.name.clone(), vec![row])),
            }
        }
    }
    Ok(out)
}
