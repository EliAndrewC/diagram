//! The download list's grammar (feature 313 plan D2): an entry is a `### <id>. <title>` heading and the lines up to the next heading; directly under the
//! heading a blank line and the three mark lines, then once marks are recorded a `- Marks recorded <date>` line; the rest is the entry's body.

use std::collections::HashMap;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::compiled;

/// `[...]` with Python's `\s`, which also takes the four separators `\x1c`-`\x1f`.
const BOX: &str = r"\[[\s\x1c-\x1f]*([xX]?)[\s\x1c-\x1f]*\]";
/// The states `MARK=<id>=<state>` may name for marks the GM ticked in contradiction.
pub(super) const RESOLVE_STATES: [&str; 4] = ["downloaded", "partial", "paywalled", "not-found"];

pub(super) static HEAD: LazyLock<Regex> = LazyLock::new(|| compiled(r"^### (H?\d+)\. "));
static ANY_HEADING: LazyLock<Regex> = LazyLock::new(|| compiled(r"^#{1,3} "));
static MARK1: LazyLock<Regex> = LazyLock::new(|| {
    compiled(&format!(
        r"^- Mark: {BOX} downloaded \| {BOX} partial \(abstract or excerpt\) \| {BOX} paywalled \| {BOX} not found[\s\x1c-\x1f]*$"
    ))
});
static MARK2: LazyLock<Regex> = LazyLock::new(|| {
    compiled(&format!(
        r"^- {BOX} Found elsewhere \(only with downloaded or partial\) - where:(.*)$"
    ))
});
static MARK3: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"^- Saved as \(optional, the file's name\):(.*)$"));
pub static RECORDED: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"^- Marks recorded (\d{4}-\d{2}-\d{2})\b.*$"));

/// Python's `str.strip()`: what `char::is_whitespace` strips and the four separators it leaves.
#[must_use]
pub fn strip(text: &str) -> &str {
    text.trim_matches(|c: char| c.is_whitespace() || ('\x1c'..='\x1f').contains(&c))
}

/// Python's `str.split()`.
#[must_use]
pub fn words(text: &str) -> Vec<&str> {
    text.split(|c: char| c.is_whitespace() || ('\x1c'..='\x1f').contains(&c))
        .filter(|w| !w.is_empty())
        .collect()
}

/// The GM's marks on one entry.
#[expect(clippy::struct_excessive_bools, reason = "the five boxes the GM ticks")]
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Marks {
    pub downloaded: bool,
    pub partial: bool,
    pub paywalled: bool,
    pub not_found: bool,
    pub elsewhere: bool,
    pub where_from: String,
    pub saved: String,
}

fn tick(on: bool) -> char {
    if on {
        'x'
    } else {
        ' '
    }
}

fn tail(words: &str, value: &str) -> String {
    if value.is_empty() {
        words.to_owned()
    } else {
        format!("{words} {value}")
    }
}

impl Marks {
    #[must_use]
    pub fn lines(&self) -> [String; 3] {
        [
            format!(
                "- Mark: [{}] downloaded | [{}] partial (abstract or excerpt) | [{}] paywalled | [{}] not found",
                tick(self.downloaded),
                tick(self.partial),
                tick(self.paywalled),
                tick(self.not_found)
            ),
            tail(
                &format!(
                    "- [{}] Found elsewhere (only with downloaded or partial) - where:",
                    tick(self.elsewhere)
                ),
                &self.where_from,
            ),
            tail("- Saved as (optional, the file's name):", &self.saved),
        ]
    }

    #[must_use]
    pub fn any(&self) -> bool {
        self.downloaded || self.partial || self.paywalled || self.not_found || self.elsewhere
    }

    /// Why these marks contradict themselves (spec FR-005), else "".
    pub(super) fn problem(&self) -> &'static str {
        if self.elsewhere && !(self.downloaded || self.partial) {
            return "found elsewhere is ticked without downloaded or partial - it says where a copy you have came from";
        }
        if self.not_found && (self.downloaded || self.partial || self.paywalled) {
            return "not found is ticked with downloaded, partial or paywalled - it means nothing was found";
        }
        ""
    }

    /// These marks with the one state the GM named in place of the ones they ticked (`MARK=`); a copy only had leaves where it came from and the file's name.
    pub(super) fn resolved(&self, state: &str) -> Result<Self, String> {
        if !RESOLVE_STATES.contains(&state) {
            return Err(format!(
                "MARK= takes one of {}, not {}",
                RESOLVE_STATES.join(", "),
                crate::checks::py_repr(&state.into())
            ));
        }
        let have = matches!(state, "downloaded" | "partial");
        Ok(Self {
            downloaded: state == "downloaded",
            partial: state == "partial",
            paywalled: state == "paywalled",
            not_found: state == "not-found",
            elsewhere: self.elsewhere && have,
            where_from: if have {
                self.where_from.clone()
            } else {
                String::new()
            },
            saved: if have {
                self.saved.clone()
            } else {
                String::new()
            },
        })
    }
}

/// One entry of the list.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Entry {
    pub id: String,
    pub heading: String,
    pub marks: Option<Marks>,
    pub recorded: Option<String>,
    pub body: Vec<String>,
}

impl Entry {
    pub(super) fn lines(&self) -> Vec<String> {
        let mut out = vec![self.heading.clone()];
        if let Some(marks) = &self.marks {
            out.push(String::new());
            out.extend(marks.lines());
            out.extend(self.recorded.clone());
        }
        out.extend(self.body.iter().cloned());
        out
    }

    #[must_use]
    pub fn body_text(&self) -> String {
        self.body.join("\n")
    }

    /// The heading and the body, as the comparison reads an entry.
    pub(super) fn whole(&self) -> String {
        format!("{}\n{}", self.heading, self.body_text())
    }
}

/// A run of text, or an entry.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Block {
    Text(String),
    Item(Entry),
}

fn head_id(line: &str) -> Option<String> {
    HEAD.captures(line).ok().flatten().map(|c| c[1].to_owned())
}

fn is_match(pattern: &Regex, line: &str) -> bool {
    pattern.is_match(line).unwrap_or(false)
}

/// The three mark lines, or None where they are not there in their form.
fn parse_marks(lines: &[&str]) -> Option<Marks> {
    let first = MARK1.captures(lines[0]).ok().flatten()?;
    let second = MARK2.captures(lines[1]).ok().flatten()?;
    let third = MARK3.captures(lines[2]).ok().flatten()?;
    let on = |n: usize| !first[n].is_empty();
    Some(Marks {
        downloaded: on(1),
        partial: on(2),
        paywalled: on(3),
        not_found: on(4),
        elsewhere: !second[1].is_empty(),
        where_from: strip(&second[2]).to_owned(),
        saved: strip(&third[1]).to_owned(),
    })
}

fn owned(lines: &[&str]) -> Vec<String> {
    lines.iter().map(|l| (*l).to_owned()).collect()
}

fn make_entry(lines: &[&str]) -> Entry {
    let id = head_id(lines[0]).unwrap_or_default();
    let heading = lines[0].to_owned();
    let marks = if lines.len() >= 5 && lines[1].is_empty() {
        parse_marks(&lines[2..5])
    } else {
        None
    };
    let Some(marks) = marks else {
        return Entry {
            id,
            heading,
            marks: None,
            recorded: None,
            body: owned(&lines[1..]),
        };
    };
    let rest = &lines[5..];
    let recorded = rest
        .first()
        .filter(|l| is_match(&RECORDED, l))
        .map(|l| (*l).to_owned());
    let body = owned(if recorded.is_some() { &rest[1..] } else { rest });
    Entry {
        id,
        heading,
        marks: Some(marks),
        recorded,
        body,
    }
}

/// The list as text runs and entries, in order; `render(parse(t)) == t` for any text.
#[must_use]
pub fn parse(text: &str) -> Vec<Block> {
    let mut blocks = Vec::new();
    let mut run: Vec<&str> = Vec::new();
    let mut open: Option<Vec<&str>> = None;
    for line in text.split('\n') {
        if head_id(line).is_some() {
            blocks.extend(open.take().map(|l| Block::Item(make_entry(&l))));
            if !run.is_empty() {
                blocks.push(Block::Text(run.join("\n")));
                run.clear();
            }
            open = Some(vec![line]);
        } else if open.is_some() && is_match(&ANY_HEADING, line) {
            blocks.extend(open.take().map(|l| Block::Item(make_entry(&l))));
            run = vec![line];
        } else if let Some(lines) = open.as_mut() {
            lines.push(line);
        } else {
            run.push(line);
        }
    }
    blocks.extend(open.take().map(|l| Block::Item(make_entry(&l))));
    if !run.is_empty() {
        blocks.push(Block::Text(run.join("\n")));
    }
    blocks
}

pub(super) fn render(blocks: &[Block]) -> String {
    blocks
        .iter()
        .map(|b| match b {
            Block::Text(text) => text.clone(),
            Block::Item(entry) => entry.lines().join("\n"),
        })
        .collect::<Vec<_>>()
        .join("\n")
}

impl Block {
    fn item(&self) -> Option<&Entry> {
        match self {
            Self::Item(entry) => Some(entry),
            Self::Text(_) => None,
        }
    }

    pub(super) fn item_mut(&mut self) -> Option<&mut Entry> {
        match self {
            Self::Item(entry) => Some(entry),
            Self::Text(_) => None,
        }
    }
}

pub fn entries(blocks: &[Block]) -> impl Iterator<Item = &Entry> {
    blocks.iter().filter_map(Block::item)
}

/// A dict of the entries by id: the ids in first-seen order, and each id's block - the last entry of that id, as a later key overwrites in Python.
pub(super) fn by_id(blocks: &[Block]) -> (Vec<String>, HashMap<String, usize>) {
    let mut order = Vec::new();
    let mut at = HashMap::new();
    for (i, block) in blocks.iter().enumerate() {
        if let Block::Item(entry) = block {
            if at.insert(entry.id.clone(), i).is_none() {
                order.push(entry.id.clone());
            }
        }
    }
    (order, at)
}

/// The entry at a block `by_id` named.
pub(super) fn entry_at(blocks: &mut [Block], index: usize) -> &mut Entry {
    blocks[index]
        .item_mut()
        .unwrap_or_else(|| unreachable!("by_id names entries"))
}

pub(super) fn entry_ref(blocks: &[Block], index: usize) -> &Entry {
    blocks[index]
        .item()
        .unwrap_or_else(|| unreachable!("by_id names entries"))
}
