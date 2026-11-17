//! The command line (feature 449 T146).

use l7r_guard::shared::tempdir::TempDir;

use super::{cli, Reply};
use crate::testkit::{fake_chrome, var_for};

fn run(args: &[&str], var: &dyn Fn(&str) -> String, input: &str) -> (Reply, String) {
    let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    let mut out = Vec::new();
    let reply = cli(&args, var, &mut input.as_bytes(), &mut out);
    (reply, String::from_utf8(out).unwrap())
}

#[test]
fn serve_and_crop_through_the_command_line() {
    let dir = TempDir::new("browser-cli");
    let fake = fake_chrome(dir.path());
    let var = var_for(&fake);
    let (reply, out) = run(
        &["serve", "--size", "800x600", "--ignore-https-errors"],
        &var,
        "{\"op\": \"close\"}\n",
    );
    assert_eq!((reply.code, out.trim()), (0, "{\"ready\":true}"));
    let (reply, _) = run(&["serve", "--user-agent", "UA/2"], &var, "");
    assert_eq!(reply.code, 0);
}

/// The crop half of what was one test with the serve half above: four starts of the fake browser together ran at FR-008's tenth of
/// a second, two each apart (feature 449 T167).
#[test]
fn crop_through_the_command_line() {
    let dir = TempDir::new("browser-cli-crop");
    let fake = fake_chrome(dir.path());
    let var = var_for(&fake);
    let png = dir.path().join("g.png");
    let page = dir.path().join("big.html");
    let (reply, _) = run(
        &["crop", page.to_str().unwrap(), "k", png.to_str().unwrap()],
        &var,
        "",
    );
    assert_eq!(reply, Reply::default());
    assert!(png.is_file());
    let (reply, _) = run(
        &[
            "crop",
            dir.path().join("noglyph.html").to_str().unwrap(),
            "k",
            png.to_str().unwrap(),
        ],
        &var,
        "",
    );
    assert_eq!(reply.code, 1);
    assert!(
        reply.stderr.starts_with("l7r-browser crop: TypeError"),
        "{}",
        reply.stderr
    );
}

#[test]
fn a_command_line_it_cannot_run_is_refused() {
    let none = |_: &str| String::new();
    for args in [&[][..], &["crop", "a"][..], &["nope"][..]] {
        let (reply, _) = run(args, &none, "");
        assert_eq!(reply.code, 2);
        assert!(reply.stderr.starts_with("usage: l7r-browser"));
    }
    let (reply, _) = run(&["serve", "--size", "big"], &none, "");
    assert_eq!(
        (reply.code, reply.stderr.as_str()),
        (2, "l7r-browser: bad --size \"big\"\n")
    );
    let (reply, _) = run(&["serve", "--size", "1x"], &none, "");
    assert_eq!(reply.code, 2);
    let (reply, _) = run(&["serve", "--what"], &none, "");
    assert!(reply
        .stderr
        .starts_with("l7r-browser: unknown option \"--what\""));
    // no variable set: the default install under an empty home, not there from the crate's directory
    assert_eq!(run(&["serve"], &none, "").0.code, 1);
    let missing = std::path::PathBuf::from("/no/such/chrome");
    let (reply, _) = run(&["serve"], &var_for(&missing), "");
    assert_eq!(reply.code, 1);
    assert!(reply.stderr.contains("install-chromium.sh"));
}
