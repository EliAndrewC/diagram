//! The claims round the landing waits for after its gate (405 T50, D23), what waiting cannot cure (feature 426 D1, feature 440 T01), and
//! the gate's own lint, committed while it waited (the GM 2026-10-24), left with ruff (feature 449 T158; its step deleted by T247).

use std::path::Path;

use l7r_shared::py_text::strip;
use l7r_shared::speckit::splitlines;

use super::cheap::kept_lines;
use super::{head, tail, Land};

/// How `claims_cure` opens each refusal that waiting cannot end - so the stop names it as such, not as the wait run out.
const CURE_OPENINGS: [&str; 3] = [
    "claims-gate.sh refuses on a finding no check in flight can cure",
    "claims-gate.sh: a claim is owed a check and none is in flight",
    "claims-gate.sh refuses on a claim whose unit was deleted unported",
];

/// Where a claims refusal met in the preflight goes: `(false, its cure)` - a stop - when no wait can cure it ([`claims_cure`]), else
/// `(true, what it said)`, deferred: the round beside the gate may still answer it (feature 440 T01).
pub(super) fn claims_route(out: &str, said: &str, in_flight: &[String]) -> (bool, String) {
    let cure = claims_cure(out, in_flight);
    if cure.is_empty() {
        (true, said.to_owned())
    } else {
        (false, cure)
    }
}

/// Why a claims refusal cannot end by waiting, with the cure - or "" when a check in flight may still answer it (feature 426 D1). An
/// INTRODUCED finding is never cured by waiting: it needs an edit, or a round arbiter's accept, which the next `make land` reads. An OWED
/// claim waits only while a claims check is in flight (`claims_flight.live`): with none, nothing is coming. Inferring "in flight" from
/// "owed" waited the whole claims wait twice on feature 417 T50's landing.
pub(super) fn claims_cure(out: &str, in_flight: &[String]) -> String {
    let lines: Vec<&str> = splitlines(out)
        .into_iter()
        .map(strip)
        .filter(|l| !l.is_empty() && !l.contains("pre-existing"))
        .collect();
    let introduced: Vec<&str> = lines
        .iter()
        .copied()
        .filter(|l| l.starts_with("introduced:"))
        .collect();
    let owed: Vec<&str> = lines
        .iter()
        .copied()
        .filter(|l| l.contains("owed ("))
        .collect();
    // a claim on a deleted `.py` unit no port carried (feature 449 T166, Q10): only the port map and a rekey cure it, never a check
    let unported: Vec<&str> = lines
        .iter()
        .copied()
        .filter(|l| l.starts_with("unported:"))
        .collect();
    if !unported.is_empty() {
        return format!(
            "{} - {}. Each line names its fix: map the unit in dev/claims-ports.json, or carry its `Research:` line onto its port, then `make claims-rekey` (ask:449-phase4-slices Q10) - then run make land again",
            CURE_OPENINGS[2],
            head(&unported.join(" | "), 600)
        );
    }
    if !introduced.is_empty() {
        let also = if owed.is_empty() {
            String::new()
        } else {
            format!(" (also owed: {})", head(&owed.join(" | "), 300))
        };
        return format!(
            "claims-gate.sh refuses on a finding no check in flight can cure - {}{also}. Fix the code or the claim and re-check it, or, for a known drift filed on an open task, `make arbiter-ask SUBJECT=<id> WHY=\"<the rounds>\" REVIEW=claims:<key>` - then run make land again",
            head(&introduced.join(" | "), 600)
        );
    }
    if !owed.is_empty() && in_flight.is_empty() {
        return format!(
            "claims-gate.sh: a claim is owed a check and none is in flight - {}. Run `make claims-triage` / `make claims-bundle OWED=1`, dispatch the agent on its MANIFEST, record its reply (`make claims-triaged` / `make claims-checked`) - then run make land again",
            head(&owed.join(" | "), 600)
        );
    }
    String::new()
}

/// The landing's stop on the claims round: "refused at once" for a refusal no wait can end ([`claims_cure`]), "did not finish" only for
/// the wait run out - feature 427 T12's landing printed the second for the first, and read as a 20-minute wait.
pub(super) fn claims_stop_line(why: &str) -> String {
    if CURE_OPENINGS.iter().any(|o| why.starts_with(o)) {
        return format!("land: the gates are green, but the claims round refuses and waiting cannot cure it - nothing landed: {why}");
    }
    format!(
        "land: the gates are green, but the claims round did not finish in {:.0} min - nothing landed: {why}",
        super::CLAIMS_WAIT_S / 60.0
    )
}

impl Land {
    /// The claims checks in flight (`claims_flight.live`), in process (`ask:449-T83-scope`).
    pub(super) fn in_flight(&self) -> Result<Vec<String>, String> {
        self.inproc.in_flight(&self.root)
    }

    /// The claims gate passing and the tree clean - the claims round recorded and committed beside the gate - or the refusal that still
    /// stands: at once when nothing waiting could cure it ([`claims_cure`], feature 426 D1), else past the wait's bound (405 T50, D23).
    pub(super) fn wait_for_claims(
        &self,
        tasks: &[String],
        d: Option<&Path>,
    ) -> Result<String, String> {
        let ticks = tasks.join(" ");
        let gate = self.script("gates/claims-gate.sh");
        let env = [("L7R_LAND_TICKS", ticks.as_str())];
        let deadline = self.clock.now() + self.claims_wait;
        let mut said = String::new();
        loop {
            let (mut rc, mut out) = self.run(&[&gate], &env)?;
            if let Some(d) = d {
                if rc != 0
                    && (out.contains("carry:") || out.contains("known:"))
                    && !["owed (", "introduced:"].iter().any(|w| out.contains(w))
                {
                    self.file_carries(d)?; // a carry is filed, not waited on (405 T77: batch 5's wait needed `make claims-carry` by hand)
                    self.file_known()?; // ...and a known drift recorded, not ruled on (feature 430 T06)
                    (rc, out) = self.run(&[&gate], &env)?;
                }
            }
            self.commit_escape_records()?;
            let dirty = self.dirty(&[])?;
            if rc == 0 && dirty.is_empty() {
                return Ok(String::new());
            }
            if rc != 0 {
                let cure = claims_cure(&out, &self.in_flight()?);
                if !cure.is_empty() {
                    return Ok(cure);
                }
            }
            let why = if rc == 0 {
                format!("uncommitted changes: {}", splitlines(&dirty)[0])
            } else {
                format!("claims-gate.sh: {}", tail(&kept_lines(&out), 600))
            };
            if self.clock.now() >= deadline {
                return Ok(why);
            }
            if why != said {
                self.say(&format!(
                    "land: waiting for the claims round before the push - {why}"
                ));
                said = why;
            }
            self.clock.sleep(self.claims_poll);
        }
    }
}

#[cfg(test)]
mod tests;
