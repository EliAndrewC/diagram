//! Python's tokenizer, as far as the parser beside it needs (feature 449 T134): names, numbers, strings with each f- or t-string's
//! replacement fields lexed as tokens of their own, operators by longest match, and the logical lines' NEWLINE, INDENT and DEDENT.
//! A text `ast.parse` refuses at the token level (an unterminated string, an unbalanced bracket, a dedent to no level, a stray
//! character) is refused here too.

/// A replacement field of an f- or t-string: its expression's tokens (ending in `End`), and the fields of its format spec.
#[derive(Debug, Clone, PartialEq)]
pub struct Hole {
    pub toks: Vec<Tok>,
    pub spec: Option<Vec<Hole>>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Tok {
    Name(String),
    Num,
    /// One string literal: whether it is an f- or t-string, and its replacement fields.
    Str(bool, Vec<Hole>),
    Op(&'static str),
    Newline,
    Indent,
    Dedent,
    End,
}

const OPS: [&str; 47] = [
    "**=", "//=", ">>=", "<<=", "...", "!=", "->", ":=", "==", "<=", ">=", "<<", ">>", "**", "//",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "@=", "+", "-", "*", "/", "%", "@", "&", "|",
    "^", "~", "<", ">", "(", ")", "[", "]", "{", "}", ",", ":", ".", ";", "=",
];

const PREFIXES: [&str; 11] = ["r", "u", "b", "br", "rb", "f", "fr", "rf", "t", "tr", "rt"];

fn is_name(c: char) -> bool {
    c.is_alphanumeric() || c == '_' || (!c.is_ascii() && c != '\u{feff}' && !c.is_whitespace())
}

struct Lexer<'a> {
    text: &'a [char],
    at: usize,
}

type R<T> = Result<T, String>;

fn err<T>(why: &str) -> R<T> {
    Err(format!("SyntaxError: {why}"))
}

impl Lexer<'_> {
    fn peek(&self, n: usize) -> Option<char> {
        self.text.get(self.at + n).copied()
    }

    fn word(&mut self) -> String {
        let start = self.at;
        while self.peek(0).is_some_and(is_name) {
            self.at += 1;
        }
        self.text[start..self.at].iter().collect()
    }

    /// A number literal, checked as Python's tokenizer checks it.
    /// Digits `ok` takes, and `_` between them.
    fn digits(&mut self, ok: fn(&char) -> bool) {
        while self.peek(0).is_some_and(|c| ok(&c) || c == '_') {
            self.at += 1;
        }
    }

    /// A number literal, read and checked as Python's tokenizer reads it: its digits for its radix, a fraction, an exponent, a `j`;
    /// a name character after it only where it opens one of the keywords Python lets touch a number (`1if x else 2`).
    fn number(&mut self) -> R<Tok> {
        let start = self.at;
        match (self.peek(0), self.peek(1).map(|c| c.to_ascii_lowercase())) {
            (Some('0'), Some('x')) => {
                self.at += 2;
                self.digits(char::is_ascii_hexdigit);
            }
            (Some('0'), Some('o')) => {
                self.at += 2;
                self.digits(|c| ('0'..='7').contains(c));
            }
            (Some('0'), Some('b')) => {
                self.at += 2;
                self.digits(|c| matches!(c, '0' | '1'));
            }
            _ => {
                self.digits(char::is_ascii_digit);
                if self.peek(0) == Some('.') {
                    self.at += 1;
                    self.digits(char::is_ascii_digit);
                }
                let signed = matches!(self.peek(1), Some('+' | '-'))
                    && self.peek(2).is_some_and(|c| c.is_ascii_digit());
                if matches!(self.peek(0), Some('e' | 'E'))
                    && (self.peek(1).is_some_and(|c| c.is_ascii_digit()) || signed)
                {
                    self.at += 1 + usize::from(signed);
                    self.digits(char::is_ascii_digit);
                }
                if matches!(self.peek(0), Some('j' | 'J')) {
                    self.at += 1;
                }
            }
        }
        let lit: String = self.text[start..self.at].iter().collect();
        let rest: String = self.text[self.at..(self.at + 4).min(self.text.len())]
            .iter()
            .collect();
        let touching = self.peek(0).is_some_and(is_name)
            && !["and", "else", "for", "if", "in", "is", "not", "or"]
                .iter()
                .any(|k| rest.starts_with(k));
        if super::NUMBER.is_match(&lit).unwrap_or(false) && !touching {
            Ok(Tok::Num)
        } else {
            err(&format!("invalid number literal {lit}"))
        }
    }

    fn string(&mut self, prefix: &str) -> R<Tok> {
        let p = prefix.to_lowercase();
        let formatted = p.contains('f') || p.contains('t');
        let quote = self.peek(0).unwrap_or('"');
        self.at += 1;
        let triple = self.peek(0) == Some(quote) && self.peek(1) == Some(quote);
        self.at += if triple { 2 } else { 0 };
        let mut holes = Vec::new();
        loop {
            let Some(c) = self.peek(0) else {
                return err("unterminated string literal");
            };
            if c == quote
                && (!triple || (self.peek(1) == Some(quote) && self.peek(2) == Some(quote)))
            {
                self.at += if triple { 3 } else { 1 };
                return Ok(Tok::Str(formatted, holes));
            }
            if c == '\n' && !triple {
                return err("unterminated string literal");
            }
            if c == '\\' {
                self.at += 2;
                continue;
            }
            if formatted && c == '{' && self.peek(1) != Some('{') {
                holes.push(self.hole()?);
                continue;
            }
            if formatted && matches!(c, '{' | '}') {
                if self.peek(1) != Some(c) {
                    return err("f-string: single '}' is not allowed");
                }
                self.at += 1;
            }
            self.at += 1;
        }
    }

    /// A replacement field from its `{` to its `}`.
    fn hole(&mut self) -> R<Hole> {
        self.at += 1;
        let mut toks = self.tokens(true)?;
        toks.push(Tok::End);
        if self.peek(0) == Some('=') {
            // `{a = }`: the debug text keeps its spaces, and the field goes on after them
            self.at += 1;
            while self.peek(0).is_some_and(|c| matches!(c, ' ' | '\t' | '\n')) {
                self.at += 1;
            }
        }
        if self.peek(0) == Some('!') {
            self.at += 1;
            if !matches!(self.word().as_str(), "r" | "s" | "a") {
                return err("f-string: invalid conversion character");
            }
        }
        let mut spec = None;
        if self.peek(0) == Some(':') {
            self.at += 1;
            let mut fields = Vec::new();
            loop {
                match self.peek(0) {
                    Some('}') => break,
                    Some('{') => fields.push(self.hole()?),
                    Some(_) => self.at += 1,
                    None => return err("f-string: expecting '}'"),
                }
            }
            spec = Some(fields);
        }
        if self.peek(0) != Some('}') {
            return err("f-string: expecting '}'");
        }
        self.at += 1;
        Ok(Hole { toks, spec })
    }

    /// The width of the indentation at `self.at`, the position moved past it, twice over as Python's tokenizer counts it: a tab to
    /// the next multiple of eight, and a tab as one column (the two disagreeing is its "inconsistent use of tabs"); a form feed
    /// back to nothing.
    fn indent(&mut self) -> (usize, usize) {
        let (mut col, mut alt) = (0, 0);
        while let Some(c) = self.peek(0) {
            match c {
                ' ' => (col, alt) = (col + 1, alt + 1),
                '\t' => (col, alt) = ((col / 8 + 1) * 8, alt + 1),
                '\x0c' => (col, alt) = (0, 0),
                _ => break,
            }
            self.at += 1;
        }
        (col, alt)
    }

    /// An operator by longest match, a bracket opened or closed against the open ones.
    fn operator(&mut self, c: char, brackets: &mut Vec<char>) -> R<Tok> {
        let rest: String = self.text[self.at..(self.at + 3).min(self.text.len())]
            .iter()
            .collect();
        let Some(op) = OPS.iter().find(|o| rest.starts_with(**o)) else {
            return err(&format!("invalid character '{c}'"));
        };
        self.at += op.chars().count();
        match *op {
            "(" | "[" | "{" => brackets.push(c),
            ")" | "]" | "}" => {
                let opener = match c {
                    ')' => '(',
                    ']' => '[',
                    _ => '{',
                };
                if brackets.pop() != Some(opener) {
                    return err(&format!("unmatched '{c}'"));
                }
            }
            _ => {}
        }
        Ok(Tok::Op(op))
    }

    /// A logical line's INDENT or DEDENTs against the open levels.
    fn levels(at: (usize, usize), levels: &mut Vec<(usize, usize)>, out: &mut Vec<Tok>) -> R<()> {
        let (col, alt) = at;
        let top = levels.last().copied().unwrap_or((0, 0));
        if col > top.0 {
            if alt <= top.1 {
                return err("inconsistent use of tabs and spaces in indentation");
            }
            levels.push(at);
            out.push(Tok::Indent);
            return Ok(());
        }
        while levels.len() > 1 && col < levels.last().map_or(0, |l| l.0) {
            levels.pop();
            out.push(Tok::Dedent);
        }
        let top = levels.last().copied().unwrap_or((0, 0));
        if col != top.0 {
            return err("unindent does not match any outer indentation level");
        }
        if alt != top.1 {
            return err("inconsistent use of tabs and spaces in indentation");
        }
        Ok(())
    }

    /// The tokens to the end of the text, or (in a replacement field) to the `}`, `!`, `:` or `=` that closes its expression.
    fn tokens(&mut self, in_hole: bool) -> R<Vec<Tok>> {
        let (mut out, mut brackets, mut levels) =
            (Vec::new(), Vec::<char>::new(), vec![(0usize, 0usize)]);
        let mut line_start = !in_hole;
        while self.at <= self.text.len() {
            if line_start && brackets.is_empty() {
                let at = self.indent();
                if matches!(self.peek(0), None | Some('\n' | '#'))
                    || (self.peek(0) == Some('\\') && self.peek(1) == Some('\n'))
                {
                    while self.peek(0).is_some_and(|c| c != '\n') {
                        self.at += 1;
                    }
                    if self.peek(0).is_none() {
                        break;
                    }
                    self.at += 1;
                    continue;
                }
                line_start = false;
                Self::levels(at, &mut levels, &mut out)?;
            }
            let Some(c) = self.peek(0) else { break };
            if in_hole && brackets.is_empty() {
                let closes = match c {
                    '}' | ':' => true,
                    '!' | '=' => self.peek(1) != Some('='),
                    _ => false,
                };
                if closes {
                    return Ok(out);
                }
            }
            match c {
                '#' => {
                    while self.peek(0).is_some_and(|n| n != '\n') {
                        self.at += 1;
                    }
                }
                '\n' => {
                    self.at += 1;
                    if brackets.is_empty() && !in_hole {
                        out.push(Tok::Newline);
                        line_start = true;
                    }
                }
                ' ' | '\t' | '\x0c' => self.at += 1,
                '\\' => {
                    if self.peek(1) != Some('\n') {
                        return err("unexpected character after line continuation character");
                    }
                    self.at += 2;
                }
                '"' | '\'' => out.push(self.string("")?),
                d if d.is_ascii_digit()
                    || (d == '.' && self.peek(1).is_some_and(|n| n.is_ascii_digit())) =>
                {
                    out.push(self.number()?);
                }
                n if is_name(n) => {
                    let word = self.word();
                    if matches!(self.peek(0), Some('"' | '\''))
                        && PREFIXES.contains(&word.to_lowercase().as_str())
                    {
                        out.push(self.string(&word)?);
                    } else {
                        out.push(Tok::Name(word));
                    }
                }
                _ => out.push(self.operator(c, &mut brackets)?),
            }
        }
        if in_hole {
            return err("f-string: expecting '}'");
        }
        if !brackets.is_empty() {
            return err("'(' was never closed");
        }
        if out
            .last()
            .is_some_and(|t| !matches!(t, Tok::Newline | Tok::Dedent))
        {
            out.push(Tok::Newline);
        }
        out.extend(levels.iter().skip(1).map(|_| Tok::Dedent));
        out.push(Tok::End);
        Ok(out)
    }
}

/// The tokens of a module's source.
///
/// # Errors
///
/// A text Python's tokenizer refuses, with why.
pub fn tokens(src: &str) -> R<Vec<Tok>> {
    let text: Vec<char> = src.chars().collect();
    Lexer { text: &text, at: 0 }.tokens(false)
}
