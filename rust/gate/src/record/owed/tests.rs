//! The owed listing, its answers and the seams, on a scratch record.

use std::path::Path;

use serde_json::{json, Value};

use super::answers::{
    amendment1_depiction_answered, answer, answered, bundle_less_refusal, file_outside,
    fixed_answer, keep_reading, legacy_depiction_answered, read_answer, reply_checks, settle,
    store, unanswered, write_answer, Named,
};
use super::answers::{keep_parts, siblings_given, store_given};
use super::{cli, entry_base, entry_units, read_at, units, FAMILIES};
use crate::record::modals;
use crate::record::testkit::{commit, edit_everything, git, put, record, record_at, stubs, WELL};

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
    put(&root, "entry-lines.json", "[\"notakind - 0094-trade.html 0094-trade.drawing.html x.html - prose at x\\n      read: a\", \"blank - 0095-other.html - prose\", \"well - 0094-trade.html - prose\", \"nodash\"]");
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
        "make check-bundle Q=0095 FOR=entry-drift KIND=\"Blank\"",
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
fn the_entry_drift_seam() {
    let root = record("owed-entry");
    let now = read_at(&root, None, None).unwrap();
    put(
        &root,
        "entry-lines.json",
        "[\"cart yard - 0094-trade.html - prose\"]",
    );
    let got = entry_units(&root, &now).unwrap();
    assert_eq!(got[0].slug, "entry-drift:cart yard");
    put(&root, "entry-raise", "");
    assert!(entry_units(&root, &now).is_err());
    put(&root, "entry-lines.json", "not json");
    std::fs::remove_file(root.join("entry-raise")).unwrap();
    assert!(entry_units(&root, &now).is_err());
    assert!(units(&root, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
    std::fs::remove_file(root.join("l7r/diagram/interactive/classes/__init__.py")).unwrap();
    assert!(units(&root, None, None, &["entry-drift"], "").is_err());
    let fresh = crate::checks::scratch("owed-entry-empty");
    git(&fresh, &["init", "-q"]);
    assert!(units(&fresh, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
}

#[test]
fn a_file_entry_owed_reads_starts_it_with_no_page_changed() {
    let root = record("owed-entry-reads");
    put(&root, "entry-raise", "");
    // nothing it reads changed: not started, so its failure is not seen
    assert!(units(&root, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
    // a registry it reads, edited in the working tree: started, and the broken engine fails as the Python's did
    put(
        &root,
        "l7r/diagram/interactive/classes/homestead.py",
        "class Well(Kind):\n    key = \"well\"\n",
    );
    assert!(units(&root, None, None, &["entry-drift"], "").is_err());
    git(
        &root,
        &[
            "checkout",
            "--",
            "l7r/diagram/interactive/classes/homestead.py",
        ],
    );
    // a new file in its import closure, untracked: started too
    put(&root, "l7r/diagram/interactive/sources.py", "");
    assert!(units(&root, None, None, &["entry-drift"], "").is_err());
    std::fs::remove_file(root.join("l7r/diagram/interactive/sources.py")).unwrap();
    // a file elsewhere in the record it reads (a write-up's data): started
    put(&root, "research/tags.json", "{}\n");
    assert!(units(&root, None, None, &["entry-drift"], "").is_err());
    std::fs::remove_file(root.join("research/tags.json")).unwrap();
    // a file it never reads, alone: not started
    put(&root, "docs/notes.md", "x\n");
    assert!(units(&root, None, None, &["entry-drift"], "")
        .unwrap()
        .is_empty());
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
    stubs(&root);
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
    let now = read_at(&rec, None, None).unwrap();
    put(&rec, "entry-noise", "");
    assert!(entry_units(&rec, &now).is_err());
    put(
        &rec,
        "scripts/record/apply_edits.py",
        "print('noise')\ndef reply_of(p):\n    return ''\n",
    );
    put(&rec, "r.md", "x");
    assert!(super::answers::reply_of(&rec, &rec.join("r.md").to_string_lossy()).is_err());
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
    let barn = modals::find(&now, "hamlet/barn").unwrap();
    let slug = "modal-depiction:hamlet/barn";
    let rec = json!({"answered": [modals::legacy_depiction_fingerprint(&root, barn).unwrap()], "utc": "2099-01-01T00:00:00Z"});
    std::fs::write(
        s.join("modal-depiction%3Ahamlet%2Fbarn.json"),
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
