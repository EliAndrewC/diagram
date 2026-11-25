//! The owed listing, its answers and the seams, on a scratch record.

use std::path::Path;

use serde_json::{json, Value};

use super::answers::{
    amendment1_depiction_answered, answer, answered, file_outside, file_outside_in, keep_reading,
    legacy_depiction_answered, read_answer, reply_checks, settle, store, unanswered, write_answer,
    Named,
};
use super::answers::{keep_parts, siblings_given, store_given};
use super::{cli, command, entry_units, entry_units_of, modal_classes, read_at, units, FAMILIES};
use crate::record::delta::Delta;

fn entry_base(root: &Path) -> String {
    Delta::new(root).entry_base()
}
use crate::record::modals;
use crate::record::testkit::{commit, edit_everything, git, put, record, record_at, PAGE, WELL};

fn run(root: &Path, args: &[&str]) -> crate::Reply {
    let mut all = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    all.extend(args.iter().map(|s| (*s).to_owned()));
    // its own environment, never the session's (feature 451 T38)
    super::cli_in(&all, &l7r_shared::env::Rooted::with(".", &[]))
}

fn none() -> Named<'static> {
    Named {
        q: "",
        notes: "",
        key: "",
        kind: "",
    }
}

/// The scratch record with every kind of edit the listing reads, a hamlet well's text changed and the entry-drift seam's lines: what
/// each of the listing's tests reads, built anew by each, as the one test they were split from built it once (feature 449 T164: a test
/// a tenth of a second, FR-008, where one record answered five listings in 160 ms).
fn listed(tag: &str) -> crate::checks::TempDir {
    let root = record(tag);
    listed_edits(&root);
    root
}

/// [`listed`]'s edits, in the working tree of `root`.
fn listed_edits(root: &Path) {
    edit_everything(root);
    put(root, WELL, "Name: Well\nAbout: Changed too.\nEntry: research/questions/0094-trade.html\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(root, "entry-lines.json", "[\"notakind - 0094-trade.html 0094-trade.drawing.html x.html - prose at x\\n      read: a\", \"privy - 0095-other.html - prose\", \"well - 0094-trade.html - prose\", \"nodash\"]");
}

#[test]
fn the_listing_names_each_unit_and_its_command() {
    let root = record("owed-listing");
    assert_eq!(
        run(&root, &[]).stdout,
        "record-owed: no record check is owed\n"
    );
    listed_edits(&root);
    let said = run(&root, &[]);
    assert_eq!(said.code, 0);
    for want in [
        "make check-bundle KEY=key-a\n",
        "make check-bundle KEY=key-b WHOLE=1  then  make record-checked CHECK=source-reader Q=0094 NOTES=n",
        "make check-bundle KEY=<the note's key> WHOLE=1",
        "make check-bundle Q=0094 FOR=quote-check",
        "make modal-bundle KIND=\"sheet/well\" FOR=modal-research",
        "make modal-triage  then",
        "make check-bundle Q=0094 FOR=entry-drift KIND=\"<the class of notakind>\"",
        "make check-bundle Q=0095 FOR=entry-drift KIND=\"Privy\"",
        "make check-bundle Q=<its section> FOR=entry-drift KIND=\"<the class of nodash>\"",
        "batched: make modal-bundle KIND=\"hamlet/well sheet/well\" FOR=modal-form",
        "translation-check:0094#gloss",
    ] {
        assert!(said.stdout.contains(want));
    }
    let batches: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join(".git/modal-batches.json")).unwrap(),
    )
    .unwrap();
    assert!(batches["batches"]["modal-form"].is_array());
}

#[test]
fn the_listing_s_slugs_and_its_unanswered_units() {
    let root = listed("owed-listing-slugs");
    let slugs = run(
        &root,
        &["--slugs", "--q", "94", "--skip-check", "quote-check"],
    )
    .stdout;
    assert!(
        slugs.contains("record-format:0094\n")
            && !slugs.contains("quote-check")
            && !slugs.contains("0095")
    );
    assert!(run(&root, &["--unanswered"])
        .stdout
        .starts_with("record-owed: "));
}

#[test]
fn the_listing_between_two_revisions_and_its_refusals() {
    let root = listed("owed-listing-between");
    let base = git(&root, &["rev-parse", "HEAD"]);
    commit(&root, "edits");
    let between = run(&root, &["--between", &base, "HEAD"]);
    assert!(between.stdout.contains("record-format:0094") && !between.stdout.contains("modal-"));
    assert_eq!(run(&root, &["--bogus"]).code, 2);
    assert_eq!(cli(&["--root".to_owned(), "/proc".to_owned()]).code, 1);
}

// the answer modes, split by feature 449 T164 into tests of their own, which pushed this file past the 1,000-line bar (Principle X)
mod answer_modes;
// the listing's closing line (451 T241), beside it for the same bar
mod listing_tail;
// a listed note echoed and kept (451 T229), beside it for the same bar
mod noted;
// a re-run on text answered before, marked (451 T232)
mod rerun;

#[test]
fn the_store_keeps_every_answer_and_settles() {
    let root = record("owed-store");
    let s = store(&root);
    write_answer(&s, "a:b", "f1", "r1", Some(&json!({"p": "b1"}))).unwrap();
    assert!(answered(&s, "a:b", "f1", ""));
    assert_eq!(settle(&s, "a:b", "f1", "f2").unwrap(), "answered");
    assert_eq!(settle(&s, "a:b", "f1", "f2").unwrap(), "answered");
    assert_eq!(settle(&s, "c:d", "b", "a").unwrap(), "pending");
    assert_eq!(settle(&s, "c:d", "", "a").unwrap(), "");
    write_answer(&s, "c:d", "b", "now", None).unwrap();
    assert!(answered(&s, "c:d", "a", ""));
    keep_reading(&s, "c:d", "rd", "readings").unwrap();
    keep_reading(&s, "c:d", "rd", "readings").unwrap();
    keep_reading(&s, "none:x", "rd", "readings").unwrap();
    write_answer(&s, "c:d", "b2", "again", None).unwrap();
    assert!(answered(&s, "c:d", "zz", "rd") && !answered(&s, "c:d", "zz", ""));
    std::fs::write(s.join("bad%3Ajson.json"), "{not").unwrap();
    assert!(read_answer(&s, "bad:json").is_empty());
    assert!(write_answer(
        &root.join("research/questions/0094-trade.html/x"),
        "a",
        "b",
        "c",
        None
    )
    .is_err());
    assert_eq!(reply_checks("record-format: 3"), ["record-format"]);
    assert_eq!(
        reply_checks("prose\nmodal-research: x"),
        ["modal-accuracy", "modal-references", "modal-gaps"]
    );
    assert!(reply_checks("nothing").is_empty());
    let own = l7r_shared::env::Rooted::with(&root, &[]);
    assert!(file_outside(&root, "c", "no heading", "")
        .unwrap()
        .filed
        .is_empty());
    assert_eq!(
        file_outside_in(
            &own,
            "c",
            "**OUTSIDE THE CHANGE**:\n- `f` | b | x | effect: page - its reader is told y\n"
        )
        .unwrap()
        .filed
        .len(),
        1
    );
    assert!(root.join("specs/_unfiled/found.jsonl").is_file());
    // the finding in the house style, a straight-quoted word too: found.jsonl is a JSON record (feature 449 T242); its file as given
    let brit = format!("behavio{}", "ur");
    let got = file_outside_in(
        &own,
        "c",
        &format!("**OUTSIDE THE CHANGE**:\n- `{brit}.md` | b | the \"{brit}\" \u{2013} off | effect: map - the \"{brit}\" reads off\n"),
    )
    .unwrap()
    .filed;
    assert_eq!(got[0]["finding"], "the \"behavior\" - off");
    assert_eq!(got[0]["effect"], "map - the \"behavior\" reads off");
    assert_eq!(got[0]["file"], format!("{brit}.md"));
    let written = std::fs::read_to_string(root.join("specs/_unfiled/found.jsonl")).unwrap();
    assert!(written.contains("the \\\"behavior\\\" - off"), "{written}");
}

/// Feature 451 T219: an outside-the-change note is filed only where it names a wrong outcome a reader of the map, the sheet or the
/// page would meet. The two rows are feature 449's own, as its `found.jsonl` holds them: row 178 (2026-11-23, impl-drift), which says
/// `effect: none on the map` in its own text and was filed, then settled by the wording audit as needing no change; and row 170
/// (2026-11-22, impl-drift), the place card that contradicted itself on a declared northwest wind, fixed as 449 T317 - its last
/// sentence, `The place card a reader sees contradicts itself`, said as the effect the form asks for.
#[test]
fn an_outside_note_is_filed_only_where_it_names_a_wrong_outcome_its_reader_meets() {
    let root = crate::checks::scratch("owed-outside-effect");
    let own = l7r_shared::env::Rooted::with(&root, &[]);
    let row_178 = "- docs/building-programs.md | types.json:magistracies row `armory`, why column | \"14 by 16.7 to 14 by 20 ft in a hall\" names only the drawn back-row size, while the band's default form runs to 18 by 41 ft; effect: none on the map, but the table's why does not cover the band it sits beside";
    let row_170 = "- rust/mode_a/src/place.rs | windbreak_default, the \"declared\" arm | A record with a declared wind from NW prints \"a local wind from the northwest that departs from the region's northwesterly winter wind\" | effect: map - the place card a reader sees contradicts itself";
    let silent = "- research/questions/0019-x.drawing.html | the fringe | the page is silent on the fringe's width";
    let reply = format!("impl-drift: 1\n\n## OUTSIDE THE CHANGE\n{row_178}\n{row_170}\n{silent}\n");
    let got = file_outside_in(&own, "impl-drift", &reply).unwrap();
    assert_eq!(got.filed.len(), 1);
    assert_eq!(got.filed[0]["file"], "rust/mode_a/src/place.rs");
    assert_eq!(
        got.filed[0]["effect"],
        "map - the place card a reader sees contradicts itself"
    );
    assert_eq!(got.dropped.len(), 2);
    let written = std::fs::read_to_string(root.join("specs/_unfiled/found.jsonl")).unwrap();
    assert_eq!(written.lines().count(), 1, "{written}");
    let said = got.said("claims-checked");
    assert!(
        said.starts_with("claims-checked: filed, not fixed - rust/mode_a/src/place.rs | windbreak_default")
            && said.contains("claims-checked: listed, not filed - docs/building-programs.md | types.json:magistracies row `armory`, why column |")
            && said.contains("claims-checked: listed, not filed - research/questions/0019-x.drawing.html | the fringe | the page is silent")
            && said.ends_with("claims-checked: a note outside the change is filed only where it ends `| effect: <map|sheet|page|tool> - <the wrong outcome its reader or user meets>` (451 T219); the rest are listed, not filed, and kept in specs/_unfiled/noted.jsonl (451 T229)\n"),
    );
    // nothing dropped, nothing to teach; nothing filed, no file written
    assert!(
        !file_outside_in(&own, "c", &format!("## OUTSIDE THE CHANGE\n{row_170}\n"))
            .unwrap()
            .said("x")
            .contains("only where")
    );
    let bare = crate::checks::scratch("owed-outside-none");
    let none = file_outside_in(
        &l7r_shared::env::Rooted::with(&bare, &[]),
        "c",
        &format!("## OUTSIDE THE CHANGE\n{silent}\n"),
    )
    .unwrap();
    // nothing filed, no found row written; the listed note is kept in noted.jsonl (451 T229)
    assert!(none.filed.is_empty() && !bare.join("specs/_unfiled/found.jsonl").exists());
    // constitution XIV's other defect, a tool that refuses valid input, is filed too: 451's found row 26 (the make-only guard)
    let guard = "- rust/guard/src/guards/make_only_hooks.rs | the direct-binary refusal | it reads a mention of the gate binary's path as a run of it | effect: tool - the make-only guard refuses `find ... -newer <tool/l7r-gate>`, a valid command";
    let tool = file_outside_in(
        &own,
        "impl-drift",
        &format!("## OUTSIDE THE CHANGE\n{guard}\n"),
    )
    .unwrap();
    assert_eq!(
        (tool.filed.len(), tool.dropped.len(), &tool.filed[0]["effect"]),
        (1, 0, &serde_json::json!("tool - the make-only guard refuses `find ... -newer <tool/l7r-gate>`, a valid command"))
    );
}

#[test]
fn an_answer_elsewhere_or_under_an_older_formula_still_answers() {
    let base = crate::checks::scratch("owed-adopt");
    let root = record_at(&base.join(".clones/main"));
    edit_everything(&root);
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let sib = base.join(".clones/sib/.git/record-checks");
    let rf = rows
        .iter()
        .find(|u| u.slug == "record-format:0094")
        .unwrap();
    l7r_gate_core::build::with(Some("{\"commit\": \"c9\"}"), false, || {
        write_answer(&sib, &rf.slug, &rf.fingerprint, "elsewhere", None)
    })
    .unwrap();
    keep_reading(&sib, &rf.slug, "r9", "readings").unwrap();
    let left = unanswered(&root).unwrap();
    assert!(!left.iter().any(|u| u.slug == "record-format:0094"));
    let mine = read_answer(&store(&root), "record-format:0094");
    assert!(mine.contains_key("readings"));
    // the judge's build comes with an adopted answer (451 T197)
    assert_eq!(mine["builds"][&rf.fingerprint]["commit"], "c9");
}

/// A depiction answered under the formula before amendment 1, or under amendment 1's, still answers; a record of another unit, or of
/// no time or an old one, answers neither. Split from the test above, in the same clone layout and edits (feature 449 T164: the one
/// test took 128 ms, over FR-008's tenth of a second).
#[test]
fn a_depiction_answered_under_an_older_formula_still_answers() {
    let (base, now) = well_redrawn("owed-adopt-formula");
    let root = base.join(".clones/main");
    let well = modals::find(&now, "hamlet/well").unwrap();
    let slug = "modal-depiction:hamlet/well";
    let s = store(&root);
    let rec = json!({"unit": slug, "answered": [modals::legacy_depiction_fingerprint(&root, well).unwrap()], "utc": "2099-01-01T00:00:00Z"});
    std::fs::write(
        s.join("modal-depiction%3Ahamlet%2Fwell.json"),
        rec.to_string(),
    )
    .unwrap();
    assert!(legacy_depiction_answered(&root, &s, slug, &now).unwrap());
    assert!(!amendment1_depiction_answered(&root, &s, slug, &now).unwrap());
    let rec = json!({"unit": slug, "answered": [modals::amendment1_depiction_fingerprint(&root, well).unwrap()], "utc": "2099-01-01T00:00:00Z"});
    std::fs::write(
        s.join("modal-depiction%3Ahamlet%2Fwell.json"),
        rec.to_string(),
    )
    .unwrap();
    assert!(amendment1_depiction_answered(&root, &s, slug, &now).unwrap());
    for (other, utc) in [
        ("modal-form:hamlet/well", "x"),
        ("modal-depiction:nope", "x"),
        (slug, ""),
        (slug, "1990-01-01T00:00:00Z"),
    ] {
        std::fs::write(
            s.join("modal-depiction%3Ahamlet%2Fwell.json"),
            json!({"utc": utc, "answered": []}).to_string(),
        )
        .unwrap();
        assert!(!legacy_depiction_answered(&root, &s, other, &now).unwrap());
        assert!(!amendment1_depiction_answered(&root, &s, other, &now).unwrap());
    }
}

/// The clone layout and edits of [`an_answer_elsewhere_or_under_an_older_formula_still_answers`], the hamlet well's depiction redrawn and
/// committed, its store made as the answers before the split made it; the pop-ups now.
fn well_redrawn(tag: &str) -> (crate::checks::TempDir, Vec<modals::Modal>) {
    let base = crate::checks::scratch(tag);
    let root = record_at(&base.join(".clones/main"));
    edit_everything(&root);
    put(&root, WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn square now.\nDrawing: research/questions/0094-trade.drawing.html\n");
    commit(&root, "the well redrawn");
    std::fs::create_dir_all(store(&root)).unwrap();
    let now = modals::modals_now(&root, true).unwrap();
    (base, now)
}

/// A depiction answered under amendment 1's formula is not listed unanswered. Split from the test above, on the same redrawn well
/// (feature 449 T164: with it the test took 102 ms, over FR-008's tenth of a second).
#[test]
fn a_depiction_answered_under_amendment_1_is_not_unanswered() {
    let (base, now) = well_redrawn("owed-adopt-unanswered");
    let root = base.join(".clones/main");
    let well = modals::find(&now, "hamlet/well").unwrap();
    let slug = "modal-depiction:hamlet/well";
    let rec = json!({"unit": slug, "answered": [modals::amendment1_depiction_fingerprint(&root, well).unwrap()], "utc": "2099-01-01T00:00:00Z"});
    std::fs::write(
        store(&root).join("modal-depiction%3Ahamlet%2Fwell.json"),
        rec.to_string(),
    )
    .unwrap();
    assert!(!unanswered(&root).unwrap().iter().any(|u| u.slug == slug));
}

#[test]
fn a_reader_who_quoted_their_own_passages_is_not_owed_again() {
    let root = record("owed-readers");
    edit_everything(&root);
    let s = store(&root);
    let named = Named {
        q: "94",
        notes: "n",
        key: "",
        kind: "",
    };
    let done = answer(
        &root,
        "source-reader",
        "READ",
        "",
        &named,
        "\u{300c}more\u{300d}",
    )
    .unwrap();
    assert_eq!(done, ["source-reader:0094#n"]);
    let mut text =
        std::fs::read_to_string(root.join("research/questions/0094-trade.notes.html")).unwrap();
    text = text.replace(
        "\u{300c}more\u{300d}",
        "\u{300c}more\u{300d} \u{300c}mo\u{300d}",
    );
    put(&root, "research/questions/0094-trade.notes.html", &text);
    let left = unanswered(&root).unwrap();
    assert!(left.iter().any(|u| u.slug == "quote-check:0094#n"));
    let _ = s;
}

/// An answer that names no owed unit of its check answers none: an intro-check named by nothing, a source-reader on notes the page
/// does not hold. Split from the test above, on the same edited notes (feature 449 T164, FR-008's tenth of a second).
#[test]
fn an_answer_naming_no_owed_unit_answers_none() {
    let root = record("owed-readers-none");
    edit_everything(&root);
    let mut text =
        std::fs::read_to_string(root.join("research/questions/0094-trade.notes.html")).unwrap();
    text = text.replace(
        "\u{300c}more\u{300d}",
        "\u{300c}more\u{300d} \u{300c}mo\u{300d}",
    );
    put(&root, "research/questions/0094-trade.notes.html", &text);
    assert!(answer(&root, "intro-check", "x", "", &none(), "")
        .unwrap()
        .is_empty());
    let drawn = Named {
        q: "94",
        notes: "d",
        key: "",
        kind: "",
    };
    assert!(answer(&root, "source-reader", "R", "", &drawn, "")
        .unwrap()
        .is_empty());
}

#[test]
fn the_entry_drift_units_and_their_commands() {
    let root = record("owed-entry");
    let now = read_at(&root, None, None).unwrap();
    let lines: Vec<String> = [
        "notakind - 0094-trade.html 0094-trade.drawing.html x.html - prose at x\n      read: a",
        "privy - 0095-other.html - prose",
        "well - 0094-trade.html - prose",
        "nodash",
    ]
    .map(str::to_owned)
    .to_vec();
    let got = entry_units_of(&root, &now, lines).unwrap();
    let slugs: Vec<&str> = got.iter().map(|u| u.slug.as_str()).collect();
    // `well` is an About-form modal, owed the modal checks instead
    assert_eq!(
        slugs,
        [
            "entry-drift:notakind",
            "entry-drift:privy",
            "entry-drift:nodash"
        ]
    );
    let none = std::collections::HashMap::new();
    let said: Vec<String> = got.iter().map(|u| command(u, &now, &none)).collect();
    assert!(said[0]
        .starts_with("make check-bundle Q=0094 FOR=entry-drift KIND=\"<the class of notakind>\""));
    assert!(said[1].starts_with("make check-bundle Q=0095 FOR=entry-drift KIND=\"Privy\""));
    assert!(said[2].starts_with(
        "make check-bundle Q=<its section> FOR=entry-drift KIND=\"<the class of nodash>\""
    ));
    // a key both registries hold names each class by its module (feature 449 T149: the registry's kinds, as the lexing met them)
    assert_eq!(
        modal_classes("well"),
        ["water_and_ways.Well", "household.Well"]
    );
    assert!(modal_classes("nope").is_empty());
}

#[test]
fn the_entry_drift_report_runs_in_process() {
    let root = record("owed-entry-run");
    put(&root, "entry-real", "");
    let now = read_at(&root, None, None).unwrap();
    // nothing moved: nothing named, and the registry is not loaded
    assert!(entry_units(&root, &now).unwrap().is_empty());
    assert!(units(&root, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
    // the tests' seam: lines named, or none
    put(&root, "entry-lines.json", "not json");
    std::fs::remove_file(root.join("entry-real")).unwrap();
    assert!(entry_units(&root, &now).is_err());
    std::fs::remove_file(root.join("entry-lines.json")).unwrap();
    assert!(entry_units(&root, &now).unwrap().is_empty());
    // a tree with no modal files is a tree with no engine: refused, as the Python's import refused it
    put(&root, "entry-real", "");
    std::fs::remove_dir_all(root.join(crate::record::modals::MODALS)).unwrap();
    assert!(entry_units(&root, &now).is_err());
    assert!(units(&root, None, None, &["entry-drift"], "").is_err());
    let fresh = crate::checks::scratch("owed-entry-empty");
    git(&fresh, &["init", "-q"]);
    assert!(units(&fresh, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
}

#[test]
fn the_entry_drift_report_loads_the_registry_when_a_page_moved() {
    let root = record("owed-entry-moved");
    put(&root, "entry-real", "");
    let now = read_at(&root, None, None).unwrap();
    // a page's findings moved: the registry loads, and the scratch tree holds only a few of its kinds' files - the Python's import error
    put(
        &root,
        PAGE,
        "<h2 id=\"t\">Trade</h2>\n<p>A new finding.</p>\n",
    );
    assert!(entry_units(&root, &now).is_err());
    // every kind's file, written in the working tree (no commit, FR-008): the registry loads and the report runs, and every kind it
    // names is About-form, owed the modal checks instead
    l7r_gate_registry::testkit::modals(&root, "research/questions/0094-trade.html");
    put(
        &root,
        PAGE,
        "<h2 id=\"t\">Trade</h2>\n<p>Another finding.</p>\n",
    );
    assert!(entry_units(&root, &now).unwrap().is_empty());
}

#[test]
fn a_file_entry_owed_reads_starts_it_with_no_page_changed() {
    let root = record("owed-entry-reads");
    let started = |root: &Path| super::entry_drift_owed(&mut Delta::new(root)).unwrap();
    // nothing it reads changed: not started
    assert!(!started(&root));
    // a modal file of the registry, edited in the working tree: started
    put(&root, WELL, "Name: Well\nAbout: Changed.\n");
    assert!(started(&root));
    git(&root, &["checkout", "--", WELL]);
    // a new file under the engine's interactive package, untracked: started too
    put(
        &root,
        "l7r/diagram/interactive/assets/siblings.json",
        "{}\n",
    );
    assert!(started(&root));
    std::fs::remove_file(root.join("l7r/diagram/interactive/assets/siblings.json")).unwrap();
    // a file elsewhere in the record it reads: started
    put(&root, "research/tags.json", "{}\n");
    assert!(started(&root));
    std::fs::remove_file(root.join("research/tags.json")).unwrap();
    // a file it never reads, alone: not started
    put(&root, "docs/notes.md", "x\n");
    assert!(!started(&root));
    // no modal files at all: the tree with no engine, started so its refusal is seen
    std::fs::remove_dir_all(root.join(crate::record::modals::MODALS)).unwrap();
    assert!(started(&root));
}

#[test]
fn a_revision_read_and_a_failing_read() {
    let root = record("owed-read");
    let rec = read_at(&root, Some("HEAD"), Some(&std::collections::HashSet::new())).unwrap();
    assert!(rec.notes.get("0094").is_some() && rec.sources.iter().count() == 0);
    assert_eq!(
        read_at(&root, Some("HEAD"), None)
            .unwrap()
            .sources
            .iter()
            .count(),
        1
    );
    std::fs::write(root.join("research/questions/0094-bad.html"), [0xff, 0xfe]).unwrap();
    assert!(read_at(&root, None, None).is_err());
    assert_eq!(run(&root, &[]).code, 1);
    std::fs::remove_file(root.join("research/questions/0094-bad.html")).unwrap();
    std::fs::write(
        root.join("research/sources/010-works-cited/0002-bad.html"),
        [0xff],
    )
    .unwrap();
    assert!(read_at(&root, None, None).is_err());
}

#[test]
fn the_store_and_its_siblings_with_the_test_variable_given() {
    // the three trees in one scratch directory: each `TempDir` sweeps the temp directory of dead ones first, 20 ms where it holds
    // 8,500 entries, and FR-008 holds a test to a tenth of a second (feature 449 T164)
    let top = crate::checks::scratch("owed-env");
    let root = record_at(&top.join("rec"));
    assert_eq!(
        store_given(&root, Some("/x/y".into())),
        std::path::PathBuf::from("/x/y")
    );
    assert!(store_given(&root, Some("".into())).ends_with(".git/record-checks"));
    // the store a root's own environment names (feature 451 T38), and none named there though the process may export one
    let rooted = l7r_shared::env::Rooted::with(&*root, &[("RECORD_CHECKS_DIR", "/x/z")]);
    assert_eq!(
        super::answers::store_in(&rooted),
        std::path::PathBuf::from("/x/z")
    );
    let unnamed = l7r_shared::env::Rooted::with(&*root, &[]);
    assert!(super::answers::store_in(&unnamed).ends_with(".git/record-checks"));
    let base = top.join("sib");
    let main = record_at(&base.join(".clones/main"));
    std::fs::create_dir_all(base.join(".clones/sib/.git/record-checks")).unwrap();
    std::fs::create_dir_all(base.join(".clones/bare")).unwrap();
    assert_eq!(siblings_given(&main, None).len(), 1);
    assert!(siblings_given(&main, Some("/t".into())).is_empty());
    assert_eq!(entry_base(&main), git(&main, &["rev-parse", "HEAD"]));
    git(&main, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert_eq!(entry_base(&main), git(&main, &["rev-parse", "HEAD"]));
    let empty = top.join("empty");
    std::fs::create_dir_all(&empty).unwrap();
    git(&empty, &["init", "-q"]);
    assert_eq!(entry_base(&empty), "");
}

#[test]
fn a_record_with_no_commit_and_the_seams_noise() {
    let root = crate::checks::scratch("owed-nocommit");
    git(&root, &["init", "-q"]);
    put(
        &root,
        "research/questions/0094-trade.html",
        "<h2>T</h2><p>Claim.<sup class=\"fn\" data-note=\"k\"></sup></p>",
    );
    put(
        &root,
        "research/questions/0094-trade.notes.html",
        "<li data-note=\"k\">\"q\"</li>",
    );
    let got = units(&root, None, None, &["record"], "").unwrap();
    assert!(got.iter().any(|u| u.slug == "quote-check:0094#k"));
    let (done, refused) = super::answers::fixed_answer(&root, "94", "k", "x: y").unwrap();
    assert!(done.is_empty() && refused == ["quote-check:0094#k"]);
    let rec = record("owed-noise");
    put(&rec, "r.md", "x\r\n&lt;&lt;&lt; kept");
    let at = |n: &str| rec.join(n).to_string_lossy().into_owned();
    assert_eq!(
        super::answers::reply_of(&rec, &at("r.md")).unwrap(),
        "x\n<<< kept"
    );
    put(&rec, "s.md", "&lt;&lt;&lt;\n<<<");
    assert_eq!(
        super::answers::reply_of(&rec, &at("s.md")).unwrap(),
        "&lt;&lt;&lt;\n<<<"
    );
    assert!(super::answers::reply_of(&rec, &at("none.md")).is_err());
}

#[test]
fn a_transcript_gives_its_last_assistant_reply() {
    use super::answers::reply_text;
    let rec = crate::checks::scratch("owed-transcript");
    let text = |lines: &[&str]| lines.join("\n") + "\n";
    put(
        &rec,
        "a.jsonl",
        &text(&[
            r#"{"type": "assistant", "message": {"content": [{"type": "text", "text": "one"}, {"type": "text", "text": " two"}]}}"#,
            r#"{"type": "assistant", "message": {"content": [{"type": "tool_use"}]}}"#,
            r#"{"type": "user", "message": "a string, never read"}"#,
            r#"{"type": "assistant", "message": {"content": "not a list"}}"#,
            r#"{"type": "assistant"}"#,
            "not json",
        ]),
    );
    assert_eq!(reply_text(&rec.join("a.jsonl")).unwrap(), "one two");
    put(&rec, "b.output", &text(&["5"]));
    assert!(reply_text(&rec.join("b.output")).is_err());
    put(
        &rec,
        "c.jsonl",
        &text(&[r#"{"type": "assistant", "message": [1]}"#]),
    );
    assert!(reply_text(&rec.join("c.jsonl")).is_err());
    put(
        &rec,
        "d.jsonl",
        &text(&[r#"{"type": "assistant", "message": {"content": [1]}}"#]),
    );
    assert!(reply_text(&rec.join("d.jsonl")).is_err());
    put(
        &rec,
        "e.jsonl",
        &text(&[r#"{"type": "assistant", "message": {"content": [{"type": "text", "text": 1}]}}"#]),
    );
    assert!(reply_text(&rec.join("e.jsonl")).is_err());
    put(
        &rec,
        "f.jsonl",
        &text(&[r#"{"type": "assistant", "message": {"content": [{"type": "text"}]}}"#]),
    );
    assert_eq!(reply_text(&rec.join("f.jsonl")).unwrap(), "");
    put(&rec, ".jsonl", "&lt;&lt;&lt;");
    assert_eq!(reply_text(&rec.join(".jsonl")).unwrap(), "<<<");
}

/// The source-reader answers [`what_a_source_reader_read_is_kept_and_netted`] starts from: what each kept of what it read, and the
/// `n` note's reader netted by a quote-check answered at the note's fingerprint now. Returns the store and the `n` reader's slug.
fn readers_kept(root: &Path) -> (std::path::PathBuf, String) {
    let s = store(root);
    keep_parts(&s, "source-reader:0094#n", root, "").unwrap();
    write_answer(&s, "source-reader:0094.drawing#d", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094.drawing#d", root, "").unwrap();
    write_answer(&s, "source-reader:0094#t", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094#t", root, "").unwrap();
    assert!(read_answer(&s, "source-reader:0094#t")["passages"]
        .as_array()
        .is_some_and(|a| !a.is_empty()));
    write_answer(&s, "source-reader:0094#gone", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094#gone", root, "").unwrap();
    // the record family alone, whose units these are: the other three families' work and git reads are not this helper's (feature 449
    // T164, FR-008)
    let rows = units(root, None, None, &["record"], "").unwrap();
    let n = rows
        .iter()
        .find(|u| u.slug == "source-reader:0094#n")
        .unwrap()
        .clone();
    write_answer(&s, &n.slug, "older", "READ", None).unwrap();
    keep_parts(&s, &n.slug, root, "\u{300c}more\u{300d} \u{300c}x\u{300d}").unwrap();
    let qn = rows
        .iter()
        .find(|u| u.slug == "quote-check:0094#n")
        .unwrap()
        .clone();
    write_answer(&s, &qn.slug, &qn.fingerprint, "V", None).unwrap();
    (s, n.slug)
}

/// The `n` note's quotation changed past what its reader quoted, and its quote-check answered again at the new fingerprint.
fn quotation_changed(root: &Path, s: &Path) {
    let mut text =
        std::fs::read_to_string(root.join("research/questions/0094-trade.notes.html")).unwrap();
    text = text.replace(
        "\"new\" \u{300c}more\u{300d}",
        "\"new\" \u{300c}more\u{300d} \"newer\"",
    );
    put(root, "research/questions/0094-trade.notes.html", &text);
    // the record family alone, whose units these are: the other three families' work and git reads are not this helper's (feature 449
    // T164, FR-008)
    let rows = units(root, None, None, &["record"], "").unwrap();
    let qn = rows
        .iter()
        .find(|u| u.slug == "quote-check:0094#n")
        .unwrap()
        .clone();
    write_answer(s, &qn.slug, &qn.fingerprint, "V", None).unwrap();
}

/// What a source-reader read is kept, and a reader whose note changed by nothing but the passages it quoted is netted: not owed.
/// The one record this and the next two tests shared took 141 ms; each now builds the state its own assertions read (feature 449
/// T164, FR-008's tenth of a second).
#[test]
fn what_a_source_reader_read_is_kept_and_netted() {
    let root = record("owed-parts");
    edit_everything(&root);
    let (_, n) = readers_kept(&root);
    assert!(!unanswered(&root).unwrap().iter().any(|u| u.slug == n));
}

/// A passage the reader never quoted, added to the note: the reader is owed again.
#[test]
fn a_reader_whose_note_gained_a_passage_it_never_quoted_is_owed_again() {
    let root = record("owed-parts-gained");
    edit_everything(&root);
    let (s, n) = readers_kept(&root);
    quotation_changed(&root, &s);
    assert!(unanswered(&root).unwrap().iter().any(|u| u.slug == n));
    // the reader's record, which the test this was split from removed next
    assert!(s.join("source-reader%3A0094%23n.json").is_file());
}

/// A reader's answer kept nothing it read (an older answer, no passages): it is owed when its note changed.
#[test]
fn a_reader_that_kept_nothing_it_read_is_owed_again() {
    let root = record("owed-parts-none");
    edit_everything(&root);
    let s = store(&root);
    quotation_changed(&root, &s);
    let n = "source-reader:0094#n";
    write_answer(&s, n, "older", "READ", None).unwrap();
    assert!(unanswered(&root).unwrap().iter().any(|u| u.slug == n));
}

#[test]
fn an_answered_listing_and_a_docstring_modal_then() {
    let root = record("owed-listed");
    edit_everything(&root);
    let ok = run(
        &root,
        &[
            "--answer",
            "record-format",
            "--result",
            "r",
            "--q",
            "94",
            "--reason",
            "a stated reason",
        ],
    );
    assert_eq!(ok.code, 0);
    let said = run(&root, &[]).stdout;
    assert!(
        said.contains("still unanswered") && said.contains("  [answered] record-format:0094  - ")
    );
}

/// A notes file outside the record's questions owes nothing.
#[test]
fn notes_outside_the_questions_owe_nothing() {
    let root = record("owed-listed-outside");
    edit_everything(&root);
    put(
        &root,
        "research/other/x.notes.html",
        "<li data-note=\"a\">\"q\" \u{300c}o\u{300d}</li>",
    );
    assert!(!run(&root, &["--slugs"]).stdout.contains("research/other"));
}

/// Split, with the test above, from [`an_answered_listing_and_a_docstring_modal_then`], on the same edits (feature 449 T164: the one
/// test took 119 ms, over FR-008's tenth of a second).
#[test]
fn an_old_answer_is_never_taken_for_a_docstring_modal() {
    let root = record("owed-listed-docstring");
    edit_everything(&root);
    let s = store(&root);
    // the store the answer before the split had made
    std::fs::create_dir_all(&s).unwrap();
    let now = modals::modals_now(&root, true).unwrap();
    // a pop-up read from a class docstring (its origin a module's line; none is since feature 319, and the registry reads none since
    // feature 449 T149): an old answer is never taken for it, there being no file to read as it stood
    let docstring = modals::Modal {
        origin: "l7r/diagram/interactive/classes/homestead.py:6".to_owned(),
        ..modals::find(&now, "hamlet/notice-board").unwrap().clone()
    };
    let now = vec![docstring];
    let board = &now[0];
    let slug = "modal-depiction:hamlet/notice-board";
    let rec = json!({"answered": [modals::legacy_depiction_fingerprint(&root, board).unwrap()], "utc": "2099-01-01T00:00:00Z"});
    std::fs::write(
        s.join("modal-depiction%3Ahamlet%2Fnotice-board.json"),
        rec.to_string(),
    )
    .unwrap();
    assert!(!legacy_depiction_answered(&root, &s, slug, &now).unwrap());
}

#[test]
fn a_second_pending_settle_survives_the_first_answer() {
    let root = record("owed-settles");
    let s = store(&root);
    assert_eq!(settle(&s, "e:f", "b1", "a1").unwrap(), "pending");
    assert_eq!(settle(&s, "e:f", "b2", "a2").unwrap(), "pending");
    write_answer(&s, "e:f", "b1", "r", None).unwrap();
    assert_eq!(read_answer(&s, "e:f")["settles"], json!({"b2": "a2"}));
}

#[test]
fn the_door_s_reads_of_the_fingerprints_and_the_notes() {
    let root = record("owed-door-reads");
    edit_everything(&root);
    let got = super::fingerprints(&root, &["record-format".to_owned()]).unwrap();
    assert!(
        !got.is_empty()
            && got
                .iter()
                .all(|(slug, _)| slug.starts_with("record-format"))
    );
    let rec = read_at(&root, None, None).unwrap();
    let (notes, cites) = super::notes_of(&rec);
    assert!(notes.is_object() && cites.is_object());
}

#[test]
fn a_translated_pair_and_a_gloss_are_owed_units() {
    let root = record("owed-translation-units");
    put(
        &root,
        "research/questions/0094-trade.notes.html",
        "<li data-note=\"t\">\u{300c}the hedge\u{300d} (translated; original: \u{300c}\u{57a3}\u{300d})</li>\n<li data-note=\"g\">\u{6728} (ki, \"tree\") here.</li>\n",
    );
    put(
        &root,
        "research/questions/zz.notes.html",
        "<li data-note=\"x\">\u{300c}a\u{300d} (translated; original: \u{300c}\u{4e00}\u{300d})</li>\n",
    );
    let got = units(&root, None, None, &["translation"], "").unwrap();
    let slugs: Vec<&str> = got.iter().map(|u| u.slug.as_str()).collect();
    assert!(slugs.contains(&"translation-check:0094#t"));
    assert!(slugs.contains(&"translation-check:0094#gloss"));
}

/// Each answer records the build that judged it, a settled one keeps its judge's, and a landing alone re-owes an answer whose build
/// held an uncommitted file other than the landing's own, naming it (a file deleted then and absent from the landing is as landed);
/// outside a landing, or with the build's files as landed, it stands (feature 451 T197, gap audit item 9).
#[test]
fn an_answer_records_its_build_and_a_landing_alone_re_owes_a_mixed_one() {
    use l7r_gate_core::build::with;
    let root = record("owed-build");
    edit_everything(&root);
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let rf = rows
        .iter()
        .find(|u| u.slug == "record-format:0094")
        .unwrap()
        .clone();
    let s = store(&root);
    let blob = git(&root, &["rev-parse", &format!("HEAD:{PAGE}")])
        .trim()
        .to_owned();
    let own = format!("{{\"commit\": \"c1\", \"dirty\": {{\"{PAGE}\": \"{blob}\"}}}}");
    let others = "{\"commit\": \"c1\", \"dirty\": {\"rust/gate/x.rs\": \"b7\", \"rust/gone.rs\": \"deleted\"}}";
    let owes = |landing: bool| {
        with(None, landing, || unanswered(&root))
            .unwrap()
            .into_iter()
            .find(|u| u.slug == rf.slug)
    };
    with(Some(&own), false, || {
        write_answer(&s, &rf.slug, &rf.fingerprint, "r", None)
    })
    .unwrap();
    assert_eq!(
        read_answer(&s, &rf.slug)["builds"][&rf.fingerprint]["commit"],
        "c1"
    );
    assert!(owes(true).is_none());
    with(Some(others), false, || {
        write_answer(&s, &rf.slug, &rf.fingerprint, "r", None)
    })
    .unwrap();
    assert!(owes(false).is_none());
    let u = owes(true).expect("a mixed answer re-owed in a landing alone");
    assert!(
        u.occasion.contains("(rust/gate/x.rs)") && u.occasion.contains("re-judge"),
        "{}",
        u.occasion
    );
    with(Some(&own), false, || {
        settle(&s, &rf.slug, &rf.fingerprint, "fp2")
    })
    .unwrap();
    let rec = read_answer(&s, &rf.slug);
    assert_eq!(rec["builds"]["fp2"], rec["builds"][&rf.fingerprint]);
    with(None, false, || write_answer(&s, &rf.slug, "fp3", "r", None)).unwrap();
    assert!(read_answer(&s, &rf.slug)["builds"].get("fp3").is_none());
}

/// The round arbiter's red fixture (feature 451 T225, `ask:stamp-reads-committed-code-as-mixed`): an answer whose build's stamped blob
/// is the file's at an earlier commit of the landing's delta, and not HEAD's, was made by the landing's own committed code and
/// stands; one whose blob no commit of the landing holds is re-owed, as is the first once no base names the delta.
#[test]
fn an_answer_by_a_build_of_an_earlier_commit_of_the_landing_stands() {
    use l7r_gate_core::build::with;
    let root = record("owed-build-own");
    let file = "rust/gate/crates/owed/src/record/owed/answers.rs";
    let base = git(&root, &["rev-parse", "HEAD"]);
    git(
        &root,
        &["update-ref", "refs/remotes/origin/main", base.trim()],
    );
    put(&root, file, "// as the answer's build held it\n");
    let _ = commit(&root, "the landing's commit of it, unchanged");
    let then = git(&root, &["rev-parse", &format!("HEAD:{file}")]);
    put(&root, file, "// a later fix of the same landing\n");
    let _ = commit(&root, "the landing's later commit");
    edit_everything(&root);
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let rf = rows
        .iter()
        .find(|u| u.slug == "record-format:0094")
        .unwrap()
        .clone();
    let s = store(&root);
    let owes = |blob: &str| {
        let build = format!("{{\"commit\": \"c1\", \"dirty\": {{\"{file}\": \"{blob}\"}}}}");
        with(Some(&build), false, || {
            write_answer(&s, &rf.slug, &rf.fingerprint, "r", None)
        })
        .unwrap();
        with(None, true, || unanswered(&root))
            .unwrap()
            .into_iter()
            .find(|u| u.slug == rf.slug)
    };
    assert!(owes(then.trim()).is_none());
    let u = owes("0123456789012345678901234567890123456789")
        .expect("a blob no commit of the landing holds is another builder's");
    assert!(u.occasion.contains(&format!("({file})")), "{}", u.occasion);
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert!(owes(then.trim()).is_some());
}

/// A landing alone re-owes a record answer only for uncommitted code its own verbs can run (feature 451 T224, the round arbiter's
/// `ask:mixed-build-53-record-answers`): the claims crate's files and a Markdown doc mix nothing, the check bundle's builder does.
#[test]
fn a_record_answer_is_mixed_only_by_code_that_builds_or_records_it() {
    use l7r_gate_core::build::with;
    let root = record("owed-build-closure");
    edit_everything(&root);
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let rf = rows
        .iter()
        .find(|u| u.slug == "record-format:0094")
        .unwrap()
        .clone();
    let s = store(&root);
    let owes = |dirty: &str| {
        let build = format!("{{\"commit\": \"c1\", \"dirty\": {{{dirty}}}}}");
        with(Some(&build), false, || {
            write_answer(&s, &rf.slug, &rf.fingerprint, "r", None)
        })
        .unwrap();
        with(None, true, || unanswered(&root))
            .unwrap()
            .into_iter()
            .find(|u| u.slug == rf.slug)
    };
    let claims = "\"rust/gate/CLAUDE.md\": \"b1\", \"rust/gate/crates/claims/src/claims/index.rs\": \"b2\", \"rust/gate/crates/claims/src/claims/commands/tests.rs\": \"b3\"";
    assert!(owes(claims).is_none());
    let check = "rust/gate/crates/bundle/src/record/bundle/check.rs";
    let u = owes(&format!("{claims}, \"{check}\": \"b4\""))
        .expect("an answer whose bundle's builder was uncommitted is re-owed");
    assert!(u.occasion.contains(&format!("({check})")), "{}", u.occasion);
}
