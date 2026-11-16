//! Python's `difflib.SequenceMatcher(None, a, b, autojunk=False)` over lines (feature 449 T79): the same matching blocks and opcodes, because what a
//! change "replaced" decides what several tools owe. With no junk and no popular lines, a longest match cannot extend, so `find_longest_match`'s two extension
//! loops have nothing to do and are left out. Over any items that hash (feature 449 T145): `quote_verbatim`'s nearest stretch of a page and its
//! differences match characters, and `find_longest_match` and `ratio` are its.

use std::collections::HashMap;
use std::hash::Hash;

/// What an opcode does to its two ranges.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tag {
    Replace,
    Delete,
    Insert,
    Equal,
}

/// `(tag, i1, i2, j1, j2)`.
pub type Opcode = (Tag, usize, usize, usize, usize);

struct Matcher<'a, T> {
    a: &'a [T],
    b2j: HashMap<&'a T, Vec<usize>>,
}

impl<'a, T: Eq + Hash> Matcher<'a, T> {
    fn new(a: &'a [T], b: &'a [T]) -> Self {
        let mut b2j: HashMap<&T, Vec<usize>> = HashMap::new();
        for (j, item) in b.iter().enumerate() {
            b2j.entry(item).or_default().push(j);
        }
        Self { a, b2j }
    }

    fn longest(&self, alo: usize, ahi: usize, blo: usize, bhi: usize) -> (usize, usize, usize) {
        let (mut best_i, mut best_j, mut best_size) = (alo, blo, 0);
        let mut j2len: HashMap<usize, usize> = HashMap::new();
        for i in alo..ahi {
            let mut next: HashMap<usize, usize> = HashMap::new();
            for &j in self.b2j.get(&self.a[i]).map_or(&[][..], Vec::as_slice) {
                if j < blo {
                    continue;
                }
                if j >= bhi {
                    break;
                }
                let k = j
                    .checked_sub(1)
                    .and_then(|p| j2len.get(&p))
                    .copied()
                    .unwrap_or(0)
                    + 1;
                next.insert(j, k);
                if k > best_size {
                    (best_i, best_j, best_size) = (i + 1 - k, j + 1 - k, k);
                }
            }
            j2len = next;
        }
        (best_i, best_j, best_size)
    }
}

/// `find_longest_match(0, len(a), 0, len(b))`: `(i, j, n)`, the earliest in `a` of the longest, then the earliest in `b`.
#[must_use]
pub fn longest_match<T: Eq + Hash>(a: &[T], b: &[T]) -> (usize, usize, usize) {
    Matcher::new(a, b).longest(0, a.len(), 0, b.len())
}

/// `ratio()`: twice the matched items over the items of both, 1.0 for two empty sequences.
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "a sequence's length, far inside f64's exact range"
)]
pub fn ratio<T: Eq + Hash>(a: &[T], b: &[T]) -> f64 {
    let total = a.len() + b.len();
    if total == 0 {
        return 1.0;
    }
    let matched: usize = matching_blocks(a, b).iter().map(|m| m.2).sum();
    2.0 * matched as f64 / total as f64
}

/// `get_matching_blocks`: `(i, j, n)`, adjacent blocks merged, ending in the `(len a, len b, 0)` sentinel.
#[must_use]
pub fn matching_blocks<T: Eq + Hash>(left: &[T], right: &[T]) -> Vec<(usize, usize, usize)> {
    let matcher = Matcher::new(left, right);
    let mut queue = vec![(0, left.len(), 0, right.len())];
    let mut found = Vec::new();
    while let Some((alo, ahi, blo, bhi)) = queue.pop() {
        let (i, j, k) = matcher.longest(alo, ahi, blo, bhi);
        if k > 0 {
            found.push((i, j, k));
            if alo < i && blo < j {
                queue.push((alo, i, blo, j));
            }
            if i + k < ahi && j + k < bhi {
                queue.push((i + k, ahi, j + k, bhi));
            }
        }
    }
    found.sort_unstable();
    let mut merged: Vec<(usize, usize, usize)> = Vec::new();
    for (i, j, k) in found {
        match merged.last_mut() {
            Some(last) if last.0 + last.2 == i && last.1 + last.2 == j => last.2 += k,
            _ => merged.push((i, j, k)),
        }
    }
    merged.push((left.len(), right.len(), 0));
    merged
}

/// `get_opcodes`.
#[must_use]
pub fn opcodes<T: Eq + Hash>(a: &[T], b: &[T]) -> Vec<Opcode> {
    let (mut i, mut j) = (0, 0);
    let mut out = Vec::new();
    for (ai, bj, size) in matching_blocks(a, b) {
        let tag = match (i < ai, j < bj) {
            (true, true) => Some(Tag::Replace),
            (true, false) => Some(Tag::Delete),
            (false, true) => Some(Tag::Insert),
            (false, false) => None,
        };
        if let Some(tag) = tag {
            out.push((tag, i, ai, j, bj));
        }
        (i, j) = (ai + size, bj + size);
        if size > 0 {
            out.push((Tag::Equal, ai, i, bj, j));
        }
    }
    out
}

/// `get_grouped_opcodes(n)`.
fn grouped(mut codes: Vec<Opcode>, n: usize) -> Vec<Vec<Opcode>> {
    if let Some(first) = codes.first_mut().filter(|c| c.0 == Tag::Equal) {
        first.1 = first.1.max(first.2.saturating_sub(n));
        first.3 = first.3.max(first.4.saturating_sub(n));
    }
    if let Some(last) = codes.last_mut().filter(|c| c.0 == Tag::Equal) {
        last.2 = last.2.min(last.1 + n);
        last.4 = last.4.min(last.3 + n);
    }
    let (mut out, mut group) = (Vec::new(), Vec::new());
    for (tag, mut i1, i2, mut j1, j2) in codes {
        if tag == Tag::Equal && i2 - i1 > n + n {
            group.push((tag, i1, i2.min(i1 + n), j1, j2.min(j1 + n)));
            out.push(std::mem::take(&mut group));
            i1 = i1.max(i2.saturating_sub(n));
            j1 = j1.max(j2.saturating_sub(n));
        }
        group.push((tag, i1, i2, j1, j2));
    }
    let lone_equal = group.len() == 1 && group[0].0 == Tag::Equal;
    if !group.is_empty() && !lone_equal {
        out.push(group);
    }
    out
}

/// `_format_range_unified`.
fn range(start: usize, stop: usize) -> String {
    let (beginning, length) = (start + 1, stop - start);
    match length {
        1 => beginning.to_string(),
        0 => format!("{},0", beginning - 1),
        _ => format!("{beginning},{length}"),
    }
}

/// `difflib.unified_diff(a, b, from_file, to_file, lineterm="", n=n)` over lines (no line of `a` or `b` carries its end).
#[must_use]
pub fn unified_diff(
    a: &[&str],
    b: &[&str],
    from_file: &str,
    to_file: &str,
    n: usize,
) -> Vec<String> {
    let mut out = Vec::new();
    for group in grouped(opcodes(a, b), n) {
        if out.is_empty() {
            out.push(format!("--- {from_file}"));
            out.push(format!("+++ {to_file}"));
        }
        let (first, last) = (group[0], group[group.len() - 1]);
        out.push(format!(
            "@@ -{} +{} @@",
            range(first.1, last.2),
            range(first.3, last.4)
        ));
        for (tag, i1, i2, j1, j2) in group {
            if tag == Tag::Equal {
                out.extend(a[i1..i2].iter().map(|l| format!(" {l}")));
                continue;
            }
            if tag != Tag::Insert {
                out.extend(a[i1..i2].iter().map(|l| format!("-{l}")));
            }
            if tag != Tag::Delete {
                out.extend(b[j1..j2].iter().map(|l| format!("+{l}")));
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::unified_diff;

    fn lines(text: &str) -> Vec<&str> {
        text.split('\n').collect()
    }

    /// Each expected string is `difflib.unified_diff(a, b, ..., lineterm="", n=n)`'s, from `CPython`.
    #[test]
    fn unified_diff_matches_pythons() {
        let (a, b) = (
            lines("h\nb\nc\nd\ne\nf\ng\nh2\ni\nj\nk"),
            lines("h\nx\nc\nd\ne\nf\ng\nh2\ny\nj\nk\nl"),
        );
        assert_eq!(
            unified_diff(&a, &b, "at the last sync", "your copy", 1).join("\n"),
            "--- at the last sync\n+++ your copy\n@@ -1,3 +1,3 @@\n h\n-b\n+x\n c\n@@ -8,4 +8,5 @@\n h2\n-i\n+y\n j\n k\n+l"
        );
        assert_eq!(
            unified_diff(&[""], &["a"], "f", "t", 1).join("\n"),
            "--- f\n+++ t\n@@ -1 +1 @@\n-\n+a"
        );
        assert!(unified_diff(&["x"], &["x"], "f", "t", 1).is_empty());
        assert_eq!(
            unified_diff(&["x", "y"], &["y"], "f", "t", 0).join("\n"),
            "--- f\n+++ t\n@@ -1 +0,0 @@\n-x"
        );
        assert_eq!(
            unified_diff(&["a", "b", "c"], &["a", "c"], "f", "t", 0).join("\n"),
            "--- f\n+++ t\n@@ -2 +1,0 @@\n-b"
        );
    }

    use super::{matching_blocks, opcodes, Tag};

    #[test]
    fn opcodes_match_pythons_on_each_shape() {
        let ops = opcodes(&["a", "b", "c", "d"], &["a", "x", "c", "e", "f"]);
        assert_eq!(
            ops,
            [
                (Tag::Equal, 0, 1, 0, 1),
                (Tag::Replace, 1, 2, 1, 2),
                (Tag::Equal, 2, 3, 2, 3),
                (Tag::Replace, 3, 4, 3, 5)
            ]
        );
        assert_eq!(
            opcodes(&["a", "b"], &["a"]),
            [(Tag::Equal, 0, 1, 0, 1), (Tag::Delete, 1, 2, 1, 1)]
        );
        assert_eq!(
            opcodes(&["a"], &["z", "a"]),
            [(Tag::Insert, 0, 0, 0, 1), (Tag::Equal, 0, 1, 1, 2)]
        );
        assert!(opcodes::<&str>(&[], &[]).is_empty());
        // over characters, as `quote_verbatim` reads a passage against a page (feature 449 T145)
        let (a, b): (Vec<char>, Vec<char>) = (
            "the dike".chars().collect(),
            "a dike wide".chars().collect(),
        );
        assert_eq!(super::longest_match(&a, &b), (3, 1, 5));
        assert!((super::ratio(&a, &b) - 10.0 / 19.0).abs() < 1e-12);
        assert!((super::ratio::<char>(&[], &[]) - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn blocks_are_the_longest_first_then_either_side_merged() {
        assert_eq!(
            matching_blocks(&["q", "m", "n"], &["x", "m", "n", "q"]),
            [(1, 1, 2), (3, 4, 0)]
        );
        assert_eq!(
            matching_blocks(&["x", "a", "b", "y"], &["a", "b", "q", "x"]),
            [(1, 0, 2), (4, 4, 0)]
        );
        assert_eq!(
            matching_blocks(&["a", "a"], &["a", "a"]),
            [(0, 0, 2), (2, 2, 0)]
        );
        assert_eq!(
            matching_blocks(&["a", "b", "c", "a"], &["z", "a", "b", "y", "c", "a"]),
            [(0, 1, 2), (2, 4, 2), (4, 6, 0)]
        );
        assert_eq!(
            matching_blocks(&["p", "q", "r"], &["q", "p", "r", "r"]),
            [(0, 1, 1), (2, 2, 1), (3, 4, 0)]
        );
    }
}
