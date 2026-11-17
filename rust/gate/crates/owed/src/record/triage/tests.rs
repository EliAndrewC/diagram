//! The pop-up triage on a scratch record.

use serde_json::{json, Value};

use super::{bundle, cli, default_out, pending, record, refusal, touched, triage_only};
use crate::record::modals;
use crate::record::owed::{merge_base, store, write_answer};
use crate::record::testkit::{put, record as fixture, DRAWING, PAGE};

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn moved_pages(root: &std::path::Path) {
    put(
        root,
        DRAWING,
        "<h2>How drawn</h2>\n<p>Drawn as a thicker line.</p>\n<p>A new block.</p>\n",
    );
    put(root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> Changed.</p>\n");
}

/// A record with nothing moved owes no pop-up a triage, and no bundle is written. Split from the test below (feature 449 T164: the one
/// test took 121 ms, over FR-008's tenth of a second).
#[test]
fn a_record_with_nothing_moved_owes_no_triage() {
    let root = fixture("triage-none");
    let out = root.join("tri");
    assert!(bundle(&root, &out, "").unwrap().is_none());
    assert!(!out.exists());
}

#[test]
fn a_triage_bundles_the_moved_pages_and_records_a_reply() {
    let root = fixture("triage-flow");
    let out = root.join("tri");
    moved_pages(&root);
    let s = store(&root);
    let base = merge_base(&root);
    let waiting = pending(&root, &base, &s, None).unwrap();
    assert!(waiting.iter().all(|w| triage_only(&w.1)) && !waiting.is_empty());
    write_answer(&s, "modal-accuracy:hamlet/well", "x", "r", Some(&json!({PAGE: crate::record::repo::git(&root, &["rev-parse", &format!("HEAD:{PAGE}")]).trim()}))).unwrap();
    std::fs::create_dir_all(&out).unwrap();
    std::fs::write(out.join("stale.txt"), "x").unwrap();
    let (manifest, n) = bundle(&root, &out, "").unwrap().unwrap();
    let text = std::fs::read_to_string(&manifest).unwrap();
    assert!(
        n >= 3
            && text.contains("> A new block.")
            && text.contains("Removed blocks")
            && text.contains("UID `choice/bamboo--both`")
    );
    assert!(
        text.contains("against the version these pop-ups' last check read")
            && text.contains("| Depiction - Drawn round.")
    );
    assert!(!out.join("stale.txt").exists());
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("triage.json")).unwrap()).unwrap();
    let units = data["units"].as_object().unwrap().clone();
    let reply = "TOUCHES `hamlet/well` @ 0094-trade.drawing - its line\nTOUCHES choice/bamboo--both - no page\nTOUCHES hamlet/nope - stray\nTOUCHES choice/bamboo--both @ elsewhere.html - unknown page\n";
    let msgs = record(&s, &units, reply, data.get("pages"), data.get("blobs")).unwrap();
    assert!(msgs.iter().any(|m| m.starts_with("refused: `hamlet/nope`")));
    assert!(msgs
        .iter()
        .any(|m| m == "touched: modal-depiction:hamlet/well - its line"));
    assert!(msgs
        .iter()
        .any(|m| m.starts_with("touched: modal-depiction:choice/bamboo--both")));
    assert!(touched(&s)
        .unwrap()
        .contains_key("modal-depiction:hamlet/well"));
    assert!(
        crate::record::owed::read_answer(&s, "modal-accuracy:hamlet/well").contains_key("pages")
    );
    assert!(record(&s, &units, "", None, None).unwrap().is_empty());
    assert!(s.join("modal-triage-touched.json").is_file());
}

/// A pop-up whose pages moved and that no check has read owes only a triage, a broken record of what was touched is refused, and a
/// bundle goes under the default root. Split from the test above, on the same moved pages and an empty store (feature 449 T164: the
/// one test took 129 ms, over FR-008's tenth of a second).
#[test]
fn a_moved_pop_up_owes_only_a_triage_and_a_broken_touched_record_is_refused() {
    let root = fixture("triage-owes");
    moved_pages(&root);
    let s = store(&root);
    let now = modals::modals_now(&root, true).unwrap();
    let well = modals::find(&now, "hamlet/well").unwrap();
    // the store as the test above left it once it was removed: none
    let _ = std::fs::remove_dir_all(&s);
    assert!(refusal(&root, well, "modal-research", None)
        .unwrap()
        .contains("owe(s) only a TRIAGE"));
    assert!(refusal(&root, well, "modal-form", Some(&[]))
        .unwrap()
        .is_empty());
    std::fs::create_dir_all(&s).unwrap();
    std::fs::write(s.join("modal-triage-touched.json"), "{bad").unwrap();
    assert!(touched(&s).is_err());
    let under = l7r_gate_core::record::bundle::default_root().join("modal-triage-");
    assert!(default_out(&root)
        .to_string_lossy()
        .starts_with(&*under.to_string_lossy()));
}

#[test]
fn the_command_line() {
    let root = fixture("triage-cli");
    let r = root.to_string_lossy().into_owned();
    let out = root.join("o").to_string_lossy().into_owned();
    assert_eq!(
        cli(&args(&["--root", &r, "bundle", "--out", &out])).stdout,
        "modal-triage: no pop-up is owed a triage\n"
    );
    moved_pages(&root);
    let said = cli(&args(&["--root", &r, "bundle", "--out", &out]));
    assert!(said
        .stdout
        .contains("unit(s); dispatch the `modal-triage` agent"));
    put(&root, "reply.md", "TOUCHES hamlet/well - x\n");
    let rec = cli(&args(&[
        "--root",
        &r,
        "record",
        "--bundle",
        &out,
        "--reply",
        &root.join("reply.md").to_string_lossy(),
    ]));
    assert!(rec.stdout.contains("unit(s) sent on to their checks"));
    assert_eq!(
        cli(&args(&[
            "--root",
            &r,
            "record",
            "--bundle",
            "/nonexistent",
            "--reply",
            "x"
        ]))
        .code,
        1
    );
}

/// The command line's refusals: a bundle's data that is not its own, arguments it does not take, a root that is not there, and a
/// modal file that cannot be read. Split from the test above, on the same bundle (feature 449 T164: the one test took 111 ms, over
/// FR-008's tenth of a second).
#[test]
fn the_command_line_s_refusals() {
    let root = fixture("triage-cli-refusals");
    let r = root.to_string_lossy().into_owned();
    let out = root.join("o").to_string_lossy().into_owned();
    moved_pages(&root);
    assert_eq!(cli(&args(&["--root", &r, "bundle", "--out", &out])).code, 0);
    put(&root, "o/triage.json", "{}");
    assert_eq!(
        cli(&args(&[
            "--root", &r, "record", "--bundle", &out, "--reply", "x"
        ]))
        .code,
        1
    );
    put(&root, "o/triage.json", "not json");
    assert_eq!(
        cli(&args(&[
            "--root", &r, "record", "--bundle", &out, "--reply", "x"
        ]))
        .code,
        1
    );
    for bad in [
        &["frob"][..],
        &["--x", "bundle"],
        &["record", "--bundle", "x"],
        &["bundle", "--y"],
    ] {
        assert_eq!(cli(&args(bad)).code, 2);
    }
    assert_eq!(
        cli(&args(&[
            "--root=/nonexistent/at/all",
            "bundle",
            "--out",
            &out
        ]))
        .code,
        0
    );
    // a modal file that cannot be read fails the bundle (a class module that did not lex did, before feature 449 T149)
    std::fs::write(root.join(crate::record::testkit::WELL), b"About: \xff\n").unwrap();
    assert_eq!(cli(&args(&["--root", &r, "bundle", "--out", &out])).code, 1);
}

/// A page that is not there is kept as no blob, and a bundle with no `--out` owes nothing on a record with nothing moved. Split from the
/// test below (feature 449 T164: the one test took 94 ms, at FR-008's tenth of a second).
#[test]
fn a_missing_page_keeps_no_blob_and_a_bare_bundle_owes_nothing() {
    let root = fixture("triage-edges-none");
    assert_eq!(super::keep(&root, "nope.html"), "");
    let r = root.to_string_lossy().into_owned();
    assert_eq!(
        cli(&args(&["--root", &r, "bundle"])).stdout,
        "modal-triage: no pop-up is owed a triage\n"
    );
}

#[test]
fn the_edges_of_a_bundle() {
    let root = fixture("triage-edges");
    put(&root, crate::record::testkit::WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html, research/questions/0095-other.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    let head = crate::record::testkit::commit(&root, "two entry pages");
    crate::record::testkit::git(&root, &["update-ref", "refs/remotes/origin/main", &head]);
    moved_pages(&root);
    let s = store(&root);
    write_answer(
        &s,
        "modal-accuracy:hamlet/well",
        "x",
        "r",
        Some(&json!({PAGE: "0".repeat(40)})),
    )
    .unwrap();
    let (manifest, n) = bundle(&root, &root.join("t"), &head).unwrap().unwrap();
    assert!(
        n > 0
            && std::fs::read_to_string(manifest)
                .unwrap()
                .contains("## research/questions/0094-trade.html")
    );
}

#[test]
fn a_page_that_only_lost_a_block_names_none_new() {
    let root = fixture("triage-removed");
    put(&root, DRAWING, "<h2>How drawn</h2>\n");
    let out = root.join("tri");
    let (manifest, _) = bundle(&root, &out, "").unwrap().unwrap();
    let text = std::fs::read_to_string(manifest).unwrap();
    assert!(text.contains("New or changed blocks:\n\n(none)"), "{text}");
}
