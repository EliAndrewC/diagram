//! A claim's label against its own words, flagged at `make claims-owed` (`scripts/record/claims_labels.py`, ported by feature 449 T82;
//! feature 405 T120, plan D91): a GUESS that says the code departs from a page, a bare GUESS naming the page that speaks, a `GUESS <page>`
//! whose page states no such figure. A flag, never a refusal.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::grammar::Claim;
use super::index::Cur;
use crate::record::units::re;

/// An account saying the code departs from a page.
static DEPARTS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(?:stricter|looser|wider|narrower|tighter|closer|farther) than (?:the page|its page|0\d{3}\b)|\bshort of (?:the page|its page|0\d{3}\b)|\bdepart(?:s|ing|ure)? from\b|\bstricter than\b",
    )
});
/// A question named in an account.
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\d.])0\d{3}\b"));
/// An account that says the named page is silent on this, or the figure is ours.
static SILENT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\bsilent\b|\bno page\b|\bdoes not (?:say|size|give|state|name)\b|\bis ours\b|\bour own\b|\bunsized\b",
    )
});
/// A figure in feet, as an account writes it.
static FEET: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:ft|feet|foot)\b"));

fn states(text: &str, fig: &str) -> bool {
    let fig = fig.strip_suffix(".0").unwrap_or(fig);
    re(&format!(
        r"(?<![\d.]){}(?!\d|\.\d)",
        fancy_regex::escape(fig)
    ))
    .is_match(text)
    .unwrap_or(false)
}

fn found(pat: &Regex, text: &str) -> bool {
    pat.is_match(text).unwrap_or(false)
}

/// The label faults of one claim, each with its fix.
pub fn flag(
    key: &str,
    claim: &Claim,
    qdir: &Path,
    pages: &mut HashMap<String, String>,
) -> Vec<String> {
    if claim.backing != "GUESS" {
        return Vec::new();
    }
    let account = &claim.account;
    let mut out = Vec::new();
    if found(&DEPARTS, account) {
        out.push(format!("claims-label: {key} - its account says the code departs from a page: that is `DEVIATION <page>`, recorded on the page (or say why the page does not speak, and keep GUESS)"));
    }
    if claim.pointers.is_empty() && found(&NAMED, account) && !found(&SILENT, account) {
        let names: BTreeSet<&str> = NAMED
            .find_iter(account)
            .flatten()
            .map(|m| m.as_str())
            .collect();
        out.push(format!(
            "claims-label: {key} - a bare GUESS says no page speaks, but its account names {}: cite the page if it states this, `GUESS <its .drawing.html>` if it records it as a guess, `DEVIATION <page>` if the code departs (or say the page is silent)",
            names.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    if !claim.pointers.is_empty() {
        for p in &claim.pointers {
            pages.entry(p.clone()).or_insert_with(|| {
                let f = qdir.join(Path::new(p).file_name().unwrap_or_default());
                std::fs::read(&f)
                    .map(|b| crate::record::repo::universal(&String::from_utf8_lossy(&b)))
                    .unwrap_or_default()
            });
        }
        let texts: Vec<&String> = claim.pointers.iter().map(|p| &pages[p]).collect();
        let mut seen = HashSet::new();
        let missing: Vec<String> = FEET
            .captures_iter(account)
            .flatten()
            .map(|c| c[1].to_owned())
            .filter(|fig| seen.insert(fig.clone()))
            .filter(|fig| !texts.iter().any(|t| states(t, fig)))
            .collect();
        if !missing.is_empty() {
            let shown: Vec<String> = missing.iter().map(|m| format!("{m} ft")).collect();
            out.push(format!(
                "claims-label: {key} - `GUESS <page>` says the page records this guess, but no page it names states {}: a bare GUESS if no page speaks, `DEVIATION <page>` if the code departs from the page's figure",
                shown.join(", ")
            ));
        }
    }
    out
}

/// Every label fault among the claims of `keys`.
pub fn flags(cur: &Cur, keys: &[String], qdir: &Path) -> Vec<String> {
    let mut pages = HashMap::new();
    let mut seen = HashSet::new();
    let mut out = Vec::new();
    for k in keys {
        if !seen.insert(k.clone()) {
            continue;
        }
        if let Some(row) = cur.get(k) {
            out.extend(flag(k, &row.claim, qdir, &mut pages));
        }
    }
    out
}

#[cfg(test)]
mod tests;
