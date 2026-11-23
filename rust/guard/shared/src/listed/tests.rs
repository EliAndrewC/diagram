use super::*;

fn items(n: usize) -> Vec<String> {
    (1..=n).map(|i| format!("  item {i}")).collect()
}

/// Items as long as a refusal's: a cap over them shortens the list even past a kept file's long path.
fn long_items(n: usize) -> Vec<String> {
    (1..=n)
        .map(|i| format!("  item {i}: {}", "x".repeat(120)))
        .collect()
}

#[test]
fn a_cap_that_would_not_shorten_the_list_says_every_item() {
    let rest = "cat /a/long/path/to/the/kept/list/of/every/item.txt";
    assert_eq!(capped(&items(3), "  ", rest), items(3).join("\n"));
    let three: Vec<String> = (1..=3).map(|i| format!("t{i}")).collect();
    assert_eq!(inline(&three, rest), "t1, t2, t3");
}

#[test]
fn a_short_list_is_said_whole_and_a_long_one_its_first_few_and_the_command_for_the_rest() {
    assert_eq!(
        capped(&items(SHOWN), "  ", "make x"),
        items(SHOWN).join("\n")
    );
    let long = capped(&items(40), "  ", "make x ALL=1");
    assert_eq!(long.lines().count(), SHOWN + 1);
    assert!(long.contains("  item 2") && !long.contains("  item 3"));
    assert!(long.ends_with("  and 38 more: `make x ALL=1`"));
    assert_eq!(
        capped_n(&items(5), 1, "  ", "make x"),
        "  item 1\n  and 4 more: `make x`"
    );
}

#[test]
fn the_rest_kept_in_a_file_is_one_cat_away_and_an_unwritable_one_says_every_item() {
    let tmp = crate::tempdir::TempDir::new("listed");
    let dir = tmp.path().to_path_buf();
    let all = long_items(9);
    let said = capped_kept(&all, "  ", &dir);
    let cmd = said.rsplit("more: `").next().unwrap().trim_end_matches('`');
    let path = cmd.strip_prefix("cat ").unwrap();
    assert_eq!(
        std::fs::read_to_string(path).unwrap(),
        all.join("\n") + "\n"
    );
    assert_eq!(kept(&dir, &all), cmd, "the same list is the same file");
    assert_eq!(capped_kept(&items(2), "  ", &dir), items(2).join("\n"));
    let first = &all[0];
    assert_eq!(
        capped_kept_n(&all, 1, "  ", &dir),
        format!("{first}\n  and 8 more: `{cmd}`")
    );
    let quiet = tmp.path().join("quiet");
    assert_eq!(capped_kept(&items(3), "  ", &quiet), items(3).join("\n"));
    assert!(!quiet.exists(), "a cap not taken writes no file");
    let blocked = dir.join("a-file");
    std::fs::write(&blocked, "").unwrap();
    assert_eq!(capped_kept(&all, "  ", &blocked), all.join("\n"));
}

#[test]
fn an_inline_list_names_its_first_few_and_the_command_for_the_rest() {
    let five: Vec<String> = (1..=5).map(|i| format!("task-{i:03}")).collect();
    assert_eq!(
        inline(&five, "cat x"),
        "task-001, task-002, and 3 more: `cat x`"
    );
    assert_eq!(
        inline(&five, ""),
        "task-001, task-002, task-003, task-004, task-005"
    );
    assert_eq!(inline(&five[..2], "cat x"), "task-001, task-002");
}
