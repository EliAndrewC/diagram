//! A nitpick fixed on the sheet owes a change-scoped round, not a full one (451 T199), on a scratch repository.

use std::path::Path;

use serde_json::{json, Value};

use super::super::super::tests::{put, repo, sheet};
use super::super::stands::standing;
use super::super::{answered, cli, unit_content_key, Reply};

const U: &str = "building-review--s";
const SVG: &str = "legacy-hand-authored-pool/compounds/s/s.svg";

fn run_in(root: &Path, a: &[&str]) -> Reply {
    let mut all: Vec<String> = a.iter().map(|s| (*s).to_owned()).collect();
    all.extend(["--clone".to_owned(), root.to_string_lossy().into_owned()]);
    cli(&all)
}

/// The full round's verdict, recorded as a reviewer records it (so the sheet it read is kept).
fn full_round(r: &Path, verdict: &str, findings: &Value) {
    put(r, ".git/f.json", &findings.to_string());
    let f = r.join(".git/f.json").to_string_lossy().into_owned();
    let said = run_in(
        r,
        &[
            "verdict",
            "--unit",
            U,
            "--verdict",
            verdict,
            "--findings-file",
            &f,
        ],
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
}

fn scoped_round(r: &Path, verdict: &str, findings: &Value) -> Reply {
    put(r, ".git/g.json", &findings.to_string());
    let f = r.join(".git/g.json").to_string_lossy().into_owned();
    run_in(
        r,
        &[
            "verdict",
            "--unit",
            U,
            "--verdict",
            verdict,
            "--findings-file",
            &f,
            "--scope",
            "change",
        ],
    )
}

fn fixed(r: &Path, ids: &str) -> Reply {
    run_in(r, &["fixed", "--unit", U, "--finding", ids])
}

/// RED FIRST (451 T199): a NEEDS-WORK whose one open finding is a nitpick, fixed on the sheet. Before T199 the edit moved the content
/// key and the verdict no longer answered: a full round owed. Now a clean change-scoped round of the edit alone carries it, and the
/// push's review gate's `reviews prereq answered` and `make verify`'s `standing` accept it.
#[test]
fn a_nitpick_fixed_on_the_sheet_is_carried_by_a_clean_change_scoped_round() {
    let r = repo("scoped");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "K0"}"#,
    );
    put(&r, ".git/green", "");
    let findings = json!([{"id": "N1", "severity": "nitpick", "what": "the label reads 'kura' for 'kura (storehouse)'"},
        {"id": "O1", "severity": "outside"}]);
    full_round(&r, "NEEDS-WORK", &findings);
    let reviewed = unit_content_key(&r, U);
    assert!(answered(&r, U, ""));
    // the nitpick fixed on the sheet: the content key moves, the verdict no longer answers (a full round, before T199)
    put(
        &r,
        SVG,
        "<svg><g data-kind=\"gate\"/>\n<text>kura (storehouse)</text></svg>",
    );
    assert_ne!(unit_content_key(&r, U), reviewed);
    assert!(!answered(&r, U, ""));

    let said = fixed(&r, "N1");
    assert_eq!(said.code, 0, "{}", said.stderr);
    let out = said.stdout;
    assert!(out.starts_with("declared: building-review--s's"), "{out}");
    let prompt =
        std::fs::read_to_string(r.join(".git/review-scoped").join(U).join("prompt.md")).unwrap();
    assert!(prompt.contains("- N1: the label reads"), "{prompt}");
    let paired = prompt.contains("before:\n```\n<svg><g data-kind=\"gate\"/></svg>\n```\nafter:");
    assert!(paired, "{prompt}");
    assert!(prompt.contains("SCOPE=change"), "{prompt}");

    // a clean scoped round carries the verdict to the sheet as edited
    let said = scoped_round(&r, "PASS", &json!([{"id": "S1", "severity": "nitpick"}]));
    assert_eq!(said.code, 0, "{}", said.stderr);
    let out = said.stdout;
    assert!(out.contains("the verdict carries"), "{out}");
    assert!(answered(&r, U, ""));
    assert_eq!(standing(&r, U), format!("{U}\n"));
    // the declaration is spent
    assert_eq!(scoped_round(&r, "PASS", &json!([])).code, 1);
    // another edit moves the sheet past the scoped round's key: owed again
    put(&r, SVG, "<svg>moved</svg>");
    assert!(!answered(&r, U, ""));
}

/// An error or questionable fix owes the full round; so does a scoped round that is not clean, a stale declaration, and a verdict
/// whose reviewed sheet was not kept.
#[test]
fn an_error_fix_or_an_unclean_scoped_round_owes_the_full_round() {
    let r = repo("scoped-refused");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "K0"}"#,
    );
    put(&r, ".git/green", "");
    let err = |x: &Reply| x.stderr.clone();
    // no verdict at all
    assert!(err(&fixed(&r, "N1")).contains("no PASS or NEEDS-WORK verdict"));
    full_round(
        &r,
        "NEEDS-WORK",
        &json!([{"id": "E1", "severity": "error"}, {"id": "N1", "severity": "nitpick"},
        {"id": "C1", "severity": "confirmation"}]),
    );
    assert!(err(&fixed(&r, "")).contains("names the nitpicks"));
    assert!(err(&fixed(&r, "Z9")).contains("raised no finding Z9"));
    assert!(err(&fixed(&r, "E1")).contains("`error` finding, not a nitpick"));
    // the open error owes the full round even when only the nitpick is named
    assert!(err(&fixed(&r, "N1")).contains("E1, a `error` finding, is open"));
    // left by `make review-accept`, it no longer does; but an unchanged sheet has nothing to scope
    put(
        &r,
        ".git/review-dispositions/building-review--s.json",
        &json!({"accepted": [{"finding": "E1", "round": "K0", "reason": "left on purpose"}]})
            .to_string(),
    );
    assert!(err(&fixed(&r, "N1")).contains("hashes as its review read it"));
    put(&r, SVG, "<svg>fixed</svg>");
    // the prompt cannot be written: refused, naming where
    put(&r, ".git/review-scoped", "a file in the way");
    assert!(err(&fixed(&r, "N1")).contains("review-scoped"));
    std::fs::remove_file(r.join(".git/review-scoped")).unwrap();
    assert_eq!(fixed(&r, "N1").code, 0);
    // a scoped round with an error, or a NEEDS-WORK, is recorded and carries nothing
    let said = scoped_round(&r, "PASS", &json!([{"id": "S1", "severity": "error"}]));
    assert!(said.stdout.contains("not clean"), "{}", said.stdout);
    assert!(!answered(&r, U, ""));
    assert_eq!(fixed(&r, "N1").code, 0);
    assert!(scoped_round(&r, "NEEDS-WORK", &json!([]))
        .stdout
        .contains("not clean"));
    assert!(!answered(&r, U, ""));
    // the sheet moved after the declaration
    assert_eq!(fixed(&r, "N1").code, 0);
    put(&r, SVG, "<svg>again</svg>");
    assert!(err(&scoped_round(&r, "PASS", &json!([]))).contains("moved since the declaration"));
    // the verdict written again since the declaration
    full_round(&r, "PASS", &json!([{"id": "N1", "severity": "nitpick"}]));
    put(&r, SVG, "<svg>third</svg>");
    assert_eq!(fixed(&r, "N1").code, 0);
    let v = r.join(".git/review-verdicts").join(format!("{U}.json"));
    let mut rec: Value = serde_json::from_str(&std::fs::read_to_string(&v).unwrap()).unwrap();
    rec["content_key"] = json!("0000000000000000");
    std::fs::write(&v, rec.to_string()).unwrap();
    assert!(err(&scoped_round(&r, "PASS", &json!([]))).contains("written again since"));
    // the reviewed sheet not kept (a verdict before T199), and no version in history hashes as it did
    let said = err(&fixed(&r, "N1"));
    assert!(said.contains("nor in git history"), "{said}");
    // no declaration, and no verdict
    std::fs::remove_dir_all(r.join(".git/review-scoped")).unwrap();
    assert!(err(&scoped_round(&r, "PASS", &json!([]))).contains("no change-scoped round declared"));
    put(
        &r,
        ".git/review-scoped/building-review--s/declared.json",
        "{}",
    );
    std::fs::remove_file(&v).unwrap();
    assert!(
        err(&scoped_round(&r, "PASS", &json!([]))).contains("no verdict for a change-scoped round")
    );
}

const NOTES: &str = "legacy-hand-authored-pool/compounds/s/s.notes.md";

/// RED FIRST (451 T214): the cascade test's round-trip sheet. Its review was written while the sheet was owed and before T199 kept the
/// sheet it read; the delta landed, and a later delta fixed the review's nitpick in the notes alone. `reviews owed` (so `make verify`
/// and `reviews snapshot`) and the push's review gate owe nothing - a notes edit is no occasion - but `make review-fixed` refused,
/// naming a full round owed. Now it says what they say: nothing is owed, under the sheet's name as under its unit's.
#[test]
fn a_notes_fix_on_a_sheet_no_delta_owes_is_owed_no_round_by_any_tool() {
    let r = repo("scoped-unowed");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    put(&r, NOTES, "# s\n\nThe study at the west end.\n");
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "K0"}"#,
    );
    put(&r, ".git/green", "");
    full_round(
        &r,
        "PASS",
        &json!([{"id": "N1", "severity": "nitpick", "what": "the west end is superseded"}]),
    );
    // a verdict before T199: no kept sheet
    std::fs::remove_dir_all(super::kept_dir(&r, U)).unwrap();
    // the delta landed: main is at it, and the sheet is owed nothing
    super::super::super::tests::commit(&r, "the sheet");
    let head = super::super::super::git(&r, &["rev-parse", "HEAD"]).unwrap();
    put(&r, ".git/refs/remotes/origin/main", &format!("{head}\n"));
    put(
        &r,
        NOTES,
        "# s\n\nThe study at the west end (superseded: the east end).\n",
    );
    assert!(super::super::super::owed::owed(&r, true).1.is_empty());
    // the snapshot the review's `make verify` took, left behind: it is no delta's, and owes nothing
    let snap = format!(".git/review-snapshot/{U}");
    put(
        &r,
        &format!("{snap}/tree.json"),
        r#"{"commit": "c0", "key": "K0", "tree": "/x", "on": "s"}"#,
    );
    put(
        &r,
        &format!("{snap}/clone/s.notes.md"),
        "# s\n\nThe study at the west end.\n",
    );
    for unit in [U, "s"] {
        let said = run_in(&r, &["fixed", "--unit", unit, "--finding", "N1"]);
        let (code, out) = (said.code, format!("{}{}", said.stdout, said.stderr));
        assert_eq!(code, 0, "{out}");
        let head = out.starts_with("building-review--s is not owed by this delta");
        assert!(head, "{out}");
        let full = out.contains("full round is owed");
        assert!(out.contains("no round is owed") && !full, "{out}");
    }
    // a name no pool sheet answers is refused as that, never read as not owed
    let said = run_in(&r, &["fixed", "--unit", "nowhere", "--finding", "N1"]);
    assert_eq!(said.code, 1);
    assert!(
        said.stderr.contains("no pool sheet `nowhere`"),
        "{}",
        said.stderr
    );
}

/// RED FIRST (451 T214): a sheet still owed whose verdict was written before T199 kept the sheet its review read. The sheet as reviewed
/// is found again in git history - each tracked version of its drawing and notes, and the drawing as it reads now (a generated
/// compound's drawing is never tracked), hashed as the verdict's content key hashes them - so the change-scoped round is written; where
/// no version hashes so, the full round is owed, saying why.
#[test]
fn a_verdict_written_before_its_sheet_was_kept_is_paired_from_git_history() {
    let r = repo("scoped-history");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    put(&r, NOTES, "# s\n\nThe study at the west end.\n");
    // committed, but main has not landed it: the sheet is new to the pool, so owed
    super::super::super::tests::commit(&r, "the sheet");
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "K0"}"#,
    );
    put(&r, ".git/green", "");
    full_round(
        &r,
        "NEEDS-WORK",
        &json!([{"id": "N1", "severity": "nitpick", "what": "the west end is superseded"}]),
    );
    std::fs::remove_dir_all(super::kept_dir(&r, U)).unwrap();
    put(&r, NOTES, "# s\n\nThe study at the east end.\n");
    let said = fixed(&r, "N1");
    assert_eq!(said.code, 0, "{}", said.stderr);
    let prompt =
        std::fs::read_to_string(r.join(".git/review-scoped").join(U).join("prompt.md")).unwrap();
    assert!(prompt.contains("before:\n```\nThe study at the west end.\n```\nafter:\n```\nThe study at the east end.\n```"), "{prompt}");
    // the recovered sheet is kept, so the next declaration reads it directly
    assert!(super::kept_dir(&r, U).join("s.notes.md").is_file());

    // a verdict written over an edit never committed: no version in history hashes as it did
    put(&r, NOTES, "# s\n\nAn uncommitted wording.\n");
    full_round(&r, "PASS", &json!([{"id": "N1", "severity": "nitpick"}]));
    std::fs::remove_dir_all(super::kept_dir(&r, U)).unwrap();
    put(&r, NOTES, "# s\n\nAnother wording.\n");
    let said = fixed(&r, "N1");
    assert_eq!(said.code, 1);
    assert!(
        said.stderr.contains("nor in git history"),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr.contains("a full round is owed"),
        "{}",
        said.stderr
    );
}
