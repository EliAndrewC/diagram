//! The words a check reads of a subject (from `record_units.read_page` and `hm_checks.subject_blocks`): a question's pages and a pop-up's paragraphs, what the first-look and reversal tests compare.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex, RegexBuilder};

use crate::shared::html_text::unescape;
use crate::shared::py_text::{self, SPACE_CLASS};

fn re(pattern: &str) -> Regex {
    RegexBuilder::new(pattern)
        .backtrack_limit(usize::MAX >> 8)
        .build()
        .unwrap_or_else(|e| unreachable!("{e}"))
}

static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static MARK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<sup class="fn" data-note="([^"]+)"></sup>"#));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static BREAK: LazyLock<Regex> = LazyLock::new(|| re(&format!(r"(?i)<br[{SPACE_CLASS}]*/?>")));
static SPACE: LazyLock<Regex> = LazyLock::new(|| re(&format!("[{SPACE_CLASS}]+")));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<h[23][^>]*>(.*?)</h[23]>"));
static INTRO: LazyLock<Regex> = LazyLock::new(|| re(r#"\bclass="intro""#));
/// A block's opening tag. `record_units`' `_BLOCK` is `<(p|li|blockquote|td|dd)\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd)\b)|\Z)`; its
/// back-reference and look-ahead need the backtracking engine, a hundred times slower over the record, so the scan below reads the same
/// blocks: a block runs to its own closing tag or to the next opening tag, whichever comes first, else to the end.
static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"<(p|li|blockquote|td|dd)\b([^>]*)>"));
static OPEN_ANY: LazyLock<Regex> = LazyLock::new(|| re(r"<(?:p|li|blockquote|td|dd)\b"));

/// (tag, attributes, inner text) of every block of `body`, as `_BLOCK.finditer` reads them.
fn blocks_of(body: &str) -> Vec<(&str, &str, &str)> {
    let (mut out, mut pos) = (Vec::new(), 0);
    while let Ok(Some(m)) = OPEN.captures_from_pos(body, pos) {
        let (tag, attrs) = (
            m.get(1).map_or("", |g| g.as_str()),
            m.get(2).map_or("", |g| g.as_str()),
        );
        let start = m.get(0).map_or(pos, |g| g.end());
        let closing = format!("</{tag}>");
        let close = body[start..].find(&closing).map(|i| start + i);
        let next = OPEN_ANY
            .find_from_pos(body, start)
            .ok()
            .flatten()
            .map(|n| n.start());
        let (end, resume) = match (close, next) {
            (Some(c), Some(n)) if c < n => (c, c + closing.len()),
            (Some(c), None) => (c, c + closing.len()),
            (_, Some(n)) => (n, n),
            (None, None) => (body.len(), body.len()),
        };
        out.push((tag, attrs, &body[start..end]));
        pos = resume;
    }
    out
}

/// One block of a question page as its reader meets it (`record_units.Block`).
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Block {
    /// The block's words.
    pub words: String,
    /// The note keys it carries, in order, once each.
    pub marks: Vec<String>,
    /// Whether it is the question's intro.
    pub intro: bool,
}

/// A question page: its heading and every block in order (`record_units.Page`).
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Page {
    /// The heading's words, or "".
    pub heading: String,
    /// The blocks, in order.
    pub blocks: Vec<Block>,
}

impl Page {
    /// The intro's words, or "".
    #[must_use]
    pub fn intro(&self) -> &str {
        self.blocks
            .iter()
            .find(|b| b.intro)
            .map_or("", |b| b.words.as_str())
    }
}

/// A fragment's words: comments and markup gone, entities decoded, whitespace collapsed, each note mark a `[^key]` (`record_units.words`).
#[must_use]
pub fn words(text: &str) -> String {
    let t = COMMENT.replace_all(text, "");
    let t = MARK.replace_all(&t, |c: &Captures| format!(" [^{}]", &c[1]));
    let t = BREAK.replace_all(&t, " ");
    let t = TAG.replace_all(&t, "");
    py_text::strip(&SPACE.replace_all(&unescape(&t), " ")).to_owned()
}

/// A question page as its reader meets it: the heading, then every block in order, the intro flagged (`record_units.read_page`).
#[must_use]
pub fn read_page(text: &str) -> Page {
    let body = COMMENT.replace_all(text, "");
    let heading = HEADING
        .captures(&body)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| words(c.get(1).map_or("", |g| g.as_str())));
    let blocks = blocks_of(&body)
        .into_iter()
        .filter_map(|(tag, attrs, inner)| {
            let w = words(inner);
            if w.is_empty() {
                return None;
            }
            let mut marks: Vec<String> = Vec::new();
            for c in MARK.captures_iter(inner).flatten() {
                if !marks.iter().any(|k| k == &c[1]) {
                    marks.push(c[1].to_owned());
                }
            }
            let intro = tag == "p" && INTRO.is_match(attrs).unwrap_or(false);
            Some(Block {
                words: w,
                marks,
                intro,
            })
        })
        .collect();
    Page { heading, blocks }
}

/// A question page's block words, in order (`record_units.read_page`'s blocks).
fn page_blocks(text: &str) -> Vec<String> {
    read_page(text)
        .blocks
        .into_iter()
        .map(|b| b.words)
        .collect()
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "a glob of the record's lowercase file names"
)]
fn question_pages(root: &Path, number: &str) -> Vec<String> {
    let dir = root.join("research/questions");
    let prefix = format!("{number}-");
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.starts_with(&prefix) && n.ends_with(".html"))
        .collect();
    names.sort();
    names
        .into_iter()
        .filter(|n| !n.ends_with(".notes.html"))
        .collect()
}

/// The subject's blocks as its checks read them: a question's pages, a pop-up's paragraphs (`hm_checks.subject_blocks`).
#[must_use]
pub fn subject_blocks(root: &Path, subject: &str) -> Vec<String> {
    if let Some(number) = subject.strip_prefix("q:") {
        let mut out = Vec::new();
        for name in question_pages(root, number) {
            if let Ok(text) = std::fs::read_to_string(root.join("research/questions").join(name)) {
                out.extend(page_blocks(&text));
            }
        }
        return out;
    }
    let file = root
        .join("l7r/diagram/interactive/assets/modals")
        .join(format!("{}.md", subject.get(6..).unwrap_or("")));
    std::fs::read_to_string(file).map_or_else(
        |_| Vec::new(),
        |text| {
            text.split("\n\n")
                .filter(|p| !p.trim().is_empty())
                .map(|p| p.split_whitespace().collect::<Vec<_>>().join(" "))
                .collect()
        },
    )
}

#[cfg(test)]
mod tests {
    use super::{read_page, subject_blocks, words};
    use crate::shared::checks::testkit::dir;

    #[test]
    fn a_page_reads_its_heading_marks_and_intro() {
        let page = read_page(
            "<h2 id=\"a\">The <b>head</b></h2><p class=\"intro\">Why.</p>\
             <p>Claim.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"k\"></sup>\
             <sup class=\"fn\" data-note=\"m\"></sup><li>unclosed<!-- no --></li><p></p>",
        );
        assert_eq!(page.heading, "The head");
        assert_eq!(page.intro(), "Why.");
        assert_eq!(page.blocks[1].marks, ["k", "m"]);
        assert_eq!(page.blocks[1].words, "Claim. [^k] [^k] [^m]");
        assert_eq!(page.blocks[2].words, "unclosed");
        assert_eq!(page.blocks.len(), 3);
        assert_eq!(read_page("no heading").intro(), "");
        assert_eq!(words("a\x1fb <br/> c"), "a b c");
    }

    #[test]
    fn a_question_reads_as_its_blocks_and_a_popup_as_its_paragraphs() {
        let d = dir("pages");
        let q = d.join("research/questions");
        std::fs::create_dir_all(&q).unwrap();
        std::fs::write(q.join("0105-baths.html"), "<!-- gone --><h2>head</h2><p class=\"intro\">One sentence.<sup class=\"fn\" data-note=\"k\"></sup> Two &amp; three.</p>\n<li>item<br/>two</li><p>unclosed<p>next</p><td></td>").unwrap();
        std::fs::write(
            q.join("0105-baths.notes.html"),
            "<p>notes are not read here</p>",
        )
        .unwrap();
        std::fs::write(q.join("0106-other.html"), "<p>other</p>").unwrap();
        assert_eq!(
            subject_blocks(&d, "q:0105"),
            [
                "One sentence. [^k] Two & three.",
                "item two",
                "unclosed",
                "next"
            ]
        );
        let m = d.join("l7r/diagram/interactive/assets/modals/sheet");
        std::fs::create_dir_all(&m).unwrap();
        std::fs::write(
            m.join("bath.md"),
            "first  line\ncontinued\n\n\nsecond\n\n   \n",
        )
        .unwrap();
        assert_eq!(
            subject_blocks(&d, "modal:sheet/bath"),
            ["first line continued", "second"]
        );
        assert!(subject_blocks(&d, "modal:sheet/none").is_empty());
        assert!(subject_blocks(&d, "q:9999").is_empty());
        assert!(subject_blocks(&d, "x").is_empty());
    }
}
