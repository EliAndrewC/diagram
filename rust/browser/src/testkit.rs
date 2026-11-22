//! The tests' Chromium (feature 449 T146; Rust since T273): this test binary started again as [`fake::ENTRY`], which speaks the
//! protocol on fds 3 and 4 as Chromium does, answering each command the crate sends from a table, so every path of the crate runs
//! without a browser, a network or a Python interpreter (SC-005). What a page does is read from its URL ([`fake`] lists the cases).

use std::path::{Path, PathBuf};

pub mod fake;

/// The program the crate starts as its browser: a shell that runs this test binary again as the fake alone, the browser's arguments
/// dropped (the fake reads none). `exec`, so a kill of the browser reaches the fake.
fn fake_program() -> String {
    let exe = std::env::current_exe().unwrap();
    format!(
        "#!/bin/sh\n{}=1 exec '{}' --exact {} --nocapture -q\n",
        fake::MARKER,
        exe.display(),
        fake::ENTRY
    )
}

/// The fake browser written into `dir`, executable; its path. The crop's waits on this test thread are then none: the fake draws
/// nothing, so a wait for it to settle proves nothing (feature 449 T167).
#[must_use]
pub fn fake_chrome(dir: &Path) -> PathBuf {
    crate::crop::WAIT_DIVISOR.set(u64::MAX);
    let at = dir.join("fake-chrome");
    executable(&at, &fake_program());
    at
}

/// `text` written to `at` as a program by `install`, as the gate's `core::write_executable` writes one: a file this process wrote
/// itself stays open for writing in any child another test thread forks meanwhile, until that child's `exec`, and running it then can
/// fail with "Text file busy". The fake browser closed before its first answer once in 12 runs with the crates' tests side by side, the
/// shape that race leaves (feature 449 T160, observed 2026-11-17; the error itself was not seen).
pub fn executable(at: &Path, text: &str) {
    let draft = at.with_extension("draft");
    std::fs::write(&draft, text).unwrap();
    let done = std::process::Command::new("install")
        .args(["-m", "755"])
        .arg(&draft)
        .arg(at)
        .status();
    assert!(done.unwrap().success());
    std::fs::remove_file(&draft).unwrap();
}

/// A program at `dir/name` running `body` as a shell script.
#[must_use]
pub fn script(dir: &Path, name: &str, body: &str) -> PathBuf {
    let at = dir.join(name);
    executable(&at, &format!("#!/bin/sh\n{body}\n"));
    at
}

/// The environment a test hands the crate: `L7R_CHROMIUM` the fake, every other name empty.
pub fn var_for(exe: &Path) -> impl Fn(&str) -> String + '_ {
    move |k: &str| {
        (k == "L7R_CHROMIUM")
            .then(|| exe.to_string_lossy().into_owned())
            .unwrap_or_default()
    }
}
