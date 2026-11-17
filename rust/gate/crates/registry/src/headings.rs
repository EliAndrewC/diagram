//! Every feature class's `Entry:` still RESOLVES - the half of feature 234 that is decidable (`scripts/gates/check-entry-headings.py`,
//! ported by feature 449 T149 under `ask:449-phase4-slices` Q5; placed in phase 4 with the registry by `ask:449-T065-scope`).
//!
//! WHY IT IS GATED WHERE THE DRIFT REPORT IS NOT: a class pointing at a question that no longer exists has no legitimate form, so it fires
//! on exactly the thing it names. `sources::research_questions` drops a question that is not there, silently, and the References tab goes
//! quietly empty on every map carrying the kind; `research/CLAUDE.md` requires a rename to fix its inbound entries, and this is the
//! mechanism that sentence never had. Measured 2026-09-12: 0 of 51 entries broken - prophylactic, and it says so.
//!
//! THE ONE LEGITIMATE NON-MATCH is a section deliberately not written, `(no dedicated entry - recorded as silent)`, recognized explicitly
//! ([`SILENT`]) and never by the absence of a match, so a broken pointer and a declared silence cannot be confused; `make audit` lists
//! every entry taking it ([`silent_listing`]).
//!
//! EVERY KIND, BOTH REGISTRIES (feature 449 T164): the Python read `CLASSES` alone, so the 99 Mode A kinds (`COMPOUND_CLASSES`) were
//! never checked - a sheet's modal pointing at a renamed question went as quietly empty as a hamlet's did before feature 234. T149's
//! port kept that gap (covering it makes the check refuse more, which FR-002's fix exception does not reach inside a port) and T164
//! closes it in a commit of its own. ONLY WHAT IS NEW IS MARKED (T164's plan review): every line the check and `make audit`'s listing
//! gave before stays byte for byte - a hamlet kind named by its bare key, the listing's rows at their old width and its count line -
//! and a sheet kind is named `sheet/<slug of the key>` (`sheet/cinnabar-workshop`), which also tells apart the four keys both
//! registries hold (`burial-ground`, `garden`, `notice-board`, `well`); the hamlet's are checked first, sorted by key, then the sheet's,
//! and the listing gives the sheet's silences a block of their own after the hamlet's.
//! RUN AT THE GATE AND AT THE PUSH: a research-page-only delta owes no gate, so the push holds it.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::sources::entry_fragments;
use l7r_gate_research::Result;

use crate::about::{classes, compound_classes, slug, FeatureClass};
use crate::kinds::SHEET_REGISTRY;

/// The name `usage_log` (the gate's `log usage`) records this check's runs under (feature 406 T03).
pub const USAGE_LOG_TOOL: &str = "check-entry-headings";

/// The declared-silence form: a section deliberately not written, recognized rather than inferred.
pub static SILENT: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?i)\(no dedicated entry\s*-\s*recorded as silent\)"));

/// The record's questions, from the tree's root.
const QUESTIONS: &str = "research/questions";

/// The fragments an entry names that the record does not hold - or the entry itself, when it names none.
#[must_use]
pub fn unresolved(root: &Path, entry: &str) -> Vec<String> {
    let named = entry_fragments(entry);
    if named.is_empty() {
        return vec![entry.to_owned()];
    }
    named
        .into_iter()
        .filter(|n| !root.join(QUESTIONS).join(n).is_file())
        .map(|n| format!("{QUESTIONS}/{n}"))
        .collect()
}

/// The hamlet's kinds and the sheet's, each with the name the check gives it.
type Blocks = [Vec<(String, FeatureClass)>; 2];

/// Both registries' kinds, each block named and sorted by key - the hamlet's then the sheet's - or None where this tree has no engine (a
/// repository the push's fixtures build): nothing to be right or wrong about there, a no-op and not a failure.
///
/// # Errors
/// A kind's modal file missing or refused - the import error the Python had; the hamlet registry's first, as it loads first.
fn loaded(root: &Path) -> Result<Option<Blocks>> {
    if !root.join("l7r").is_dir() {
        return Ok(None);
    }
    Ok(Some(named(root)?))
}

/// The hamlet's kinds by their bare key, as the check named them before T164, and the sheet's as `sheet/<slug>`, each sorted by key.
fn named(root: &Path) -> Result<Blocks> {
    let block = |mut kinds: Vec<FeatureClass>, name: &dyn Fn(&str) -> String| {
        kinds.sort_by(|a, b| a.key.cmp(&b.key));
        kinds
            .into_iter()
            .map(|fc| (name(&fc.key), fc))
            .collect::<Vec<_>>()
    };
    let hamlet = block(classes(root)?, &str::to_owned);
    let sheet = block(compound_classes(root)?, &|key| {
        format!("{}/{}", SHEET_REGISTRY.dir, slug(key))
    });
    Ok([hamlet, sheet])
}

/// Every class whose `Entry:` resolves to no research question and is not a declared silence.
///
/// # Errors
/// The registry not loading.
pub fn broken(root: &Path) -> Result<Vec<String>> {
    let Some(all) = loaded(root)? else {
        return Ok(Vec::new());
    };
    let mut bad = Vec::new();
    for (name, fc) in all.into_iter().flatten() {
        if SILENT.is_match(&fc.entry).unwrap_or(false) {
            continue;
        }
        let missing = unresolved(root, &fc.entry);
        if !missing.is_empty() {
            bad.push(format!("{name}: Entry names {}", missing.join(", ")));
        }
    }
    Ok(bad)
}

/// Proves the check still bites: fires on a question that does not exist, stays quiet on a real one, and the declared-silence form
/// swallows no broken pointer. A checker that cannot fail is worth nothing. The pointers it must not resolve are built from parts, so the
/// research-pointer check reads no fixture here.
fn selftest(root: &Path) -> Result<std::result::Result<String, String>> {
    let real = "research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html";
    let silence = format!(
        "research/contents.json#fields ({} - recorded as silent)",
        "no dedicated entry"
    );
    let missing = format!("{QUESTIONS}/{}-a-question-that-does-not-exist.html", "0999");
    let retired = format!(
        "research/contents.json#{} - 'a page and a heading, the form retired by feature 301'",
        "field-archetypes"
    );
    let silent = |t: &str| SILENT.is_match(t).unwrap_or(false);
    // the FORM half always runs: telling a declared silence from a broken pointer is this check's own logic and owes nothing to the engine
    let mut checks = vec![
        (silent(&silence), "the declared silence must be recognized"),
        (
            !silent(real),
            "a real entry must not read as a declared silence",
        ),
        (
            !silent(&format!("{QUESTIONS}/{}-not-there.html", "0999")),
            "a broken pointer must not read as a declared silence",
        ),
    ];
    let engine = loaded(root)?.is_some();
    if engine {
        checks.extend([
            (
                unresolved(root, real).is_empty(),
                "the checker cannot see a question that exists - its matching surface is dead",
            ),
            (
                !unresolved(root, &missing).is_empty(),
                "a broken pointer must be named",
            ),
            (
                !unresolved(root, &retired).is_empty(),
                "an entry naming no fragment is broken",
            ),
        ]);
    }
    Ok(match checks.iter().find(|(ok, _)| !ok) {
        Some((_, why)) => Err((*why).to_owned()),
        None if engine => Ok("check-entry-headings selftest ok\n".to_owned()),
        None => Ok("check-entry-headings selftest ok (form only - no diagram skill in this tree to resolve against)\n".to_owned()),
    })
}

/// `l7r-gate check entry-headings [ROOT] | --selftest`: exit 1 naming each broken entry, as the Python did; a failed self-test exits 1
/// with its assertion. The second value is whether the run is recorded in the usage log: a registry that does not load exits 1 with
/// its refusal and records nothing, as the Python's import raised before its run was recorded (its traceback's text is not an output
/// FR-002 binds, `ask:449-usage-text`; its exit status and the absent record are).
#[must_use]
pub fn cli(args: &[String], tool_root: &Path) -> (l7r_gate_core::Reply, bool) {
    let reply = |stdout: String, stderr: String, code: i32| l7r_gate_core::Reply {
        stdout,
        stderr,
        code,
    };
    let crashed = |e: l7r_gate_research::Error| {
        (
            reply(String::new(), format!("{}: {}\n", e.kind, e.message), 1),
            false,
        )
    };
    if args.first().map(String::as_str) == Some("--selftest") {
        return match selftest(tool_root) {
            Ok(Ok(said)) => (reply(said, String::new(), 0), true),
            Ok(Err(why)) => (
                reply(String::new(), format!("AssertionError: {why}\n"), 1),
                false,
            ),
            Err(e) => crashed(e),
        };
    }
    let root = l7r_gate_research::resolve(Path::new(args.first().map_or(".", String::as_str)));
    match broken(&root) {
        Ok(bad) if bad.is_empty() => (reply(String::new(), String::new(), 0), true),
        Ok(bad) => {
            let mut err =
                "a class entry names a research question the record does not hold:\n".to_owned();
            for line in bad {
                let _ = writeln!(err, "  {line}");
            }
            err.push_str("\nRename an anchor and you owe its inbound links - `research/CLAUDE.md` says so and this is what\nchecks it. Fix the `Entry:` tag (`make fragment-move` rewrites it for you), or restore the question. A section deliberately not written is written\nas `research/contents.json#<section> (no dedicated entry - recorded as silent)`.\n");
            (reply(String::new(), err, 1), true)
        }
        Err(e) => crashed(e),
    }
}

/// What `make audit` lists of the declared silences (the Makefile's one-line Python before T149): each hamlet class taking the form, then
/// their count, as before T164; then the Mode A kinds' block (feature 449 T164), its rows at a width of their own (29, the longest
/// `sheet/<slug>`, where the hamlet's 22 fits a bare key) and its own count, so no line the listing gave before changes.
///
/// # Errors
/// The registry not loading.
pub fn silent_listing(root: &Path) -> Result<String> {
    let [hamlet, sheet] = named(root)?;
    let mut out = String::new();
    for (kinds, width, what) in [(&hamlet, 22, "entries"), (&sheet, 29, "Mode A entries")] {
        let total = kinds.len();
        let mut rows = 0;
        for (name, fc) in kinds
            .iter()
            .filter(|(_, fc)| SILENT.is_match(&fc.entry).unwrap_or(false))
        {
            let _ = writeln!(out, "  {name:<width$} {}", fc.entry);
            rows += 1;
        }
        let _ = writeln!(
            out,
            "  {rows} of {total} {what} name no section; the other {} must RESOLVE, checked at the gate and the push.",
            total - rows
        );
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
