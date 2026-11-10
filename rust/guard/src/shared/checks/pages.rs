//! The words a check reads of a subject (from `record_units.read_page` and `hm_checks.subject_blocks`): a question's pages and a pop-up's paragraphs, what the first-look and reversal tests compare.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::shared::html_text::unescape;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static MARK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<sup class="fn" data-note="([^"]+)"></sup>"#));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static BREAK: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)<br\s*/?>"));
static SPACE: LazyLock<Regex> = LazyLock::new(|| re(r"\s+"));
static BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?s)<(p|li|blockquote|td|dd)\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd)\b)|\z)")
});

/// A fragment's words: comments and markup gone, entities decoded, whitespace collapsed, each note mark a `[^key]` (`record_units.words`).
fn words(text: &str) -> String {
    let t = COMMENT.replace_all(text, "");
    let t = MARK.replace_all(&t, |c: &Captures| format!(" [^{}]", &c[1]));
    let t = BREAK.replace_all(&t, " ");
    let t = TAG.replace_all(&t, "");
    SPACE.replace_all(&unescape(&t), " ").trim().to_owned()
}

/// A question page's block words, in order (`record_units.read_page`'s blocks).
fn page_blocks(text: &str) -> Vec<String> {
    let body = COMMENT.replace_all(text, "");
    BLOCK
        .captures_iter(&body)
        .flatten()
        .map(|m| words(m.get(3).map_or("", |g| g.as_str())))
        .filter(|w| !w.is_empty())
        .collect()
}

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
    use super::subject_blocks;
    use crate::shared::checks::testkit::dir;

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
