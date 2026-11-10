//! Python's `difflib.SequenceMatcher(None, a, b, autojunk=False)` over lines (feature 449 T79): the same matching blocks and opcodes, because what a
//! change "replaced" decides what several tools owe. With no junk and no popular lines, a longest match cannot extend, so `find_longest_match`'s two extension
//! loops have nothing to do and are left out.

use std::collections::HashMap;

/// What an opcode does to its two ranges.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Tag {
    Replace,
    Delete,
    Insert,
    Equal,
}

/// `(tag, i1, i2, j1, j2)`.
pub(crate) type Opcode = (Tag, usize, usize, usize, usize);

struct Matcher<'a> {
    a: &'a [&'a str],
    b2j: HashMap<&'a str, Vec<usize>>,
}

impl Matcher<'_> {
    fn longest(&self, alo: usize, ahi: usize, blo: usize, bhi: usize) -> (usize, usize, usize) {
        let (mut best_i, mut best_j, mut best_size) = (alo, blo, 0);
        let mut j2len: HashMap<usize, usize> = HashMap::new();
        for i in alo..ahi {
            let mut next: HashMap<usize, usize> = HashMap::new();
            for &j in self.b2j.get(self.a[i]).map_or(&[][..], Vec::as_slice) {
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

/// `get_matching_blocks`: `(i, j, n)`, adjacent blocks merged, ending in the `(len a, len b, 0)` sentinel.
pub(crate) fn matching_blocks(left: &[&str], right: &[&str]) -> Vec<(usize, usize, usize)> {
    let mut b2j: HashMap<&str, Vec<usize>> = HashMap::new();
    for (j, line) in right.iter().enumerate() {
        b2j.entry(line).or_default().push(j);
    }
    let matcher = Matcher { a: left, b2j };
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
pub(crate) fn opcodes(a: &[&str], b: &[&str]) -> Vec<Opcode> {
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

#[cfg(test)]
mod tests {
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
        assert!(opcodes(&[], &[]).is_empty());
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
