//! Its unit tests (feature 449 T174).
//!
//! Research:
//!     its tests - NONE: tests, deciding nothing about a building

use super::{main, parse, pathlib, Ask};

fn words(args: &[&str]) -> Vec<String> {
    args.iter().map(|a| (*a).to_owned()).collect()
}

fn run(plan: &str, json: &str) -> Ask {
    Ask::Run {
        plan: plan.to_owned(),
        json: json.to_owned(),
    }
}

fn refused(why: &str) -> Ask {
    Ask::Refused(why.to_owned())
}

#[test]
fn the_arguments_read_as_argparse_reads_them() {
    // each answer `CPython` 3.14.4's argparse gave over the same parser (scratchpad t174/argprobe)
    let required = "the following arguments are required: plan";
    let expected = "argument --json: expected one argument";
    let cases: Vec<(Vec<&str>, Ask)> = vec![
        (vec![], refused(required)),
        (vec!["a"], run("a", "")),
        (vec!["a", "b"], refused("unrecognized arguments: b")),
        (vec!["-x"], refused(required)),
        (
            vec!["a", "-x", "b"],
            refused("unrecognized arguments: -x b"),
        ),
        (vec!["a", "--json"], refused(expected)),
        (vec!["--json", "j", "a"], run("a", "j")),
        (vec!["a", "--js", "j"], run("a", "j")),
        (vec!["a", "--j=j"], run("a", "j")),
        (vec!["--", "-a"], run("-a", "")),
        (vec!["--", "--"], run("--", "")),
        (
            vec!["a", "--", "--json", "x"],
            refused("unrecognized arguments: --json x"),
        ),
        (vec!["-h"], Ask::Help),
        (vec!["a", "-hx"], Ask::Help),
        (vec!["-h x"], Ask::Help),
        (vec!["--he"], Ask::Help),
        (vec!["--bad", "-h"], Ask::Help),
        (
            vec!["--help=x"],
            refused("argument -h/--help: ignored explicit argument 'x'"),
        ),
        (
            vec!["-h=1"],
            refused("argument -h/--help: ignored explicit argument '1'"),
        ),
        (
            vec!["-h-x"],
            refused("argument -h/--help: ignored explicit argument '-x'"),
        ),
        (
            vec!["--=x"],
            refused("ambiguous option: --=x could match --help, --json"),
        ),
        (vec!["a", "--json", "-1"], run("a", "-1")),
        (vec!["a", "--json", "-h"], refused(expected)),
        (vec!["a", "--json", "--"], refused(expected)),
        (vec!["-1.5", "--json", "-.5"], run("-1.5", "-.5")),
        (vec!["-a b"], run("-a b", "")),
        (vec!["a", "--json="], run("a", "")),
        (vec!["--json=a=b", "p"], run("p", "a=b")),
        (vec!["--x=1", "a"], refused("unrecognized arguments: --x=1")),
        (vec!["a", "-j"], refused("unrecognized arguments: -j")),
        (
            vec!["a", "--jsonx"],
            refused("unrecognized arguments: --jsonx"),
        ),
    ];
    for (args, ask) in cases {
        assert_eq!(parse(&words(&args)), ask, "{args:?}");
    }
}

#[test]
fn a_path_is_written_as_pathlib_writes_it() {
    // `CPython` 3.14.4's `str(pathlib.Path(p))`
    for (given, written) in [
        ("", "."),
        (".", "."),
        ("./a", "a"),
        ("a//b/./c", "a/b/c"),
        ("//a", "//a"),
        ("///a", "/a"),
        ("a/", "a"),
        ("a/..", "a/.."),
        ("/", "/"),
    ] {
        assert_eq!(pathlib(given), written, "{given}");
    }
}

#[test]
fn the_command_prints_writes_and_refuses_as_the_script_did() {
    let dir = l7r_shared::tempdir::TempDir::new("mode-a-size-table");
    let at = |name: &str| dir.path().join(name).to_string_lossy().into_owned();
    let sheet = r#"<svg><rect x="0" y="0" width="30" height="3" data-kind="wall"/><circle cx="1" cy="1" r="3" data-kind="tub"/></svg>"#;
    std::fs::write(at("s.svg"), sheet).unwrap();
    let r = main(&words(&[&at("s.svg"), "--json", &at("s.json")]));
    assert_eq!((r.code, r.stderr.as_str()), (0, ""), "{}", r.stderr);
    assert!(r
        .stdout
        .starts_with("size-table: s.svg - 3 px = 1 ft; 1 rects, 0 wall gaps\n"));
    assert!(r
        .stdout
        .ends_with("    2.0    2.0     0.0     0.0  circle   -2,-2         tub\n"));
    assert!(std::fs::read_to_string(at("s.json"))
        .unwrap()
        .contains("\"kind\": \"wall\""));
    assert_eq!(main(&words(&[&at("s.svg")])).stdout, r.stdout);
    // a JSON that cannot be written: the tables printed, the traceback's last line
    let r = main(&words(&[
        &at("s.svg"),
        &format!("--json={}", dir.path().display()),
    ]));
    assert_eq!(r.code, 1);
    assert!(r.stdout.contains("marks (") && r.stderr.starts_with("IsADirectoryError: [Errno 21]"));
    // the marks refused after the table printed
    std::fs::write(
        at("m.svg"),
        r#"<svg><g transform="translate(.)"><circle r="1" data-kind="x"/></g></svg>"#,
    )
    .unwrap();
    let r = main(&words(&[&at("m.svg")]));
    assert_eq!(
        (
            r.code,
            r.stdout.starts_with("size-table: m.svg"),
            r.stderr.as_str()
        ),
        (
            1,
            true,
            "ValueError: could not convert string to float: '.'\n"
        )
    );
    // no plan, a directory, bytes that are not UTF-8, a refused sheet
    let r = main(&words(&[&format!("{}//./none.svg", dir.path().display())]));
    assert_eq!(
        (r.code, r.stderr),
        (
            2,
            format!("size-table: no such plan - {}\n", at("none.svg"))
        )
    );
    assert_eq!(main(&words(&[&at("")])).code, 2);
    std::fs::write(at("b.svg"), b"\xff<svg/>").unwrap();
    assert!(main(&words(&[&at("b.svg")]))
        .stderr
        .starts_with("UnicodeDecodeError: "));
    std::fs::write(at("p.svg"), "<svg").unwrap();
    let r = main(&words(&[&at("p.svg")]));
    assert_eq!((r.code, r.stdout.as_str()), (1, ""));
    // the help and a refusal of the arguments
    let r = main(&words(&["-h"]));
    assert!(
        r.code == 0
            && r.stdout
                .starts_with("usage: l7r-mode-a size-table [-h] [--json JSON] plan\n\nEvery drawn")
    );
    let r = main(&[]);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (2, "usage: l7r-mode-a size-table [-h] [--json JSON] plan\nl7r-mode-a size-table: error: the following arguments are required: plan\n")
    );
}
