//! The tick's text and its research boxes (feature 449 T131): each refusal, the verify note replaced or added, the boxes kept and
//! ticked, and Python's line boundaries.

use super::{boxes_refusal, is_boxes_line, lines_kept, tick, Refused};

const TASKS: &str = "# Tasks\n\n- [ ] T01 the first\n      research: rendering\n      verify: old\n        wrapped\n      - [ ] research pass\n- [ ] T02 no verify\n\n\n## Next\n\n- [x] T09 done\n- [ ] T10 last";

#[test]
fn a_tick_replaces_the_verify_text_and_keeps_the_boxes() {
    let (new, line) = tick(TASKS, "T01", "  checked  ", false).unwrap();
    assert_eq!(line, "- [x] T01 the first");
    assert!(new.contains("- [x] T01 the first\n      research: rendering\n      verify: DONE. checked\n      - [ ] research pass\n- [ ] T02"));
    assert!(!new.contains("wrapped"));
    // the boxes ticked with it
    let (boxed, _) = tick(TASKS, "T01", "n", true).unwrap();
    assert!(boxed.contains("      - [x] research pass\n"));
}

#[test]
fn a_task_with_no_verify_line_gets_one_before_the_blank_lines() {
    let (new, _) = tick(TASKS, "T02", "n", false).unwrap();
    assert!(new.contains("- [x] T02 no verify\n      verify: DONE. n\n\n\n## Next"));
    // a last line with no newline gets one
    let (end, _) = tick(TASKS, "T10", "n", false).unwrap();
    assert!(end.ends_with("- [x] T10 last\n      verify: DONE. n\n"));
}

#[test]
fn each_refusal_is_said() {
    let refused = |t: &str, note: &str, boxes: bool| tick(TASKS, t, note, boxes).unwrap_err();
    assert_eq!(
        refused("T01", "  ", false),
        Refused::Value("the verify note is empty - say what was verified (NOTE=...)".to_owned())
    );
    assert_eq!(
        refused("T09", "n", false),
        Refused::Value("T09 is already ticked".to_owned())
    );
    assert_eq!(
        refused("T99", "n", false),
        Refused::Value("no open task T99 in tasks.md".to_owned())
    );
    assert_eq!(
        refused("T0", "n", false),
        Refused::Value("no open task T0 in tasks.md".to_owned())
    );
    assert_eq!(
        refused("T02", "n", true),
        Refused::Exit("--boxes: no research-box line found in '- [x] T02 no verify' - is this a `research: physical` task?".to_owned())
    );
}

#[test]
fn python_s_line_boundaries_and_whitespace_hold() {
    assert_eq!(
        lines_kept("a\r\nb\x0cc\u{2028}d"),
        vec!["a\r\n", "b\x0c", "c\u{2028}", "d"]
    );
    assert_eq!(lines_kept(""), Vec::<&str>::new());
    assert!(is_boxes_line("\x1c- [ ] x"));
    assert!(!is_boxes_line("- [ ] x"));
    assert!(!is_boxes_line(""));
    // a verify line ending in a form feed is replaced with a newline
    let (new, _) = tick("- [ ] T01 a\n  verify: x\x0cy\n", "T01", "n", false).unwrap();
    assert_eq!(new, "- [x] T01 a\n  verify: DONE. n\n");
}

#[test]
fn an_open_research_box_refuses_a_physical_task_unless_this_tick_ticks_it() {
    let physical = "- [ ] T03 p\n      research: physical\n      - [ ] research pass\n- [ ] T04 q\n      research: physical\n      - [x] research pass\n# end\n      - [ ] after the heading\n";
    assert!(boxes_refusal(physical, "T03", false)
        .contains("T03 is a `research: physical` task with a research box unticked"));
    assert_eq!(boxes_refusal(physical, "T03", true), "");
    assert_eq!(boxes_refusal(physical, "T04", false), "");
    assert_eq!(boxes_refusal(physical, "T99", false), "");
    assert_eq!(
        boxes_refusal("- [ ] T05 r\n      - [ ] a box\n", "T05", false),
        ""
    );
}
