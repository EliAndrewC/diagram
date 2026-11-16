//! The absence note's words (feature 449 T144; expected values `absence.py`'s).

use super::{render, unrender, LEAD, MARKER};

#[test]
fn an_absence_note_shows_its_lead_and_unrenders_back() {
    let body = format!("  {MARKER}<!-- searched --> x");
    let shown = render(&body);
    assert_eq!(
        shown,
        format!("  <span class=\"sep\">{MARKER}</span><span class=\"absence-lead\">{LEAD}</span><!-- searched --> x")
    );
    assert_eq!(unrender(&shown), body);
    assert_eq!(render("a cited note"), "a cited note");
}
