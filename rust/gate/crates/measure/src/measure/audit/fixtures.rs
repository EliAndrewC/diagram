//! `make audit`'s guard firings less the test fixtures' rows already on the live guard log (feature 451 T444).
//!
//! WHY: until 451 T143 three crates' tests wrote rows into `~/.claude/guard-log`, and those rows remain. No field marks one - its
//! session is `unknown` and its `cwd` and `transcript` empty, as every row a gate tool writes outside a hook - so only content
//! tells a class apart, measured 2026-11-27 over a copy of the live log (127,416 rows): `checks` `check-closed` rows whose reason
//! is the tests' "nothing to close here" (2,230 of 2,234; the other four carry a session's own reason), and `plan-gate` and
//! `task-add` rows naming a feature with no `specs/` directory (`449-x`, `600-x`, `444-x`: 982 blocked and 15 escaped, the 15
//! carrying a session's exported `PLAN_REVIEW_OK` into the fixture; `9001-x`: 9). With them the plan gate read 48% escaped; without,
//! 69% (1,560 of 2,262). Label: CONVENTION - a content rule over a closed set of rows, which 451 T143's fix stopped adding to.
//!
//! What a real firing could match: a session closing checks with the reason "nothing to close here" word for word, and a plan-gate
//! or task-add row of a feature whose `specs/` directory the reading tree lacks (a clone behind main) - so the left-out line names
//! each slug with its count, and a tree with no `specs/` directory at all leaves out none of those. The `sync-with-main`
//! `closing-owes` rows (1,017 on the same copy) are a real refusal's byte for byte, so a signal from outside the row tells them (451
//! T468, `runs.rs`): one inside a cohort crate's test run is left out; one before the event logs' first `Phase` line cannot be told,
//! stays counted and makes the guard's escape rate unknown; any other, and any after `FIXTURES_END`, is a real refusal's.

use std::path::Path;

use serde_json::Value;

use super::runs::{Runs, FIXTURES_END};

/// The detail the tests close their checks with.
const CLOSED: &str = "nothing to close here";

/// What the left-out rows were, for the line that says so.
#[derive(Default)]
pub(super) struct LeftOut {
    closed: usize,
    plan: Vec<(String, usize)>,
    task: Vec<(String, usize)>,
    /// The cohort crate's test runs, the signal for the `closing-owes` rows (451 T468).
    runs: Runs,
    /// `closing-owes` rows inside one of those runs, left out.
    in_run: usize,
    /// `closing-owes` rows before the event logs' first `Phase` line, counted, which no signal tells apart.
    untold: usize,
}

/// The guard whose `closing-owes` rows only a signal from outside the row tells apart.
pub(super) const SYNC: &str = "sync-with-main";

/// `<digits>-<slug>`, a feature directory's name.
fn feature_like(name: &str) -> bool {
    let Some((number, slug)) = name.split_once('-') else {
        return false;
    };
    !number.is_empty()
        && number.bytes().all(|b| b.is_ascii_digit())
        && !slug.is_empty()
        && slug
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
}

/// The feature a gate row names where it writes one: the plan gate's `<feature>: ...` or `specs/<feature>`, the task-add's
/// `<feature> T<n>: ...`.
fn named(guard: &str, detail: &str) -> Option<String> {
    let name = match guard {
        "plan-gate" => detail
            .strip_prefix("specs/")
            .filter(|rest| !rest.contains(' '))
            .or_else(|| detail.split_once(": ").map(|(head, _)| head))?,
        "task-add" => detail.split_once(' ').map(|(head, _)| head)?,
        _ => return None,
    };
    feature_like(name).then(|| name.to_owned())
}

fn tally(slugs: &mut Vec<(String, usize)>, slug: String) {
    if let Some(at) = slugs.iter().position(|(s, _)| *s == slug) {
        slugs[at].1 += 1;
    } else {
        slugs.push((slug, 1));
    }
}

impl LeftOut {
    /// Nothing left out yet; `runs` the cohort crate's test runs the event logs hold.
    pub(super) fn new(runs: Runs) -> Self {
        Self {
            runs,
            ..Self::default()
        }
    }

    /// Whether `guard`'s escape rate rests on rows no signal tells apart (451 T468).
    pub(super) fn untold(&self, guard: &str) -> bool {
        guard == SYNC && self.untold > 0
    }

    /// Whether a `closing-owes` row written at `utc` is a fixture's (a cohort test run holds it), tallying one no signal tells.
    fn closing(&mut self, utc: &str) -> bool {
        if utc >= FIXTURES_END {
            return false;
        }
        if self.runs.holds(utc) {
            self.in_run += 1;
            return true;
        }
        if self.runs.first.as_deref().is_none_or(|f| utc < f) {
            self.untold += 1;
        }
        false
    }

    /// Whether `row` is a fixture's (and so tallied here); `specs` the reading tree's `specs/` directory.
    pub(super) fn take(&mut self, row: &Value, specs: &Path) -> bool {
        let text = |k: &str| row.get(k).and_then(Value::as_str).unwrap_or_default();
        let (guard, detail) = (text("guard"), text("detail"));
        if guard == "checks" && text("rule") == "check-closed" && detail == CLOSED {
            self.closed += 1;
            return true;
        }
        if guard == SYNC && text("rule") == "closing-owes" {
            return self.closing(text("utc"));
        }
        let Some(slug) = named(guard, detail) else {
            return false;
        };
        if !specs.is_dir() || specs.join(&slug).is_dir() {
            return false;
        }
        tally(
            if guard == "plan-gate" {
                &mut self.plan
            } else {
                &mut self.task
            },
            slug,
        );
        true
    }

    /// The lines that say what was left out, none where nothing was.
    pub(super) fn lines(&self) -> Vec<String> {
        let sum = |slugs: &[(String, usize)]| slugs.iter().map(|(_, n)| n).sum::<usize>();
        let total = self.closed + sum(&self.plan) + sum(&self.task) + self.in_run;
        let mut out = Vec::new();
        let mut parts = Vec::new();
        if self.closed > 0 {
            parts.push(format!("checks check-closed \"{CLOSED}\" {}", self.closed));
        }
        for (guard, slugs) in [("plan-gate", &self.plan), ("task-add", &self.task)] {
            if slugs.is_empty() {
                continue;
            }
            let mut by = slugs.clone();
            by.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
            let each: Vec<String> = by.iter().map(|(s, n)| format!("{s} {n}")).collect();
            parts.push(format!(
                "{guard} naming a feature with no specs/ directory {} ({})",
                sum(slugs),
                each.join(", ")
            ));
        }
        if self.in_run > 0 {
            parts.push(format!(
                "{SYNC} closing-owes inside a cohort crate's test run {}",
                self.in_run
            ));
        }
        if total > 0 {
            out.push(format!(
                "  left out, as test fixtures' rows (451 T444, T468): {total} - {}",
                parts.join("; ")
            ));
        }
        if self.untold > 0 {
            out.push(format!(
                "  cannot tell (451 T468): {SYNC} closing-owes {} {} - a fixture's row is a real refusal's byte for byte, so its escape rate is unknown",
                self.untold,
                self.runs.first.as_ref().map_or_else(
                    || "with no event log's Phase line to read".to_owned(),
                    |f| format!("before the event logs' first Phase line, {f}Z, with no test run to stand in")
                )
            ));
        }
        out
    }
}
