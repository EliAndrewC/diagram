//! The pipe form is red on the forced race and refused; the here-string form is green and passes.

use std::process::Command;

use super::super::tests::{commit, put, repo};
use super::{cli, scan};

/// The forced interleaving (451 T252, T253): the matching line, then 1.3 MB, more than a pipe holds, so the writer is always still
/// writing when grep exits at its match.
const PRELUDE: &str = "set -uo pipefail\nseen() { local __seen_var=$1; shift; grep \"$@\" <<< \"${!__seen_var}\"; }\nLONG=$(printf 'MATCH\\n'; seq 200000)\nbig() { printf 'MATCH\\n'; seq 200000; }\nset -- MATCH $(seq 50000)\n";

/// Each form's check line, as a suite or a script writes it, and whether it is the pipe form.
const FORMS: [(&str, bool); 8] = [
    ("printf '%s' \"$LONG\" | grep -q MATCH", true),
    ("echo \"$LONG\" | grep -q MATCH", true),
    ("printf '%s\\n' \"$@\" | grep -qx MATCH", true),
    ("big | grep -q MATCH", true),
    ("big | grep -m1 MATCH >/dev/null", true),
    ("seen LONG -q MATCH", false),
    ("o=$(big) && seen o -q MATCH", false),
    ("grep -qx MATCH <<< \"$(printf '%s\\n' \"$@\")\"", false),
];

/// Does the line, run under the forced race, find the line that is there?
fn finds(line: &str) -> bool {
    let script = format!("{PRELUDE}{line} && echo FOUND\n");
    let out = Command::new("bash").arg("-c").arg(script).output().unwrap();
    String::from_utf8_lossy(&out.stdout).contains("FOUND")
}

#[test]
fn each_pipe_form_reads_a_present_line_absent_and_is_refused_its_here_string_finds_it() {
    for (line, pipe) in FORMS {
        assert_eq!(finds(line), !pipe, "{line}");
        assert_eq!(scan(line).len(), usize::from(pipe), "{line}");
    }
    // negated, the pipe form is a false pass on a line that is there
    assert!(finds("! printf '%s' \"$LONG\" | grep -q MATCH"));
    assert_eq!(scan("! printf '%s' \"$LONG\" | grep -q MATCH").len(), 1);
}

#[test]
fn what_the_scan_reads_and_leaves() {
    // grep's words that read to the end, an or-list, a comment, a here-string
    for line in [
        "printf '%s' \"$OUT\" | grep -c x",
        "printf '%s' \"$OUT\" | grep -E 'a|b' -o",
        "a || grep -q x f",
        "  # printf '%s' \"$OUT\" | grep -q x",
        "grep -q x <<< \"$OUT\"",
        "x | head -1",
        "x | grep --line-buffered y",
    ] {
        assert!(scan(line).is_empty(), "{line}");
    }
    for line in [
        "x | grep -Eq y",
        "x | grep -E -q y",
        "x|grep -l y",
        "x | grep --quiet y",
        "x | grep --max-count=1 y",
    ] {
        assert_eq!(scan(line).len(), 1, "{line}");
    }
    // a pipe continued onto the next line is read there, named at its first line
    assert_eq!(
        scan("a\nx |\n  grep -q y\nb\n"),
        vec![(2, "x | grep -q y".to_owned())]
    );
    assert_eq!(scan("x | \\\n  grep -q y\n").len(), 1);
    // the escape takes two words or more
    assert!(scan("run 'ps | grep -q make' # pipe-ok: a guard's payload").is_empty());
    assert_eq!(scan("run 'ps | grep -q make' # pipe-ok: payload").len(), 1);
}

#[test]
fn the_check_names_each_line_in_the_scope_and_passes_a_clean_tree() {
    let dir = repo("pipe-race");
    put(
        &dir,
        "tests/hooks/test-a.sh",
        "set -uo pipefail\nprintf '%s' \"$OUT\" | grep -q x && ok\n",
    );
    put(&dir, "scripts/run", "#!/usr/bin/env bash\nx | grep -q y\n");
    put(&dir, "scripts/notes.txt", "x | grep -q y\n");
    put(&dir, "scripts/data", "plain\nx | grep -q y\n");
    put(&dir, "rust/x.sh", "x | grep -q y\n");
    commit(&dir);
    let root = dir.to_string_lossy().into_owned();
    let said = cli(
        &["--root".to_owned(), root.clone()],
        std::path::Path::new("/"),
    );
    assert_eq!(said.code, 1);
    assert!(
        said.stderr
            .contains("pipe-race: scripts/run:2: x | grep -q y\n"),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr
            .contains("pipe-race: tests/hooks/test-a.sh:2: printf"),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr.contains("pipe-race: 2 line(s)"),
        "{}",
        said.stderr
    );
    assert!(
        !said.stderr.contains("notes.txt")
            && !said.stderr.contains("data")
            && !said.stderr.contains("rust/")
    );
    put(&dir, "tests/hooks/test-a.sh", "seen OUT -q x && ok\n");
    put(
        &dir,
        "scripts/run",
        "#!/usr/bin/env bash\ngrep -q y <<< \"$(x)\"\n",
    );
    let said = cli(&[], &dir);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(said.stdout.starts_with("pipe-race: no shell file"));
}
