//! The pop-up triage on a scratch record.

use serde_json::{json, Value};

use super::{bundle, cli, default_out, pending, record, refusal, touched, triage_only};
use crate::record::modals;
use crate::record::owed::{merge_base, store, write_answer};
use crate::record::testkit::{put, record as fixture, DRAWING, PAGE, WELL};

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

/// The fixture with its pop-ups repeating the page's words, committed as the base, so an edit of those words owes them a triage under
/// the echo rule (feature 451 T186).
fn echoing(tag: &str) -> l7r_gate_core::checks::TempDir {
    let root = fixture(tag);
    put(&root, WELL, "Name: Well\nAbout: A well in the yard, a short way apart.\n\nIt is deep, as an unmarked claim of the page says.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round, drawn as a line.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, "l7r/diagram/interactive/assets/modals/choice/bamboo--both.md", "Name: Bamboo\nAbout: Both kinds, drawn as a line.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>An unmarked claim of the page stands here.</p>\n");
    let base = crate::record::testkit::commit(&root, "echoing");
    put(&root, ".git/refs/remotes/origin/main", &format!("{base}\n"));
    root
}

fn moved_pages(root: &std::path::Path) {
    put(
        root,
        DRAWING,
        "<h2>How drawn</h2>\n<p>Drawn as a thicker line.</p>\n<p>A new block.</p>\n",
    );
    put(root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart, they say.<sup class=\"fn\" data-note=\"k\"></sup> Changed.</p>\n");
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
    let root = echoing("triage-flow");
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
            && text.contains("NEW: A new block.")
            && text.contains("WORD DIFF: Drawn as a {+thicker+} line. [-[^d]-]")
            && text.contains("Removed (no longer on the page):\n  OLD: An unmarked claim of the page stands here.")
            && text.contains("UID `choice/bamboo--both`")
    );
    assert!(
        text.contains("against the version these pop-ups' last check read")
            && text.contains("# The pop-ups, whole")
            && text.contains(
                "Depiction: Drawn round, drawn as a line.\nDrawing: research/questions/0094-trade.drawing.html"
            )
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
    let root = echoing("triage-cli");
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
        .contains("unit(s) left; dispatch the `modal-triage` agent"));
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
    let root = echoing("triage-edges");
    put(&root, crate::record::testkit::WELL, "Name: Well\nAbout: A well in the yard, a short way apart.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html, research/questions/0095-other.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
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
    let root = echoing("triage-removed");
    put(&root, DRAWING, "<h2>How drawn</h2>\n");
    let out = root.join("tri");
    let (manifest, _) = bundle(&root, &out, "").unwrap().unwrap();
    let text = std::fs::read_to_string(manifest).unwrap();
    assert!(
        text.contains("Removed (no longer on the page):\n  OLD: Drawn as a line. [^d]")
            && !text.contains("NEW:")
    );
}

const SPLIT_TO: &str = "research/questions/0331-where.html";

fn units_of(root: &std::path::Path, uid: &str) -> Vec<String> {
    let s = store(root);
    pending(root, &merge_base(root), &s, None)
        .unwrap()
        .into_iter()
        .map(|u| u.0)
        .filter(|slug| slug.ends_with(&format!(":{uid}")))
        .collect()
}

/// Feature 451 T186, red first: a page edit of only a footnote marker, a link and a comment re-owed the pop-up's checks and sent it to
/// the agent; the tool now clears it, answering its units with no agent and writing no bundle.
#[test]
fn a_marker_link_or_comment_edit_is_cleared_by_the_tool() {
    let root = fixture("triage-tool-clear");
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"z\"></sup> More <a href=\"https://e.org\">here</a>.<!-- Evidence: guess --></p>\n<p>An unmarked claim.</p>\n");
    assert!(!units_of(&root, "hamlet/well").is_empty());
    let s = store(&root);
    let (got, cleared) = super::bundle_in(&root, &root.join("tri"), "", &s).unwrap();
    assert!(got.is_none() && cleared > 0);
    assert!(units_of(&root, "hamlet/well").is_empty());
    let answer = crate::record::owed::read_answer(&s, "modal-accuracy:hamlet/well");
    assert!(answer.get("pages").is_some_and(|p| p.get(PAGE).is_some()));
    let r = root.to_string_lossy().into_owned();
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>An unmarked claim.<sup class=\"fn\" data-note=\"z\"></sup></p>\n");
    let said = cli(&args(&[
        "--root",
        &r,
        "bundle",
        "--out",
        &root.join("o").to_string_lossy(),
    ]));
    assert!(said
        .stdout
        .contains("cleared by the tool (no claim-bearing change); no agent is owed"));
    put(
        &root,
        "edits.json",
        "[{\"id\": \"E1\", \"file\": \"a.notes.html\"}]",
    );
    let edits = root.join("edits.json").to_string_lossy().into_owned();
    let replayed = cli(&args(&["--root", &r, "replay", "--edits", &edits]));
    assert!(replayed.stdout.starts_with("E1\tcleared\t"));
    let none = root.join("none.json").to_string_lossy().into_owned();
    assert_eq!(
        cli(&args(&["--root", &r, "replay", "--edits", &none])).code,
        1
    );
}

/// Feature 451 T185, red first: a split - a block moved verbatim to a new page, the source pointing to it - re-owed every pop-up
/// citing the source; now it re-owes nothing, and the moved block is read where it lives, so a later edit of it there re-owes the
/// pop-up with the change paired.
#[test]
fn a_split_with_its_pointer_re_owes_nothing_and_an_edit_of_the_moved_block_re_owes() {
    let root = echoing("triage-split");
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>Its account is now at <a class=\"moved\" href=\"0331-where.html\">Where</a>.</p>\n");
    put(
        &root,
        SPLIT_TO,
        "<h2 id=\"w\">Where</h2>\n<p>An unmarked claim of the page stands here.</p>\n",
    );
    let owed_now = units_of(&root, "hamlet/well");
    assert!(owed_now.iter().any(|s| s.starts_with("modal-accuracy:")));
    let s = store(&root);
    let (got, cleared) = super::bundle_in(&root, &root.join("tri"), "", &s).unwrap();
    assert!(got.is_none() && cleared >= owed_now.len(), "{got:?}");
    assert!(units_of(&root, "hamlet/well").is_empty());
    let answer = crate::record::owed::read_answer(&s, "modal-accuracy:hamlet/well");
    assert!(answer
        .get("pages")
        .is_some_and(|p| p.get(SPLIT_TO).is_some()));
    put(
        &root,
        SPLIT_TO,
        "<h2 id=\"w\">Where</h2>\n<p>A marked claim of the page stands here.</p>\n",
    );
    assert!(!units_of(&root, "hamlet/well").is_empty());
    let (got, _) = super::bundle_in(&root, &root.join("tri"), "", &s).unwrap();
    let text = std::fs::read_to_string(got.unwrap().0).unwrap();
    assert!(
        text.contains(&format!("## {SPLIT_TO}"))
            && text
                .contains("WORD DIFF: [-An unmarked-] {+A marked+} claim of the page stands here.")
    );
}

/// A block moved with no pointer is a removal, and the session is told the pointer's form; a marker gone whose key the pop-up's
/// Sources names is sent to the agent (rule C), not cleared.
#[test]
fn a_move_with_no_pointer_and_a_cited_key_gone_go_to_the_agent() {
    let root = fixture("triage-unpointed");
    let other = format!("research/questions/{}-elsewhere.html", "0400");
    put(
        &root,
        &other,
        "<h2 id=\"e\">Elsewhere</h2>\n<p>An unmarked claim.</p>\n",
    );
    put(&root, WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nSources: k\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart. More here.</p>\n");
    let s = store(&root);
    let (got, _) = super::bundle_in(&root, &root.join("tri"), "", &s).unwrap();
    let text = std::fs::read_to_string(got.unwrap().0).unwrap();
    assert!(
        text.contains("Note keys no longer on the page or a page it points to: k")
            && text.contains("OLD: An unmarked claim.")
            && text.contains(&format!("{PAGE} -> {other}"))
            && text.contains("<a class=\"moved\" href=\"NNNN-<slug>.html\">")
    );
}

/// Feature 451 T186's replay over a landing: the whole filter, a pop-up read at the landing's parent.
#[test]
fn a_landing_replays_through_the_filter() {
    let root = echoing("triage-replay");
    moved_pages(&root);
    let landing = crate::record::testkit::commit(&root, "a landing");
    let r = root.to_string_lossy().into_owned();
    let out = cli(&args(&["--root", &r, "replay", "--landing", &landing])).stdout;
    assert!(out.contains(
        "hamlet/well\tfires\tresearch/questions/0094-trade.html\tit repeats words changed in"
    ));
    assert!(out.contains("choice/bamboo--both\tfires\t"));
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart, they say.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"z\"></sup> Changed.</p>\n<p>Something else entirely, new here.</p>\n");
    let quiet = crate::record::testkit::commit(&root, "a marker and a block no pop-up repeats");
    let out = cli(&args(&["--root", &r, "replay", "--landing", &quiet])).stdout;
    assert!(out.contains("hamlet/well\tcleared\tresearch/questions/0094-trade.html\t\n"));
    assert!(matches!(
        super::replay_landing(&root, "no-such-rev"),
        Ok(_) | Err(_)
    ));
}

/// T184's shape (feature 451 T194): a page split to a new one with its pointer - a marked block moved verbatim, a block moved with a
/// small edit, a block moved with a gloss inserted. `hamlet/well` cites the moved key and repeats only unchanged words; `bamboo--both`
/// repeats the glossed sentence's neighbors.
fn split_like_t184(tag: &str) -> l7r_gate_core::checks::TempDir {
    let root = fixture(tag);
    put(&root, WELL, "Name: Well\nAbout: A well in the yard. It is lined with cedar planks.\nGuesses: - a guess\nSources: k2\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, "l7r/diagram/interactive/assets/modals/choice/bamboo--both.md", "Name: Bamboo\nAbout: The first wells were dug here.\nEntry: research/questions/0094-trade.html\n");
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>The well was dug of stone by the elders.<sup class=\"fn\" data-note=\"k2\"></sup></p>\n<p>The yard well was lined with cedar planks long ago.</p>\n<p>The first wells were dug of whatever stone lay near.</p>\n");
    let base = crate::record::testkit::commit(&root, "before the split");
    put(&root, ".git/refs/remotes/origin/main", &format!("{base}\n"));
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>Its account is now at <a class=\"moved\" href=\"0331-where.html\">Where</a>.</p>\n");
    put(&root, SPLIT_TO, "<h2 id=\"w\">Where</h2>\n<p>The well was dug of stone by the elders.<sup class=\"fn\" data-note=\"k2\"></sup></p>\n<p>The yard well was lined with cedar planks in old times.</p>\n<p>The first wells (ido) were dug of whatever stone lay near.</p>\n");
    root
}

/// Feature 451 T194, red first: T184's split re-owed every pop-up reading the source - its cited key read as gone though it moved with
/// its block, and a block moved with an edit compared with an unrelated sentence - and the MANIFEST showed the moved blocks as removed.
#[test]
fn a_split_like_t184_s_owes_only_the_pop_up_repeating_changed_words() {
    let root = split_like_t184("triage-t184");
    let s = store(&root);
    let (got, _) = super::bundle_in(&root, &root.join("tri"), "", &s).unwrap();
    let text = std::fs::read_to_string(got.unwrap().0).unwrap();
    assert!(units_of(&root, "hamlet/well").is_empty(), "{text}");
    assert!(text.contains("UID `choice/bamboo--both`") && !text.contains("UID `hamlet/well`"));
    assert!(text.contains("Moved with edits") && text.contains("wells {+(ido)+} were"));
    assert!(!text.contains("Removed (no longer on the page):\n  OLD: The first wells"));
    assert!(!text.contains("Note keys no longer on the page"));
}

/// Feature 451 T194, red first: the replay of a landing follows the source page's pointers, so it models a split as the bundle does.
#[test]
fn a_landing_s_replay_follows_a_split_s_pointers() {
    let root = split_like_t184("triage-t184-replay");
    let landing = crate::record::testkit::commit(&root, "the split");
    let r = root.to_string_lossy().into_owned();
    let out = cli(&args(&["--root", &r, "replay", "--landing", &landing])).stdout;
    let bamboo = format!(
        "choice/bamboo--both\tfires\t{PAGE}\tit repeats words changed in \"the first wells were"
    );
    let well = [
        format!("hamlet/well\tcleared\t{PAGE}\t\n"),
        format!("hamlet/well\tcleared\t{SPLIT_TO}\t\n"),
    ];
    let got = (
        out.contains(&bamboo),
        well.iter().all(|w| out.contains(w.as_str())),
    );
    assert_eq!(got, (true, true), "{out}");
}
