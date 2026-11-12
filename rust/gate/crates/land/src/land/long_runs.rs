//! Pass 2: the long runs, each only where its record does not cover this content (`land.py`'s `long_runs` and what it calls). The
//! changed modules' coverage check that once ran beside the gate is gone since the Python tests were deleted (feature 449 FR-001b:
//! `land.py`'s `start_cover` answered None and nothing else reached its branches), so its paths are not ported.

use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Child, Command};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::{py_read, stop, Land};

/// The gate the green-gate stamp names for each stale area: "(make done again)", "(make hooks-test again)", "(make page-check again)".
static NAMED_GATE: LazyLock<Regex> = LazyLock::new(|| re(r"\(make ([\w-]+) again\)"));
/// The paths that decide how a landing and its gate run (the round arbiter's `tooling_fix` on red-gate@2026-10-24T19:17:09Z, feature 415:
/// T03 put `cover_changed.py` beside the gate on the direct route, untested beside a real gate, and two red gates followed). A delta
/// touching one whose green-gate stamp still passes runs the TOOLING TESTS, not `make done` (the round arbiter's process-fault on
/// ask:430-machinery-gate, 2026-10-26): the done recipe's reuse branch ignores scripts/, tests/ and the Makefile by the GM's 2026-08-25
/// rule ("I thought we were omitting make done results for changes to the hooks or scripts or makefile changes"), so the `make done`
/// this used to add always short-circuited. `land.py`'s list, with the landing's own code at its new home: the commit deleting
/// `scripts/land.py` put it in `rust/gate/crates/land/`, which a delta changes as it changed the Python (feature 449 T121).
static GATE_MACHINERY: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^(rust/gate/crates/land/.*|scripts/gates/.*|Makefile|tests/conftest\.py|tests/_scope\.py)$",
    )
});
/// `work_budget.review`'s refusal for a run never made.
const MISSING_RUN: &str = "no work-budget run at the pushed engine";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The delta's paths that decide how a landing and its gate run.
fn gate_machinery(names: &[String]) -> Vec<String> {
    names
        .iter()
        .filter(|n| GATE_MACHINERY.is_match(n).unwrap_or(false))
        .cloned()
        .collect()
}

impl Land {
    /// Pass 2's runs, each only where its record does not cover this content; 0 when the push may go. The green-gate stamp names the
    /// gate each stale area owes (make done, make hooks-test, make page-check) and each named one runs - T30-T35's own landing owed
    /// hooks-test alone, which a `make done` would not have stamped.
    pub(super) fn long_runs(&self) -> Result<i32, String> {
        let gate = self.gate();
        let stamp = [gate.as_str(), "stamp", "--check", "origin/main"];
        // THE RUST STAGE GATE'S RECORD FIRST (feature 444 T21's landing): the landing cohort's own check asks for it, so made after the
        // cohort it refused a cohort that had passed 54 of 54 - it rolls in seconds and nothing the gate does moves the engine it keys
        let why = self.rust_gate_run()?;
        if !why.is_empty() {
            self.warn(&why);
            return Ok(1);
        }
        let (rc, out) = self.run(&stamp, &[])?;
        let names = self.delta_names()?;
        let machinery = gate_machinery(&names);
        if !machinery.is_empty() && rc == 0 {
            let why = self.machinery_tests(&machinery)?;
            if !why.is_empty() {
                self.warn(&why);
                return Ok(1);
            }
        }
        if machinery.is_empty() {
            let reads = tooling_reads(&self.root, &names)?;
            if !reads.is_empty() {
                self.say(&format!("land: the delta changes scripts or tooling tests - the {} tooling test file(s) reaching them run", reads.len()));
                let file = format!("FILE={}", reads.join(" "));
                if self.loud(
                    &[&self.make, "--no-print-directory", "test-file", &file],
                    &[],
                )? != 0
                {
                    self.warn("land: the tooling tests the delta reaches are red - nothing landed; fix them and run make land again");
                    return Ok(1);
                }
            }
        }
        if rc != 0 && self.named_gates(&out)? != 0 {
            return Ok(1);
        }
        if rc != 0 {
            let (rc, out) = self.run(&stamp, &[])?;
            if rc != 0 {
                self.warn(&format!("land: the gates it named are green, but the green-gate stamp still refuses - nothing landed:\n{out}"));
                return Ok(1);
            }
        }
        if self.engine_delta()?
            && self.port()? != "rust-only"
            && self.run(&[&gate, "cohort", "check"], &[])?.0 != 0
        {
            self.say("land: no landing cohort on this engine - make cohort-landing");
            if self.make("cohort-landing")? != 0 {
                self.warn("land: the landing cohort refused - nothing landed (above)");
                return Ok(1);
            }
            self.commit_regenerated("cohort")?;
        }
        let why = self.budget_run()?;
        if !why.is_empty() {
            self.warn(&why);
            return Ok(1);
        }
        Ok(0)
    }

    /// Each gate the stamp names, the landing cohort beside `make done` where it is owed; 1 when one is red. What they regenerated and
    /// recorded is committed after.
    fn named_gates(&self, stamp_said: &str) -> Result<i32, String> {
        let mut targets: Vec<String> = Vec::new();
        for m in NAMED_GATE.captures_iter(stamp_said).flatten() {
            if !targets.iter().any(|t| t == &m[1]) {
                targets.push(m[1].to_owned());
            }
        }
        if targets.is_empty() {
            targets.push("done".to_owned());
        }
        // THE COHORT BESIDE THE GATE (405 T48, D21): they share no work - the gate rolls the five pool maps, the cohort its seeds and rows
        // - and T19's landing spent 4.4 of its 7 minutes on the cohort after a green gate; none while the port switch stands at rust-only
        // (feature 444 FR-023): no landing waits on the Python stages' rolls
        let mut cohort = None;
        if targets.iter().any(|t| t == "done")
            && self.engine_delta()?
            && self.port()? != "rust-only"
            && self.run(&[&self.gate(), "cohort", "check"], &[])?.0 != 0
        {
            cohort = Some(self.start_cohort()?);
        }
        let ran = self.gates_and_cohort(&targets, &mut cohort);
        stop_cohort(cohort.as_mut().map(|(c, _)| c));
        if ran? != 0 {
            return Ok(1);
        }
        self.commit_records()?;
        self.commit_regenerated("gate")?;
        Ok(0)
    }

    /// The named gates in turn, then the cohort beside them waited on; 1 at the first red one.
    fn gates_and_cohort(
        &self,
        targets: &[String],
        cohort: &mut Option<(Child, PathBuf)>,
    ) -> Result<i32, String> {
        for target in targets {
            self.say(&format!("land: the green-gate stamp does not cover this content - make {target} (the changed modules' coverage beside it)"));
            if self.run_gate(target)? != 0 {
                self.warn(&format!(
                    "land: make {target} is red - nothing landed; fix it and run make land again"
                ));
                return Ok(1);
            }
        }
        if let Some((child, log)) = cohort.as_mut() {
            self.say("land: the gate is green - waiting for the landing cohort beside it");
            let status = child.wait().map_err(super::io)?;
            let text =
                String::from_utf8_lossy(&std::fs::read(&*log).unwrap_or_default()).into_owned();
            let shown: Vec<&str> = splitlines(&text)
                .into_iter()
                .filter(|l| {
                    l.contains("passed the whole gate")
                        || l.contains("fresh block")
                        || l.to_uppercase().contains("REGRESS")
                })
                .collect();
            self.say(&shown.join("\n"));
            if !status.success() {
                self.warn(&format!(
                    "land: the landing cohort refused - nothing landed ({})",
                    log.display()
                ));
                return Ok(1);
            }
        }
        Ok(0)
    }

    /// `make <target>` in its own process group, held so a stopped landing stops it ([`stop`]): its exit code. With no `FULL_FRACTION`
    /// cutoff: a landing runs what its change reaches, however much (feature 415 T05, D8) - a make variable the test recipe hands to the
    /// planner's call alone, never an environment the gate's tests inherit (the round arbiter on red-gate@2026-10-24T19:05: an exported
    /// `INCR_NO_CUTOFF` reached three planner tests and turned them red).
    fn run_gate(&self, target: &str) -> Result<i32, String> {
        let mut child = self
            .command(&[&self.make, "--no-print-directory", target, "NO_CUTOFF=1"])
            .process_group(0)
            .spawn()
            .map_err(|e| super::spawn_error(&self.make, &e))?;
        stop::hold(child.id());
        let status = child.wait();
        stop::release(child.id());
        Ok(super::code_of(status.map_err(super::io)?))
    }

    /// `make cohort-landing` in its own process group, beside the gate (405 T48, D21): its rolls are no gate's (the census variables
    /// removed), its reference check leaves the gate's `roll-cache-class` alone, its output to a log under the git dir.
    fn start_cohort(&self) -> Result<(Child, PathBuf), String> {
        let (jobs, avail) = self.cohort_jobs()?;
        let log = self.git_dir()?.join("land-cohort.log");
        self.say(&format!("land: make cohort-landing JOBS={jobs} beside the gate ({avail} MB free to the container; its log {})", log.display()));
        let sink = std::fs::File::create(&log).map_err(super::io)?;
        let err = sink.try_clone().map_err(super::io)?;
        let jobs = format!("JOBS={jobs}");
        // the process's environment less the census variables, then what the landing exported, as `land.py`'s dict comprehension
        // over `os.environ` built it
        let mut cmd = Command::new(&self.make);
        cmd.args(["--no-print-directory", "cohort-landing", &jobs])
            .current_dir(&self.root)
            .env_clear()
            .envs(
                std::env::vars_os()
                    .filter(|(k, _)| !k.to_string_lossy().starts_with("L7R_ROLL_CENSUS")),
            )
            .envs(self.exported.borrow().iter().cloned());
        let child = cmd
            .env("L7R_REF_NO_CLASS", "1")
            .stdout(sink)
            .stderr(err)
            .process_group(0)
            .spawn()
            .map_err(|e| super::spawn_error(&self.make, &e))?;
        stop::hold(child.id());
        Ok((child, log))
    }

    /// A gate-machinery delta whose stamp passes: `make hooks-test` where the hooks stamp is stale; why nothing lands, or ''.
    fn machinery_tests(&self, machinery: &[String]) -> Result<String, String> {
        let first: Vec<&str> = machinery.iter().take(3).map(String::as_str).collect();
        self.say(&format!("land: the delta changes how a landing or its gate runs ({}) - the gate's reuse stands (the GM's 2026-08-25 rule: scripts/ and the Makefile owe no make done), so the guard suites run instead (ask:430-machinery-gate)", first.join(", ")));
        if self
            .run(&[&self.gate(), "stamp", "--fresh", "hooks"], &[])?
            .0
            != 0
            && self.loud(&[&self.make, "--no-print-directory", "hooks-test"], &[])? != 0
        {
            return Ok(
                "land: make hooks-test is red - nothing landed; fix it and run make land again"
                    .to_owned(),
            );
        }
        Ok(String::new())
    }

    /// A run record the gate or the cohort could not commit - two commits at once, one lost the index lock - committed here.
    fn commit_records(&self) -> Result<(), String> {
        if !self.dirty(&["dev/cohort-log", "dev/run-log"])?.is_empty() {
            self.run(&["git", "add", "--", "dev/cohort-log", "dev/run-log"], &[])?;
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "the run records (make land)",
                    "--",
                    "dev/cohort-log",
                    "dev/run-log",
                ],
                &[],
            )?;
        }
        Ok(())
    }

    /// What a gate run regenerated under `pool/` (T12: Kuwabata's manifest), committed so the push carries it.
    fn commit_regenerated(&self, why: &str) -> Result<(), String> {
        if !self.dirty(&["pool/"])?.is_empty() {
            self.run(&["git", "add", "--", "pool/"], &[])?;
            let message = format!("regenerated by the landing's {why} (make land)");
            self.run(&["git", "commit", "-q", "-m", &message], &[])?;
        }
        Ok(())
    }

    /// THE RUST STAGE GATE'S RECORD, MADE HERE (feature 444 amendment 5, D6): the push refuses an engine landing with no `make rust-gate`
    /// record on its engine with no failing seed (`l7r-gate cohort rust-owed`); where it is owed, land rolls it and commits
    /// `dev/rust-gate/`. A failing seed stops the landing: no Rust stage may end with a failing check (FR-019).
    fn rust_gate_run(&self) -> Result<String, String> {
        if !self.engine_delta()? || self.run(&[&self.gate(), "cohort", "rust-owed"], &[])?.0 != 0 {
            return Ok(String::new());
        }
        self.say("land: no Rust stage gate record on this engine - make rust-gate");
        let failed = self.make("rust-gate")?;
        self.run(&["git", "add", "--", "dev/rust-gate"], &[])?;
        self.run(
            &[
                "git",
                "commit",
                "-q",
                "-m",
                "the Rust stage gate's record at the landing's engine (make land)",
            ],
            &[],
        )?;
        Ok(if failed == 0 {
            String::new()
        } else {
            "land: the Rust stage gate has a failing seed - nothing landed (above); no Rust stage may end with a failing check".to_owned()
        })
    }

    /// THE WORK-BUDGET RUN THE PUSH WILL ASK FOR, MADE HERE (feature 444 T20, D1): on an engine delta the push's `make
    /// work-budget-review` refuses a push with no run at its engine, and T17's and T19's landings each lost a gate to it. Asked first, as
    /// the push asks it; where its one refusal is that missing run, `make work-budget` is run and committed. Any other refusal - an
    /// accepted stage over its figure - stops the landing as before: only the GM's words raise a figure.
    fn budget_run(&self) -> Result<String, String> {
        if !self.engine_delta()? {
            return Ok(String::new());
        }
        let (rc, out) = self.run(
            &[
                &self.make,
                "--no-print-directory",
                "work-budget-review",
                "ROUTE=GATED",
            ],
            &[],
        )?;
        if rc == 0 {
            return Ok(String::new());
        }
        if !out.contains(MISSING_RUN) {
            return Ok(format!(
                "land: the work-budget review refuses this engine - nothing landed:\n{}",
                strip(&out)
            ));
        }
        self.say("land: no work-budget run at this engine - make work-budget");
        if self.make("work-budget")? != 0 {
            return Ok("land: make work-budget failed - nothing landed (above)".to_owned());
        }
        self.run(
            &["git", "add", "--", "dev/work-budget.md", "dev/work-budget"],
            &[],
        )?;
        self.run(
            &[
                "git",
                "commit",
                "-q",
                "-m",
                "the work-budget run at the landing's engine (make land)",
            ],
            &[],
        )?;
        Ok(String::new())
    }
}

/// The cohort's whole process group ended - a red gate voids what it would record, and no exit leaves it running.
fn stop_cohort(cohort: Option<&mut Child>) {
    if let Some(child) = cohort {
        if matches!(child.try_wait(), Ok(None)) {
            stop::kill_group(child.id());
            let _ = child.wait();
        }
        stop::release(child.id());
    }
}

/// The tooling test files a delta of scripts reaches: each changed `tests/tooling/` test, and each one naming a changed `scripts/**/*.py`
/// by its module name. WHY (feature 446 T03, 2026-10-28): a delta of `scripts/record/` and its tests is no gate machinery and its stamp
/// owes only `make hooks-test`, so the tooling tests never ran - T02 landed a call that broke `test_known_drift.py`'s stub of `owed`,
/// caught only by T03's Makefile line pulling in the whole tooling run.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, case and all"
)]
fn tooling_reads(root: &Path, names: &[String]) -> Result<Vec<String>, String> {
    let file_name = |n: &str| n.rsplit('/').next().unwrap_or_default().to_owned();
    let mut tests: Vec<String> = names
        .iter()
        .filter(|n| {
            n.starts_with("tests/tooling/")
                && file_name(n).starts_with("test_")
                && n.ends_with(".py")
                && root.join(n).is_file()
        })
        .cloned()
        .collect();
    let mut stems: Vec<String> = names
        .iter()
        .filter(|n| n.starts_with("scripts/") && n.ends_with(".py"))
        .map(|n| {
            let name = file_name(n);
            name.rsplit_once('.')
                .map_or(name.as_str(), |(s, _)| s)
                .to_owned()
        })
        .collect();
    stems.sort();
    stems.dedup();
    if !stems.is_empty() {
        let alternatives: Vec<String> = stems
            .iter()
            .map(|s| fancy_regex::escape(s).into_owned())
            .collect();
        let pattern = re(&format!(r"\b(?:{})\b", alternatives.join("|")));
        let mut found = Vec::new();
        walk_tests(&root.join("tests/tooling"), &mut found);
        for p in found {
            if pattern.is_match(&py_read(&p)?).unwrap_or(false) {
                tests.push(super::rel_of(root, &p));
            }
        }
    }
    tests.sort();
    tests.dedup();
    Ok(tests)
}

/// Every `test_*.py` under `dir` (`rglob`).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "`rglob(\"test_*.py\")`, case and all"
)]
fn walk_tests(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        let name = entry.file_name().to_string_lossy().into_owned();
        if entry.file_type().is_ok_and(|t| t.is_dir()) {
            walk_tests(&path, out);
        } else if name.starts_with("test_") && name.ends_with(".py") {
            out.push(path);
        }
    }
}

#[cfg(test)]
mod tests;
