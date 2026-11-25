//! A split is a move for a pop-up's `Drawing:` line (451 T234, `dev/modals.md` D5): where a split's `<a class="moved">` pointer on a
//! drawing page a pop-up's `Drawing:` names leads to a drawing page it does not name, and its Depiction states what that page holds,
//! the page is added to the line, mechanically, and owes nothing - the pop-up's `modal-depiction` answer is carried to the new line
//! (`answers::settle`), as a LINKS fix "states no fact, so it settles once applied" (451 T188). M14 leaves the `Entry:` line alone
//! for a split (451 T184); a `Drawing:` link is what the Depiction tab shows its reader, so the line gains the page the rules now
//! live on. Before it, page session P3b moved 0005's rice-shoots section to 0346 and `hamlet/paddy`'s `Drawing:` still named only
//! 0005, whose next modal-depiction read would report 0346 missing (the cascade record, 2026-11-25).
//!
//! "States" is measured as the addition rule measures a phrase (451 T209, [`shared_phrases`]): the Depiction and the target's blocks (a
//! pointer back left out) share at least [`LINK_PHRASES`] word trigrams of [`LINK_WORDS`] words naming a thing. The target's blocks are
//! read whole: a pop-up whose Depiction states a block the target gained since the split is owed the link by D5 all the same. The
//! added entry carries the condition of the listed page it was reached from (`[settlement_form=dispersed]`), none where an
//! unconditional listed page reaches it.

use std::path::Path;

use l7r_shared::checks::pages::read_page;

use super::super::owed::answers;
use super::super::repo::{fail, read_text, Fail};
use super::super::triage::change::{follow, is_pointer_block, shared_phrases};
use super::{depiction_fingerprint, followed, modals_now, parse_tags, Modal, DEPICTION_CHECK, TAG};

#[cfg(test)]
mod tests;

/// How many of a shared trigram's three words must name a thing (the addition rule's phrase; the triage's own is 3,
/// `change::SUBJECT_WORDS`). A KNOB with [`LINK_PHRASES`], measured 2026-11-25 over every pop-up's unlisted split targets in the tree
/// (52 pairs; targets 0346, P3b's, and 0349, P11's; the plan's T234 section): at 3, one pair shares a phrase (`settlement_form--dispersed`
/// and 0349) and `hamlet/paddy`'s Depiction is missed; at 2, eight pairs share one or more.
pub const LINK_WORDS: usize = 2;

/// How many distinct phrases of [`LINK_WORDS`] a Depiction and a split's target must share for it to state the target. A KNOB, measured
/// with [`LINK_WORDS`]: at 3, `hamlet/paddy` and 0346 (3: "dot a plant", "no ruled row", "scatter of shoot") and
/// `settlement_form--dispersed` and 0349 (6, "a scattered settlement" ...), the two the Depictions state; at 2, also `hamlet/well`
/// ("a scattered farm", "within reach of" - its water, not the farm's reach of its rice) and `settlement_form--nucleated` ("gap
/// between the", "the gap between" - one phrase); at 1, four more on a single generic phrase ("the field edge", "beside its field").
pub const LINK_PHRASES: usize = 3;

/// The `Drawing:` entries a split's pointers owe `m`: each drawing page reached from its `Drawing:` pages that the line does not name
/// and whose blocks its Depiction states, in the order the pointers are followed, with the condition of the listed page reaching it.
#[must_use]
pub fn owed_links(root: &Path, m: &Modal) -> Vec<String> {
    let said = m.tag("Depiction");
    if said.is_empty() {
        return Vec::new();
    }
    let listed = m.drawing_files();
    let read = |f: &str| std::fs::read_to_string(root.join(f)).unwrap_or_default();
    let entries: Vec<(String, String)> = m
        .tag("Drawing")
        .split(',')
        .map(|e| {
            let e = e.trim();
            let (path, cond) = e.split_once(char::is_whitespace).unwrap_or((e, ""));
            (path.to_owned(), cond.trim().to_owned())
        })
        .collect();
    followed(root, &listed)
        .into_iter()
        .filter(|t| !listed.contains(t) && t.ends_with(".drawing.html"))
        .filter(|t| {
            let html = read(t);
            let blocks: Vec<String> = read_page(&html)
                .blocks
                .into_iter()
                .map(|b| b.words)
                .filter(|w| !is_pointer_block(w, &html))
                .collect();
            shared_phrases(&blocks.join("\n"), said, LINK_WORDS).len() >= LINK_PHRASES
        })
        .map(|t| {
            let conds: Vec<&str> = entries
                .iter()
                .filter(|(p, _)| follow(std::slice::from_ref(p), read, str::to_owned).contains(&t))
                .map(|(_, c)| c.as_str())
                .collect();
            match conds.iter().find(|c| !c.is_empty()) {
                Some(c) if !conds.contains(&"") => format!("{t} {c}"),
                _ => t,
            }
        })
        .collect()
}

/// `text`, a modal file, with `added` put at the end of its `Drawing:` tag, or in a `Drawing:` line of their own at its end where it
/// has none.
#[must_use]
pub fn with_links(text: &str, added: &[String]) -> String {
    let lines: Vec<&str> = text.split_inclusive('\n').collect();
    let Some(at) = lines.iter().position(|l| l.starts_with("Drawing:")) else {
        let sep = if text.is_empty() || text.ends_with('\n') {
            ""
        } else {
            "\n"
        };
        return format!("{text}{sep}Drawing: {}\n", added.join(", "));
    };
    let mut last = at;
    for (i, l) in lines.iter().enumerate().skip(at + 1) {
        if l.trim().is_empty() || TAG.is_match(l.trim_end()).unwrap_or(false) {
            break;
        }
        last = i;
    }
    let line = lines[last];
    let body = line.trim_end();
    format!(
        "{}{body}, {}{}{}",
        lines[..last].concat(),
        added.join(", "),
        &line[body.len()..],
        lines[last + 1..].concat()
    )
}

/// Add each pop-up's owed links to its `Drawing:` line and carry its `modal-depiction` answer in `store` to the line's new
/// fingerprint; a line per pop-up changed. A pop-up whose `modal-depiction` is not answered as it stands is left alone and named: the
/// edit would turn a triage it is owed into a full check, and the check it is owed reads the pointer and makes the link a LINKS fix.
/// Run after the triage's own clears (`run_bundle`), so a pop-up the split cleared is answered when it is read here.
///
/// # Errors
///
/// Where a modal or a page cannot be read or written: the error says which and why.
pub fn apply(root: &Path, store: &Path) -> Result<Vec<String>, Fail> {
    let mut said = Vec::new();
    for m in modals_now(root, true)? {
        let links = owed_links(root, &m);
        if links.is_empty() {
            continue;
        }
        let names: Vec<&str> = links
            .iter()
            .map(|l| l.rsplit('/').next().unwrap_or(l))
            .collect();
        let slug = format!("{DEPICTION_CHECK}:{}", m.uid());
        let before = depiction_fingerprint(root, &m)?;
        if !answers::answered(store, &slug, &before, "") {
            said.push(format!(
                "{}: Drawing: lacks {} (a split's target its Depiction states) - left: its {DEPICTION_CHECK} is owed, and adds it as a LINKS fix (D5, 451 T234)",
                m.uid(),
                names.join(", ")
            ));
            continue;
        }
        let path = root.join(&m.origin);
        let fresh = with_links(&read_text(&path)?, &links);
        std::fs::write(&path, &fresh).map_err(fail)?;
        let now = Modal {
            tags: parse_tags(&fresh),
            doc: fresh,
            ..m.clone()
        };
        answers::settle(store, &slug, &before, &depiction_fingerprint(root, &now)?)?;
        said.push(format!(
            "{}: Drawing: gained {} (a split's target its Depiction states; D5, 451 T234)",
            m.uid(),
            names.join(", ")
        ));
    }
    Ok(said)
}
