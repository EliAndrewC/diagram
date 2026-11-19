//! A caption broken across lines (feature 449 T202; research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html,
//! "A caption breaks across lines only when that is what clears the ground beneath it"): the ways of cutting its words into two or three
//! lines, and the one each count of lines takes.
//!
//! Research: the wrap's cut - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: cut only between words, where the longest line comes out shortest, ties to the most even lengths; never a short word alone on a line while there are more words than lines

use crate::work_counts::count;

/// The longest word a line may not hold alone, in letters ("of", "the").
///
/// Research: a short word - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a short word is never left alone on a line - a line holding a single one-, two- or three-letter word is refused while there are more words than lines
pub const SHORT_WORD: usize = 3;

/// Every way of cutting `n` words into `k` non-empty runs, as the indexes where each run after the first starts.
fn cuts(n: usize, k: usize) -> Vec<Vec<usize>> {
    fn go(start: usize, left: usize, n: usize, at: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if left == 0 {
            out.push(at.clone());
            return;
        }
        for c in start..=(n - left) {
            at.push(c);
            go(c + 1, left - 1, n, at, out);
            at.pop();
        }
    }
    let mut out = Vec::new();
    if k >= 1 && n >= k {
        go(1, k - 1, n, &mut Vec::new(), &mut out);
    }
    out
}

/// The text cut into `k` lines as 0242 cuts it, with each line's width at `char_w` px a character, or `None` where it has fewer words
/// than lines, or every cut strands a short word. `wrap_cut` counts each cut considered.
#[must_use]
pub fn cut(text: &str, k: usize, char_w: f64) -> Option<Vec<String>> {
    let words: Vec<&str> = text.split_whitespace().collect();
    let width = |ws: &[&str]| {
        #[expect(clippy::cast_precision_loss, reason = "a line's character count")]
        let n = ws.join(" ").chars().count() as f64;
        n * char_w
    };
    let mut best: Option<(f64, f64, Vec<Vec<&str>>)> = None;
    for at in cuts(words.len(), k) {
        count("wrap_cut@cut", 1);
        let bounds: Vec<usize> = std::iter::once(0)
            .chain(at.iter().copied())
            .chain(std::iter::once(words.len()))
            .collect();
        let runs: Vec<Vec<&str>> = bounds
            .windows(2)
            .map(|b| words[b[0]..b[1]].to_vec())
            .collect();
        let stranded = words.len() > k
            && runs
                .iter()
                .any(|r| r.len() == 1 && r[0].chars().count() <= SHORT_WORD);
        if stranded {
            continue;
        }
        let ws: Vec<f64> = runs.iter().map(|r| width(r)).collect();
        let longest = ws.iter().copied().fold(0.0, f64::max);
        let spread = longest - ws.iter().copied().fold(f64::INFINITY, f64::min);
        if best.as_ref().is_none_or(|b| (longest, spread) < (b.0, b.1)) {
            best = Some((longest, spread, runs));
        }
    }
    best.map(|(_, _, runs)| runs.into_iter().map(|r| r.join(" ")).collect())
}

#[cfg(test)]
mod tests {
    use super::{cut, cuts};

    #[test]
    fn every_way_of_cutting_is_tried() {
        assert_eq!(cuts(3, 2), vec![vec![1], vec![2]]);
        assert_eq!(cuts(4, 3).len(), 3);
        assert!(cuts(1, 2).is_empty());
        assert!(cuts(2, 0).is_empty());
    }

    /// 0242's worked example: "Shrine of Benten" never leaves "of" alone on a line.
    #[test]
    fn a_short_word_is_never_left_alone_on_a_line() {
        let two = cut("Shrine of Benten", 2, 1.0).unwrap();
        assert!(two == ["Shrine of", "Benten"] || two == ["Shrine", "of Benten"]);
        // as many lines as words: the rule does not refuse a short word there
        assert_eq!(
            cut("Shrine of Benten", 3, 1.0).unwrap(),
            ["Shrine", "of", "Benten"]
        );
        // every cut of four short words into three lines strands one of them
        assert_eq!(cut("an old inn by", 3, 1.0), None);
        assert_eq!(cut("one", 2, 1.0), None);
    }

    /// The longest line as short as it can be, ties to the most even.
    #[test]
    fn the_cut_makes_the_longest_line_shortest() {
        assert_eq!(
            cut("barges downstream to Nagahara city", 2, 1.0).unwrap(),
            ["barges downstream", "to Nagahara city"]
        );
        assert_eq!(cut("notice board", 2, 1.0).unwrap(), ["notice", "board"]);
        assert_eq!(
            cut("aaaa bb cc dddd", 2, 1.0).unwrap(),
            ["aaaa bb", "cc dddd"]
        );
    }
}
