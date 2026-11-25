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
/// A note mark's key as a block's words carry it, `[^key]`.
static KEY: LazyLock<Regex> = LazyLock::new(|| re(r"\[\^([^\]\s]+)\]"));
/// A Markdown link or image, `[text](target)`: its text kept.
static MD_LINK: LazyLock<Regex> = LazyLock::new(|| re(r"!?\[([^\]]*)\]\([^)]*\)"));
/// Code ticks.
static MD_TICKS: LazyLock<Regex> = LazyLock::new(|| re(r"`+"));
/// Emphasis, `**x**`, `__x__`, `*x*` or `_x_`, opening and closing at a word's edge (a `snake_case` name keeps its underscores).
static MD_EMPHASIS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<![\w*])(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1(?![\w*])"));

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

/// A procedure section's block (Markdown, its comments out) as a page's block words read: a link's text kept and its target dropped,
/// code ticks and emphasis dropped, inline HTML read as a page's, so a link, markup or code-tick edit of a section is cleared by the
/// tool as a page's is (feature 451 T191).
#[must_use]
pub fn md_words(block: &str) -> String {
    let t = MD_LINK.replace_all(block, "$1");
    let t = MD_TICKS.replace_all(&t, "");
    let t = MD_EMPHASIS.replace_all(&t, "$2");
    words(&t)
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

/// `files`, then every page a split's pointers reach from them, each once (feature 451 T185, T196): `read` gives a file's text, `place`
/// turns a pointer's repository path into the caller's form - a pop-up's repository path, a claim's page name under its `qdir`. A
/// target's own split is followed too (the size rule may split a split's target again), each page read once, so a cycle ends.
#[must_use]
pub fn follow(
    files: &[String],
    read: impl Fn(&str) -> String,
    place: impl Fn(&str) -> String,
) -> Vec<String> {
    let mut out = files.to_vec();
    let mut i = 0;
    while i < out.len() {
        for t in pointer_targets(&read(&out[i])) {
            let t = place(&t);
            if !out.contains(&t) {
                out.push(t);
            }
        }
        i += 1;
    }
    out
}

/// A change's blocks moved with an edit, as a MANIFEST shows them (feature 451 T194, shared with the claims' by T196): each its old self,
/// its new self on the page `reach` names, and their word diff.
#[must_use]
pub fn moved_edited_lines(c: &Change, reach: &str) -> Vec<String> {
    c.moved_edited
        .iter()
        .map(|(old, new)| {
            format!(
                "Moved with edits (to {reach}):\n  OLD: {old}\n  NEW: {new}\n  WORD DIFF: {}\n",
                word_diff(old, new)
            )
        })
        .collect()
}

/// A change's removed blocks less those it moved with an edit, which [`moved_edited_lines`] shows.
#[must_use]
pub fn removed_unmoved(c: &Change) -> Vec<String> {
    c.removed
        .iter()
        .filter(|w| !c.moved_edited.iter().any(|(o, _)| o == *w))
        .cloned()
        .collect()
}

/// The words of each pointer's link text on a page.
#[must_use]
pub fn pointer_texts(html: &str) -> Vec<String> {
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
    /// Note keys neither the page nor any page the reader reaches carries now (feature 451 T194: a key moved with its block to a
    /// pointer's target is not gone).
    pub keys_gone: Vec<String>,
    /// Blocks cleared by the tool: their claim words unchanged (markers, markup), or a pointer.
    pub cleared: usize,
    /// Blocks moved: removed here and standing verbatim on a page the reader reaches, or arrived here from one it reached before.
    pub moved: usize,
    /// Removed blocks that stand verbatim on a page this one does not point to: a split with no pointer, owed as removals.
    pub unpointed: Vec<(String, String)>,
    /// Removed blocks that moved with an edit (feature 451 T194): (the old block, its version new on a page the reader reaches, paired
    /// at [`PAIR_RATIO`]). Each stays in `removed`, owed as the echo rule reads it, and the MANIFEST shows it as moved, with its diff.
    pub moved_edited: Vec<(String, String)>,
    /// Blocks of `added` that arrived with an edit from a page the reader reached at its last check (451 T209): paired at
    /// [`PAIR_RATIO`] with a block gone from there, so their edit is the source page's echo to read, and they are no addition.
    pub arrived_edited: Vec<String>,
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
    let mut marks_now: HashSet<&str> = now
        .iter()
        .flat_map(|b| &b.marks)
        .map(String::as_str)
        .collect();
    marks_now.extend(
        reached_now
            .iter()
            .flat_map(|w| KEY.captures_iter(w).map_while(Result::ok))
            .filter_map(|c| c.get(1).map(|m| m.as_str())),
    );
    let mut keys_gone: Vec<String> = Vec::new();
    for k in was.iter().flat_map(|b| &b.marks) {
        if !marks_now.contains(k.as_str()) && !keys_gone.contains(k) {
            keys_gone.push(k.clone());
        }
    }
    Change {
        keys_gone,
        ..blocks_change(
            &was.iter().map(|b| b.words.clone()).collect::<Vec<_>>(),
            &now.iter().map(|b| b.words.clone()).collect::<Vec<_>>(),
            &pointer_texts(fresh),
            reached_now,
            reached_before,
            elsewhere,
        )
    }
}

/// [`page_change`]'s half over block words, the one a claim's triage shares (feature 451 T191): `was` and `now` the blocks' words
/// before and after (a page's, or a procedure section's through [`md_words`]), `links` the pointers' link texts on the page now; no
/// note key is read here, so `keys_gone` is empty.
#[must_use]
pub fn blocks_change<S: std::hash::BuildHasher>(
    was: &[String],
    now: &[String],
    links: &[String],
    reached_now: &HashSet<String, S>,
    reached_before: &HashSet<String, S>,
    elsewhere: &[(String, HashSet<String, S>)],
) -> Change {
    let mut gone: Vec<String> = Vec::new();
    let mut fresh_blocks: Vec<String> = now.to_vec();
    for b in was {
        if let Some(i) = fresh_blocks.iter().position(|w| w == b) {
            fresh_blocks.remove(i);
        } else {
            gone.push(b.clone());
        }
    }
    let mut change = Change::default();
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
        let bare = without_pointers(&f, links);
        let same = old_claims
            .iter()
            .position(|(c, _)| *c == claim || (!links.is_empty() && *c == bare));
        if let Some(i) = same {
            old_claims.remove(i);
            change.cleared += 1;
        } else if claim.is_empty() || is_pointer(&f, links) {
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
    moved_with_edits(&mut change, reached_now, reached_before);
    change.arrived_edited = arrived_with_edits(&change.added, reached_now, reached_before);
    change
}

/// The blocks of `added` that pair at [`PAIR_RATIO`] with a block the reader reached before and reaches no more: a block moved here with
/// an edit (451 T209).
fn arrived_with_edits<S: std::hash::BuildHasher>(
    added: &[String],
    reached_now: &HashSet<String, S>,
    reached_before: &HashSet<String, S>,
) -> Vec<String> {
    let left: Vec<Vec<&str>> = reached_before
        .iter()
        .filter(|w| !reached_now.contains(*w))
        .map(|w| w.split(' ').collect())
        .collect();
    added
        .iter()
        .filter(|a| {
            let aw: Vec<&str> = a.split(' ').collect();
            left.iter()
                .any(|lw| l7r_gate_core::difflib::ratio(lw, &aw) >= PAIR_RATIO)
        })
        .cloned()
        .collect()
}

/// Which of a change's removed blocks moved with an edit (feature 451 T194, T184's split): each paired with its closest block new on a
/// page the reader reaches (there now, not at its last check) at [`PAIR_RATIO`]; one whose claim words are its pair's is moved whole.
fn moved_with_edits<S: std::hash::BuildHasher>(
    change: &mut Change,
    reached_now: &HashSet<String, S>,
    reached_before: &HashSet<String, S>,
) {
    let mut arrived: Vec<&String> = reached_now
        .iter()
        .filter(|w| !reached_before.contains(*w))
        .collect();
    if arrived.is_empty() {
        return;
    }
    arrived.sort(); // a tie goes to the last in this order (`max_by`), never the hash set's
    let arrived: Vec<(&String, Vec<&str>)> = arrived
        .into_iter()
        .map(|w| (w, w.split(' ').collect()))
        .collect();
    let mut kept: Vec<String> = Vec::new();
    for old in std::mem::take(&mut change.removed) {
        let ow: Vec<&str> = old.split(' ').collect();
        let best = arrived
            .iter()
            .map(|(w, aw)| (*w, l7r_gate_core::difflib::ratio(&ow, aw)))
            .filter(|(_, r)| *r >= PAIR_RATIO)
            .max_by(|a, b| a.1.total_cmp(&b.1));
        match best {
            Some((w, _)) if claim_words(w) == claim_words(&old) => change.moved += 1,
            Some((w, _)) => {
                change.moved_edited.push((old.clone(), w.clone()));
                kept.push(old);
            }
            None => kept.push(old),
        }
    }
    change.removed = kept;
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

/// THE ADDITION RULE's phrase (451 T209, T212; the cascade test, 2026-11-24): how many of a word trigram's three words must name a thing
/// ([`NOT_SUBJECT`] none of them) for a sentence new on a page that repeats it to be sent on. A KNOB, measured 2026-11-24 by the landing
/// replay of 085f4598c3, cce80ca436 and 7fc9f06512 (the plan's T209 section): at 3, 18 of the 167 (pop-up, page) pairs the tool cleared
/// before are sent, the stables Depiction's miss among them, and none of the 17 page-caused corrections is missed; at 2 ("the main
/// gate", "a samurai house"), 65, most of them a page's own topic repeated.
pub const SUBJECT_WORDS: usize = 3;
/// Words that name no subject: function words, and the record's own words for its sources and its plans, which every page and pop-up
/// repeats ("no page we read", "our plans draw", "is a GUESS").
const NOT_SUBJECT: [&str; 75] = [
    "a", "about", "all", "also", "an", "and", "any", "are", "as", "at", "be", "been", "both",
    "but", "by", "can", "could", "did", "do", "draw", "drawn", "each", "every", "few", "for",
    "from", "gives", "given", "guess", "had", "has", "have", "how", "if", "in", "into", "is", "it",
    "its", "map", "may", "more", "most", "no", "none", "nor", "not", "of", "on", "one", "only",
    "or", "our", "own", "page", "plan", "read", "recorded", "say", "so", "some", "source", "than",
    "that", "the", "their", "them", "there", "they", "this", "to", "was", "we", "were", "what",
];
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
    let mut fresh = sentences(page_now.iter());
    let standing: HashSet<String> = sentences(reached_now.iter())
        .into_iter()
        .chain(fresh.iter().cloned())
        .collect();
    // the nearest new sentence is sought on the page and the pages the reader reaches (feature 451 T194: a sentence moved with a small
    // edit is compared with its moved self), each candidate's words read once
    fresh.extend(
        standing
            .iter()
            .filter(|s| !fresh.contains(s))
            .cloned()
            .collect::<Vec<_>>(),
    );
    let near_words: Vec<(String, Vec<String>)> = fresh
        .into_iter()
        .map(|n| {
            let w = word_list(&n);
            (n, w)
        })
        .collect();
    let pop_words = word_list(popup);
    let pop: HashSet<[&str; 3]> = trigrams(&pop_words).into_iter().collect();
    for s in sentences(old.iter())
        .into_iter()
        .filter(|s| !standing.contains(s))
    {
        let ow = word_list(&s);
        let og: HashSet<[&str; 3]> = trigrams(&ow).into_iter().collect();
        let near = near_words
            .iter()
            .map(|(n, nw)| {
                let shared = trigrams(nw).into_iter().filter(|t| og.contains(t)).count();
                (shared, n, nw)
            })
            .max_by(|a, b| (a.0, a.1).cmp(&(b.0, b.1)))
            .map_or_else(Vec::new, |n| n.2.clone());
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

/// THE ECHO RULE read from a rewrite's new side (feature 451 T191, the claims' measured miss): a sentence a rewritten block holds that
/// its old self did not, whose changed words `reader` repeats as a word trigram ([`echo`] with the pair's sides swapped); the sentence,
/// or None. A claim whose label a page rewrites ("a tree beside it ... is a GUESS") repeats the new words, not the dropped ones.
#[must_use]
pub fn echo_rewritten(c: &Change, reader: &str) -> Option<String> {
    let (old, new): (Vec<String>, Vec<String>) = c.pairs.iter().cloned().unzip();
    echo(&new, &old, &HashSet::<String>::new(), reader)
}

/// A text's words, lower-cased, each with a possessive's `'s` and a plural's `s` taken off.
fn stems(text: &str) -> Vec<String> {
    word_list(text)
        .into_iter()
        .map(|w| {
            let w = w.trim_end_matches("'s").trim_end_matches('\'');
            match w.strip_suffix('s') {
                Some(stem) if stem.len() > 2 && !stem.ends_with('s') => stem.to_owned(),
                _ => w.to_owned(),
            }
        })
        .filter(|w| !w.is_empty())
        .collect()
}

/// Whether a word names a thing: not one of [`NOT_SUBJECT`], read as stemmed.
fn names_a_thing(w: &str) -> bool {
    !NOT_SUBJECT.contains(&w) && !NOT_SUBJECT.contains(&format!("{w}s").as_str())
}

/// A text's word trigrams that hold `words` words naming a thing.
fn subject_trigrams(text: &str, words: usize) -> HashSet<String> {
    stems(text)
        .windows(3)
        .filter(|t| t.iter().filter(|w| names_a_thing(w)).count() >= words)
        .map(|t| t.join(" "))
        .collect()
}

/// The phrases two texts share, sorted: each a word trigram of `words` words naming a thing, as the addition rule reads a phrase (451
/// T234: a split's target read against a Depiction, `split_links`).
#[must_use]
pub fn shared_phrases(one: &str, other: &str, words: usize) -> Vec<String> {
    let mut shared: Vec<String> = subject_trigrams(one, words)
        .intersection(&subject_trigrams(other, words))
        .cloned()
        .collect();
    shared.sort();
    shared
}

/// THE ADDITION RULE (451 T209, T212; the cascade test, 2026-11-24): a sentence of a block new outright on the page that repeats a
/// phrase of what `reader` states - a word trigram holding [`SUBJECT_WORDS`] words naming a thing - so that it says something new of the
/// reader's own subject, whether it adds to it, narrows it or falsifies an absence or a single case it states; (the new sentence, the
/// phrase), or None. Only blocks new outright are read: a rewritten block is the echo's, and a block moved from a page the reader
/// reached, with an edit or none, is no addition.
#[must_use]
pub fn addition(c: &Change, reader: &str) -> Option<(String, String)> {
    let words = SUBJECT_WORDS;
    let said = subject_trigrams(reader, words);
    let new = c.added.iter().filter(|a| !c.arrived_edited.contains(a));
    sentences(new).into_iter().find_map(|s| {
        let mut shared: Vec<String> = subject_trigrams(&s, words)
            .intersection(&said)
            .cloned()
            .collect();
        shared.sort();
        shared.into_iter().next().map(|t| (s, t))
    })
}

/// Why a page's change, left after the tool's clears, still owes a pop-up reading `popup` its triage, or None (the GM's first filter,
/// 2026-11-23): a note key its Sources names gone from the page (rule C kept reachable), an echo, or an addition ([`addition`], 451
/// T209: a sentence new on the page that shares a subject with one the pop-up states). `_found`, the new findings' headlines, is read no
/// more: the three fixed phrases it was read with ("the one case", "only one case", "every plan") sent a pop-up stating one on any new
/// finding, related or not, and the addition rule reads every new block against what the pop-up states (451 T212); the parameter stays
/// while the claims crate's caller passes it.
#[must_use]
pub fn fires<S: std::hash::BuildHasher>(
    c: &Change,
    page_now: &[String],
    reached_now: &HashSet<String, S>,
    popup: &str,
    _found: &[String],
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
    addition(c, popup)
        .map(|(s, t)| format!("a sentence new on the page, \"{s}\", repeats its phrase \"{t}\""))
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
