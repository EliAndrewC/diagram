//! What the research record's tools share (feature 449 T79-T88, from `record.rs`, split out by T92): a reply, a flag's value, Python's
//! `splitlines` and `read_text`, and the modules every record tool reads through - the git and Python seams (`repo`), argparse's reading
//! (`args`), a delta's units (`units`), the bundles' helpers and runner (`bundle`).

use std::io::ErrorKind;
use std::path::Path;

use crate::Reply;

pub mod args;
pub mod bundle;
pub mod repo;
#[cfg(any(test, feature = "testkit"))]
pub mod testkit;
pub mod units;

#[must_use]
pub fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// The value after `name` in `args`, or "".
#[must_use]
pub fn flag<'a>(args: &'a [String], name: &str) -> &'a str {
    args.windows(2)
        .find(|w| w[0] == name)
        .map_or("", |w| w[1].as_str())
}

/// `text` split as Python's `str.splitlines` splits it, so a form feed still ends a line and a line number means what it did.
#[must_use]
pub fn py_lines(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    let mut chars = text.char_indices().peekable();
    while let Some((i, c)) = chars.next() {
        if matches!(
            c,
            '\n' | '\r'
                | '\u{b}'
                | '\u{c}'
                | '\u{1c}'
                | '\u{1d}'
                | '\u{1e}'
                | '\u{85}'
                | '\u{2028}'
                | '\u{2029}'
        ) {
            out.push(&text[start..i]);
            if c == '\r' && chars.peek().is_some_and(|(_, n)| *n == '\n') {
                chars.next();
            }
            start = chars.peek().map_or(text.len(), |(n, _)| *n);
        }
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

/// The first `n` characters of `text`.
#[must_use]
pub fn first_chars(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

/// `Path.read_text(encoding="utf-8")`: strict UTF-8, and universal newlines, so a file this rewrites comes out with Python's line ends.
///
/// # Errors
///
/// The read's failure, or `InvalidData` where the bytes are not UTF-8.
pub fn read_text(path: &Path) -> std::io::Result<String> {
    let text = String::from_utf8(std::fs::read(path)?).map_err(|_| ErrorKind::InvalidData)?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

#[cfg(test)]
mod tests {
    use super::{first_chars, flag, py_lines, read_text, reply};

    #[test]
    fn the_shared_readers_read_as_python_reads() {
        assert_eq!(py_lines("a\nb\r\nc\rd\x0ce"), ["a", "b", "c", "d", "e"]);
        assert_eq!(py_lines("a\n"), ["a"]);
        assert_eq!(first_chars("abc", 2), "ab");
        let args = ["--a".to_owned(), "x".to_owned()];
        assert_eq!(flag(&args, "--a"), "x");
        assert_eq!(flag(&args, "--b"), "");
        assert_eq!(reply(String::new(), String::new(), 3).code, 3);
        let dir = crate::checks::scratch("core-record");
        std::fs::write(dir.join("t.txt"), "a\r\nb\rc").unwrap();
        assert_eq!(read_text(&dir.join("t.txt")).unwrap(), "a\nb\nc");
        std::fs::write(dir.join("bad.txt"), [0xff_u8]).unwrap();
        assert!(read_text(&dir.join("bad.txt")).is_err());
        assert!(read_text(&dir.join("none.txt")).is_err());
    }
}
