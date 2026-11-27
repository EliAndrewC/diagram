//! A NITPICK FIXED ON THE SHEET OWES A ROUND OF ITS EDIT ALONE (feature 451 T199; the GM 2026-11-23, "check whether there are any
//! other gaps like this", the gap audit's item 11, T188's rule reaching building-review; his route, request.md: "make only the
//! smallest possible changes perhaps with some kind of adversarial subagent review process"). A building-review nitpick or wording
//! finding fixed on the sheet moves its content key, so the verdict no longer carries ([`super::carried`]) and a full round was owed.
//!
//! `make review-fixed UNIT=<unit> FINDING="<ids>"` ([`declare`]) names the nitpicks an edit fixed. It is refused unless each is a
//! `nitpick` of the last PASS or NEEDS-WORK, every other open finding is minor ([`super::stands::MINOR`]) or left by `make
//! review-accept`, and the sheet as that review read it was kept (at the verdict's writing, [`keep`]) and hashes as reviewed. It writes
//! the change-scoped prompt: the edit's runs of lines, before and after, in T189's pairs (`l7r_gate_core::difflib::paired`, the record
//! checks' change section), and the whole sheet named for context. A building-review dispatched on it judges, adversarially, ONLY
//! whether the edit did no more than the named fixes and made nothing wrong; its last act is `make review-verdict ... SCOPE=change`
//! ([`record`]), which writes `scoped` into the verdict record. A clean one - PASS, every finding minor, its gate not red - carries the
//! verdict to the sheet as edited ([`carries`]), so `make verify`'s standing check, the checkpoint and the push's review gate (which
//! asks `reviews prereq answered`) accept it. Anything else, or an error or questionable fix, owes the full round, as before.
//!
//! WHY, measured 2026-11-23 over the 66 building-review rounds the session transcripts hold: of the 12 later rounds after a round left
//! with only nitpick or outside findings, 0 of the 7 attributable were owed by a nitpick fixed on the sheet alone, and 5 of the 12 are
//! unknown (their prompts name no review tree). The rule is the GM's, not a measured saving: a style edit is not a factual one, and a
//! re-review is scoped to the change.
//!
//! Research: a nitpick fixed on the sheet owes a scoped round - NONE: review bookkeeping, no map decision

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_pool::walk;
use serde_json::{json, Value};

use super::stands::MINOR;
use super::{
    accepted_ids, folder_key, get, latest_verdict, raised_findings, read_json, reply, round_key,
    text_of, unit_content_key, unit_folder_on, unit_gate_state, unit_sheet, verdict_dir, Reply,
};

/// The sheet's two files a review reads, as [`super::folder_key`] hashes them.
fn files(on: &str) -> [String; 2] {
    [format!("{on}.svg"), format!("{on}.notes.md")]
}

/// Where the sheet as the unit's last review read it is kept: `.git/review-verdicts/<unit>.reviewed/`.
#[must_use]
pub fn kept_dir(clone: &Path, unit: &str) -> PathBuf {
    verdict_dir(clone).join(format!("{unit}.reviewed"))
}

/// Where a declared change-scoped round's prompt and declaration live: `.git/review-scoped/<unit>/`.
fn scoped_dir(clone: &Path, unit: &str) -> PathBuf {
    l7r_shared::guards::event_log_hooks::common_git_dir(clone)
        .join("review-scoped")
        .join(unit)
}

/// Keep the unit's sheet, `on` in `folder`, as the review that is writing its verdict read it (the verdict record's last act).
pub fn keep(clone: &Path, unit: &str, folder: &Path, on: &str) {
    let dir = kept_dir(clone, unit);
    let _ = std::fs::remove_dir_all(&dir);
    let _ = std::fs::create_dir_all(&dir);
    for f in files(on) {
        let _ = std::fs::copy(folder.join(&f), dir.join(&f));
    }
}

/// Whether `v`'s change-scoped round was clean and moved its sheet from `at` (the verdict's own content key) to `now`.
#[must_use]
pub fn carries(v: &Value, at: &str, now: &str) -> bool {
    get(v, "scoped").is_some_and(|s| {
        get(s, "clean") == Some(&json!(true))
            && text_of(s, "from", "") == at
            && text_of(s, "to", "") == now
    })
}

/// What `make review-fixed` found: the change-scoped round declared (its prompt's path), or no round owed at all (the words to print).
#[derive(Debug, PartialEq, Eq)]
pub enum Fixed {
    Declared(PathBuf),
    NotOwed(String),
}

/// The unit `make review-fixed UNIT=` names: a unit's slug as given, a sheet's bare name as its building-review (451 T214: the cascade
/// test's `UNIT=ochiba-roundtrip-test` was read as a unit with no verdict on file, and refused as one owing a full round).
#[must_use]
pub fn unit_of(name: &str) -> String {
    if super::super::owed::is_unit_slug(name) {
        name.to_owned()
    } else {
        format!("building-review--{name}")
    }
}

/// Declare that the sheet's edit since `name`'s last verdict fixes only the nitpicks `named`: the scoped prompt's path, no round owed
/// where the delta owes the unit none, or the refusal.
///
/// A unit the delta does not owe - its sheet's edit no occasion (feature 294: a notes edit is none) - owes no round of any kind, as
/// `reviews owed` (`make verify`, `reviews snapshot`) and the push's review gate, which asks only owed units, read it (451 T214: the
/// cascade test's round-trip sheet, whose notes-only fix these owed nothing and `make review-fixed` a full round). An owed unit whose
/// verdict was written before T199 kept its sheet has that sheet found again in git history ([`recover`]).
///
/// # Errors
/// The refusal, naming what owes the full round.
pub fn declare(clone: &Path, name: &str, named: &[String]) -> Result<Fixed, String> {
    let full = "a full round is owed (`make verify`, then dispatch its prompt)";
    let unit = unit_of(name);
    let unit = unit.as_str();
    // owed as `reviews owed` reads the delta, never by a snapshot an earlier `make verify` left: the round-trip sheet's, a day old,
    // read as its sheet, was the cascade test's "not kept" (451 T214)
    let sheet = unit_sheet(clone, unit);
    let owed = (!sheet.is_empty()).then(|| unit_folder_on(clone, unit, || sheet.clone()));
    let Some((folder, on)) = owed.flatten() else {
        let sheet = unit.rsplit("--").next().unwrap_or_default();
        if walk(clone).folder(sheet).is_none() {
            return Err(format!(
                "no pool sheet `{sheet}` (UNIT={name}): name a sheet or its building-review unit"
            ));
        }
        return Ok(Fixed::NotOwed(format!(
            "{unit} is not owed by this delta (no occasion in it, as `make verify`, `reviews snapshot` and the push's review gate read \
             it): no round is owed for the edit, full or change-scoped, and the last verdict stays on file as it is (451 T214)\n"
        )));
    };
    let Some(v) = latest_verdict(clone, unit)
        .filter(|v| matches!(text_of(v, "verdict", "").as_str(), "PASS" | "NEEDS-WORK"))
    else {
        return Err(format!(
            "{unit} has no PASS or NEEDS-WORK verdict to carry, and the delta owes it a round: its first full round, which no \
             change-scoped one stands for - {full}"
        ));
    };
    if named.is_empty() {
        return Err("FINDING=\"<ids>\" names the nitpicks the edit fixed".to_owned());
    }
    let raised = raised_findings(&v);
    let left = accepted_ids(clone, unit, &round_key(&v));
    for id in named {
        let Some(f) = raised.iter().find(|f| &text_of(f, "id", "") == id) else {
            return Err(format!("{unit}'s last verdict raised no finding {id}"));
        };
        let sev = text_of(f, "severity", "none");
        if sev != "nitpick" {
            return Err(format!(
                "{id} is a `{sev}` finding, not a nitpick: its fix owes the full round - {full}"
            ));
        }
    }
    for f in &raised {
        let (id, sev) = (text_of(f, "id", ""), text_of(f, "severity", "none"));
        if !named.contains(&id) && !MINOR.contains(&sev.as_str()) && !left.contains(&id) {
            return Err(format!("{id}, a `{sev}` finding, is open: an error or questionable finding owes the full round - {full}"));
        }
    }
    // a verdict carries a content key wherever its unit names a sheet (`write_verdict`)
    let from = text_of(&v, "content_key", "");
    let kept = kept_dir(clone, unit);
    if folder_key(&kept, &on) != from && !recover::recover(clone, &folder, &on, &from, &kept) {
        return Err(format!(
            "the sheet as {unit}'s review read it is neither kept (a verdict written before 451 T199) nor in git history (no \
             committed version of its drawing and notes hashes as it did), so its edit cannot be shown: {full}"
        ));
    }
    let to = folder_key(&folder, &on);
    if to == from {
        return Err(format!(
            "{unit}'s sheet hashes as its review read it - run `make verify` after the edit, so its snapshot is the sheet as edited; \
             an unchanged sheet's verdict stands as it is"
        ));
    }
    let dir = scoped_dir(clone, unit);
    let prompt = dir.join("prompt.md");
    let decl = json!({"from": from, "to": to, "fixed": named});
    std::fs::create_dir_all(&dir)
        .and_then(|()| std::fs::write(&prompt, prompt_text(unit, &v, named, &kept, &folder, &on)))
        .and_then(|()| std::fs::write(dir.join("declared.json"), decl.to_string()))
        .map_err(|e| format!("{}: {e}", dir.display()))?;
    Ok(Fixed::Declared(prompt))
}

/// The change-scoped round's prompt: its contract, the named nitpicks, and the edit's pairs.
fn prompt_text(
    unit: &str,
    v: &Value,
    named: &[String],
    kept: &Path,
    folder: &Path,
    on: &str,
) -> String {
    let mut out = format!(
        "UNIT: {unit}\nSCOPE: change (451 T199) - a CHANGE-SCOPED ROUND, not a full building-review round.\n\n\
         The last full round's {} declared these nitpicks fixed by the edit below:\n",
        text_of(v, "verdict", "")
    );
    for f in raised_findings(v) {
        let id = text_of(&f, "id", "");
        if named.contains(&id) {
            let _ = writeln!(out, "- {id}: {}", text_of(&f, "what", ""));
        }
    }
    let _ = write!(
        out,
        "\nJudge ONLY this edit, and judge it ADVERSARIALLY - assume it does more than it says until the pairs show otherwise:\n\
         1. Does it do only what the named nitpicks asked? Any change beyond them (geometry, a mark moved, text no finding named) is an \
         `error` finding naming the pair.\n\
         2. Does it fix each named nitpick? One left unfixed is a `nitpick` finding naming it.\n\
         3. Did it make anything wrong on the sheet? An `error` or `questionable` finding, by your contract's norms.\n\
         Re-open nothing the edit did not touch: a finding elsewhere is severity `outside`. The whole sheet, for context: `{}` and `{}`.\n\n\
         Your last act: findings to a JSON list of {{\"id\", \"severity\", \"what\"}}, then \
         `make review-verdict UNIT={unit} VERDICT=<PASS|NEEDS-WORK> FINDINGS=<file> SCOPE=change`; quote its line. Anything but a PASS \
         whose findings are only nitpick, outside or confirmation owes the full round.\n\n### The edit (the sheet as reviewed, then now)\n\n",
        folder.join(format!("{on}.svg")).display(),
        folder.join(format!("{on}.notes.md")).display()
    );
    for f in files(on) {
        let (a, b) = (
            std::fs::read_to_string(kept.join(&f)).unwrap_or_default(),
            std::fs::read_to_string(folder.join(&f)).unwrap_or_default(),
        );
        let (a, b): (Vec<&str>, Vec<&str>) = (a.lines().collect(), b.lines().collect());
        for pair in l7r_gate_core::difflib::paired(&f, &a, &b, true) {
            let _ = writeln!(out, "{pair}");
        }
    }
    out
}

/// What `make review-fixed` prints on a declaration.
#[must_use]
pub fn declared_text(unit: &str, prompt: &Path) -> String {
    format!(
        "declared: {unit}'s edit fixes only the named nitpicks. Dispatch ONE building-review on the change-scoped prompt {} \
         (its slug begins with {unit}) in place of the full round; its `make review-verdict ... SCOPE=change` decides whether the \
         verdict carries (451 T199)\n",
        prompt.display()
    )
}

/// The change-scoped round's last act (`make review-verdict ... SCOPE=change`): `scoped` written into the unit's verdict record.
#[must_use]
pub fn record(clone: &Path, unit: &str, verdict: &str, findings: &[Value]) -> Reply {
    let refuse = |why: String| {
        reply(
            String::new(),
            format!("make review-verdict SCOPE=change: {why}\n"),
            1,
        )
    };
    let path = scoped_dir(clone, unit).join("declared.json");
    let Some(decl) = read_json(&path) else {
        return refuse(format!("{unit} has no change-scoped round declared - `make review-fixed UNIT={unit} FINDING=\"<ids>\"` declares one"));
    };
    let Some(mut v) = latest_verdict(clone, unit) else {
        return refuse(format!(
            "{unit} has no verdict for a change-scoped round to answer"
        ));
    };
    let (from, to) = (text_of(&decl, "from", ""), text_of(&decl, "to", ""));
    if text_of(&v, "content_key", "") != from {
        return refuse(format!(
            "{unit}'s verdict was written again since the declaration: declare again"
        ));
    }
    if unit_content_key(clone, unit) != to {
        return refuse(format!("{unit}'s sheet moved since the declaration: `make review-fixed` again on the sheet as it reads now"));
    }
    let gate = unit_gate_state(clone, unit);
    let clean = verdict == "PASS"
        && gate != "red"
        && findings
            .iter()
            .all(|f| MINOR.contains(&text_of(f, "severity", "none").as_str()));
    let scoped = json!({"from": from, "to": to, "fixed": decl.get("fixed").cloned().unwrap_or(Value::Null),
        "verdict": verdict, "gate": gate, "findings": findings, "clean": clean});
    if let Value::Object(m) = &mut v {
        m.insert("scoped".to_owned(), scoped);
    }
    let _ = super::super::write_json(&verdict_dir(clone).join(format!("{unit}.json")), &v);
    let _ = std::fs::remove_file(&path);
    let said = if clean {
        "the verdict carries to the sheet as edited"
    } else {
        "not clean - the full round is owed (`make verify`, then dispatch its prompt)"
    };
    reply(
        format!("recorded the change-scoped {verdict} for {unit} (gate {gate}): {said}\n"),
        String::new(),
        0,
    )
}

mod recover;

#[cfg(test)]
mod tests;
