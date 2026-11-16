//! A cited URL as the source archive ids it (`l7r/diagram/interactive/record/archive.py`'s `clean` and `url_id`, feature 309): ONE rule
//! for the record's port, the bundles' pointer (`url_of`) and the two guards that read the archive (feature 449 T144, phase 4's S1 under
//! `ask:449-phase4-slices`). The guards had each restated it - `archive-first` with six entities where Python's `html.unescape` decodes them
//! all, `blocked-fetch` with none (its Python, `hm_fetch.archived`, unescaped) - so a URL carrying any other entity was looked up under an
//! id the archive never wrote; one implementation here (FR-003), and the restatements are gone.

use crate::shared::html_text::unescape;
use crate::shared::sha256;

/// `url` less the punctuation a sentence leaves after it: a trailing `.`, `,`, `;` or `:`, and a closing parenthesis only where the URL
/// did not open one, since `(https://.../Edo)` wraps a URL and `町屋_(商家)` is part of one. One character at a time, as the Python loop.
#[must_use]
pub fn trimmed(url: &str) -> &str {
    let mut url = url;
    loop {
        let excess = url.ends_with(')') && url.matches(')').count() > url.matches('(').count();
        if !(excess || url.ends_with(['.', ',', ';', ':'])) {
            return url;
        }
        url = &url[..url.len() - 1];
    }
}

/// A URL as it is cited: entity-unescaped (the record is HTML - `&amp;` in a query is `&`), its fragment dropped, and [`trimmed`].
#[must_use]
pub fn clean(url: &str) -> String {
    let whole = unescape(url);
    trimmed(whole.split('#').next().unwrap_or("")).to_owned()
}

/// A cited URL's manifest id: the first 12 hex of the SHA-256 of the URL as cited ([`clean`]).
#[must_use]
pub fn url_id(url: &str) -> String {
    sha256::hex(clean(url).as_bytes())[..12].to_owned()
}

#[cfg(test)]
mod tests {
    use super::{clean, trimmed, url_id};

    /// Each answer is `archive.clean` / `archive.url_id` on the same text (observed 2026-11-16, `CPython` 3.13).
    #[test]
    fn a_url_is_cleaned_as_the_archive_cleans_it() {
        assert_eq!(trimmed("https://e.org/a_(b))."), "https://e.org/a_(b)");
        assert_eq!(trimmed("https://e.org/x);:,"), "https://e.org/x");
        assert_eq!(
            clean("https://e.org/?a=1&amp;b=2#frag."),
            "https://e.org/?a=1&b=2"
        );
        assert_eq!(clean("https://e.org/&eacute;."), "https://e.org/\u{e9}");
        assert_eq!(url_id("https://example.org/"), "8198d1bac40a");
    }
}
