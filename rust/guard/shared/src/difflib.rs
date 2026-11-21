//! Python's `difflib.unified_diff`, exactly (feature 449 T045 decision (c)): `SequenceMatcher` with its default `autojunk`, which is not a minimal diff, so which lines carry a `+` is its own.
//! `difflib_cases.json`, generated from `CPython`'s `difflib`, pins it byte for byte.

use std::collections::HashMap;
use std::fmt::Write;

/// (the tag, `i1`, `i2`, `j1`, `j2`).
type Op = (&'static str, usize, usize, usize, usize);

/// Each line's positions in `b`; with 200 lines or more, a line on more than 1% of them plus one is popular and left out (`autojunk`).
fn index_of<'a>(b: &[&'a str]) -> HashMap<&'a str, Vec<usize>> {
    let mut b2j: HashMap<&str, Vec<usize>> = HashMap::new();
    for (i, line) in b.iter().enumerate() {
        b2j.entry(line).or_default().push(i);
    }
    if b.len() >= 200 {
        let limit = b.len() / 100 + 1;
        b2j.retain(|_, places| places.len() <= limit);
    }
    b2j
}

/// The longest matching block of `a[alo..ahi]` and `b[blo..bhi]`, earliest in `a`, then earliest in `b`.
fn longest(
    a: &[&str],
    b: &[&str],
    b2j: &HashMap<&str, Vec<usize>>,
    (alo, ahi, blo, bhi): (usize, usize, usize, usize),
) -> (usize, usize, usize) {
    let (mut from_a, mut from_b, mut size) = (alo, blo, 0);
    let mut j2len: HashMap<usize, usize> = HashMap::new();
    for (i, line) in a.iter().enumerate().take(ahi).skip(alo) {
        let mut next: HashMap<usize, usize> = HashMap::new();
        for &j in b2j.get(line).into_iter().flatten() {
            if j < blo {
                continue;
            }
            if j >= bhi {
                break;
            }
            let k = j
                .checked_sub(1)
                .and_then(|p| j2len.get(&p).copied())
                .unwrap_or(0)
                + 1;
            next.insert(j, k);
            if k > size {
                (from_a, from_b, size) = (i + 1 - k, j + 1 - k, k);
            }
        }
        j2len = next;
    }
    while from_a > alo && from_b > blo && a[from_a - 1] == b[from_b - 1] {
        from_a -= 1;
        from_b -= 1;
        size += 1;
    }
    while from_a + size < ahi && from_b + size < bhi && a[from_a + size] == b[from_b + size] {
        size += 1;
    }
    (from_a, from_b, size)
}

fn matching_blocks(a: &[&str], b: &[&str]) -> Vec<(usize, usize, usize)> {
    let b2j = index_of(b);
    let (mut queue, mut blocks) = (vec![(0, a.len(), 0, b.len())], Vec::new());
    while let Some(range) = queue.pop() {
        let (alo, ahi, blo, bhi) = range;
        let (at_a, at_b, size) = longest(a, b, &b2j, range);
        if size > 0 {
            blocks.push((at_a, at_b, size));
            if alo < at_a && blo < at_b {
                queue.push((alo, at_a, blo, at_b));
            }
            if at_a + size < ahi && at_b + size < bhi {
                queue.push((at_a + size, ahi, at_b + size, bhi));
            }
        }
    }
    blocks.sort_unstable();
    let (mut out, mut held) = (Vec::new(), (0, 0, 0));
    for (i2, j2, k2) in blocks {
        if held.0 + held.2 == i2 && held.1 + held.2 == j2 {
            held.2 += k2;
        } else {
            if held.2 > 0 {
                out.push(held);
            }
            held = (i2, j2, k2);
        }
    }
    if held.2 > 0 {
        out.push(held);
    }
    out.push((a.len(), b.len(), 0));
    out
}

fn opcodes(a: &[&str], b: &[&str]) -> Vec<Op> {
    let (mut i, mut j, mut out) = (0, 0, Vec::new());
    for (ai, bj, size) in matching_blocks(a, b) {
        let tag = match (i < ai, j < bj) {
            (true, true) => Some("replace"),
            (true, false) => Some("delete"),
            (false, true) => Some("insert"),
            (false, false) => None,
        };
        if let Some(tag) = tag {
            out.push((tag, i, ai, j, bj));
        }
        (i, j) = (ai + size, bj + size);
        if size > 0 {
            out.push(("equal", ai, i, bj, j));
        }
    }
    out
}

fn grouped(a: &[&str], b: &[&str], n: usize) -> Vec<Vec<Op>> {
    let mut codes = opcodes(a, b);
    if codes.is_empty() {
        codes.push(("equal", 0, 1, 0, 1));
    }
    if let Some(first) = codes.first_mut().filter(|c| c.0 == "equal") {
        *first = (
            "equal",
            first.1.max(first.2.saturating_sub(n)),
            first.2,
            first.3.max(first.4.saturating_sub(n)),
            first.4,
        );
    }
    if let Some(last) = codes.last_mut().filter(|c| c.0 == "equal") {
        *last = (
            "equal",
            last.1,
            last.2.min(last.1 + n),
            last.3,
            last.4.min(last.3 + n),
        );
    }
    let (mut groups, mut group) = (Vec::new(), Vec::new());
    for (tag, mut i1, i2, mut j1, j2) in codes {
        if tag == "equal" && i2 - i1 > n + n {
            group.push((tag, i1, i2.min(i1 + n), j1, j2.min(j1 + n)));
            groups.push(std::mem::take(&mut group));
            (i1, j1) = (i1.max(i2 - n), j1.max(j2 - n));
        }
        group.push((tag, i1, i2, j1, j2));
    }
    if !(group.is_empty() || (group.len() == 1 && group[0].0 == "equal")) {
        groups.push(group);
    }
    groups
}

fn range(start: usize, stop: usize) -> String {
    match stop - start {
        1 => (start + 1).to_string(),
        0 => format!("{start},0"),
        length => format!("{},{length}", start + 1),
    }
}

fn push_lines(out: &mut String, mark: char, lines: &[&str]) {
    for line in lines {
        out.push(mark);
        out.push_str(line);
    }
}

/// `difflib.unified_diff(a, b, fromfile, tofile, n=3)`, joined; `a` and `b` are lines with their endings.
#[must_use]
pub fn unified(a: &[&str], b: &[&str], from: &str, to: &str) -> String {
    let groups = grouped(a, b, 3);
    let mut out = String::new();
    if groups.is_empty() {
        return out;
    }
    let _ = writeln!(out, "--- {from}\n+++ {to}");
    for group in groups {
        let (first, last) = (group[0], group[group.len() - 1]);
        let _ = writeln!(
            out,
            "@@ -{} +{} @@",
            range(first.1, last.2),
            range(first.3, last.4)
        );
        for (tag, i1, i2, j1, j2) in group {
            if tag == "equal" {
                push_lines(&mut out, ' ', &a[i1..i2]);
            } else {
                if tag != "insert" {
                    push_lines(&mut out, '-', &a[i1..i2]);
                }
                if tag != "delete" {
                    push_lines(&mut out, '+', &b[j1..j2]);
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use serde_json::Value;

    use super::{range, unified};

    fn lines(v: &Value) -> Vec<String> {
        v.as_array()
            .unwrap()
            .iter()
            .map(|l| l.as_str().unwrap().to_owned())
            .collect()
    }

    #[test]
    fn every_case_is_cpythons_byte_for_byte() {
        let cases: Vec<Value> = serde_json::from_str(include_str!("difflib_cases.json")).unwrap();
        assert!(cases.len() >= 60);
        for case in cases {
            let (a, b) = (lines(&case["a"]), lines(&case["b"]));
            let (ar, br): (Vec<&str>, Vec<&str>) = (
                a.iter().map(String::as_str).collect(),
                b.iter().map(String::as_str).collect(),
            );
            assert_eq!(
                unified(&ar, &br, "a/x", "b/x"),
                case["out"].as_str().unwrap()
            );
        }
    }

    #[test]
    fn a_range_is_written_as_difflib_writes_it() {
        assert_eq!(
            (range(0, 1), range(3, 3), range(2, 5)),
            ("1".to_owned(), "3,0".to_owned(), "3,3".to_owned())
        );
        assert_eq!(unified(&[], &[], "a", "b"), "");
    }
}
