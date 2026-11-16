//! The one browser crate (feature 449 T146, phase 4's S3a; the round arbiter's `ask:449-phase4-slices` Q4 and `ask:449-T80-order` step
//! 4): headless Chromium over the `DevTools` protocol, never Playwright. It serves the source archive's fetch (the gate's `archive`
//! crate runs `l7r-browser serve` for `archive.py`'s requests and renders), the depiction bundle's glyph crop (`l7r-browser crop`, for
//! `glyph_crop.py`), and at S7 `page_lit`'s pixel reads. Its own binary: the gate and the guard reach it as a program
//! (`scripts/gates/l7r-gate.sh browser ...`) and never compile it.
//!
//! [`cdp`] is the pipe, [`chromium`] which binary and its switches, [`page`] a context's pages as Playwright set them up, [`get`] the
//! context's plain request, [`url`] a URL as that request read it, [`serve`] and [`crop`] the two commands.

pub mod base64;
pub mod cdp;
pub mod chromium;
pub mod crop;
pub mod get;
pub mod page;
pub mod serve;
pub mod url;

#[cfg(test)]
pub(crate) mod testkit;

use std::path::Path;

/// What a command prints and its exit status.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Reply {
    pub stdout: String,
    pub stderr: String,
    pub code: i32,
}

fn refuse(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

const USAGE: &str = "usage: l7r-browser serve [--user-agent UA] [--ignore-https-errors] [--size WxH] | crop <page> <key> <out>\n";

/// `serve`'s options: the context's user agent, whether it ignores certificate errors, and its viewport (Playwright's default 1280 x
/// 720).
fn serve_options(args: &[String]) -> Result<page::Options, String> {
    let mut options = page::Options {
        width: 1280,
        height: 720,
        user_agent: None,
        ignore_https_errors: false,
    };
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--user-agent" => options.user_agent = it.next().cloned(),
            "--ignore-https-errors" => options.ignore_https_errors = true,
            "--size" => {
                let size = it.next().cloned().unwrap_or_default();
                let (w, h) = size.split_once('x').unwrap_or_default();
                options.width = w
                    .parse()
                    .map_err(|_| format!("l7r-browser: bad --size {size:?}\n"))?;
                options.height = h
                    .parse()
                    .map_err(|_| format!("l7r-browser: bad --size {size:?}\n"))?;
            }
            other => return Err(format!("l7r-browser: unknown option {other:?}\n{USAGE}")),
        }
    }
    Ok(options)
}

/// The command line, `serve` reading `input` and answering on `output` (the process's stdin and stdout).
#[must_use]
pub fn cli(
    args: &[String],
    var: &dyn Fn(&str) -> String,
    input: &mut dyn std::io::BufRead,
    output: &mut dyn std::io::Write,
) -> Reply {
    match args.first().map(String::as_str) {
        Some("serve") => {
            let options = match serve_options(&args[1..]) {
                Ok(o) => o,
                Err(e) => return refuse(e, 2),
            };
            let mut b = match page::Browser::open(var, options) {
                Ok(b) => b,
                Err(e) => return refuse(format!("l7r-browser: {e}\n"), 1),
            };
            let ua = match b.options.user_agent.clone() {
                Some(ua) => ua,
                None => b
                    .launched
                    .cdp
                    .call("Browser.getVersion", serde_json::json!({}), None)
                    .ok()
                    .and_then(|v| v.get("userAgent")?.as_str().map(str::to_owned))
                    .unwrap_or_default(),
            };
            serve::serve(&mut b, &ua, input, output);
            Reply::default()
        }
        Some("crop") if args.len() == 4 => {
            let crop = page::Browser::open(var, crop::options()).and_then(|mut b| {
                crop::crop(&mut b, Path::new(&args[1]), &args[2], Path::new(&args[3]))
            });
            match crop {
                Ok(()) => Reply::default(),
                Err(e) => refuse(format!("l7r-browser crop: {e}\n"), 1),
            }
        }
        _ => refuse(USAGE.to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
