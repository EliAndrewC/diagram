//! How a caption may be cut into lines (feature 449 T151, `labels/layout.py` whole; the cutting rule is feature 133 T39's): the GM's
//! wrap rule (research/contents.json#map-conventions, "Labels on maps (cartographic label placement)"): one line if that clears the
//! sheet, else the first of two or three lines that does. The placer asks it at every seat, one line first.
//!
//! Research:
//!     wrap order - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: one line, then two, then three
//!     line cut - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: between words, the shortest
//!         longest line, ties to even lengths, no word of three letters or fewer alone

use l7r_guard::shared::py_text::split;

/// The cut points `itertools.combinations(range(1, n_words), k)` yields, in its (lexicographic) order.
///
/// Research: the cut points - NONE: every way to cut a run of words into lines, enumerated; the cut the caption takes is [`cut`]'s
fn combinations(n_words: usize, k: usize) -> Vec<Vec<usize>> {
    fn go(from: usize, end: usize, k: usize, head: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if k == 0 {
            out.push(head.clone());
            return;
        }
        for i in from..end {
            head.push(i);
            go(i + 1, end, k - 1, head, out);
            head.pop();
        }
    }
    let mut out = Vec::new();
    go(1, n_words, k, &mut Vec::new(), &mut out);
    out
}

/// The best way to set `words` on `n` lines, or None when there is none. Words are never broken; among the splits into `n` lines the
/// one with the SHORTEST longest line wins, ties broken toward even lengths. A line that is only one short word - three letters or
/// fewer - is refused whenever there are more words than lines.
///
/// Research: line cut - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: between words, the shortest longest line, ties to even lengths, no word of three letters or fewer alone
#[must_use]
pub fn cut(words: &[&str], n: usize) -> Option<Vec<String>> {
    let mut best: Option<((usize, usize), Vec<String>)> = None;
    for cuts in combinations(words.len(), n.saturating_sub(1)) {
        let bounds: Vec<usize> = std::iter::once(0)
            .chain(cuts)
            .chain(std::iter::once(words.len()))
            .collect();
        let lines: Vec<String> = bounds
            .windows(2)
            .map(|w| words[w[0]..w[1]].join(" "))
            .collect();
        let lens: Vec<usize> = lines.iter().map(|l| l.chars().count()).collect();
        if words.len() > n && lens.iter().any(|&l| l <= 3) {
            continue; // a short word never stands alone
        }
        let longest = lens.iter().copied().max().unwrap_or(0);
        let score = (longest, longest - lens.iter().copied().min().unwrap_or(0));
        if best.as_ref().is_none_or(|(s, _)| score < *s) {
            best = Some((score, lines));
        }
    }
    best.map(|(_, lines)| lines)
}

/// Every layout a caption may take, in the order the wrap rule tries them: one line, then two, then three (three only for three words
/// or more).
///
/// Research: wrap order - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: one line, then two, then three
#[must_use]
pub fn layouts(text: &str) -> Vec<Vec<String>> {
    let words = split(text);
    let mut out = vec![vec![text.to_owned()]];
    for n in [2, 3] {
        if words.len() >= n {
            if let Some(lines) = cut(&words, n) {
                out.push(lines);
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{cut, layouts};

    #[test]
    fn a_caption_is_cut_between_words_and_never_leaves_a_short_word_alone() {
        // Python: layouts("Shrine of Benten") == [["Shrine of Benten"], ["Shrine", "of Benten"], ["Shrine", "of", "Benten"]] - the
        // two-line cuts tie, and the first in `combinations`' order stands
        assert_eq!(
            layouts("Shrine of Benten"),
            [
                vec!["Shrine of Benten"],
                vec!["Shrine", "of Benten"],
                vec!["Shrine", "of", "Benten"]
            ]
        );
        // Python: layouts("a b c d") == [["a b c d"]] - every cut leaves a short line alone
        assert_eq!(layouts("a b c d"), [vec!["a b c d"]]);
        assert_eq!(layouts("word"), [vec!["word"]]);
        // Python's cut(["aaaa", "bb", "cccc"], 2) == ["aaaa", "bb cccc"], and with a longer last word the evener cut wins
        assert_eq!(
            cut(&["aaaa", "bb", "cccc"], 2).unwrap(),
            ["aaaa", "bb cccc"]
        );
        assert_eq!(
            cut(&["aaaa", "bb", "ccccc"], 2).unwrap(),
            ["aaaa bb", "ccccc"]
        );
        assert_eq!(cut(&["a", "b"], 2).unwrap(), ["a", "b"]);
    }
}
