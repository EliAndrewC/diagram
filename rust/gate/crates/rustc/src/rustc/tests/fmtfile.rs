//! `make format FILE=<path>` (feature 451 T34): rustfmt over the one file named, read on its standard input so rustfmt follows none of
//! its `mod` children, with its crate's edition; another crate's file, and the file's own children, keep their bytes.

use std::path::Path;
use std::time::{Duration, SystemTime};

use super::{dispatch, two_crates, world_with};
use crate::rustc::World;

/// The fake rustfmt in the world's toolchain directory: it notes where it ran and its words, squeezes runs of spaces from its input,
/// and fails on an input holding `BROKEN`, as rustfmt fails on a file that does not parse.
fn fake_rustfmt(world: &World) {
    crate::write_executable(
        &world.path_dir.join("rustfmt"),
        &format!(
            "#!/bin/sh\necho \"$PWD $*\" >> \"{}/rustfmt-calls\"\nin=$(cat)\ncase \"$in\" in *BROKEN*) echo 'error: this file contains an unclosed delimiter' >&2; exit 1;; esac\nprintf '%s\\n' \"$in\" | tr -s ' '\n",
            world.path_dir.display()
        ),
    );
}

fn rustfmt_calls(world: &World) -> Vec<String> {
    std::fs::read_to_string(world.path_dir.join("rustfmt-calls"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|w| (*w).to_owned()).collect()
}

fn read(root: &Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap()
}

/// Two crates, each with a file rustfmt would change; `a`'s `lib.rs` declares a child module that would change too.
fn unformatted(root: &Path) {
    std::fs::write(
        root.join("rust/a/Cargo.toml"),
        "[package]\nname = \"a\"\nedition = \"2021\"\n",
    )
    .unwrap();
    std::fs::write(root.join("rust/a/src/lib.rs"), "mod k;\nfn  f( ) {}\n").unwrap();
    std::fs::write(root.join("rust/a/src/k.rs"), "fn  g( ) {}\n").unwrap();
    std::fs::write(root.join("rust/b/src/lib.rs"), "fn  h( ) {}\n").unwrap();
}

#[test]
fn a_file_run_formats_that_file_alone_with_its_crates_edition() {
    let (root, ..) = two_crates();
    unformatted(&root);
    let world = world_with(&root, "echo cargo-ran; exit 0");
    fake_rustfmt(&world);
    let done = dispatch(&world, &words(&["format", "--file", "rust/a/src/lib.rs"]));
    assert_eq!(done.code, 0, "{}{}", done.stdout, done.stderr);
    assert_eq!(read(&root, "rust/a/src/lib.rs"), "mod k;\nfn f( ) {}\n");
    // another crate's file and the named file's own child keep their bytes
    assert_eq!(read(&root, "rust/b/src/lib.rs"), "fn  h( ) {}\n");
    assert_eq!(read(&root, "rust/a/src/k.rs"), "fn  g( ) {}\n");
    assert!(
        done.stdout
            .contains("rust-checks: format on rust/a/src/lib.rs: formatted"),
        "{}",
        done.stdout
    );
    // rustfmt, never cargo, from the file's directory (where it finds a rustfmt.toml), with the crate's edition
    assert_eq!(
        rustfmt_calls(&world),
        [format!(
            "{} --edition 2021",
            root.join("rust/a/src").display()
        )]
    );
    assert!(std::fs::read_to_string(world.target.join("calls"))
        .unwrap_or_default()
        .is_empty());
}

#[test]
fn several_files_are_each_formatted_and_an_absolute_path_is_one() {
    let (root, ..) = two_crates();
    unformatted(&root);
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    let absolute = root.join("rust/b/src/lib.rs").display().to_string();
    let done = dispatch(
        &world,
        &words(&["format", "--file", "rust/a/src/k.rs", "--file", &absolute]),
    );
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(read(&root, "rust/a/src/k.rs"), "fn g( ) {}\n");
    // a crate naming no edition is rustfmt's and cargo's default, 2015
    assert_eq!(read(&root, "rust/b/src/lib.rs"), "fn h( ) {}\n");
    assert!(rustfmt_calls(&world)[1].ends_with(" --edition 2015"));
    assert!(done
        .stdout
        .contains("format on rust/b/src/lib.rs: formatted"));
}

#[test]
fn a_file_already_formatted_is_not_written() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    let file = root.join("rust/a/src/lib.rs");
    let old = SystemTime::now() - Duration::from_secs(3600);
    std::fs::File::options()
        .write(true)
        .open(&file)
        .unwrap()
        .set_modified(old)
        .unwrap();
    let done = dispatch(&world, &words(&["format", "--file", "rust/a/src/lib.rs"]));
    assert_eq!(done.code, 0);
    assert!(done.stdout.contains("already formatted"), "{}", done.stdout);
    assert_eq!(std::fs::metadata(&file).unwrap().modified().unwrap(), old);
}

#[test]
fn a_check_run_writes_nothing_and_refuses_a_file_rustfmt_would_change() {
    let (root, ..) = two_crates();
    unformatted(&root);
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    let done = dispatch(
        &world,
        &words(&["format", "--check", "--file", "rust/a/src/lib.rs"]),
    );
    assert_eq!(done.code, 1);
    assert_eq!(read(&root, "rust/a/src/lib.rs"), "mod k;\nfn  f( ) {}\n");
    assert!(
        done.stderr
            .contains("run `make format FILE=rust/a/src/lib.rs`"),
        "{}",
        done.stderr
    );
    std::fs::write(root.join("rust/a/src/lib.rs"), "fn f() {}\n").unwrap();
    let clean = dispatch(
        &world,
        &words(&["format", "--file", "rust/a/src/lib.rs", "--check"]),
    );
    assert_eq!(clean.code, 0, "{}", clean.stderr);
}

#[test]
fn a_file_rustfmt_cannot_parse_is_left_as_it_was_with_rustfmts_words() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    std::fs::write(root.join("rust/a/src/lib.rs"), "fn  f( { BROKEN\n").unwrap();
    let done = dispatch(&world, &words(&["format", "--file", "rust/a/src/lib.rs"]));
    assert_eq!(done.code, 1);
    assert_eq!(read(&root, "rust/a/src/lib.rs"), "fn  f( { BROKEN\n");
    assert!(
        done.stderr.contains("unclosed delimiter"),
        "{}",
        done.stderr
    );
    assert!(done.stderr.contains("format FAILED on rust/a/src/lib.rs"));
}

#[test]
fn a_file_no_crate_owns_or_none_at_all_is_refused_with_the_form() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    std::fs::write(root.join("loose.rs"), "fn  f( ) {}\n").unwrap();
    std::fs::write(root.join("rust/a/notes.md"), "x\n").unwrap();
    std::fs::write(
        root.join("rust/b/Cargo.toml"),
        "[package]\nedition.workspace = true\n",
    )
    .unwrap();
    for (file, why) in [
        ("rust/a/src/gone.rs", "no such file"),
        ("loose.rs", "no crate under the tree owns it"),
        ("rust/a/notes.md", "not a Rust file"),
        ("rust/b/src/lib.rs", "its edition is not a literal"),
        ("/elsewhere/x.rs", "no such file"),
    ] {
        let done = dispatch(&world, &words(&["format", "--file", file]));
        assert_eq!(done.code, 2, "{file}: {}", done.stderr);
        assert!(done.stderr.contains(why), "{file}: {}", done.stderr);
        assert!(done.stderr.contains("make format FILE=<path>"));
    }
    assert!(rustfmt_calls(&world).is_empty());
    assert_eq!(read(&root, "loose.rs"), "fn  f( ) {}\n");
}

#[test]
fn a_file_with_a_crate_or_another_check_or_no_path_is_the_usage() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    for (args, why) in [
        (
            &["format", "--file", "rust/a/src/lib.rs", "--crate", "rust/b"][..],
            "FILE= and CRATE= together",
        ),
        (&["lint", "--file", "rust/a/src/lib.rs"][..], "usage"),
        (&["format", "--file"][..], "usage"),
        (&["format", "--file", "x.rs", "--what"][..], "usage"),
    ] {
        let done = dispatch(&world, &words(args));
        assert_eq!(done.code, 2, "{args:?}");
        assert!(done.stderr.contains(why), "{args:?}: {}", done.stderr);
    }
    assert!(rustfmt_calls(&world).is_empty());
}

#[test]
fn an_unreadable_file_a_rustfmt_that_cannot_start_or_a_write_refused_is_said() {
    use std::os::unix::fs::PermissionsExt as _;
    let (root, ..) = two_crates();
    unformatted(&root);
    let world = world_with(&root, "exit 0");
    // not UTF-8: refused before rustfmt is asked
    std::fs::write(root.join("rust/a/src/bin.rs"), [0xff, 0xfe]).unwrap();
    let done = dispatch(&world, &words(&["format", "--file", "rust/a/src/bin.rs"]));
    assert_eq!(done.code, 2);
    assert!(
        done.stderr.contains("rust/a/src/bin.rs: "),
        "{}",
        done.stderr
    );
    // the toolchain's rustfmt there but not a program
    std::fs::write(world.path_dir.join("rustfmt"), "not a program").unwrap();
    let done = dispatch(&world, &words(&["format", "--file", "rust/a/src/k.rs"]));
    assert_eq!(done.code, 1);
    assert!(
        done.stderr.contains("cannot start rustfmt"),
        "{}",
        done.stderr
    );
    assert_eq!(read(&root, "rust/a/src/k.rs"), "fn  g( ) {}\n");
    // a file rustfmt changed but that cannot be written
    fake_rustfmt(&world);
    let file = root.join("rust/b/src/lib.rs");
    std::fs::set_permissions(&file, std::fs::Permissions::from_mode(0o444)).unwrap();
    let done = dispatch(&world, &words(&["format", "--file", "rust/b/src/lib.rs"]));
    std::fs::set_permissions(&file, std::fs::Permissions::from_mode(0o644)).unwrap();
    assert_eq!(done.code, 1);
    assert!(
        done.stderr.contains("format FAILED on rust/b/src/lib.rs: "),
        "{}",
        done.stderr
    );
}

#[test]
fn the_toolchains_rustfmt_is_the_one_run_and_the_paths_where_there_is_none() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    fake_rustfmt(&world);
    assert_eq!(
        super::super::fmtfile::rustfmt_exe(&world.path_dir),
        world.path_dir.join("rustfmt").display().to_string()
    );
    assert_eq!(
        super::super::fmtfile::rustfmt_exe(&root.join("no-toolchain")),
        "rustfmt"
    );
}
