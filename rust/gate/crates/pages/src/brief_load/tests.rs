//! The write cap's count over the real briefs `brief_load.py`'s tests held (`tests/tooling/fixtures/brief_load/`), each line what the
//! Python printed for it (observed 2026-11-14, `brief_load.py record <brief>` at HEAD), and over scratch briefs for every other branch.

use std::path::{Path, PathBuf};

use super::{cli, count, declared, refusal, split_names, stems};

fn fixtures() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../tests/tooling/fixtures/brief_load")
}

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn the_real_briefs_count_as_the_python_counted_them() {
    let f = fixtures();
    let at = |n: &str| f.join(n).to_string_lossy().into_owned();
    let record = at("record");
    let ok = cli(&args(&[
        &record,
        &at("g1-check-a.md"),
        &at("h1-check-a.md"),
        &at("owed-buildings-1.md"),
    ]));
    assert_eq!(
        (ok.code, ok.stdout.as_str()),
        (
            0,
            "write 2 g1-check-a.md: 0040, 0041\nwrite 2 h1-check-a.md: 0042, 0043\ncheck 6 owed-buildings-1.md: 0044, 0045, 0046, 0047, 0048, 0049\n"
        )
    );
    let v2 = cli(&args(&[&record, &at("v2-write.md")]));
    assert_eq!(v2.code, 1);
    assert_eq!(
        v2.stdout,
        "write 9 v2-write.md: 0010, 0011, 0012, 0013, 0014, 0015, 0016, 0017, B30\n  REFUSED: it assigns 9 questions (0010, 0011, 0012, 0013, 0014, \
         0015, 0016, 0017, B30); a write session takes at most 4 (feature 274: a write session's cost grows with the square of its length). \
         Split it into 3 briefs of at most 4 - v2a-write.md, v2b-write.md, v2c-write.md - each with its own handoff, and queue them one \
         after another; or, for a deliberate larger load, set WRITE_CAP_OK='<reason>'\n"
    );
    let s = cli(&args(&[&record, &at("s-write.md")]));
    assert!(s
        .stdout
        .starts_with("write 8 s-write.md: FR-001, D50, D51, A133, A135, D49, D52, D56\n"));
    assert!(s.stdout.ends_with(
        ". The lines counted as FR-001 name no question and lead with no item id; if they are the parts of one question, nest them as \
         indented sub-bullets under one `- B1 ...` line naming it (`NNNN` in backticks)\n"
    ));
    for (brief, line) in [
        (
            "c1-write.md",
            "write 6 c1-write.md: 0020, 0021, 0022, 0023, 0024, 0025\n",
        ),
        (
            "x1-write.md",
            "write 10 x1-write.md: 0030, 0031, 0032, 0033, 0034, 0035, 0036, 0037, 0038, 0039\n",
        ),
    ] {
        assert!(cli(&args(&[&record, &at(brief)])).stdout.starts_with(line));
    }
}

#[test]
fn the_record_s_stems_are_read_from_its_files() {
    let d = l7r_gate_core::ci::fixtures::scratch("brief-stems");
    let q = d.join("questions");
    std::fs::create_dir_all(&q).unwrap();
    for name in [
        "0094-a.html",
        "0095-b.drawing.html",
        "0096-c.notes.html",
        "0097-.html",
        "009x-d.html",
        "0098_e.html",
        "0099-f.txt",
        "12-g.html",
    ] {
        std::fs::write(q.join(name), "").unwrap();
    }
    assert_eq!(stems(&d).into_iter().collect::<Vec<_>>(), [94, 95]);
    assert!(stems(Path::new("/no/such/record")).is_empty());
}

#[test]
fn what_a_brief_assigns_and_declares() {
    let d = l7r_gate_core::ci::fixtures::scratch("brief-count");
    std::fs::create_dir_all(d.join("questions")).unwrap();
    for n in ["0001", "0002", "0003", "0005"] {
        std::fs::write(d.join(format!("questions/{n}-q.html")), "").unwrap();
    }
    let blocks = "intro\n**Your questions:** Q=0001, 0002\nKIND=x (Q=0007)\n\nQ=0009 outside\n**Your pairs**\nQ=0003\n# heading\nQ=0008\n";
    let (n, detail) = count(blocks, &d).unwrap();
    assert_eq!((n, detail), (4, args(&["0001", "0002", "0003", "0007"])));
    let numbered = "**Your questions:** Q=0001\n1. ends the block Q=0002\n";
    assert_eq!(count(numbered, &d).unwrap().0, 1);
    let items = "## Your items\n- `0001`, `0005` and `file.py:0002` and fc:0003\n  continued `0003`\n- A133 A135, D49 D52-D56 then B16's finding\n\
                 - A133 again\n- **Bold** words lead\n- Q=0002 in a line\nnot an item\n## Next\n- `0003`\n";
    let (n, detail) = count(items, &d).unwrap();
    assert_eq!(
        (n, detail),
        (
            11,
            args(&[
                "0001", "0002", "0003", "0005", "A133", "A135", "D49", "D52", "D56", "A133",
                "**Bold**"
            ])
        )
    );
    assert_eq!(
        count("## Your items\n- \n", &d).unwrap_err(),
        "IndexError: list index out of range"
    );
    assert_eq!(declared("x <!-- page-load: kind=check --> y"), "check");
    assert_eq!(declared("none"), "");
}

#[test]
fn a_refusal_says_why_and_how_to_split() {
    let d = l7r_gate_core::ci::fixtures::scratch("brief-refusal");
    let b = Path::new("g.md");
    assert_eq!(
        refusal(b, "<!-- page-load: kind=split -->", &d).unwrap(),
        ""
    );
    assert_eq!(
        refusal(b, "<!-- page-load: kind=odd -->", &d).unwrap(),
        "it declares kind=odd, which is not an exempt kind (check, assertions, split, handover)"
    );
    assert!(refusal(b, "nothing", &d)
        .unwrap()
        .ends_with("add `<!-- page-load: kind=<check|assertions|split|handover> -->` if it is not a group's writing"));
    assert_eq!(refusal(b, "## Your items\n- A1 x\n", &d).unwrap(), "");
    let five = "## Your items\n- A10 x\n- A11 x\n- A12 x\n- A13 x\n- A14 x\n";
    let why = refusal(b, five, &d).unwrap();
    assert!(why.contains("Split it into 2 briefs of at most 4 - ga.md, gb.md - each"));
    assert!(why.ends_with("set WRITE_CAP_OK='<reason>'"), "{why}");
    assert!(refusal(b, "## Your items\n- \n", &d).is_err());
    assert_eq!(
        split_names(Path::new("v2-write.md"), 9),
        args(&["v2a-write.md", "v2b-write.md", "v2c-write.md"])
    );
    assert_eq!(
        split_names(Path::new("plain"), 5),
        args(&["plaina", "plainb"])
    );
    // a first word of digits other than ASCII is a digit to `str.isdigit`, and no tip names it
    let digits = "## Your items\n- \u{0663}\u{0664} x\n- A10\n- A11\n- A12\n- A13\n";
    assert!(!refusal(b, digits, &d)
        .unwrap()
        .contains("The lines counted as"));
}

#[test]
fn the_command_refuses_a_short_line_and_raises_on_an_unreadable_brief() {
    let d = l7r_gate_core::ci::fixtures::scratch("brief-cli");
    let r = d.to_string_lossy().into_owned();
    assert_eq!(cli(&args(&[&r])).code, 2);
    std::fs::write(d.join("bad.md"), [0xff_u8]).unwrap();
    std::fs::write(d.join("none.md"), "nothing\n").unwrap();
    let none = cli(&args(&[
        &r,
        &format!("{r}/none.md"),
        &format!("{r}/bad.md"),
    ]));
    assert_eq!(none.code, 1);
    assert!(none
        .stdout
        .starts_with("write 0 none.md: -\n  REFUSED: it assigns nothing"));
    assert!(none.stderr.contains("UnicodeDecodeError"));
    std::fs::write(d.join("raise.md"), "## Your items\n- \n").unwrap();
    assert!(cli(&args(&[&r, &format!("{r}/raise.md")]))
        .stderr
        .contains("IndexError"));
}
