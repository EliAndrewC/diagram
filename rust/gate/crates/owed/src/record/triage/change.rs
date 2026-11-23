//! What a page edit changed, as a pop-up's or a claim's triage needs it (feature 451 T185, T186; the GM 2026-11-23, request.md "the
//! convergence talk"): the blocks whose CLAIM words changed, each changed block paired with its old self, after the edits that cannot
//! change a claim are cleared by the tool - comments, tags, links and glossary marks (gone from a block's words already) and footnote
//! markers (dropped here) - and after a split's moves: a block that stands verbatim on another page
//! the reader still reaches is moved, not removed, and the source page's pointer to it is no claim.
//!
//! What the tool clears is only what cannot state a fact or a label. Whether the rest matters is the `modal-triage` agent's rule,
//! (A)-(C), stated once, in its contract (`.claude/agents/modal-triage.md`); nothing here restates it.

use std::collections::HashSet;
use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::difflib::Tag;
use l7r_shared::checks::pages::{read_page, words};

use super::super::units::re;

/// A footnote marker as a block's words carry it.
static MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"\s*\[\^[^\]\s]+\]"));
static EMPTY_BRACKETS: LazyLock<Regex> = LazyLock::new(|| re(r"\(\s*[,;]?\s*\)"));
static SPACE_BEFORE: LazyLock<Regex> = LazyLock::new(|| re(r"\s+([,.;:)])"));
static SPACES: LazyLock<Regex> = LazyLock::new(|| re(r"\s+"));
/// The pointer a split leaves on its source page: `<a class="moved" href="NNNN-<slug>[.drawing].html">` (T185's form).
static POINTER: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?s)<a\s+class="moved"\s+href="(\d{4}-[a-z0-9-]+(?:\.drawing)?\.html)(?:#[^"]*)?"[^>]*>(.*?)</a>"#,
    )
});
static DIGIT: LazyLock<Regex> = LazyLock::new(|| re(r"\d"));

/// The words a pointer block may carry beyond its link's own (a GUESS, a knob: "The full account of X is now at <link>." is about a
/// dozen; a claim beside a pointer is longer, carries a figure or a note mark, and goes to the agent).
pub const POINTER_WORDS: usize = 25;
/// The `difflib` ratio at which a changed block is paired with its old self (the blind test's pairing, reclassify.md).
pub const PAIR_RATIO: f64 = 0.6;

/// A block's words as a claim reads them: no footnote markers, punctuation spacing settled. An original-language quotation or term
/// on a question page stays: correcting its wording or a character changes what the page says a source says (spec-fidelity MODE 4,
/// 2026-11-23: not in the GM's list); the originals files, where most of them live, reach no pop-up's checks at all.
#[must_use]
pub fn claim_words(block_words: &str) -> String {
    let t = MARKER.replace_all(block_words, "");
    let t = EMPTY_BRACKETS.replace_all(&t, "");
    let t = SPACES.replace_all(&t, " ");
    SPACE_BEFORE.replace_all(&t, "$1").trim().to_owned()
}

/// The question pages a page's pointers name (repository paths), each once, in order.
#[must_use]
pub fn pointer_targets(html: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for c in POINTER.captures_iter(html).map_while(Result::ok) {
        let path = format!("research/questions/{}", &c[1]);
        if !out.contains(&path) {
            out.push(path);
        }
    }
    out
}

/// The words of each pointer's link text on a page.
fn pointer_texts(html: &str) -> Vec<String> {
    POINTER
        .captures_iter(html)
        .map_while(Result::ok)
        .map(|c| words(&c[2]))
        .filter(|w| !w.is_empty())
        .collect()
}

/// `block` with every pointer's link text taken out, as a claim reads it.
fn without_pointers(block: &str, links: &[String]) -> String {
    let mut t = block.to_owned();
    for l in links {
        t = t.replace(l.as_str(), " ");
    }
    claim_words(&t)
}

/// Whether a new block is only a pointer: it carries a pointer's link, no note mark, no figure, and few words beside the link.
fn is_pointer(block: &str, links: &[String]) -> bool {
    links.iter().any(|l| block.contains(l.as_str())) && !block.contains("[^") && {
        let rest = without_pointers(block, links);
        !DIGIT.is_match(&rest).unwrap_or(true) && rest.split(' ').count() <= POINTER_WORDS
    }
}

/// What one page's edit changed, for one reader of it.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Change {
    /// (old, new) blocks paired, their claim words differing.
    pub pairs: Vec<(String, String)>,
    /// Blocks new outright.
    pub added: Vec<String>,
    /// Blocks removed outright, and not moved to a page the reader reaches.
    pub removed: Vec<String>,
    /// Note keys the page no longer carries anywhere.
    pub keys_gone: Vec<String>,
    /// Blocks cleared by the tool: their claim words unchanged (markers, markup), or a pointer.
    pub cleared: usize,
    /// Blocks moved: removed here and standing verbatim on a page the reader reaches, or arrived here from one it reached before.
    pub moved: usize,
    /// Removed blocks that stand verbatim on a page this one does not point to: a split with no pointer, owed as removals.
    pub unpointed: Vec<(String, String)>,
}

impl Change {
    /// Whether nothing is left for the agent.
    #[must_use]
    pub fn is_clear(&self) -> bool {
        self.pairs.is_empty() && self.added.is_empty() && self.removed.is_empty()
    }
}

/// What a reader of one page must still be told of its edit from `old` to `fresh`.
///
/// `reached_now`: every block's words on the other pages the reader reaches now (its pages and their pointers' targets);
/// `reached_before`: every block's words on the pages it reached at its last check; `elsewhere`: (page, its block words) of pages the
/// reader does not reach, where a removed block found is a split with no pointer.
#[must_use]
pub fn page_change<S: std::hash::BuildHasher>(
    old: &str,
    fresh: &str,
    reached_now: &HashSet<String, S>,
    reached_before: &HashSet<String, S>,
    elsewhere: &[(String, HashSet<String, S>)],
) -> Change {
    let was = read_page(old).blocks;
    let now = read_page(fresh).blocks;
    let mut gone: Vec<String> = Vec::new();
    let mut fresh_blocks: Vec<String> = now.iter().map(|b| b.words.clone()).collect();
    for b in &was {
        if let Some(i) = fresh_blocks.iter().position(|w| *w == b.words) {
            fresh_blocks.remove(i);
        } else {
            gone.push(b.words.clone());
        }
    }
    let marks_now: HashSet<&String> = now.iter().flat_map(|b| &b.marks).collect();
    let mut keys_gone: Vec<String> = Vec::new();
    for k in was.iter().flat_map(|b| &b.marks) {
        if !marks_now.contains(k) && !keys_gone.contains(k) {
            keys_gone.push(k.clone());
        }
    }
    let mut change = Change {
        keys_gone,
        ..Change::default()
    };
    let links = pointer_texts(fresh);
    gone.retain(|g| {
        let moved = reached_now.contains(g);
        change.moved += usize::from(moved);
        !moved
    });
    fresh_blocks.retain(|f| {
        let arrived = reached_before.contains(f);
        change.moved += usize::from(arrived);
        !arrived
    });
    for g in &gone {
        if let Some((page, _)) = elsewhere.iter().find(|(_, ws)| ws.contains(g)) {
            change.unpointed.push((g.clone(), page.clone()));
        }
    }
    let mut old_claims: Vec<(String, String)> =
        gone.into_iter().map(|g| (claim_words(&g), g)).collect();
    let mut left: Vec<String> = Vec::new();
    for f in fresh_blocks {
        let claim = claim_words(&f);
        let bare = without_pointers(&f, &links);
        let same = old_claims
            .iter()
            .position(|(c, _)| *c == claim || (!links.is_empty() && *c == bare));
        if let Some(i) = same {
            old_claims.remove(i);
            change.cleared += 1;
        } else if claim.is_empty() || is_pointer(&f, &links) {
            change.cleared += 1;
        } else {
            left.push(f);
        }
    }
    let mut olds: Vec<String> = old_claims
        .into_iter()
        .filter(|(c, _)| {
            let empty = c.is_empty();
            change.cleared += usize::from(empty);
            !empty
        })
        .map(|(_, g)| g)
        .collect();
    for f in left {
        let fw: Vec<&str> = f.split(' ').collect();
        let best = olds
            .iter()
            .enumerate()
            .map(|(i, o)| {
                let ow: Vec<&str> = o.split(' ').collect();
                (i, l7r_gate_core::difflib::ratio(&ow, &fw))
            })
            .filter(|(_, r)| *r >= PAIR_RATIO)
            .max_by(|a, b| a.1.total_cmp(&b.1));
        if let Some((i, _)) = best {
            change.pairs.push((olds.remove(i), f));
        } else {
            change.added.push(f);
        }
    }
    change.removed = olds;
    change
}

/// A word diff of a pair, `[-removed-]` and `{+added+}`, as the blind test's bundles showed it.
#[must_use]
pub fn word_diff(old: &str, fresh: &str) -> String {
    let (a, b): (Vec<&str>, Vec<&str>) = (old.split(' ').collect(), fresh.split(' ').collect());
    let mut out: Vec<String> = Vec::new();
    for (tag, i1, i2, j1, j2) in l7r_gate_core::difflib::opcodes(&a, &b) {
        let (was, now) = (a[i1..i2].join(" "), b[j1..j2].join(" "));
        out.push(match tag {
            Tag::Equal => was,
            Tag::Delete => format!("[-{was}-]"),
            Tag::Insert => format!("{{+{now}+}}"),
            Tag::Replace => format!("[-{was}-] {{+{now}+}}"),
        });
    }
    out.join(" ")
}

/// What a page's split pointers reach: every block's words on the pages they name, read beside it in `qdir` (a claim's triage, whose
/// cited page names its split's other part only through the pointer).
#[must_use]
pub fn reached_by_pointers(html: &str, qdir: &std::path::Path) -> HashSet<String> {
    pointer_targets(html)
        .iter()
        .filter_map(|t| std::path::Path::new(t).file_name())
        .flat_map(|n| block_words(&std::fs::read_to_string(qdir.join(n)).unwrap_or_default()))
        .collect()
}

/// Whether `block`, new on the page `html`, is only a split's pointer.
#[must_use]
pub fn is_pointer_block(block: &str, html: &str) -> bool {
    is_pointer(block, &pointer_texts(html))
}

/// Every block's words of a page's text.
#[must_use]
pub fn block_words(text: &str) -> HashSet<String> {
    read_page(text)
        .blocks
        .into_iter()
        .map(|b| b.words)
        .collect()
}

static SENTENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<=[.;:?!])\s+"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z0-9']+"));

/// The pop-up phrases that state a single case, which a new finding on a page it reads can falsify (the GM's rule of 2026-11-23,
/// needed.md's arm (c)). A knob, measured 2026-11-23 on the landings 085f4598c3 and cce80ca436 (`record modal-triage replay
/// --landing`): with "not recorded" and "no source" in it, the arm fired on 104 of 114 pop-ups, since most Guesses tabs say "not
/// recorded"; with these three, 56 of 114 and none of the 17 page-caused corrections missed.
pub const ABSENCE: [&str; 3] = ["the one case", "only one case", "every plan"];
/// A finding's headline: a list item opening in bold, as the record writes a finding.
static FINDING: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<li>\s*<strong>(.*?)</strong>"));

/// The headlines of the findings `fresh` holds that `old` does not: the new findings an edit adds.
#[must_use]
pub fn new_findings(old: &str, fresh: &str) -> Vec<String> {
    let heads = |t: &str| -> Vec<String> {
        FINDING
            .captures_iter(t)
            .map_while(Result::ok)
            .map(|c| words(&c[1]))
            .collect()
    };
    let was = heads(old);
    heads(fresh)
        .into_iter()
        .filter(|h| !was.contains(h))
        .collect()
}

fn word_list(text: &str) -> Vec<String> {
    WORD.find_iter(&text.to_lowercase())
        .map_while(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect()
}

fn trigrams(w: &[String]) -> Vec<[&str; 3]> {
    w.windows(3)
        .map(|t| [t[0].as_str(), t[1].as_str(), t[2].as_str()])
        .collect()
}

/// The sentences of blocks' claim words, lower-cased, each of more than three words (needed.md's rule script).
fn sentences<'a>(blocks: impl Iterator<Item = &'a String>) -> Vec<String> {
    let mut out = Vec::new();
    for b in blocks {
        let text = claim_words(b).to_lowercase();
        for s in SENTENCE.split(&text).map_while(Result::ok) {
            let s = s.trim();
            if s.split_whitespace().count() > 3 && !out.iter().any(|o: &String| o == s) {
                out.push(s.to_owned());
            }
        }
    }
    out
}

/// THE ECHO RULE (the GM 2026-11-23, needed.md): a sentence `old` held that no page the reader reaches still holds, removed or
/// rewritten, whose changed words the pop-up repeats - a word trigram of the pop-up equal to one of the old sentence's that covers a
/// word changed against its nearest new sentence on the page; the sentence, or None.
#[must_use]
pub fn echo<S: std::hash::BuildHasher>(
    old: &[String],
    page_now: &[String],
    reached_now: &HashSet<String, S>,
    popup: &str,
) -> Option<String> {
    let fresh = sentences(page_now.iter());
    let standing: HashSet<String> = sentences(reached_now.iter())
        .into_iter()
        .chain(fresh.iter().cloned())
        .collect();
    let pop_words = word_list(popup);
    let pop: HashSet<[&str; 3]> = trigrams(&pop_words).into_iter().collect();
    for s in sentences(old.iter())
        .into_iter()
        .filter(|s| !standing.contains(s))
    {
        let ow = word_list(&s);
        let og: HashSet<[&str; 3]> = trigrams(&ow).into_iter().collect();
        let near = fresh
            .iter()
            .map(|n| {
                let nw = word_list(n);
                let shared = trigrams(&nw).into_iter().filter(|t| og.contains(t)).count();
                (shared, n.clone(), nw)
            })
            .max_by(|a, b| (a.0, &a.1).cmp(&(b.0, &b.1)))
            .map_or_else(Vec::new, |n| n.2);
        let mut marked: HashSet<usize> = HashSet::new();
        for (tag, i1, i2, _, _) in l7r_gate_core::difflib::opcodes(&ow, &near) {
            match tag {
                Tag::Equal => {}
                Tag::Insert => marked.extend(i1.saturating_sub(1)..(i1 + 2).min(ow.len())),
                _ => marked.extend(i1..i2),
            }
        }
        let hit = trigrams(&ow)
            .into_iter()
            .enumerate()
            .any(|(i, t)| (i..i + 3).any(|k| marked.contains(&k)) && pop.contains(&t));
        if hit {
            return Some(s);
        }
    }
    None
}

/// Whether the pop-up states a single case ([`ABSENCE`]).
#[must_use]
pub fn says_absence(popup: &str) -> bool {
    let text = popup.to_lowercase();
    ABSENCE.iter().any(|a| text.contains(a))
}

/// Why a page's change, left after the tool's clears, still owes a pop-up reading `popup` its triage, or None (the GM's first filter,
/// 2026-11-23): a note key its Sources names gone from the page (rule C kept reachable), an echo, or a new finding (`found`, from
/// [`new_findings`]) where it states a single case.
#[must_use]
pub fn fires<S: std::hash::BuildHasher>(
    c: &Change,
    page_now: &[String],
    reached_now: &HashSet<String, S>,
    popup: &str,
    found: &[String],
) -> Option<String> {
    if let Some(k) = c.keys_gone.first() {
        return Some(format!("its Sources key {k} is gone from the page"));
    }
    let old: Vec<String> = c
        .pairs
        .iter()
        .map(|p| p.0.clone())
        .chain(c.removed.iter().cloned())
        .collect();
    if let Some(s) = echo(&old, page_now, reached_now, popup) {
        return Some(format!("it repeats words changed in \"{s}\""));
    }
    (!found.is_empty() && says_absence(popup)).then(|| {
        format!(
            "a new finding (\"{}\"), where it states a single case",
            found[0]
        )
    })
}

/// The tool's half of the triage replayed over recorded edits (feature 451 T186's replay): a JSON list of `{id, file, oldraw,
/// newraw}`, one changed block each; a line per edit, `<id>\tcleared|sent\t<why>`.
///
/// # Errors
///
/// Where the list does not parse.
pub fn replay(edits: &str) -> Result<String, String> {
    let list: Vec<serde_json::Value> = serde_json::from_str(edits).map_err(|e| e.to_string())?;
    let field = |e: &serde_json::Value, k: &str| {
        e.get(k)
            .and_then(serde_json::Value::as_str)
            .unwrap_or("")
            .to_owned()
    };
    let mut out = String::new();
    for e in &list {
        let (id, file) = (field(e, "id"), field(e, "file"));
        let why = if file.ends_with(".notes.html") || file.ends_with(".originals.html") {
            "cleared\tno pop-up reads it (Entry: and Drawing: name question and drawing pages)"
        } else if page_change(
            &field(e, "oldraw"),
            &field(e, "newraw"),
            &HashSet::new(),
            &HashSet::new(),
            &[],
        )
        .is_clear()
        {
            "cleared\tno claim word changed (comment, markup, link or marker)"
        } else {
            "sent\tits claim words changed"
        };
        let _ = writeln!(out, "{id}\t{why}");
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
