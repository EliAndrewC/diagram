//! The claims round the landing waits for after its gate (405 T50, D23), what waiting cannot cure (feature 426 D1, feature 440 T01), and
//! the gate's own lint committed while it waits (the GM 2026-10-24).

use std::path::Path;
use std::time::Instant;

use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::cheap::kept_lines;
use super::{head, py_read, tail, Land};

/// How `claims_cure` opens each refusal that waiting cannot end - so the stop names it as such, not as the wait run out.
const CURE_OPENINGS: [&str; 2] = [
    "claims-gate.sh refuses on a finding no check in flight can cure",
    "claims-gate.sh: a claim is owed a check and none is in flight",
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
        let deadline = Instant::now() + self.claims_wait;
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
            self.commit_gate_formatting()?;
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
            if Instant::now() >= deadline {
                return Ok(why);
            }
            if why != said {
                self.say(&format!(
                    "land: waiting for the claims round before the push - {why}"
                ));
                said = why;
            }
            std::thread::sleep(self.claims_poll);
        }
    }

    /// `text` as the gate's lint leaves it (`make done`: `ruff check --fix`, then `ruff format`), asked of the file's own path so its
    /// configuration applies; None where ruff fails.
    fn ruffed(&self, path: &str, text: &str) -> Result<Option<String>, String> {
        let mut out = text.to_owned();
        for cmd in [
            &["check", "--fix", "--quiet"][..],
            &["format", "--quiet"][..],
        ] {
            let mut args = vec![self.python.as_str(), "-m", "ruff"];
            args.extend(cmd);
            args.extend(["--stdin-filename", path, "-"]);
            let mut child = self
                .command(&args)
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::piped())
                .spawn()
                .map_err(|e| super::spawn_error(&self.python, &e))?;
            let feed = out.clone();
            let mut pipe = child.stdin.take();
            let writer = std::thread::spawn(move || {
                if let Some(p) = pipe.as_mut() {
                    let _ = std::io::Write::write_all(p, feed.as_bytes());
                }
            });
            let done = child.wait_with_output().map_err(super::io)?;
            let _ = writer.join();
            let code = super::code_of(done.status);
            let said = super::decode(&done.stdout)?;
            super::decode(&done.stderr)?;
            if !(code == 0 || code == 1) || said.is_empty() {
                return Ok(None);
            }
            out = said;
        }
        Ok(Some(out))
    }

    /// THE GATE'S OWN LINT IS COMMITTED, NEVER WAITED ON (the GM 2026-10-24, after T07's landing sat 20 min of the claims wait on a test
    /// whose imports the gate's `ruff check --fix` had sorted - nothing would ever commit it). Each modified tracked `.py` file whose
    /// working copy is exactly its HEAD copy run through the gate's ruff is committed; any other change is left for the wait to name.
    /// The paths committed.
    #[expect(
        clippy::case_sensitive_file_extension_comparisons,
        reason = "Python's `str.endswith`, case and all"
    )]
    pub(super) fn commit_gate_formatting(&self) -> Result<Vec<String>, String> {
        let status = self.run(&["git", "status", "--porcelain"], &[])?.1;
        let paths: Vec<String> = splitlines(&status)
            .into_iter()
            .filter(|l| l.starts_with(" M ") && l.ends_with(".py"))
            .map(|l| l.chars().skip(3).collect())
            .collect();
        let mut mine = Vec::new();
        for path in paths {
            let (rc, was) = self.run(&["git", "show", &format!("HEAD:{path}")], &[])?;
            let now = match std::fs::read(self.root.join(&path)) {
                Ok(_) => py_read(&self.root.join(&path))?,
                Err(_) => continue,
            };
            if rc == 0 && was != now && self.ruffed(&path, &was)?.as_deref() == Some(now.as_str()) {
                mine.push(path);
            }
        }
        if !mine.is_empty() {
            let mut cmd = vec![
                "git",
                "commit",
                "-q",
                "-m",
                "the gate's own lint and format, committed (make land)",
                "--",
            ];
            cmd.extend(mine.iter().map(String::as_str));
            self.run(&cmd, &[])?;
        }
        Ok(mine)
    }
}

#[cfg(test)]
mod tests;
