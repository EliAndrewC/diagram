//! `l7r-browser serve`: one browser context held open for a caller that asks it, a JSON line at a time, for a request or a render
//! (feature 449 T146) - the gate's `archive` crate, whose capture logic `archive.py` was, and the `uncited` crate's fetch (T147, where
//! Python's `archive.Browser` forwarder reached it). One process a context, as `archive.py` held one Playwright context a `Browser`.
//!
//! In: `{"op": "get", "url", "headers": [[name, value], ...], "timeout_ms", "max_redirects", "out"}` (the body written to `out`),
//! `{"op": "render", "url", "timeout_ms", "idle_ms"}`, `{"op": "close"}`. Out, a line each: `{"status", "url", "content_type"}`,
//! `{"mhtml", "text"}`, or `{"error"}`; first of all `{"ready": true}` once the browser is up.

use std::io::{BufRead, Write};
use std::path::Path;
use std::time::Duration;

use serde_json::{json, Value};

use crate::get::{get, Ask};
use crate::page::Browser;

/// `inner_text`'s wait for a body: Playwright's default timeout.
const BODY_WAIT: Duration = Duration::from_secs(30);

/// One render: the page loaded, its network idle (or the idle wait over), its MHTML and its body's text; the page closed either way.
///
/// # Errors
/// The navigation's, the snapshot's or the text's failure.
pub fn render(
    b: &mut Browser,
    url: &str,
    timeout: Duration,
    idle: Duration,
) -> Result<(String, String), String> {
    let page = b.new_page()?;
    let mut steps = || -> Result<(String, String), String> {
        let loader = b.goto(&page, url, timeout)?;
        if !loader.is_empty() {
            b.wait_idle(&page, &loader, idle);
        }
        let mhtml = b.mhtml(&page)?;
        Ok((mhtml, b.body_text(&page, BODY_WAIT)?))
    };
    let done = steps();
    b.close_page(&page);
    done
}

fn number(v: &Value, key: &str, default: u64) -> u64 {
    v.get(key).and_then(Value::as_u64).unwrap_or(default)
}

fn text<'a>(v: &'a Value, key: &str) -> &'a str {
    v.get(key).and_then(Value::as_str).unwrap_or_default()
}

/// The answer to one asked line.
fn answer(b: &mut Browser, user_agent: &str, asked: &Value) -> Value {
    let error = |e: String| json!({"error": e});
    match text(asked, "op") {
        "get" => {
            let headers: Vec<(String, String)> = asked
                .get("headers")
                .and_then(Value::as_array)
                .map(|a| {
                    a.iter()
                        .filter_map(|h| {
                            Some((
                                h.get(0)?.as_str()?.to_owned(),
                                h.get(1)?.as_str()?.to_owned(),
                            ))
                        })
                        .collect()
                })
                .unwrap_or_default();
            let ask = Ask {
                url: text(asked, "url"),
                headers: &headers,
                timeout: Duration::from_millis(number(asked, "timeout_ms", 60_000)),
                max_redirects: u32::try_from(number(asked, "max_redirects", 10)).unwrap_or(10),
                user_agent,
                program: "curl",
            };
            get(b, &ask, Path::new(text(asked, "out"))).map_or_else(
                error,
                |g| json!({"status": g.status, "url": g.url, "content_type": g.content_type}),
            )
        }
        "render" => render(
            b,
            text(asked, "url"),
            Duration::from_millis(number(asked, "timeout_ms", 60_000)),
            Duration::from_millis(number(asked, "idle_ms", 10_000)),
        )
        .map_or_else(error, |(mhtml, text)| json!({"mhtml": mhtml, "text": text})),
        other => error(format!("unknown op {other:?}")),
    }
}

/// Answers each line of `input` on `output` until a `close` or the end of the input.
pub fn serve(b: &mut Browser, user_agent: &str, input: &mut dyn BufRead, output: &mut dyn Write) {
    // the caller waits for this line, so a browser that could not start is told apart from one slow to answer
    if writeln!(output, "{}", json!({"ready": true}))
        .and_then(|()| output.flush())
        .is_err()
    {
        return;
    }
    for line in input.lines() {
        let Ok(line) = line else { return };
        let asked: Value = serde_json::from_str(&line).unwrap_or(Value::Null);
        if text(&asked, "op") == "close" {
            return;
        }
        let reply = answer(b, user_agent, &asked);
        if writeln!(output, "{reply}")
            .and_then(|()| output.flush())
            .is_err()
        {
            return;
        }
    }
}

#[cfg(test)]
mod tests;
