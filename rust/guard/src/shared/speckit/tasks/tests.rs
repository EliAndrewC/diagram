//! The tasks archive over scratch texts and directories (feature 449 T142).

use std::path::Path;

use super::*;
use crate::shared::tempdir::TempDir;

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

const OPEN_TEXT: &str = "# Tasks - feature 9\n\nA paragraph.\n\n## Phase 1\n\n- [x] T2 second\n      research: rendering\n      verify: DONE. two\n- [ ] T3 open\n      research: rendering\n- [x] T1 first\n      research: physical\n      - [x] research pass  - [x] recorded and cited\n\n      a note in a second paragraph\n\n## Phase 2\n\n- [x] T4 its box open\n      research: physical\n      - [x] research pass  - [ ] recorded and cited\n- [ ] GM review (make gm-reviewed F=9) [lands-open]\n      research: rendering\n";

#[test]
fn joined_puts_a_newline_between_and_none_where_there_is_no_archive() {
    assert_eq!(joined("a\n", ""), "a\n");
    assert_eq!(joined("a", "b\n"), "a\nb\n");
    assert_eq!(joined("a\n", "b\n"), "a\nb\n");
    assert_eq!(joined("", "b\n"), "b\n");
}

#[test]
fn archived_reads_a_ticked_id_alone() {
    let done = "# h\n\n- [x] T10 x\n- [x] T1a y\n";
    assert!(archived(done, "T10"));
    assert!(archived(done, "T1a"));
    assert!(!archived(done, "T1"));
    assert!(!archived("- [ ] T5 open\n", "T5"));
}

#[test]
fn the_ticked_tasks_move_in_task_order_and_the_rest_stays() {
    let (open, done, ids) = archive_text(OPEN_TEXT, "", "9-x").unwrap();
    assert_eq!(ids, vec!["T1", "T2"]);
    // the open task, the ticked one with a box open, the GM's box, the headings and the prose stay, under the pointer
    assert_eq!(open, format!("# Tasks - feature 9\n\n{POINTER}\n\nA paragraph.\n\n## Phase 1\n\n- [ ] T3 open\n      research: rendering\n\n## Phase 2\n\n- [x] T4 its box open\n      research: physical\n      - [x] research pass  - [ ] recorded and cited\n- [ ] GM review (make gm-reviewed F=9) [lands-open]\n      research: rendering\n"));
    assert_eq!(done, "# 9-x - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)\n\n- [x] T1 first\n      research: physical\n      - [x] research pass  - [x] recorded and cited\n\n      a note in a second paragraph\n- [x] T2 second\n      research: rendering\n      verify: DONE. two\n");
    // what the readers count is unchanged: every box, every ticked one
    let count = |t: &str, pat: &str| t.lines().filter(|l| l.starts_with(pat)).count();
    let all = joined(&open, &done);
    assert_eq!(count(&all, "- ["), count(OPEN_TEXT, "- ["));
    assert_eq!(count(&all, "- [x]"), count(OPEN_TEXT, "- [x]"));
    // ...and a second run moves nothing
    assert_eq!(archive_text(&open, &done, "9-x"), None);
}

#[test]
fn a_later_archive_merges_by_id_and_keeps_its_header_and_a_duplicate() {
    let done = "# kept header\n\n- [x] T1 one\n- [x] T5 five\n      verify: DONE. five\n\n\n";
    let open = "- [x] T3 three\n- [x] T10 ten\n- [x] T5 again\n- [ ] T11 open\n";
    let (open, done, ids) = archive_text(open, done, "9-x").unwrap();
    assert_eq!(ids, vec!["T3", "T5", "T10"]);
    assert_eq!(done, "# kept header\n\n- [x] T1 one\n- [x] T3 three\n- [x] T5 five\n      verify: DONE. five\n- [x] T5 again\n- [x] T10 ten\n");
    // no title: the pointer goes on top
    assert_eq!(open, format!("{POINTER}\n\n- [ ] T11 open\n"));
}

#[test]
fn a_box_with_no_id_in_an_archive_sorts_last_and_the_pointer_is_written_once() {
    let done = "- [ ] stray box\n- [x] T2 two\n";
    let (_, done, _) = archive_text("# T\n- [x] T1 one", done, "9-x").unwrap();
    assert!(done.starts_with("# 9-x - the ticked tasks"));
    assert!(done.ends_with("- [x] T1 one\n- [x] T2 two\n- [ ] stray box\n"));
    // a title with no blank line under it gets one, and a file that has the pointer is not given another
    assert_eq!(
        with_pointer("# T\nbody\n"),
        format!("# T\n\n{POINTER}\n\nbody\n")
    );
    let once = with_pointer("# T\n\nbody\n");
    assert_eq!(with_pointer(&once), once);
}

#[test]
fn a_blank_line_ends_a_block_where_no_indented_line_follows() {
    let open = "- [x] T1 one\n\nprose\n";
    let (kept, done, _) = archive_text(open, "", "9-x").unwrap();
    assert!(done.ends_with("- [x] T1 one\n"));
    assert_eq!(kept, format!("{POINTER}\n\nprose\n"));
    let open = "text\n- [x] T1 one\n      v\n\n## H\n";
    assert_eq!(
        archive_text(open, "", "9-x").unwrap().0,
        format!("{POINTER}\n\ntext\n\n## H\n")
    );
}

#[test]
fn the_directory_forms_read_and_write_both_files() {
    let tmp = TempDir::new("guard-speckit-tasks");
    let d = tmp.join("specs/9-x");
    // no tasks.md: nothing is read, nothing moves
    assert_eq!(archive(&d).unwrap(), Vec::<String>::new());
    assert_eq!(all_text(&d).unwrap(), "");
    put(&tmp, "specs/9-x/tasks.md", "- [ ] T1 open\n");
    assert_eq!(archive(&d).unwrap(), Vec::<String>::new());
    assert!(!d.join(DONE).exists());
    put(&tmp, "specs/9-x/tasks.md", "- [ ] T1 open\n- [x] T2 done\n");
    assert_eq!(archive(&d).unwrap(), vec!["T2"]);
    assert_eq!(done_text(&d).unwrap(), "# 9-x - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)\n\n- [x] T2 done\n");
    assert_eq!(
        all_text(&d).unwrap(),
        format!("{POINTER}\n\n- [ ] T1 open\n{}", done_text(&d).unwrap())
    );
    // an archive that cannot be written: the error, and tasks.md as it was
    put(&tmp, "specs/9-x/tasks.md", "- [x] T3 done\n");
    std::fs::remove_file(d.join(DONE)).unwrap();
    std::fs::create_dir(d.join(DONE)).unwrap();
    assert!(archive(&d).is_err());
    assert_eq!(
        std::fs::read_to_string(d.join(OPEN)).unwrap(),
        "- [x] T3 done\n"
    );
    std::fs::remove_dir(d.join(DONE)).unwrap();
    put(&tmp, "specs/9-x/tasks-done.md", "- [x] T2 done\n");
    assert_eq!(archive(&d).unwrap(), vec!["T3"]);
}
