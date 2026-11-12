//! The command lines, read as argparse reads them.

use super::{parse, Spec};

fn specs() -> [Spec; 5] {
    [
        Spec::value("--root"),
        Spec::value("--result"),
        Spec::value("--reason"),
        Spec::flag("--slugs"),
        Spec::pair("--between"),
    ]
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn flags_values_and_pairs_are_read() {
    let p = parse(
        &args(&[
            "--root",
            "a",
            "--root=b",
            "--sl",
            "--between",
            "x",
            "y",
            "--result",
            "-1",
            "--reason",
            "- two words",
        ]),
        &specs(),
    )
    .unwrap();
    assert_eq!(p.text("--root", "."), "b");
    assert_eq!(p.all("--root"), ["a", "b"]);
    assert_eq!(p.text("--missing", "d"), "d");
    assert!(p.on("--slugs") && !p.on("--other"));
    assert_eq!(p.pair("--between"), Some(("x", "y")));
    assert_eq!(p.pair("--nope"), None);
    assert_eq!(p.text("--result", ""), "-1");
    assert_eq!(p.text("--reason", ""), "- two words");
}

#[test]
fn what_argparse_refuses_is_refused() {
    for bad in [
        &["stray"][..],
        &["-x"],
        &["--bogus"],
        &["--re", "x"],
        &["--root"],
        &["--root", "--slugs"],
        &["--root", "-z"],
        &["--slugs=1"],
        &["--between", "a"],
        &["--between=a"],
        &["--between", "a", "--slugs"],
    ] {
        assert!(parse(&args(bad), &specs()).is_err(), "{bad:?}");
    }
    assert!(parse(&args(&["--root", "-"]), &specs()).is_ok());
}
