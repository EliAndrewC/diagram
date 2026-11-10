//! `check-bundle-hooks` (feature 250; feature 449 T043, T86): a record check reads a BUNDLE, not the repository - reading a file under it attaches every `CLAUDE.md` above that file (about 28,000 tokens a check, research
//! R1). A dispatch of a record check whose prompt names a repository file and no bundle is refused with the `make check-bundle` command for what it names; a bundle's owed-checks line is enforced (feature 311); and each dispatch
//! first waits on its task's decisions (feature 375 FR-003(a)) and is recorded in the check state.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::checks::handle;
use crate::shared::escape;
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "check-bundle-hooks",
    events: &["PreToolUse"],
    matcher: "Agent",
    decide,
};

const NAME: &str = "check-bundle";
/// The checks whose contract reads a bundle (`.claude/agents/<name>.md`, "Read the BUNDLE").
const CHECKS: [&str; 12] = [
    "quote-check",
    "record-format",
    "source-applicability",
    "source-reader",
    "entry-drift",
    "record-style",
    "translation-check",
    "intro-check",
    "impl-drift",
    "modal-form",
    "modal-research",
    "modal-depiction",
];
const MODALS: [&str; 3] = ["modal-form", "modal-research", "modal-depiction"];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static DECIDE_OK: LazyLock<Regex> = LazyLock::new(|| re(r#"\bDECIDE_OK="([^"]*)""#));
static BUNDLE_NAMED: LazyLock<Regex> =
    LazyLock::new(|| re(r#"[^\s`"]*/MANIFEST\.md|/tmp/l7r-check/[^\s`")]+"#));
static CHECK_BUNDLE_OK: LazyLock<Regex> = LazyLock::new(|| re(r#"CHECK_BUNDLE_OK="([^"]*)""#));
static CHECK_NOT_OWED_OK: LazyLock<Regex> = LazyLock::new(|| re(r#"CHECK_NOT_OWED_OK="([^"]*)""#));
static MANIFESTS: LazyLock<Regex> = LazyLock::new(|| re(r#"(/[^\s`"<>)]*MANIFEST\.md)"#));
static OWED_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^owed-checks: *(.*)$"));
static REPO_PATHS: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?<![\w.-])(?:/diagram(?:/\.clones/[\w.-]+)?/)?research/[^\s`"<>)]+"#));
static QUESTION: LazyLock<Regex> = LazyLock::new(|| re(r"research/questions/(\d{4})-[^/]*\.html$"));
static WORK_CITED: LazyLock<Regex> =
    LazyLock::new(|| re(r"research/sources/010-works-cited/\d+-([a-z0-9-]+)\.html$"));

fn fire(
    event: &Event,
    kind: &str,
    detail: &str,
    rule: &str,
    context: Option<&str>,
    session: &Session,
) {
    let _ = log::write(&log::Entry {
        guard: NAME,
        event: kind,
        detail,
        rule,
        context: context.map(|c| json!(c)),
        input: &event.input,
        session_name: &session.name(),
    });
}

fn capture(pattern: &Regex, text: &str) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|g| g.as_str().to_owned()))
}

fn git_root(cwd: &str, here: &Path) -> String {
    let at = if cwd.is_empty() { "." } else { cwd };
    ask(here, "git", &["-C", at, "rev-parse", "--show-toplevel"], "")
        .out
        .trim()
        .to_owned()
}

/// FR-003(a) DECIDE FIRST: a check waits for its task's decisions' verdict. The refusal's text and rule, or None; an escape is logged here.
fn decide_first(
    event: &Event,
    session: &Session,
    atype: &str,
    prompt: &str,
    here: &Path,
    tree: &Path,
) -> Option<Answer> {
    if let Some(why) = capture(&DECIDE_OK, prompt)
        .filter(|w| w.split_whitespace().count() >= 2 && w.chars().count() >= 8)
    {
        fire(event, "escaped", &why, "decide-ok", None, session);
        return None;
    }
    let root = git_root(field(&event.input, "cwd"), here);
    if root.is_empty() {
        return None;
    }
    let said = ask(
        here,
        &tree.join("scripts/gates/l7r-gate.sh").to_string_lossy(),
        &["plan", "decided", &root],
        "",
    );
    if said.code != 1 || said.out.trim().is_empty() {
        return None;
    }
    let named = BUNDLE_NAMED
        .find(prompt)
        .ok()
        .flatten()
        .map_or("its prompt", |m| m.as_str());
    let line = format!("{atype} on {named}: {}", said.out.trim());
    fire(
        event,
        "blocked",
        "dispatch",
        "decide-first",
        Some(&line),
        session,
    );
    Some(Answer::Refuse(format!("\nBLOCKED: {line}\n(or DECIDE_OK=\"<reason>\" in the prompt; scripts/hooks/check-bundle-hooks.sh, feature 375)\n")))
}

/// A check the bundle owes, or what its MANIFEST owes instead: `Some((manifest, owes))` when `atype` is not owed, the MANIFEST's words.
fn not_owed_on(atype: &str, prompt: &str) -> Option<(String, String)> {
    if atype == "record-style" {
        return None;
    }
    for path in MANIFESTS
        .captures_iter(prompt)
        .flatten()
        .map(|c| c[1].to_owned())
    {
        let Ok(text) = std::fs::read_to_string(&path) else {
            continue;
        };
        let owed = capture(&OWED_LINE, &text);
        if owed
            .as_deref()
            .is_none_or(|o| !o.split_whitespace().any(|c| c == atype))
        {
            let listed = owed.map_or_else(
                || "(none - a bundle from before feature 311: build it again)".to_owned(),
                |o| o.trim().to_owned(),
            );
            return Some((path, listed));
        }
    }
    None
}

fn not_owed_refusal(
    event: &Event,
    session: &Session,
    atype: &str,
    mp: &str,
    owes: &str,
) -> Vec<Answer> {
    fire(
        event,
        "blocked",
        &format!("{atype} not owed on {mp}"),
        "not-owed",
        None,
        session,
    );
    vec![Answer::Refuse(format!(
        "\n\x1b[1mBLOCKED: `{atype}` is not owed on this bundle.\x1b[0m\n\nIts MANIFEST ({mp}) owes: {owes}\nA check is owed only where the words it reads changed (`make record-owed` lists every unit, feature 311) -\nre-running it on words it already passed is the waste the GM named. Dispatch only what is owed;\na check the GM asked for, or a backfill: CHECK_NOT_OWED_OK=\"<why>\" in the prompt.\n(scripts/hooks/check-bundle-hooks.sh; feature 311)\n"
    ))]
}

fn command_for(path: &str, atype: &str) -> Option<String> {
    if let Some(key) = capture(&WORK_CITED, path) {
        let whole = if atype == "source-reader" {
            " WHOLE=1"
        } else {
            ""
        };
        return Some(format!("make check-bundle KEY={key}{whole}"));
    }
    capture(&QUESTION, path).map(|q| {
        let scoped = if atype == "record-style" || atype == "translation-check" {
            format!(" FOR={atype}")
        } else {
            String::new()
        };
        format!("make check-bundle Q={q}{scoped}")
    })
}

fn repository_refusal(
    event: &Event,
    session: &Session,
    atype: &str,
    paths: &[String],
) -> Vec<Answer> {
    let mut cmds: Vec<String> = if MODALS.contains(&atype) {
        vec![format!(
            "make modal-bundle KIND=<the modal class> FOR={atype}"
        )]
    } else {
        paths.iter().filter_map(|p| command_for(p, atype)).collect()
    };
    let mut seen = std::collections::HashSet::new();
    cmds.retain(|c| seen.insert(c.clone()));
    if cmds.is_empty() {
        cmds.push("make check-bundle Q=<question number>   (or KEY=<registry key>)".to_owned());
    }
    fire(
        event,
        "blocked",
        &format!("{atype} dispatched into the repository"),
        "repo-path",
        None,
        session,
    );
    let listed: String = cmds.iter().map(|c| format!("    {c}\n")).collect();
    vec![Answer::Refuse(format!(
        "\n\x1b[1mBLOCKED: this `{atype}` dispatch points the agent at files IN the repository.\x1b[0m\n\nReading one attaches every CLAUDE.md above it - about 28,000 tokens, 55-65% of a check's context\non the measured runs (feature 250, research R1). Copy what it reads out first:\n\n{listed}\nthen re-send the dispatch naming the MANIFEST.md it prints (and nothing under /diagram).\nA file the bundle lacks: EXTRA=\"<path> ...\" on the same command. A check that truly cannot be\nbundled: CHECK_BUNDLE_OK=\"<why>\" in the prompt.\n(scripts/hooks/check-bundle-hooks.sh; feature 250)\n"
    ))]
}

fn bundle_verdict(event: &Event, session: &Session, atype: &str, prompt: &str) -> Vec<Answer> {
    if let Some(reason) = capture(&CHECK_BUNDLE_OK, prompt) {
        if escape::enough(&reason) {
            fire(event, "escaped", &reason, "check-bundle-ok", None, session);
            return Vec::new();
        }
        fire(
            event,
            "blocked",
            &format!("CHECK_BUNDLE_OK=\"{reason}\""),
            "CHECK_BUNDLE_OK-no-reason",
            None,
            session,
        );
        return vec![Answer::Refuse("BLOCKED: CHECK_BUNDLE_OK needs a REASON - two words and eight characters - so the audit says why.\n".to_owned())];
    }
    if prompt.contains("MANIFEST.md") {
        if let Some(reason) = capture(&CHECK_NOT_OWED_OK, prompt) {
            if escape::enough(&reason) {
                fire(
                    event,
                    "escaped",
                    &reason,
                    "check-not-owed-ok",
                    None,
                    session,
                );
                return Vec::new();
            }
            fire(
                event,
                "blocked",
                &format!("CHECK_NOT_OWED_OK=\"{reason}\""),
                "CHECK_NOT_OWED_OK-no-reason",
                None,
                session,
            );
            return vec![Answer::Refuse("BLOCKED: CHECK_NOT_OWED_OK needs a REASON - two words and eight characters - so the audit says why.\n".to_owned())];
        }
        if let Some((mp, owes)) = not_owed_on(atype, prompt) {
            return not_owed_refusal(event, session, atype, &mp, &owes);
        }
        fire(
            event,
            "permitted",
            &format!("{atype} reads a bundle"),
            "bundle-named",
            None,
            session,
        );
        return Vec::new();
    }
    let paths: Vec<String> = REPO_PATHS
        .find_iter(prompt)
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect();
    if paths.is_empty() {
        fire(
            event,
            "permitted",
            &format!("{atype} names no repository file"),
            "no-repo-path",
            None,
            session,
        );
        return Vec::new();
    }
    repository_refusal(event, session, atype, &paths)
}

/// The record check's two gates (decide first, the check's own bundle rule) and its counted dispatch.
fn judge(event: &Event, session: &Session, here: &Path, tree: &Path) -> Vec<Answer> {
    if event.tool() != "Agent" {
        return Vec::new();
    }
    let null = Value::Null;
    let ti = event.input.get("tool_input").unwrap_or(&null);
    let (atype, prompt) = (field(ti, "subagent_type"), field(ti, "prompt"));
    let is_check = CHECKS.contains(&atype);
    if is_check {
        if let Some(a) = decide_first(event, session, atype, prompt, here, tree) {
            return vec![a];
        }
    }
    let held = handle::handle("dispatch", &event.input, None);
    if !held.is_empty() {
        let text = handle::blocked_text(&held);
        fire(
            event,
            "blocked",
            "dispatch",
            "round-open-or-capped",
            Some(&text),
            session,
        );
        return vec![Answer::Refuse(text)];
    }
    if is_check {
        return bundle_verdict(event, session, atype, prompt);
    }
    Vec::new()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(event, session, &here, &tree)
}

#[cfg(test)]
mod tests;
