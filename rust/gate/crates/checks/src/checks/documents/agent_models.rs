//! Every subagent check runs on the tier recorded for it: a model AND an effort, pinned in its file (the port of
//! `tests/test_agent_models.py`, feature 449 T133, `ask:449-phase3-remainder` Q3).
//!
//! THE RULING (GM 2026-09-19, feature 251). Judgment stays on Opus; what is purely mechanical is a script and runs on no model; and a
//! DOWNGRADE stands only after it is run on artifacts with known findings (`specs/251-tiered-subagent-checks/research.md` R5). `sonnet`
//! stays a legal value for the day a seeded run supports it.
//!
//! WHAT NEVER CHANGES. Nothing is inherited. An agent file with no `model:` runs on the SESSION's model, which is how nineteen settlement
//! reviews ran on Fable while that file said `inherit` (research R1), and a file with no `effort:` runs at the session's effort (R6). So
//! both keys are owed by every file, and the roster is derived from the directory: a new agent owes its tier here the day it lands.
//!
//! WHAT A DEFINED AGENT IS NOT HANDED (GM 2026-09-19, feature 256). *"If there's something that a subagent should know, it should be in
//! the subagent specification."* Every file carries `omitClaudeMd: true` except the ones `KEEPS_CLAUDE_MD` names (measured: a first turn
//! of 55-63 k tokens fell to 8-12 k and nothing recorded was missed - `specs/256-defined-subagents-without-claude-md/research.md`). The
//! GM asked for this to be enforced by a test (2026-09-20). An exception is a measured case the GM approved, never a session's own call.
//!
//! TO CHANGE A TIER: change the row here and the frontmatter together, and record why - for a downgrade, the seeded-fault runs that
//! justify it, THREE A LEG (GM 2026-09-21; the doctrine is in `docs/spec-kit-and-reviews.md`).

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::{files_in, re, read, rel, root};

pub(super) type Pinned = BTreeMap<String, BTreeMap<String, String>>;

const MODELS: [&str; 2] = ["opus", "sonnet"];
const EFFORTS: [&str; 5] = ["low", "medium", "high", "xhigh", "max"];

/// agent, model, effort.
const TIERS: [(&str, &str, &str); 27] = [
    ("record-format", "opus", "medium"), // Sonnet missed at medium (R5) and at high (R7); opus/medium hit everything
    ("source-reader", "opus", "high"),   // Sonnet tried and missed: research R5
    ("quote-check", "opus", "medium"),
    ("entry-drift", "opus", "medium"),
    ("record-style", "opus", "high"),
    ("translation-check", "opus", "medium"), // feature 292: judgment of meaning; no seeded downgrade run yet
    ("intro-check", "opus", "medium"), // feature 311: judgment about a reader; seeded runs on Opus only (plan D4)
    ("impl-drift", "opus", "medium"), // feature 316; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("modal-form", "opus", "medium"), // feature 319; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("modal-research", "opus", "medium"), // feature 319; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("modal-depiction", "opus", "medium"), // feature 319 D13; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("escalation-check", "opus", "medium"),
    ("round-arbiter", "opus", "high"), // feature 375 FR-011: judges a process in the GM's place at a round cap; binding
    ("spec-fidelity-verify", "opus", "high"), // medium tried and missed: research R5
    ("spec-fidelity", "opus", "high"), // Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("source-applicability", "opus", "high"),
    ("size-audit", "opus", "high"),
    ("building-review", "opus", "high"), // Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("settlement-review", "sonnet", "high"), // feature 294 T34: Opus + 3/3 Sonnet found the seeded re-skin
    ("glyph-check", "opus", "high"), // feature 294; Sonnet 5.5 tried 2026-10-17 and missed (383 research R10)
    ("fix-check", "sonnet", "high"), // feature 294: the GM-complaint fix check; T34: Opus + 3/3 Sonnet found the unfired fix
    ("perf-audit", "opus", "high"),
    ("claims-triage", "opus", "medium"), // 383 amendment 6: impl-drift's question pre-sorted, a judgment; was ad hoc on opus
    ("modal-triage", "opus", "medium"), // 383 amendment 6: the pop-up checks' question pre-sorted, a judgment; was ad hoc on opus
    ("research-pass", "opus", "medium"), // 383 amendment 6: a search pass judges what a source attests; was ad hoc
    ("source-filter", "opus", "medium"), // feature 312: judges a source with no question in hand; calibrated three runs a leg (R2)
    ("work-budget", "opus", "high"), // feature 443 T05 (FR-008): judges a budget's arithmetic and the landed code against it
];

/// agent -> why it KEEPS the CLAUDE.md files. An entry here is a MEASURED case the GM approved, never a session's convenience: the
/// session shows what the field cost that check on recorded findings and recommends, the GM answers, and the row quotes both.
/// EMPTY since feature 383 amendment 6 (the GM 2026-10-17: what subagents share belongs in their system prompt): `spec-fidelity` kept the
/// files from 2026-09-20 until three runs a leg with and without, scored blind, found every recorded item without them (specs/383
/// research R14); the files cost it ~22k tokens written fresh at every dispatch (research R13).
const KEEPS_CLAUDE_MD: [(&str, &str); 0] = [];

/// The frontmatter's `key: value` lines, split at the first colon, a later key overriding an earlier; None for a file with none.
pub(super) fn frontmatter(text: &str) -> Option<BTreeMap<String, String>> {
    let caps = re(r"(?s)\A---\n(.*?)\n---").captures(text).ok()??;
    Some(
        splitlines(&caps[1])
            .into_iter()
            .filter_map(|line| line.split_once(':'))
            .map(|(k, v)| (strip(k).to_owned(), strip(v).to_owned()))
            .collect(),
    )
}

/// Each `*.md` of the agents directory by its stem, and a problem for each that has no frontmatter.
pub(super) fn pinned(agents: &Path) -> (Pinned, Vec<String>) {
    let mut out = Pinned::new();
    let mut bad = Vec::new();
    for p in files_in(agents, ".md") {
        let stem = p
            .file_stem()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        match frontmatter(&read(&p)) {
            Some(fm) => {
                out.insert(stem, fm);
            }
            None => bad.push(format!("{stem}.md: no YAML frontmatter - open the file with a `---` block holding name, model, effort and omitClaudeMd")),
        }
    }
    (out, bad)
}

fn found(pinned: &Pinned) -> Vec<String> {
    if pinned.len() >= 11 {
        return Vec::new();
    }
    vec![format!("only {} agent files found - the roster is derived from .claude/agents/, so the repository root resolved wrong", pinned.len())]
}

fn untiered(pinned: &Pinned, tiers: &[(&str, &str, &str)]) -> Vec<String> {
    let files: BTreeSet<&str> = pinned.keys().map(String::as_str).collect();
    let table: BTreeSet<&str> = tiers.iter().map(|t| t.0).collect();
    let mut bad = Vec::new();
    let no_row: Vec<&&str> = files.difference(&table).collect();
    if !no_row.is_empty() {
        bad.push(format!("agent files with no recorded tier - add a row to TIERS in rust/gate/crates/checks/src/checks/documents/agent_models.rs: {no_row:?}"));
    }
    let no_file: Vec<&&str> = table.difference(&files).collect();
    if !no_file.is_empty() {
        bad.push(format!(
            "tiers recorded for agents that do not exist - drop their rows from TIERS: {no_file:?}"
        ));
    }
    bad
}

/// Each agent whose `key` is not one of `legal`, with what it says (`<missing>` for none).
fn not_pinned(pinned: &Pinned, key: &str, legal: &[&str]) -> BTreeMap<String, String> {
    pinned
        .iter()
        .filter(|(_, fm)| !fm.get(key).is_some_and(|v| legal.contains(&v.as_str())))
        .map(|(a, fm)| {
            (
                a.clone(),
                fm.get(key).map_or("<missing>", String::as_str).to_owned(),
            )
        })
        .collect()
}

fn inherited_model(pinned: &Pinned) -> Vec<String> {
    let wrong = not_pinned(pinned, "model", &MODELS);
    if wrong.is_empty() {
        return Vec::new();
    }
    vec![format!("a check runs on opus or sonnet, pinned - never inherit, never absent, never fable; set `model:` in the frontmatter: {wrong:?}")]
}

fn inherited_effort(pinned: &Pinned) -> Vec<String> {
    let wrong = not_pinned(pinned, "effort", &EFFORTS);
    if wrong.is_empty() {
        return Vec::new();
    }
    vec![format!("a check pins its effort ({}) - an absent one is the session's; set `effort:` in the frontmatter: {wrong:?}", EFFORTS.join(", "))]
}

fn disagreeing(pinned: &Pinned, tiers: &[(&str, &str, &str)]) -> Vec<String> {
    let field = |fm: &BTreeMap<String, String>, k: &str| fm.get(k).cloned().unwrap_or_default();
    tiers
        .iter()
        .filter_map(|&(a, m, e)| pinned.get(a).map(|fm| (a, m, e, field(fm, "model"), field(fm, "effort"))))
        .filter(|(_, m, e, fm_m, fm_e)| (fm_m.as_str(), fm_e.as_str()) != (*m, *e))
        .map(|(a, m, e, fm_m, fm_e)| format!("{a}: the frontmatter says ({fm_m}, {fm_e}), TIERS says ({m}, {e}) - change both together, recording why"))
        .collect()
}

fn claude_md(pinned: &Pinned, keeps: &[(&str, &str)]) -> Vec<String> {
    let kept: BTreeSet<&str> = keeps.iter().map(|k| k.0).collect();
    let omits = |a: &str| {
        pinned
            .get(a)
            .and_then(|fm| fm.get("omitClaudeMd"))
            .is_some_and(|v| v == "true")
    };
    let mut bad: Vec<String> = kept
        .iter()
        .filter(|a| !pinned.contains_key(**a) || omits(a))
        .map(|a| format!("KEEPS_CLAUDE_MD names an agent that is gone or that carries the field after all - drop the row: {a}"))
        .collect();
    let wrong: Vec<&String> = pinned
        .keys()
        .filter(|a| !kept.contains(a.as_str()) && !omits(a))
        .collect();
    if !wrong.is_empty() {
        bad.push(format!("a defined agent carries `omitClaudeMd: true` in its frontmatter (feature 256, GM 2026-09-19: what a subagent should know belongs in its own specification, not in CLAUDE.md or the memory index) - missing in: {wrong:?}. Add the field, and write into the contract each project rule the check's job depends on."));
    }
    bad
}

fn malformed(tiers: &[(&str, &str, &str)]) -> Vec<String> {
    tiers
        .iter()
        .filter(|(_, m, e)| !MODELS.contains(m) || !EFFORTS.contains(e))
        .map(|(a, m, e)| {
            format!(
                "TIERS row {a} is ({m}, {e}): a model of {MODELS:?} and an effort of {EFFORTS:?}"
            )
        })
        .collect()
}

/// The settings that would put subagents on the 1-hour prompt cache (feature 383 amendment 6, FR-038): it doubles the price of every
/// write a subagent makes in its whole run to keep a few-thousand-token prefix warm; the default 5 minutes covers a fan-out.
fn hour_ttl(paths: &[std::path::PathBuf], root: &Path) -> Vec<String> {
    let hour = re(
        r#"(?i)(?:cacheTtl|CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL)["']?\s*[:=]\s*["']?(?:1h|60m|3600)"#,
    );
    paths
        .iter()
        .filter(|p| hour.is_match(&read(p)).unwrap_or(false))
        .map(|p| format!("{}: a 1-hour subagent cache doubles every write a subagent makes - remove it (feature 383 FR-038)", rel(p, root)))
        .collect()
}

fn ttl_sources(root: &Path) -> Vec<std::path::PathBuf> {
    let mut out: Vec<std::path::PathBuf> = [".claude/settings.json", ".claude/settings.local.json"]
        .iter()
        .map(|p| root.join(p))
        .filter(|p| p.is_file())
        .collect();
    out.extend(files_in(&root.join(".claude/agents"), ".md"));
    out.extend(files_in(&root.join("scripts/container"), ""));
    out
}

fn real() -> Pinned {
    let (pinned, bad) = pinned(&root().join(".claude/agents"));
    assert_eq!(bad, Vec::<String>::new());
    pinned
}

#[test]
fn the_agents_directory_was_found() {
    assert_eq!(found(&real()), Vec::<String>::new());
}

#[test]
fn every_agent_file_has_a_tier_and_every_tier_has_a_file() {
    assert_eq!(untiered(&real(), &TIERS), Vec::<String>::new());
}

#[test]
fn no_agent_inherits_its_model() {
    assert_eq!(inherited_model(&real()), Vec::<String>::new());
}

#[test]
fn no_agent_inherits_its_effort() {
    assert_eq!(inherited_effort(&real()), Vec::<String>::new());
}

#[test]
fn every_agent_file_agrees_with_the_tier_table() {
    assert_eq!(disagreeing(&real(), &TIERS), Vec::<String>::new());
}

#[test]
fn every_agent_launches_without_the_claude_md_files() {
    assert_eq!(claude_md(&real(), &KEEPS_CLAUDE_MD), Vec::<String>::new());
}

#[test]
fn the_tier_table_itself_is_well_formed() {
    assert_eq!(malformed(&TIERS), Vec::<String>::new());
}

#[test]
fn no_setting_puts_subagents_on_the_hour_long_cache() {
    let top = root();
    assert_eq!(hour_ttl(&ttl_sources(&top), &top), Vec::<String>::new());
}

#[test]
fn frontmatter_reads_both_keys_and_refuses_a_file_without_any() {
    let fm = frontmatter("---\nname: x\nmodel: opus\neffort: high\ndescription: a: b\n---\nbody")
        .unwrap();
    assert_eq!(fm.get("model").map(String::as_str), Some("opus"));
    assert_eq!(fm.get("effort").map(String::as_str), Some("high"));
    assert_eq!(fm.get("description").map(String::as_str), Some("a: b"));
    assert_eq!(frontmatter("no frontmatter here"), None);
    let dir = crate::checks::scratch("agent-models");
    crate::checks::tests::put(&dir, "a.md", "---\nmodel: opus\n---\n");
    crate::checks::tests::put(&dir, "b.md", "no frontmatter");
    let (got, bad) = pinned(&dir);
    assert_eq!(got.keys().collect::<Vec<_>>(), ["a"]);
    assert!(bad[0].starts_with("b.md: no YAML frontmatter"), "{bad:?}");
}

#[test]
fn every_defect_of_the_roster_is_named_with_its_fix() {
    let fm = |pairs: &[(&str, &str)]| {
        pairs
            .iter()
            .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
            .collect()
    };
    let mut seeded = Pinned::new();
    seeded.insert(
        "a".to_owned(),
        fm(&[("model", "inherit"), ("effort", "high")]),
    );
    seeded.insert(
        "b".to_owned(),
        fm(&[("model", "opus"), ("omitClaudeMd", "true")]),
    );
    let tiers = [("a", "opus", "high"), ("c", "fable", "high")];
    assert!(found(&seeded)[0].contains("only 2 agent files found"));
    let missing = untiered(&seeded, &tiers);
    assert!(missing[0].contains("no recorded tier") && missing[0].contains("\"b\""));
    assert!(missing[1].contains("do not exist") && missing[1].contains("\"c\""));
    assert!(inherited_model(&seeded)[0].contains("\"a\": \"inherit\""));
    assert!(inherited_effort(&seeded)[0].contains("\"b\": \"<missing>\""));
    assert_eq!(disagreeing(&seeded, &tiers), ["a: the frontmatter says (inherit, high), TIERS says (opus, high) - change both together, recording why"]);
    let keeps = claude_md(&seeded, &[("b", "carries it"), ("gone", "no file")]);
    assert!(keeps[0].ends_with("drop the row: b") && keeps[1].ends_with("drop the row: gone"));
    assert!(keeps[2].contains("missing in: [\"a\"]"), "{keeps:?}");
    assert_eq!(claude_md(&seeded, &[("a", "measured")]).len(), 0);
    assert!(malformed(&tiers)[0].starts_with("TIERS row c is (fable, high)"));
}

#[test]
fn a_seeded_hour_long_cache_is_found() {
    let dir = crate::checks::scratch("agent-ttl");
    crate::checks::tests::put(
        &dir,
        ".claude/settings.json",
        r#"{"env": {"CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL": "1h"}, "experimental": {"cacheTtl": "1h"}}"#,
    );
    crate::checks::tests::put(&dir, "scripts/container/x.sh", "cacheTtl: 5m\n");
    let got = hour_ttl(&ttl_sources(&dir), &dir);
    assert_eq!(got, [".claude/settings.json: a 1-hour subagent cache doubles every write a subagent makes - remove it (feature 383 FR-038)"]);
}
