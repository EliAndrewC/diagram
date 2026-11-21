//! Taking a page apart: the assembly's inverse (`record/split.py`, feature 258; ported by feature 449 T144). A heading inside an HTML
//! comment is not a section (`SOURCES.html` once held two whole `<h2>` groups in a comment), and a heading is recognized wherever it stands
//! on its line. Offsets here are BYTE offsets into the text, where the Python's were characters; a message that names one names the
//! character offset, as the Python's did.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::py_text::repr;

use crate::{re, Error, Result};

static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static ID: LazyLock<Regex> = LazyLock::new(|| re(r#"id="([^"]*)""#));
/// What closes every page of the record: the closing tags, with the pointer to its citations page before them where there is one.
const CLOSE: &str = "\n</main>\n</body>\n</html>";
const CITATIONS: &str = "\n<section class=\"citations\">";
const SECTION_END: &str = "</section>";

/// One entry inside a section - a registry source: its heading and its body, verbatim.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    pub id: String,
    pub text: String,
}

/// One section of a page: its heading and everything to the next section, except what its entries hold.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Section {
    pub id: String,
    pub text: String,
    pub entries: Vec<Entry>,
}

/// A page taken apart: assembly is `front`, the sections in order, `tail`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Page {
    pub front: String,
    pub sections: Vec<Section>,
    pub tail: String,
}

/// The [start, end) of every HTML comment.
#[must_use]
pub fn comments(html: &str) -> Vec<(usize, usize)> {
    COMMENT
        .find_iter(html)
        .map_while(std::result::Result::ok)
        .map(|m| (m.start(), m.end()))
        .collect()
}

/// Is the byte at `at` the start of a word character, as `re`'s `\b` reads one?
fn word_at(html: &str, at: usize) -> bool {
    html[at..]
        .chars()
        .next()
        .is_some_and(|c| c.is_alphanumeric() || c == '_')
}

/// Where every `<hN` that opens a real section starts: not one inside a comment, wherever it sits on its line. By bisection over the
/// comments' starts (feature 383: comments never overlap, so only the last to open at or before a heading can hide it).
#[must_use]
pub fn headings(html: &str, level: usize) -> Vec<usize> {
    let hidden = comments(html);
    let starts: Vec<usize> = hidden.iter().map(|h| h.0).collect();
    let inside = |at: usize| {
        let i = starts.partition_point(|s| *s <= at);
        i > 0 && at < hidden[i - 1].1
    };
    let tag = format!("<h{level}");
    html.match_indices(&tag)
        .map(|(at, _)| at)
        .filter(|at| !word_at(html, at + tag.len()) && !inside(*at))
        .collect()
}

/// The id of the heading opening at `at`; a heading without one is refused, never given a made-up name.
///
/// # Errors
/// No `>` closes the tag (Python's `str.index`), or the tag carries no id.
pub fn heading_id(html: &str, at: usize) -> Result<String> {
    let tag_end = html[at..]
        .find('>')
        .map(|n| at + n)
        .ok_or_else(|| Error::new("ValueError", "substring not found"))?;
    if let Some(found) = ID.captures(&html[at..tag_end]).ok().flatten() {
        return Ok(found[1].to_owned());
    }
    Err(Error::new(
        "ValueError",
        format!(
            "a heading with no id at offset {}: {} - the record's anchors are heading ids, and a fragment is named for one",
            html[..at].chars().count(),
            repr(&html[at..=tag_end])
        ),
    ))
}

/// Take a page apart into front, sections and tail; `entry_level` the heading level whose occurrences inside a section are entries of
/// their own (3 for the registry), passed rather than guessed.
///
/// # Errors
/// A page that does not end as every page of the record ends, or a heading with no id.
pub fn split(html: &str, entry_level: Option<usize>, level: usize) -> Result<Page> {
    let tail_at = tail_start(html)?;
    let opens: Vec<usize> = headings(html, level)
        .into_iter()
        .filter(|at| *at < tail_at)
        .collect();
    let Some(first) = opens.first() else {
        return Ok(Page {
            front: html[..tail_at].to_owned(),
            sections: Vec::new(),
            tail: html[tail_at..].to_owned(),
        });
    };
    let mut sections = Vec::new();
    for (i, start) in opens.iter().enumerate() {
        let stop = opens.get(i + 1).copied().unwrap_or(tail_at);
        sections.push(section(html, *start, stop, entry_level)?);
    }
    Ok(Page {
        front: html[..*first].to_owned(),
        sections,
        tail: html[tail_at..].to_owned(),
    })
}

fn section(html: &str, start: usize, stop: usize, entry_level: Option<usize>) -> Result<Section> {
    let body = &html[start..stop];
    let id = heading_id(html, start)?;
    let opens = entry_level.map_or_else(Vec::new, |l| headings(body, l));
    let Some(first) = opens.first() else {
        return Ok(Section {
            id,
            text: body.to_owned(),
            entries: Vec::new(),
        });
    };
    let mut entries = Vec::new();
    for (i, at) in opens.iter().enumerate() {
        let end = opens.get(i + 1).copied().unwrap_or(body.len());
        entries.push(Entry {
            id: heading_id(body, *at)?,
            text: body[*at..end].to_owned(),
        });
    }
    Ok(Section {
        id,
        text: body[..*first].to_owned(),
        entries,
    })
}

/// Where the closing run begins (`_TAIL.search`, its `$` matching at the end or before a final newline): the closing tags, ended by at
/// most two newlines, and before them the citations pointer opened at the earliest place a `</section>` just before the tags can close.
/// Refused rather than guessed.
fn tail_start(html: &str) -> Result<usize> {
    let refused = || {
        Error::new(
            "ValueError",
            "this page does not end with `</main></body></html>` and its optional citations pointer - the splitter has not been shown its shape",
        )
    };
    let body = ["\n\n", "\n", ""]
        .iter()
        .find_map(|end| html.strip_suffix(end).and_then(|b| b.strip_suffix(CLOSE)))
        .ok_or_else(refused)?;
    let close_at = body.len();
    if !body.ends_with(SECTION_END) {
        return Ok(close_at);
    }
    let last_open = close_at - SECTION_END.len();
    Ok(html
        .match_indices(CITATIONS)
        .map(|(at, _)| at)
        .find(|at| at + CITATIONS.len() <= last_open)
        .unwrap_or(close_at))
}

#[cfg(test)]
mod tests;
