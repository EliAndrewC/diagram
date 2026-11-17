//! The run (feature 449 T161): which sides of which cases rerun, the kept results, the report.
//!
//! THE STATE DIRECTORY, beside the cases file `<dir>/<stem>.json`, is `<dir>/<stem>.diff-run/`:
//! - `results/<case id>.old.json`, `results/<case id>.new.json`: each side's kept result and the key it ran under (a whole world's
//!   `.old.whole.json`, `.new.whole.json` where the file declares a sparse list, feature 449 T169);
//! - `reports/diff-run-<kind>-<UTC>.json`: one report a run, `<kind>` one of `incremental`, `only`, `twice`, `verify`, `all` - only a
//!   `--verify` run's path carries `diff-run-verify`, the path `make decide`'s lint asks a plan's differential count to cite;
//! - `work/old`, `work/new`: a side's world while it runs, removed after.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

use l7r_guard::shared::log::civil;
use serde_json::{json, Value};

use crate::cases::{Case, Cases, Worlds};
use crate::keys::{applying, keys, Hasher};
use crate::norm::{compare, kept, Kept};

/// What the command line asked for.
#[derive(Default)]
pub struct Opts {
    pub only: Option<String>,
    pub verify: bool,
    pub twice: bool,
    pub all: bool,
    pub reason: Option<String>,
}

impl Opts {
    /// The worlds the run builds (feature 449 T169): whole for a `--verify` or `--all` run - the record a plan cites - and wherever no
    /// sparse path list is declared; sparse for the runs that iterate.
    #[must_use]
    pub fn worlds(&self, cases: &Cases) -> Worlds {
        if self.verify || self.all || !cases.declares_sparse() {
            Worlds::Whole
        } else {
            Worlds::Sparse
        }
    }

    /// The run's kind, as the report and its path name it.
    #[must_use]
    pub fn kind(&self) -> &'static str {
        if self.all {
            "all"
        } else if self.verify {
            "verify"
        } else if self.twice {
            "twice"
        } else if self.only.is_some() {
            "only"
        } else {
            "incremental"
        }
    }
}

/// `YYYYMMDDTHHMMSSZ` now.
#[must_use]
pub fn stamp() -> String {
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}Z")
}

/// A case's file name in `results/`: its name made safe, and a short hash of the name so two names that read alike never share one.
#[must_use]
pub fn case_id(name: &str) -> String {
    let safe: String = name
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '-' {
                c
            } else {
                '_'
            }
        })
        .take(48)
        .collect();
    format!(
        "{safe}-{}",
        &l7r_guard::shared::sha256::hex(name.as_bytes())[..10]
    )
}

/// A side's kept result: `<case id>.<side>.json`, and `<case id>.<side>.whole.json` for a whole world's where the file declares a sparse
/// list (feature 449 T169), so a verify's old sides stand from one verify to the next while the sparse runs keep their own.
fn result_path(cases: &Cases, case: &Case, which: &str, worlds: Worlds) -> PathBuf {
    let whole = if worlds == Worlds::Whole && cases.declares_sparse() {
        ".whole"
    } else {
        ""
    };
    cases
        .state
        .join("results")
        .join(format!("{}.{which}{whole}.json", case_id(&case.name)))
}

/// The kept result of one side and the key it ran under, if any.
fn load(path: &Path) -> Option<(String, Kept)> {
    let v: Value = serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()?;
    Some((
        v["key"].as_str()?.to_owned(),
        Kept::from_json(&v["result"])?,
    ))
}

fn save(path: &Path, key: &str, case: &Case, k: &Kept) -> Result<(), String> {
    let text =
        json!({"key": key, "case": case.name, "utc": stamp(), "result": k.to_json()}).to_string();
    write(path, &(text + "\n"))
}

/// A file written, its directory made first.
fn write(path: &Path, text: &str) -> Result<(), String> {
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new(".")))
        .and_then(|()| std::fs::write(path, text))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// One side of one case: its kept result when its key stands and nothing forces it, else a fresh run, kept at once (an interrupted run
/// keeps what it finished).
struct SideRun {
    kept: Option<Kept>,
    rerun: bool,
    error: Option<String>,
}

fn one_side(
    cases: &Cases,
    case: &Case,
    (which, worlds): (&str, Worlds),
    key: &str,
    force: bool,
) -> SideRun {
    let path = result_path(cases, case, which, worlds);
    if !force {
        if let Some((was, k)) = load(&path) {
            if was == key {
                return SideRun {
                    kept: Some(k),
                    rerun: false,
                    error: None,
                };
            }
        }
    }
    match fresh(cases, case, which, worlds) {
        Ok(k) => match save(&path, key, case, &k) {
            Ok(()) => SideRun {
                kept: Some(k),
                rerun: true,
                error: None,
            },
            Err(e) => SideRun {
                kept: None,
                rerun: true,
                error: Some(e),
            },
        },
        Err(e) => SideRun {
            kept: None,
            rerun: true,
            error: Some(format!("{which} side: {e}")),
        },
    }
}

fn fresh(cases: &Cases, case: &Case, which: &str, worlds: Worlds) -> Result<Kept, String> {
    let side = if which == "old" {
        &cases.old
    } else {
        &cases.new
    };
    let world = cases.state.join("work").join(which);
    let raw = crate::run::side(cases, case, side, (which, worlds), &world)?;
    Ok(kept(&raw, &applying(cases, case), cases.max_text))
}

/// The report's path: `reports/diff-run-<kind>-<stamp>.json`, `-2` and on where a run of the same kind wrote one in the same second.
pub(crate) fn report_path(state: &Path, kind: &str, stamp: &str) -> PathBuf {
    let dir = state.join("reports");
    let base = format!("diff-run-{kind}-{stamp}");
    let mut path = dir.join(format!("{base}.json"));
    let mut n = 2;
    while path.exists() {
        path = dir.join(format!("{base}-{n}.json"));
        n += 1;
    }
    path
}

fn side_row(r: &SideRun, key: &str) -> Value {
    json!({"key": key, "rerun": r.rerun, "took_s": r.kept.as_ref().map(|k| k.took_s)})
}

/// One case run and compared: its report row, and whether it is the same on both sides with no run-to-run noise.
fn one_case(
    cases: &Cases,
    case: &Case,
    (old_key, new_key): &(String, String),
    opts: &Opts,
) -> (Value, bool) {
    let worlds = opts.worlds(cases);
    let old = one_side(
        cases,
        case,
        ("old", worlds),
        old_key,
        opts.all || opts.twice,
    );
    let mut noise = Vec::new();
    if opts.twice {
        if let Some(first) = &old.kept {
            match fresh(cases, case, "old", worlds) {
                Ok(second) => noise = compare(first, &second, "old run 1", "old run 2"),
                Err(e) => noise.push(format!("old side's second run: {e}")),
            }
        }
    }
    let new = one_side(
        cases,
        case,
        ("new", worlds),
        new_key,
        opts.all || opts.verify || opts.only.is_some(),
    );
    let (diffs, taken) = match (&old.kept, &new.kept) {
        (Some(a), Some(b)) => (
            compare(a, b, &cases.old.label, &cases.new.label),
            a.taken.union(&b.taken).cloned().collect::<Vec<_>>(),
        ),
        _ => (Vec::new(), Vec::new()),
    };
    let errors: Vec<&String> = [&old.error, &new.error].into_iter().flatten().collect();
    let same = errors.is_empty() && diffs.is_empty() && noise.is_empty();
    let row = json!({
        "name": case.name, "same": same, "diffs": diffs, "norms": taken, "noise": noise, "errors": errors,
        "old": side_row(&old, old_key), "new": side_row(&new, new_key),
    });
    (row, same)
}

fn secs(v: &Value) -> String {
    v["took_s"]
        .as_f64()
        .map_or_else(|| "-".to_owned(), |t| format!("{t:.1}s"))
}

fn line(row: &Value) -> String {
    let mark = if !row["errors"].as_array().is_none_or(Vec::is_empty) {
        "FAIL"
    } else if row["same"] == true {
        "SAME"
    } else {
        "DIFF"
    };
    let how = |s: &Value| if s["rerun"] == true { "rerun" } else { "kept" };
    let noise = row["noise"].as_array().map_or(0, Vec::len);
    format!(
        "{mark} old {:>7} {:5}  new {:>7} {:5}  {}{}",
        secs(&row["old"]),
        how(&row["old"]),
        secs(&row["new"]),
        how(&row["new"]),
        row["name"].as_str().unwrap_or_default(),
        if noise > 0 {
            format!("  noise: {noise}")
        } else {
            String::new()
        }
    )
}

/// The run: the report's JSON and its path, the printed summary, and whether every case was the same.
///
/// # Errors
///
/// What refuses the run before any case runs: an unknown `--only`, a declared path that does not exist, a failed build.
pub fn execute(
    cases: &Cases,
    opts: &Opts,
    progress: &mut dyn Write,
) -> Result<(PathBuf, String, bool), String> {
    let start = Instant::now();
    let todo: Vec<&Case> = match &opts.only {
        Some(name) => vec![cases
            .cases
            .iter()
            .find(|c| &c.name == name)
            .ok_or_else(|| {
                let names: Vec<&str> = cases.cases.iter().map(|c| c.name.as_str()).collect();
                format!(
                    "no case named {name:?}; the cases are: {}",
                    names.join(", ")
                )
            })?],
        None => cases.cases.iter().collect(),
    };
    // the builds first, then every key: a stale binary is made current before anything is keyed or run, and a declaration that names
    // nothing refuses the run before an hour of it, not after
    crate::run::build(cases, &cases.old, "old")?;
    crate::run::build(cases, &cases.new, "new")?;
    let mut h = Hasher::default();
    let all_keys: Vec<(String, String)> = todo
        .iter()
        .map(|c| keys(cases, c, &mut h, opts.worlds(cases)))
        .collect::<Result<_, _>>()?;
    let (mut rows, mut all_same) = (Vec::new(), true);
    let mut norms: BTreeMap<String, usize> = BTreeMap::new();
    let (mut rerun, mut kept_n) = (0, 0);
    for (case, k) in todo.iter().zip(&all_keys) {
        let (row, same) = one_case(cases, case, k, opts);
        all_same &= same;
        for side in ["old", "new"] {
            if row[side]["rerun"] == true {
                rerun += 1;
            } else {
                kept_n += 1;
            }
        }
        for n in row["norms"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            *norms.entry(n.to_owned()).or_default() += 1;
        }
        let _ = writeln!(progress, "{}", line(&row));
        rows.push(row);
    }
    let differing: Vec<&Value> = rows
        .iter()
        .filter(|r| r["same"] != true)
        .map(|r| &r["name"])
        .collect();
    let wall = (start.elapsed().as_secs_f64() * 10.0).round() / 10.0;
    let kind = opts.kind();
    let path = report_path(&cases.state, kind, &stamp());
    let worlds = if opts.worlds(cases) == Worlds::Whole {
        "whole"
    } else {
        "sparse"
    };
    let report = json!({
        "kind": kind, "only": opts.only, "twice": opts.twice, "reason": opts.reason, "cases_file": cases.file.display().to_string(),
        "utc": stamp(), "wall_s": wall, "cases_total": rows.len(), "sides_rerun": rerun, "sides_kept": kept_n,
        "differing": differing, "normalizations": norms, "worlds": worlds, "cases": rows,
    });
    write(
        &path,
        &(serde_json::to_string_pretty(&report).unwrap_or_default() + "\n"),
    )?;
    let mut shown = String::new();
    for row in rows.iter().filter(|r| r["same"] != true) {
        let _ = write!(shown, "\n{}\n", line(row));
        for d in row["errors"]
            .as_array()
            .into_iter()
            .chain(row["diffs"].as_array())
            .chain(row["noise"].as_array())
            .flatten()
        {
            let text: Vec<&str> = d.as_str().unwrap_or_default().lines().take(30).collect();
            let _ = writeln!(shown, "  {}", text.join("\n  "));
        }
    }
    let said = match (worlds, opts.verify || opts.all) {
        ("whole", true) => "whole, world.checkout.sparse ignored - a verify's figures are the record",
        ("whole", false) => "whole (no sparse path list declared)",
        _ => "sparse (world.checkout.sparse) - for iterating only; a plan cites a VERIFY=1 report, built on whole worlds",
    };
    let summary = format!(
        "{shown}diff-run ({kind}): {} cases, {} differing; sides rerun {rerun}, kept {kept_n}; {wall:.1} s\nnormalizations (cases taking each): {}\nworlds: {said}\nreport: {}\n",
        rows.len(),
        differing.len(),
        serde_json::to_string(&norms).unwrap_or_default(),
        path.display()
    );
    Ok((path, summary, all_same))
}
