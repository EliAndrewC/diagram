//! The census over scratch clones: the table the Python printed for the same files (feature 449 T136's differential fixture), each
//! raise the Python met, and the command line.

use std::fmt::Write as _;

use serde_json::json;

use super::super::tests::{dir, put};
use super::{census, cli, fixed, report, tally};

const HEAD: &str = "## Review checks, measured (feature 294 on)\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n";
const ROW: &str =
    "| 2026-10-04 | fix-check | well | PASS | x | geometric | - | - | 150 s | 250k in (1k cached) / 1k out |\n";

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

/// What `review_census.py --root` printed for these two files (observed 2026-11-12, HEAD 51b46a226).
#[test]
fn the_table_is_the_pythons_for_the_same_files() {
    let d = dir("census-table");
    put(
        &d,
        "dev/review-ledger-r0.json",
        r#"[{"agent": "size-audit", "runs": 2, "not_reviewable_runs": 1, "findings": {"geometric": 5, "judgment": "1_0"}, "author_missed_fixed": true, "wall_min": 1.5},
 {"runs": " 3 ", "findings": null, "wall_min": 2.5},
 {"agent": 7, "runs": 0, "findings": {}, "wall_min": 0.5}]"#,
    );
    put(
        &d,
        "dev/review-ledger.md",
        &format!(
            "{HEAD}| 2026-10-02 | glyph-check | privy | not-reviewable | reads | nothing | yes | - | 90 s | 3100k in (2900k cached) / 4.2k out |\n\
             | 2026-10-02 | glyph-check | privy | not-reviewable | second | judgment | no | - | 90 s | 3100k in (2900k cached) / 4.2k out |\r\n\
             | 2026-10-03 | size-audit | hall | PASS | x | odd | yes | - | about 5 | none |\n\
             | 2026-10-03 | short |\n{ROW}\n## after\n| 2026-10-05 | ignored | x | PASS | x | nothing | - | - | 9 s | 1k in |\n"
        ),
    );
    let got = cli(&args(&["--root", &d.to_string_lossy()]), &d.join("nowhere"));
    assert_eq!(
        (got.code, got.stdout.as_str(), got.stderr.as_str()),
        (
            0,
            "check | runs | not-reviewable | geometric | judgment | paperwork | nothing | author missed | wall (min) | tokens (M)\n\
             size-audit | 3 | 1 | 5 | 10 | 0 | 0 | 2 | 2 | 0.0\n\
             None | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0.0\n\
             glyph-check | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 2 | 3.1\n\
             fix-check | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0.2\n\
             7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0\n",
            ""
        )
    );
    // the default clone is the gate's tree; no r0 file (or a directory in its place) is no old rows
    std::fs::remove_file(d.join("dev/review-ledger-r0.json")).unwrap();
    std::fs::create_dir(d.join("dev/review-ledger-r0.json")).unwrap();
    let own = cli(&[], &d);
    assert!(own
        .stdout
        .ends_with("fix-check | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0.2\n"));
}

#[test]
fn each_raise_of_the_python_is_exit_one_and_nothing_printed() {
    let d = dir("census-raise");
    let raises = |r0: Option<&str>, ledger: Option<&str>| {
        let _ = std::fs::remove_file(d.join("dev/review-ledger-r0.json"));
        let _ = std::fs::remove_file(d.join("dev/review-ledger.md"));
        if let Some(r0) = r0 {
            put(&d, "dev/review-ledger-r0.json", r0);
        }
        if let Some(l) = ledger {
            put(&d, "dev/review-ledger.md", l);
        }
        let got = cli(&args(&["--root", &d.to_string_lossy()]), &d);
        (
            got.code,
            got.stdout.is_empty(),
            got.stderr
                .starts_with("Traceback (most recent call last):\n  l7r-gate reviews census\n"),
        )
    };
    let good = format!("{HEAD}{ROW}");
    for r0 in [
        "not json",
        "3",
        "null",
        "{\"a\": 1}",
        "\"s\"",
        "[1]",
        "[{\"findings\": [1]}]",
        "[{\"runs\": \"abc\"}]",
        "[{\"runs\": [1]}]",
    ] {
        assert_eq!(raises(Some(r0), Some(&good)), (1, true, true), "{r0}");
    }
    assert_eq!(raises(None, None), (1, true, true));
    std::fs::write(d.join("dev/review-ledger-r0.json"), [0xff_u8]).unwrap();
    put(&d, "dev/review-ledger.md", &good);
    assert!(census(&d).is_err());
    std::fs::remove_file(d.join("dev/review-ledger-r0.json")).unwrap();
    std::fs::write(d.join("dev/review-ledger.md"), [0xff_u8]).unwrap();
    assert!(census(&d).is_err());
    // an empty wall cell: `"".split()[0]`
    let empty_wall = format!(
        "{HEAD}| 2026-10-04 | fix-check | well | PASS | x | geometric | - | - |  | 1k in |\n"
    );
    assert_eq!(raises(None, Some(&empty_wall)), (1, true, true));
    // what is not a raise: an empty object or string walks no rows, a falsy figure is zero
    for r0 in [
        "{}",
        "\"\"",
        "[{\"runs\": \"\", \"findings\": 0, \"wall_min\": [], \"not_reviewable_runs\": {}}]",
    ] {
        assert_eq!(raises(Some(r0), Some(&good)).0, 0, "{r0}");
    }
}

/// Python's `isdigit` and `\d` take any script's decimal digits, and `float()` reads them (the Python's output for these rows, observed
/// 2026-11-12); a fraction is no digit.
#[test]
fn any_scripts_decimal_digits_are_read_as_python_reads_them() {
    let d = dir("census-digits");
    let mut ledger = HEAD.to_owned();
    for (s, w, k) in [
        ("a", "\u{662}\u{660} s", "\u{663}k in"),
        ("b", "\u{1d7d7}\u{1d7ce} s", "x"),
        ("c", "90s", "12k in"),
        ("d", "\u{bd} s", "\u{661}\u{660}\u{660}k in"),
    ] {
        let _ = writeln!(
            ledger,
            "| 2026-10-02 | glyph-check | {s} | PASS | f | nothing | - | - | {w} | {k} |"
        );
    }
    put(&d, "dev/review-ledger.md", &ledger);
    assert_eq!(
        census(&d).unwrap(),
        "check | runs | not-reviewable | geometric | judgment | paperwork | nothing | author missed | wall (min) | tokens (M)\n\
         glyph-check | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 2 | 0.1"
    );
}

#[test]
fn the_figures_are_printed_as_pythons_format_prints_them() {
    assert_eq!(fixed(0.5, 0), "0");
    assert_eq!(fixed(1.5, 0), "2");
    assert_eq!(fixed(2.5, 0), "2");
    assert_eq!(fixed(-0.3, 0), "-0");
    assert_eq!(fixed(0.25, 1), "0.2");
    assert_eq!(fixed(f64::NAN, 0), "nan");
    assert_eq!(fixed(f64::INFINITY, 0), "inf");
    // a NaN run count sorts beside the others rather than refusing
    let t = tally(
        &json!([{"agent": "a", "runs": "nan"}, {"agent": "b", "runs": 1}]),
        "",
    )
    .unwrap();
    assert!(report(&t).contains("\na | nan |"));
}

#[test]
fn a_bad_command_line_is_argparses_exit_two() {
    let got = cli(&args(&["--bogus"]), std::path::Path::new("."));
    assert_eq!((got.code, got.stdout.as_str()), (2, ""));
    assert!(got.stderr.contains("usage: l7r-gate reviews census"));
    assert_eq!(super::super::cli(&args(&["census", "--bogus"])).code, 2);
}
