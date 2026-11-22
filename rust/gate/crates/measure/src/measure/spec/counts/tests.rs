//! The two rewritten one-liners: what they count, and the Python's raise on a missing or unreadable file.

use super::{open_rows, registered_guards};

fn ran(
    f: fn(&std::path::Path, &mut String) -> super::Ran,
    root: &std::path::Path,
) -> (Result<i32, String>, String) {
    let mut out = String::new();
    let r = f(root, &mut out);
    (r, out)
}

#[test]
fn the_open_rows_are_those_no_wave_took_and_not_deferred() {
    let dir = crate::checks::scratch("spec-open-rows");
    l7r_gate_core::record::testkit::put(
        &dir,
        "specs/328-match-the-research/ranking.json",
        r#"[{"tier": "E3", "verdict": "DRIFTED"}, {"tier": "E3", "verdict": "DRIFTED", "wave": 0},
            {"tier": "E3", "verdict": "DRIFTED", "wave": 12}, {"tier": "E3", "verdict": "IN-STEP"},
            {"tier": "E1", "verdict": "DRIFTED", "wave": ""}, {"tier": "E3", "verdict": "DRIFTED", "scope": "deferred"},
            {"tier": "E3", "verdict": "DRIFTED", "scope": "local"}]"#,
    );
    assert_eq!(
        ran(open_rows, &dir),
        (Ok(0), "5 open, 3 E3 DRIFTED\n".to_owned())
    );
    l7r_gate_core::record::testkit::put(&dir, "specs/328-match-the-research/ranking.json", "{}");
    assert!(ran(open_rows, &dir).0.unwrap_err().starts_with("TypeError"));
    l7r_gate_core::record::testkit::put(&dir, "specs/328-match-the-research/ranking.json", "[");
    assert!(ran(open_rows, &dir)
        .0
        .unwrap_err()
        .starts_with("JSONDecodeError"));
}

#[test]
fn the_registered_guards_are_the_distinct_hook_files_named() {
    let dir = crate::checks::scratch("spec-guards");
    assert!(ran(registered_guards, &dir)
        .0
        .unwrap_err()
        .starts_with("OSError"));
    l7r_gate_core::record::testkit::put(
        &dir,
        ".claude/settings.json",
        r#"{"hooks": {"PreToolUse": [{"hooks": [{"command": "bash scripts/hooks/plan-gate-hooks.sh; x"},
              {"command": "bash scripts/hooks/a-hooks.sh b-hooks.sh"}, {"command": "scripts/hooks/l7r-guard.sh"}, {}]},
            {"matcher": "Bash"}],
            "Stop": [{"hooks": [{"command": "scripts/hooks/plan-gate-hooks.sh"}]}], "Odd": {}}}"#,
    );
    assert_eq!(ran(registered_guards, &dir), (Ok(0), "2\n".to_owned()));
    l7r_gate_core::record::testkit::put(&dir, ".claude/settings.json", "{}");
    assert_eq!(ran(registered_guards, &dir), (Ok(0), "0\n".to_owned()));
}
