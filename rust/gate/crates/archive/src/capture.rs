//! One capture (`archive.py`'s second part; ported by feature 449 T146): a cited URL's outcome and the files that go in the archive for
//! it, in the order of plan D2 - the live fetch first; a DEAD page then a Wayback snapshot, then the GM's copy, else `unreachable`; a
//! REFUSED page the GM's copy first, then a snapshot, else `partial`.

use std::path::Path;

use l7r_guard::shared::sha256;
use serde_json::{json, Map, Value};

use crate::fetch::{ext_of, failure, fetch, revision, snapshot_raw, wayback, Client, Fetched};
use crate::Result;

/// Files by name, in the order the Python's dict kept them.
pub type Files = Vec<(String, Vec<u8>)>;

/// One URL's outcome and the files that go in the archive for it, by name in the Python's order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Capture {
    pub outcome: String,
    pub files: Vec<(String, Vec<u8>)>,
    pub record: Map<String, Value>,
    pub reason: String,
}

/// `served.<ext>`, `page.mhtml` where it rendered and `text.txt` where it has text.
#[must_use]
pub fn files_of(got: &Fetched) -> Vec<(String, Vec<u8>)> {
    let mut out = vec![(
        format!("served{}", ext_of(&got.content_type, got.landed())),
        got.body.clone(),
    )];
    if !got.mhtml.is_empty() {
        out.push(("page.mhtml".to_owned(), got.mhtml.clone().into_bytes()));
    }
    if !got.text.is_empty() {
        out.push(("text.txt".to_owned(), got.text.clone().into_bytes()));
    }
    out
}

/// The capture's record, its keys in the Python's order.
#[must_use]
pub fn record_of(url: &str, got: &Fetched, origin: &str) -> Map<String, Value> {
    let mut m = Map::new();
    m.insert("url".into(), json!(url));
    m.insert("fetched_url".into(), json!(got.url));
    m.insert("final_url".into(), json!(got.landed()));
    m.insert(
        "status".into(),
        got.status.map_or(Value::Null, |s| json!(s)),
    );
    m.insert("content_type".into(), json!(got.content_type));
    m.insert("sha256".into(), json!(sha256::hex(&got.body)));
    m.insert("bytes".into(), json!(got.body.len()));
    m.insert(
        "revision".into(),
        json!(if got.is_html() {
            revision(&got.body)
        } else {
            String::new()
        }),
    );
    m.insert("origin".into(), json!(origin));
    m.insert("whole_page".into(), json!(!got.mhtml.is_empty()));
    m
}

/// `{**a, k: v}`: `a` with `k` set, an existing key keeping its place.
#[must_use]
pub fn with(mut a: Map<String, Value>, k: &str, v: Value) -> Map<String, Value> {
    a.insert(k.to_owned(), v);
    a
}

/// The newest Wayback snapshot of `url` captured, or none where there is none or it will not fetch.
///
/// # Errors
/// As [`fetch`] and [`wayback`].
pub fn from_snapshot(
    client: &mut dyn Client,
    url: &str,
    reason: &str,
    record_dir: &Path,
) -> Result<Option<Capture>> {
    let Some((at, when)) = wayback(client, url)? else {
        return Ok(None);
    };
    let mut old = fetch(client, &snapshot_raw(&at), record_dir)?;
    if failure(&at, &old).0 == "dead" {
        return Ok(None);
    }
    if old.is_html() {
        let (mhtml, shown) = client.render(&at);
        old.mhtml = mhtml;
        if !shown.is_empty() {
            old.text = shown;
        }
    }
    Ok(Some(Capture {
        outcome: "archived-earlier-snapshot".to_owned(),
        files: files_of(&old),
        record: with(
            record_of(url, &old, &format!("wayback {when}")),
            "live_failure",
            json!(reason),
        ),
        reason: reason.to_owned(),
    }))
}

/// One cited URL captured in the order of plan D2 (see the module).
///
/// # Errors
/// As [`fetch`] and [`wayback`]: a blocked URL, or an answer the Python raised on.
pub fn capture(
    client: &mut dyn Client,
    url: &str,
    has_gm_copy: bool,
    cache_text: &str,
    record_dir: &Path,
) -> Result<Capture> {
    let live = fetch(client, url, record_dir)?;
    let (kind, reason) = failure(url, &live);
    if kind.is_empty() && live.is_html() && live.mhtml.is_empty() {
        return Ok(Capture {
            outcome: "partial".to_owned(),
            files: files_of(&live),
            record: record_of(url, &live, "live"),
            reason: "the page would not render whole: its served HTML and text are kept".to_owned(),
        });
    }
    if kind.is_empty() {
        return Ok(Capture {
            outcome: "archived".to_owned(),
            files: files_of(&live),
            record: record_of(url, &live, "live"),
            reason: String::new(),
        });
    }
    let served = if live.body.is_empty() {
        Vec::new()
    } else {
        files_of(&live)
    };
    let cached: Vec<(String, Vec<u8>)> = if cache_text.is_empty() {
        Vec::new()
    } else {
        vec![(
            "page-cache-text.txt".to_owned(),
            cache_text.as_bytes().to_vec(),
        )]
    };
    let base = if live.body.is_empty() {
        let mut m = Map::new();
        m.insert("url".into(), json!(url));
        m.insert("live_failure".into(), json!(reason));
        m
    } else {
        with(record_of(url, &live, "live"), "live_failure", json!(reason))
    };
    let gm = has_gm_copy.then(|| Capture {
        outcome: "archived-gm-copy".to_owned(),
        files: served.clone(),
        record: with(base.clone(), "origin", json!("the GM's downloaded copy")),
        reason: reason.clone(),
    });
    let otherwise = |outcome: &str, files: Vec<(String, Vec<u8>)>| Capture {
        outcome: outcome.to_owned(),
        files,
        record: base.clone(),
        reason: reason.clone(),
    };
    if kind == "refused" {
        if let Some(gm) = gm {
            return Ok(gm);
        }
        let found = from_snapshot(client, url, &reason, record_dir)?;
        return Ok(found.unwrap_or_else(|| otherwise("partial", merged(served, cached))));
    }
    let found = from_snapshot(client, url, &reason, record_dir)?;
    Ok(found
        .or(gm)
        .unwrap_or_else(|| otherwise("unreachable", cached)))
}

/// `{**a, **b}` of two file lists.
fn merged(a: Vec<(String, Vec<u8>)>, b: Vec<(String, Vec<u8>)>) -> Vec<(String, Vec<u8>)> {
    let mut out = a;
    for (k, v) in b {
        match out.iter_mut().find(|(n, _)| *n == k) {
            Some(slot) => slot.1 = v,
            None => out.push((k, v)),
        }
    }
    out
}

/// A file past this is stored in parts: GitHub refuses a file past 100 MB, and 95 leaves room.
pub const PART: usize = 95 * (1 << 20);

/// Files past `part` bytes cut into `<name>.partN`, with each whole file's SHA-256 and part count to join it by.
#[must_use]
pub fn split_large(files: Files, part: usize) -> (Files, Map<String, Value>) {
    let mut out = Vec::new();
    let mut parts = Map::new();
    for (name, body) in files {
        if body.len() <= part {
            out.push((name, body));
            continue;
        }
        let pieces: Vec<&[u8]> = body.chunks(part.max(1)).collect();
        for (n, piece) in pieces.iter().enumerate() {
            out.push((format!("{name}.part{}", n + 1), piece.to_vec()));
        }
        parts.insert(
            name,
            json!({"parts": pieces.len(), "sha256": sha256::hex(&body), "bytes": body.len()}),
        );
    }
    (out, parts)
}

#[cfg(test)]
mod tests;
