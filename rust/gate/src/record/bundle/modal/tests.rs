//! Modal bundles and the prepass on the testkit's record: each check's parts, the order, the triage, the batch.

use std::path::Path;

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{args, scratch, state};
use crate::record::testkit::{edit_everything, put, WELL};

fn ask<'a>(for_: &'a str, out: &'a str, reason: &'a str, order_ok: &'a str) -> Ask<'a> {
    Ask {
        for_,
        out,
        reason,
        order_ok,
    }
}

fn run_on(root: &Path) -> Run {
    Run::new(root)
}

#[test]
fn the_text_helpers() {
    assert_eq!(visible("<!-- c --><p>a &amp; <b>b</b></p>\n x"), "a & b x");
    assert_eq!(heading("<h2 id=\"x\">The <i>head</i></h2>"), "The head");
    assert_eq!(heading("none"), "");
    assert_eq!(
        subjects("<!-- tags: setting=x; subject=a, b ,; level=y -->"),
        vec!["a", "b"]
    );
    assert!(subjects("<!-- tags: setting=x -->").is_empty() && subjects("").is_empty());
    assert_eq!(
        conditions_shown("- [winter_crop=wheat|barley][role=x] grows\n[a=b]"),
        "- (only where winter_crop is wheat or barley and role is x) grows\n(only where a is b) "
    );
    assert_eq!(around("0123456789", 4, 5, 2), "23456");
    assert_eq!(band("particular"), (80, 400));
    assert_eq!(guide("particular"), PARTICULAR);
}

#[test]
fn the_prepass() {
    let root = scratch("modal-prepass");
    let r = root.to_string_lossy().into_owned();
    let p = cli(&args(&["hamlet/well", "--prepass", "--root", &r]));
    assert!(
        p.stdout.starts_with("prepass - ") && p.stdout.contains("<- OUTSIDE THE BAND"),
        "{}",
        p.stdout
    );
    assert_eq!(cli(&args(&["Nope", "--prepass", "--root", &r])).code, 2);
    assert_eq!(cli(&args(&[])).code, 2);
    assert_eq!(cli(&args(&["x", "--for", "bogus"])).code, 2);
    assert_eq!(cli(&args(&["x", "--bogus"])).code, 2);
    put(&root, WELL, &format!("Name: Well\nForm: particular\nAbout: {} this project. The record says so.\nGuesses: - One. Two. Three. Four.\nEntry: research/questions/0777-none.html\n", "word ".repeat(90)));
    let p = cli(&args(&["hamlet/well", "--prepass", "--root", &r]));
    assert!(
        p.stdout
            .contains("barred phrase in About (M11/M16): 'this project'")
            && p.stdout.contains("a guess past two sentences")
            && p.stdout
                .contains("Entry names no file: research/questions/0777-none.html"),
        "{}",
        p.stdout
    );
    put(
        &root,
        WELL,
        &format!("Name: Well\nAbout: {}\n", "word ".repeat(130)),
    );
    let p = cli(&args(&["hamlet/well", "--prepass", "--root", &r]));
    assert!(
        p.stdout.contains("- Entry names no question file"),
        "{}",
        p.stdout
    );
    put(&root, "l7r/diagram/interactive/classes/bad.py", "class (\n");
    assert_eq!(
        cli(&args(&["hamlet/well", "--prepass", "--root", &r])).code,
        1
    );
    assert_eq!(cli(&args(&["hamlet/well", "--root", &r])).code, 1);
}

#[test]
fn each_checks_bundle() {
    let root = scratch("modal-bundle");
    put(
        &root,
        "research/assets/glossary-variants.txt",
        "wells\twell\nother\tthing\n",
    );
    put(&root, "research/questions/0096-wells.html", "<h2 id=\"w\">Wells <b>below</b></h2>\n<!-- tags: subject=water -->\n<p>Every well and the wells.</p>\n");
    put(
        &root,
        "research/questions/0094-trade.html",
        "<h2 id=\"t\">Trade</h2>\n<!-- tags: subject=water -->\n<p>x</p>\n",
    );
    put(
        &root,
        "research/questions/0097-dry.html",
        "<h2>Dry</h2>\n<p>nothing</p>\n",
    );
    let o = root.join("out").to_string_lossy().into_owned();
    let mut run = run_on(&root);
    assert_eq!(
        bundle(
            &mut run,
            &root,
            "hamlet/well",
            &ask("modal-research", &format!("{o}/r"), "a backfill asked", "")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    let cands = std::fs::read_to_string(root.join("out/r/candidates.md")).unwrap();
    assert!(cands.contains("1. `research/questions/0096-wells.html` - Wells below  [tags water; term hits 3; score 14]"), "{cands}");
    assert!(
        root.join("out/r/cand/0096-wells.html").is_file()
            && root.join("out/r/record/0097-dry.html").is_file()
            && root.join("out/r/entry/0094-trade.html").is_file()
    );
    let text = std::fs::read_to_string(root.join("out/r/MANIFEST.md")).unwrap();
    assert!(
        text.contains("Beside it, NOT inlined")
            && text.contains("owed-checks: modal-research\nunit: modal-accuracy:hamlet/well ")
            && text.contains("page: research/questions/0094-trade.html "),
        "{text}"
    );
    let mut run = run_on(&root);
    assert_eq!(
        bundle(
            &mut run,
            &root,
            "sheet/well",
            &ask("modal-research", &format!("{o}/s"), "a backfill asked", "")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    let reply = root.join("held.md");
    put(&root, "held.md", "EDIT l7r/diagram/interactive/assets/modals/hamlet/well.md\n<<<\nold\n===\nA well in the yard.\n>>>\nEDIT x\n<<<\nold\n===\n  \n>>>\n");
    state(
        &root,
        &json!({"dispatches": {"a": {"check": "modal-research", "subjects": ["modal:hamlet/well"], "t": 1, "reply": reply.to_string_lossy()}, "b": {"check": "modal-research", "subjects": ["modal:hamlet/well"], "t": 2, "aid": "none-such"}, "c": {"check": "modal-form", "subjects": ["modal:hamlet/well"], "t": 3}}}),
    );
    let mut run = run_on(&root);
    assert_eq!(
        bundle(
            &mut run,
            &root,
            "hamlet/well",
            &ask("modal-form", &format!("{o}/f"), "", "")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    assert_eq!(
        std::fs::read_to_string(root.join("out/f/research-held.md")).unwrap(),
        "# Wording the research rounds fixed - keep it\n\n- 'A well in the yard.'\n"
    );
    assert!(research_held(&root, "sheet/well", "x").is_empty());
    let mut run = run_on(&root);
    assert_eq!(
        bundle(&mut run, &root, "Nope", &ask("modal-form", &o, "", "")).unwrap(),
        2
    );
    put(&root, "busy/x", "x");
    let busy = root.join("busy").to_string_lossy().into_owned();
    assert_eq!(
        bundle(
            &mut run_on(&root),
            &root,
            "hamlet/well",
            &ask("modal-form", &busy, "", "")
        )
        .unwrap(),
        2
    );
    let mut run = run_on(&root);
    assert_eq!(
        bundles(
            &mut run,
            &root,
            &["hamlet/well", "sheet/well"],
            &ask("modal-form", &format!("{o}/b"), "", "")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    let top = std::fs::read_to_string(root.join("out/b/MANIFEST.md")).unwrap();
    assert!(
        top.starts_with("# 2 pop-ups for modal-form, one agent")
            && top.contains("unit: modal-form:sheet/well "),
        "{top}"
    );
    assert_eq!(
        bundles(
            &mut run_on(&root),
            &root,
            &["hamlet/well", "Nope"],
            &ask("modal-form", &format!("{o}/b"), "", "")
        )
        .unwrap(),
        2
    );
    let r = root.to_string_lossy().into_owned();
    let both = cli(&args(&[
        "hamlet/well sheet/well",
        "--root",
        &r,
        "--out",
        &format!("{o}/c"),
    ]));
    assert_eq!(both.code, 0, "{}", both.stderr);
    std::fs::write(root.join("research/questions/0097-dry.html"), [0xff]).unwrap();
    assert!(bundle(
        &mut run_on(&root),
        &root,
        "hamlet/well",
        &ask("modal-research", &format!("{o}/r"), "", "")
    )
    .is_err());
}

#[test]
fn the_order_and_the_triage_hold_a_bundle() {
    let root = scratch("modal-order");
    let o = root.join("out").to_string_lossy().into_owned();
    put(&root, WELL, "Name: Well\nAbout: A well in the yard, changed.\n\nIt is deep.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    let mut run = run_on(&root);
    assert_eq!(
        bundle(
            &mut run,
            &root,
            "hamlet/well",
            &ask("modal-research", &o, "", "")
        )
        .unwrap(),
        3
    );
    assert!(
        run.err
            .contains("modal-form:hamlet/well is owed and unanswered")
            && run.err.contains("CHECK_ORDER_OK=\"<why>\""),
        "{}",
        run.err
    );
    assert_eq!(
        bundle(
            &mut run_on(&root),
            &root,
            "hamlet/well",
            &ask("modal-research", &o, "", "x")
        )
        .unwrap(),
        3
    );
    let mut run = run_on(&root);
    assert_eq!(
        bundle(
            &mut run,
            &root,
            "hamlet/well",
            &ask("modal-research", &o, "", " an audit asked ")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    assert!(run
        .out
        .starts_with("modal-bundle: bundled out of order, because: an audit asked\n"));
    assert!(std::fs::read_to_string(root.join("out/MANIFEST.md"))
        .unwrap()
        .contains("check-order-escape: an audit asked\n"));
    let fresh = scratch("modal-triage-held");
    edit_everything(&fresh);
    let o = fresh.join("out").to_string_lossy().into_owned();
    let mut run = run_on(&fresh);
    let code = bundle(
        &mut run,
        &fresh,
        "hamlet/well",
        &ask("modal-depiction", &o, "x", "an audit asked"),
    )
    .unwrap();
    assert_eq!(code, 3, "{} {}", run.out, run.err);
    assert!(
        run.err
            .contains("A check the GM asked for, or a backfill: REASON=\"<why>\""),
        "{}",
        run.err
    );
    let mut run = run_on(&fresh);
    assert_eq!(
        bundle(
            &mut run,
            &fresh,
            "hamlet/well",
            &ask("modal-depiction", &o, "a backfill asked", "an audit asked")
        )
        .unwrap(),
        0,
        "{}",
        run.err
    );
    assert!(run
        .out
        .starts_with("modal-bundle: bundled without its triage, because: a backfill asked\n"));
}
