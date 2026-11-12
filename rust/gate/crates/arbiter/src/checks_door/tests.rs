use super::close_cli;

#[test]
fn close_answers_its_usage_and_its_verdict() {
    assert_eq!(close_cli(&[]).code, 2);
    let one = close_cli(&["s".to_owned(), "x".to_owned()]);
    assert_eq!(one.code, 2);
    let two = close_cli(&["s".to_owned(), "nothing to close here".to_owned()]);
    assert_eq!(two.code, 0);
    assert!(two.stdout.contains("0 silent dispatch(es) on s"));
    let three = close_cli(&[
        "s".to_owned(),
        "nothing to close here".to_owned(),
        "ag".to_owned(),
    ]);
    assert_eq!(three.code, 0);
}
