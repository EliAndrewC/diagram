//! The map notes' reader at its edges (feature 449 T150); part A's page lockstep held it to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`) on every pool and legacy notes file.
//!
//! Research: the notes reader's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{bullets, get, normalize_key, parse_map_notes, read_map_notes};

#[test]
fn the_block_reads_what_it_can_and_nothing_else() {
    assert_eq!(
        normalize_key("  **District   Direction**_ "),
        "district direction"
    );
    let notes = parse_map_notes(
        "## Map notes\n### Place\n- **district**: A\n  wrapped\n### Features\n- **well**: b\n",
    );
    assert_eq!(get(&notes.place, "district"), Some("A wrapped"));
    assert_eq!(get(&notes.features, "well"), Some("b"));
    assert_eq!(get(&notes.features, "pond"), None);
    assert!(bullets("- **a**:\n").is_empty());
    assert_eq!(parse_map_notes("nothing"), super::MapNotes::default());
    assert_eq!(
        read_map_notes(std::path::Path::new("/no/such.notes.md")),
        super::MapNotes::default()
    );
    let dir = l7r_guard::shared::tempdir::TempDir::new("notes-read");
    let at = dir.path().join("m.notes.md");
    std::fs::write(
        &at,
        b"## Map notes\r\n### Place\r\n- **district**: \xff\r\n",
    )
    .unwrap();
    assert_eq!(
        get(&read_map_notes(&at).place, "district"),
        Some("\u{fffd}")
    );
}
