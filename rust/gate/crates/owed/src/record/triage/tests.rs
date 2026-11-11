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

#[test]
fn a_triage_bundles_the_moved_pages_and_records_a_reply() {
    let root = fixture("triage-flow");
    let out = root.join("tri");
    assert!(bundle(&root, &out, "").unwrap().is_none());
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
    let now = modals::modals_now(&root, true).unwrap();
    let well = modals::find(&now, "hamlet/well").unwrap();
    std::fs::remove_file(s.join("modal-triage-touched.json")).unwrap();
    std::fs::remove_dir_all(&s).unwrap();
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
    put(
        &root,
        "l7r/diagram/interactive/classes/broken.py",
        "x = (\n",
    );
    assert_eq!(cli(&args(&["--root", &r, "bundle", "--out", &out])).code, 1);
}

#[test]
fn the_edges_of_a_bundle() {
    let root = fixture("triage-edges");
    assert_eq!(super::keep(&root, "nope.html"), "");
    let r = root.to_string_lossy().into_owned();
    assert_eq!(
        cli(&args(&["--root", &r, "bundle"])).stdout,
        "modal-triage: no pop-up is owed a triage\n"
    );
    put(&root, crate::record::testkit::WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html, research/questions/0095-other.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    crate::record::testkit::commit(&root, "two entry pages");
    let head = crate::record::testkit::git(&root, &["rev-parse", "HEAD"]);
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
