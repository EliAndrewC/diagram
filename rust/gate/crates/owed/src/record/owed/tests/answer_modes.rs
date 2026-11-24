//! The answer modes of `record record-owed` on a scratch record, refused and recorded as the Python did: one test of fifteen answers in
//! order until feature 449 T164 split it at the answers that read nothing the earlier ones wrote (FR-008's tenth of a second), and moved
//! the parts here from `tests.rs`, which they took past the 1,000-line bar.

use super::super::answers::{
    bundle_less_refusal, fixed_answer, keep_reading, read_answer, store, write_answer,
};
use super::run;
use crate::record::testkit::{edit_everything, put, record};

/// The answer modes, refused and recorded as the Python did. One scratch record answered fifteen times in order took 306 ms; it is
/// split at the answers that read nothing the earlier ones wrote, each part on a record of its own (feature 449 T164, FR-008's
/// tenth of a second): a record-format answer is refused without its result, a bundle or a reason, recorded with them, and an
/// answer matching no owed unit records nothing.
#[test]
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
}

/// A source-reader answer needs its reply, keeps what it read and quoted, and files what the reply found outside the change.
#[test]
fn a_source_reader_answer_keeps_its_reply_and_files_what_is_outside_the_change() {
    let root = record("owed-answers-reader");
    edit_everything(&root);
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
    put(&root, "reply.md", "source-reader: 1\n\u{300c}more\u{300d} \u{300c}x\u{300d}\n## OUTSIDE THE CHANGE\n- `a.html` | b | c | effect: page - d\n- no row\n# end\n");
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
    assert!(
        sr.stdout
            .contains("filed, not fixed - a.html | b | c | effect: page - d")
            && sr.code == 0
    );
    let rec = read_answer(&store(&root), "source-reader:0094#n");
    assert!(
        rec.contains_key("passages")
            && rec.contains_key("reply_quotes")
            && rec.contains_key("readings")
    );
}

/// An answer with a bundle answers the units its manifest names, and a bundle that is not there answers none.
#[test]
fn a_bundle_answers_the_units_its_manifest_names() {
    let root = record("owed-answers-bundle");
    edit_everything(&root);
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
}

/// A modal check's answer names its kinds, a write-up check's its key.
#[test]
fn a_kind_or_a_key_answers_its_own_units() {
    let root = record("owed-answers-kind");
    edit_everything(&root);
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
}

/// A fix by another check's finding is a quote-check's alone, and on notes owed one.
#[test]
fn a_fix_by_another_check_is_a_quote_check_s_on_notes_owed_one() {
    let root = record("owed-answers-fixed");
    edit_everything(&root);
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
}

/// A fix by another check's finding is refused while the quotation's keys were never kept.
#[test]
fn a_fix_by_another_check_is_refused_while_no_quotation_key_was_kept() {
    let root = record("owed-answers-fixed-refused");
    edit_everything(&root);
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
}

/// A fix by another check's finding answers its quote-check once the quotation's keys were kept.
#[test]
fn a_fix_by_another_check_answers_once_the_quotation_s_keys_are_kept() {
    let root = record("owed-answers-fixed-kept");
    edit_everything(&root);
    write_answer(&store(&root), "quote-check:0094#n", "old", "r", None).unwrap();
    let qk = super::super::answers::quotation_keys(&root, None, &["quote-check:0094#n".to_owned()])
        .unwrap();
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
}

/// A note owed no quote-check answers none and refuses none, and a source-reader's answer on notes needs no bundle.
#[test]
fn a_fix_on_a_note_owed_nothing_answers_none() {
    let root = record("owed-answers-fixed-none");
    edit_everything(&root);
    assert!(bundle_less_refusal("source-reader", "n", "").is_empty());
    let (done, refused) = fixed_answer(&root, "94", "zzz", "x").unwrap();
    assert!(done.is_empty() && refused.is_empty());
}
