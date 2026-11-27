//! The stream against the whole-string read it replaced (451 T508): the same answer on every fixture at every chunk size, UTF-8
//! checked as `read_to_string` checked it, one chunk held, the read stopped early only on a no.

use std::cell::Cell;
use std::io::{Cursor, Read};

use super::{after_first, found, held_after, holds, snaps, CHUNK};

const HOLDS: &[u8] = b"\"plan_holds\":";
const SNAPS: &[u8] = b"\"plan_snaps\"";

/// The prefilters as they were before T508, the oracle: the whole file read into a string, a failed read no.
fn old(state: &[u8]) -> (bool, bool) {
    let Ok(text) = std::str::from_utf8(state) else {
        return (false, false);
    };
    let holds = text.split_once("\"plan_holds\":").is_some_and(|(_, rest)| {
        rest.trim_start()
            .strip_prefix('{')
            .is_some_and(|inner| !inner.trim_start().starts_with('}'))
    });
    (holds, text.contains("\"plan_snaps\""))
}

fn new(state: &[u8], chunk: usize) -> (bool, bool) {
    let h = after_first(&mut Cursor::new(state), HOLDS, chunk, &held_after);
    (
        h,
        after_first(&mut Cursor::new(state), SNAPS, chunk, &found),
    )
}

const CASES: &[&[u8]] = &[
    b"",
    b"{}",
    b"{\"dispatches\": {}, \"plan_holds\": {}}",
    b"{\"plan_holds\": {\"h\": 1}}",
    b"{\n \"plan_holds\": {\n  \"toolu\": {\n   \"t\": 1\n  }\n }\n}",
    b"{\n \"plan_holds\":\n {\n }\n}",
    b"{\"plan_holds\": { }",
    b"{\"plan_holds\":",
    b"{\"plan_holds\":   ",
    b"{\"plan_holds\": {",
    b"{\"plan_holds\": {   ",
    b"{\"plan_holds\": 3}",
    "{\"plan_holds\":\u{a0}{\u{2003}\"x\": 1}}".as_bytes(),
    "{\"plan_holds\":\u{2003}{\u{a0}}}".as_bytes(),
    "{\"plan_holds\":\u{e9}{\"x\": 1}}".as_bytes(),
    "{\"\u{1f600}\": \"\u{e9}\u{2003}\", \"plan_holds\": {\"\u{e9}\": 1}, \"plan_snaps\": {}}"
        .as_bytes(),
    b"{\"n\": \"\\\"plan_holds\\\": {\\\"x\\\"\", \"plan_holds\": {}}",
    b"{\"plan_holds\": {}, \"versions\": {\"plan_holds\": {\"x\": 1}}}",
    b"{\"plan_holds\": {\"x\": 1}, \"plan_snaps\": {\"e\": {}}}",
    b"{\"plan_snaps\"",
    b"plan_snaps \"plan_snap\" \"plan_holds\"",
    // not UTF-8: a bad byte before the key, inside the text after it, after the decision, and a character cut by the file's end
    b"{\"d\": \"\xff\", \"plan_holds\": {\"h\": 1}, \"plan_snaps\": {}}",
    b"{\"plan_holds\": \xff{\"h\": 1}}",
    b"{\"plan_holds\": {\"h\": \"\xc3(\"}, \"plan_snaps\": {}}",
    b"{\"plan_holds\": {\"h\": 1}, \"plan_snaps\": {}, \"v\": \"\xe2\x82\"}",
    b"{\"plan_holds\": {\"h\xc3",
    b"{\"plan_holds\": {}, \"v\": \"\xff\"}",
];

#[test]
fn the_stream_answers_as_the_whole_string_did_at_every_chunk_size() {
    for case in CASES {
        for chunk in 1..=case.len() + 2 {
            assert_eq!(new(case, chunk), old(case), "{case:?} chunk {chunk}");
        }
    }
}

/// A reader that counts what it is asked for and gives.
struct Counted<'a> {
    inner: Cursor<&'a [u8]>,
    widest: &'a Cell<usize>,
    given: &'a Cell<usize>,
}

impl Read for Counted<'_> {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        self.widest.set(self.widest.get().max(buf.len()));
        let n = self.inner.read(buf)?;
        self.given.set(self.given.get() + n);
        Ok(n)
    }
}

#[test]
fn the_read_holds_one_chunk_and_stops_early_only_on_a_no() {
    for (holds, want, whole) in [("{\"h\": 1}", true, true), ("{}", false, false)] {
        let mut state = vec![b'x'; 2_000_000];
        state.extend_from_slice(format!("\"plan_holds\": {holds}").as_bytes());
        state.extend(vec![b'y'; 600_000]);
        let (widest, given) = (Cell::new(0), Cell::new(0));
        let mut r = Counted {
            inner: Cursor::new(&state),
            widest: &widest,
            given: &given,
        };
        assert_eq!(after_first(&mut r, HOLDS, CHUNK, &held_after), want);
        assert!(widest.get() <= CHUNK, "{}", widest.get());
        assert_eq!(given.get() == state.len(), whole);
    }
}

/// A reader that gives what it holds and then fails.
struct Failing<'a>(Cursor<&'a [u8]>);

impl Read for Failing<'_> {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        match self.0.read(buf)? {
            0 => Err(std::io::Error::other("t508")),
            n => Ok(n),
        }
    }
}

fn failing(state: &[u8], chunk: usize) -> bool {
    after_first(&mut Failing(Cursor::new(state)), HOLDS, chunk, &held_after)
}

#[test]
fn a_failed_read_is_no_hold() {
    assert!(!failing(b"", 4));
    // the key fills the first chunk exactly, and the read fails before what follows it says anything
    assert!(!failing(HOLDS, HOLDS.len()));
    // what follows says yes, and the read fails before the rest is checked
    assert!(!failing(b"\"plan_holds\": {\"h\"", 18));
}

#[test]
fn a_decision_never_given_is_no() {
    let none = |_: &str, _: bool| None;
    assert!(!after_first(
        &mut Cursor::new(b"\"plan_holds\": {}"),
        HOLDS,
        4,
        &none
    ));
}

#[test]
fn the_files_are_read_and_a_missing_one_holds_nothing() {
    let d = crate::tempdir::TempDir::new("t508-scan");
    let p = d.path().join("checks-open.json");
    assert!(!holds(&p) && !snaps(&p));
    let both = "{\n \"plan_holds\": {\n  \"h\": {}\n },\n \"plan_snaps\": {}\n}";
    std::fs::write(&p, both).unwrap();
    assert!(holds(&p) && snaps(&p));
    std::fs::write(&p, "{\n \"plan_holds\": {}\n}").unwrap();
    assert!(!holds(&p) && !snaps(&p));
}
