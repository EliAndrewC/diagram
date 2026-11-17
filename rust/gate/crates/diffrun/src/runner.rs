//! The run (feature 449 T161): which sides of which cases rerun, the kept results, the report.
//!
//! THE STATE DIRECTORY, beside the cases file `<dir>/<stem>.json`, is `<dir>/<stem>.diff-run/`:
//! - `results/<case id>.old.json`, `results/<case id>.new.json`: each side's kept result and the key it ran under (a whole world's
//!   `.old.whole.json`, `.new.whole.json` where the file declares a sparse list, feature 449 T169);
//! - `reports/diff-run-<kind>-<UTC>.json`: one report a run, `<kind>` one of `incremental`, `only`, `twice`, `verify`, `all` - only a
//!   `--verify` run's path carries `diff-run-verify`, the path `make decide`'s lint asks a plan's differential count to cite;
//! - `work/old`, `work/new`: a side's world while it runs, removed after; on a run of several workers (`--jobs`), `work/old-<w>` and
//!   `work/new-<w>`, each worker's own.
//!
//! SEVERAL WORKERS (`--jobs N`, feature 449 T173): T170's verify run took 392.6 s wall for 105 cases whose sides' own commands summed to
//! 11.6 s - the rest a side's world (a whole checkout of 27,770 files, its setup, two snapshots, its removal), about 1.8 s a side, 210
//! sides one after another. The owed sides now run on N threads, each in its own world; the main thread alone keeps the record - it
//! builds each case's row and prints its line once that case and every case before it are done, so the report, the lines and their
//! order are a serial run's. A side's error names the world a serial run would have named, so no text depends on the worker.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
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
    /// The workers the owed sides run on (`--jobs`, feature 449 T173): 0 and 1 alike one, the run as it always was.
    pub jobs: usize,
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
#[derive(Default)]
struct SideRun {
    kept: Option<Kept>,
    rerun: bool,
    error: Option<String>,
}

/// One side's run, and for `--twice`'s old side the noise between its two runs.
#[derive(Default)]
struct Done {
    side: SideRun,
    noise: Vec<String>,
}

const SIDES: [&str; 2] = ["old", "new"];

/// Whether the run reruns `which` whatever its key: every side under `--all`, the old under `--twice`, the new under `--verify` and
/// `--only`.
fn forced(opts: &Opts, which: &str) -> bool {
    opts.all
        || if which == "old" {
            opts.twice
        } else {
            opts.verify || opts.only.is_some()
        }
}

/// The side's kept result where its key stands and nothing forces it; `None` where the side is owed a run.
fn standing(
    cases: &Cases,
    case: &Case,
    (which, worlds): (&str, Worlds),
    key: &str,
    force: bool,
) -> Option<SideRun> {
    if force {
        return None;
    }
    let (was, k) = load(&result_path(cases, case, which, worlds))?;
    (was == key).then_some(SideRun {
        kept: Some(k),
        rerun: false,
        error: None,
    })
}

/// One owed side run fresh in `world`, kept at once (an interrupted run keeps what it finished); `--twice`'s old side run again there
/// and the two compared.
fn rerun(
    cases: &Cases,
    case: &Case,
    (which, worlds): (&str, Worlds),
    key: &str,
    (twice, world): (bool, &Path),
) -> Done {
    let path = result_path(cases, case, which, worlds);
    let side = match fresh(cases, case, (which, worlds), world) {
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
    };
    let mut noise = Vec::new();
    if twice {
        if let Some(first) = &side.kept {
            match fresh(cases, case, (which, worlds), world) {
                Ok(second) => noise = compare(first, &second, "old run 1", "old run 2"),
                Err(e) => noise.push(format!("old side's second run: {e}")),
            }
        }
    }
    Done { side, noise }
}

/// The world a side runs in: `work/<which>` on a run of one worker, as always, and `work/<which>-<w>` for worker `w` of several, so no
/// two sides running at once share one (feature 449 T173).
fn world(cases: &Cases, which: &str, worker: Option<usize>) -> PathBuf {
    let name = worker.map_or_else(|| which.to_owned(), |w| format!("{which}-{w}"));
    cases.state.join("work").join(name)
}

fn fresh(
    cases: &Cases,
    case: &Case,
    (which, worlds): (&str, Worlds),
    at: &Path,
) -> Result<Kept, String> {
    let side = if which == "old" {
        &cases.old
    } else {
        &cases.new
    };
    // a worker's world named as a serial run names it, in the error alone (a kept result already reads `<WORLD>`), so a side's error
    // is the same text whatever worker ran it (feature 449 T173)
    let raw = crate::run::side(cases, case, side, (which, worlds), at).map_err(|e| {
        e.replace(
            &at.display().to_string(),
            &world(cases, which, None).display().to_string(),
        )
    })?;
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

/// One case's two sides compared: its report row, `same` where both sides agree with no run-to-run noise.
fn one_case(
    cases: &Cases,
    case: &Case,
    (old_key, new_key): &(String, String),
    [old, new]: [Done; 2],
) -> Value {
    let (noise, old, new) = (old.noise, old.side, new.side);
    let (diffs, taken) = match (&old.kept, &new.kept) {
        (Some(a), Some(b)) => (
            compare(a, b, &cases.old.label, &cases.new.label),
            a.taken.union(&b.taken).cloned().collect::<Vec<_>>(),
        ),
        _ => (Vec::new(), Vec::new()),
    };
    let errors: Vec<&String> = [&old.error, &new.error].into_iter().flatten().collect();
    let same = errors.is_empty() && diffs.is_empty() && noise.is_empty();
    json!({
        "name": case.name, "same": same, "diffs": diffs, "norms": taken, "noise": noise, "errors": errors,
        "old": side_row(&old, old_key), "new": side_row(&new, new_key),
    })
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

/// Every case's row, in the cases' order, each case's line printed as soon as it and every case before it are done. The kept sides are
/// read here; the owed ones run on `opts.jobs` workers, clamped to their count, each worker in its own world (feature 449 T173). The
/// main thread alone writes `progress` and builds the rows, so they come out as a serial run's whichever side finishes first.
fn run_cases(
    cases: &Cases,
    opts: &Opts,
    (todo, all_keys): (&[&Case], &[(String, String)]),
    progress: &mut dyn Write,
) -> Vec<Value> {
    let worlds = opts.worlds(cases);
    let key = |i: usize, s: usize| {
        if s == 0 {
            &all_keys[i].0
        } else {
            &all_keys[i].1
        }
    };
    let mut slots: Vec<[Option<Done>; 2]> = todo.iter().map(|_| [None, None]).collect();
    let mut owed = Vec::new();
    for (i, case) in todo.iter().enumerate() {
        for (s, which) in SIDES.into_iter().enumerate() {
            match standing(cases, case, (which, worlds), key(i, s), forced(opts, which)) {
                Some(side) => {
                    slots[i][s] = Some(Done {
                        side,
                        noise: Vec::new(),
                    });
                }
                None => owed.push((i, s)),
            }
        }
    }
    let workers = opts.jobs.max(1).min(owed.len());
    let next = AtomicUsize::new(0);
    let (tx, rx) = std::sync::mpsc::channel();
    let mut rows = Vec::with_capacity(todo.len());
    std::thread::scope(|scope| {
        for w in 0..workers {
            let (tx, owed, next) = (tx.clone(), &owed, &next);
            scope.spawn(move || {
                while let Some(&(i, s)) = owed.get(next.fetch_add(1, Ordering::Relaxed)) {
                    let which = SIDES[s];
                    let at = world(cases, which, (workers > 1).then_some(w));
                    let twice = opts.twice && s == 0;
                    let done = rerun(cases, todo[i], (which, worlds), key(i, s), (twice, &at));
                    // the receiver lives until every worker is done, so a send cannot fail
                    let _ = tx.send((i, s, done));
                }
            });
        }
        drop(tx);
        let mut emit = |slots: &mut Vec<[Option<Done>; 2]>| {
            while let Some(slot) = slots
                .get_mut(rows.len())
                .filter(|slot| slot.iter().all(Option::is_some))
            {
                let i = rows.len();
                let pair = std::mem::take(slot).map(Option::unwrap_or_default);
                let row = one_case(cases, todo[i], &all_keys[i], pair);
                let _ = writeln!(progress, "{}", line(&row));
                rows.push(row);
            }
        };
        emit(&mut slots);
        for (i, s, done) in rx {
            slots[i][s] = Some(done);
            emit(&mut slots);
        }
    });
    rows
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
    let rows = run_cases(cases, opts, (&todo, &all_keys), progress);
    let mut all_same = true;
    let mut norms: BTreeMap<String, usize> = BTreeMap::new();
    let (mut rerun, mut kept_n) = (0, 0);
    for row in &rows {
        all_same &= row["same"] == true;
        for side in SIDES {
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
