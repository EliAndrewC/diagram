//! A trial started (its number claimed in process, its brief written) and its one review bundled.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_guard::shared::checks::resolved;

use super::{brief, bundle, measurement_only, review_cli, start_cli};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

const TEMPLATE: &str = "# Trial [N]\n\n**Form**: trial\n**Created**: [DATE]\n**Approved**: the GM, [DATE], \"[his words, verbatim]\"\n";

#[test]
fn a_trial_claims_its_number_and_writes_its_brief() {
    let dir = scratch("trial-start");
    let m = resolved(&dir);
    let tree = m.join(".clones/t");
    std::fs::create_dir_all(&tree).unwrap();
    git(&tree, &["init", "-q"]);
    put(&tree, ".specify/templates/trial-template.md", TEMPLATE);
    put(&tree, "specs/440-old/spec.md", "x\n");
    let done = start_cli(&words(&["fewer-seats"]), &tree, " the \"GM\" said ");
    assert_eq!((done.code, done.stdout.as_str()), (0, "441-fewer-seats\n"));
    assert!(
        done.stderr
            .contains("claim-feature: claimed specs/441-fewer-seats/")
            && done.stderr.ends_with("one review when Done\n")
    );
    let spec = std::fs::read_to_string(tree.join("specs/441-fewer-seats/spec.md")).unwrap();
    assert!(
        spec.starts_with("# Trial 441\n")
            && spec.contains("\"the 'GM' said\"")
            && !spec.contains("[DATE]")
    );
    assert_eq!(
        std::fs::read_to_string(tree.join("specs/441-fewer-seats/request.md")).unwrap(),
        "# Feature 441 - the GM's request, verbatim\n\n> [the GM's words, verbatim]\n"
    );
    // no words given: the placeholder stays; a request already there is kept
    put(&tree, "specs/442-kept/request.md", "mine\n");
    let tmpl = tree.join(".specify/templates/trial-template.md");
    brief(&tree.join("specs/442-kept"), "2026-01-01", &tmpl, "  ").unwrap();
    assert!(std::fs::read_to_string(tree.join("specs/442-kept/spec.md"))
        .unwrap()
        .contains("[his words, verbatim]"));
    assert_eq!(
        std::fs::read_to_string(tree.join("specs/442-kept/request.md")).unwrap(),
        "mine\n"
    );
    assert!(brief(&tree.join("specs/x-bad"), "d", &tmpl, "")
        .unwrap_err()
        .contains("invalid literal"));
    assert!(brief(&tree.join("specs/443-none"), "d", &tmpl, "").is_err());
    // the slug refused by the claim: its refusal and exit
    let refused = start_cli(&words(&["Bad"]), &tree, "");
    assert_eq!((refused.code, refused.stdout.as_str()), (2, ""));
    assert!(refused.stderr.contains("REFUSED"));
    for bad in [&[][..], &[" "], &["a", "b"]] {
        assert_eq!(start_cli(&words(bad), &tree, "").code, 2);
    }
    // no template: the claim stands and the brief raised
    std::fs::remove_file(&tmpl).unwrap();
    let raised = start_cli(&words(&["no-template"]), &tree, "");
    assert_eq!(raised.code, 1);
    assert!(
        raised.stderr.contains("claimed specs/443-no-template/")
            && raised.stderr.contains("Traceback")
    );
}

fn trial(root: &Path, name: &str, status: &str) {
    put(
        root,
        &format!("specs/{name}/spec.md"),
        &format!("# T\n**Form**: trial\n**Status**: {status}\n"),
    );
    put(root, &format!("specs/{name}/request.md"), "words\n");
    put(root, &format!("specs/{name}/research/a.md"), "a\n");
    put(root, &format!("specs/{name}/research/b.json"), "{}\n");
    put(root, &format!("specs/{name}/research/c.txt"), "no\n");
}

#[test]
fn a_trial_review_bundles_the_brief_and_says_how_to_read_it() {
    let root = scratch("trial-review");
    let check = scratch("trial-review-out");
    trial(&root, "441-stopped", "Done - set down at the measurement");
    trial(&root, "447-spike", "Done; the spike lands");
    put(&root, "specs/450-plain/spec.md", "# an ordinary spec\n");
    put(&root, "specs/451-empty/notes.md", "x\n");
    put(&check, "trial-review-441/stale.md", "old\n");
    let review = |n: &str| review_cli(&words(&[n]), &root, &check);
    let stopped = review("441");
    assert_eq!(stopped.code, 0);
    assert!(
        stopped.stdout.contains("of trial 441-stopped")
            && stopped.stdout.contains("CHECK each figure")
    );
    let out = check.join("trial-review-441");
    assert!(
        !out.join("stale.md").exists()
            && out.join("research/b.json").is_file()
            && !out.join("research/c.txt").exists()
    );
    let manifest = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    assert!(manifest.ends_with(
        "## Files\n\n- `spec.md`\n- `request.md`\n- `research/a.md`\n- `research/b.json`\n"
    ));
    let spike = review(" 447 ");
    assert!(spike
        .stdout
        .ends_with("Its spike lands engine code: review it in full.\n"));
    assert!(
        std::fs::read_to_string(check.join("trial-review-447/MANIFEST.md"))
            .unwrap()
            .contains("re-running what you need")
    );
    for (n, says) in [
        ("450", "is no trial brief"),
        ("451", "is no trial brief"),
        ("9", "specs/009-* is no trial brief"),
        ("x", "F=<feature number>"),
        ("", "F="),
    ] {
        let r = review(n);
        assert_eq!(r.code, 2, "{n}");
        assert!(r.stderr.contains(says), "{n}: {}", r.stderr);
    }
    assert_eq!(review_cli(&[], &root, &check).code, 2);
    // a superscript passes `isdigit` and `int()` raised on it
    assert!(review("\u{b2}")
        .stderr
        .contains("invalid literal for int() with base 10: '\u{b2}'"));
    // a brief that is not UTF-8, and a bundle that cannot be made: both raise
    std::fs::write(root.join("specs/450-plain/spec.md"), [0xff]).unwrap();
    assert_eq!(review("450").code, 1);
    std::fs::remove_dir_all(check.join("trial-review-447")).unwrap();
    put(&check, "trial-review-447", "a file\n");
    assert_eq!(review("447").code, 1);
}

#[test]
fn the_bundle_s_own_failures() {
    let root = scratch("trial-bundle");
    trial(&root, "441-x", "Done");
    std::fs::create_dir_all(root.join("specs/441-x/research/dir.md")).unwrap();
    let out = scratch("trial-bundle-out");
    assert!(bundle(&root.join("specs/441-x"), &out.join("b"), true).is_err());
    std::os::unix::fs::symlink(&root, out.join("link")).unwrap();
    assert!(bundle(&root.join("specs/441-x"), &out.join("link"), true).is_err());
    put(&out, "blocked", "x\n");
    assert!(bundle(&root.join("specs/441-y"), &out.join("blocked/b"), true).is_err());
    std::fs::remove_dir_all(root.join("specs/441-x/research")).unwrap();
    std::fs::remove_file(root.join("specs/441-x/request.md")).unwrap();
    let only = bundle(&root.join("specs/441-x"), &out.join("c"), false).unwrap();
    assert!(std::fs::read_to_string(only)
        .unwrap()
        .ends_with("## Files\n\n- `spec.md`\n"));
}

#[test]
fn a_status_says_whether_the_measurement_stopped_it() {
    assert!(measurement_only(
        "x\n**Status**: Done - set down after the measurement\n"
    ));
    assert!(measurement_only(
        "**Status**: done, Stopped at the measurement\n"
    ));
    assert!(!measurement_only("**Status**: Done\n"));
    assert!(!measurement_only("**Status**: Open, set down\n"));
    assert!(!measurement_only("no status line\n"));
}
