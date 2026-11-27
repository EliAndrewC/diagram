//! Pass 1: every refusal the landing would meet that costs seconds to ask, all of them (`land.py`'s `cheap_refusals` and what it calls) -
//! and the records the landing writes for itself on the way: the ledger rows, the make-targets page, the claims' moved rows, the carries,
//! the known drifts and its own escape records.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::py_text::strip;
use l7r_shared::speckit::splitlines;

use super::{head, name_of, py_read, rel_of, tail, Land};
use crate::Reply;

const PHASE_TEMPLATE: &str = ".specify/templates/phase-checklist.md";
static PHASE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\s*phase:\s*([a-z_]+)\s*$"));
static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[([ xX])\] (\d\. \*\*[^*]+\*\*)"));
static FILED_INTO: LazyLock<Regex> = LazyLock::new(|| re(r"filed into (\S+) T\d+"));

fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A reply as `run` read a command's: its code, its stdout then its stderr.
fn said(r: Reply) -> (i32, String) {
    (r.code, r.stdout + &r.stderr)
}

/// The gates the first pass asks, in its order: the push's own, the record gate among them since 451 T307 part 2 (the push ran
/// `entry-gate.sh` beside the claims gate and the first pass never asked it).
const GATES: [&str; 4] = [
    "claims-gate.sh",
    "review-gate.sh",
    "plan-gate.sh",
    "entry-gate.sh",
];

/// The gates of [`GATES`] that take a range as their first argument (`origin/main...HEAD` unset), given the hand-in base at hand-in.
const RANGED: [&str; 2] = ["review-gate.sh", "plan-gate.sh"];

/// The first pass's two modes (461 T06, D4): the landing's, and the hand-in's in a builder's tree, whose delta is the working tree
/// against `base` (the hand-in base: the clone's HEAD in phase 1, `origin/main` from phase 2, D3), whose records are written into the
/// tree uncommitted, and which asks what the builder can answer - each task's tick check, the phase checklist, open claims, the named
/// files, the stale coverage-exempt entry, the ledger rows owed, the four gates and the push's table - and not what is the lane's:
/// another writer's changes, the mark's hold, the red-gate tripwire (the gate's stamp rows are the landing's skip in both). No
/// coverage runs in either (FR-002).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Pass {
    /// `make land`'s first pass.
    Landing,
    /// The hand-in's, over a tree applied onto `base` and not yet committed.
    HandIn {
        /// The commit the work was applied onto.
        base: String,
    },
}

/// The rows of the push's table (`cohort`'s `push::CHECKS`) the first pass cannot ask before its gate: the green-gate stamp, which
/// the gate itself writes (and the landing's second pass reads, `long_runs`).
pub(super) const AFTER_GATE: [&str; 2] = ["gate-stamp selftest", "gate-stamp"];
/// ...and the row it asks in its own form, naming the tasks it lands as the push will find them ticked (`--landing --tasks`).
pub(super) const OWN_FORM: [&str; 1] = ["ledger-owed"];

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
    pub(super) fn write_ledger(&self, d: &Path, tasks: &[String]) -> Result<(), String> {
        let ledger = self.root.join("dev/review-ledger.md");
        let ledger = ledger.to_string_lossy();
        // its own tasks' plan reviews are this landing's to write, open as they still are before the tick; every other open task's
        // is left to that task's landing (451 T231, `reviews`' `ledger_passes/left.rs`)
        let (feature, ticks) = (name_of(d), tasks.join(" "));
        self.ledger(&[
            "--write-plan-reviews",
            "--ledger",
            &ledger,
            "--landing",
            &feature,
            "--tasks",
            &ticks,
        ]);
        let at = format!(
            "specs/{}/ (the records its checks wrote; make land)",
            name_of(d)
        );
        // ...and of the passes traced to the feature, its own tasks' and no other open task's (451 T305, `left.rs`)
        self.ledger(&[
            "--write",
            &at,
            "--ledger",
            &ledger,
            "--landing",
            &feature,
            "--tasks",
            &ticks,
        ]);
        if !self.dirty(&["dev/review-ledger.md"])?.is_empty() {
            self.record_commit(&[
                "git",
                "commit",
                "-q",
                "-m",
                "the review passes' ledger rows, written at landing (make land)",
                "--",
                "dev/review-ledger.md",
            ])?;
        }
        Ok(())
    }

    /// The ledger rows the landing still owes after its write, as the push's ledger row asks: '' where none, else the refusal naming
    /// `make ledger-owed WRITE=`. Asked in the first pass and again after the claims wait's write (451 T413). The landing owes the rows
    /// of its own tasks' passes and every pass no other landing writes; another open task's plan review is left to that task's landing
    /// (451 T147, `reviews`' `ledger_passes/left.rs`), as the push's `--refuse` leaves it once the landing's tasks are ticked.
    pub(super) fn ledger_refusal(&self, d: &Path, tasks: &[String]) -> String {
        let ledger = self.root.join("dev/review-ledger.md");
        let (name, ticks, at) = (name_of(d), tasks.join(" "), ledger.to_string_lossy());
        let asked = [
            "--ledger",
            &at,
            "--refuse",
            "--landing",
            &name,
            "--tasks",
            &ticks,
        ];
        let (_rc, owed) = self.ledger(&asked);
        if owed.contains("| ? |") {
            return "review passes with no ledger row - make ledger-owed WRITE=\"<where you recorded what you did>\"".to_owned();
        }
        String::new()
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
            self.record_commit(&["git", "commit", "-q", "-m", &message])?;
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
            self.record_commit(&[
                "git",
                "commit",
                "-q",
                "-m",
                "known drifts recorded for the GM's review (make land, feature 430 T06)",
            ])?;
        }
        Ok(())
    }

    /// `sorted((root / "specs").glob("*/<file>"))`, relative to the root.
    pub(super) fn each_spec(&self, file: &str) -> Vec<String> {
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
    /// In its hand-in mode ([`Pass::HandIn`], 461 T06) it asks what the builder can answer and not what is the lane's (D4).
    pub(super) fn cheap_refusals(
        &self,
        d: &Path,
        tasks: &[String],
        note: &str,
        pass: &Pass,
        deferred: Option<&mut Vec<String>>,
    ) -> Result<Vec<String>, String> {
        let base = match pass {
            Pass::Landing => None,
            Pass::HandIn { base } => Some(base.clone()),
        };
        let prior = self.hand_in.replace(base);
        let out = self.first_pass(d, tasks, note, deferred);
        let hand_in = self.hand_in.replace(prior).is_some();
        // a builder runs `make builder-done` again, never `make land` (each cure's last words)
        Ok(out?
            .into_iter()
            .map(|s| {
                if hand_in {
                    s.replace("run make land again", "run make builder-done again")
                } else {
                    s
                }
            })
            .collect())
    }

    fn first_pass(
        &self,
        d: &Path,
        tasks: &[String],
        note: &str,
        deferred: Option<&mut Vec<String>>,
    ) -> Result<Vec<String>, String> {
        let base = self.hand_in.borrow().clone();
        // A CLONE ON A HISTORY MAIN NO LONGER SHARES (the push's `refuse_unrelated_history`, 451 T413, [`super::parity`]): said alone,
        // before the pass commits anything - every other answer reads a delta that has no merge base, and the cure is a re-clone
        let unrelated = self.unrelated_history()?;
        if !unrelated.is_empty() {
            return Ok(vec![unrelated]);
        }
        let text = py_read(&d.join("tasks.md"))?;
        // one refusal shared by several tasks (an hour's step-back) is printed once, naming them all
        let mut by_why: Vec<(String, Vec<String>)> = Vec::new();
        let mut add = |why: String, task: &str| match by_why.iter_mut().find(|(w, _)| *w == why) {
            Some((_, ts)) => ts.push(task.to_owned()),
            None => by_why.push((why, vec![task.to_owned()])),
        };
        // the landing tree's HEAD, read once for every task's named files (451 T294, [`super::named`])
        let held = self.held()?;
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
            // each said, as T20 D2 has it - and a file its own words name that HEAD lacks, its code not carried (451 T294)
            for why in [
                self.phase_refusal(d, &text, task)?,
                self.open_claims_refusal(d, &text, task)?,
                super::named::refused(d, &text, task, &held),
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
        self.records_on_the_way(d, tasks)?;
        let stale = self.stale_exempt_refusal()?;
        if !stale.is_empty() {
            stops.push(stale);
        }
        // ANOTHER WRITER'S CHANGES, NAMED (451 T242), with an open builder handoff naming the clone; asked again before the ticks -
        // but not at hand-in, where the tree is the builder's own (461 D4's right column, as the mark's hold and the tripwire below)
        if base.is_none() {
            let writer = self.writer_refusal(tasks)?;
            if !writer.is_empty() {
                stops.push(writer);
            }
        }
        let owed = self.ledger_refusal(d, tasks);
        if !owed.is_empty() {
            stops.push(owed);
        }
        // the mark's task holds, unless each task landed is ready beside it (451 T101, `ready.rs`); at hand-in the lane's ordering
        let held = if base.is_none() {
            self.hold(d, tasks)?
        } else {
            String::new()
        };
        if !held.is_empty() {
            stops.push(format!("held by {held}"));
        }
        // ...and, as the push asks, every other spec directory the delta touches and the feature pointer (451 T413, `parity.rs`)
        stops.extend(self.others_in_progress(d)?);
        let ticks = tasks.join(" ");
        // A RED-GATE TRIPWIRE HOLDS THE LANDING'S GATE (feature 405 T44, D18): asked here with the others, on a landing that runs one
        if base.is_none() && !self.arbiter_ok && self.engine_delta()? {
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
        self.gate_refusals(base.as_deref(), &ticks, deferred, &mut stops)?;
        let pushed = self.push_refusal(d, &ticks)?;
        if !pushed.is_empty() {
            stops.push(pushed);
        }
        Ok(stops)
    }

    /// The four gates of the first pass, each refusal a stop - but the claims gate's that a round in flight may answer, which goes to
    /// `deferred` (and at hand-in, with none given, is the lane's and quiet).
    fn gate_refusals(
        &self,
        base: Option<&str>,
        ticks: &str,
        mut deferred: Option<&mut Vec<String>>,
        stops: &mut Vec<String>,
    ) -> Result<(), String> {
        for gate in GATES {
            let path = self.script(&format!("gates/{gate}"));
            let mut cmd = vec![path.as_str()];
            // the two gates that take a range read the hand-in's: the working tree against its base (461 D4)
            if let Some(base) = base.filter(|_| RANGED.contains(&gate)) {
                cmd.push(base);
            }
            let (rc, out) = self.run(&cmd, &[("L7R_LAND_TICKS", ticks)])?;
            if rc == 0 {
                continue;
            }
            let said = format!("{gate}: {}", tail(&kept_lines(&out), 600));
            // ...BUT A CLAIMS REFUSAL NO WAIT CAN CURE IS A STOP NOW (feature 440 T01, the GM 2026-10-27): an owed claim with no check
            // in flight, or an introduced finding, cannot be answered while the gate runs - feature 438's landing ran its whole gate
            // (about 19 min) and then refused on a claim never dispatched
            // ...and at hand-in only an owed claim with a round in flight is the lane's to wait on (D4): said to `deferred` if given,
            // else quiet; any other claims refusal is the builder's
            let (to_defer, why) =
                if gate == "claims-gate.sh" && (deferred.is_some() || base.is_some()) {
                    let flight = self.in_flight()?;
                    let (wait, why) = super::claims_wait::claims_route(&out, &said, &flight);
                    let lane_s = !flight.is_empty() && out.contains("owed (");
                    (wait && (base.is_none() || lane_s), why)
                } else {
                    (false, said)
                };
            match deferred.as_deref_mut() {
                Some(later) if to_defer => later.push(why),
                _ if to_defer => {}
                _ => stops.push(why),
            }
        }
        Ok(())
    }

    /// THE PUSH'S OWN TABLE, ASKED BEFORE THE GATE (451 T307 part 2). WHY: the push ran `l7r-gate push-checks` after the landing's
    /// gate, and the first pass asked two of its 26 rows (the ledger's and the make-targets page's), so a file past the line bar, a
    /// research pointer, a spec-lint finding or an unresolved conflict was a refusal met after a whole gate run. One call of the same
    /// table, every refusing row said (`--every`), so a row added to the push is asked here by construction; skipped are the rows
    /// that cannot precede the gate ([`AFTER_GATE`]), the row asked above in the landing's form ([`OWN_FORM`]) and, as the push
    /// skips it, the closing row under a `CLOSE_OK` that states a reason. Run with what the push is told: the tasks and the feature.
    fn push_refusal(&self, d: &Path, ticks: &str) -> Result<String, String> {
        let (gate, root) = (self.gate(), self.root.to_string_lossy().into_owned());
        let mut cmd = vec![gate.as_str(), "push-checks", root.as_str(), "--every"];
        for row in AFTER_GATE.iter().chain(&OWN_FORM) {
            cmd.extend(["--skip", row]);
        }
        if l7r_shared::escape::enough(strip(&self.root.var("CLOSE_OK"))) {
            cmd.extend(["--skip", "closing"]);
        }
        let told = [("L7R_LAND_TICKS", ticks), ("SPECIFY_FEATURE", &name_of(d))];
        let (rc, out) = self.run(&cmd, &told)?;
        if rc == 0 {
            return Ok(String::new());
        }
        Ok(format!("push-checks: {}", every_row_said(&out)))
    }

    /// The records the first pass writes and commits for itself: the ledger, the make-targets page, the claims' moved rows, the
    /// carries, the known drifts and its own escape records.
    fn records_on_the_way(&self, d: &Path, tasks: &[String]) -> Result<(), String> {
        self.write_ledger(d, tasks)?;
        // ...and the make-targets page, regenerated where the Makefile moved (feature 405 T46, D19): the push's `make-docs` check
        // refused T43's landing after its hooks-test, for a page `make docs` writes in a second
        // asked in process (feature 449 T135, where it ran `scripts/make-docs.py`): a failed write is passed over as the command's
        // exit was, and the commit below then finds nothing to take
        if l7r_gate_cohort::make_docs::check(&self.root).code != 0 {
            let _ = l7r_gate_cohort::make_docs::write(&self.root);
            self.record_commit(&[
                "git",
                "commit",
                "-q",
                "-m",
                "docs/make-targets.html regenerated at landing (make land, 405 T46)",
                "--",
                "docs/make-targets.html",
            ])?;
        }
        // A MOVED UNIT KEEPS ITS CLAIMS' ROWS (405 T58): a file split into a package at the 1,000-line bar re-keys them, owing nothing;
        // and a PORTED one (feature 449 T166, Q10): the rows carried onto the port the map names, the deferred list re-keyed with them
        self.claims(&["rekey"]);
        // both files asked of one `git status`, each moved where a line names it, as its own status would have listed it (feature 449
        // T167: a git process fewer a landing)
        let paths = ["dev/claims-index.json", "dev/claims-deferred.json"];
        // unstripped, so each line keeps its two status columns
        let status = self
            .run(
                &["git", "status", "--porcelain", "--", paths[0], paths[1]],
                &[],
            )?
            .1;
        let moved: Vec<&str> = paths
            .into_iter()
            .filter(|path| {
                status.lines().any(|line| {
                    line.get(3..)
                        .is_some_and(|named| named.split(" -> ").any(|p| p == *path))
                })
            })
            .collect();
        if !moved.is_empty() {
            let mut cmd = vec![
                "git",
                "commit",
                "-q",
                "-m",
                "claim rows carried to the files their units moved to, or to their ports (make land, 405 T58, 449 T166)",
                "--",
            ];
            cmd.extend(moved);
            self.record_commit(&cmd)?;
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
        if phase_of(d, text, task).is_none() {
            return Ok(String::new());
        }
        let changed: Vec<String> = self
            .delta_names()?
            .into_iter()
            .filter(|n| n.starts_with("rust/") || n.starts_with("l7r/"))
            .collect();
        if changed.is_empty() {
            return Ok(String::new());
        }
        // no seam: it was the `l7r/**/*.py` files defining `stage_<phase>`, and feature 449 T247 found none left (T158 deleted the
        // engine's Python), so its walk was deleted
        let out = self.claims(&["report"]).1;
        let (own, _left) = self.inproc.scope_split(&self.root, &out, &changed, &[])?;
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

/// What `push-checks --every` said, as the first pass shows it: the rows' own output cut to its last 600 characters, then EVERY
/// refusing row's `sync-with-main:` line whole (451 T307 part 2: one tail of the whole output, as a gate's refusal is shown, cut the
/// earliest rows' lines where several refused - the very list `--every` exists to give).
fn every_row_said(out: &str) -> String {
    let (rows, rest): (Vec<&str>, Vec<&str>) = splitlines(out)
        .into_iter()
        .partition(|l| l.starts_with("sync-with-main: "));
    let detail = tail(&kept_lines(&rest.join("\n")), 600);
    let said: Vec<String> = std::iter::once(detail)
        .filter(|d| !d.is_empty())
        .chain(rows.into_iter().map(|r| strip(r).to_owned()))
        .collect();
    said.join(" | ")
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
    l7r_shared::regex::build(&pattern)
        .ok()
        .and_then(|r| r.find(text).ok().flatten())
        .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// `_BOX.findall`: (tick, box) of every box line.
fn boxes_in(text: &str) -> Vec<(String, String)> {
    BOX.captures_iter(text)
        .map_while(Result::ok)
        .map(|m| (m[1].to_owned(), m[2].to_owned()))
        .collect()
}

#[cfg(test)]
mod tests;
