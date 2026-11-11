//! The modal-depiction answers recorded under an earlier fingerprint formula that still answer their pop-up (from `record_owed.py`,
//! feature 449 T87; split from `answers.rs` by T92 to keep it under the file cap).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{answered, read_answer};
use crate::record::modals::{self, Modal};
use crate::record::repo::{git, Fail};
use crate::record::units::re;

static LINE_NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(r":\d+$"));

/// The pop-up `m` as its file stood when an answer was recorded at `utc`, or None.
fn modal_then(root: &Path, m: &Modal, utc: &str) -> Option<Modal> {
    let rel = if LINE_NUMBERED.is_match(&m.origin).unwrap_or(false) {
        m.origin.rsplit_once(':').map_or(m.origin.as_str(), |p| p.0)
    } else {
        m.origin.as_str()
    };
    let then = git(
        root,
        &[
            "rev-list",
            "-1",
            &format!("--before={utc}"),
            "HEAD",
            "--",
            rel,
        ],
    );
    let then = then.trim();
    if then.is_empty() || !rel.as_bytes().ends_with(b".md") {
        return None;
    }
    let text = git(root, &["show", &format!("{then}:{rel}")]);
    modals::choice_modal(rel, &text, true)
}

/// A modal-depiction answer recorded under the fingerprint's old formula still answers the words it read.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn legacy_depiction_answered(
    root: &Path,
    store_dir: &Path,
    slug: &str,
    modals_now: &[Modal],
) -> Result<bool, Fail> {
    let Some(kind) = slug.strip_prefix("modal-depiction:") else {
        return Ok(false);
    };
    let rec = read_answer(store_dir, slug);
    let Some(m) = modals::find(modals_now, kind) else {
        return Ok(false);
    };
    let utc = rec.get("utc").and_then(Value::as_str).unwrap_or("");
    if utc.is_empty()
        || !answered(
            store_dir,
            slug,
            &modals::legacy_depiction_fingerprint(root, m)?,
            "",
        )
    {
        return Ok(false);
    }
    Ok(modal_then(root, m, utc).is_some_and(|old| old.entry() == m.entry()))
}

/// A modal-depiction answer recorded under amendment 1's formula still answers its pop-up where what the check judges since amendment 6 is unchanged since the answer.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn amendment1_depiction_answered(
    root: &Path,
    store_dir: &Path,
    slug: &str,
    modals_now: &[Modal],
) -> Result<bool, Fail> {
    let Some(kind) = slug.strip_prefix("modal-depiction:") else {
        return Ok(false);
    };
    let rec = read_answer(store_dir, slug);
    let Some(m) = modals::find(modals_now, kind) else {
        return Ok(false);
    };
    let utc = rec.get("utc").and_then(Value::as_str).unwrap_or("");
    if utc.is_empty() {
        return Ok(false);
    }
    let Some(old) = modal_then(root, m, utc) else {
        return Ok(false);
    };
    Ok(answered(
        store_dir,
        slug,
        &modals::amendment1_depiction_fingerprint(root, &old)?,
        "",
    ) && modals::depiction_fingerprint(root, &old)? == modals::depiction_fingerprint(root, m)?)
}
