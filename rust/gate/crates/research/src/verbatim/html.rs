//! The visible text of a page as `quote_verbatim._Visible` read it (feature 449 T145): `CPython` 3.14.4's `html.parser.HTMLParser`
//! (`convert_charrefs=True`), fed the page once and closed, with only what `_Visible` handles - the data, and the start and end tags that
//! open or close a skipped element or a block. Ported from the installed `/usr/lib/python3.14/html/parser.py` line by line, not from
//! memory: 3.14 reads `script`, `style` and their kin as raw text, a comment closes at `--!>`, and an unterminated construct at the end
//! is dropped, each of which decides what text a quotation is matched against. What the parser reports and `_Visible` ignores (comments,
//! declarations, processing instructions, attributes' values) is skipped over exactly as the parser skips it, never reported.

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::html_text::unescape;
use l7r_shared::py_text::strip;

fn re(pattern: &str) -> Regex {
    crate::re(pattern)
}

const SKIP: [&str; 3] = ["script", "style", "noscript"];
const BLOCK: [&str; 23] = [
    "p",
    "div",
    "br",
    "li",
    "ul",
    "ol",
    "tr",
    "td",
    "th",
    "table",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "section",
    "article",
    "blockquote",
    "dd",
    "dt",
    "pre",
    "figcaption",
];
const CDATA: [&str; 7] = [
    "script",
    "style",
    "xmp",
    "iframe",
    "noembed",
    "noframes",
    "plaintext",
];
const RCDATA: [&str; 2] = ["textarea", "title"];

static STARTTAGOPEN: LazyLock<Regex> = LazyLock::new(|| re(r"^<[a-zA-Z]"));
static ENDTAGOPEN: LazyLock<Regex> = LazyLock::new(|| re(r"^</[a-zA-Z]"));
static COMMENTCLOSE: LazyLock<Regex> = LazyLock::new(|| re(r"--!?>"));
static COMMENTABRUPT: LazyLock<Regex> = LazyLock::new(|| re(r"^-?>"));
/// `[\t\n\r\f ]`, the parser's whitespace.
fn ws(b: u8) -> bool {
    matches!(b, b'\t' | b'\n' | b'\r' | 0x0c | b' ')
}

/// THE TAG PATTERNS SCANNED BY HAND (feature 449 T145): `tagfind_tolerant`, `attrfind_tolerant` and `locatetagend` as regular expressions
/// were run anchored at a tag through the regex crate's backtracking engine, which scanned the rest of the page from every start it was
/// handed - a whole page's tags cost its length squared (two seconds for one Wikipedia page, the T145 differential's archive sweep). Each
/// is a run of classes with one place a backtrack changes the match - a quoted value with no closing quote after whitespace, read as an
/// empty bare value one whitespace earlier - and is written out here, byte for byte (every delimiter is ASCII, so a UTF-8 byte never is one).
fn run_while(b: &[u8], mut at: usize, keep: impl Fn(u8) -> bool) -> usize {
    while at < b.len() && keep(b[at]) {
        at += 1;
    }
    at
}

/// `[\t\n\r\f ]*=[\t\n\r\f ]*('[^']*'|"[^"]*"|(?!['"])[^>\t\n\r\f ]*)` at `at`: its end, or None where it does not match.
fn value_end(b: &[u8], at: usize) -> Option<usize> {
    let eq = run_while(b, at, ws);
    if b.get(eq) != Some(&b'=') {
        return None;
    }
    let start = run_while(b, eq + 1, ws);
    match b.get(start) {
        Some(&q @ (b'\'' | b'"')) => match b[start + 1..].iter().position(|&c| c == q) {
            Some(close) => Some(start + 1 + close + 1),
            // no closing quote: one whitespace given back, an empty bare value there
            None => (start > eq + 1).then_some(start - 1),
        },
        _ => Some(run_while(b, start, |c| c != b'>' && !ws(c))),
    }
}

/// `(?:[\t\n\r\f ]|/(?!>))*` at `at`.
fn gap_end(b: &[u8], mut at: usize) -> usize {
    while at < b.len() && (ws(b[at]) || (b[at] == b'/' && b.get(at + 1) != Some(&b'>'))) {
        at += 1;
    }
    at
}

/// An attribute's name, `[^\t\n\r\f />][^\t\n\r\f /=>]*`, at `at`: its end, or None.
fn name_end(b: &[u8], at: usize) -> Option<usize> {
    let first = *b.get(at)?;
    (!ws(first) && first != b'/' && first != b'>')
        .then(|| run_while(b, at + 1, |c| !ws(c) && !matches!(c, b'/' | b'=' | b'>')))
}

/// `tagfind_tolerant` at `at` (a letter there): the tag name's end and the match's end.
fn tagfind(raw: &str, at: usize) -> (usize, usize) {
    let b = raw.as_bytes();
    let name = run_while(b, at + 1, |c| !ws(c) && c != b'/' && c != b'>');
    (name, gap_end(b, name))
}

/// `attrfind_tolerant` at `at`, its look-behind tested by the caller: the match's end, or None.
fn attrfind(raw: &str, at: usize) -> Option<usize> {
    let b = raw.as_bytes();
    let name = name_end(b, at)?;
    Some(gap_end(b, value_end(b, name).unwrap_or(name)))
}

/// `locatetagend` at `at` (a letter there): the match's end.
fn locatetagend(raw: &str, at: usize) -> usize {
    let b = raw.as_bytes();
    let mut k = run_while(
        b,
        run_while(b, at + 1, |c| !ws(c) && c != b'/' && c != b'>'),
        |c| ws(c) || c == b'/',
    );
    while k > 0
        && matches!(
            b[k - 1],
            b'\'' | b'"' | b'\t' | b'\n' | b'\r' | 0x0c | b' ' | b'/'
        )
    {
        let Some(name) = name_end(b, k) else { break };
        k = run_while(b, value_end(b, name).unwrap_or(name), |c| {
            ws(c) || c == b'/'
        });
    }
    k + usize::from(b.get(k) == Some(&b'>'))
}

/// The end of `pattern` matched at `at` (Python's `pattern.match(rawdata, at)`).
fn match_end(pattern: &Regex, raw: &str, at: usize) -> Option<usize> {
    pattern
        .find(raw.get(at..).unwrap_or(""))
        .ok()
        .flatten()
        .map(|m| at + m.end())
}

/// `set_cdata_mode`'s `interesting`: the element's end tag, its letters matched in either case (`re.IGNORECASE | re.ASCII`).
fn closing(tag: &str) -> Regex {
    let letters = tag.chars().fold(String::new(), |mut l, c| {
        let _ = write!(l, "[{}{}]", c.to_ascii_lowercase(), c.to_ascii_uppercase());
        l
    });
    re(&format!("</{letters}(?=[\\t\\n\\r\\x0c />])"))
}

/// What `_Visible` keeps, and the parser's state between `feed` and `close`.
#[derive(Default)]
struct Parser {
    out: String,
    skip: usize,
    cdata: Option<(String, bool)>,
}

impl Parser {
    fn data(&mut self, text: &str) {
        if self.skip == 0 {
            self.out.push_str(text);
        }
    }

    fn start(&mut self, tag: &str) {
        if SKIP.contains(&tag) {
            self.skip += 1;
        } else if BLOCK.contains(&tag) {
            self.out.push(' ');
        }
    }

    fn end(&mut self, tag: &str) {
        if SKIP.contains(&tag) {
            self.skip = self.skip.saturating_sub(1);
        } else if BLOCK.contains(&tag) {
            self.out.push(' ');
        }
    }

    /// Text found between constructs, unescaped unless a raw-text element holds it.
    fn text(&mut self, raw: &str) {
        let escapable = self.cdata.as_ref().is_none_or(|c| c.1);
        if escapable {
            self.data(&unescape(raw));
        } else {
            self.data(raw);
        }
    }

    /// `parse_starttag`: the end of a whole start tag, or None while it is unterminated.
    fn starttag(&mut self, raw: &str, i: usize) -> Option<usize> {
        let endpos = locatetagend(raw, i + 1);
        if !raw[..endpos].ends_with('>') {
            return None;
        }
        let (name, mut k) = tagfind(raw, i + 1);
        let tag = raw[i + 1..name].to_lowercase();
        while k < endpos {
            let after = matches!(
                raw.as_bytes()[k - 1],
                b'\'' | b'"' | b'\t' | b'\n' | b'\r' | 0x0c | b' ' | b'/'
            );
            match attrfind(raw, k).filter(|_| after) {
                Some(next) => k = next,
                None => break,
            }
        }
        let end = strip(&raw[k..endpos]);
        // JUNK BEFORE THE `>` is the tag's own text, as the parser handed it over; never met in 3.14 (the tag-end and attribute patterns
        // read one grammar - 400,000 random tags, none, observed 2026-11-16), and kept because the Python keeps it
        let junk = end != ">" && end != "/>";
        self.data(&raw[i..if junk { endpos } else { i }]);
        // junk opens nothing: no tag is named, so nothing is skipped, spaced or read raw after it
        let tag = if junk { String::new() } else { tag };
        self.start(&tag);
        if end.ends_with("/>") {
            self.end(&tag);
        } else if CDATA.contains(&tag.as_str()) {
            self.cdata = Some((tag, false));
        } else if RCDATA.contains(&tag.as_str()) {
            self.cdata = Some((tag, true));
        }
        Some(endpos)
    }

    /// `parse_endtag`: the end of a whole end tag (one with no name ignored or read as a comment), or None while unterminated.
    fn endtag(&mut self, raw: &str, i: usize) -> Option<usize> {
        raw[i + 2..].find('>')?;
        if match_end(&ENDTAGOPEN, raw, i).is_none() {
            if raw[i + 2..].starts_with('>') {
                return Some(i + 3);
            }
            return raw[i + 2..].find('>').map(|p| i + 2 + p + 1);
        }
        let j = locatetagend(raw, i + 2);
        if !raw[..j].ends_with('>') {
            return None;
        }
        let tag = raw[i + 2..tagfind(raw, i + 2).0].to_lowercase();
        self.end(&tag);
        self.cdata = None;
        Some(j)
    }

    /// The construct opening with `<` at `i`: its end, or None while it is unterminated.
    fn construct(&mut self, raw: &str, i: usize) -> Option<usize> {
        let rest = &raw[i..];
        let find =
            |what: &str, from: usize| raw.get(from..).and_then(|r| r.find(what)).map(|p| from + p);
        if match_end(&STARTTAGOPEN, raw, i).is_some() {
            self.starttag(raw, i)
        } else if rest.starts_with("</") {
            self.endtag(raw, i)
        } else if rest.starts_with("<!--") {
            let at = i + 4;
            match COMMENTCLOSE.find(&raw[at..]).ok().flatten() {
                Some(m) => Some(at + m.end()),
                None => match_end(&COMMENTABRUPT, raw, at),
            }
        } else if rest.starts_with("<?") {
            find(">", i + 2).map(|j| j + 1)
        } else if rest.starts_with("<![CDATA[") {
            find("]]>", i + 9).map(|j| j + 3)
        } else if rest
            .get(..9)
            .is_some_and(|d| d.eq_ignore_ascii_case("<!doctype"))
        {
            find(">", i + 9).map(|j| j + 1)
        } else {
            find(">", i + 2).map(|j| j + 1)
        }
    }

    /// `goahead(end)` over `raw`: what is left unparsed.
    fn goahead(&mut self, raw: &str, end: bool) -> String {
        let n = raw.len();
        let mut i = 0;
        while i < n {
            let j = match &self.cdata {
                None => {
                    if let Some(p) = raw[i..].find('<') {
                        i + p
                    } else {
                        // a charref cut in half at the end waits for more text: an `&` among the last 34 characters with no space or
                        // `;` after it
                        let from = raw[i..]
                            .char_indices()
                            .rev()
                            .nth(33)
                            .map_or(i, |(p, _)| i + p);
                        let amp = raw[from..].rfind('&').map(|p| from + p);
                        if amp.is_some_and(|a| {
                            !raw[a..].contains(['\t', '\n', '\r', '\x0c', ' ', ';'])
                        }) {
                            break;
                        }
                        n
                    }
                }
                Some((tag, _)) if tag == "plaintext" => n,
                Some((tag, _)) => match closing(tag).find(&raw[i..]).ok().flatten() {
                    Some(m) => i + m.start(),
                    None => break,
                },
            };
            if i < j {
                self.text(&raw[i..j]);
            }
            i = j;
            if i == n {
                break;
            }
            let rest = &raw[i..];
            let k = if rest.starts_with('<')
                && (match_end(&STARTTAGOPEN, raw, i).is_some()
                    || rest[1..].starts_with(['/', '!', '?']))
            {
                self.construct(raw, i)
            } else if i + 1 < n || end {
                self.data("<");
                Some(i + 1)
            } else {
                break;
            };
            match k {
                Some(k) => i = k,
                None if !end => break,
                None => {
                    if rest.starts_with("</") && i + 2 == n {
                        self.data("</");
                    }
                    i = n;
                }
            }
        }
        if end && i < n {
            self.text(&raw[i..n]);
            i = n;
        }
        raw[i..].to_owned()
    }
}

/// `_Visible`'s text of `markup`, before `squeeze`: no script, style or comment; a space at every block boundary.
#[must_use]
pub fn visible(markup: &str) -> String {
    let mut p = Parser::default();
    let rest = p.goahead(markup, false);
    p.goahead(&rest, true);
    p.out
}

#[cfg(test)]
mod tests;
