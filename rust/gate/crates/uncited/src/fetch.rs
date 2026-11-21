//! The fetch (feature 312 FR-007): every page of the set with no saved text, or a shell of one, read into the page cache - live, then the
//! Wayback Machine's newest snapshot - or ruled unreadable with its access state. In lanes, every URL of one host in one lane (the
//! archive's rule: never two requests to a host at once); the Python's lanes were processes, these are threads, each with its own
//! browser, as the archive's backfill.

use std::path::Path;
use std::sync::Mutex;

use l7r_gate_archive::backfill::{lanes, RECYCLE_EVERY};
use l7r_gate_archive::fetch::{fetch, wayback, Client};
use l7r_gate_research::pages::{put, Stored};
use l7r_shared::attempts::{self, More};
use l7r_shared::consulted;
use serde_json::json;

use crate::lists::{line, not_kept};
use crate::rule::{access_of, needs_fetch, no_substance};
use crate::{chars, record_dir, strip, text_of, Error, Result, EMPTY, SHELL_CHARS};

/// How a browser starts (the archive's `l7r-browser serve`, or a test's stand-in).
pub type Start = dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync;

/// A browser started on first use, as the Python's `Browser` started its process on its first request: a start that fails is that
/// page's error, and the next page tries again.
pub struct Lazy<'a> {
    start: &'a Start,
    root: &'a Path,
    client: Option<Box<dyn Client>>,
}

impl<'a> Lazy<'a> {
    #[must_use]
    pub fn new(start: &'a Start, root: &'a Path) -> Self {
        Self {
            start,
            root,
            client: None,
        }
    }

    /// The browser, started if it is not.
    ///
    /// # Errors
    /// It will not start.
    pub fn get(&mut self) -> Result<&mut dyn Client> {
        if self.client.is_none() {
            self.client = Some((self.start)(self.root)?);
        }
        Ok(self
            .client
            .as_deref_mut()
            .unwrap_or_else(|| unreachable!("started above")))
    }

    /// A fresh browser on the next use.
    pub fn recycle(&mut self) {
        self.client = None;
    }
}

/// `got.text.strip()` where the fetch brought a page (a text, no error, a status under 400), else nothing.
#[must_use]
pub fn live_text(got: &l7r_gate_archive::fetch::Fetched) -> String {
    if !got.text.is_empty() && got.error.is_empty() && got.status.is_some_and(|s| s != 0 && s < 400)
    {
        strip(&got.text).to_owned()
    } else {
        String::new()
    }
}

/// Read one page into the cache: live, then the Wayback Machine's newest snapshot. A read replaces saved text only when it is longer.
/// Returns `("", "")` when the page now has more than an empty shell, or (its access state, why).
///
/// # Errors
/// The browser, a blocked URL, the cache.
pub fn fetch_one(browser: &mut Lazy<'_>, root: &Path, url: &str) -> Result<(String, String)> {
    let home = consulted::home(root);
    let record = record_dir(root);
    let mut have = strip(&text_of(&home, url)?.unwrap_or_default()).to_owned();
    let got = fetch(browser.get()?, url, &record)?;
    let mut text = live_text(&got);
    let (state, why) = if text.is_empty() {
        let status = got
            .status
            .map_or_else(|| "None".to_owned(), |s| s.to_string());
        let why = if got.error.is_empty() {
            format!("HTTP {status}")
        } else {
            got.error.clone()
        };
        (access_of(&got).to_owned(), why)
    } else {
        (String::new(), String::new())
    };
    let mut origin = "fetch";
    if chars(&text) < SHELL_CHARS {
        if let Some((snap, _)) = wayback(browser.get()?, url)? {
            let old = fetch(browser.get()?, &snap, &record)?;
            let old_text = strip(&old.text);
            if !old.text.is_empty() && chars(old_text) > chars(&text) {
                old_text.clone_into(&mut text);
                origin = "wayback";
            }
        }
    }
    if chars(&text) > chars(&have) {
        put(
            &home,
            url,
            &text,
            &Stored {
                fetched: None,
                exact: true,
                origin,
            },
            &record,
        )?;
        have = text;
    }
    if chars(&have) >= EMPTY {
        return Ok((String::new(), String::new()));
    }
    Ok((
        if state.is_empty() {
            "down".to_owned()
        } else {
            state
        },
        if why.is_empty() {
            "an empty page".to_owned()
        } else {
            why
        },
    ))
}

/// What a lane counts.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Counts {
    pub read: usize,
    pub unreadable: usize,
    pub error: usize,
}

/// One lane: every page of `urls` with no saved text, or a shell of one, read or ruled unreadable; a fresh browser every
/// [`RECYCLE_EVERY`] URLs, and after a page whose read failed. Each page's line is said as it goes.
///
/// # Errors
/// The cache, the attempts log or the not-kept list (a page's own fetch failing is its `error` line, not the lane's).
pub fn lane(
    root: &Path,
    urls: &[String],
    start: &Start,
    say: &(dyn Fn(&str) + Sync),
) -> Result<Counts> {
    lane_every(root, urls, start, say, RECYCLE_EVERY)
}

/// [`lane`] with a fresh browser every `every` URLs: its test recycles at the third page rather than the twenty-fifth, each unreadable
/// page's two log lines starting four processes, 26 pages of them past FR-008's tenth of a second (feature 449 T167).
fn lane_every(
    root: &Path,
    urls: &[String],
    start: &Start,
    say: &(dyn Fn(&str) + Sync),
    every: usize,
) -> Result<Counts> {
    let home = consulted::home(root);
    let mut browser = Lazy::new(start, root);
    let mut counts = Counts::default();
    for (i, u) in urls.iter().enumerate() {
        if no_substance(u) || !needs_fetch(&home, u)? {
            continue;
        }
        if (i + 1) % every == 0 {
            browser.recycle();
        }
        let (state, why) = match fetch_one(&mut browser, root, u) {
            Ok(got) => got,
            Err(err) => {
                // a browser that died under one page (Playwright "Event loop is closed!", 2026-10-02) ends one page's read, not the
                // lane: the page is left unjudged for the next run, and the lane gets a fresh browser
                say(&format!(
                    "{:22} {u} - {}: {}",
                    "error",
                    err.kind,
                    crate::first(&err.message, 120)
                ));
                counts.error += 1;
                browser.recycle();
                continue;
            }
        };
        let outcome = if state.is_empty() {
            "unknown"
        } else {
            "unreadable"
        };
        let more = More {
            route: "uncited-fetch",
            ..More::default()
        };
        attempts::add(
            root,
            u,
            "unknown",
            "feature 312's filter: is the page worth keeping",
            outcome,
            &more,
            &record_dir(root),
        )?;
        if state.is_empty() {
            counts.read += 1;
            say(&format!("{:22} {u}", "read"));
        } else {
            not_kept(
                root,
                &[line(u, &["unreadable".to_owned()], "rule", &why, &state)?],
            )?;
            counts.unreadable += 1;
            say(&format!("{:22} {u}", format!("unreadable {state}")));
        }
    }
    Ok(counts)
}

/// The fetch in lanes, every URL of one host in one lane; the lanes' counts summed.
///
/// # Errors
/// A lane's error (the first a lane met), as the Python's pool re-raised it.
pub fn fetch_all(
    root: &Path,
    urls: &[String],
    workers: i64,
    start: &Start,
    say: &(dyn Fn(&str) + Sync),
) -> Result<serde_json::Value> {
    let jobs = lanes(urls, usize::try_from(workers.max(1)).unwrap_or(1));
    let total = Mutex::new(Counts::default());
    let first_error: Mutex<Option<Error>> = Mutex::new(None);
    std::thread::scope(|s| {
        for job in &jobs {
            let (total, first_error) = (&total, &first_error);
            s.spawn(move || match lane(root, job, start, say) {
                Ok(c) => {
                    if let Ok(mut t) = total.lock() {
                        t.read += c.read;
                        t.unreadable += c.unreadable;
                        t.error += c.error;
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
    Ok(json!({"read": t.read, "unreadable": t.unreadable, "error": t.error}))
}

#[cfg(test)]
mod tests;
