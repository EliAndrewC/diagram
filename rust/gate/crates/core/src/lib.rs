//! The gate's shared core (feature 449 T92): what every other gate crate reads - the reply a subcommand gives, a file's content id, the
//! difference of two texts, the records the gate's shell writes (`logs`), and the small readers each tool once kept for itself, under the
//! module names they had in the one crate, so a path such as `crate::checks::py_repr` still names them. The `testkit` feature carries
//! the test helpers the other crates' tests build on.

pub mod checks;
pub mod checks_door;
pub mod codeid;
pub mod cohort;
pub mod difflib;
pub mod logs;
pub mod measure;
pub mod plan;
pub mod record;

/// The remote path's test fixtures, shared by the cohort's and the route's tests.
#[cfg(any(test, feature = "testkit"))]
pub mod ci {
    pub mod fixtures;
}

/// What a subcommand answered: the text for stdout and for stderr, and the exit code.
#[derive(Debug, PartialEq, Eq)]
pub struct Reply {
    pub stdout: String,
    pub stderr: String,
    pub code: i32,
}

/// Write an executable a test will run, the file written by a child process.
///
/// A thread that forks in another test copies every open descriptor until its child execs, so a
/// script this process has just written can still be open for writing in that child and running
/// it fails with "Text file busy". `install` holds the only descriptor that writes the file, and
/// it has exited by the time this returns.
///
/// # Panics
///
/// Where the draft cannot be written, installed or removed.
#[cfg(any(test, feature = "testkit"))]
pub fn write_executable(path: &std::path::Path, text: &str) {
    let draft = path.with_extension("draft");
    std::fs::write(&draft, text).unwrap();
    let done = std::process::Command::new("install")
        .args(["-m", "755"])
        .arg(&draft)
        .arg(path)
        .status();
    assert!(done.unwrap().success());
    std::fs::remove_file(&draft).unwrap();
}

#[cfg(test)]
mod kit_tests;

#[cfg(test)]
mod tests {
    #[test]
    fn an_executable_is_written_whole() {
        let dir = crate::checks::scratch("core-exec");
        let path = dir.join("run.sh");
        super::write_executable(&path, "#!/bin/sh\necho ok\n");
        let out = std::process::Command::new(&path).output().unwrap();
        assert_eq!(String::from_utf8_lossy(&out.stdout), "ok\n");
    }
}
