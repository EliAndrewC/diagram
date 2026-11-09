//! Refuse to record a gate GREEN when the run finished too fast to have done the work (feature 449 T068, from `check-run-plausible.py`).
//!
//! WHY (found 2026-09-05): a dry run was minting a push credential. GNU make executes `$(MAKE)` sub-invocations even under `-n`, so `make -n
//! done` walks the recipe, every phase trivially succeeds, and the closing lines write a correctly-hashed green record in about four seconds.
//! The floor comes from the pinned ratchet baseline: a dry run lands around 1% of it, a genuine warm run has never been below about 30%,
//! and ten percent sits in the empty middle. A smoke alarm for "nothing happened", not a proof that the right thing happened.

use std::path::Path;

use fancy_regex::Regex;

use super::Outcome;

pub(super) const USAGE_LOG_TOOL: &str = "check-run-plausible";
const ABSOLUTE_MIN: u64 = 5;

/// The pinned baseline `ratchet.py` keeps for this target; read off its text until that file is ported.
fn baseline(root: &Path, target: &str) -> Option<u64> {
    let text = std::fs::read_to_string(root.join("scripts/measure/ratchet.py")).ok()?;
    let row = Regex::new(&format!(
        r#""{}":\s*Ratchet\((?:[^=]|=(?!\s*\d))*?\bbaseline=(\d+)"#,
        fancy_regex::escape(target)
    ))
    .ok()?;
    row.captures(&text)
        .ok()??
        .get(1)?
        .as_str()
        .parse()
        .ok()
        .filter(|b| *b > 0)
}

fn floor_for(root: &Path, target: &str) -> Option<u64> {
    baseline(root, target).map(|b| ABSOLUTE_MIN.max(b / 10))
}

/// Is this a `make -n`? The first word of MAKEFLAGS carries the single-letter flags; any other word may hold an `n` in a variable.
fn dry_run(flags: &str) -> bool {
    let first = flags.split(' ').next().unwrap_or_default();
    !first.contains('=') && first.contains('n')
}

#[expect(
    clippy::cast_precision_loss,
    reason = "a floor of seconds, far inside f64's exact range"
)]
fn check(root: &Path, target: &str, seconds: f64, flags: &str, mode: &str) -> Option<String> {
    if dry_run(flags) {
        return Some(format!("REFUSED to record `{target}` green: this is a DRY RUN (`make -n`).\n  make executes $(MAKE) sub-invocations even under -n, so the recipe reaches its\n  recording lines having done no work. A dry run must not mint a push credential."));
    }
    let floor = if mode == "incremental" {
        Some(ABSOLUTE_MIN)
    } else {
        floor_for(root, target)
    }?;
    (seconds < floor as f64).then(|| format!("REFUSED to record `{target}` green: it finished in {seconds:.0}s, under the {floor}s floor.\n  The floor is 10% of the pinned ratchet baseline for `{target}`, so it tracks the era\n  rather than a fixed number. A run this fast did not do the work, and a green record is\n  the whole of what a push demands. Nothing was recorded; run the gate for real."))
}

/// `l7r-gate check run-plausible <target> <elapsed-seconds> [full|incremental] | --reuse <target>`.
pub(super) fn cli(args: &[String], root: &Path, flags: &str) -> Outcome {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let bold = |text: String| Outcome::refuse(format!("\n\x1b[1m{text}\x1b[0m\n\n"));
    match words.as_slice() {
        ["--reuse", target] if dry_run(flags) => Outcome::refuse(format!("\n\x1b[1mREFUSED to re-stamp `{target}`: this is a DRY RUN (`make -n`).\x1b[0m\n  A dry run must not refresh a verification record either - re-stamping is what\n  kept a bogus record alive across every later gate.\n\n")),
        ["--reuse", _] => Outcome::out(String::new()),
        [target, secs] | [target, secs, _] => {
            let Ok(seconds) = secs.parse::<f64>() else {
                return Outcome::out(String::new()); // an unparseable duration is not this guard's business
            };
            let mode = words.get(2).copied().unwrap_or("full");
            check(root, target, seconds, flags, mode).map_or_else(|| Outcome::out(String::new()), bold)
        }
        _ => Outcome::usage("usage: check run-plausible <target> <elapsed-seconds> [full|incremental] | --reuse <target>\n"),
    }
}

#[cfg(test)]
mod tests;
