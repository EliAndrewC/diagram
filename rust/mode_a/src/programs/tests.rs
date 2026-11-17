//! `make building-programs`'s port: the table, the blocks, the command line and the command (feature 449 T168).
//!
//! Research:
//!     the programs tool's tests - NONE: fixtures and assertions, deciding nothing about a building

use std::os::unix::fs::PermissionsExt as _;
use std::path::Path;

use serde_json::json;

use super::{apply, band_text, main, parse, render, Ask, PROGRAMS};
use crate::types::tests::kinds_tree;
use crate::types::{parse_types, Band, Kinds, DECLARATION};

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn a_band_is_written_as_the_python_wrote_it() {
    assert_eq!(band_text(&Band::default()), "presence");
    let b = Band {
        w: Some((6.0, 16.5)),
        h: Some((6.0, 1e7)),
        area: Some((0.5, 100.0)),
    };
    assert_eq!(band_text(&b), "6-16.5 by 6-1e+07 ft; 0.5-100 sq ft");
    // a w without an h writes no size, only the area
    assert_eq!(
        band_text(&Band {
            w: Some((1.0, 2.0)),
            ..Band::default()
        }),
        ""
    );
}

fn declaration() -> serde_json::Value {
    json!([
        {"tier": "shrine", "title": "S", "program": "p", "hand_drawn": false, "checks": [], "notes": "After the table.",
         "required": [
            {"id": "well", "kind": "well", "band_ft": {"w": [4, 8], "h": [4, 8]}, "site": "sacred_spring", "optional": true,
             "forms": {"pond": null, "basin": {"area": [10, 20]}}},
            {"id": "hall", "label": "^hall$", "band_ft": {}, "class": "guess", "why": "a reason"}]},
        {"tier": "manor", "title": "M", "program": "p", "hand_drawn": true, "checks": [],
         "required": [{"id": "gate", "kind": "main gate", "band_ft": {"area": [1, 2]}}]}
    ])
}

const HEAD: &str = "| item | found by the tag or label (or declared by id) | band (feet; either orientation) | class | why |\n|---|---|---|---|---|";

#[test]
fn a_type_renders_its_table_and_its_notes() {
    let dir = kinds_tree("mode-a-render");
    let types = parse_types(&declaration()).unwrap();
    let table = render(&types[0], &mut Kinds::new(dir.path())).unwrap();
    assert_eq!(
        table,
        format!(
            "{HEAD}\n| `well` | `data-kind=\"well\"` | 4-8 by 4-8 ft (under `pond`: absent; under `basin`: 10-20 sq ft) - optional, a knob - a site item: drawn where the sheet's declared map shows a sacred spring inside the frame | per statement | its depth its curb |\n| `hall` | `/^hall$/` | presence | guess | a reason |\n\nAfter the table."
        )
    );
    let table = render(&types[1], &mut Kinds::new(dir.path())).unwrap();
    assert!(table.ends_with(
        "| `gate` | `data-kind=\"main gate\"` | 1-2 sq ft | per statement | nothing guessed |"
    ));
}

#[test]
fn the_blocks_are_rewritten_last_first_and_a_missing_one_is_named() {
    let dir = kinds_tree("mode-a-apply");
    let types = parse_types(&declaration()).unwrap();
    let page = "a\n<!-- types.json:manor -->\nold\n<!-- /types.json:manor -->\nb\n<!-- types.json:shrine -->\nx\n<!-- /types.json:shrine -->\n";
    let (out, missing) = apply(page, &types, &mut Kinds::new(dir.path())).unwrap();
    assert!(missing.is_empty());
    let manor = render(&types[1], &mut Kinds::new(dir.path())).unwrap();
    let shrine = render(&types[0], &mut Kinds::new(dir.path())).unwrap();
    assert_eq!(
        out,
        format!("a\n<!-- types.json:manor -->\n{manor}\n<!-- /types.json:manor -->\nb\n<!-- types.json:shrine -->\n{shrine}\n<!-- /types.json:shrine -->\n")
    );
    // a tier marked twice: its last block is the one rewritten; a mismatched close is no block
    let twice = "<!-- types.json:manor -->\n1\n<!-- /types.json:manor -->\n<!-- types.json:manor -->\n2\n<!-- /types.json:manor -->\n<!-- types.json:shrine -->\n3\n<!-- /types.json:manor -->";
    let (out, missing) = apply(twice, &types, &mut Kinds::new(dir.path())).unwrap();
    assert_eq!(missing, ["shrine"]);
    assert!(out.starts_with("<!-- types.json:manor -->\n1\n") && out.contains(&manor));
    // a kind the registry does not know refuses the run
    let mut bad = declaration();
    bad[1]["required"][0]["kind"] = json!("t168-none");
    assert!(apply(
        page,
        &parse_types(&bad).unwrap(),
        &mut Kinds::new(dir.path())
    )
    .is_err());
}

#[test]
fn the_command_line_is_read_as_argparse_read_it() {
    let run = |check: bool, path: Option<&str>| Ask::Run {
        check,
        path: path.map(str::to_owned),
    };
    let refused = |s: &str| Ask::Refused(s.to_owned());
    assert_eq!(parse(&args(&[])), run(false, None));
    assert_eq!(parse(&args(&["--check", "--check"])), run(true, None));
    assert_eq!(parse(&args(&["--chec", "--pa", "x"])), run(true, Some("x")));
    assert_eq!(
        parse(&args(&["--path=a=b", "--path", "-1"])),
        run(false, Some("-1"))
    );
    assert_eq!(parse(&args(&["--path", "-x y"])), run(false, Some("-x y")));
    assert_eq!(parse(&args(&["--path="])), run(false, Some("")));
    assert_eq!(parse(&args(&["--x", "-h"])), Ask::Help);
    assert_eq!(parse(&args(&["--he"])), Ask::Help);
    assert_eq!(parse(&args(&["-hx", "--path"])), Ask::Help);
    assert_eq!(
        parse(&args(&["--help=1"])),
        refused("argument -h/--help: ignored explicit argument '1'")
    );
    assert_eq!(
        parse(&args(&["--check="])),
        refused("argument --check: ignored explicit argument ''")
    );
    assert_eq!(
        parse(&args(&["--path"])),
        refused("argument --path: expected one argument")
    );
    assert_eq!(
        parse(&args(&["--path", "--check"])),
        refused("argument --path: expected one argument")
    );
    assert_eq!(
        parse(&args(&["--path", "--"])),
        refused("argument --path: expected one argument")
    );
    assert_eq!(
        parse(&args(&[
            "--x", "--y", "foo", "-c", "-", "-1", "-.5", "-1.", "-a b"
        ])),
        refused("unrecognized arguments: --x --y foo -c - -1 -.5 -1. -a b")
    );
    assert_eq!(
        parse(&args(&["--", "--check"])),
        refused("unrecognized arguments: -- --check")
    );
}

#[test]
fn the_command_writes_checks_and_refuses_as_the_python_did() {
    let dir = kinds_tree("mode-a-main");
    let tree = dir.path();
    std::fs::create_dir_all(tree.join("l7r/diagram/buildings")).unwrap();
    std::fs::create_dir_all(tree.join("docs")).unwrap();
    std::fs::write(tree.join(DECLARATION), declaration().to_string()).unwrap();
    let page = tree.join(PROGRAMS);
    let shown = super::relpath(&page.to_string_lossy(), "");
    let stale = "<!-- types.json:manor -->\nold\n<!-- /types.json:manor -->\n<!-- types.json:shrine -->\nx\n<!-- /types.json:shrine -->\n";
    std::fs::write(&page, stale).unwrap();
    let r = main(&args(&["--check"]), tree);
    assert_eq!(
        (r.code, r.stderr),
        (
            1,
            format!("building-programs: {shown} is STALE - run `make building-programs`\n")
        )
    );
    let r = main(&args(&[]), tree);
    assert_eq!(
        (r.code, r.stdout),
        (0, format!("building-programs: wrote {shown}\n"))
    );
    let r = main(&args(&["--check"]), tree);
    assert_eq!(
        (r.code, r.stdout),
        (0, format!("building-programs: {shown} is current\n"))
    );
    // a page with no block for a declared tier, named by the path as given
    let other = tree.join("other.md");
    std::fs::write(&other, "nothing\n").unwrap();
    let given = other.to_string_lossy().into_owned();
    let r = main(&args(&["--path", &given]), tree);
    assert_eq!((r.code, r.stderr), (1, format!("building-programs: no `<!-- types.json:<tier> -->` block in {given} for: shrine, manor\n")));
    // what the Python did not catch: its traceback's last line
    let r = main(&args(&["--path", "/nonexistent/t168.md"]), tree);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            1,
            "FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/t168.md'\n"
        )
    );
    let r = main(&args(&["--path", &given]), Path::new("/nonexistent/t168"));
    assert_eq!(
        (r.code, r.stderr.starts_with("FileNotFoundError: ")),
        (1, true)
    );
    // a page it cannot write
    let unwritable = tree.join("docs/dir.md");
    std::fs::create_dir_all(unwritable.join("x")).unwrap();
    let r = main(&args(&["--path", &unwritable.to_string_lossy()]), tree);
    assert_eq!(
        (
            r.code,
            r.stderr.starts_with("IsADirectoryError: [Errno 21]")
        ),
        (1, true)
    );
    // a stale page it may read and not write: Python's `open(path, "w")` refusal
    std::fs::write(&page, stale).unwrap();
    std::fs::set_permissions(&page, std::fs::Permissions::from_mode(0o444)).unwrap();
    let r = main(&args(&[]), tree);
    std::fs::set_permissions(&page, std::fs::Permissions::from_mode(0o644)).unwrap();
    assert_eq!(
        (r.code, r.stderr.starts_with("PermissionError: [Errno 13]")),
        (1, true)
    );
    // the help and a refusal
    let r = main(&args(&["-h"]), tree);
    assert!(r.code == 0 && r.stdout.starts_with("usage: ") && r.stdout.contains("\noptions:\n"));
    let r = main(&args(&["--x"]), tree);
    assert_eq!(
        (
            r.code,
            r.stderr
                .ends_with("l7r-mode-a building-programs: error: unrecognized arguments: --x\n")
        ),
        (2, true)
    );
}
