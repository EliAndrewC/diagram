//! The doors Python's `archive.py` forwards through until S3b (`uncited.py`, `uncited_imports.py`, `archive_ops.py`) and S4
//! (`research_search.py`, `semantic_index.py`) port its importers (feature 449 T146; FR-003: ONE writer of the archive's working copy and
//! of its manifest rows, this crate; `ask:449-T86-door`: a name a command can carry goes by command). Each verb is one function here:
//!
//! - `ensure --home H [--remote R]`, `push --home H`, `place-gm --home H --name N` (the entry as JSON on stdin): the working copy's
//!   writes the Python makes while it holds the archive's lock itself (`Archive.locked`), so these never take it - taking it again from
//!   another process would wait on the caller forever;
//! - `url-row --root R --url U [--no-push]` (who cites it as JSON on stdin), `lane --root R [--rows FILE]` (its URLs on stdin, a line
//!   each; its rows to FILE, a JSON line each),
//!   `settle --root R`, `sync-gm --root R`, `write-row --root R --url U` (the row on stdin): the manifest's writers;
//! - `serve --root R`: the browser, a JSON line at a time - `get`, `render`, `fetch` and `wayback`, each body through the file the asker
//!   names - for Python's `archive.Browser`, `fetch` and `wayback`.
//!
//! A raise prints `<Kind>: <message>` on stderr and exits 1; the Python forwarder raises the same kind.

use std::io::BufRead;
use std::path::{Path, PathBuf};

use l7r_gate_core::record::args::{parse, Spec};
use l7r_gate_research::record::archive::Cited;
use serde_json::{json, Value};

use super::{raised, reply};
use crate::backfill::{lane, Lane};
use crate::fetch::{fetch, wayback, Client, Fetched};
use crate::manifest::{archive_url, place_gm, settle, sync_gm_copies, write_row};
use crate::store::Archive;
use crate::{Error, Reply, Result};

fn read_all(input: &mut dyn BufRead) -> String {
    let mut text = String::new();
    let _ = input.read_to_string(&mut text);
    text
}

fn json_in(input: &mut dyn BufRead) -> Result<Value> {
    l7r_guard::shared::pyjson::loads(&read_all(input))
        .map_err(|e| Error::new("JSONDecodeError", e.to_string()))
}

fn strings(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(Value::as_array)
        .map(|a| a.iter().map(l7r_guard::shared::pyjson::py_str).collect())
        .unwrap_or_default()
}

/// One forwarded verb.
#[must_use]
pub fn cli(verb: &str, args: &[String], reach: &mut super::Reach<'_>) -> Reply {
    let start = reach.start;
    let input: &mut dyn BufRead = reach.input;
    let specs = [
        Spec::value("--home"),
        Spec::value("--root"),
        Spec::value("--remote"),
        Spec::value("--name"),
        Spec::value("--url"),
        Spec::flag("--no-push"),
        Spec::value("--rows"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(e) => {
            return reply(
                String::new(),
                format!("l7r-gate record archive {verb}: error: {e}\n"),
                2,
            )
        }
    };
    let root = PathBuf::from(p.text("--root", "."));
    let mut store = Archive::new(Path::new(p.text("--home", ".")), None);
    if p.has("--remote") {
        p.text("--remote", "").clone_into(&mut store.remote);
    }
    let done: Result<String> = match verb {
        "ensure" => store.ensure().map(|()| String::new()),
        "push" => store.push(),
        "place-gm" => {
            json_in(input).and_then(|entry| place_gm(&store, p.text("--name", ""), &entry))
        }
        "url-row" => json_in(input).and_then(|who| {
            let who = Cited {
                keys: strings(&who, "keys"),
                notes: strings(&who, "notes"),
            };
            let mut client = start(&root)?;
            let row = archive_url(
                &root,
                p.text("--url", ""),
                &who,
                client.as_mut(),
                &store,
                !p.on("--no-push"),
            )?;
            Ok(Value::Object(row).to_string())
        }),
        "lane" => {
            let urls: Vec<String> = read_all(input)
                .lines()
                .filter(|l| !l.is_empty())
                .map(str::to_owned)
                .collect();
            l7r_gate_research::record::archive::cited(&root.join("research"))
                .map_err(Error::from)
                .and_then(|who| {
                    let how = Lane {
                        root: &root,
                        who: &who,
                        start,
                        say: reach.say,
                    };
                    // the rows, a JSON line each, to the file `--rows` names: the Python's `_lane` returned them
                    let rows = lane(&how, &urls, &store)?;
                    let lines: String = rows
                        .into_iter()
                        .map(|r| Value::Object(r).to_string() + "\n")
                        .collect();
                    let at = p.text("--rows", "/dev/null");
                    std::fs::write(at, lines)
                        .map_err(|e| Error::new("OSError", format!("{e}: '{at}'")))?;
                    Ok(String::new())
                })
        }
        "settle" => settle(&root).map(|n| n.to_string()),
        "sync-gm" => sync_gm_copies(&root, &store).map(|n| n.to_string()),
        "write-row" => json_in(input)
            .and_then(|row| write_row(&root, p.text("--url", ""), &row).map(|()| String::new())),
        _ => return serve(&root, input, reach.output, start),
    };
    match done {
        Ok(text) if text.is_empty() => reply(String::new(), String::new(), 0),
        Ok(text) => reply(format!("{text}\n"), String::new(), 0),
        Err(e) => raised(String::new(), &e),
    }
}

/// A fetch's fields as the door answers them, its body written to `out`.
fn fetched(got: &Fetched, out: &str) -> Value {
    let _ = std::fs::write(out, &got.body);
    json!({"url": got.url, "status": got.status, "final_url": got.final_url, "content_type": got.content_type,
           "mhtml": got.mhtml, "text": got.text, "error": got.error})
}

fn raise(e: &Error) -> Value {
    json!({"raise": e.kind, "message": e.message})
}

/// `serve --root R`: a browser for the Python's `Browser`, a JSON line in and out at a time until `close` or the end of the input.
pub fn serve(
    root: &Path,
    input: &mut dyn BufRead,
    output: &mut dyn std::io::Write,
    start: &(dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync),
) -> Reply {
    let mut client = match start(root) {
        Ok(c) => c,
        Err(e) => {
            let _ = writeln!(output, "{}", raise(&e));
            return reply(String::new(), String::new(), 1);
        }
    };
    let _ = writeln!(output, "{}", json!({"ready": true})).and_then(|()| output.flush());
    let record_dir = root.join("research");
    let mut line = String::new();
    while input.read_line(&mut line).unwrap_or(0) > 0 {
        let asked: Value = serde_json::from_str(&line).unwrap_or(Value::Null);
        line.clear();
        let text = |k: &str| {
            asked
                .get(k)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        let (url, out) = (text("url"), text("out"));
        let answer = match text("op").as_str() {
            "get" => fetched(&client.get(&url), &out),
            "render" => {
                let (mhtml, shown) = client.render(&url);
                json!({"mhtml": mhtml, "text": shown})
            }
            "fetch" => fetch(client.as_mut(), &url, &record_dir)
                .map_or_else(|e| raise(&e), |g| fetched(&g, &out)),
            "wayback" => wayback(client.as_mut(), &url).map_or_else(
                |e| raise(&e),
                |s| json!({"snapshot": s.map(|(u, t)| vec![u, t])}),
            ),
            "close" => break,
            other => json!({"raise": "ValueError", "message": format!("unknown op {other:?}")}),
        };
        if writeln!(output, "{answer}")
            .and_then(|()| output.flush())
            .is_err()
        {
            break;
        }
    }
    reply(String::new(), String::new(), 0)
}

#[cfg(test)]
mod tests;
