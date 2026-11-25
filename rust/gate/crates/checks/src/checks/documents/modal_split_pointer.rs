//! The modal checks' M14 counts a split's pointer as a listing (451 T184, the round arbiter's `ask:t184-split-entry-references`): a
//! page reached through a listed page's `<a class="moved">` pointer counts as listed, so an `Entry:` naming a split's source page is
//! clean (the GM 2026-11-23: "nothing needs to cascade simply because a split occurs"). Before it, modal-research found 24 M14
//! findings on 19 pop-ups after the split of 0009 and 0059, every one an Entry line naming the page the text left. An agent file is
//! prose, so what this proves is that the rule is WRITTEN where each agent reads it: modal-research's own REFERENCES contract and the
//! M14 guideline of `dev/modals.md`, in its source and in each modal check's generated copy (`make agent-sync`).
//!
//! D5 carries the split's rule for the `Drawing:` line (451 T234): a split ADDS its target page to each pop-up whose `Drawing:` names
//! the source and whose Depiction states a moved block, mechanically and owing nothing (`make modal-triage`,
//! `record::modals::split_links`). Before it, P3b's move of 0005's rice-shoots section to 0346 left `hamlet/paddy`'s line naming
//! only 0005, and D5 and modal-depiction's LINKS contract, saying nothing of a split, would have read 0346 as a missing link.

use super::{read, root};

#[cfg(test)]
mod tests;

/// The files whose M14 must carry the split pointer's rule.
pub(super) const FILES: [&str; 4] = [
    "dev/modals.md",
    ".claude/agents/modal-research.md",
    ".claude/agents/modal-form.md",
    ".claude/agents/modal-depiction.md",
];

/// The paragraph of `text` opening `head`, from it to the next blank line.
fn para<'a>(text: &'a str, head: &str) -> Option<&'a str> {
    let at = text.find(head)?;
    let rest = &text[at..];
    Some(rest.find("\n\n").map_or(rest, |end| &rest[..end]))
}

/// The M14 guideline's paragraph in `text`.
fn m14(text: &str) -> Option<&str> {
    para(text, "**M14.")
}

/// Each of `texts` ((path, text)) whose M14 does not count a `moved` pointer as a listing, naming its fix.
pub(super) fn missing(texts: &[(&str, String)]) -> Vec<String> {
    let mut bad = Vec::new();
    for (path, text) in texts {
        let holds = |part: &str| part.contains("<a class=\"moved\"") && part.contains("split");
        if !m14(text).is_some_and(holds) {
            bad.push(format!("{path}: its M14 does not count a split's `<a class=\"moved\">` pointer as a listing - restore the clause in dev/modals.md's M14 and run make agent-sync (451 T184, ask:t184-split-entry-references)"));
        }
        if !para(text, "**D5.").is_some_and(holds) {
            bad.push(format!("{path}: its D5 does not say a split adds its `<a class=\"moved\">` target to the `Drawing:` line - restore the clause in dev/modals.md's D5 and run make agent-sync (451 T234)"));
        }
        if path.ends_with("modal-depiction.md") && !para(text, "**LINKS** (D5").is_some_and(holds) {
            bad.push(format!("{path}: its LINKS contract does not say a split adds its `<a class=\"moved\">` target to the `Drawing:` line - restore the clause (451 T234)"));
        }
        if path.ends_with("modal-research.md") {
            let contract = text.find("**REFERENCES** (M14)").map(|at| &text[at..]);
            let para = contract.map(|c| c.find("\n\n").map_or(c, |end| &c[..end]));
            if !para.is_some_and(holds) {
                bad.push(format!("{path}: its REFERENCES contract does not count a split's `<a class=\"moved\">` pointer as a listing - restore the clause (451 T184)"));
            }
        }
    }
    bad
}
