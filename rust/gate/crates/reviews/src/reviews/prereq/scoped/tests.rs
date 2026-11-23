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
    // the reviewed sheet not kept (a verdict before T199)
    assert!(err(&fixed(&r, "N1")).contains("was not kept"));
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
