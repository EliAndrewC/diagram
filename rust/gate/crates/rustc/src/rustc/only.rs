//! A BUILDER'S FILTERED TEST RUN (feature 451 T435, measured by T342: `dev/measurements/2026-11-27/test-selection/results.md`).
//! `make rust-test CRATE=<dir> ONLY="<filter> ..."` is `l7r-gate rust test --crate <dir> --only "<filter> ..."`: the words go to
//! every test binary of the crate (and its doctest pass), after cargo's `--`, as libtest's name filters - `land::carry` runs the
//! tests whose path holds it. While a builder iterates it runs the tests its change reaches: the land crate's `land::carry` is 39 of
//! its 155 tests, 0.54 to 0.92 s of wall against 1.68 to 9.16 s whole, measured 2026-11-27 (the record's section 3).
//!
//! A FILTERED RUN IS NO CRATE'S GREEN: it keeps no result (`answer` skips `keep_green`, so neither the run's key nor the test
//! binary's passed line is written), so the run after it - a `make builder-checks`, a `make rust-test` without `ONLY=`, a
//! `test-counters` sharing the binary - still runs the whole crate and never reads "unchanged - its last green result stands" from
//! it. It may READ one: where the whole crate's green stands on this code, its filtered part passed too, and nothing runs. Its
//! `test` Phase line carries `"only"`, the words, so a reader can tell a part from the crate's run. `make builder-checks` stays the
//! whole crate at a builder's end (T342's DECISION; `scripts/container/builder-brief.md`).
//!
//! Only `test` takes it: `test-counters`, `cover` and the rest keep results a part would stand in for, and `test-times` times each
//! test alone already. A word starting with `-` is refused (libtest would read it as its own flag), and a filter that runs no test
//! of a crate is that crate's failure, so a mistyped module is not read as a pass. So a filter names its crate: with no `--crate`
//! every crate the filter misses would fail, and the line is refused with the command to run (`uncrated`).

use super::{Ran, World};

/// The command-line flag; its value is the filter words, split on white space.
pub(super) const FLAG: &str = "--only";

/// The filter words of one `--only` value: none where it is empty or a word would be a libtest flag.
pub(super) fn words(value: &str) -> Option<Vec<String>> {
    let words: Vec<String> = value.split_whitespace().map(str::to_owned).collect();
    (!words.is_empty() && !words.iter().any(|w| w.starts_with('-'))).then_some(words)
}

/// Every filter word the arguments name (`parse` has refused a malformed one).
pub(super) fn of(args: &[String]) -> Vec<String> {
    args.windows(2)
        .filter(|w| w[0] == FLAG)
        .filter_map(|w| words(&w[1]))
        .flatten()
        .collect()
}

/// The tests a run's output says ran (passed, failed or ignored) and filtered out, over every binary's `test result:` line.
fn tally(stdout: &str) -> (u64, u64) {
    let (mut ran, mut out) = (0, 0);
    for line in stdout.lines().filter(|l| l.starts_with("test result:")) {
        let mut last = 0;
        for word in line.split([' ', ';', '.']).filter(|w| !w.is_empty()) {
            match word {
                "passed" | "failed" | "ignored" => ran += last,
                "filtered" => out += last,
                _ => last = word.parse().unwrap_or(0),
            }
        }
    }
    (ran, out)
}

/// A green filtered run's crate judged (its caller passes no red one): its line said, and one that ran none of its tests made its
/// crate's failure.
pub(super) fn judge(world: &World, shown: &str, done: &mut Ran, stdout: &mut String) {
    match summary(world, shown, &done.stdout) {
        Ok(line) => stdout.push_str(&line),
        Err(why) => (done.code, done.stderr) = (1, why + &done.stderr),
    }
}

/// A green filtered run's line for a crate, or, where the filter ran none of its tests, the failure that says so.
fn summary(world: &World, shown: &str, stdout: &str) -> Result<String, String> {
    let filter = world.only.join(" ");
    match tally(stdout) {
        (0, _) => Err(format!(
            "rust-checks: test ONLY \"{filter}\" ran no test of {shown} - name a module path its tests hold (e.g. land::carry), or drop ONLY= to run the whole crate\n"
        )),
        (ran, out) => Ok(format!(
            "rust-checks: test ONLY \"{filter}\" on {shown}: {ran} ran, {out} filtered out - a part, not kept as the crate's green\n"
        )),
    }
}

/// The run's last line where it was filtered: that a part of each crate ran and none is kept; nothing for a whole run.
pub(super) fn noted(world: &World) -> String {
    if world.only.is_empty() {
        return String::new();
    }
    format!(
        "rust-checks: ONLY \"{}\" ran a part of each crate's tests, NOT kept as its green - `make builder-checks` runs the whole crate\n",
        world.only.join(" ")
    )
}

/// A `test` line's filter with no `--crate`: refused, with the command to run (451 T435's closing half) - every crate the filter
/// misses would turn red by the zero-match rule above, so a crate-wide filter can only fail; `None` where a crate is named.
pub(super) fn uncrated(args: &[String]) -> Option<String> {
    let filter = of(args).join(" ");
    (args.first().map(String::as_str) == Some("test")
        && !filter.is_empty()
        && !args.iter().any(|a| a == "--crate"))
    .then(|| format!("rust-checks: test ONLY \"{filter}\" names no crate - every crate the filter misses would fail; add CRATE=<dir>, as in `make rust-test CRATE=rust/gate/crates/land ONLY=\"{filter}\"`\n"))
}
