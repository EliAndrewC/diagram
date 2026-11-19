//! What a pattern can find against the style guide, listed for `record-style` (`scripts/record/style_prepass.py`, feature 292; ported by
//! feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`): the metric figure with no conversion, the visible "GM", the paragraph
//! over 150 words, the absence note in its old form and the kanji without its gloss (each a finding), and the sentences resting on an
//! absence note, the years in lead lines and the lead lines themselves (each to rule on). `l7r-gate record style-prepass` is the
//! command (the `bundle` crate), and `owed::translation` reads [`glosses`] in process.

use std::collections::{BTreeMap, HashSet};
use std::hash::BuildHasher;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::py_text::{split, strip};

use crate::pyre::py;
use crate::re;

/// The longest a paragraph or a bullet's own text may run, in words of visible text (STYLE.md 3).
pub const MAX_WORDS: usize = 150;

static METRIC: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r"(?<![\w.])(\d[\d,]*(?:\.\d+)?(?:\s*(?:-|to)\s*\d[\d,]*(?:\.\d+)?)?)\s*(km2|km|ha|m2|cm|mm|m|kilometers?|hectares?|meters?|centimeters?|millimeters?|square meters?)(?![\w])",
    )
});
static CONVERTED: LazyLock<Regex> =
    LazyLock::new(|| py(r"^\s*\(~[\d,.\-\sx]+(?:ft|in|acres?|sq ft|square feet|miles?)\b"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static QUOTED: LazyLock<Regex> =
    LazyLock::new(|| re("(?s)<q>.*?</q>|\u{300c}.*?\u{300d}|&quot;.*?&quot;|\"[^\"]*\""));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static SPACES: LazyLock<Regex> = LazyLock::new(|| py(r"\s+"));
static BLOCK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?s)<p[^>]*>(.*?)</p>|<li[^>]*>(.*?)(?=<ul>|<ol>|</li>)"));
static SUP: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<sup[^>]*>.*?</sup>"));
static OLD_ABSENCE: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"(?s)<li data-note="([^"]+)">\s*no publicly readable source\s*\(searched"#)
});
static FOREIGN: LazyLock<Regex> = LazyLock::new(|| {
    re(r"[\x{3040}-\x{30ff}\x{3400}-\x{9fff}\x{ac00}-\x{d7af}\x{f900}-\x{faff}]+")
});
/// The one form a term in its own script takes in our words: the characters, then `(romaji, «meaning»)` once its quotes are set aside.
static GLOSS: LazyLock<Regex> = LazyLock::new(|| py(r#"^\s*\(([^()",]+), «([^»]+)»\)"#));
static ORIG: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<span class="orig"[^>]*>.*?</span>"#));
static GLOSS_QUOTES: LazyLock<Regex> = LazyLock::new(|| {
    re("(\\([^()\",]+, )(?:\"|&quot;|\u{201c})([^\"\u{201c}\u{201d}&]+)(?:\"|&quot;|\u{201d})(\\))")
});
static GM: LazyLock<Regex> = LazyLock::new(|| py(r"\bGM(?:'s)?\b"));
static LEAD: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?s)<li>\s*<strong>(.*?)</strong>\s*<br>\s*(.*?)(?=</li>|<ul>)"));
static YEAR: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\d-])1[0-9]{3}(?![\d])"));
static SENTENCE_END: LazyLock<Regex> =
    LazyLock::new(|| py("(?<=[.!?])\\s+(?=[A-Z<(\"\u{201c}\u{300c}])"));
static ABSENT: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<li data-note="([^"]+)">\s*no publicly readable source"#));
static PARAGRAPH: LazyLock<Regex> = LazyLock::new(|| py(r"</?(?:p|li)\b[^>]*>"));
static FOOTED: LazyLock<Regex> = LazyLock::new(|| re(r"([.!?])((?:<sup[^>]*></sup>)+)"));
static DATA_NOTE: LazyLock<Regex> = LazyLock::new(|| re(r#"data-note="([^"]+)""#));

fn sub(pattern: &Regex, text: &str, with: &str) -> String {
    pattern.replace_all(text, with).into_owned()
}

/// `text[max(0, start - before) : end + after].strip()`, the bounds characters of `text`.
fn around(text: &str, start: usize, end: usize, before: usize, after: usize) -> String {
    let (s, e) = (text[..start].chars().count(), text[..end].chars().count());
    let piece: String = text
        .chars()
        .skip(s.saturating_sub(before))
        .take(e + after - s.saturating_sub(before))
        .collect();
    strip(&piece).to_owned()
}

/// `old_absence`: the key of each absence note still in the old form.
#[must_use]
pub fn old_absence(notes_html: &str) -> Vec<String> {
    OLD_ABSENCE
        .captures_iter(notes_html)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect()
}

/// `own_text`: our own visible words - quotations, originals, comments and tags out, a gloss's quoted meaning kept in guillemets.
#[must_use]
pub fn own_text(html: &str) -> String {
    let bare = sub(&ORIG, &sub(&COMMENT, html, " "), " ");
    let kept = GLOSS_QUOTES.replace_all(&bare, |m: &Captures| {
        format!("{}«{}»{}", &m[1], &m[2], &m[3])
    });
    sub(&SPACES, &sub(&TAG, &sub(&QUOTED, &kept, " "), " "), " ")
}

/// `foreign_in_own_text`: each run of CJK, kana or hangul in our own words not followed by its gloss, in context.
#[must_use]
pub fn foreign_in_own_text(html: &str) -> Vec<String> {
    let text = own_text(html);
    FOREIGN
        .find_iter(&text)
        .map_while(Result::ok)
        .filter(|m| !GLOSS.is_match(&text[m.end()..]).unwrap_or(false))
        .map(|m| {
            format!(
                "{} - ...{}...",
                m.as_str(),
                around(&text, m.start(), m.end(), 40, 20)
            )
        })
        .collect()
}

/// `glosses`: (characters, reading, meaning) for every glossed term in our own words.
#[must_use]
pub fn glosses(html: &str) -> Vec<(String, String, String)> {
    let text = own_text(html);
    let mut out = Vec::new();
    for m in FOREIGN.find_iter(&text).map_while(Result::ok) {
        if let Some(g) = GLOSS.captures(&text[m.end()..]).ok().flatten() {
            out.push((
                m.as_str().to_owned(),
                strip(&g[1]).to_owned(),
                strip(&g[2]).to_owned(),
            ));
        }
    }
    out
}

/// `visible_prose`: the section's own words, less every quotation and comment.
#[must_use]
pub fn visible_prose(html: &str) -> String {
    sub(
        &SPACES,
        &sub(&TAG, &sub(&QUOTED, &sub(&COMMENT, html, " "), " "), " "),
        " ",
    )
}

/// `unconverted`: each metric figure in the prose with no conversion after it.
#[must_use]
pub fn unconverted(html: &str) -> Vec<String> {
    let text = visible_prose(html);
    METRIC
        .find_iter(&text)
        .map_while(Result::ok)
        .filter(|m| !CONVERTED.is_match(&text[m.end()..]).unwrap_or(false))
        .map(|m| {
            format!(
                "{} - ...{}...",
                m.as_str(),
                around(&text, m.start(), m.end(), 50, 30)
            )
        })
        .collect()
}

/// `gm_mentions`: each visible "GM", quotations included.
#[must_use]
pub fn gm_mentions(html: &str) -> Vec<String> {
    let text = sub(&SPACES, &sub(&TAG, &sub(&COMMENT, html, " "), " "), " ");
    GM.find_iter(&text)
        .map_while(Result::ok)
        .map(|m| format!("...{}...", around(&text, m.start(), m.end(), 40, 60)))
        .collect()
}

/// `long_paragraphs`: each paragraph or bullet text over [`MAX_WORDS`] words.
#[must_use]
pub fn long_paragraphs(html: &str) -> Vec<String> {
    let body = sub(&COMMENT, html, "");
    let mut out = Vec::new();
    for m in BLOCK.captures_iter(&body).map_while(Result::ok) {
        let inner = m.get(1).or_else(|| m.get(2)).map_or("", |g| g.as_str());
        let text = sub(&TAG, &sub(&SUP, inner, ""), " ");
        let words = split(&text);
        if words.len() > MAX_WORDS {
            out.push(format!(
                "{} words - {}...",
                words.len(),
                words[..14].join(" ")
            ));
        }
    }
    out
}

/// `absence_sentences`: each sentence of the prose carrying a footnote whose note is an absence note, with the note's key.
#[must_use]
pub fn absence_sentences(html: &str, notes_html: &str) -> Vec<String> {
    let absent: HashSet<String> = ABSENT
        .captures_iter(notes_html)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    let mut out = Vec::new();
    let body = sub(&COMMENT, html, "");
    for block in PARAGRAPH.split(&body).map_while(Result::ok) {
        let block = FOOTED.replace_all(block, "$2$1");
        for sentence in SENTENCE_END.split(&block).map_while(Result::ok) {
            let keys: Vec<String> = DATA_NOTE
                .captures_iter(sentence)
                .map_while(Result::ok)
                .map(|c| c[1].to_owned())
                .filter(|k| absent.contains(k))
                .collect();
            if !keys.is_empty() {
                let words = sub(&SPACES, &sub(&TAG, sentence, ""), " ");
                let words: String = strip(&words).chars().take(220).collect();
                out.push(format!("[{}] {words}", keys.join(", ")));
            }
        }
    }
    out
}

fn leads(html: &str) -> Vec<(String, String)> {
    let flat = |t: &str| strip(&sub(&SPACES, &sub(&TAG, t, ""), " ")).to_owned();
    LEAD.captures_iter(&sub(&COMMENT, html, ""))
        .map_while(Result::ok)
        .map(|m| (flat(&m[1]), flat(&m[2])))
        .collect()
}

/// `lead_line_years`: each year in a lead line, and whether the glossary defines it.
#[must_use]
pub fn lead_line_years<S: BuildHasher>(
    html: &str,
    glossary_words: &HashSet<String, S>,
) -> Vec<String> {
    let mut out = Vec::new();
    for (lead, _) in leads(html) {
        for y in YEAR.find_iter(&lead).map_while(Result::ok) {
            let y = y.as_str();
            let known = if glossary_words.contains(y) {
                "a glossary tooltip"
            } else {
                "NOT in the glossary"
            };
            out.push(format!("{y} ({known}) - {lead}"));
        }
    }
    out
}

/// `lead_lines`: each bullet's lead line, `Q` or `S`, with the start of its body.
#[must_use]
pub fn lead_lines(html: &str) -> Vec<String> {
    leads(html)
        .into_iter()
        .map(|(lead, body)| {
            let kind = if lead.ends_with('?') { 'Q' } else { 'S' };
            format!(
                "{kind}  {lead}  |  {}",
                body.chars().take(110).collect::<String>()
            )
        })
        .collect()
}

fn listed(lines: &mut Vec<String>, found: &[String]) {
    if found.is_empty() {
        lines.push("  none".to_owned());
    } else {
        lines.extend(found.iter().map(|x| format!("  {x}")));
    }
}

/// `report`: the prepass text for the named question fragments, their notes adding the two lists read from the footnotes.
#[must_use]
pub fn report<S: BuildHasher>(
    fragments: &[(String, String)],
    glossary_words: &HashSet<String, S>,
    notes: &BTreeMap<String, String>,
) -> String {
    let mut lines = Vec::new();
    for (name, html) in fragments {
        let note = notes.get(name).map_or("", String::as_str);
        let old = old_absence(note);
        let mut foreign = foreign_in_own_text(html);
        foreign.extend(foreign_in_own_text(note));
        let (metric, lead, gm, long) = (
            unconverted(html),
            lead_lines(html),
            gm_mentions(html),
            long_paragraphs(html),
        );
        let years = lead_line_years(html, glossary_words);
        let resting = absence_sentences(html, note);
        lines.push(format!("== {name}"));
        lines.push(format!(
            "METRIC WITHOUT A CONVERSION ({}) - each is a FAIL of STYLE.md 6:",
            metric.len()
        ));
        listed(&mut lines, &metric);
        lines.push(format!("GM IN THE VISIBLE TEXT ({}) - each is a FAIL of STYLE.md 1 (the ruling goes in a comment):", gm.len()));
        listed(&mut lines, &gm);
        lines.push(format!("PARAGRAPH OVER {MAX_WORDS} WORDS ({}) - each is a FAIL of STYLE.md 3 (split it, or make it a list):", long.len()));
        listed(&mut lines, &long);
        lines.push(format!("ABSENCE NOTE IN THE OLD FORM ({}) - each is a FAIL of STYLE.md 7 (search into a comment, findings visible):", old.len()));
        listed(&mut lines, &old);
        lines.push(format!("KANJI WITHOUT ITS GLOSS ({}) - each is a FAIL of STYLE.md 5: follow it with (romaji, \"English meaning\"), or drop it:", foreign.len()));
        listed(&mut lines, &foreign);
        lines.push(format!("SENTENCES RESTING ON AN ABSENCE NOTE ({}) - rule on each: a silence or our own GUESS, never what an unread page says:", resting.len()));
        listed(&mut lines, &resting);
        lines.push(format!("YEARS IN LEAD LINES ({}) - rule on each: is its significance given in the line, or by its tooltip?", years.len()));
        listed(&mut lines, &years);
        lines.push(format!("LEAD LINES ({}) - rule on each: statement or question (STYLE.md 3), and readable from what precedes it:", lead.len()));
        listed(&mut lines, &lead);
    }
    lines.join("\n") + "\n"
}

#[cfg(test)]
mod tests;
