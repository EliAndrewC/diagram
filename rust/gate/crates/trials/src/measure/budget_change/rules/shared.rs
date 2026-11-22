//! The rules a hamlet stage and a pool-sheet stage share (feature 449 T243, split from `rules.rs` at the file-scale bar): a raise's
//! readiness, whether it raises and its caps against the first figure; a change's words and re-pointing; an accept's audit and its
//! hold of one counted figure to its budget. `rules.rs` asks each at a hamlet stage's sizes, `sheets.rs` on a pool-sheet stage's
//! sheets.

use std::path::Path;

use l7r_shared::pyjson::py_str;
use serde_json::Value;

use super::super::{fixed, verdict_of, LEEWAY, MISSED, R, RAISE_CAP, SOUND};
use super::{accepted_by, is, missed_work};

/// A re-derived figure `at` (`at 40`, `on all sheets`) that is no raise on its standing one: why, else none. A pool-sheet stage's
/// raise asks it of its sheets together, as a hamlet stage's asks it at its top size (feature 449 T243).
pub(in super::super) fn no_raise(phase: &str, at: &str, new: f64, standing: f64) -> Option<String> {
    (new <= standing).then(|| format!("`{phase}`'s re-derived budget {at}, {}, is no raise on {} - a lowering re-pins with LOWER=1", fixed(new, 0, true), fixed(standing, 0, true)))
}

/// A raise's caps on one figure `at` against its `first` (444 FR-022): past ten times it, the GM's words (`to` the change's figure
/// form); past twice it, a second SOUND (`sound`: the raise's verdict and its second) - "" when within. A hamlet stage's raise asks
/// it at its top size, a pool-sheet stage's on each sheet (feature 449 T243).
pub(in super::super) fn past_first(
    root: &Path,
    phase: &str,
    at: &str,
    new: f64,
    first: f64,
    sound: (&str, &str),
    to: &str,
) -> R<String> {
    if new > RAISE_CAP * first {
        return Ok(format!(
            "`{phase}`'s re-derived budget {at}, {}, is past 10 times its first, {} - an order of magnitude needs the GM's words (feature 444 FR-022): make budget-change PHASE={phase} {to} DERIVATION= VERDICT= WORDS=\"<the GM's words>\"",
            fixed(new, 0, true),
            fixed(first, 0, true)
        ));
    }
    // PAST TWICE THE FIRST, THE RIGOROUS ANALYSIS (FR-022 rule 2; the GM: "I don't want us to just think it's reasonable to have
    // things take an order of magnitude more operations than we estimated. Without extremely rigorous analysis"): a second
    // MODE BUDGET dispatch of the same bundle, blind to the first, judges it SOUND too
    let (verdict, second) = sound;
    if new > LEEWAY * first
        && (second.is_empty() || second == verdict || verdict_of(&root.join(second))? != SOUND)
    {
        let read = if !second.is_empty() && second != verdict {
            let word = verdict_of(&root.join(second))?;
            format!(
                " ({second} reads {})",
                if word.is_empty() { "nothing" } else { &word }
            )
        } else {
            String::new()
        };
        return Ok(format!(
            "`{phase}`'s re-derived budget {at}, {}, is {} times its first, {} - past 2 times a raise needs a second SOUND, from an independent MODE BUDGET dispatch of the same bundle blind to the first: SECOND=<its verdict file>{read}",
            fixed(new, 0, true),
            fixed(new / first, 1, false),
            fixed(first, 0, true)
        ));
    }
    Ok(String::new())
}

/// What a raise owes before its figures (444 FR-022): a budgeted stage, before its acceptance - or an accepted one the round
/// arbiter `opened` to it (449 T250, ask:449-T250-raise-accepted) - and a derivation naming the work its first one missed - "" when
/// it owes nothing more. A hamlet stage's and a pool-sheet stage's (feature 449 T243).
pub(in super::super) fn raise_ready(
    root: &Path,
    phase: &str,
    status: &Value,
    derivation: &str,
    opened: bool,
) -> R<String> {
    if !(opened || is(status, "budgeted")) {
        return Ok(format!("`{phase}` is {} - RAISE=1 raises a budgeted stage, before its acceptance (feature 444 FR-022)", py_str(status)));
    }
    if missed_work(root, derivation)?.is_empty() {
        return Ok(format!(
            "{derivation} names no work its first derivation missed - a raise without the GM's words counts each item under `{MISSED}` (feature 444 FR-022); a figure that is only an estimate off is the leeway's, at acceptance"
        ));
    }
    Ok(String::new())
}

/// A change without the GM's words, refused.
pub(in super::super) const NO_WORDS: &str =
    "no WORDS - a budget changes only with the GM's own words";

/// A change's re-pointing (444 FR-015): both a DERIVATION and its VERDICT or neither, the derivation a file, the verdict SOUND - ""
/// when it holds. A hamlet stage's change and a pool-sheet stage's (feature 449 T243).
pub(in super::super) fn repoint_refusal(root: &Path, derivation: &str, verdict: &str) -> R<String> {
    if derivation.is_empty() != verdict.is_empty() {
        return Ok("re-pointing a stage names both its DERIVATION= and its VERDICT=".to_owned());
    }
    if !derivation.is_empty() && !root.join(derivation).is_file() {
        return Ok(format!("no derivation at {derivation}"));
    }
    if !verdict.is_empty() && verdict_of(&root.join(verdict))? != SOUND {
        return Ok(format!("{verdict} is no SOUND verdict - a stage is re-pointed only at a derivation its verdict judged SOUND"));
    }
    Ok(String::new())
}

/// An accept's audit (444 FR-005, FR-013): its MODE AUDIT WITHIN or LEEWAY, or the round arbiter's accept naming the phase - ""
/// when it stands. A hamlet stage's accept and a pool-sheet stage's (feature 449 T243).
pub(in super::super) fn audit_refusal(
    root: &Path,
    phase: &str,
    audit: &str,
    arbiter: &str,
    derivation: &str,
) -> R<String> {
    if arbiter.is_empty() {
        let word = verdict_of(&root.join(audit))?;
        if word != "WITHIN" && word != "LEEWAY" {
            return Ok(format!(
                "{audit} reads {}, not WITHIN or LEEWAY - a phase is accepted on its MODE AUDIT's WITHIN, or LEEWAY at up to 2 times its budget (`make work-budget-bundle MODE=audit PHASE={phase}`)",
                if word.is_empty() { "nothing" } else { &word }
            ));
        }
    } else if !accepted_by(root, derivation, phase, arbiter)? {
        return Ok(format!("the round arbiter's log holds no accept at {arbiter} naming `{phase}` - a phase is accepted on its MODE AUDIT's WITHIN or that accept"));
    }
    Ok(String::new())
}

/// One figure an accept holds: the phase, where (`at 40 households`, `on beta-sheet`), its budget there, its first before a raise,
/// and whether its raise had a second SOUND.
pub(in super::super) struct Held<'a> {
    pub phase: &'a str,
    pub at: &'a str,
    pub budget: f64,
    pub first: Option<f64>,
    pub second: bool,
}

/// A counted figure an accept holds to its budget (444 FR-022 rules 1 and 2): "" when within, else why not.
pub(in super::super) fn over_refusal(
    root: &Path,
    held: &Held,
    ops: f64,
    audit: &str,
    arbiter: &str,
) -> R<String> {
    let Held {
        phase, at, budget, ..
    } = *held;
    // FR-022 rule 1: past the budget only on the audit's LEEWAY (the agent named the excess and judged it), never past twice it;
    // the arbiter's accept stands in for a WITHIN, never for a LEEWAY (FR-006: the arbiter accepts no phase over its budget)
    if ops > LEEWAY * budget
        || (ops > budget && (!arbiter.is_empty() || verdict_of(&root.join(audit))? != "LEEWAY"))
    {
        if budget == 0.0 {
            return Err("ZeroDivisionError: float division by zero".to_owned());
        }
        let past = ops > LEEWAY * budget;
        return Ok(format!(
            "`{phase}`: {} counted operations {at}, {} times its budget {}{} - rebuild it again, raise the budget on a SOUND re-derivation naming the work it missed (`make budget-set RAISE=1`, FR-022), or with the GM's words (`make budget-change`, FR-006)",
            fixed(ops, 0, true),
            fixed(ops / budget, 2, false),
            fixed(budget, 0, true),
            if past { ", past the leeway's 2 times" } else { " - over it, a phase is accepted on the MODE AUDIT's LEEWAY" }
        ));
    }
    // FR-022 rule 2: raise and leeway together - within twice the FIRST budget on a raise judged by one SOUND, within ten
    // times it on one judged by two independent ones; past that, the GM's words
    let cap = if held.second { RAISE_CAP } else { LEEWAY };
    if let Some(first) = held.first.filter(|f| ops > cap * f) {
        return Ok(format!(
            "`{phase}`: {} counted operations {at}, past {} times its first budget {}{}",
            fixed(ops, 0, true),
            if held.second { "10" } else { "2" },
            fixed(first, 0, true),
            if held.second {
                " - an order of magnitude needs the GM's words (`make budget-change`, FR-022)"
            } else {
                " - past twice the first, its raise owes a second, independent SOUND (`make budget-set RAISE=1 SECOND=`) or the GM's words (FR-022)"
            }
        ));
    }
    Ok(String::new())
}
