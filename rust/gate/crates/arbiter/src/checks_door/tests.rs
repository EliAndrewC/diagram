use super::{close_cli, close_in};

/// The guard log of this test, never the live one (451 T309: each run of it wrote its two `CHECK_CLOSED` escapes into
/// `~/.claude/guard-log`, 2,229 of them by 2026-11-26): one directory for the process, as the land, plan and task crates'
/// `quiet_census`.
fn quiet_log() {
    static DIR: std::sync::OnceLock<std::path::PathBuf> = std::sync::OnceLock::new();
    DIR.get_or_init(|| {
        let dir = l7r_shared::tempdir::beside_binary("gate-arbiter-log");
        std::env::set_var("GUARD_LOG_DIR", &dir);
        dir
    });
}

#[test]
fn close_answers_its_usage_and_its_verdict() {
    quiet_log();
    // the usage is answered before any tree is read: the one call on the process's own directory
    assert_eq!(close_cli(&[]).code, 2);
    // a scratch tree with no check state, never the one the tests run in
    let root = crate::checks::scratch("arbiter-close");
    std::fs::create_dir_all(root.join(".git")).unwrap();
    let one = close_in(&root, &["s".to_owned(), "x".to_owned()]);
    assert_eq!(one.code, 2);
    let two = close_in(&root, &["s".to_owned(), "nothing to close here".to_owned()]);
    assert_eq!(two.code, 0);
    assert!(two.stdout.contains("0 silent dispatch(es) on s"));
    let three = close_in(
        &root,
        &[
            "s".to_owned(),
            "nothing to close here".to_owned(),
            "ag".to_owned(),
        ],
    );
    assert_eq!(three.code, 0);
}
