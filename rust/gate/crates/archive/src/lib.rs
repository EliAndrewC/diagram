//! The source archive's capture (feature 449 T146, phase 4's S3a, `ask:449-phase4-slices`): `scripts/record/archive.py` ported -
//! archive every source the record cites into the PRIVATE repository `EliAndrewC/diagram-research` (feature 309).
//!
//! WHY (the GM, 2026-10-02, `specs/309-source-archive/request.md`): a hedge against *"websites going offline, failing to be maintained"*
//! or *"changing URLs in a website redesign"* - *"backup copies of all of the content we are referencing"*, every web page and every
//! PDF, *"even things which seem at low risk of going away, like wikipedia pages"*, and for a web page *"the whole webpage with images
//! and css and such and not just the html content"*. The repository is PRIVATE on purpose: much of it is copyrighted, and *"for now I
//! just want an archive"*.
//!
//! WHAT A CAPTURE HOLDS (spec FR-002), in `<id[:2]>/<id>/<UTC time>/` of the archive - sharded by the URL id's first two hex digits, so no
//! directory holds more than a few hundred entries (GitHub lists only the first 1,000 of a directory; the GM asked for the layout to stay
//! browsable as the archive grows past 5,000 URLs, 2026-10-02) - with who cites it in `capture.json`: `served.<ext>` the bytes the site
//! served, unaltered; `page.mhtml` a web page whole, as Chromium rendered it, in one file any Chromium browser opens offline (plan D1);
//! `text.txt` its readable text; `capture.json` the URL cited and fetched, the time, the status, the type, the SHA-256, the keys and
//! notes that cite it, and a `MediaWiki` page's revision (plan D7). A file past [`capture::PART`] bytes is written in parts.
//!
//! THE BROWSER is the one browser crate (`rust/browser/`), run as a program ([`client`]): this crate never compiles it, so the gate's
//! build does not either. The modules: [`fetch`] one fetch, [`capture`] one capture, [`store`] the working copy, [`manifest`] the rows and
//! one URL archived, [`backfill`] the lanes, [`ops`] the housekeeping and lookups (`archive_ops.py`, feature 449 T147), [`cli`]
//! `l7r-gate record archive ...`.

use std::fmt;

pub mod backfill;
pub mod capture;
pub mod cli;
pub mod client;
pub mod fetch;
pub mod manifest;
pub mod ops;
pub mod store;

#[cfg(test)]
pub(crate) mod testkit;
// the tests' world for the crates whose tests drive the archive (feature 449 T147: the `uncited` crate), the same file
#[cfg(all(not(test), feature = "testkit"))]
pub mod testkit;

/// A refusal, as the Python raised it: the exception's class name and its message.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error {
    pub kind: &'static str,
    pub message: String,
}

impl Error {
    #[must_use]
    pub fn new(kind: &'static str, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.kind, self.message)
    }
}

impl From<l7r_gate_research::Error> for Error {
    fn from(e: l7r_gate_research::Error) -> Self {
        Self::new(e.kind, e.message)
    }
}

impl From<l7r_guard::shared::blocked::Fault> for Error {
    fn from(f: l7r_guard::shared::blocked::Fault) -> Self {
        Self::new(f.kind, f.message)
    }
}

/// Compiles a pattern the source spells out, with no backtracking limit: Python's `re` has none, and a page's lazy scan to its end
/// (a `<script>` that never closes) ran past `fancy_regex`'s default of a million steps in the research crate's sweeps (feature 449
/// T145), where it panics.
#[must_use]
pub(crate) fn re(pattern: &str) -> fancy_regex::Regex {
    fancy_regex::RegexBuilder::new(pattern)
        .backtrack_limit(usize::MAX)
        .build()
        .unwrap_or_else(|e| unreachable!("{e}"))
}

/// A result of this crate.
pub type Result<T> = std::result::Result<T, Error>;

pub use l7r_gate_core::Reply;

#[cfg(test)]
mod tests;
