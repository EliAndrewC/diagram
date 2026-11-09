//! The dispatch decision: every condition, evaluated and reported even after one fails, so a session sees the whole picture in one turn (from `ci/decision.py`). Order: route, feature-complete (merge only), green-local-since-edit,
//! tree-not-already-verified, breaker, the last because it alone costs an AWS call. The verdict is the first failing condition, or SKIP-VERIFIED, or DISPATCH.

use std::fmt::Write as _;

use super::config;
use super::features::FeatureStatus;
use crate::delta::Delta;
use crate::state::State;

pub(crate) const MERGE: &str = "merge";
pub(crate) const CHECK: &str = "check";
/// A third mode rather than a flag on `check`, because it needs a buildspec of its own that writes no verified record and never pushes (feature 177).
pub(crate) const MEASURE: &str = "measure";

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Condition {
    pub name: &'static str,
    pub passed: bool,
    pub why: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct VerifiedRecord {
    pub tree: String,
    pub build_id: String,
    pub scope: String,
    pub utc: String,
}

impl VerifiedRecord {
    /// A `reference` record does not satisfy a full merge; a `full` record satisfies either (FR-027).
    fn satisfies(&self, scope: &str) -> bool {
        self.scope == "full" || scope == "reference"
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct Estimate {
    pub minutes: f64,
    pub cost_usd: f64,
    pub month_to_date_usd: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct Decision {
    pub conditions: Vec<Condition>,
    pub estimate: Estimate,
    pub verdict: String,
}

impl Decision {
    pub(crate) fn dispatches(&self) -> bool {
        self.verdict == "DISPATCH"
    }

    pub(crate) fn skip_verified(&self) -> bool {
        self.verdict == "SKIP-VERIFIED"
    }
}

fn cents(value: f64) -> f64 {
    (value * 100.0).round() / 100.0
}

pub(crate) fn estimate(scope: &str, month_to_date_usd: f64, operation: Option<&str>) -> Estimate {
    let minutes = config::estimate_minutes(if operation.is_some() {
        "operation"
    } else {
        scope
    });
    Estimate {
        minutes,
        cost_usd: cents(minutes * config::RATE_PER_MIN),
        month_to_date_usd: cents(month_to_date_usd),
    }
}

/// Everything a decision weighs; only `decide` reads it.
pub(crate) struct Inputs<'a> {
    pub delta: &'a Delta,
    pub state: Option<&'a State>,
    pub now_hash: &'a str,
    pub verified: Option<VerifiedRecord>,
    pub breaker: Option<&'a str>,
    pub mode: &'a str,
    pub feature: Option<&'a FeatureStatus>,
    pub scope: &'a str,
    pub month_to_date_usd: f64,
    pub operation: Option<&'a str>,
    pub remote_off: Option<&'a str>,
    pub measure: bool,
}

fn green_since_edit(state: Option<&State>, now_hash: &str) -> Condition {
    let (passed, why) = match state {
        None => (false, "no local check recorded - run `make quick` (or reference / test-file / a local done) first".to_owned()),
        Some(s) if s.event != "green-local" => (false, format!("the last gate FAILED (`make {}` at {}) - run `make quick` (or reference / test-file) green before dispatching again", s.target, s.utc)),
        Some(s) if s.hash != now_hash => (false, format!("`make {}` was green at {}, but the code changed since - that run vouched for different code; run `make quick` again", s.target, s.utc)),
        Some(s) => (true, format!("`make {}` green at {} against exactly this code", s.target, s.utc)),
    };
    Condition {
        name: "green-local-since-edit",
        passed,
        why,
    }
}

fn not_verified(verified: Option<&VerifiedRecord>, scope: &str) -> Condition {
    let (passed, why) = match verified {
        Some(v) if v.satisfies(scope) => {
            let who = if v.build_id.starts_with("local:") {
                "a green local `make done` on exactly this engine content (main adds none)"
                    .to_owned()
            } else {
                v.build_id.clone()
            };
            (false, format!("this engine content was verified {}-scope by {who} - no second build (SKIP-VERIFIED)", v.scope))
        }
        Some(v) => (
            true,
            format!(
                "verified only at {} scope by {}; a {scope} run is still owed",
                v.scope, v.build_id
            ),
        ),
        None => (
            true,
            "no verified record for the tree this would land".to_owned(),
        ),
    };
    Condition {
        name: "tree-not-already-verified",
        passed,
        why,
    }
}

pub(crate) fn decide(i: Inputs<'_>) -> Decision {
    let mut conds = vec![Condition {
        name: "remote-enabled",
        passed: i.remote_off.is_none(),
        why: i
            .remote_off
            .unwrap_or("remote is on (dev/switches.json)")
            .to_owned(),
    }];
    // the measurement route bypasses this condition and only this one (feature 177 FR-009a), and the row is still printed
    let reason = i.delta.reason();
    conds.push(Condition {
        name: "route-is-gated",
        passed: i.delta.route() == "GATED" || i.measure,
        why: if i.measure {
            format!("{reason} - BYPASSED: a measurement has no engine delta to point at (FR-009a)")
        } else {
            reason
        },
    });
    if i.mode == MERGE {
        let none = FeatureStatus::default();
        let f = i.feature.unwrap_or(&none);
        conds.push(Condition {
            name: "feature-complete",
            passed: f.complete(),
            why: f.why(),
        });
    }
    conds.push(green_since_edit(i.state, i.now_hash));
    // a verified record says a gate passed on this tree; it says nothing about a cohort, a cache audit or what a run cost
    let verified = i.verified.filter(|_| i.operation.is_none() && !i.measure);
    conds.push(not_verified(verified.as_ref(), i.scope));
    conds.push(Condition {
        name: "breaker-not-tripped",
        passed: i.breaker.is_none(),
        why: i
            .breaker
            .unwrap_or("the monthly hard stop has not tripped")
            .to_owned(),
    });

    let failing = conds
        .iter()
        .find(|c| !c.passed && c.name != "tree-not-already-verified" && c.name != "remote-enabled");
    let verdict = match failing {
        Some(c) => format!("REFUSE({})", c.name),
        None if verified.as_ref().is_some_and(|v| v.satisfies(i.scope)) => {
            "SKIP-VERIFIED".to_owned()
        }
        None if i.remote_off.is_some() => "REFUSE(remote-enabled)".to_owned(),
        None => "DISPATCH".to_owned(),
    };
    Decision {
        conditions: conds,
        estimate: estimate(i.scope, i.month_to_date_usd, i.operation),
        verdict,
    }
}

/// The whole picture, before a cent is spent (FR-014).
pub(crate) fn render(d: &Decision, mode: &str, scope: &str) -> String {
    let mut out = format!("ci-{mode} ({scope} scope) - dispatch conditions:");
    for c in &d.conditions {
        let _ = write!(
            out,
            "\n  [{}] {:<26} {}",
            if c.passed { "ok" } else { "--" },
            c.name,
            c.why
        );
    }
    let e = &d.estimate;
    let _ = write!(out, "\n  estimate: ~{:.0} build-min at ${:.2}/min = ~${:.2}; month-to-date remote spend ${:.2}\n  verdict: {}", e.minutes, config::RATE_PER_MIN, e.cost_usd, e.month_to_date_usd, d.verdict);
    out
}

#[cfg(test)]
mod tests;
