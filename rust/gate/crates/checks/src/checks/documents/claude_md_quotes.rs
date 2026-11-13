//! Every phrase a hook, a gate or a script quotes from a CLAUDE.md is still in that CLAUDE.md (feature 383 amendment 6, FR-040, plan
//! D44) - the port of `tests/test_claude_md_quotes.py` by feature 449 T133, `ask:449-phase3-remainder` Q3.
//!
//! CLAUDE.md is kept to an always-on core plus an index (the GM 2026-10-17), its detail moved verbatim into topic docs; a refusal that
//! sends a session to `CLAUDE.md "Session clones"` must still find that section there. Three such pointers were already stale when the
//! Python test was written - two copied from gm-assistant's hooks and one naming a heading the root no longer had.

use std::path::{Path, PathBuf};

use super::{files_in, files_under, re, read, rel, root};

const QUOTE: &str =
    r#"((?:[\w./-]+/)?CLAUDE\.md)`?[,:]?\s*(?:[-(]\s*)?\\?["']([A-Z][^"'\\\n]{3,80}?)\\?["']"#;
const NESTED: [&str; 4] = [
    "research/CLAUDE.md",
    "tests/CLAUDE.md",
    "l7r/diagram/CLAUDE.md",
    "scripts/CLAUDE.md",
];

/// The tooling that may quote a CLAUDE.md: the scripts' shell, Python and text files, the agent files, the guard's sources, the
/// settings and the Makefile.
fn sources(root: &Path) -> Vec<PathBuf> {
    let scripts = root.join("scripts");
    let mut out: Vec<PathBuf> = [".sh", ".py", ".txt"]
        .iter()
        .flat_map(|s| files_under(&scripts, s))
        .chain(files_in(&root.join(".claude/agents"), ".md"))
        .chain(files_under(&root.join("rust/guard/src"), ".rs"))
        .filter(|p| !p.components().any(|c| c.as_os_str() == "__pycache__"))
        .chain(
            [root.join(".claude/settings.json"), root.join("Makefile")]
                .into_iter()
                .filter(|p| p.is_file()),
        )
        .collect();
    out.sort();
    out.dedup();
    out
}

/// (the quoting file, the CLAUDE.md it names, the phrase) for each quote in the tooling.
fn quotes(root: &Path) -> Vec<(String, String, String)> {
    let quote = re(QUOTE);
    let mut out = Vec::new();
    for p in sources(root) {
        for caps in quote.captures_iter(&read(&p)).flatten() {
            let name = NESTED
                .iter()
                .find(|n| caps[1].ends_with(*n))
                .unwrap_or(&"CLAUDE.md");
            out.push((
                rel(&p, root),
                (*name).to_owned(),
                l7r_guard::shared::py_text::strip(&caps[2]).to_owned(),
            ));
        }
    }
    out
}

fn unresolved(root: &Path) -> Vec<String> {
    quotes(root)
        .into_iter()
        .filter(|(_, name, phrase)| !read(&root.join(name)).to_lowercase().contains(&phrase.to_lowercase()))
        .map(|(src, name, phrase)| format!("{src}: {name} '{phrase}' - a hook or script quotes a CLAUDE.md phrase that file no longer holds; keep the phrase there, or re-aim the quote"))
        .collect()
}

#[test]
fn every_quoted_claude_md_phrase_resolves() {
    // the extractor finds the tooling's quotes
    assert!(quotes(&root()).len() >= 9);
    assert_eq!(unresolved(&root()), Vec::<String>::new());
}

#[test]
fn a_quote_whose_phrase_moved_out_is_caught() {
    let dir = crate::checks::scratch("claude-md-quotes");
    crate::checks::tests::put(
        &dir,
        "scripts/x-hooks.sh",
        "echo \"(scripts/x-hooks.sh; CLAUDE.md \\\"Session clones\\\")\"\n",
    );
    crate::checks::tests::put(
        &dir,
        "scripts/__pycache__/y.py",
        "# CLAUDE.md \"Session clones\"\n",
    );
    crate::checks::tests::put(
        &dir,
        "rust/guard/src/a.rs",
        "// tests/CLAUDE.md \"Running it\"\n",
    );
    crate::checks::tests::put(&dir, "tests/CLAUDE.md", "## Running it\n");
    crate::checks::tests::put(&dir, "CLAUDE.md", "# Project\n\n## Session clones\n");
    assert_eq!(unresolved(&dir), Vec::<String>::new());
    crate::checks::tests::put(
        &dir,
        "CLAUDE.md",
        "# Project\n\nThe clones moved to docs/session-clones.md.\n",
    );
    assert_eq!(unresolved(&dir), ["scripts/x-hooks.sh: CLAUDE.md 'Session clones' - a hook or script quotes a CLAUDE.md phrase that file no longer holds; keep the phrase there, or re-aim the quote"]);
}
