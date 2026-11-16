//! THE SET (feature 312 FR-006): computed, never listed - the ledger's and the page cache's URLs with no archive manifest row
//! (`archive_ops.consulted_urls`), less any URL a registry entry carries (a cited URL under another spelling, or an uncited entry
//! already written), less any URL with a verdict, less a blocked domain; plus the manifest rows that no key and no footnote cite.
//! Re-run it after later research and it holds only the pages read since.

use std::collections::HashSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::consulted::{self, norm};
use l7r_guard::shared::pyjson::{py_str, truthy};

use crate::lists::{field, get, read, urls_of};
use crate::{key_of, name_of, py, read_text, registry_files, Result, KEPT, NOT_KEPT};

/// The GM's own campaign notes are canon, never an uncited source (the GM, 2026-10-02: *"we should probably never do that, just as a
/// general rule"*): no page of theirs enters the set.
static CANON: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?i)^github\.com/eliandrewc/|^raw\.githubusercontent\.com/eliandrewc/"));
static KOTOBANK: LazyLock<Regex> = LazyLock::new(|| py(r"^kotobank\.jp/word/[^/]*-(\d+)$"));
static OPENALEX: LazyLock<Regex> = LazyLock::new(|| py(r"^api\.openalex\.org/works/doi:(.+)$"));
static GITHUB_RAW: LazyLock<Regex> =
    LazyLock::new(|| py(r"^raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/"));
/// Wikisource too: the Zuo zhuan's Duke Cheng was kept under /zh-hant/ beside its cited /wiki/ page (2026-10-02).
static ZH_VARIANT: LazyLock<Regex> = LazyLock::new(|| {
    py(r"^zh\.(wikipedia|wikisource)\.org/(?:zh-(?:hans|hant|cn|tw|hk|sg|mo)|wiki)/")
});
/// One file server under two names (Yannopoulos 2015 on both, 2026-10-02).
const HOST_ALIASES: [(&str, &str); 2] = [
    ("mdpi-res.com/", "res.mdpi.com/"),
    ("online.bunka.go.jp/", "bunka.nii.ac.jp/"),
];

/// The URLs with a verdict, kept or not.
///
/// # Errors
/// A list that will not read, or a line with no URL.
pub fn judged(root: &Path) -> Result<HashSet<String>> {
    let mut out = urls_of(&read(root, NOT_KEPT)?)?;
    out.extend(urls_of(&read(root, KEPT)?)?);
    Ok(out)
}

/// Every URL any registry entry carries, cited or uncited, normalized.
///
/// # Errors
/// An entry that will not read.
pub fn registry_norms(root: &Path) -> Result<HashSet<String>> {
    let mut out = HashSet::new();
    for f in registry_files(root) {
        out.extend(
            l7r_gate_archive::ops::urls_in(&read_text(&f)?)
                .iter()
                .map(|u| norm(u)),
        );
    }
    Ok(out)
}

/// The manifest rows nothing cites - no key, no footnote: the captures made before the GM held the backfill.
///
/// # Errors
/// A row that will not read.
pub fn prehold(root: &Path) -> Result<Vec<String>> {
    let mut out = Vec::new();
    for p in l7r_gate_archive::manifest::row_files(root) {
        let r = l7r_gate_archive::manifest::load_row(&p)?;
        if !get(&r, "keys")?.is_some_and(truthy) && !get(&r, "notes")?.is_some_and(truthy) {
            out.push(field(&r, "url")?);
        }
    }
    Ok(out)
}

/// The URLs the ledger marks `cited:<key>` whose key still has a registry entry: a page cited under another spelling of its URL (FR-022,
/// research.md R4 - six of the eight, each covered by its key's archived copy). A mark whose key no entry holds is not a citation, and
/// its page is judged like any other.
///
/// # Errors
/// The ledger that will not read, a row no mapping or with no URL.
pub fn cited_marks(root: &Path) -> Result<HashSet<String>> {
    let keys: HashSet<String> = registry_files(root)
        .iter()
        .filter_map(|f| key_of(&name_of(f)).map(str::to_owned))
        .collect();
    let mut out = HashSet::new();
    for r in consulted::read(&consulted::home(root))? {
        let outcome = get(&r, "outcome")?.map(py_str).unwrap_or_default();
        if let Some(key) = outcome.strip_prefix("cited:") {
            if keys.contains(crate::strip(key)) {
                out.insert(field(&r, "url")?);
            }
        }
    }
    Ok(out)
}

/// One work under one key: a normalized URL with Chinese Wikipedia's script variants folded into `/wiki/` - the same article served as
/// `/zh-hans/X`, `/zh-tw/X` and `/wiki/X` was judged and written up twice (Pingyao's wall, 2026-10-02).
#[must_use]
pub fn work(n: &str) -> String {
    let n = ZH_VARIANT.replace(n, "zh.${1}.org/wiki/");
    // a file by its raw URL and its page URL (daizhige, 2026-10-02)
    let n = GITHUB_RAW.replace(&n, "github.com/${1}/${2}/blob/${3}/");
    // Kotobank serves an entry by its number, whatever word is in front (2026-10-02)
    let n = KOTOBANK.replace(&n, "kotobank.jp/word/${1}");
    // OpenAlex's record of a DOI is that DOI's work: a check read the cited Northampton abstract there (2026-10-02)
    let n = OPENALEX.replace(&n, "doi.org/${1}").into_owned();
    for (alias, host) in HOST_ALIASES {
        if let Some(rest) = n.strip_prefix(alias) {
            return format!("{host}{rest}");
        }
    }
    n
}

/// Whether a normalized URL is the GM's own canon.
#[must_use]
pub fn canon(n: &str) -> bool {
    CANON.is_match(n).unwrap_or(false)
}

/// The set: each work once, by its first spelling read, sorted.
///
/// # Errors
/// A list, the registry, the ledger, the cache or the blocked list that will not read.
pub fn uncited_set(root: &Path) -> Result<Vec<String>> {
    let mut skip_from = judged(root)?;
    skip_from.extend(registry_norms(root)?);
    skip_from.extend(cited_marks(root)?);
    let skip: HashSet<String> = skip_from.iter().map(|n| work(n)).collect();
    let rules = l7r_gate_research::record::blocked::domains(&crate::record_dir(root))?;
    let mut out: Vec<String> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();
    let mut all = l7r_gate_archive::ops::consulted_urls(root)?;
    all.extend(prehold(root)?);
    for u in all {
        let n = work(&norm(&u));
        if !skip.contains(&n)
            && l7r_guard::shared::blocked::blocked(&u, &rules).is_none()
            && !canon(&n)
            && seen.insert(n)
        {
            out.push(u);
        }
    }
    out.sort();
    Ok(out)
}

#[cfg(test)]
mod tests;
