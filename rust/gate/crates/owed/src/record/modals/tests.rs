//! The pop-ups: their text, their fingerprints and what their words or pages owe.

use super::{
    about_keys, agent_units, choice_modal, cli, depiction_owed_by, earlier_units, find,
    fingerprints, modals_at, modals_now, owed, parse_tags, Modal, RevReader,
};
use crate::record::testkit::{commit, git, put, record, DRAWING, PAGE, WELL};

fn strings(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_order_of_the_checks() {
    assert_eq!(agent_units("modal-form"), ["modal-form"]);
    assert_eq!(earlier_units(&strings(&["modal-gaps"])), ["modal-form"]);
    assert_eq!(
        earlier_units(&strings(&["modal-depiction"])),
        [
            "modal-form",
            "modal-accuracy",
            "modal-references",
            "modal-gaps"
        ]
    );
    assert!(earlier_units(&strings(&["modal-form"])).is_empty());
    assert!(earlier_units(&strings(&["modal-gaps", "modal-form"])).is_empty());
    assert!(earlier_units(&strings(&["x"])).is_empty());
    assert!(earlier_units(&[]).is_empty());
}

#[test]
fn tags_read_as_the_page_reads_them() {
    let tags = parse_tags("intro line\nAbout: one\n\n\n\n two  words\nGuesses: - a\n  more\n- b\nDepiction:\n\nfirst\nEntry: x\nAbout: again\nWhy: old\n");
    let get = |k: &str| tags.iter().find(|(t, _)| t == k).map(|(_, v)| v.as_str());
    assert_eq!(get("About"), Some("again"));
    assert_eq!(tags[0].0, "About");
    assert_eq!(get("Guesses"), Some("- a more\n- b"));
    assert_eq!(get("Depiction"), Some("first"));
    assert_eq!(get("Why"), Some("old"));
    assert_eq!(parse_tags("Guesses: x\ny\n")[0].1, "x y");
    assert!(parse_tags("none").is_empty());
}

#[test]
fn a_modal_says_its_uid_files_and_json() {
    let m = choice_modal("l7r/diagram/interactive/assets/modals/choice/a--b.md", "Name: N\nAbout: A\nForm: \nEntry: research/questions/0001-a.html, research/questions/0001-a.html\nDrawing: research/questions/0002-b.drawing.html\nDepiction: D\n", true).unwrap();
    assert_eq!(m.uid(), "choice/a--b");
    assert_eq!(m.entry_files(), ["research/questions/0001-a.html"]);
    assert_eq!(
        m.drawing_files(),
        ["research/questions/0002-b.drawing.html"]
    );
    let j = m.json();
    assert_eq!(j["form"], "standard");
    assert_eq!(Modal::from_json(&j), m);
    assert_eq!(Modal::from_json(&serde_json::Value::Null).key, "");
    let sheet = Modal {
        key: "Karo's House".to_owned(),
        origin: "x/modals/sheet/k.md".to_owned(),
        tags: vec![("Form".to_owned(), "particular".to_owned())],
        ..Modal::default()
    };
    assert_eq!(sheet.uid(), "sheet/karo-s-house");
    assert_eq!(sheet.json()["form"], "particular");
    assert_eq!(
        Modal {
            origin: "compound_kinds/x.py:3".to_owned(),
            ..Modal::default()
        }
        .uid(),
        "sheet/"
    );
    assert!(choice_modal("a.md", "Name: n\n", true).is_none());
    assert!(choice_modal("a.md", "", false).is_none());
    assert!(choice_modal("a.md", "Name: n\n", false).is_some());
    assert!(depiction_owed_by(None, &m));
    assert!(!depiction_owed_by(Some(&m), &m));
    assert!(depiction_owed_by(
        Some(&m),
        &Modal {
            tags: vec![],
            ..m.clone()
        }
    ));
}

#[test]
fn modals_now_and_at_a_revision_and_what_they_owe() {
    let root = record("modals-owed");
    let now = modals_now(&root, true).unwrap();
    let uids: Vec<String> = now.iter().map(Modal::uid).collect();
    assert_eq!(
        uids,
        [
            "hamlet/well",
            "hamlet/notice-board",
            "sheet/well",
            "choice/bamboo--both"
        ]
    );
    assert_eq!(modals_now(&root, false).unwrap().len(), 5);
    assert_eq!(
        now[1].origin,
        "l7r/diagram/interactive/assets/modals/hamlet/notice-board.md"
    );
    assert!(
        find(&now, "water_and_ways.Well").is_some()
            && find(&now, "NoticeBoard").is_some()
            && find(&now, "sheet/well").is_some()
            && find(&now, "nope").is_none()
    );
    assert_eq!(about_keys(&root).unwrap().len(), 3);
    let base = git(&root, &["rev-parse", "HEAD"]);
    assert_eq!(modals_at(&root, &base, true).unwrap().iter().count(), 4);
    assert!(owed(&root, &base, "").unwrap().is_empty());
    let all_new = owed(&root, "", "").unwrap();
    assert!(all_new.iter().any(|r| r.1 == "new to the About form"));
}

/// What a pop-up owes when a page its `Entry:` or `Drawing:` names moved, or its own text changed. Split from the test above with the
/// next, each on a record of its own (feature 449 T164: the one test took 127 ms, over FR-008's tenth of a second).
#[test]
fn a_moved_page_or_a_changed_text_owes_the_modal_checks() {
    let root = record("modals-owed-moved");
    let now = modals_now(&root, true).unwrap();
    let base = git(&root, &["rev-parse", "HEAD"]);
    put(
        &root,
        DRAWING,
        "<h2>How drawn</h2>\n<p>Drawn as a thicker line.</p>\n",
    );
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart, <span class=\"money\">now</span>.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>An unmarked claim.</p>\n");
    put(
        &root,
        "research/questions/0095-other.html",
        "<h2>Other</h2>\n<p class=\"intro\">Old intro.</p>\n<!-- only a comment --><p>Body.</p>\n",
    );
    let rows = owed(&root, &base, "").unwrap();
    let whys: Vec<&str> = rows.iter().map(|r| r.1.as_str()).collect();
    assert!(whys
        .iter()
        .any(|w| w.starts_with("a page its Entry names moved (0094-trade.html)")));
    assert!(whys
        .iter()
        .any(|w| w.starts_with("a page its Drawing: names moved")));
    assert!(owed(&root, &base, "hamlet/notice-board")
        .unwrap()
        .is_empty());
    put(&root, WELL, "Name: Well\nAbout: Changed.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn square.\n");
    put(&root, "research/questions/0099-untracked.html", "<p>x</p>");
    let copy =
        std::fs::read_to_string(root.join("research/questions/0094-trade.originals.html")).unwrap();
    put(
        &root,
        "research/questions/0096-a-copy.originals.html",
        &copy,
    );
    let rows = owed(&root, &base, "hamlet/well").unwrap();
    assert!(rows
        .iter()
        .any(|r| r.0 == "modal-form:hamlet/well" && r.1 == "its About, Guesses or Entry changed"));
    assert!(rows.iter().any(|r| r.0 == "modal-depiction:hamlet/well"
        && r.1 == "its Depiction, Drawing: or Entry: changed"));
    let (form, research) = fingerprints(&root, &now[0]).unwrap();
    assert_ne!(form, research);
}

/// A modal file that is not UTF-8 cannot be read now; a revision's reader reads it as `cat-file` gives it.
#[test]
fn a_modal_file_that_is_not_utf8_is_refused_now_and_read_at_a_revision() {
    let root = record("modals-owed-unreadable");
    let base = git(&root, &["rev-parse", "HEAD"]);
    std::fs::write(root.join(WELL), b"About: \xff\n").unwrap();
    assert!(modals_now(&root, true).is_err());
    assert!(owed(&root, &base, "").is_err());
    commit(&root, "an unreadable modal");
    let head = git(&root, &["rev-parse", "HEAD"]);
    assert_eq!(modals_at(&root, &head, true).unwrap().iter().count(), 4);
}

#[test]
fn a_revision_reader_lists_and_reads() {
    let root = record("modals-rev");
    let mut r = RevReader::new(
        &root,
        "HEAD",
        &["l7r/diagram/interactive/assets/modals/hamlet/"],
    );
    assert_eq!(
        r.names("l7r/diagram/interactive/assets/modals/hamlet"),
        [
            "l7r/diagram/interactive/assets/modals/hamlet/notice-board.md",
            WELL,
            "l7r/diagram/interactive/assets/modals/hamlet/wood-shed.md"
        ]
    );
    assert!(r.read(WELL).is_some());
    assert!(r
        .read("l7r/diagram/interactive/assets/modals/hamlet/none.md")
        .is_none());
    assert!(r.read(PAGE).is_some());
    assert!(r.read("nope.html").is_none());
}

#[test]
fn every_modal_s_ids_are_listed_by_uid() {
    let root = record("modals-ids");
    let r = root.to_string_lossy().into_owned();
    let said = cli(&["--root".to_owned(), r.clone(), "--ids".to_owned()]);
    assert_eq!(said.code, 0);
    let got: serde_json::Value = serde_json::from_str(&said.stdout).unwrap();
    let uids: Vec<&String> = got.as_object().unwrap().keys().collect();
    assert_eq!(
        uids,
        [
            "choice/bamboo--both",
            "hamlet/notice-board",
            "hamlet/well",
            "hamlet/wood-shed",
            "sheet/well"
        ]
    );
    let well = &got["hamlet/well"];
    let m = find(&modals_now(&root, true).unwrap(), "hamlet/well")
        .unwrap()
        .clone();
    assert_eq!(
        (
            well["cls"].as_str(),
            well["origin"].as_str(),
            well["fp_form"].as_str()
        ),
        (
            Some("water_and_ways.Well"),
            Some(WELL),
            Some(fingerprints(&root, &m).unwrap().0.as_str())
        )
    );
    std::fs::write(root.join(WELL), b"About: \xff\n").unwrap();
    assert_eq!(cli(&["--root".to_owned(), r, "--ids".to_owned()]).code, 1);
}

#[test]
fn the_command_line() {
    let root = record("modals-cli");
    put(&root, WELL, "Name: Well\nAbout: Changed.\n");
    let said = cli(&["--root".to_owned(), root.to_string_lossy().into_owned()]);
    assert!(
        said.code == 0
            && said
                .stdout
                .contains("modal-form:hamlet/well  - its About, Guesses or Entry changed\n")
    );
    assert_eq!(cli(&["--x".to_owned()]).code, 2);
    std::fs::write(root.join(WELL), b"About: \xff\n").unwrap();
    assert_eq!(
        cli(&["--root".to_owned(), root.to_string_lossy().into_owned()]).code,
        1
    );
    assert_eq!(
        cli(&["--root".to_owned(), "/nonexistent/at/all".to_owned()]).code,
        0
    );
}
