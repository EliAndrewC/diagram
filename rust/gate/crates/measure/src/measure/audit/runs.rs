//! The cohort crate's test runs, by time, from every clone's event log (feature 451 T468): the signal from outside a guard row that
//! tells the cohort push tests' `sync-with-main` `closing-owes` rows from a real refusal's, which no field or content does (451 T444).
//!
//! WHY: until 451 T143 landed (2026-11-27T06:41Z) two tests of `rust/gate/crates/cohort` (`push/tests.rs`) wrote a `closing-owes` row
//! into the live guard log each run, byte for byte a real refusal's. Each test or coverage run of that crate writes a `Phase` line
//! (451 T05) with its span, so a row written inside one is the run's. Measured 2026-11-27 over a copy of `~/.claude/guard-log` (1,017
//! `closing-owes` rows) and every clone's `.git/l7r-events/`: of the 361 rows from the logs' first `Phase` line (2026-11-20T11:57Z) on,
//! 359 stand inside a cohort `test` or `cover-run` span, whole seconds; those spans cover 0.25% of that wall time, and 348 of the 354
//! before T143 hold a row; one of the other two stands inside a landing's refused push. The 656 rows before the first `Phase` line have
//! no span to stand in, so they cannot be told. Label: CONVENTION - a signal over a closed set of rows, bounded by `FIXTURES_END`.

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use l7r_gate_core::codeid::common_git_dir;
use serde_json::Value;

/// After 451 T143's landing no test writes the live guard log (`31c827d6ff`, landed 2026-11-27T06:41Z; the copy's last `closing-owes`
/// row 06:32:57Z), so a row after it is a real refusal's wherever it stands: the rule is closed at its end, never left to drop one.
pub(super) const FIXTURES_END: &str = "2026-11-27T06:41:00";

/// The event logs' first `Phase` line and the cohort crate's test runs, each `(start, end)` to the whole second.
#[derive(Default)]
pub(super) struct Runs {
    pub(super) first: Option<String>,
    spans: Vec<(String, String)>,
}

/// The event-log directory of `base`'s repository, where it has one.
fn events_dir(base: &Path) -> Option<PathBuf> {
    Some(common_git_dir(base)?.join("l7r-events")).filter(|d| d.is_dir())
}

/// A time to the whole second, as a guard row's `utc` is written (`2026-11-22T10:00:00Z`): its first 19 characters.
fn second(t: &str) -> &str {
    t.get(..19).unwrap_or(t)
}

impl Runs {
    /// Read from the event logs of `cwd`'s repository and of each clone under `clones`, each log once.
    pub(super) fn read(cwd: &Path, clones: &Path) -> Self {
        let mut bases = vec![cwd.to_path_buf()];
        let mut under: Vec<PathBuf> = std::fs::read_dir(clones)
            .map(|rd| rd.filter_map(Result::ok).map(|e| e.path()).collect())
            .unwrap_or_default();
        under.sort();
        bases.extend(under);
        let mut seen: HashSet<PathBuf> = HashSet::new();
        let mut runs = Self::default();
        for dir in bases.iter().filter_map(|b| events_dir(b)) {
            if !seen.insert(std::fs::canonicalize(&dir).unwrap_or_default()) {
                continue;
            }
            for name in super::super::events::names(&dir) {
                if Path::new(&name).extension().is_some_and(|x| x == "jsonl") {
                    runs.add(&std::fs::read_to_string(dir.join(name)).unwrap_or_default());
                }
            }
        }
        runs
    }

    /// The `Phase` lines of one log's text: every one moves `first`; a cohort crate's test or coverage run is a span.
    fn add(&mut self, text: &str) {
        for line in text.lines().filter(|l| l.contains("\"Phase\"")) {
            let Ok(e) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            let at = |k: &str| e.get(k).and_then(Value::as_str).map(second);
            let (Some(t0), Some(t1)) = (at("t0"), at("t1")) else {
                continue;
            };
            if self.first.as_deref().is_none_or(|f| t0 < f) {
                self.first = Some(t0.to_owned());
            }
            let cohort = e.get("crates").and_then(Value::as_array).is_some_and(|cs| {
                cs.iter()
                    .any(|c| c.as_str().is_some_and(|c| c.ends_with("crates/cohort")))
            });
            let step = e.get("step").and_then(Value::as_str);
            if cohort && matches!(step, Some("test" | "cover-run")) {
                self.spans.push((t0.to_owned(), t1.to_owned()));
            }
        }
    }

    /// Whether a row written at `utc` stands inside a cohort crate's test run.
    pub(super) fn holds(&self, utc: &str) -> bool {
        let at = second(utc);
        self.spans
            .iter()
            .any(|(a, b)| a.as_str() <= at && at <= b.as_str())
    }
}
