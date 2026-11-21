//! The record checks' four helpers, as commands and in process (feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`):
//! `l7r-gate record quote-verbatim` (`quote_verbatim.py`), `record-prepass` (`record_prepass.py`), `style-prepass` (`style_prepass.py`)
//! and `source-pages` (`source_pages.py`), each the Python's `main` over the `research` crate's library. The check bundle calls the same
//! functions in process where it ran them through `scripts/bundle_door.py`'s `run` verb (feature 383 D6), and its residue save calls
//! [`save_cached`] where that runner's `save_cached` verb ran; both verbs, and `passages`, left the runner with this cut. Here because each
//! needs `owed`'s `fragments_for` and `bundle` calls them: the commands' dispatch is the `record` crate's.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_research::pages::{CachedPages, Inner};
use l7r_gate_research::prepass;
use l7r_gate_research::source_pages::{self, Ledger};
use l7r_gate_research::sources::Reader;
use l7r_gate_research::style;
use l7r_gate_research::verbatim::{
    self,
    fetch::{Curl, Got, Pages},
    judge,
};
use l7r_gate_research::{record::notes::render_note, record::site_notes, record::store};
use l7r_shared::consulted;
use l7r_shared::py_text::repr;
use l7r_shared::pyjson::dumps;
use serde_json::{json, Map, Value};

use crate::record::args::{parse_with, Spec};
use crate::record::bundle::py_path;
use crate::record::leaves::fragments_for;
use crate::Reply;

/// What a report's default file name may not hold.
static UNSAFE: std::sync::LazyLock<fancy_regex::Regex> =
    std::sync::LazyLock::new(|| crate::record::units::re(r"[^A-Za-z0-9.-]+"));

/// The environment `source_pages` reads its ledger's context from: the process's.
#[cfg(not(test))]
fn env(name: &str) -> String {
    consulted::var(name)
}

#[cfg(test)]
thread_local! {
    /// The tests' environment, each test thread its own and empty unless a test names a variable: the guard this crate builds on is
    /// compiled without `cfg(test)`, so its own seam reads the shell's (feature 451 T24: an exported `SPECIFY_FEATURE` skipped the
    /// `.specify/feature.json` path a test meant to reach, and the crate's coverage went red).
    pub(crate) static VARS: std::cell::RefCell<std::collections::HashMap<String, String>> = std::cell::RefCell::default();
}

/// The environment `source_pages` reads its ledger's context from: the test thread's own map.
#[cfg(test)]
fn env(name: &str) -> String {
    VARS.with(|v| v.borrow().get(name).cloned().unwrap_or_default())
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A refusal the Python raised and did not catch: exit 1, its kind and words on stderr (`ask:449-usage-text`: the traceback unbound).
fn raised(said: String, e: &l7r_gate_research::Error) -> Reply {
    reply(said, format!("{}: {}\n", e.kind, e.message), 1)
}

/// argparse's own refusal: exit 2, one line naming the command and the complaint (`ask:449-usage-text`).
fn usage(cmd: &str, complaint: &str) -> Reply {
    reply(String::new(), format!("{cmd}: error: {complaint}\n"), 2)
}

/// The repository a path is in: its top, where `.git` is.
fn top(at: &Path) -> PathBuf {
    consulted::repo_root(Some(at))
}

/// The record's blocked lists' tree: the gate's own tree (`L7R_GATE_TREE`), else the repository.
fn record_dir(root: &Path) -> PathBuf {
    crate::record::repo::tree_of(root).join("research")
}

/// `numbered`: a question page with its references numbered from 1, and its notes as `<li id="fn-N">`.
fn numbered(
    reader: &Reader,
    research: &Path,
    file: &str,
) -> l7r_gate_research::Result<(String, String)> {
    let question = reader.record_text(&format!("questions/{file}"))?;
    let notes = store::page_notes(file, research)?;
    let (body, placed) = site_notes::small_page(&question, &notes, file)?;
    Ok((
        body,
        placed
            .iter()
            .map(|n| render_note(n, ""))
            .collect::<Vec<_>>()
            .join("\n"),
    ))
}

/// The questions a run names: `q`'s pages, else every page a section or tag holds.
fn files_named(
    q: &str,
    within: &str,
    root: &Path,
    research: &Path,
) -> l7r_gate_research::Result<Vec<String>> {
    if !q.is_empty() {
        let rooted = l7r_gate_research::resolve(root);
        return Ok(fragments_for(q, &rooted)
            .into_iter()
            .filter(|f| !f.ends_with(".notes.html"))
            .map(|f| f.rsplit('/').next().unwrap_or("").to_owned())
            .collect());
    }
    if within.is_empty() {
        return Ok(Vec::new());
    }
    Ok(store::load(research)?
        .select(within)
        .iter()
        .map(|p| p.file.clone())
        .collect())
}

/// Where `quote_verbatim` reads a page: the offline copies `--offline` names, else the page cache over the network.
fn source_for(offline: &str, cwd: &Path) -> Source {
    if offline.is_empty() {
        let here = top(cwd);
        let home = consulted::home(&here);
        let pages = Pages::new(None, Box::new(Curl::default()));
        Source::Cached(CachedPages::new(
            Inner::Pages(pages),
            &home,
            l7r_gate_research::pages::refresh_wanted(),
            true,
            &here,
            &record_dir(&here),
        ))
    } else {
        Source::Offline(Pages::new(
            Some(&cwd.join(offline)),
            Box::new(Curl::default()),
        ))
    }
}

/// `quote_verbatim.main`: each question's report printed, the JSON for quote-check written.
#[must_use]
pub fn quote_verbatim(args: &[String], cwd: &Path) -> Reply {
    let specs = [
        Spec::value("--in"),
        Spec::value("--notes"),
        Spec::value("--root"),
        Spec::value("--json"),
        Spec::value("--offline"),
    ];
    let parsed = match parse_with(args, &specs, 1) {
        Ok(p) => p,
        Err(e) => return usage("quote_verbatim.py", &e),
    };
    let q = parsed.positional.first().map_or("", String::as_str);
    let (within, root_arg) = (parsed.text("--in", ""), parsed.text("--root", "."));
    let root = cwd.join(root_arg);
    let research = root.join("research");
    let files = match files_named(q, within, &root, &research) {
        Ok(f) => f,
        Err(e) => return raised(String::new(), &e),
    };
    let name = if q.is_empty() {
        format!("IN={within}")
    } else {
        q.to_owned()
    };
    if files.is_empty() {
        let shown = [q, within]
            .into_iter()
            .find(|s| !s.is_empty())
            .unwrap_or("nothing");
        return reply(
            String::new(),
            format!("quote-verbatim: {} names no question - e.g. make quote-verbatim Q=0041 or IN=homesteads\n", repr(shown)),
            2,
        );
    }
    let mut source = source_for(parsed.text("--offline", ""), cwd);
    let only = verbatim::wanted(parsed.text("--notes", ""));
    let reader = Reader::new(&research);
    let (mut said, mut entries) = (String::new(), Vec::new());
    for file in &files {
        let (page, cites) = match numbered(&reader, &research, file) {
            Ok(n) => n,
            Err(e) => return raised(said, &e),
        };
        let notes: Vec<Map<String, Value>> = verbatim::footnotes(&cites)
            .into_iter()
            .filter(|n| verbatim::is_wanted(n, only.as_ref()))
            .collect();
        let mut failed = None;
        // a refusal stops the run where the Python's exception did: nothing after it is fetched or stored
        let mut get = |u: &str| {
            if failed.is_some() {
                return Got::state("UNFETCHABLE", "");
            }
            match source.get(u) {
                Ok(g) => g,
                Err(e) => {
                    failed = Some(e);
                    Got::state("UNFETCHABLE", "")
                }
            }
        };
        let mut mine = judge::report(&notes, &verbatim::assertions(&page), &mut get);
        if let Some(e) = failed {
            return raised(said, &e);
        }
        for e in &mut mine {
            e.insert("question".into(), json!(file));
        }
        said.push_str(&verbatim::render(
            &format!("questions/{file}"),
            &mine,
            &source.refused(),
        ));
        said.push('\n');
        entries.extend(mine);
    }
    let json_arg = parsed.text("--json", "");
    let out = if json_arg.is_empty() {
        let safe = UNSAFE.replace_all(&name, "-");
        py_path(&format!("{root_arg}/.git/quote-verbatim/{safe}.json"))
    } else {
        py_path(json_arg)
    };
    let refused: Map<String, Value> = source
        .refused()
        .into_iter()
        .map(|(h, w)| (h, json!(w)))
        .collect();
    let report = json!({"page": name, "footnotes": entries, "refused": refused});
    let at = cwd.join(&out);
    let written = std::fs::create_dir_all(at.parent().unwrap_or(cwd))
        .and_then(|()| std::fs::write(&at, dumps(&report, Some(1), false) + "\n"));
    if let Err(e) = written {
        return reply(said, format!("OSError: {e}\n"), 1);
    }
    let _ = writeln!(said, "  report for quote-check: {}", out.display());
    reply(said, String::new(), 0)
}

/// Where a run's pages come from: the host's page cache over the network, or saved pages by URL hash.
enum Source {
    Cached(CachedPages),
    Offline(Pages),
}

impl Source {
    fn get(&mut self, url: &str) -> l7r_gate_research::Result<Got> {
        match self {
            Self::Cached(c) => c.get(url),
            Self::Offline(p) => p
                .get(url)
                .map_err(|e| l7r_gate_research::Error::new("ValueError", e)),
        }
    }

    fn refused(&self) -> Vec<(String, String)> {
        match self {
            Self::Cached(c) => c.refused(),
            Self::Offline(p) => p.refused.clone(),
        }
    }
}

/// `record_prepass.main`: the listing for record-format, the files to hand the check, and the JSON where asked.
#[must_use]
pub fn record_prepass(args: &[String], cwd: &Path) -> Reply {
    let specs = [
        Spec::value("--in"),
        Spec::value("--root"),
        Spec::value("--json"),
    ];
    let parsed = match parse_with(args, &specs, 1) {
        Ok(p) => p,
        Err(e) => return usage("record_prepass.py", &e),
    };
    let q = parsed.positional.first().map_or("", String::as_str);
    let (within, root_arg) = (parsed.text("--in", ""), parsed.text("--root", "."));
    let root = cwd.join(root_arg);
    let research = root.join(prepass::RESEARCH);
    let reader = Reader::new(&research);
    let read = || -> l7r_gate_research::Result<(String, String, Vec<String>)> {
        if matches!(q, "sources" | "SOURCES" | "SOURCES.html") {
            return Ok((
                "SOURCES".to_owned(),
                reader.record_text("SOURCES.html")?,
                Vec::new(),
            ));
        }
        let picked = if q.is_empty() && !within.is_empty() {
            store::load(&research)?
                .select(within)
                .iter()
                .map(|p| p.file.clone())
                .collect::<Vec<_>>()
                .join(",")
        } else {
            q.to_owned()
        };
        let rooted = l7r_gate_research::resolve(&root);
        let fragments = if picked.is_empty() {
            Vec::new()
        } else {
            fragments_for(&picked, &rooted)
        };
        let mut pages = Vec::new();
        for f in fragments.iter().filter(|f| !f.ends_with(".notes.html")) {
            pages.push(
                reader.record_text(&format!("questions/{}", f.rsplit('/').next().unwrap_or("")))?,
            );
        }
        let name = if q.is_empty() {
            format!("IN={within}")
        } else {
            q.to_owned()
        };
        Ok((name, pages.join("\n"), fragments))
    };
    let (name, page, fragments) = match read() {
        Ok(r) => r,
        Err(e) => return raised(String::new(), &e),
    };
    if page.is_empty() {
        let shown = [q, within]
            .into_iter()
            .find(|s| !s.is_empty())
            .unwrap_or("nothing");
        return reply(String::new(), format!("record-prepass: {} names no question - e.g. make record-prepass Q=0041, IN=homesteads, or Q=SOURCES\n", repr(shown)), 2);
    }
    let listing = match prepass::read_glossary(&root)
        .and_then(|g| prepass::prepass(&page, &g, Some(&research)))
    {
        Ok(l) => l,
        Err(e) => return raised(String::new(), &e),
    };
    let mut said = prepass::render(&name, &listing) + "\n";
    if !fragments.is_empty() {
        said.push_str("\n## What to hand the check (feature 258)\n\n");
        said.push_str(
            "The files these sections are written in - read THESE, not the built site:\n\n",
        );
        said.push_str(
            &(fragments
                .iter()
                .map(|f| format!("  {f}"))
                .collect::<Vec<_>>()
                .join("\n")
                + "\n"),
        );
    }
    let json_arg = parsed.text("--json", "");
    if !json_arg.is_empty() {
        let body = dumps(&json!({"page": name, "sections": listing}), Some(1), false) + "\n";
        if let Err(e) = std::fs::write(cwd.join(json_arg), body) {
            return reply(said, format!("OSError: {e}\n"), 1);
        }
    }
    reply(said, String::new(), 0)
}

/// `style_prepass.main`: the style guide's mechanical half for the named questions.
#[must_use]
pub fn style_prepass(args: &[String], cwd: &Path) -> Reply {
    let parsed = match parse_with(args, &[Spec::value("--root")], 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => {
            return usage(
                "style_prepass.py",
                "the following arguments are required: q",
            )
        }
        Err(e) => return usage("style_prepass.py", &e),
    };
    let q = &parsed.positional[0];
    let root = cwd.join(parsed.text("--root", "."));
    let root = l7r_gate_research::resolve(&root);
    let rels: Vec<String> = fragments_for(q, &root)
        .into_iter()
        .filter(|r| !r.ends_with(".notes.html"))
        .collect();
    if rels.is_empty() {
        return reply(String::new(), format!("style-prepass: no question is {} - name one by its number, e.g. make style-prepass Q=0041\n", repr(q)), 2);
    }
    let read = |p: &Path| -> Result<String, String> {
        let raw = std::fs::read(p).map_err(|e| format!("OSError: {e}"))?;
        let text = String::from_utf8(raw).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
        Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
    };
    let variants = root.join("research/assets/glossary-variants.txt");
    let words: HashSet<String> = if variants.is_file() {
        match read(&variants) {
            Ok(t) => l7r_shared::checks::reply::py_lines(&t)
                .into_iter()
                .map(|l| l.split('\t').next().unwrap_or("").to_owned())
                .collect(),
            Err(e) => return reply(String::new(), e + "\n", 1),
        }
    } else {
        HashSet::new()
    };
    let (mut notes, mut fragments) = (BTreeMap::new(), Vec::new());
    for r in &rels {
        let name = r.rsplit('/').next().unwrap_or("").to_owned();
        let n = root.join(format!("{}.notes.html", &r[..r.len() - ".html".len()]));
        if n.is_file() {
            match read(&n) {
                Ok(t) => {
                    notes.insert(name.clone(), t);
                }
                Err(e) => return reply(String::new(), e + "\n", 1),
            }
        }
    }
    for r in &rels {
        match read(&root.join(r)) {
            Ok(t) => fragments.push((r.rsplit('/').next().unwrap_or("").to_owned(), t)),
            Err(e) => return reply(String::new(), e + "\n", 1),
        }
    }
    reply(style::report(&fragments, &words, &notes), String::new(), 0)
}

/// `source_pages.main`'s refusals before any page is read: none given, no reason recorded, or a page already judged.
fn source_refusal(
    urls: &[String],
    question: &str,
    sought: &str,
    reread: &str,
    ledger: bool,
    here: &Path,
) -> Option<Reply> {
    if urls.is_empty() {
        return Some(reply(
            String::new(),
            "source-pages: no pointer given - URL=<u1> [URL=<u2> ...]\n".to_owned(),
            2,
        ));
    }
    if ledger && (question.is_empty() || l7r_shared::py_text::strip(sought).is_empty()) {
        return Some(reply(
            String::new(),
            format!("{}\n", source_pages::NEEDS_SOUGHT),
            2,
        ));
    }
    if !ledger
        || matches!(question.to_lowercase().as_str(), "" | "none")
        || source_pages::reason_ok(reread)
    {
        return None;
    }
    let mut err = String::new();
    for u in urls {
        let closed = match source_pages::judged_before(here, u, question) {
            Ok(c) => c,
            Err(e) => return Some(raised(String::new(), &e)),
        };
        for x in closed {
            let f = |k: &str| {
                x.get(k)
                    .map_or_else(|| "None".to_owned(), l7r_shared::pyjson::py_str)
            };
            let _ = writeln!(
                err,
                "source-pages: {u} was already read for question {question} on {}: {} - {}",
                f("date"),
                f("outcome"),
                f("sought")
            );
        }
    }
    if err.is_empty() {
        return None;
    }
    err.push_str("source-pages: a page already judged for this question is read again only with a reason:\n    make source-pages ... REREAD=\"<what changed, or what you look for now that was not looked for then>\"\n");
    Some(reply(String::new(), err, 2))
}

/// `source_pages.main`: each pointer's page saved, the manifest printed.
#[must_use]
pub fn source_pages(args: &[String], cwd: &Path) -> Reply {
    let specs = [
        Spec::value("--quotes"),
        Spec::value("--question"),
        Spec::value("--sought"),
        Spec::value("--reread"),
        Spec::flag("--no-ledger"),
    ];
    let parsed = match parse_with(args, &specs, usize::MAX) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => {
            return usage(
                "source_pages.py",
                "the following arguments are required: out, urls",
            )
        }
        Err(e) => return usage("source_pages.py", &e),
    };
    let (out_arg, urls) = (&parsed.positional[0], &parsed.positional[1..]);
    let (question, sought) = (parsed.text("--question", ""), parsed.text("--sought", ""));
    let ledger_on = !parsed.on("--no-ledger");
    let here = top(cwd);
    if let Some(r) = source_refusal(
        urls,
        question,
        sought,
        parsed.text("--reread", ""),
        ledger_on,
        &here,
    ) {
        return r;
    }
    let quotes: Option<Vec<String>> = match parsed.text("--quotes", "") {
        "" => None,
        path => match std::fs::read_to_string(cwd.join(path))
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
        {
            Some(q) => Some(q),
            None => {
                return reply(
                    String::new(),
                    format!("JSONDecodeError: {path} is not a JSON list of passages\n"),
                    1,
                )
            }
        },
    };
    let home = consulted::home(&here);
    let questions: Vec<String> = if matches!(question.to_lowercase().as_str(), "" | "none") {
        Vec::new()
    } else {
        vec![question.to_owned()]
    };
    let ledger = if ledger_on {
        match consulted::context_from(&here, &env) {
            Ok(ctx) => Some(Ledger {
                home: home.clone(),
                ctx,
                questions,
                root: here.clone(),
                sought: l7r_shared::py_text::strip(sought).to_owned(),
            }),
            Err(e) => return reply(String::new(), format!("{}: {}\n", e.kind, e.message), 1),
        }
    } else {
        None
    };
    let pages = Pages::new(None, Box::new(Curl::default()));
    let mut cache = CachedPages::new(
        Inner::Pages(pages),
        &home,
        l7r_gate_research::pages::refresh_wanted(),
        false,
        &here,
        &record_dir(&here),
    );
    let out = py_path(out_arg);
    let mut said = String::new();
    let rows = match source_pages::save(
        urls,
        &cwd.join(&out),
        &mut cache,
        quotes.as_deref(),
        ledger.as_ref(),
        &mut said,
    ) {
        Ok(r) => r,
        Err(e) => return raised(said, &e),
    };
    said.push_str(
        &std::fs::read_to_string(cwd.join(&out).join("MANIFEST.txt")).unwrap_or_default(),
    );
    let saved = rows.iter().filter(|r| r.state == "FETCHED").count();
    let _ = writeln!(
        said,
        "  saved {saved} of {} to {} - hand source-reader the manifest",
        rows.len(),
        out.display()
    );
    reply(said, String::new(), 0)
}

/// The check bundle's residue save: `source_pages.save` of `urls` into `out` from the host's page cache only, a page it does not hold
/// named and never fetched (`bundle_door.save_cached`'s port).
///
/// # Errors
/// What the save refused, as the runner's error was.
pub fn save_cached(urls: &[String], out: &Path) -> Result<(), String> {
    let here = top(Path::new("."));
    let home = consulted::home(&here);
    let mut cache = CachedPages::new(
        Inner::NotCached,
        &home,
        false,
        false,
        &here,
        &record_dir(&here),
    );
    let mut said = String::new();
    source_pages::save(urls, out, &mut cache, None, None, &mut said)
        .map(|_| ())
        .map_err(|e| format!("{}: {}", e.kind, e.message))
}

/// What a check bundle's helper printed and its exit, run in process (stdout then stderr, as the runner captured them).
#[must_use]
pub fn run(name: &str, args: &[String], root: &Path) -> Option<(i32, String)> {
    let got = match name {
        "quote_verbatim" => quote_verbatim(args, root),
        "record_prepass" => record_prepass(args, root),
        "style_prepass" => style_prepass(args, root),
        "source_pages" => source_pages(args, root),
        _ => return None,
    };
    Some((got.code, got.stdout + &got.stderr))
}

#[cfg(test)]
mod tests;
