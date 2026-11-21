//! The page cache's imported copies, read live and checked (feature 312, research.md R5; `scripts/record/uncited_imports.py`, ported by
//! feature 449 T147): `verify` reads each imported copy live and records whether it was this page, another page's text, or could not be
//! told; `copy_verdicts` lists the filter verdicts that blamed a saved copy on a page now read live, to read and then requeue or mark
//! `stands`. Run through `make uncited DO=verify|copy-verdicts|stands`.

use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::{LazyLock, Mutex};

use fancy_regex::Regex;
use l7r_gate_archive::backfill::lanes;
use l7r_gate_archive::fetch::fetch;
use l7r_gate_research::pages::{cached, entry_dir, put, Stored};
use l7r_shared::consulted::{self, norm};
use l7r_shared::pyjson::py_str;
use serde_json::{json, Value};

use crate::fetch::{live_text, Lazy, Start};
use crate::lists::{field, get, read, write};
use crate::{
    chars, first, py, record_dir, text_of, today, Error, Result, EMPTY, MISFILED, NOT_KEPT,
};

/// The page's saved text when it came from feature 288's one-time import of old saves, which filed some pages' text under another URL
/// (observed 2026-10-02: `ja.wikipedia.org/wiki/村` held 砂利道's article) - else none.
///
/// # Errors
/// The cache's read.
pub fn imported(home: &Path, url: &str) -> Result<Option<String>> {
    let hit = cached(home, url, 10_000.0, false)?;
    Ok(hit
        .filter(|h| {
            h.meta
                .get("origin")
                .map(py_str)
                .unwrap_or_default()
                .starts_with("import")
        })
        .map(|h| h.text))
}

/// Text decoded in the wrong charset: more than 1% replacement characters (U+FFFD).
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "a count against a hundredth of a length, as the Python compared them"
)]
pub fn garbled(text: &str) -> bool {
    let n = chars(text);
    n >= EMPTY && text.chars().filter(|c| *c == '\u{fffd}').count() as f64 > n as f64 / 100.0
}

/// The share of a text's characters that are Chinese or Japanese (`[぀-ヿ㐀-鿿]`).
#[expect(
    clippy::cast_precision_loss,
    reason = "a share of characters, as the Python divided them"
)]
fn cjk(t: &str) -> f64 {
    let c = t
        .chars()
        .filter(|ch| matches!(u32::from(*ch), 0x3040..=0x30ff | 0x3400..=0x9fff))
        .count();
    c as f64 / chars(t).max(1) as f64
}

/// A live read that is less than the copy it would replace: under half its length (Adachi's page came back as a machine-translation
/// notice), or a Chinese or Japanese page come back mostly in Latin script (Osaka Info's English edition) - observed 2026-10-02.
#[must_use]
pub fn worse_read(old: &str, live: &str) -> bool {
    chars(live) * 2 < chars(old) || (cjk(old) > 0.2 && cjk(live) < cjk(old) / 4.0)
}

/// Two texts of one page: their character 4-grams over the first 5,000 characters overlap by a third or more (a page re-fetched later
/// differs by its edits and its navigation, never by its subject).
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "counts of grams, as the Python divided them"
)]
pub fn same_page(a: &str, b: &str) -> bool {
    let (ga, gb) = (
        crate::dupes::grams_of(a, 5000),
        crate::dupes::grams_of(b, 5000),
    );
    if ga.is_empty() || gb.is_empty() {
        return false;
    }
    let both = ga.iter().filter(|g| gb.contains(*g)).count();
    both as f64 / (ga.len() + gb.len() - both) as f64 >= 1.0 / 3.0
}

/// What a verify lane counts, by result.
pub type Tally = [usize; 3];

const RESULTS: [&str; 3] = ["same", "misfiled", "unread"];

/// Each URL whose saved text is an imported copy, read live: the copy replaced by the live text, and a line in `import-check.jsonl` saying
/// whether the copy was this page (`same`), another page's (`misfiled`), or could not be told (`unread`). A misfiled page's verdict is then
/// judged again from the live text. Each page's line is said as it goes.
///
/// # Errors
/// The cache, the browser, a blocked URL, the check's list.
pub fn verify(
    root: &Path,
    urls: &[String],
    start: &Start,
    say: &(dyn Fn(&str) + Sync),
) -> Result<Tally> {
    let home = consulted::home(root);
    let mut browser = Lazy::new(start, root);
    let mut counts = [0; 3];
    for u in urls {
        let Some(old) = imported(&home, u)? else {
            continue;
        };
        let got = fetch(browser.get()?, u, &record_dir(root))?;
        let mut live = live_text(&got);
        // a mis-decoded, cut or translated read never replaces a copy (2026-10-02)
        if garbled(&live) || worse_read(&old, &live) {
            live = String::new();
        }
        let result = if chars(&live) < EMPTY {
            2
        } else {
            usize::from(!same_page(&old, &live))
        };
        if result == 1 {
            // kept beside the live text: the 4-gram measure flags a skin change as readily as another page (R5), so a flag is confirmed
            // by reading before `requeue`
            let d = entry_dir(&home, u);
            crate::mkdir(&d)?;
            crate::write_text(&d.join("imported.txt"), &old)?;
        }
        if !live.is_empty() && result != 2 {
            put(
                &home,
                u,
                &live,
                &Stored {
                    fetched: None,
                    exact: true,
                    origin: "fetch",
                },
                &record_dir(root),
            )?;
        }
        write(
            root,
            &[json!({"url": norm(u), "raw": u, "result": RESULTS[result], "date": today()})],
            MISFILED,
        )?;
        counts[result] += 1;
        say(&format!("{:10} {u}", RESULTS[result]));
    }
    Ok(counts)
}

/// The verify in lanes, each with its own browser; the lanes' counts summed.
///
/// # Errors
/// A lane's error (the first a lane met).
pub fn verify_all(
    root: &Path,
    urls: &[String],
    workers: i64,
    start: &Start,
    say: &(dyn Fn(&str) + Sync),
) -> Result<Value> {
    let jobs = lanes(urls, usize::try_from(workers.max(1)).unwrap_or(1));
    let total = Mutex::new([0; 3]);
    let first_error: Mutex<Option<Error>> = Mutex::new(None);
    std::thread::scope(|s| {
        for job in &jobs {
            let (total, first_error) = (&total, &first_error);
            s.spawn(move || match verify(root, job, start, say) {
                Ok(c) => {
                    let mut t = total
                        .lock()
                        .unwrap_or_else(std::sync::PoisonError::into_inner);
                    for (a, b) in t.iter_mut().zip(c) {
                        *a += b;
                    }
                }
                Err(e) => {
                    if let Ok(mut f) = first_error.lock() {
                        f.get_or_insert(e);
                    }
                }
            });
        }
    });
    if let Some(e) = first_error.into_inner().ok().flatten() {
        return Err(e);
    }
    let t = total.into_inner().unwrap_or_default();
    Ok(json!({"same": t[0], "misfiled": t[1], "unread": t[2]}))
}

/// Every page-cache entry that came from the one-time import - cited and uncited alike (the defect is the cache's).
///
/// # Errors
/// A `meta.json` that will not read.
pub fn imported_urls(home: &Path) -> Result<Vec<String>> {
    let mut out = Vec::new();
    for shard in crate::entries(&home.join(l7r_gate_research::pages::CACHE)) {
        for entry in crate::entries(&shard) {
            let meta = entry.join("meta.json");
            if !meta.is_file() {
                continue;
            }
            let m = crate::loads(&crate::read_text(&meta)?)?;
            let text = |k: &str| get(&m, k).map(|v| v.map(py_str).unwrap_or_default());
            if text("origin")?.starts_with("import") && text("url")?.starts_with("http") {
                out.push(field(&m, "url")?);
            }
        }
    }
    Ok(out)
}

/// A not-kept note that blames the saved copy rather than the page (2026-10-02: two blogs ruled unreadable from mojibake imports and a
/// village page ruled no-substance from a title-only shell, each readable live).
static COPY_FAULT: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r"(?i)mojibake|saved text|saved copy|title only|shell|encod|garbage|garbled|JavaScript|captcha|challenge|truncat",
    )
});

/// Pages to read and, if the page is readable, `requeue`: a filter verdict whose note blames the saved copy, on a page the import check
/// has since read live into the cache readable (1,500 characters or more, not garbled).
///
/// # Errors
/// The lists or the cache.
pub fn copy_verdicts(root: &Path) -> Result<Vec<String>> {
    let mut nk: HashMap<String, Value> = HashMap::new();
    for x in read(root, NOT_KEPT)? {
        if get(&x, "basis")?.and_then(Value::as_str) == Some("source-filter") {
            nk.insert(field(&x, "url")?, x);
        }
    }
    let rows = read(root, MISFILED)?;
    let mut stood = HashSet::new();
    for x in &rows {
        if field(x, "result")? == "verdict-stands" {
            stood.insert(field(x, "url")?);
        }
    }
    let home = consulted::home(root);
    let mut out = Vec::new();
    for x in &rows {
        let url = field(x, "url")?;
        let v = if stood.contains(&url) {
            None
        } else {
            nk.get(&url)
        };
        let Some(v) = v else { continue };
        let note = get(v, "note")?.map(py_str).unwrap_or_default();
        let result = field(x, "result")?;
        if !(matches!(result.as_str(), "same" | "misfiled")
            && COPY_FAULT.is_match(&note).unwrap_or(false))
        {
            continue;
        }
        let raw = field(x, "raw")?;
        let text = text_of(&home, &raw)?.unwrap_or_default();
        if chars(&text) >= 1500 && !garbled(&text) {
            let reasons: Vec<String> = get(v, "reasons")?
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .map(py_str)
                .collect();
            out.push(format!(
                "{raw}  ({}: {})",
                reasons.join(", "),
                first(&note, 90)
            ));
        }
    }
    Ok(out)
}

/// A page [`copy_verdicts`] listed, read, and its verdict found sound (the live page is as the verdict says): it leaves the list.
///
/// # Errors
/// The check's list.
pub fn stands(root: &Path, raw: &str, note: &str) -> Result<()> {
    write(
        root,
        &[
            json!({"url": norm(raw), "raw": raw, "result": "verdict-stands", "note": note, "date": today()}),
        ],
        MISFILED,
    )
}

#[cfg(test)]
mod tests;
