//! Pass 1: every refusal the landing would meet that costs seconds to ask, all of them (`land.py`'s `cheap_refusals` and what it calls) -
//! and the records the landing writes for itself on the way: the ledger rows, the make-targets page, the claims' moved rows, the carries,
//! the known drifts and its own escape records.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::{head, name_of, py_read, rel_of, tail, Land};
use crate::Reply;

const PHASE_TEMPLATE: &str = ".specify/templates/phase-checklist.md";
static PHASE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\s*phase:\s*([a-z_]+)\s*$"));
static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[([ xX])\] (\d\. \*\*[^*]+\*\*)"));
static FILED_INTO: LazyLock<Regex> = LazyLock::new(|| re(r"filed into (\S+) T\d+"));

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A reply as `run` read a command's: its code, its stdout then its stderr.
fn said(r: Reply) -> (i32, String) {
    (r.code, r.stdout + &r.stderr)
}

/// The gates the first pass asks, in its order.
const GATES: [&str; 3] = ["claims-gate.sh", "review-gate.sh", "plan-gate.sh"];

impl Land {
    /// `l7r-gate claims --root <root> <args>`, in process (`ask:449-T83-scope`).
    pub(super) fn claims(&self, args: &[&str]) -> (i32, String) {
        let root = self.root.to_string_lossy().into_owned();
        let mut all = vec!["--root".to_owned(), root];
        all.extend(args.iter().map(|a| (*a).to_owned()));
        said(self.inproc.claims(&all))
    }

    /// `l7r-gate reviews ledger-owed <args>`, in process (`ask:449-T83-scope`), run from the root as the command was.
    fn ledger(&self, args: &[&str]) -> (i32, String) {
        let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
        said(self.inproc.ledger(&args, &self.root))
    }

    /// The ledger rows the push would name as owed, written and committed: the plan reviews' (385 T72) and every other pass traced to
    /// this feature - its claims round's above all (405 T39, D13). Asked in the first pass, and again after the claims wait (405 T52,
    /// D27: T49's claims round ran beside the gate, after the first pass, and its row was written by hand).
    pub(super) fn write_ledger(&self, d: &Path) -> Result<(), String> {
        let ledger = self.root.join("dev/review-ledger.md");
        let ledger = ledger.to_string_lossy();
        self.ledger(&["--write-plan-reviews", "--ledger", &ledger]);
        let at = format!(
            "specs/{}/ (the records its checks wrote; make land)",
            name_of(d)
        );
        self.ledger(&["--write", &at, "--ledger", &ledger]);
        if !self.dirty(&["dev/review-ledger.md"])?.is_empty() {
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "the review passes' ledger rows, written at landing (make land)",
                    "--",
                    "dev/review-ledger.md",
                ],
                &[],
            )?;
        }
        Ok(())
    }

    /// Every carried claims finding filed as an open task of the feature and committed (405 T36, D10) - asked in the first pass and
    /// again in the claims wait, where a round beside the gate meets new carries (405 T77).
    pub(super) fn file_carries(&self, d: &Path) -> Result<(), String> {
        let name = name_of(d);
        let num = name.split('-').next().unwrap_or_default();
        let (rc, out) = self.claims(&["carry", "--feature", num]);
        if rc == 0 && out.contains("filed into") {
            self.say(&format!("land: {}", strip(&out)));
            // ...into the claims feature when this delta holds no engine code (the GM, 2026-10-26; `claims_carry.target`)
            let rel = FILED_INTO
                .captures(&out)
                .ok()
                .flatten()
                .map_or_else(|| rel_of(&self.root, d), |m| format!("specs/{}", &m[1]));
            self.run(
                &[
                    "git",
                    "add",
                    "--",
                    &format!("{rel}/tasks.md"),
                    &format!("{rel}/claims-carried.jsonl"),
                ],
                &[],
            )?;
            let message = format!(
                "{name}: claims findings outside the change filed as a task (make land, 405 T36)"
            );
            self.run(&["git", "commit", "-q", "-m", &message], &[])?;
        }
        Ok(())
    }

    /// Every known drift the claims gate would refuse unrecorded, recorded for the GM in its task's feature and committed (feature 430
    /// T06, D6): the claims gate admits a known drift once `make claims-known` has recorded it, and the landing runs it.
    pub(super) fn file_known(&self) -> Result<(), String> {
        let (rc, out) = self.claims(&["known"]);
        // ...not its "no known drift is unrecorded"
        if rc == 0 && out.contains("claims-known: recorded") {
            self.say(&format!("land: {}", strip(&out)));
            let mut cmd: Vec<String> = vec!["git".into(), "add".into(), "--".into()];
            cmd.extend(self.each_spec("gm-review.jsonl"));
            cmd.extend(self.each_spec("tasks.md"));
            let cmd: Vec<&str> = cmd.iter().map(String::as_str).collect();
            self.run(&cmd, &[])?;
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "known drifts recorded for the GM's review (make land, feature 430 T06)",
                ],
                &[],
            )?;
        }
        Ok(())
    }

    /// `sorted((root / "specs").glob("*/<file>"))`, relative to the root.
    fn each_spec(&self, file: &str) -> Vec<String> {
        let mut out: Vec<String> = std::fs::read_dir(self.root.join("specs"))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path().join(file))
            .filter(|p| p.exists())
            .map(|p| rel_of(&self.root, &p))
            .collect();
        out.sort();
        out
    }

    /// A stale entry of the coverage-exempt record (feature 448 D4), asked in seconds here rather than at the gate's floor.
    fn stale_exempt_refusal(&self) -> Result<String, String> {
        let gate = self.gate();
        let out = self
            .command(&[&gate, "coverage-exempt", "stale"])
            .stdin(std::process::Stdio::inherit())
            .output()
            .map_err(|e| super::spawn_error(&gate, &e))?;
        if !out.status.success() {
            return Ok(strip(&super::decode(&out.stderr)?).to_owned());
        }
        let stdout = super::decode(&out.stdout)?;
        let stale: Vec<&str> = splitlines(&stdout)
            .into_iter()
            .map(|l| l.split('\t').next().unwrap_or_default())
            .collect();
        if stale.is_empty() {
            return Ok(String::new());
        }
        let noun = if stale.len() == 1 { "y" } else { "ies" };
        Ok(format!(
            "dev/coverage-exempt.json names {} stale entr{noun} ({}) - make coverage-exempt PRUNE=1",
            stale.len(),
            stale.join(", ")
        ))
    }

    /// Pass 1: every refusal the landing would meet that costs seconds to ask, all of them - but the claims gate's, which goes to
    /// `deferred` when given (405 T50, D23: the claims round runs beside the gate, and the landing waits for it before the push).
    pub(super) fn cheap_refusals(
        &self,
        d: &Path,
        tasks: &[String],
        note: &str,
        mut deferred: Option<&mut Vec<String>>,
    ) -> Result<Vec<String>, String> {
        let text = py_read(&d.join("tasks.md"))?;
        // one refusal shared by several tasks (an hour's step-back) is printed once, naming them all
        let mut by_why: Vec<(String, Vec<String>)> = Vec::new();
        let mut add = |why: String, task: &str| match by_why.iter_mut().find(|(w, _)| *w == why) {
            Some((_, ts)) => ts.push(task.to_owned()),
            None => by_why.push((why, vec![task.to_owned()])),
        };
        // each task's tick refusal and `refusal(..., landed=False)`, in process (feature 449 T131, where this ran `tick-task.py
        // --land-check` by path): a raise there is the landing's, as the import's was
        for checked in
            l7r_gate_task::tick::checks(&self.root, d, note, tasks, self.boxes, &self.tick_env())?
        {
            if checked.box_open {
                self.box_open.borrow_mut().push(checked.task.clone());
            }
            let task = checked.task.as_str();
            if !checked.tick.is_empty() {
                add(checked.tick, task);
                continue;
            }
            if !checked.refusal.is_empty() {
                add(checked.refusal, task);
            }
            // each said, as T20 D2 has it
            for why in [
                self.phase_refusal(d, &text, task)?,
                self.open_claims_refusal(d, &text, task)?,
            ] {
                if !why.is_empty() {
                    add(why, task);
                }
            }
        }
        let mut stops: Vec<String> = by_why
            .into_iter()
            .map(|(why, ts)| format!("{}: {why}", ts.join(", ")))
            .collect();
        self.records_on_the_way(d)?;
        let stale = self.stale_exempt_refusal()?;
        if !stale.is_empty() {
            stops.push(stale);
        }
        if !self.dirty(&[])?.is_empty() {
            stops.push("uncommitted changes - commit them first".to_owned());
        }
        let ledger = self.root.join("dev/review-ledger.md");
        let (_rc, owed) = self.ledger(&["--ledger", &ledger.to_string_lossy()]);
        if owed.contains("| ? |") {
            stops.push("review passes with no ledger row - make ledger-owed WRITE=\"<where you recorded what you did>\"".to_owned());
        }
        let ticks = tasks.join(" ");
        let held = said(
            self.inproc
                .holding(&d.to_string_lossy(), &ticks, &self.root),
        )
        .1;
        let held = strip(&held);
        if !held.is_empty() {
            stops.push(format!("held by {held}"));
        }
        // A RED-GATE TRIPWIRE HOLDS THE LANDING'S GATE (feature 405 T44, D18): asked here with the others, on a landing that runs one
        if !self.arbiter_ok && self.engine_delta()? {
            let (rc, out) = self.run(&[&self.gate(), "arbiter", "gate-held"], &[])?;
            if rc != 0 {
                let out = strip(&out);
                stops.push(
                    out.strip_prefix("make done: refused - ")
                        .unwrap_or(out)
                        .to_owned(),
                );
            }
        }
        for gate in GATES {
            let (rc, out) = self.run(
                &[&self.script(&format!("gates/{gate}"))],
                &[("L7R_LAND_TICKS", &ticks)],
            )?;
            if rc == 0 {
                continue;
            }
            let said = format!("{gate}: {}", tail(&kept_lines(&out), 600));
            // ...BUT A CLAIMS REFUSAL NO WAIT CAN CURE IS A STOP NOW (feature 440 T01, the GM 2026-10-27): an owed claim with no check
            // in flight, or an introduced finding, cannot be answered while the gate runs - feature 438's landing ran its whole gate
            // (about 19 min) and then refused on a claim never dispatched
            let (to_defer, why) = if gate == "claims-gate.sh" && deferred.is_some() {
                super::claims_wait::claims_route(&out, &said, &self.in_flight()?)
            } else {
                (false, said)
            };
            match deferred.as_deref_mut() {
                Some(later) if to_defer => later.push(why),
                _ => stops.push(why),
            }
        }
        Ok(stops)
    }

    /// The records the first pass writes and commits for itself: the ledger, the make-targets page, the claims' moved rows, the
    /// carries, the known drifts and its own escape records.
    fn records_on_the_way(&self, d: &Path) -> Result<(), String> {
        self.write_ledger(d)?;
        // ...and the make-targets page, regenerated where the Makefile moved (feature 405 T46, D19): the push's `make-docs` check
        // refused T43's landing after its hooks-test, for a page `make docs` writes in a second
        // asked in process (feature 449 T135, where it ran `scripts/make-docs.py`): a failed write is passed over as the command's
        // exit was, and the commit below then finds nothing to take
        if l7r_gate_cohort::make_docs::check(&self.root).code != 0 {
            let _ = l7r_gate_cohort::make_docs::write(&self.root);
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "docs/make-targets.html regenerated at landing (make land, 405 T46)",
                    "--",
                    "docs/make-targets.html",
                ],
                &[],
            )?;
        }
        // A MOVED UNIT KEEPS ITS CLAIMS' ROWS (405 T58): a file split into a package at the 1,000-line bar re-keys them, owing nothing
        self.claims(&["rekey"]);
        if !self.dirty(&["dev/claims-index.json"])?.is_empty() {
            self.run(
                &[
                    "git",
                    "commit",
                    "-q",
                    "-m",
                    "claim rows carried to the files their units moved to (make land, 405 T58)",
                    "--",
                    "dev/claims-index.json",
                ],
                &[],
            )?;
        }
        // A FINDING OUTSIDE THE CHANGE IS FILED, NOT REFUSED (feature 405 T36, D10): the carry files every carried claims finding as an
        // open task of this feature - what `make claims-carry` does by hand - and the box lands with the work
        self.file_carries(d)?;
        self.file_known()?;
        self.commit_escape_records()
    }

    /// A feature-444 phase task (`phase: <stage>` in its lines) lands only with its checklist, `phases/<stage>.md`, holding every box
    /// of the template, each ticked (feature 443 FR-010, plan D12); '' when it may land, else the file and the first box short.
    fn phase_refusal(&self, d: &Path, text: &str, task: &str) -> Result<String, String> {
        let Some(stage) = phase_of(d, text, task) else {
            return Ok(String::new());
        };
        let rel = format!("{}/phases/{stage}.md", rel_of(&self.root, d));
        let template = py_read(&self.root.join(PHASE_TEMPLATE))?;
        let boxes = boxes_in(&template);
        if !self.root.join(&rel).is_file() {
            return Ok(format!("phase {stage}: no checklist at {rel} - copy {PHASE_TEMPLATE} there and tick each box with its evidence"));
        }
        let have = boxes_in(&py_read(&self.root.join(&rel))?);
        for (_, b) in &boxes {
            // `dict((b, t) for t, b in ...)`: the last of a box's lines decides
            match have.iter().rev().find(|(_, hb)| hb == b) {
                None => return Ok(format!("phase {stage}: {rel} lacks the box `{b}` - every one of the template's eight boxes is owed")),
                Some((t, _)) if t == " " => return Ok(format!("phase {stage}: {rel} has `{b}` unticked - each box is ticked, with its evidence, before the phase lands")),
                Some(_) => {}
            }
        }
        Ok(String::new())
    }

    /// A RUST STAGE LANDS WITH NO OPEN CLAIM (feature 444 FR-021, amendment 6, the GM 2026-10-31: "every Rust stage end its initial
    /// implementation with zero open claims"): a phase task's landing is refused while `make claims-report` lists an open finding in the
    /// stage's own code - its Rust the delta changes, a Python unit the delta adds or changes, a Python unit its seam reads at run time
    /// (`claims_scope`, FR-021 as amended 2026-11-01). '' otherwise. (`land.py`'s `file_left` branch, which filed the other findings to
    /// the open-claims feature, had no caller that set it, so it is not ported.)
    fn open_claims_refusal(&self, d: &Path, text: &str, task: &str) -> Result<String, String> {
        let Some(stage) = phase_of(d, text, task) else {
            return Ok(String::new());
        };
        let changed: Vec<String> = self
            .delta_names()?
            .into_iter()
            .filter(|n| n.starts_with("rust/") || n.starts_with("l7r/"))
            .collect();
        if changed.is_empty() {
            return Ok(String::new());
        }
        let seam: Vec<String> = stage_seam(&self.root, &stage)?
            .iter()
            .map(|p| p.to_string_lossy().into_owned())
            .collect();
        let out = self.claims(&["report"]).1;
        let (own, _left) = self.inproc.scope_split(&self.root, &out, &changed, &seam)?;
        if own.is_empty() {
            return Ok(String::new());
        }
        let mut shown: String = own
            .iter()
            .take(5)
            .map(|l| head(l, 140))
            .collect::<Vec<_>>()
            .join("; ");
        if own.len() > 5 {
            let _ = write!(shown, " and {} more", own.len() - 5);
        }
        Ok(format!("{task} is a Rust stage's landing with {} open claim finding(s) in its own code - close each (fix the code or the claim, then re-check it) before it lands (FR-021): {shown}", own.len()))
    }
}

/// The lines of a refusal worth showing: each stripped, the empty and the "pre-existing" ones dropped, joined by " | ".
pub(super) fn kept_lines(out: &str) -> String {
    splitlines(out)
        .into_iter()
        .map(strip)
        .filter(|l| !l.is_empty() && !l.contains("pre-existing"))
        .collect::<Vec<_>>()
        .join(" | ")
}

/// The stage a feature-444 phase task names (`phase: <stage>` in its lines), or None.
fn phase_of(d: &Path, text: &str, task: &str) -> Option<String> {
    if !name_of(d).starts_with("444-") {
        return None;
    }
    let block = task_block(text, task);
    PHASE
        .captures(&block)
        .ok()
        .flatten()
        .map(|m| m[1].to_owned())
}

/// The lines of `task` in a tasks.md: its box line and what follows it, up to the next task's box.
fn task_block(text: &str, task: &str) -> String {
    let pattern = format!(
        r"(?ms)^- \[[ xX]\] {}\b.*?(?=^- \[|\z)",
        fancy_regex::escape(task)
    );
    Regex::new(&pattern)
        .ok()
        .and_then(|r| r.find(text).ok().flatten())
        .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// `_BOX.findall`: (tick, box) of every box line.
fn boxes_in(text: &str) -> Vec<(String, String)> {
    BOX.captures_iter(text)
        .flatten()
        .map(|m| (m[1].to_owned(), m[2].to_owned()))
        .collect()
}

/// The Python files that define `stage_<phase>` - the seam whose imports the Rust stage runs on: every `l7r/**/*.py`, in path order.
fn stage_seam(root: &Path, phase: &str) -> Result<Vec<PathBuf>, String> {
    let pat = re(&format!(r"(?m)^def stage_{}\(", fancy_regex::escape(phase)));
    let mut files = Vec::new();
    walk_py(&root.join("l7r"), &mut files);
    files.sort_by(|a, b| a.components().cmp(b.components()));
    let mut out = Vec::new();
    for p in files {
        if pat.is_match(&py_read(&p)?).unwrap_or(false) {
            out.push(p);
        }
    }
    Ok(out)
}

/// Every `*.py` under `dir` (`rglob`), symlinked directories not followed.
fn walk_py(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        let real_dir = entry.file_type().is_ok_and(|t| t.is_dir());
        if real_dir {
            walk_py(&path, out);
        } else if path.extension().is_some_and(|e| e == "py") && path.is_file() {
            out.push(path);
        }
    }
}

#[cfg(test)]
mod tests;
