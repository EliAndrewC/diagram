//! A Python module read as `ast.parse` reads it, as far as the work-budget audit asks of it (feature 449 T134, the port of
//! `work_budget_bundle.py`, which asked `CPython`'s `ast`): every function and class it defines, its module- and class-level names,
//! its imports and its calls, in the order `ast.walk` visits them.
//!
//! WHY A PARSER AND NOT THE GUARD'S `pylex`: `ast.walk` is breadth-first, so which module a call brings first - the order of the
//! audit bundle's `code/` list - follows each call's depth in the tree, and the depth needs every expression parsed; `pylex` is a
//! lexer for three facts that need neither indentation nor numbers (feature 449 T050), and it decides none of these. The tree
//! here keeps `CPython`'s shape and field order for every node that can hold a call, an import or a definition; a leaf (a constant,
//! an operator, a context, an alias, a match pattern) holds none, so leaving it out moves nothing `ast.walk` yields.

use std::collections::VecDeque;
use std::sync::LazyLock;

use fancy_regex::Regex;

mod expr;
mod lex;
mod stmt;

use lex::Tok;

/// What a call calls, as the audit reads it: a name, a name's attribute, or anything else.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Callee {
    Name(String),
    Attr(String, String),
    Other,
}

/// An imported name and what it is bound as (`as`).
pub type Alias = (String, Option<String>);

/// A node's kind, as far as the audit reads it.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum What {
    Other,
    Name(String),
    /// An attribute: the name it is read from (when it is read from a name), and the attribute.
    Attr(Option<String>, String),
    Tuple,
    List,
    Starred,
    Subscript,
    Call(Callee),
    Def(String),
    /// A class: its name and the names its body assigns at its own level.
    Class(String, Vec<String>),
    Import(Vec<Alias>),
    /// `from <module> import ...`: the module (`""` for none), its level of dots, the names.
    From(String, usize, Vec<Alias>),
    /// An assignment's (or an annotated one's) targets that are plain names.
    Assign(Vec<String>),
}

/// A node of the tree: its kind and its children, in `CPython`'s field order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Node {
    pub what: What,
    pub kids: Vec<Node>,
}

/// A node.
fn node(what: What, kids: Vec<Node>) -> Node {
    Node { what, kids }
}

/// A node with no kind the audit reads.
fn other(kids: Vec<Node>) -> Node {
    node(What::Other, kids)
}

/// A module: its statements.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Module {
    pub body: Vec<Node>,
}

/// Python's number literals, the tokenizer's check (`1_000`, `0x_ff`, `1e-3`, `2j`; never `007` or `1__0`).
static NUMBER: LazyLock<Regex> = LazyLock::new(|| {
    let digits = "[0-9](?:_?[0-9])*";
    let exponent = format!("[eE][-+]?{digits}");
    let point = format!("(?:{digits})?\\.{digits}|{digits}\\.");
    let float = format!("(?:{point})(?:{exponent})?|{digits}{exponent}");
    Regex::new(&format!(
        "^(?:0[xX](?:_?[0-9a-fA-F])+|0[oO](?:_?[0-7])+|0[bB](?:_?[01])+|[1-9](?:_?[0-9])*|0+(?:_?0)*|(?:{float})|(?:{float}|{digits})[jJ])$"
    ))
    .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Python's hard keywords: none is a name.
const KEYWORDS: [&str; 35] = [
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import",
    "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while",
    "with", "yield",
];

type R<T> = Result<T, String>;

/// Whether `lit` is a number literal Python's tokenizer reads.
#[must_use]
pub fn is_number(lit: &str) -> bool {
    NUMBER.is_match(lit).unwrap_or(false)
}

/// The tokens and the parser's place in them.
struct Parser {
    toks: Vec<Tok>,
    at: usize,
}

impl Parser {
    fn peek(&self, n: usize) -> &Tok {
        self.toks.get(self.at + n).unwrap_or(&Tok::End)
    }

    fn is_op(&self, op: &str) -> bool {
        matches!(self.peek(0), Tok::Op(o) if *o == op)
    }

    fn is_word(&self, word: &str) -> bool {
        matches!(self.peek(0), Tok::Name(w) if w == word)
    }

    fn eat_op(&mut self, op: &str) -> bool {
        let hit = self.is_op(op);
        self.at += usize::from(hit);
        hit
    }

    fn eat_word(&mut self, word: &str) -> bool {
        let hit = self.is_word(word);
        self.at += usize::from(hit);
        hit
    }

    fn expect_op(&mut self, op: &str) -> R<()> {
        if self.eat_op(op) {
            Ok(())
        } else {
            self.fail()
        }
    }

    fn expect_word(&mut self, word: &str) -> R<()> {
        if self.eat_word(word) {
            Ok(())
        } else {
            self.fail()
        }
    }

    /// A name that is no keyword.
    fn ident(&mut self) -> R<String> {
        match self.peek(0) {
            Tok::Name(w) if !KEYWORDS.contains(&w.as_str()) => {
                let w = w.clone();
                self.at += 1;
                Ok(w)
            }
            _ => self.fail(),
        }
    }

    fn fail<T>(&self) -> R<T> {
        Err(format!(
            "SyntaxError: invalid syntax at token {} ({:?})",
            self.at,
            self.peek(0)
        ))
    }
}

/// The module `src` holds.
///
/// # Errors
///
/// Where `ast.parse` would raise its `SyntaxError`: why.
pub fn parse(src: &str) -> R<Module> {
    let mut p = Parser {
        toks: lex::tokens(src)?,
        at: 0,
    };
    let body = p.file()?;
    Ok(Module { body })
}

/// Every node of the module in `ast.walk`'s order (breadth first, each node's children in field order), the module itself left out.
#[must_use]
pub fn walk(m: &Module) -> Vec<&Node> {
    let (mut out, mut todo): (Vec<&Node>, VecDeque<&Node>) = (Vec::new(), m.body.iter().collect());
    while let Some(n) = todo.pop_front() {
        todo.extend(n.kids.iter());
        out.push(n);
    }
    out
}

/// The names a body's assignments bind at its own level (`x = ...`, `x: T`), as `targets` a module- or class-level scan reads.
fn own_names(body: &[Node]) -> Vec<String> {
    body.iter()
        .filter_map(|n| match &n.what {
            What::Assign(names) => Some(names.clone()),
            _ => None,
        })
        .flatten()
        .collect()
}

/// The names the module binds at its own level and at each class's (every class, nested ones too).
#[must_use]
pub fn scope_names(m: &Module) -> Vec<String> {
    let mut out = own_names(&m.body);
    for n in walk(m) {
        if let What::Class(_, own) = &n.what {
            out.extend(own.iter().cloned());
        }
    }
    out
}

#[cfg(test)]
mod tests;
