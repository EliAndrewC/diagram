//! The verdicts of `quote_verbatim` (feature 449 T145): a passage VERBATIM, DIFFERS (the closest stretch of the page and what differs)
//! or NOT-ON-PAGE against a page's text, and a citation's quotation and readability verdicts over every passage and link it carries.
//! The Python kept each verdict by its passage and page in `record_cache.ParseCache` (feature 383 amendment 1: the nearest-stretch search
//! was 21 of a 25 s run); this port keeps none - `ask:449-T81-slices` leaves caching to each Rust caller's own measurement, and the
//! search here costs what the T145 differential measured (its record), the verdict the same either way.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::difflib::{longest_match, opcodes, ratio, Tag};
use l7r_shared::py_text::{repr, SPACE_CLASS};
use serde_json::{json, Map, Value};

use super::fetch::Got;
use super::squeeze;
use crate::re;

/// Below this similarity the nearest stretch of the page is not worth showing: NOT-ON-PAGE rather than DIFFERS.
const NEAR: f64 = 0.85;

static ELISION: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"[{SPACE_CLASS}]*(?:\[[{SPACE_CLASS}]*(?:\.\.\.|…)[{SPACE_CLASS}]*\]|\.\.\.|…)[{SPACE_CLASS}]*"
    ))
});
static REF_MARK: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"[{SPACE_CLASS}]*\[(?:\d{{1,3}}|注[{SPACE_CLASS}]*\d+|note[{SPACE_CLASS}]*\d+|citation needed|要出典)\]"
    ))
});

fn chars(text: &str) -> Vec<char> {
    text.chars().collect()
}

fn string(chars: &[char]) -> String {
    chars.iter().collect()
}

/// Python's `round(x, 3)`: the exact binary value rounded to three places, half to even, read back.
#[must_use]
pub fn round3(x: f64) -> f64 {
    format!("{x:.3}").parse().unwrap_or(x)
}

/// `nearest`: (similarity, the stretch of `page` closest to `passage`), anchored on their longest shared run.
#[must_use]
pub fn nearest(passage: &[char], page: &[char]) -> (f64, Vec<char>) {
    if passage.is_empty() || page.is_empty() {
        return (0.0, Vec::new());
    }
    let (a, b, size) = longest_match(page, passage);
    if size == 0 {
        return (0.0, Vec::new());
    }
    let start = a.saturating_sub(b);
    let slack = 8.max(passage.len() / 10);
    let window = &page[start..page.len().min(start + passage.len() + slack)];
    let (mut best, mut best_text) = (0.0, Vec::new());
    let low = passage.len().saturating_sub(slack);
    let mut cut = window.len();
    while cut >= low {
        let r = ratio(&window[..cut], passage);
        if r > best {
            (best, best_text) = (r, window[..cut].to_vec());
        }
        if cut == 0 {
            break;
        }
        cut -= 1;
    }
    (best, best_text)
}

/// `differences`: `quoted 'x' / page 'y'` for each place the two differ.
#[must_use]
pub fn differences(passage: &[char], stretch: &[char]) -> Vec<String> {
    opcodes(passage, stretch)
        .into_iter()
        .filter(|op| op.0 != Tag::Equal)
        .map(|(_, i1, i2, j1, j2)| {
            format!(
                "quoted {} / page {}",
                repr(&string(&passage[i1..i2])),
                repr(&string(&stretch[j1..j2]))
            )
        })
        .collect()
}

/// `find_in_order`: (start, end) of `pieces` found in `have` one after another; None for none, or no pieces.
#[must_use]
pub fn find_in_order(pieces: &[Vec<char>], have: &[char]) -> Option<(usize, usize)> {
    let (mut at, mut first) = (0, None);
    for piece in pieces {
        let hit = (at..=have.len().checked_sub(piece.len())?)
            .find(|&i| have[i..i + piece.len()] == piece[..])?;
        first.get_or_insert(hit);
        at = hit + piece.len();
    }
    first.map(|f| (f, at))
}

/// The character index of each byte offset of `text` that starts a character, and of its end.
fn char_at(text: &str, byte: usize) -> usize {
    text[..byte].chars().count()
}

/// `unmarked`: `have` without the page's reference markers, and for each kept character its index in `have`.
#[must_use]
pub fn unmarked(have: &str) -> (Vec<char>, Vec<usize>) {
    let total = have.chars().count();
    let (mut kept, mut at) = (Vec::new(), 0);
    for m in REF_MARK.find_iter(have).map_while(Result::ok) {
        let (s, e) = (char_at(have, m.start()), char_at(have, m.end()));
        kept.extend(at..s);
        at = e;
    }
    kept.extend(at..total);
    let all = chars(have);
    (kept.iter().map(|&i| all[i]).collect(), kept)
}

/// `_verdict` of a squeezed passage against a squeezed page.
fn verdict_of(want: &str, have: &str) -> Map<String, Value> {
    let pieces: Vec<Vec<char>> = ELISION
        .split(want)
        .map_while(Result::ok)
        .filter(|p| !p.is_empty())
        .map(chars)
        .collect();
    let have_chars = chars(have);
    let mut out = Map::new();
    if find_in_order(&pieces, &have_chars).is_some() {
        out.insert("quotation".into(), json!("VERBATIM"));
        return out;
    }
    let want_chars = chars(want);
    // a run of Wikipedia markers inside the quoted span is named as the difference, never forgiven
    let (bare, kept) = unmarked(have);
    if let Some((s, e)) = find_in_order(&pieces, &bare) {
        let stretch = &have_chars[kept[s]..=kept[e - 1]];
        out.insert("quotation".into(), json!("DIFFERS"));
        out.insert("page_text".into(), json!(string(stretch)));
        out.insert(
            "differences".into(),
            json!(differences(&want_chars, stretch)),
        );
        out.insert("similarity".into(), json!(1.0));
        out.insert("only_reference_markers".into(), json!(true));
        return out;
    }
    let (r, stretch) = nearest(&want_chars, &have_chars);
    if r >= NEAR {
        let text = string(&stretch);
        let only = squeeze(&REF_MARK.replace_all(&text, "")) == want;
        out.insert("quotation".into(), json!("DIFFERS"));
        out.insert("page_text".into(), json!(text));
        out.insert(
            "differences".into(),
            json!(differences(&want_chars, &stretch)),
        );
        out.insert("similarity".into(), json!(round3(r)));
        out.insert("only_reference_markers".into(), json!(only));
        return out;
    }
    out.insert("quotation".into(), json!("NOT-ON-PAGE"));
    out.insert("similarity".into(), json!(round3(r)));
    out
}

/// `verdict`: VERBATIM, DIFFERS or NOT-ON-PAGE for one passage on one page's text.
#[must_use]
pub fn verdict(passage: &str, page: &str) -> Map<String, Value> {
    verdict_of(&squeeze(passage), &squeeze(page))
}

fn word(v: &Map<String, Value>) -> &str {
    v.get("quotation").and_then(Value::as_str).unwrap_or("")
}

fn truthy_text(v: Option<&String>) -> Option<&String> {
    v.filter(|s| !s.is_empty())
}

/// The verdict of one passage over the pages read: an archived text confirms a quotation and never sinks one.
fn best_of(
    target: &str,
    read: &[(&String, Option<&String>)],
    links: &[String],
    states: &[Got],
) -> Map<String, Value> {
    let want = squeeze(target);
    let per_page: Vec<Map<String, Value>> = read
        .iter()
        .map(|(text, archived)| {
            let v = verdict_of(&want, &squeeze(text));
            match archived {
                Some(a) if word(&v) != "VERBATIM" => {
                    let mut m = Map::new();
                    m.insert("quotation".into(), json!("NOT-CHECKED"));
                    m.insert(
                        "why".into(),
                        json!(format!(
                            "not found verbatim in the archived text of {a} - check by hand"
                        )),
                    );
                    m
                }
                _ => v,
            }
        })
        .collect();
    let at = per_page
        .iter()
        .position(|v| word(v) == "VERBATIM")
        .or_else(|| per_page.iter().position(|v| word(v) == "DIFFERS"))
        .unwrap_or(0);
    let mut best = per_page[at].clone();
    if word(&best) == "VERBATIM" {
        if let Some(a) = read[at].1 {
            best.insert("archived".into(), json!(a));
        }
    }
    let unread = links.iter().zip(states).find(|(_, s)| s.state != "FETCHED");
    if word(&best) == "NOT-ON-PAGE" {
        if let Some((u, _)) = unread {
            let mut m = Map::new();
            m.insert("quotation".into(), json!("NOT-CHECKED"));
            m.insert(
                "why".into(),
                json!(format!(
                    "not on the pages read; it may be on {u}, which could not be read here"
                )),
            );
            best = m;
        }
    }
    best
}

/// `judge_note`: the quotation and readability verdicts of one citation, over every passage and every link it carries.
pub fn judge_note(
    note: &Map<String, Value>,
    get: &mut dyn FnMut(&str) -> Got,
) -> Map<String, Value> {
    let links: Vec<String> = note["links"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect();
    let states: Vec<Got> = links.iter().map(|u| get(u)).collect();
    let read: Vec<(&String, Option<&String>)> = states
        .iter()
        .filter(|s| s.state == "FETCHED")
        .map(|s| (&s.text, truthy_text(s.archived.as_ref())))
        .collect();
    let mut results: Vec<Map<String, Value>> = Vec::new();
    for p in note["passages"].as_array().into_iter().flatten() {
        let field = |k: &str| p.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
        let original = field("original");
        let target = if original.is_empty() {
            field("quote")
        } else {
            original.clone()
        };
        let best = if read.is_empty() {
            let first = &states[0];
            let mut m = Map::new();
            m.insert(
                "quotation".into(),
                json!(if first.state == "UNFETCHABLE" {
                    "UNFETCHABLE"
                } else {
                    "NOT-CHECKED"
                }),
            );
            m.insert("why".into(), json!(first.why));
            m
        } else {
            best_of(&target, &read, &links, &states)
        };
        let mut r = p.as_object().cloned().unwrap_or_default();
        r.insert(
            "matched".into(),
            json!(if original.is_empty() {
                "quote"
            } else {
                "original"
            }),
        );
        r.extend(best);
        results.push(r);
    }
    let readable = readability(&results, &states, !read.is_empty());
    let mut out = note.clone();
    out.insert(
        "passages".into(),
        Value::Array(results.into_iter().map(Value::Object).collect()),
    );
    out.insert("readability".into(), json!(readable));
    out
}

/// A citation's readability: READABLE is the live link's verdict, an archived text's confirmation counted only where that link answered.
fn readability(results: &[Map<String, Value>], states: &[Got], fetched: bool) -> &'static str {
    let flag = |r: &Map<String, Value>, k: &str| r.get(k).is_some_and(l7r_shared::pyjson::truthy);
    if results.is_empty() {
        "-"
    } else if states.iter().all(|s| s.state == "OWN") {
        "NOT-READABLE (the link is this project's own page)"
    } else if results
        .iter()
        .all(|r| word(r) == "VERBATIM" || flag(r, "only_reference_markers"))
    {
        let dead = states
            .iter()
            .any(|s| s.state == "FETCHED" && truthy_text(s.archived.as_ref()).is_some() && !s.live);
        if dead && results.iter().any(|r| flag(r, "archived")) {
            "-"
        } else {
            "READABLE"
        }
    } else if fetched
        && results
            .iter()
            .any(|r| matches!(word(r), "NOT-ON-PAGE" | "DIFFERS"))
    {
        "NOT-READABLE (the page was read and does not carry the passage as quoted)"
    } else {
        "-"
    }
}

/// `report`: each note judged where it is a citation, its assertion beside it.
pub fn report(
    notes: &[Map<String, Value>],
    claims: &Map<String, Value>,
    get: &mut dyn FnMut(&str) -> Got,
) -> Vec<Map<String, Value>> {
    notes
        .iter()
        .map(|note| {
            let mut entry = if note.get("class").and_then(Value::as_str) == Some("citation") {
                judge_note(note, get)
            } else {
                let mut e = note.clone();
                e.insert("readability".into(), json!("-"));
                e
            };
            let id = note.get("id").and_then(Value::as_str).unwrap_or("");
            entry.insert(
                "assertion".into(),
                claims.get(id).cloned().unwrap_or_else(|| json!("")),
            );
            entry
        })
        .collect()
}

#[cfg(test)]
mod tests;
