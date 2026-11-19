//! A number with a unit of measure (feature 447 amendment 4, ported by feature 449 T138): the field-size runs dropped sources whose
//! printed passage was the nearest by meaning but held no size - Hattori's sizes, Bray's "twenty yards square" and Huizhou's 0.715-mu
//! parcel stood elsewhere in their files (`specs/447-semantic-index/research/t05-why.md`) - so each source also shows the passage where a
//! measure stands nearest the question's terms. Number and unit forms are those the archive's cases use (t05-why.md: Hattori and Ofuro
//! write ㎡, Bray "twenty yards square", the Huizhou register formal numerals with 分 厘 毫 步); a false hit (歩 "step", 分 "part") costs a
//! line, a miss a source. The pattern is the Python's, compiled through `research::pyre` so `\b`, `\s` and `re.IGNORECASE` read as
//! Python's.

use std::sync::LazyLock;

use fancy_regex::Regex;

use super::SNIPPET;

const WORDS: &str = "one two three four five six seven eight nine ten eleven twelve fifteen twenty thirty forty fifty sixty hundred half quarter";

static MEASURE: LazyLock<Regex> = LazyLock::new(|| {
    let words = WORDS.split(' ').collect::<Vec<_>>().join("|");
    let num = format!(
        r"(?:\d[\d,.]*|[〇一二三四五六七八九十百千万壱弐参拾廿壹贰貳叁參肆伍陆陸柒捌玖佰仟两兩]+|\b(?:{words})\b(?: an?)?)"
    );
    let unit = concat!(
        r"(?:反|段|畝|畆|歩|步|坪|町|亩|顷|頃|坵|丘|分|厘|毫|間|尺|丈|㎡|m2|m²|平方メートル|平方米|ヘクタール|公顷|",
        r"hectares?\b|ha\b|acres?\b|square (?:feet|foot|yards?|met(?:er|re)s?)\b|feet\b|foot\b|ft\b|yards?\b|mows?\b|mu\b|",
        r"tan\b|se\b|bu\b|tsubo\b|ch[oō]\b|ken\b|qing\b|qiu\b)"
    );
    l7r_gate_research::pyre::py(&format!(r"(?i){num}\s*{unit}"))
});

/// Characters either side of a measure in which the question's terms are counted, first close then near (measured 2026-10-30: with only
/// the 300-character count every measure on Hattori's page tied, and its site area "2万㎡" won over its plots' "10㎡ほど ... 180㎡"; on the
/// Ofuro page a menu's "第一歩" won over "1区画3-5㎡").
pub const CLOSE: usize = 60;
pub const NEAR: usize = 300;

/// The (start, end) of the passages around the `n` best measures that do not overlap - best by the most of `terms` within CLOSE, then
/// within NEAR, then the most other measures within CLOSE (a run of sizes), the earliest on a tie.
#[must_use]
pub fn measure_passages(body: &str, terms: &[String], n: usize) -> Vec<(i64, i64)> {
    let low: Vec<char> = body.to_lowercase().chars().collect();
    let len = body.chars().count();
    let terms: Vec<Vec<char>> = terms
        .iter()
        .map(|t| t.to_lowercase().chars().collect())
        .collect();
    // each match's start in characters (`m.start()`), the byte offsets walked once
    let mut found = Vec::new();
    let (mut byte, mut chars) = (0, 0);
    for m in MEASURE.find_iter(body).map_while(Result::ok) {
        chars += body[byte..m.start()].chars().count();
        byte = m.start();
        found.push(chars);
    }
    let count = |at: usize, span: usize| {
        // `low[max(0, at - span):at + span]`, clamped as Python clamps a slice
        let lo = at.saturating_sub(span).min(low.len());
        let window = &low[lo..(at + span).min(low.len()).max(lo)];
        terms
            .iter()
            .filter(|t| t.is_empty() || window.windows(t.len()).any(|w| w == t.as_slice()))
            .count()
    };
    let mut scored: Vec<((usize, usize, usize), i64)> = found
        .iter()
        .map(|&at| {
            let lo = found.partition_point(|&o| o + CLOSE < at);
            let hi = found.partition_point(|&o| o <= at + CLOSE);
            let neg = -i64::try_from(at).unwrap_or(0);
            ((count(at, CLOSE), count(at, NEAR), hi - lo - 1), neg)
        })
        .collect();
    scored.sort_unstable();
    let snippet = i64::try_from(SNIPPET).unwrap_or(0);
    let len = i64::try_from(len).unwrap_or(0);
    let mut out: Vec<(i64, i64)> = Vec::new();
    for (_, neg) in scored.iter().rev() {
        let start = (-neg - snippet / 2).max(0);
        let span = (start, len.min(start + snippet));
        if !out.iter().any(|(s, e)| *s < span.1 && span.0 < *e) {
            out.push(span);
            if out.len() >= n {
                break;
            }
        }
    }
    out
}

#[cfg(test)]
mod tests;
