//! The owed listing, its answers and the seams, on a scratch record.

use std::path::Path;

use serde_json::{json, Value};

use super::answers::{
    amendment1_depiction_answered, answer, answered, bundle_less_refusal, file_outside,
    fixed_answer, keep_reading, legacy_depiction_answered, read_answer, reply_checks, settle,
    store, unanswered, write_answer, Named,
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
    cli(&all)
}

fn none() -> Named<'static> {
    Named {
        q: "",
        notes: "",
        key: "",
        kind: "",
    }
}

#[test]
fn the_listing_names_each_unit_and_its_command() {
    let root = record("owed-listing");
    assert_eq!(
        run(&root, &[]).stdout,
        "record-owed: no record check is owed\n"
    );
    edit_everything(&root);
    put(&root, WELL, "Name: Well\nAbout: Changed too.\nEntry: research/questions/0094-trade.html\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, "entry-lines.json", "[\"notakind - 0094-trade.html 0094-trade.drawing.html x.html - prose at x\\n      read: a\", \"privy - 0095-other.html - prose\", \"well - 0094-trade.html - prose\", \"nodash\"]");
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
    let base = git(&root, &["rev-parse", "HEAD"]);
    commit(&root, "edits");
    let between = run(&root, &["--between", &base, "HEAD"]);
    assert!(between.stdout.contains("record-format:0094") && !between.stdout.contains("modal-"));
    assert_eq!(run(&root, &["--bogus"]).code, 2);
    assert_eq!(cli(&["--root".to_owned(), "/proc".to_owned()]).code, 1);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scratch record answered in order, each answer read back by the next"
)]
fn answers_are_recorded_and_refused_as_the_python_did() {
    let root = record("owed-answers");
    edit_everything(&root);
    assert_eq!(run(&root, &["--answer", "record-format"]).code, 2);
    assert!(run(
        &root,
        &["--answer", "record-format", "--result", "r", "--q", "94"]
    )
    .stderr
    .contains("REFUSED - a record-format answer without BUNDLE="));
    assert!(run(
        &root,
        &[
            "--answer",
            "record-format",
            "--result",
            "r",
            "--q",
            "94",
            "--reason",
            "x"
        ]
    )
    .stderr
    .contains("REASON needs two words"));
    let ok = run(
        &root,
        &[
            "--answer",
            "record-format",
            "--result",
            "3 of 3",
            "--q",
            "94",
            "--reason",
            "a stated reason",
        ],
    );
    assert!(
        ok.code == 0
            && ok
                .stdout
                .contains("record-checked: 1 unit(s) answered - record-format:0094")
    );
    assert!(std::fs::read_dir(root.join("dev/bypass-log"))
        .unwrap()
        .next()
        .is_some());
    assert_eq!(
        run(
            &root,
            &[
                "--answer",
                "intro-check",
                "--result",
                "r",
                "--q",
                "1",
                "--reason",
                "nothing owed here"
            ]
        )
        .code,
        3
    );
    let sr = run(
        &root,
        &[
            "--answer",
            "source-reader",
            "--result",
            "READ",
            "--q",
            "94",
            "--notes",
            "n",
            "--reply",
            &root.join("reply.md").to_string_lossy(),
        ],
    );
    assert_eq!(sr.code, 1);
    put(&root, "reply.md", "source-reader: 1\n\u{300c}more\u{300d} \u{300c}x\u{300d}\n## OUTSIDE THE CHANGE\n- `a.html` | b | c\n- no row\n# end\n");
    let sr = run(
        &root,
        &[
            "--answer",
            "source-reader",
            "--result",
            "READ",
            "--q",
            "94",
            "--notes",
            "n",
            "--reply",
            &root.join("reply.md").to_string_lossy(),
        ],
    );
    assert!(sr.stdout.contains("filed, not fixed - a.html | b | c") && sr.code == 0);
    let rec = read_answer(&store(&root), "source-reader:0094#n");
    assert!(
        rec.contains_key("passages")
            && rec.contains_key("reply_quotes")
            && rec.contains_key("readings")
    );
    let bundle = root.join("bundle");
    std::fs::create_dir_all(&bundle).unwrap();
    put(&root, "bundle/MANIFEST.md", &format!("unit: quote-check:0094#k ffffffffffffffff\nunit: cart yard:x 0123\nunit: record-format:0095 abc\npage: {} {}\n", "research/questions/0094-trade.html", "a".repeat(40)));
    let qc = run(
        &root,
        &[
            "--answer",
            "quote-check",
            "--result",
            "V",
            "--bundle",
            &bundle.to_string_lossy(),
        ],
    );
    assert!(qc.stdout.contains("quote-check:0094#k"));
    assert!(read_answer(&store(&root), "quote-check:0094#k").contains_key("qkeys") || qc.code == 0);
    assert_eq!(
        run(
            &root,
            &[
                "--answer",
                "quote-check",
                "--result",
                "V",
                "--bundle",
                "/nonexistent/b"
            ]
        )
        .code,
        3
    );
    let kind = run(
        &root,
        &[
            "--answer",
            "modal-research",
            "--result",
            "A",
            "--kind",
            "sheet/well,x",
            "--reason",
            "the pop-up checked",
        ],
    );
    assert!(kind.stdout.contains("modal-accuracy:sheet/well"));
    let key = run(
        &root,
        &[
            "--answer",
            "source-applicability",
            "--result",
            "FITS",
            "--key",
            "key-a",
            "--reason",
            "the key checked",
        ],
    );
    assert!(key.stdout.contains("source-applicability:key-a"));
    assert_eq!(
        run(
            &root,
            &[
                "--answer",
                "record-format",
                "--fixed-by",
                "x: y",
                "--result",
                "r"
            ]
        )
        .code,
        2
    );
    assert_eq!(
        run(
            &root,
            &[
                "--answer",
                "quote-check",
                "--fixed-by",
                "x: y",
                "--q",
                "94",
                "--notes",
                "nope"
            ]
        )
        .code,
        3
    );
    let fixed = run(
        &root,
        &[
            "--answer",
            "quote-check",
            "--fixed-by",
            "source-reader: locator",
            "--q",
            "94",
            "--notes",
            "n",
        ],
    );
    assert_eq!(fixed.code, 2);
    write_answer(&store(&root), "quote-check:0094#n", "old", "r", None).unwrap();
    let qk =
        super::answers::quotation_keys(&root, None, &["quote-check:0094#n".to_owned()]).unwrap();
    keep_reading(
        &store(&root),
        "quote-check:0094#n",
        &qk["quote-check:0094#n"],
        "qkeys",
    )
    .unwrap();
    let fixed = run(
        &root,
        &[
            "--answer",
            "quote-check",
            "--fixed-by",
            "source-reader: locator",
            "--q",
            "94",
            "--notes",
            "n",
        ],
    );
    assert!(fixed.code == 0 && fixed.stdout.contains("as another check's fix"));
    assert!(bundle_less_refusal("source-reader", "n", "").is_empty());
    let (done, refused) = fixed_answer(&root, "94", "zzz", "x").unwrap();
    assert!(done.is_empty() && refused.is_empty());
}

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
    assert!(file_outside(&root, "c", "no heading").unwrap().is_empty());
    assert_eq!(
        file_outside(&root, "c", "**OUTSIDE THE CHANGE**:\n- `f` | b | x\n")
            .unwrap()
            .len(),
        1
    );
    assert!(root.join("specs/_unfiled/found.jsonl").is_file());
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
    write_answer(&sib, &rf.slug, &rf.fingerprint, "elsewhere", None).unwrap();
    keep_reading(&sib, &rf.slug, "r9", "readings").unwrap();
    let left = unanswered(&root).unwrap();
    assert!(!left.iter().any(|u| u.slug == "record-format:0094"));
    assert!(read_answer(&store(&root), "record-format:0094").contains_key("readings"));
    put(&root, WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn square now.\nDrawing: research/questions/0094-trade.drawing.html\n");
    commit(&root, "the well redrawn");
    let now = modals::modals_now(&root, true).unwrap();
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
    assert!(!unanswered(&root).unwrap().iter().any(|u| u.slug == slug));
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
    let _ = s;
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
    let started = |root: &Path| super::entry_drift_owed(&mut Delta::new(root));
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
    let root = record("owed-env");
    assert_eq!(
        store_given(&root, Some("/x/y".into())),
        std::path::PathBuf::from("/x/y")
    );
    assert!(store_given(&root, Some("".into())).ends_with(".git/record-checks"));
    let base = crate::checks::scratch("owed-env-sib");
    let main = record_at(&base.join(".clones/main"));
    std::fs::create_dir_all(base.join(".clones/sib/.git/record-checks")).unwrap();
    std::fs::create_dir_all(base.join(".clones/bare")).unwrap();
    assert_eq!(siblings_given(&main, None).len(), 1);
    assert!(siblings_given(&main, Some("/t".into())).is_empty());
    assert_eq!(entry_base(&main), git(&main, &["rev-parse", "HEAD"]));
    git(&main, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert_eq!(entry_base(&main), git(&main, &["rev-parse", "HEAD"]));
    let empty = crate::checks::scratch("owed-env-empty");
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

#[test]
fn what_a_source_reader_read_is_kept_and_netted() {
    let root = record("owed-parts");
    edit_everything(&root);
    let s = store(&root);
    keep_parts(&s, "source-reader:0094#n", &root, "").unwrap();
    write_answer(&s, "source-reader:0094.drawing#d", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094.drawing#d", &root, "").unwrap();
    write_answer(&s, "source-reader:0094#t", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094#t", &root, "").unwrap();
    assert!(read_answer(&s, "source-reader:0094#t")["passages"]
        .as_array()
        .is_some_and(|a| !a.is_empty()));
    write_answer(&s, "source-reader:0094#gone", "f", "r", None).unwrap();
    keep_parts(&s, "source-reader:0094#gone", &root, "").unwrap();
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let n = rows
        .iter()
        .find(|u| u.slug == "source-reader:0094#n")
        .unwrap()
        .clone();
    write_answer(&s, &n.slug, "older", "READ", None).unwrap();
    keep_parts(&s, &n.slug, &root, "\u{300c}more\u{300d} \u{300c}x\u{300d}").unwrap();
    let qn = rows
        .iter()
        .find(|u| u.slug == "quote-check:0094#n")
        .unwrap()
        .clone();
    write_answer(&s, &qn.slug, &qn.fingerprint, "V", None).unwrap();
    assert!(!unanswered(&root).unwrap().iter().any(|u| u.slug == n.slug));
    let mut text =
        std::fs::read_to_string(root.join("research/questions/0094-trade.notes.html")).unwrap();
    text = text.replace(
        "\"new\" \u{300c}more\u{300d}",
        "\"new\" \u{300c}more\u{300d} \"newer\"",
    );
    put(&root, "research/questions/0094-trade.notes.html", &text);
    let rows = units(&root, None, None, &FAMILIES, "").unwrap();
    let qn = rows
        .iter()
        .find(|u| u.slug == "quote-check:0094#n")
        .unwrap()
        .clone();
    write_answer(&s, &qn.slug, &qn.fingerprint, "V", None).unwrap();
    assert!(unanswered(&root).unwrap().iter().any(|u| u.slug == n.slug));
    std::fs::remove_file(s.join("source-reader%3A0094%23n.json")).unwrap();
    write_answer(&s, &n.slug, "older", "READ", None).unwrap();
    assert!(unanswered(&root).unwrap().iter().any(|u| u.slug == n.slug));
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
    put(
        &root,
        "research/other/x.notes.html",
        "<li data-note=\"a\">\"q\" \u{300c}o\u{300d}</li>",
    );
    assert!(!run(&root, &["--slugs"]).stdout.contains("research/other"));
    let s = store(&root);
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
