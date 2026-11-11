//! The report printed whole to a pipe, paged on a terminal it overflows.

use super::{page, rows, Screen};

fn screen(tty: bool, rows: usize, pager: &str, off: bool) -> Screen {
    Screen {
        tty,
        rows,
        pager: pager.to_owned(),
        off,
    }
}

#[test]
fn a_long_report_goes_through_the_pager_only_on_a_terminal() {
    let dir = crate::checks::scratch("claims-pager");
    let sink = dir.join("paged.txt");
    let pager = format!("cat > {}", sink.display());
    assert_eq!(page("a\nb", &screen(false, 1, &pager, false)), "a\nb\n");
    assert_eq!(page("a\nb", &screen(true, 1, &pager, true)), "a\nb\n");
    assert_eq!(page("a\nb", &screen(true, 9, &pager, false)), "a\nb\n");
    assert_eq!(
        page("a\nb", &screen(true, 1, "no-such-pager-anywhere", false)),
        "a\nb\n"
    );
    assert_eq!(page("a\nb", &screen(true, 1, &pager, false)), "");
    assert_eq!(std::fs::read_to_string(&sink).unwrap(), "a\nb\n");
    assert_eq!(page("a\nb", &screen(true, 1, "/bin/true", false)), "");
    assert_eq!(rows(Some("40".into()), "echo 9 80"), 40);
    assert_eq!(rows(Some("x".into()), "echo 9 80"), 9);
    assert_eq!(rows(None, "exit 1"), 24);
    let here = Screen::here();
    assert!(!here.tty && here.rows == 24 && !here.pager.is_empty());
}

#[test]
fn the_screen_is_read_from_its_parts() {
    let s = Screen::of(
        true,
        Some("7".into()),
        Some(String::new()),
        Some("1".into()),
    );
    assert!(s.tty && s.rows == 7 && s.pager == "less -FRSX" && s.off);
    let s = Screen::of(false, None, Some("more".into()), Some(String::new()));
    assert!(!s.tty && s.rows == 24 && s.pager == "more" && !s.off);
}
