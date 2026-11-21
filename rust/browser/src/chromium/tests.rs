//! Which Chromium and how it starts (feature 449 T146).

use std::path::PathBuf;

use l7r_shared::tempdir::TempDir;

use super::{arguments, executable, pinned, Launched};
use crate::testkit::{fake_chrome, var_for};

#[test]
fn the_pin_names_the_version_the_install_script_fetches() {
    let v = pinned("CHROMIUM_VERSION");
    assert!(v.split('.').count() == 4 && v.chars().all(|c| c.is_ascii_digit() || c == '.'));
    assert_eq!(pinned("CHROMIUM_SHA256").len(), 64);
    assert_eq!(pinned("NO_SUCH_LINE"), "");
}

#[test]
fn the_executable_is_named_or_found_under_the_pinned_version() {
    let none = |_: &str| String::new();
    let home = |k: &str| {
        if k == "HOME" {
            "/home/x".to_owned()
        } else {
            String::new()
        }
    };
    let moved = |k: &str| {
        if k == "L7R_CHROMIUM_HOME" {
            "/opt/c".to_owned()
        } else {
            String::new()
        }
    };
    let v = pinned("CHROMIUM_VERSION");
    assert_eq!(
        executable(&home),
        PathBuf::from(format!(
            "/home/x/.cache/l7r-chromium/{v}/chrome-headless-shell-linux64/chrome-headless-shell"
        ))
    );
    assert_eq!(
        executable(&moved),
        PathBuf::from(format!(
            "/opt/c/{v}/chrome-headless-shell-linux64/chrome-headless-shell"
        ))
    );
    assert!(executable(&none).starts_with(".cache/l7r-chromium"));
    let fake = PathBuf::from("/x/fake");
    assert_eq!(executable(&var_for(&fake)), fake);
    assert!(super::env_var("L7R_NO_SUCH_VARIABLE_T146").is_empty());
}

#[test]
fn the_arguments_are_playwrights_switches_then_the_profile_and_the_pipe() {
    let args = arguments(std::path::Path::new("/p"));
    assert_eq!(args[0], "--disable-field-trial-config");
    assert!(args.contains(&"--headless".to_owned()));
    assert_eq!(
        &args[args.len() - 3..],
        [
            "--user-data-dir=/p",
            "--remote-debugging-pipe",
            "--no-startup-window"
        ]
    );
}

#[test]
fn a_browser_starts_on_its_own_profile_and_one_not_installed_is_refused() {
    let dir = TempDir::new("browser-chromium");
    let fake = fake_chrome(dir.path());
    let launched = Launched::start(&var_for(&fake)).unwrap();
    drop(launched);
    let missing = dir.path().join("missing");
    let err = Launched::start(&var_for(&missing)).err().unwrap();
    assert!(err.contains("run scripts/container/install-chromium.sh"));
    let mute = crate::testkit::script(dir.path(), "mute", "exit 0");
    assert!(Launched::start(&var_for(&mute)).is_err());
}
