//! `make maps` (feature 449 T252; Constitution VI, "THERE IS ONE COMMAND, AND IT PICKS ITS OWN SCOPE", GM 2026-08-23, rebuilt on the
//! GM's 2026-11-22 ruling "okay good, please proceed on that basis then"): the one self-scoping command over the Rust sweeps. It reads
//! how the LAST run went from one record, `.git/maps-state.json`, and decides both the scope and the verbosity from it:
//!
//! - last run PASSED: every tier row's whole run, every failure reported together;
//! - last run FAILED, or no last run: each row's reference map alone, drawn and judged, stopping at the FIRST problem; only when every
//!   reference is clean does the same run widen to the whole of every row;
//! - `SCOPE=reference` / `SCOPE=all` says what is meant; `TIER=<row>` runs that row alone.
//!
//! WHY (measured 2026-11-22, this tree, warm): a reference map costs about half a second (Inashiro's roll 0.4-0.7 s, one Mode A sheet's
//! audit 0.09 s) where the whole run costs the cohort's 4.4-4.8 s and the Mode A crate's 315 tests about 25 s fresh (1.6 s where its
//! last green result stands) - and each larger tier adds its own. The Python `make maps` (`mapcheck.py`) went with the Python engine
//! (feature 444 T39), leaving two commands, `make map MAP=` and the pool sweep, which the clause forbids.
//!
//! THE TIER TABLE ([`TIERS`]): one row a tier, its pool folders and its named reference map; each larger tier (villages, towns,
//! provincial cities) adds its row as it gains a live generator. A row's steps are the launcher's own commands
//! (`scripts/gates/l7r-gate.sh <words>`), so nothing here is an engine: drawing is `pool map` (the generation cache, `make map`'s), and
//! judging is the engine's check - `mode-a sweep <map>` (one sheet through its tier's registered checks) and `hamlet --check <spec>`
//! (the roll's refusals and the finished map's rules), since a draw judges no rule and a cached map runs nothing at all. A row's whole
//! run draws every live map of its folders, the reference first, then judges the tier: the Mode A crate's tests and pool sweep
//! (`rust test --crate rust/mode_a`, `make rust-test CRATE=rust/mode_a`'s), or every pool hamlet checked and the 48-seed cohort
//! (`make cohort`'s). Widening re-runs the references inside the whole runs (a cached draw and a judge, about half a second a row),
//! so a narrow run is always a prefix of a wide one.
//!
//! Research: plumbing - NONE: runs the tiers' existing draws and checks and records how the run went, deciding nothing about a place

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::{json, Value};

use crate::walk::{walk, Map, Walk};
use crate::LIVE;

/// The command's usage.
pub const USAGE: &str = "usage: pool maps [--scope auto|reference|all] [--tier <row>]  (make maps [SCOPE=reference|all] [TIER=<row>])\n";

/// The record's file in the checkout's git directory.
const NAME: &str = "maps-state.json";

/// How a row's maps are judged.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Judge {
    /// `mode-a sweep <map>` for one sheet; the crate's tests and pool sweep for the tier.
    ModeA,
    /// `hamlet --check <spec>...` for the pool's hamlets; the cohort besides for the tier.
    Hamlet,
}

/// One tier row: its name, the pool folders it covers, its reference map, how it is judged.
#[derive(Clone, Copy, Debug)]
pub struct Row {
    pub name: &'static str,
    pub folders: &'static [&'static str],
    pub reference: &'static str,
    pub judge: Judge,
}

/// THE TIER TABLE. The hamlet reference is Constitution VI's canonical hamlet, Inashiro. The Mode A reference is a GENERATED compound,
/// `county-magistracy-example`, because the clause is about generator changes and a hand sheet does not move under one (chosen by the
/// session for T252, 2026-11-22). Add a tier by adding its row and naming its reference deliberately, never alphabetically.
pub const TIERS: &[Row] = &[
    Row {
        name: "hamlets",
        folders: &["hamlets"],
        reference: "inashiro",
        judge: Judge::Hamlet,
    },
    Row {
        name: "mode-a",
        folders: &["magistracies", "country-shrines"],
        reference: "county-magistracy-example",
        judge: Judge::ModeA,
    },
];

/// What was asked for.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Scope {
    Auto,
    Reference,
    All,
}

/// Runs a launcher command: whether it passed, and what it said.
pub trait Launch {
    fn run(&mut self, args: &[String]) -> (bool, String);
}

/// The launcher, `scripts/gates/l7r-gate.sh <words>` from the root, its stdout and stderr kept in that order.
pub struct Launcher {
    pub root: PathBuf,
}

impl Launch for Launcher {
    fn run(&mut self, args: &[String]) -> (bool, String) {
        let script = self.root.join("scripts/gates/l7r-gate.sh");
        match Command::new(&script)
            .args(args)
            .current_dir(&self.root)
            .output()
        {
            Ok(o) => (
                o.status.success(),
                format!(
                    "{}{}",
                    String::from_utf8_lossy(&o.stdout),
                    String::from_utf8_lossy(&o.stderr)
                ),
            ),
            Err(e) => (false, format!("{} did not start: {e}\n", script.display())),
        }
    }
}

/// One step: its label, and the launcher's words.
struct Step {
    label: String,
    args: Vec<String>,
}

fn step(label: String, args: Vec<String>) -> Step {
    Step { label, args }
}

/// The last run, as the record holds it.
#[derive(Debug)]
pub struct Last {
    pub ok: bool,
    pub scope: String,
    pub failed: Vec<String>,
}

/// Where the record lives: a worktree's `.git` is a file naming its own git directory, so two checkouts never share one.
#[must_use]
pub fn state_file(root: &Path) -> PathBuf {
    let dotgit = root.join(".git");
    let text = std::fs::read_to_string(&dotgit).unwrap_or_default();
    match text.trim().strip_prefix("gitdir:") {
        Some(rest) => root.join(rest.trim()).join(NAME),
        None => dotgit.join(NAME),
    }
}

/// The last run, or None where there is none or it does not read (both are taken as failed).
#[must_use]
pub fn read(root: &Path) -> Option<Last> {
    let v: Value = serde_json::from_str(&std::fs::read_to_string(state_file(root)).ok()?).ok()?;
    Some(Last {
        ok: v["ok"].as_bool()?,
        scope: v["scope"].as_str().unwrap_or_default().to_owned(),
        failed: v["failed"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(Value::as_str)
                    .map(str::to_owned)
                    .collect()
            })
            .unwrap_or_default(),
    })
}

/// A row's live maps, its reference first (Err where the reference is not among them).
fn maps<'a>(w: &'a Walk, row: &Row) -> Result<Vec<&'a Map>, String> {
    let mut found: Vec<&Map> = w
        .in_tree(LIVE)
        .filter(|m| m.kind.is_live() && row.folders.contains(&m.tier.as_str()))
        .collect();
    found.sort_by_key(|m| (m.name != row.reference, m.name.clone()));
    if found.first().is_some_and(|m| m.name == row.reference) {
        Ok(found)
    } else {
        Err(format!(
            "{}: the reference map {} is no live map of {} - name one in the tier table (rust/gate/crates/pool/src/maps.rs)",
            row.name,
            row.reference,
            row.folders.iter().map(|f| format!("pool/{f}")).collect::<Vec<_>>().join(", ")
        ))
    }
}

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

/// The hamlet driver's check of these maps' specs.
fn hamlet_check(maps: &[&Map]) -> Vec<String> {
    let mut args = words(&["hamlet", "--check"]);
    args.extend(
        maps.iter()
            .map(|m| m.file(".spec.json").to_string_lossy().into_owned()),
    );
    args
}

/// A row's reference: drawn, then judged.
fn reference_steps(w: &Walk, row: &Row) -> Result<Vec<Step>, String> {
    let r = maps(w, row)?[0];
    let judged = match row.judge {
        Judge::ModeA => vec!["mode-a".to_owned(), "sweep".to_owned(), r.rel()],
        Judge::Hamlet => hamlet_check(&[r]),
    };
    Ok(vec![
        step(
            format!("{}: {} drawn", row.name, r.name),
            vec!["pool".to_owned(), "map".to_owned(), r.rel()],
        ),
        step(format!("{}: {} judged", row.name, r.name), judged),
    ])
}

/// A row's whole run: every live map drawn, the reference first, then the tier judged.
fn wide_steps(w: &Walk, row: &Row) -> Result<Vec<Step>, String> {
    let all = maps(w, row)?;
    let mut drawn = words(&["pool", "map"]);
    drawn.extend(all.iter().map(|m| m.rel()));
    let mut out = vec![step(format!("{}: every map drawn", row.name), drawn)];
    match row.judge {
        Judge::ModeA => out.push(step(
            format!("{}: the crate's tests and the pool sweep", row.name),
            words(&["rust", "test", "--crate", "rust/mode_a"]),
        )),
        Judge::Hamlet => {
            out.push(step(
                format!("{}: every pool hamlet judged", row.name),
                hamlet_check(&all),
            ));
            out.push(step(
                format!("{}: the cohort, 48 seeds", row.name),
                words(&["hamlet", "--cohort", "1", "48"]),
            ));
        }
    }
    Ok(out)
}

/// What a run did: its output, its failures, the steps it ran.
#[derive(Default)]
struct Ran {
    out: String,
    failed: Vec<String>,
    steps: usize,
}

impl Ran {
    /// The steps of each row; `stop` ends the run at the first problem.
    fn rows(
        &mut self,
        w: &Walk,
        rows: &[&Row],
        steps_of: fn(&Walk, &Row) -> Result<Vec<Step>, String>,
        stop: bool,
        launch: &mut dyn Launch,
    ) {
        for row in rows {
            let steps = match steps_of(w, row) {
                Ok(s) => s,
                Err(why) => {
                    let _ = writeln!(self.out, "FAILED: {why}");
                    self.failed.push(why);
                    if stop {
                        return;
                    }
                    continue;
                }
            };
            for s in steps {
                let _ = writeln!(self.out, "== {} ==", s.label);
                let (ok, said) = launch.run(&s.args);
                self.steps += 1;
                self.out.push_str(&said);
                if !ok {
                    let _ = writeln!(self.out, "FAILED: {}", s.label);
                    self.failed.push(s.label);
                    if stop {
                        return;
                    }
                }
            }
        }
    }
}

/// `make maps` over `rows` (the tier table in a run): the scope picked, the steps run through `launch`, the record written.
#[must_use]
pub fn run(
    root: &Path,
    rows: &[Row],
    scope: Scope,
    tier: Option<&str>,
    launch: &mut dyn Launch,
) -> crate::Said {
    let chosen: Vec<&Row> = rows
        .iter()
        .filter(|r| tier.is_none_or(|t| r.name == t))
        .collect();
    if chosen.is_empty() {
        let names: Vec<&str> = rows.iter().map(|r| r.name).collect();
        return (
            String::new(),
            format!(
                "make maps: no tier row {} - the rows: {}\n",
                tier.unwrap_or_default(),
                names.join(", ")
            ),
            2,
        );
    }
    let last = read(root);
    let why = match (scope, &last) {
        (Scope::Reference, _) => "SCOPE=reference".to_owned(),
        (Scope::All, _) => "SCOPE=all".to_owned(),
        (Scope::Auto, None) => "no last run".to_owned(),
        (Scope::Auto, Some(l)) if l.ok => "last run PASSED".to_owned(),
        (Scope::Auto, Some(l)) => format!("last run FAILED on {}", l.failed.join(", ")),
    };
    let wide_first = scope == Scope::All || (scope == Scope::Auto && last.is_some_and(|l| l.ok));
    let what = match (wide_first, scope) {
        (true, _) => "every tier whole, reporting every failure",
        (false, Scope::Reference) => "the reference maps alone, stopping at the first problem",
        (false, _) => "the reference maps first, stopping at the first problem; widening only once they are clean",
    };
    let w = walk(root);
    let mut ran = Ran::default();
    let _ = writeln!(ran.out, "make maps: {why} -> {what}");
    let mut widened = wide_first;
    if wide_first {
        ran.rows(&w, &chosen, wide_steps, false, launch);
    } else {
        ran.rows(&w, &chosen, reference_steps, true, launch);
        if ran.failed.is_empty() && scope == Scope::Auto {
            ran.out.push_str(
                "make maps: the reference maps are clean - widening to every tier whole\n",
            );
            ran.rows(&w, &chosen, wide_steps, false, launch);
            widened = true;
        }
    }
    let ok = ran.failed.is_empty();
    let record = json!({
        "ok": ok,
        "scope": if widened { "all" } else { "reference" },
        "failed": ran.failed,
        "tiers": chosen.iter().map(|r| r.name).collect::<Vec<_>>(),
    });
    let _ = writeln!(
        ran.out,
        "make maps: {} step(s) over {} tier row(s), {}",
        ran.steps,
        chosen.len(),
        if ok {
            "every one clean".to_owned()
        } else {
            format!("{} failed: {}", ran.failed.len(), ran.failed.join("; "))
        }
    );
    let file = state_file(root);
    if let Err(e) = std::fs::write(&file, format!("{record:#}\n")) {
        return (
            ran.out,
            format!(
                "make maps: the run's record could not be written to {}: {e}\n",
                file.display()
            ),
            1,
        );
    }
    (ran.out, String::new(), i32::from(!ok))
}

/// `maps [--scope auto|reference|all] [--tier <row>]`, through the launcher, over the tier table.
#[must_use]
pub fn cli(root: &Path, args: &[&str]) -> crate::Said {
    let (mut scope, mut tier) = (Scope::Auto, None);
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match (*a, it.next().copied()) {
            ("--scope", Some("auto")) => scope = Scope::Auto,
            ("--scope", Some("reference")) => scope = Scope::Reference,
            ("--scope", Some("all")) => scope = Scope::All,
            ("--tier", Some(t)) => tier = Some(t),
            _ => return (String::new(), USAGE.to_owned(), 2),
        }
    }
    run(
        root,
        TIERS,
        scope,
        tier,
        &mut Launcher {
            root: root.to_path_buf(),
        },
    )
}

#[cfg(test)]
mod tests;
