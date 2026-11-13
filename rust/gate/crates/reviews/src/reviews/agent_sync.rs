//! `l7r-gate reviews agent-sync [--check]` (feature 449 T136, the round arbiter's `ask:449-phase3-remainder`): `scripts/reviews/agent_sync.py`'s
//! port behind `make agent-sync`, and the one writer of the generated part of the three modal checks' agent files.
//!
//! WHY the text lives there (feature 383 amendment 6, FR-032, plan D35): an agent file is the agent's system prompt, the first thing in
//! every dispatch, so it is read from the prompt cache by every dispatch of its type after the first; a bundle is read after the
//! prompt, which differs per unit, so every copy of a text in a bundle is written to the cache fresh. The three modal checks' bundles
//! each carried the modal guidelines, 15-17k characters, 339 times between 2026-10-10 and 10-17 (research R13). The GM, 2026-10-17:
//! *"any context that subagents share in common is put either into their system prompt, ideally, or ... at the very beginning of the
//! prompt"*.
//!
//! A section is the source's text between `<!-- generated: <source> -->` and `<!-- /generated: <source> -->`; everything else in the
//! agent file is the agent's own and is left as it is. Edit the source (`dev/modals.md`), never the copy. Files are read as Python's
//! text mode read them (`\r\n` and `\r` as `\n`); an unreadable, missing or undecodable file, or an unwritable agent file, is the
//! Python's raise: exit 1, a `Traceback` line, and the agent files written before it left written.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::ledger::raised;
use super::reply;
use crate::record::args::{parse, Spec};
use crate::record::bundle::rstrip;
use crate::record::repo::universal;
use crate::Reply;

const MODALS: &[&str] = &["dev/modals.md", "dev/modals-particular.md"];
/// Each agent file and the sources it carries, in order.
pub type SyncTable<'a> = &'a [(&'a str, &'a [&'a str])];
/// The agent files this tool writes.
pub const SYNC: SyncTable<'static> = &[
    (".claude/agents/modal-form.md", MODALS),
    (".claude/agents/modal-depiction.md", MODALS),
    (".claude/agents/modal-research.md", MODALS),
];
/// The heading the generated part opens under.
pub const HEAD: &str = "## The guidelines (generated - `make agent-sync` writes them from their sources; edit the source, not this copy)";

/// A generated section left inside the agent's own part (`re.S`, the shortest section first).
static SECTION: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?s)\n<!-- generated: [^>]*-->.*?<!-- /generated: [^>]*-->\n?")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// The agent file with its generated part (HEAD and the sections after it) written from `sources`, in their order.
#[must_use]
pub fn render(agent_text: &str, sources: &[(&str, String)]) -> String {
    let own = agent_text
        .split_once(&format!("\n{HEAD}"))
        .map_or(agent_text, |(own, _)| own);
    let own = SECTION.replace_all(rstrip(own), "\n").into_owned();
    let sections: Vec<String> = sources
        .iter()
        .map(|(s, t)| {
            format!(
                "<!-- generated: {s} -->\n{}\n<!-- /generated: {s} -->\n",
                rstrip(t)
            )
        })
        .collect();
    format!("{}\n\n{HEAD}\n\n{}", rstrip(&own), sections.join("\n"))
}

/// `path.read_text(encoding="utf-8")`: strict UTF-8, newlines as text mode reads them.
fn read(path: &Path) -> Result<String, String> {
    std::fs::read_to_string(path)
        .map(|t| universal(&t))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// The agent file as it should be, and as it is.
fn wanted(root: &Path, agent: &str, sources: &[&str]) -> Result<(String, String), String> {
    let path = root.join(agent);
    let text = read(&path)?;
    let mut read_sources = Vec::with_capacity(sources.len());
    for s in sources {
        read_sources.push((*s, read(&root.join(s))?));
    }
    Ok((render(&text, &read_sources), read(&path)?))
}

/// The agent files whose generated part differs from their sources.
///
/// # Errors
///
/// An agent file or a source unreadable.
pub fn stale<'a>(
    root: &Path,
    sync: SyncTable<'a>,
) -> Result<Vec<(&'a str, &'a [&'a str])>, String> {
    let mut out = Vec::new();
    for (agent, sources) in sync {
        let (want, have) = wanted(root, agent, sources)?;
        if want != have {
            out.push((*agent, *sources));
        }
    }
    Ok(out)
}

/// Each stale agent file written from its sources; the ones written.
///
/// # Errors
///
/// A file unreadable or an agent file unwritable: the ones before it stay written, as the Python left them.
pub fn write<'a>(root: &Path, sync: SyncTable<'a>) -> Result<Vec<&'a str>, String> {
    let changed = stale(root, sync)?;
    for (agent, sources) in &changed {
        let (want, _) = wanted(root, agent, sources)?;
        let path = root.join(agent);
        std::fs::write(&path, want).map_err(|e| format!("{}: {e}", path.display()))?;
    }
    Ok(changed.into_iter().map(|(agent, _)| agent).collect())
}

/// `agent_sync.py [--check]` over the clone at `root`: write the stale agent files and say which, or with `--check` name each and exit 1.
#[must_use]
pub fn cli(args: &[String], root: &Path, sync: SyncTable<'_>) -> Reply {
    let p = match parse(args, &[Spec::flag("--check")]) {
        Ok(p) => p,
        Err(why) => {
            return reply(
                String::new(),
                format!("usage: l7r-gate reviews agent-sync [--check]\nl7r-gate reviews agent-sync: error: {why}\n"),
                2,
            )
        }
    };
    if p.on("--check") {
        return match stale(root, sync) {
            Ok(bad) => {
                let mut out = String::new();
                for (agent, sources) in &bad {
                    let _ = writeln!(
                        out,
                        "agent-sync: {agent} differs from {} - run `make agent-sync` and commit the agent file",
                        sources.join(", ")
                    );
                }
                reply(out, String::new(), i32::from(!bad.is_empty()))
            }
            Err(why) => raised(String::new(), "agent-sync", &why),
        };
    }
    match write(root, sync) {
        Ok(changed) => {
            let tail = if changed.is_empty() {
                " - all in step".to_owned()
            } else {
                format!(": {}", changed.join(", "))
            };
            reply(
                format!(
                    "agent-sync: {} agent file(s) written{tail}\n",
                    changed.len()
                ),
                String::new(),
                0,
            )
        }
        Err(why) => raised(String::new(), "agent-sync", &why),
    }
}

#[cfg(test)]
mod tests;
