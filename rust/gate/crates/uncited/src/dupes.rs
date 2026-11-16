//! The kept pages that are one work with another (feature 312, the write-ups' dedupe): by URL under another spelling, by the same saved
//! text, or by a body similar to a page on the same host once the host's boilerplate is set aside.

use std::collections::{HashMap, HashSet};
use std::path::Path;

use l7r_guard::shared::consulted::{self, norm};

use crate::entries::{entry_holding, merge};
use crate::lists::{field, read, unkeep};
use crate::set::work;
use crate::{name_of, read_text, registry_files, squeeze, text_of, Result, KEPT};

/// A page's character 4-grams.
pub type Grams = HashSet<[char; 4]>;

/// Retired unread only at or above this; below it a pair is listed to read - the North and South magistracy pages of one ward site, two
/// works, scored 0.78 once their live text replaced the saved copies (2026-10-02).
pub const SIMILAR_SURE: f64 = 0.95;
/// Measured 2026-10-02 over the kept pages: one article under two URLs (redirects, variants, an import and a fetch) 0.69-1.00; two pages
/// of one site or one property sharing its template (two magistrate offices, two Yokota buildings, two blog posts) 0.51-0.59. Two true
/// pairs fall below (生垣, 庙会, 0.57) - left to source-applicability.
pub const SIMILAR: f64 = 0.65;
/// The 4-grams a host repeats on this many pages or more are its boilerplate.
pub const BOILERPLATE_DOCS: usize = 4;

/// The saved text of one revision, whatever URL reached it: two redirects to one article (杖刑 and 笞刑, 2026-10-02) save the same body.
/// The head is skipped (the title a redirect may carry); a page too short to tell gives none.
#[must_use]
pub fn fingerprint(text: Option<&str>) -> String {
    let body: Vec<char> = squeeze(text.unwrap_or("")).chars().collect();
    if body.len() < 1000 {
        return String::new();
    }
    let tail: String = body[200..].iter().collect();
    l7r_guard::shared::sha1::hex(tail.as_bytes())
}

/// Every `n`-gram of a text's first `limit` characters, its whitespace squeezed first.
#[must_use]
pub fn grams_of(text: &str, limit: usize) -> Grams {
    let t: Vec<char> = squeeze(text).chars().take(limit).collect();
    t.windows(4).map(|w| [w[0], w[1], w[2], w[3]]).collect()
}

/// Character 4-grams of a page's first 30,000 characters; what the host repeats is set aside by [`boilerplate`].
#[must_use]
pub fn body_grams(text: Option<&str>) -> Grams {
    grams_of(text.unwrap_or(""), 30_000)
}

/// The share of two sets' grams held by both (0 where either is empty).
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "counts of grams, as the Python divided them"
)]
pub fn overlap(a: &Grams, b: &Grams) -> f64 {
    if a.is_empty() || b.is_empty() {
        return 0.0;
    }
    let both = a.iter().filter(|g| b.contains(*g)).count();
    both as f64 / (a.len() + b.len() - both) as f64
}

/// The 4-grams a host repeats on [`BOILERPLATE_DOCS`] pages or more (navigation, a category's navbox, a database's template). One work
/// saved as two or three spellings (a redirect, a variant, an import) shares its own text on at most three; short articles of one category
/// share only their navbox, and without this scored as one work (寺内町 and 宿場, 2026-10-02).
#[must_use]
pub fn boilerplate(docs: &[&Grams]) -> Grams {
    let mut df: HashMap<[char; 4], usize> = HashMap::new();
    for d in docs {
        for g in *d {
            *df.entry(*g).or_default() += 1;
        }
    }
    df.into_iter()
        .filter(|(_, n)| *n >= BOILERPLATE_DOCS)
        .map(|(g, _)| g)
        .collect()
}

/// A URL's host as the duplicates read it: its normalized form up to the first `/`.
fn host_of(n: &str) -> String {
    n.split('/').next().unwrap_or_default().to_owned()
}

/// A duplicate found: the kept page's raw URL, what it duplicates (a key or an earlier kept page's raw URL), and why.
pub type Duplicate = (String, String, String);

/// Kept pages that are one work with a cited entry's URL or an earlier kept page - by URL under another spelling ([`work`]), by the same
/// saved text ([`fingerprint`]), or by a body [`SIMILAR`] to a page on the same host once the host's boilerplate is set aside.
///
/// # Errors
/// The registry, the kept list or the cache that will not read.
pub fn duplicate_works(root: &Path) -> Result<Vec<Duplicate>> {
    let mut seen: HashMap<String, String> = HashMap::new();
    let home = consulted::home(root);
    let mut cited: Vec<(String, String, Grams)> = Vec::new();
    for f in registry_files(root) {
        if f.parent().map(name_of).as_deref()
            == Some(&name_of(std::path::Path::new(crate::UNCITED)))
        {
            continue;
        }
        let name = name_of(&f);
        let stem = name.strip_suffix(".html").unwrap_or(&name);
        let key = stem
            .split_once('-')
            .map(|(_, k)| k.to_owned())
            .unwrap_or_default();
        for u in l7r_gate_archive::ops::urls_in(&read_text(&f)?) {
            // the citation's closing parenthesis, which the URL pattern takes in
            let u = u.trim_end_matches(|c| ").,;:".contains(c));
            seen.entry(work(&norm(u))).or_insert_with(|| key.clone());
            cited.push((
                host_of(&norm(u)),
                key.clone(),
                body_grams(text_of(&home, u)?.as_deref()),
            ));
        }
    }
    let mut kept: Vec<(String, String, Option<String>)> = Vec::new();
    for x in read(root, KEPT)? {
        let raw = field(&x, "raw")?;
        let text = text_of(&home, &raw)?;
        kept.push((field(&x, "url")?, raw, text));
    }
    let kept_g: Vec<Grams> = kept
        .iter()
        .map(|(_, _, t)| body_grams(t.as_deref()))
        .collect();
    let mut by_host: HashMap<String, Vec<&Grams>> = HashMap::new();
    for (host, _, g) in &cited {
        by_host.entry(host.clone()).or_default().push(g);
    }
    for ((url, _, _), g) in kept.iter().zip(&kept_g) {
        by_host.entry(host_of(url)).or_default().push(g);
    }
    let common: HashMap<String, Grams> = by_host
        .iter()
        .map(|(h, d)| (h.clone(), boilerplate(d)))
        .collect();
    let mut bodies: HashMap<String, Vec<(Grams, String)>> = HashMap::new();
    for (host, key, g) in &cited {
        if !g.is_empty() {
            let less: Grams = g.difference(&common[host]).copied().collect();
            bodies
                .entry(host.clone())
                .or_default()
                .push((less, key.clone()));
        }
    }
    let mut out = Vec::new();
    for ((url, raw, text), g) in kept.iter().zip(kept_g) {
        let host = host_of(url);
        // every kept page's host is among the hosts the boilerplate was read over
        let g: Grams = g.difference(&common[&host]).copied().collect();
        let marks: Vec<String> = [work(url), fingerprint(text.as_deref())]
            .into_iter()
            .filter(|m| !m.is_empty())
            .collect();
        let mut hit = marks
            .iter()
            .find_map(|m| seen.get(m))
            .map(|k| (k.clone(), "same URL or text".to_owned()));
        if hit.as_ref().is_none_or(|(k, _)| k.is_empty()) {
            // `max` over (score, key) pairs: a tie on the score goes to the greater key
            let best = bodies
                .get(&host)
                .into_iter()
                .flatten()
                .map(|(b, k)| (overlap(&g, b), k))
                .fold(None::<(f64, &String)>, |acc, x| match acc {
                    Some(a) if (a.0, a.1) >= (x.0, x.1) => Some(a),
                    _ => Some(x),
                });
            hit = best
                .filter(|(s, _)| *s >= SIMILAR)
                .map(|(s, k)| (k.clone(), format!("similar {s:.2}")));
        }
        if let Some((k, why)) = hit.filter(|(k, _)| !k.is_empty()) {
            out.push((raw.clone(), k, why));
        } else {
            for m in &marks {
                seen.insert(m.clone(), raw.clone());
            }
            if !g.is_empty() {
                bodies.entry(host).or_default().push((g, raw.clone()));
            }
        }
    }
    Ok(out)
}

/// Every duplicate [`duplicate_works`] finds retired: a written entry by `merge`, an unwritten kept page by moving its line to the
/// not-kept list. What it duplicates stays (a cited entry, or the first kept page). A pair only similar below [`SIMILAR_SURE`] is listed to
/// read, never retired.
///
/// # Errors
/// The duplicates, an entry, the merge or the move.
pub fn dedupe(root: &Path, dry: bool) -> Result<Vec<String>> {
    let mut done = Vec::new();
    for (raw, into, why) in duplicate_works(root)? {
        let into_key = if into.starts_with("http") {
            entry_holding(root, &into)?
                .filter(|k| !k.is_empty())
                .unwrap_or_else(|| into.clone())
        } else {
            into.clone()
        };
        let key = entry_holding(root, &raw)?.filter(|k| !k.is_empty());
        let shown = key.clone().unwrap_or_else(|| raw.clone());
        let similar = why.starts_with("similar");
        let score: f64 = why
            .split_whitespace()
            .nth(1)
            .and_then(|s| s.parse().ok())
            .unwrap_or(1.0);
        if similar && score < SIMILAR_SURE {
            done.push(format!("{shown} ~ {into_key} ({why} - read both; `make uncited DO=merge KEY= INTO=` if one work)"));
            continue;
        }
        if !dry {
            match &key {
                Some(k) => {
                    merge(root, k, &into_key)?;
                }
                None => unkeep(
                    root,
                    &raw,
                    &["duplicate".to_owned()],
                    "rule",
                    &format!("the same work as {into_key}"),
                )?,
            }
        }
        done.push(format!(
            "{shown} -> {into_key}{}",
            if similar {
                format!(" ({why})")
            } else {
                String::new()
            }
        ));
    }
    Ok(done)
}

#[cfg(test)]
mod tests;
