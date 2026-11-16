//! Blocked domains and banned citations: the one decision every fetch route, every store and the build ask (`record/blocked.py`, feature
//! 312; ported by feature 449 T144). A BLOCKED DOMAIN (an AI-generated site) is refused everywhere; a source forbidden for any other reason
//! is BANNED AT THE CITATION by URL pattern, never by domain (the GM, 2026-10-02). Every entry carries the GM's approval, or the list is
//! refused. The domain half - the list, a URL's host, the rule and its message - is the guard's `shared::blocked`, which the
//! `blocked-fetch` guard reads too (FR-003); the patterns and the build's census are here.

use std::cell::OnceCell;
use std::path::Path;

use fancy_regex::Regex;
use l7r_guard::shared::blocked::{approval, load};
pub use l7r_guard::shared::blocked::{host, refusal, Rule, DOMAINS};
use l7r_guard::shared::pyjson::{py_str, value_repr};

use crate::record::archive;
use crate::{Error, Result};

pub const CITATIONS: &str = "banned-citations.json";

/// Every blocked domain (`blocked.domains`).
///
/// # Errors
/// The list's refusal: no approval, no domain or reason, not JSON.
pub fn domains(record_dir: &Path) -> Result<Vec<Rule>> {
    Ok(l7r_guard::shared::blocked::domains(record_dir)?)
}

/// Every banned pattern, each compiled (`blocked.patterns`).
///
/// # Errors
/// The list's refusal, or a pattern that does not compile (its message the regex library's words).
pub fn patterns(record_dir: &Path) -> Result<Vec<(Regex, Rule)>> {
    let (place, rows) = load(record_dir, CITATIONS, "pattern")?;
    let mut out = Vec::new();
    for (m, raw) in rows {
        let text = py_str(&m);
        let compiled = Regex::new(&text).map_err(|e| {
            Error::new(
                "BlockedListError",
                format!("{place}: pattern {} does not compile ({e})", value_repr(&m)),
            )
        })?;
        let rule = Rule {
            matches: text,
            reason: py_str(&raw["reason"]),
            approved: approval(&place, &raw)?,
        };
        out.push((compiled, rule));
    }
    Ok(out)
}

/// The two lists of one record, each read the first time it is needed, as the Python's cached readers were.
struct Lists<'d> {
    dir: &'d Path,
    domains: OnceCell<Vec<Rule>>,
    patterns: OnceCell<Vec<(Regex, Rule)>>,
}

impl<'d> Lists<'d> {
    fn new(dir: &'d Path) -> Self {
        Self {
            dir,
            domains: OnceCell::new(),
            patterns: OnceCell::new(),
        }
    }

    fn blocked(&self, url: &str) -> Result<Option<Rule>> {
        if self.domains.get().is_none() {
            let _ = self.domains.set(domains(self.dir)?);
        }
        let rules = self.domains.get().map_or(&[][..], Vec::as_slice);
        Ok(l7r_guard::shared::blocked::blocked(url, rules).cloned())
    }

    fn banned(&self, url: &str) -> Result<Option<Rule>> {
        if let Some(rule) = self.blocked(url)? {
            return Ok(Some(rule));
        }
        if self.patterns.get().is_none() {
            let _ = self.patterns.set(patterns(self.dir)?);
        }
        let rules = self.patterns.get().map_or(&[][..], Vec::as_slice);
        Ok(rules
            .iter()
            .find(|(p, _)| p.is_match(url).unwrap_or(false))
            .map(|(_, r)| r.clone()))
    }
}

/// The blocked-domain rule a URL falls under: its host is the domain or a subdomain of it.
///
/// # Errors
/// The list's refusal.
pub fn blocked(url: &str, record_dir: &Path) -> Result<Option<Rule>> {
    Lists::new(record_dir).blocked(url)
}

/// The banned-citation rule a URL matches (a blocked domain is banned too).
///
/// # Errors
/// Either list's refusal, the patterns' only where the domains did not already answer.
pub fn banned(url: &str, record_dir: &Path) -> Result<Option<Rule>> {
    Lists::new(record_dir).banned(url)
}

/// Refuse a URL on a blocked domain - the call every fetch route and store makes first.
///
/// # Errors
/// `Blocked`, its message the one refusal; or the list's own refusal.
pub fn check(url: &str, what: &str, record_dir: &Path) -> Result<()> {
    match blocked(url, record_dir)? {
        Some(rule) => Err(Error::new("Blocked", refusal(url, &rule, what))),
        None => Ok(()),
    }
}

/// One build refusal per cited URL - a registry entry's (its comments' too) or a footnote's link - on a blocked domain or matching a
/// banned pattern (FR-003, FR-004); the census is the archive's, so what the build calls cited is one thing everywhere.
///
/// # Errors
/// The registry's or a list's refusal.
pub fn refusals(record_dir: &Path) -> Result<Vec<String>> {
    let lists = Lists::new(record_dir);
    let mut out = Vec::new();
    for (url, who) in archive::cited(record_dir)? {
        let Some(rule) = lists.banned(&url)? else {
            continue;
        };
        let place = [who.keys.clone(), who.notes.clone()].concat().join(", ");
        let listed = if lists.blocked(&url)?.is_some() {
            DOMAINS
        } else {
            CITATIONS
        };
        out.push(format!(
            "banned citation: {url} ({place}) is on {listed} ({} - {}) - cite the fact from another source, or state its absence (feature 312)",
            rule.matches, rule.reason
        ));
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
