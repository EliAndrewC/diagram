//! `l7r-mode-a sheet-page`: a sheet's page written and its census printed (feature 449 T150, the engine port's step 2), the command
//! `interactive/sheet.py`'s `write_sheet_page` runs for the six pool generators - so the generators stay as they were, their one call the
//! same, and the page's Python (`page.py`, `place.py`, `raster.py` and the rest) is gone.
//!
//! The reply is one JSON line on stdout: the census (`counts` as ordered pairs, `unclassed`, `unregistered`) and `reads`, every data file
//! the writer read ([`crate::reads`], for the generation cache); a refusal is `{"error": {"kind", "message"}}` with exit 1 and the
//! traceback's last line on stderr, which the wrapper raises as the exception the Python writer raised.
//!
//! Research: the page command - NONE: arguments in, the census and the reads out, deciding nothing about a building

use std::io::Read;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::Error;
use serde_json::json;

use crate::raster::Host;

/// The command's usage line.
pub const USAGE: &str =
    "usage: l7r-mode-a sheet-page <map.svg> [--with-raster | --no-raster] [--stdin]\n";

/// What the command was asked: the sheet's path, the raster switch (none: the render condition decides), whether the text is on stdin.
fn parse(args: &[String]) -> Option<(&str, Option<bool>, bool)> {
    let (mut path, mut raster, mut stdin) = (None, None, false);
    for a in args {
        match a.as_str() {
            "--with-raster" if raster.is_none() => raster = Some(true),
            "--no-raster" if raster.is_none() => raster = Some(false),
            "--stdin" if !stdin => stdin = true,
            flag if flag.starts_with("--") => return None,
            p if path.is_none() => path = Some(p),
            _ => return None,
        }
    }
    Some((path?, raster, stdin))
}

/// The page of the sheet the arguments name, with the text read from `input` when `--stdin` is given; the registry the sheets' own
/// (`compound_classes`, the modal files `interactive/compound_kinds` reads).
#[must_use]
pub fn main(args: &[String], tree: &Path, host: &Host, input: &mut dyn Read) -> Reply {
    run(
        args,
        tree,
        host,
        input,
        &l7r_gate_registry::about::compound_classes,
    )
}

/// The registry's reader, handed in: a test's tree holds no modal files.
type Registry = dyn Fn(&Path) -> Result<Vec<FeatureClass>, Error>;

fn run(
    args: &[String],
    tree: &Path,
    host: &Host,
    input: &mut dyn Read,
    registry: &Registry,
) -> Reply {
    let Some((path, raster, stdin)) = parse(args) else {
        return reply(String::new(), USAGE, 2);
    };
    let _ = crate::reads::take(); // this run's reads alone
    let written = (|| {
        let text = if stdin {
            let mut bytes = Vec::new();
            input
                .read_to_end(&mut bytes)
                .map_err(|e| Error::new("OSError", e.to_string()))?;
            Some(
                String::from_utf8(bytes)
                    .map_err(|e| Error::new("UnicodeDecodeError", format!("'utf-8' codec: {e}")))?,
            )
        } else {
            None
        };
        let registry = registry(tree)?;
        super::write_sheet_page(tree, host, path, &registry, raster, text.as_deref(), None)
    })();
    match written {
        Ok(census) => {
            let reads: Vec<String> = crate::reads::take()
                .iter()
                .map(|p| p.to_string_lossy().into_owned())
                .collect();
            let out = json!({
                "counts": census.counts, "unclassed": census.unclassed, "unregistered": census.unregistered, "reads": reads,
            });
            reply(format!("{out}\n"), "", 0)
        }
        Err(e) => {
            let out = json!({"error": {"kind": e.kind, "message": e.message}});
            reply(format!("{out}\n"), &crate::py::uncaught(&e), 1)
        }
    }
}

fn reply(stdout: String, stderr: &str, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: stderr.to_owned(),
        code,
    }
}

#[cfg(test)]
mod tests {
    use super::{main, parse, run};
    use crate::raster::Host;
    use l7r_gate_registry::about::FeatureClass;

    fn words(w: &[&str]) -> Vec<String> {
        w.iter().map(|s| (*s).to_owned()).collect()
    }

    #[test]
    fn the_arguments_are_one_sheet_and_its_switches() {
        assert_eq!(
            parse(&words(&["a.svg", "--no-raster", "--stdin"])),
            Some(("a.svg", Some(false), true))
        );
        assert_eq!(
            parse(&words(&["--with-raster", "a.svg"])),
            Some(("a.svg", Some(true), false))
        );
        for bad in [
            &["a.svg", "b.svg"][..],
            &[],
            &["a.svg", "--x"],
            &["a.svg", "--no-raster", "--with-raster"],
            &["a.svg", "--stdin", "--stdin"],
        ] {
            assert_eq!(parse(&words(bad)), None, "{bad:?}");
        }
    }

    /// A standard input that fails to read.
    struct Broken;

    impl std::io::Read for Broken {
        fn read(&mut self, _: &mut [u8]) -> std::io::Result<usize> {
            Err(std::io::Error::other("closed"))
        }
    }

    #[test]
    fn the_command_prints_the_census_and_its_reads_or_the_refusal() {
        // the read log this test's runs take, no other test's run draining it meanwhile (feature 449 T151)
        let _log = crate::reads::taker();
        // a tree of its own, its registry empty: the whole registry's modal files would take the test past FR-008's tenth of a second
        let dir = l7r_guard::shared::tempdir::TempDir::new("sheet-page-cli");
        let tree = dir.path();
        let assets = tree.join(crate::page::ASSETS);
        std::fs::create_dir_all(&assets).unwrap();
        for (name, text) in [
            ("page.css", "/* css */\n"),
            ("page.js", "// js\n"),
            ("page-text.json", "{\"plain_cursor\": []}"),
            ("glossary.json", "{}"),
            ("choices.json", "{\"choices\": []}"),
        ] {
            std::fs::write(assets.join(name), text).unwrap();
        }
        std::fs::write(tree.join("l7r/diagram/knobs.json"), "{\"knobs\": {}}").unwrap();
        let real = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        std::fs::copy(
            real.join(crate::page::ASSETS).join("place.json"),
            assets.join("place.json"),
        )
        .unwrap();
        let host = Host {
            vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
            ..Host::default()
        };
        let svg = tree.join("s.svg").to_string_lossy().into_owned();
        let well = |_: &std::path::Path| {
            Ok(vec![FeatureClass {
                key: "well".into(),
                name: "Well".into(),
                ..Default::default()
            }])
        };
        let run = |args: &[&str], input: &str| {
            run(&words(args), tree, &host, &mut input.as_bytes(), &well)
        };
        let r = run(
            &[&svg, "--stdin"],
            "<svg viewBox=\"0 0 9 9\"><rect data-kind=\"nope\"/><rect data-kind=\"well\"/><circle/></svg>",
        );
        let v: serde_json::Value = serde_json::from_str(&r.stdout).unwrap();
        assert_eq!(r.code, 0, "{}", r.stderr);
        assert_eq!(v["counts"], serde_json::json!([["nope", 1], ["well", 1]]));
        assert_eq!(v["unregistered"], serde_json::json!(["nope"]));
        assert_eq!(v["unclassed"].as_array().map(Vec::len), Some(1));
        let reads = v["reads"].as_array().unwrap();
        assert!(reads
            .iter()
            .any(|p| p.as_str().unwrap().ends_with("/page.css")));
        assert!(tree.join("s.html").is_file());
        let r = run(&[&svg], "");
        assert_eq!(
            (r.code, r.stderr.starts_with("FileNotFoundError: [Errno 2]")),
            (1, true)
        );
        assert!(r
            .stdout
            .starts_with("{\"error\":{\"kind\":\"FileNotFoundError\""));
        let r = run(&[&svg, "--stdin"], "<svg><g></svg>");
        assert_eq!((r.code, r.stderr.starts_with("ValueError: ")), (1, true));
        // a render the guard refuses leaves no page where there was none (FIXED, feature 449 T183: the Python's open-before-render
        // left it empty); a page with nowhere to go is refused before any render
        let big = tree.join("big.svg").to_string_lossy().into_owned();
        let wide = "<svg viewBox=\"0 0 900 900\" width=\"900\" height=\"900\"><rect data-kind=\"well\"/></svg>";
        let r = run(&[&big, "--with-raster", "--stdin"], wide);
        assert!(r.stderr.starts_with("RenderedInATest: "), "{}", r.stderr);
        assert!(!tree.join("big.html").exists());
        let nowhere = tree.join("no/dir/s.svg").to_string_lossy().into_owned();
        let r = run(&[&nowhere, "--with-raster", "--stdin"], wide);
        assert!(r.stderr.starts_with("FileNotFoundError: "), "{}", r.stderr);
        let r = super::run(
            &words(&[&svg, "--stdin"]),
            tree,
            &host,
            &mut &b"\xff"[..],
            &well,
        );
        assert_eq!(
            (r.code, r.stderr.starts_with("UnicodeDecodeError: ")),
            (1, true)
        );
        let r = super::run(&words(&[&svg, "--stdin"]), tree, &host, &mut Broken, &well);
        assert_eq!((r.code, r.stderr.starts_with("OSError: ")), (1, true));
        // the command's own registry, read from a tree with no modal files: the refusal, not the page
        let r = main(&words(&[&svg, "--stdin"]), tree, &host, &mut &b"<svg/>"[..]);
        assert_eq!(r.code, 1);
        assert_eq!(run(&[], "").code, 2);
    }
}
