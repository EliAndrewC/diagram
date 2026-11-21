//! The three facts `hookdeps.py` asked Python's `ast` for, read without Python (feature 449 T050): which lines hold a docstring, what a file imports, and
//! the string constants of its code. A lexer rather than a parser: every fact here is decided by tokens and logical lines, and the port was held to the
//! Python's own answers over the whole repository before that was deleted (`m:t050-deps-differential`).

use std::collections::BTreeSet;
use std::mem::take;

/// What a Python file says, or None for what `ast.parse` could not read either (an unterminated string, an unbalanced bracket).
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Facts {
    /// The lines of every docstring (of the module, a function, a class).
    pub docstring_lines: BTreeSet<usize>,
    /// The last part of each module imported, and each name a `from` import takes.
    pub imported: Vec<String>,
    /// Every string constant of the code, adjacent literals joined, an f-string's literal parts each its own.
    pub strings: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum Kind {
    Name(String),
    Op(char),
    Newline,
    Str {
        pieces: Vec<String>,
        bytes: bool,
        plain: bool,
    },
}

#[derive(Debug, Clone)]
struct Tok {
    kind: Kind,
    first: usize,
    last: usize,
}

const PREFIXES: [&str; 11] = ["r", "u", "b", "br", "rb", "f", "fr", "rf", "t", "tr", "rt"];

fn is_name(c: char) -> bool {
    c.is_alphanumeric() || c == '_' || !c.is_ascii()
}

struct Lexer {
    text: Vec<char>,
    at: usize,
    line: usize,
    strings: Vec<String>,
}

impl Lexer {
    fn peek(&self, n: usize) -> Option<char> {
        self.text.get(self.at + n).copied()
    }

    fn bump(&mut self) -> Option<char> {
        let c = self.peek(0)?;
        self.at += 1;
        self.line += usize::from(c == '\n');
        Some(c)
    }

    fn name(&mut self) -> String {
        let start = self.at;
        while self.peek(0).is_some_and(is_name) {
            self.at += 1;
        }
        self.text[start..self.at].iter().collect()
    }

    /// The tokens up to the end of the text, or (in an f-string's hole) up to the `}`, `:` or `!` that closes the expression.
    fn tokens(&mut self, in_hole: bool) -> Option<Vec<Tok>> {
        let (mut out, mut depth) = (Vec::<Tok>::new(), 0usize);
        while let Some(c) = self.peek(0) {
            let line = self.line;
            if in_hole
                && depth == 0
                && (matches!(c, '}' | ':') || (c == '!' && self.peek(1) != Some('=')))
            {
                return Some(out);
            }
            let op = |kind| Tok {
                kind,
                first: line,
                last: line,
            };
            match c {
                '#' => {
                    while self.peek(0).is_some_and(|n| n != '\n') {
                        self.at += 1;
                    }
                }
                '\n' => {
                    self.bump();
                    if depth == 0 && out.last().is_some_and(|t| t.kind != Kind::Newline) {
                        out.push(op(Kind::Newline));
                    }
                }
                ' ' | '\t' | '\r' | '\x0c' => self.at += 1,
                '\\' if self.peek(1) == Some('\n') => {
                    self.at += 1;
                    self.bump();
                }
                '"' | '\'' => out.push(self.string("", line)?),
                n if is_name(n) => {
                    let word = self.name();
                    let quoted = matches!(self.peek(0), Some('"' | '\''));
                    if quoted && PREFIXES.contains(&word.to_lowercase().as_str()) {
                        out.push(self.string(&word, line)?);
                    } else {
                        out.push(op(Kind::Name(word)));
                    }
                }
                _ => {
                    self.at += 1;
                    if matches!(c, '(' | '[' | '{') {
                        depth += 1;
                    } else if matches!(c, ')' | ']' | '}') {
                        depth = depth.checked_sub(1)?;
                    }
                    out.push(op(Kind::Op(c)));
                }
            }
        }
        if in_hole || depth > 0 {
            return None;
        }
        if out.last().is_some_and(|t| t.kind != Kind::Newline) {
            let line = self.line;
            out.push(Tok {
                kind: Kind::Newline,
                first: line,
                last: line,
            });
        }
        Some(out)
    }

    fn escape(&mut self, raw: bool, into: &mut String) -> Option<()> {
        self.at += 1;
        let c = self.bump()?;
        if raw {
            into.extend(['\\', c]);
            return Some(());
        }
        match c {
            '\n' => {}
            'n' => into.push('\n'),
            't' => into.push('\t'),
            'r' => into.push('\r'),
            '\\' | '\'' | '"' => into.push(c),
            other => into.extend(['\\', other]),
        }
        Some(())
    }

    fn string(&mut self, prefix: &str, first: usize) -> Option<Tok> {
        let p = prefix.to_lowercase();
        let (raw, bytes, formatted) = (
            p.contains('r'),
            p.contains('b'),
            p.contains('f') || p.contains('t'),
        );
        let quote = self.bump()?;
        let triple = self.peek(0) == Some(quote) && self.peek(1) == Some(quote);
        self.at += if triple { 2 } else { 0 };
        let (mut pieces, mut current) = (Vec::new(), String::new());
        loop {
            let c = self.peek(0)?;
            if c == quote
                && (!triple || (self.peek(1) == Some(quote) && self.peek(2) == Some(quote)))
            {
                self.at += if triple { 3 } else { 1 };
                break;
            }
            if c == '\n' && !triple {
                return None;
            }
            if c == '\\' {
                self.escape(raw, &mut current)?;
                continue;
            }
            if formatted && c == '{' && self.peek(1) != Some('{') {
                self.hole()?;
                pieces.push(take(&mut current));
                continue;
            }
            if formatted && matches!(c, '{' | '}') {
                if self.peek(1) != Some(c) {
                    return None;
                }
                self.at += 1;
            }
            current.push(self.bump()?);
        }
        pieces.push(current);
        let last = self.line;
        Some(Tok {
            kind: Kind::Str {
                pieces,
                bytes,
                plain: !formatted,
            },
            first,
            last,
        })
    }

    /// An f-string's `{...}`: the strings of its expression, then its conversion and its format spec.
    fn hole(&mut self) -> Option<()> {
        self.at += 1;
        let toks = self.tokens(true)?;
        self.runs(&toks);
        if self.peek(0) == Some('!') {
            self.at += 1;
            self.name();
        }
        if self.peek(0) == Some(':') {
            self.at += 1;
            let mut spec = String::new();
            loop {
                match self.peek(0)? {
                    '}' => break,
                    '{' => self.hole()?,
                    _ => spec.push(self.bump()?),
                }
            }
            self.strings.push(spec);
        }
        (self.bump()? == '}').then_some(())
    }

    /// Each run of adjacent string tokens as its constants.
    fn runs(&mut self, toks: &[Tok]) {
        let (mut current, mut open) = (String::new(), false);
        for t in toks {
            if let Kind::Str { pieces, .. } = &t.kind {
                open = true;
                for (n, piece) in pieces.iter().enumerate() {
                    if n > 0 {
                        self.strings.push(take(&mut current));
                    }
                    current.push_str(piece);
                }
            } else if open {
                self.strings.push(take(&mut current));
                open = false;
            }
        }
        if open {
            self.strings.push(current);
        }
    }
}

fn name_of(t: Option<&Tok>) -> &str {
    match t.map(|t| &t.kind) {
        Some(Kind::Name(n)) => n,
        _ => "",
    }
}

/// The token after a `def` or `class` header's colon, for a line that is one.
fn body_of(line: &[Tok]) -> Option<usize> {
    let first = name_of(line.first());
    if !(matches!(first, "def" | "class") || (first == "async" && name_of(line.get(1)) == "def")) {
        return None;
    }
    let mut depth = 0;
    for (i, t) in line.iter().enumerate() {
        match t.kind {
            Kind::Op('(' | '[' | '{') => depth += 1,
            Kind::Op(')' | ']' | '}') => depth -= 1,
            Kind::Op(':') if depth == 0 => return Some(i + 1),
            _ => {}
        }
    }
    None
}

fn docstring(stmt: &[Tok], lines: &mut BTreeSet<usize>) {
    let n = stmt
        .iter()
        .take_while(|t| matches!(t.kind, Kind::Str { .. }))
        .count();
    let plain = stmt[..n].iter().all(|t| {
        matches!(
            t.kind,
            Kind::Str {
                plain: true,
                bytes: false,
                ..
            }
        )
    });
    let ends = stmt.get(n).is_none_or(|t| matches!(t.kind, Kind::Op(';')));
    if n > 0 && plain && ends {
        lines.extend(stmt[0].first..=stmt[n - 1].last);
    }
}

fn statement(rest: &[Tok]) -> &[Tok] {
    let end = rest
        .iter()
        .position(|t| t.kind == Kind::Op(';'))
        .unwrap_or(rest.len());
    &rest[..end]
}

fn plain_import(rest: &[Tok], out: &mut Vec<String>) {
    for item in statement(rest).split(|t| t.kind == Kind::Op(',')) {
        let dotted = item.iter().take_while(|t| name_of(Some(t)) != "as");
        out.extend(
            dotted
                .filter_map(|t| Some(name_of(Some(t))).filter(|n| !n.is_empty()))
                .last()
                .map(str::to_owned),
        );
    }
}

fn from_import(rest: &[Tok], out: &mut Vec<String>) {
    let stmt = statement(rest);
    let Some(at) = stmt.iter().position(|t| name_of(Some(t)) == "import") else {
        return;
    };
    let Some(module) = stmt[..at]
        .iter()
        .rev()
        .map(|t| name_of(Some(t)))
        .find(|n| !n.is_empty())
    else {
        return;
    };
    out.push(module.to_owned());
    for item in stmt[at + 1..].split(|t| t.kind == Kind::Op(',')) {
        out.extend(
            item.iter()
                .map(|t| name_of(Some(t)))
                .find(|n| !n.is_empty())
                .map(str::to_owned),
        );
    }
}

/// One top-level class that assigns a string `key`, as `ast` reads it (`modal_owed.kinds_in`).
#[derive(Debug, Default, PartialEq, Eq)]
pub struct KindClass {
    /// The class's name.
    pub name: String,
    /// The value of its first constant `key = ...` assignment.
    pub key: String,
    /// The line its `class` keyword stands on.
    pub line: usize,
    /// Its docstring, as `ast.get_docstring` cleans it; "" for none.
    pub doc: String,
}

fn is_plain_eq(stmt: &[Tok], i: usize) -> bool {
    stmt[i].kind == Kind::Op('=')
        && stmt.get(i + 1).is_none_or(|t| t.kind != Kind::Op('='))
        && (i == 0
            || !matches!(
                stmt[i - 1].kind,
                Kind::Op(
                    '=' | '!'
                        | '<'
                        | '>'
                        | ':'
                        | '+'
                        | '-'
                        | '*'
                        | '/'
                        | '%'
                        | '&'
                        | '|'
                        | '^'
                        | '@'
                        | '~'
                )
            ))
}

/// The parts of an assignment split at its depth-zero `=` signs.
fn assignment_parts(stmt: &[Tok]) -> Vec<&[Tok]> {
    let (mut parts, mut depth, mut start) = (Vec::new(), 0, 0);
    for (i, t) in stmt.iter().enumerate() {
        match t.kind {
            Kind::Op('(' | '[' | '{') => depth += 1,
            Kind::Op(')' | ']' | '}') => depth -= 1,
            _ if depth == 0 && is_plain_eq(stmt, i) => {
                parts.push(&stmt[start..i]);
                start = i + 1;
            }
            _ => {}
        }
    }
    parts.push(&stmt[start..]);
    parts
}

/// `toks` without the parentheses that wrap the whole of it (`('p' 'q')`, `(key)`): grouping, not a tuple, to `ast`.
fn unwrapped(mut toks: &[Tok]) -> &[Tok] {
    while toks.len() >= 2
        && toks[0].kind == Kind::Op('(')
        && toks[toks.len() - 1].kind == Kind::Op(')')
    {
        let mut depth = 0usize;
        let closes_last = toks.iter().enumerate().all(|(i, t)| {
            match t.kind {
                Kind::Op('(' | '[' | '{') => depth += 1,
                Kind::Op(')' | ']' | '}') => depth -= 1,
                _ => {}
            }
            depth > 0 || i == toks.len() - 1
        });
        let inner = &toks[1..toks.len() - 1];
        if !closes_last || inner.iter().any(|t| t.kind == Kind::Op(',')) {
            break;
        }
        toks = inner;
    }
    toks
}

/// A statement's constant value as `ast.Constant` holds it: a string's text, any other constant, or None for anything else.
/// An `ast.Constant`: a string's text, or any other constant (a number, `None`, bytes).
#[derive(Debug, PartialEq, Eq)]
enum Constant {
    Text(String),
    Other,
}

/// A string token's pieces and flags, or None for any other token.
fn str_of(t: &Tok) -> Option<(&[String], bool, bool)> {
    match &t.kind {
        Kind::Str {
            pieces,
            bytes,
            plain,
        } => Some((pieces.as_slice(), *bytes, *plain)),
        _ => None,
    }
}

fn constant_of(value: &[Tok]) -> Option<Constant> {
    let value = unwrapped(value);
    let strings: Option<Vec<(&[String], bool, bool)>> = value.iter().map(str_of).collect();
    if let Some(parts) = strings.filter(|p| !p.is_empty()) {
        if parts.iter().any(|(_, _, plain)| !plain) {
            return None;
        }
        if parts.iter().any(|(_, bytes, _)| *bytes) {
            return Some(Constant::Other);
        }
        return Some(Constant::Text(
            parts
                .iter()
                .flat_map(|(pieces, ..)| pieces.iter().map(String::as_str))
                .collect(),
        ));
    }
    let number = !value.is_empty()
        && value.iter().all(|t| match &t.kind {
            Kind::Name(n) => {
                matches!(n.as_str(), "True" | "False" | "None")
                    || n.starts_with(|c: char| c.is_ascii_digit())
            }
            Kind::Op('.') => true,
            _ => false,
        });
    number.then_some(Constant::Other)
}

/// What a body statement sets `key` to, where it is an `ast.Assign` of a constant to the bare name `key`.
fn key_of(stmt: &[Tok]) -> Option<Constant> {
    let parts = assignment_parts(stmt);
    let (value, targets) = parts.split_last()?;
    if targets.is_empty()
        || !targets
            .iter()
            .any(|t| t.len() == 1 && name_of(t.first()) == "key")
    {
        return None;
    }
    constant_of(value)
}

/// `inspect.cleandoc`, as `CPython` 3.14 cleans a docstring.
fn cleandoc(doc: &str) -> String {
    let mut lines: Vec<Vec<char>> = doc
        .split('\n')
        .map(|l| expand_tabs(l).chars().collect())
        .collect();
    let margin = lines[1..]
        .iter()
        .filter_map(|l| {
            let content = l.iter().skip_while(|c| **c == ' ').count();
            (content > 0).then(|| l.len() - content)
        })
        .min();
    let skip = lines[0].iter().take_while(|c| **c == ' ').count();
    lines[0].drain(..skip);
    if let Some(m) = margin {
        for line in &mut lines[1..] {
            line.drain(..m.min(line.len()));
        }
    }
    let text: Vec<String> = lines.iter().map(|l| l.iter().collect()).collect();
    let (first, last) = (
        text.iter().position(|l| !l.is_empty()),
        text.iter().rposition(|l| !l.is_empty()),
    );
    first
        .zip(last)
        .map_or_else(String::new, |(a, b)| text[a..=b].join("\n"))
}

fn expand_tabs(line: &str) -> String {
    let mut out = String::new();
    let mut col = 0;
    for c in line.chars() {
        if c == '\t' {
            let n = 8 - col % 8;
            out.extend(std::iter::repeat_n(' ', n));
            col += n;
        } else {
            out.push(c);
            col = if matches!(c, '\r') { 0 } else { col + 1 };
        }
    }
    out
}

fn statements(line: &[Tok]) -> Vec<&[Tok]> {
    line.split(|t| t.kind == Kind::Op(';'))
        .filter(|s| !s.is_empty())
        .collect()
}

/// A class's body statements: what follows its colon on its own line, else the logical lines one indent in.
fn body_statements<'a>(
    lines: &[&'a [Tok]],
    at: usize,
    body: usize,
    indent_of: &dyn Fn(&[Tok]) -> usize,
) -> Vec<&'a [Tok]> {
    if body < lines[at].len() {
        return statements(&lines[at][body..]);
    }
    let Some(depth) = lines.get(at + 1).map(|l| indent_of(l)) else {
        return Vec::new();
    };
    if depth == 0 {
        return Vec::new();
    }
    lines[at + 1..]
        .iter()
        .take_while(|l| indent_of(l) > 0)
        .filter(|l| indent_of(l) == depth)
        .flat_map(|l| statements(l))
        .collect()
}

/// The classes of `src` that set a string `key` (`modal_owed.kinds_in`), or None where it is no Python a lexer can follow. The same lexer as [`read`], so a class's text is read the way a file's facts are.
#[must_use]
pub fn kinds(src: &str) -> Option<Vec<KindClass>> {
    let mut lexer = Lexer {
        text: src.chars().collect(),
        at: 0,
        line: 1,
        strings: Vec::new(),
    };
    let toks = lexer.tokens(false)?;
    let source_lines: Vec<&str> = src.split('\n').collect();
    let indent_of = |line: &[Tok]| -> usize {
        source_lines[line[0].first - 1]
            .chars()
            .take_while(|c| *c == ' ' || *c == '\t')
            .count()
    };
    let lines: Vec<&[Tok]> = toks
        .split(|t| t.kind == Kind::Newline)
        .filter(|l| !l.is_empty())
        .collect();
    let mut out = Vec::new();
    for (at, line) in lines.iter().enumerate() {
        if indent_of(line) != 0 || name_of(line.first()) != "class" {
            continue;
        }
        let stmts = body_statements(&lines, at, body_of(line)?, &indent_of);
        let Some(Constant::Text(key)) = stmts.iter().find_map(|s| key_of(s)) else {
            continue;
        };
        let doc = stmts
            .first()
            .and_then(|s| match constant_of(s) {
                Some(Constant::Text(d)) => Some(d),
                _ => None,
            })
            .map_or_else(String::new, |d| cleandoc(&d));
        out.push(KindClass {
            name: name_of(line.get(1)).to_owned(),
            key,
            line: line[0].first,
            doc,
        });
    }
    Some(out)
}

/// The facts of `src`, or None where it is no Python a lexer can follow.
#[must_use]
pub fn read(src: &str) -> Option<Facts> {
    let mut lexer = Lexer {
        text: src.chars().collect(),
        at: 0,
        line: 1,
        strings: Vec::new(),
    };
    let toks = lexer.tokens(false)?;
    lexer.runs(&toks);
    let mut facts = Facts {
        strings: lexer.strings,
        ..Facts::default()
    };
    let mut want_doc = true;
    for line in toks
        .split(|t| t.kind == Kind::Newline)
        .filter(|l| !l.is_empty())
    {
        if take(&mut want_doc) {
            docstring(line, &mut facts.docstring_lines);
        }
        if let Some(body) = body_of(line) {
            if body < line.len() {
                docstring(&line[body..], &mut facts.docstring_lines);
            } else {
                want_doc = true;
            }
        }
        for (i, t) in line.iter().enumerate() {
            if i > 0 && !matches!(line[i - 1].kind, Kind::Op(';' | ':')) {
                continue;
            }
            match name_of(Some(t)) {
                "import" => plain_import(&line[i + 1..], &mut facts.imported),
                "from" => from_import(&line[i + 1..], &mut facts.imported),
                _ => {}
            }
        }
    }
    Some(facts)
}

#[cfg(test)]
mod tests;
