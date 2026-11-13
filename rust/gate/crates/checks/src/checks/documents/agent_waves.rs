//! The Workflow authorization and the saved `check-wave` workflow (the rest of `tests/test_agent_models.py`, ported by feature 449 T133,
//! `ask:449-phase3-remainder` Q3).
//!
//! Feature 383 amendment 7 (FR-044, SC-032; plan D49): the appended system prompt authorizes Workflow for the named wave jobs only.
//! Claude Code's default prompt says to call Workflow only on the user's explicit request, and outranks CLAUDE.md - without this text a
//! session keeps hand-launching waves, each agent waking the main session once (research R20).

use std::collections::BTreeSet;

use super::agent_models::pinned;
use super::{re, read, root};

/// The GM's draft list (diagram-fanout-workflows.md, recommendation 2); the authorization may add only agents that replaced
/// general-purpose waves (the two triage agents, amendment 6), and what the GM adds himself.
const DRAFT_JOBS: [&str; 14] = [
    "source-applicability",
    "quote-check",
    "settlement-review",
    "entry-drift",
    "modal-depiction",
    "record-format",
    "impl-drift",
    "modal-research",
    "building-review",
    "source-reader",
    "glyph-check",
    "modal-form",
    "round-arbiter",
    "translation-check", // added by the GM, 2026-10-26: "I also do pre-authorize the translation check as a wave job"
];
const REPLACED_GP: [&str; 2] = ["claims-triage", "modal-triage"];
const MISSING: &str =
    "the Workflow authorization is missing from scripts/container/append-system-prompt.md";

/// The jobs the authorization names (its WAVE JOBS list), or None when the authorization is missing.
fn wave_jobs(text: &str) -> Option<Vec<String>> {
    if !text.contains("Workflow is pre-authorized for recurring waves of typed agents")
        || !text.contains("check-wave")
    {
        return None;
    }
    let caps = re(r"(?s)WAVE JOBS:(.*?) - run them")
        .captures(text)
        .ok()??;
    Some(
        re(r"`([\w-]+)`")
            .captures_iter(&caps[1])
            .flatten()
            .map(|c| c[1].to_owned())
            .collect(),
    )
}

fn wave_problems(text: &str, defined: &BTreeSet<String>, decider: &[String]) -> Vec<String> {
    let Some(jobs) = wave_jobs(text) else {
        return vec![MISSING.to_owned()];
    };
    let mut out: Vec<String> = jobs
        .iter()
        .filter(|j| !defined.contains(*j))
        .map(|j| format!("{j}: no .claude/agents/{j}.md - define the agent or drop it from the WAVE JOBS list"))
        .collect();
    out.extend(
        jobs.iter()
            .filter(|j| !DRAFT_JOBS.contains(&j.as_str()) && !REPLACED_GP.contains(&j.as_str()))
            .map(|j| format!("{j}: not a wave job (the GM's draft list, or an agent that replaced a general-purpose wave) - drop it from the WAVE JOBS list")),
    );
    let named: BTreeSet<&String> = jobs.iter().collect();
    let in_hooks: BTreeSet<&String> = decider.iter().collect();
    let differ: Vec<&&String> = named.symmetric_difference(&in_hooks).collect();
    if !differ.is_empty() {
        out.push(format!("the authorization and workflow_hooks.rs's WAVE_JOBS disagree - make the two lists equal: {differ:?}"));
    }
    out
}

/// Every job of the GM's draft that the authorization does not name.
fn unauthorized(text: &str) -> Vec<String> {
    let jobs = wave_jobs(text).unwrap_or_default();
    DRAFT_JOBS
        .iter()
        .filter(|d| !jobs.iter().any(|j| j == *d))
        .map(|d| format!("{d}: a job of the GM's draft that the authorization does not name - add it to WAVE JOBS"))
        .collect()
}

/// `WAVE_JOBS` as `workflow_hooks.rs` declares it, or None where it is gone.
fn wave_decider(text: &str) -> Option<Vec<String>> {
    let caps = re(r"(?s)const WAVE_JOBS: \[&str; \d+\] = \[(.*?)\];")
        .captures(text)
        .ok()??;
    Some(
        re(r#""([\w-]+)""#)
            .captures_iter(&caps[1])
            .flatten()
            .map(|c| c[1].to_owned())
            .collect(),
    )
}

/// Plan D47 (FR-043): the saved workflow types every `agent()` call from its args, returns a schema object, re-launches a unit that came
/// back null once, and runs each declared verify step after its unit with the reply appended.
fn check_wave(js: &str) -> Vec<String> {
    let mut bad = Vec::new();
    for (needle, what) in [
        ("name: 'check-wave'", "the workflow's name"),
        ("args.units", "the units read from its args"),
        ("args.agentType", "the agent type read from its args"),
        (
            "required: ['label', 'verdict', 'text']",
            "the reply schema's required fields",
        ),
        (
            "(got, u) => got || run(args.agentType, u.prompt, u.label, 'Checks')",
            "a null unit re-launched once",
        ),
        ("u.then", "the declared verify steps"),
        ("check before you:", "the reply appended to a verify step"),
        (
            "{ ...replies[i], label: u.label }",
            "405 T131: each reply stamped with its unit's own label",
        ),
    ] {
        if !js.contains(needle) {
            bad.push(format!(
                ".claude/workflows/check-wave.js lost {what}: put back `{needle}`"
            ));
        }
    }
    if !re(r"agent\(prompt, \{ agentType: type, label, phase, schema: REPLY \}\)")
        .is_match(js)
        .unwrap_or(false)
    {
        bad.push(".claude/workflows/check-wave.js: every agent() typed, with the schema - `agent(prompt, { agentType: type, label, phase, schema: REPLY })`".to_owned());
    }
    let calls = re(r"(?<![\w.])agent\(").find_iter(js).count();
    if calls != 1 {
        bad.push(format!(
            ".claude/workflows/check-wave.js has {calls} agent() calls: one, the typed one"
        ));
    }
    bad
}

fn defined() -> BTreeSet<String> {
    pinned(&root().join(".claude/agents"))
        .0
        .into_keys()
        .collect()
}

fn decider() -> Vec<String> {
    wave_decider(&read(
        &root().join("rust/guard/src/guards/workflow_hooks.rs"),
    ))
    .unwrap_or_default()
}

#[test]
fn the_workflow_authorization_names_only_defined_wave_jobs() {
    let text = read(&root().join("scripts/container/append-system-prompt.md"));
    // WAVE_JOBS is not in workflow_hooks.rs when this is empty
    assert!(!decider().is_empty());
    assert_eq!(
        wave_problems(&text, &defined(), &decider()),
        Vec::<String>::new()
    );
    assert_eq!(unauthorized(&text), Vec::<String>::new());
}

#[test]
fn a_seeded_authorization_is_caught() {
    let text = read(&root().join("scripts/container/append-system-prompt.md"));
    let (defined, decider) = (defined(), decider());
    assert_eq!(wave_problems("no such text", &defined, &decider), [MISSING]);
    assert_eq!(
        wave_problems(
            "Workflow is pre-authorized for recurring waves of typed agents, check-wave",
            &defined,
            &decider
        ),
        [MISSING]
    );
    let seeded = text.replace(
        "`modal-triage`",
        "`modal-triage`, `no-such-agent`, `escalation-check`",
    );
    let found = wave_problems(&seeded, &defined, &decider);
    assert!(found
        .iter()
        .any(|f| f.contains("no-such-agent: no .claude/agents")));
    assert!(found
        .iter()
        .any(|f| f.contains("escalation-check: not a wave job")));
    assert!(found.iter().any(|f| f.contains("WAVE_JOBS disagree")));
    let dropped = text.replace("`quote-check`", "`quote`");
    assert!(unauthorized(&dropped)[0].starts_with("quote-check: a job of the GM's draft"));
    assert_eq!(wave_decider("no list"), None);
}

#[test]
fn check_wave_types_every_agent_and_carries_its_follow_up() {
    let js = read(&root().join(".claude/workflows/check-wave.js"));
    assert_eq!(check_wave(&js), Vec::<String>::new());
}

#[test]
fn a_seeded_check_wave_is_caught() {
    let bad = check_wave("x.agent(y) agent(a) agent(b)");
    assert_eq!(bad.len(), 10);
    assert_eq!(
        bad[9],
        ".claude/workflows/check-wave.js has 2 agent() calls: one, the typed one"
    );
}
