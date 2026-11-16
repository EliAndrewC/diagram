//! `bytes.decode(name)` for the charsets `quote_verbatim.decode` tries (feature 449 T145): `CPython`'s own strict decoders, read from
//! `codecs.tsv`, which was generated once from `CPython` 3.14.4's codecs (the `html5_entities.tsv` pattern). WHY NOT A CRATE: `encoding_rs`
//! decodes by the WHATWG tables, and measured over every one- and two-byte sequence it differed from `CPython` on 7,441 of them - 1,556
//! `cp932` sequences it refused, 457 `euc_jp`, 258 `gb18030` and 4,884 `big5` sequences `CPython` refuses that it read, and 286 read as
//! other characters (observed 2026-11-16, method: scratchpad `t145/encprobe`) - and a quotation decoded otherwise is judged otherwise.
//!
//! The names: `CPython` lower-cases a name, folds each run of other characters than letters, digits and `.` to one `_`
//! (`encodings.normalize_encoding`), and looks it up among its aliases; held here are the aliases of the codecs below. A page declares a
//! charset outside them nowhere in the archive (3,364 captured pages, observed 2026-11-16: `utf-8`, `utf8`, `shift_jis`, `shift-jis`,
//! `x-sjis`, `windows-31j`, `iso-8859-1`, `euc-jp`, `gb2312`, `windows-1252`, `us-ascii`); such a name is read as one `CPython` cannot find,
//! and the next charset is tried, a difference from the Python only on a page that declares one.

use std::collections::HashMap;
use std::sync::LazyLock;

const TABLES: &str = include_str!("codecs.tsv");

/// One codec of the table: its single bytes and its sequences by prefix.
#[derive(Default)]
struct Table {
    single: HashMap<u8, char>,
    rows: HashMap<Vec<u8>, (u8, Vec<Option<char>>)>,
    pointers: Vec<(u32, u32, u32)>,
}

impl Table {
    fn seq(&self, prefix: &[u8], last: u8) -> Option<char> {
        let (first, cells) = self.rows.get(prefix)?;
        let at = usize::from(last.checked_sub(*first)?);
        cells.get(at).copied().flatten()
    }

    /// gb18030's four-byte form: its pointer, then the run that holds it.
    fn four(&self, b: &[u8]) -> Option<char> {
        let ok = |x: u8, lo: u8, hi: u8| (lo..=hi).contains(&x);
        if !(ok(b[0], 0x81, 0xfe)
            && ok(b[1], 0x30, 0x39)
            && ok(b[2], 0x81, 0xfe)
            && ok(b[3], 0x30, 0x39))
        {
            return None;
        }
        let p = ((u32::from(b[0] - 0x81) * 10 + u32::from(b[1] - 0x30)) * 126
            + u32::from(b[2] - 0x81))
            * 10
            + u32::from(b[3] - 0x30);
        let at = self.pointers.partition_point(|r| r.0 <= p).checked_sub(1)?;
        let (start, cp, n) = self.pointers[at];
        (p < start + n)
            .then(|| char::from_u32(cp + p - start))
            .flatten()
    }
}

struct Codecs {
    tables: HashMap<&'static str, Table>,
    aliases: HashMap<&'static str, &'static str>,
}

fn hex(h: &str) -> Option<u32> {
    u32::from_str_radix(h, 16).ok()
}

static CODECS: LazyLock<Codecs> = LazyLock::new(|| {
    let mut tables: HashMap<&str, Table> = HashMap::new();
    let mut aliases = HashMap::new();
    for line in TABLES.lines().filter(|l| !l.starts_with('#')) {
        let cells: Vec<&str> = line.split('\t').collect();
        if cells[0] == "alias" {
            aliases.insert(cells[1], cells[2]);
            continue;
        }
        let table = tables.entry(cells[0]).or_default();
        let first = hex(cells[2]).unwrap_or(0);
        if cells[1] == "p" {
            let (cp, n) = (hex(cells[3]).unwrap_or(0), hex(cells[4]).unwrap_or(0));
            table.pointers.push((first, cp, n));
            continue;
        }
        let points: Vec<Option<char>> = cells[3]
            .split(' ')
            .map(|c| hex(c).and_then(char::from_u32))
            .collect();
        let first = u8::try_from(first).unwrap_or(0);
        if cells[1] == "-" {
            for (i, c) in points.iter().enumerate() {
                if let (Some(c), Ok(i)) = (c, u8::try_from(i)) {
                    table.single.insert(first + i, *c);
                }
            }
        } else {
            let prefix: Vec<u8> = (0..cells[1].len() / 2)
                .filter_map(|i| u8::from_str_radix(&cells[1][2 * i..2 * i + 2], 16).ok())
                .collect();
            table.rows.insert(prefix, (first, points));
        }
    }
    Codecs { tables, aliases }
});

/// `encodings.normalize_encoding` of a lower-cased name.
fn normalized(name: &str) -> String {
    let mut out = String::new();
    let mut punct = false;
    for c in name.chars() {
        if c.is_alphanumeric() || c == '.' {
            if punct && !out.is_empty() {
                out.push('_');
            }
            if c.is_ascii() {
                out.push(c.to_ascii_lowercase());
            }
            punct = false;
        } else {
            punct = true;
        }
    }
    out
}

/// The codec `CPython` finds under `name`, among those held here.
#[must_use]
pub fn lookup(name: &str) -> Option<&'static str> {
    let norm = normalized(name);
    let aliases = &CODECS.aliases;
    aliases
        .get(norm.as_str())
        .or_else(|| aliases.get(norm.replace('.', "_").as_str()))
        .copied()
}

/// `raw.decode(name)`, strict: None where `CPython` raises (`LookupError` or `UnicodeDecodeError`).
#[must_use]
pub fn decode(raw: &[u8], name: &str) -> Option<String> {
    match lookup(name)? {
        "utf_8" => std::str::from_utf8(raw).ok().map(str::to_owned),
        "ascii" => raw
            .is_ascii()
            .then(|| String::from_utf8_lossy(raw).into_owned()),
        "latin_1" => Some(raw.iter().map(|&b| char::from(b)).collect()),
        codec => table_decode(CODECS.tables.get(codec)?, raw),
    }
}

fn table_decode(t: &Table, raw: &[u8]) -> Option<String> {
    let mut out = String::with_capacity(raw.len());
    let mut i = 0;
    while i < raw.len() {
        let b = raw[i];
        if let Some(c) = t.single.get(&b) {
            out.push(*c);
            i += 1;
        } else if let Some(c) = raw.get(i + 1).and_then(|&n| t.seq(&[b], n)) {
            out.push(c);
            i += 2;
        } else if let Some(c) = raw.get(i + 2).and_then(|&n| t.seq(&raw[i..i + 2], n)) {
            out.push(c);
            i += 3;
        } else if let Some(c) = raw.get(i..i + 4).and_then(|four| t.four(four)) {
            out.push(c);
            i += 4;
        } else {
            return None;
        }
    }
    Some(out)
}

#[cfg(test)]
mod tests;
