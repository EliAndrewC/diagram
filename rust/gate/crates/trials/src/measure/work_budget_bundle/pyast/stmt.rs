//! Python's statements, as the grammar of `ast.parse` reads them (feature 449 T134): each in `CPython`'s shape and field order (a
//! function's arguments, body, decorators, returns and type parameters; a class's bases, keywords, body, decorators and type
//! parameters; an `elif` as an `If` in its parent's `orelse`).

use super::expr::check_target;
use super::lex::Tok;
use super::{node, other, own_names, Node, Parser, What, R};

const AUGMENTED: [&str; 13] = [
    "+=", "-=", "*=", "/=", "//=", "%=", "@=", "&=", "|=", "^=", ">>=", "<<=", "**=",
];

impl Parser {
    /// Every statement to the end of the tokens.
    pub(super) fn file(&mut self) -> R<Vec<Node>> {
        let mut body = Vec::new();
        while self.peek(0) != &Tok::End {
            body.extend(self.statement()?);
        }
        Ok(body)
    }

    fn statement(&mut self) -> R<Vec<Node>> {
        if let Some(n) = self.compound()? {
            return Ok(vec![n]);
        }
        self.simple_stmts()
    }

    /// A `:` and the block after it: its statements on the same line, or an indented run of them.
    fn block(&mut self) -> R<Vec<Node>> {
        self.expect_op(":")?;
        if self.peek(0) != &Tok::Newline {
            return self.simple_stmts();
        }
        self.at += 1;
        if self.peek(0) != &Tok::Indent {
            return self.fail();
        }
        self.at += 1;
        let mut body = Vec::new();
        while self.peek(0) != &Tok::Dedent {
            body.extend(self.statement()?);
        }
        self.at += 1;
        Ok(body)
    }

    /// `else:` and its block, or nothing.
    fn orelse(&mut self) -> R<Vec<Node>> {
        if self.eat_word("else") {
            return self.block();
        }
        Ok(vec![])
    }

    fn compound(&mut self) -> R<Option<Node>> {
        let word = match self.peek(0) {
            Tok::Op("@") => "@".to_owned(),
            Tok::Name(w) => w.clone(),
            _ => return Ok(None),
        };
        let next_is =
            |p: &Self, ws: &[&str]| matches!(p.peek(1), Tok::Name(w) if ws.contains(&w.as_str()));
        Ok(Some(match word.as_str() {
            "@" => {
                let mut decorators = Vec::new();
                while self.eat_op("@") {
                    decorators.push(self.named_expression()?);
                    if self.peek(0) != &Tok::Newline {
                        return self.fail();
                    }
                    self.at += 1;
                }
                self.eat_word("async");
                if self.is_word("class") {
                    self.classdef(decorators)?
                } else {
                    self.funcdef(decorators)?
                }
            }
            "async" if next_is(self, &["def", "for", "with"]) => {
                self.at += 1;
                return self.compound();
            }
            "def" => self.funcdef(vec![])?,
            "class" => self.classdef(vec![])?,
            "if" => self.if_stmt()?,
            "while" => {
                self.at += 1;
                let mut kids = vec![self.named_expression()?];
                kids.extend(self.block()?);
                kids.extend(self.orelse()?);
                other(kids)
            }
            "for" => {
                self.at += 1;
                let mut kids = vec![self.star_targets()?];
                self.expect_word("in")?;
                kids.push(self.star_expressions()?);
                kids.extend(self.block()?);
                kids.extend(self.orelse()?);
                other(kids)
            }
            "try" => self.try_stmt()?,
            "with" => self.with_stmt()?,
            "match" => {
                let save = self.at;
                let Ok(n) = self.match_stmt() else {
                    self.at = save;
                    return Ok(None);
                };
                n
            }
            _ => return Ok(None),
        }))
    }

    /// `[T: bound = default, *Ts, **P]`: each a type parameter holding its bound and its default.
    fn type_params(&mut self) -> R<Vec<Node>> {
        let mut out = Vec::new();
        if !self.eat_op("[") {
            return Ok(out);
        }
        while !self.is_op("]") {
            let mut kids = Vec::new();
            if self.eat_op("*") {
                self.ident()?;
                if self.eat_op("=") {
                    kids.push(self.star_expression()?);
                }
            } else {
                let spec = self.eat_op("**");
                self.ident()?;
                if !spec && self.eat_op(":") {
                    kids.push(self.expression()?);
                }
                if self.eat_op("=") {
                    kids.push(self.expression()?);
                }
            }
            out.push(other(kids));
            if !self.eat_op(",") {
                break;
            }
        }
        self.expect_op("]")?;
        Ok(out)
    }

    /// `def name[T](params) -> returns: body`: a `FunctionDef`.
    fn funcdef(&mut self, decorators: Vec<Node>) -> R<Node> {
        self.expect_word("def")?;
        let name = self.ident()?;
        let params = self.type_params()?;
        self.expect_op("(")?;
        let mut kids = vec![self.params(false)?];
        self.expect_op(")")?;
        let returns = if self.eat_op("->") {
            Some(self.expression()?)
        } else {
            None
        };
        kids.extend(self.block()?);
        kids.extend(decorators);
        kids.extend(returns);
        kids.extend(params);
        Ok(node(What::Def(name), kids))
    }

    /// `class name[T](bases, keywords): body`: a `ClassDef`, with the names its body binds at its own level.
    fn classdef(&mut self, decorators: Vec<Node>) -> R<Node> {
        self.expect_word("class")?;
        let name = self.ident()?;
        let params = self.type_params()?;
        let mut kids = if self.eat_op("(") {
            self.call_args()?
        } else {
            vec![]
        };
        let body = self.block()?;
        let own = own_names(&body);
        kids.extend(body);
        kids.extend(decorators);
        kids.extend(params);
        Ok(node(What::Class(name, own), kids))
    }

    /// `if test: body` with its `elif`s (each an `If` in the `orelse` before it) and its `else`.
    fn if_stmt(&mut self) -> R<Node> {
        self.at += 1;
        let mut kids = vec![self.named_expression()?];
        kids.extend(self.block()?);
        if self.is_word("elif") {
            kids.push(self.if_stmt()?);
        } else {
            kids.extend(self.orelse()?);
        }
        Ok(other(kids))
    }

    /// `try`: its body, its handlers (each its type, then its body), its `else`, its `finally`.
    fn try_stmt(&mut self) -> R<Node> {
        self.at += 1;
        let mut kids = self.block()?;
        let mut starred: Option<bool> = None;
        while self.eat_word("except") {
            // `except` and `except*` never mix in one `try`, and `except*` names its types
            let star = self.eat_op("*");
            if starred.is_some_and(|s| s != star) || (star && self.is_op(":")) {
                return self.fail();
            }
            starred = Some(star);
            let mut handler = Vec::new();
            if !self.is_op(":") {
                let first = self.expression()?;
                handler.push(if self.is_op(",") {
                    let mut elts = vec![first];
                    while self.eat_op(",") {
                        elts.push(self.expression()?);
                    }
                    node(What::Tuple, elts)
                } else {
                    first
                });
                if self.eat_word("as") {
                    self.ident()?;
                }
            }
            handler.extend(self.block()?);
            kids.push(other(handler));
        }
        kids.extend(self.orelse()?);
        if self.eat_word("finally") {
            kids.extend(self.block()?);
        } else if starred.is_none() {
            return self.fail();
        }
        Ok(other(kids))
    }

    /// One `with` item: its context expression and its target.
    fn with_item(&mut self) -> R<Node> {
        let mut kids = vec![self.expression()?];
        if self.eat_word("as") {
            let target = self.star_targets_one()?;
            kids.push(target);
        }
        Ok(other(kids))
    }

    /// A single target (`as` binds one, a tuple only in brackets).
    fn star_targets_one(&mut self) -> R<Node> {
        let target = if self.eat_op("*") {
            node(What::Starred, vec![self.bitwise_or()?])
        } else {
            self.bitwise_or()?
        };
        check_target(&target)?;
        Ok(target)
    }

    /// `with` items (bracketed or not) and its body.
    fn with_stmt(&mut self) -> R<Node> {
        self.at += 1;
        let mut kids = Vec::new();
        if self.is_op("(") {
            let save = self.at;
            self.at += 1;
            let mut items = Vec::new();
            let bracketed = loop {
                match self.with_item() {
                    Ok(item) => items.push(item),
                    Err(_) => break false,
                }
                if !self.eat_op(",") || self.is_op(")") {
                    break self.eat_op(")") && self.is_op(":");
                }
            };
            if bracketed {
                kids = items;
            } else {
                self.at = save;
            }
        }
        if kids.is_empty() {
            kids.push(self.with_item()?);
            while self.eat_op(",") {
                kids.push(self.with_item()?);
            }
        }
        kids.extend(self.block()?);
        Ok(other(kids))
    }

    /// `match subject:` and its cases (each its pattern, its guard, its body); a pattern holds no call, so it is skipped whole.
    fn match_stmt(&mut self) -> R<Node> {
        self.at += 1;
        let mut kids = vec![self.star_named_list()?];
        self.expect_op(":")?;
        if self.peek(0) != &Tok::Newline || self.peek(1) != &Tok::Indent {
            return self.fail();
        }
        self.at += 2;
        while self.eat_word("case") {
            let (mut depth, start) = (0usize, self.at);
            loop {
                match self.peek(0) {
                    Tok::Op(":") if depth == 0 => break,
                    Tok::Name(w) if depth == 0 && w == "if" => break,
                    Tok::Op("(" | "[" | "{") => depth += 1,
                    Tok::Op(")" | "]" | "}") => depth = depth.saturating_sub(1),
                    Tok::Newline | Tok::End => return self.fail(),
                    _ => {}
                }
                self.at += 1;
            }
            if self.at == start {
                return self.fail();
            }
            let mut case = vec![other(vec![])];
            if self.eat_word("if") {
                case.push(self.named_expression()?);
            }
            case.extend(self.block()?);
            kids.push(other(case));
        }
        if kids.len() == 1 || self.peek(0) != &Tok::Dedent {
            return self.fail();
        }
        self.at += 1;
        Ok(other(kids))
    }

    /// Simple statements to the end of their line, `;` between them.
    fn simple_stmts(&mut self) -> R<Vec<Node>> {
        let mut out = vec![self.simple_stmt()?];
        while self.eat_op(";") && self.peek(0) != &Tok::Newline {
            out.push(self.simple_stmt()?);
        }
        if self.peek(0) != &Tok::Newline {
            return self.fail();
        }
        self.at += 1;
        Ok(out)
    }

    /// A dotted module name.
    fn dotted(&mut self) -> R<String> {
        let mut name = self.ident()?;
        while self.eat_op(".") {
            name.push('.');
            name.push_str(&self.ident()?);
        }
        Ok(name)
    }

    /// `name [as other]`, `dotted` reading the name.
    fn alias(&mut self, dotted: bool) -> R<(String, Option<String>)> {
        let name = if dotted {
            self.dotted()?
        } else {
            self.ident()?
        };
        let asname = if self.eat_word("as") {
            Some(self.ident()?)
        } else {
            None
        };
        Ok((name, asname))
    }

    /// `from .module import a as b, c`: the module, its level, the names.
    fn import_from(&mut self) -> R<Node> {
        self.at += 1;
        let mut level = 0;
        loop {
            if self.eat_op(".") {
                level += 1;
            } else if self.eat_op("...") {
                level += 3;
            } else {
                break;
            }
        }
        let module = if self.is_word("import") {
            String::new()
        } else {
            self.dotted()?
        };
        if level == 0 && module.is_empty() {
            return self.fail();
        }
        self.expect_word("import")?;
        let mut names = Vec::new();
        if self.eat_op("*") {
            names.push(("*".to_owned(), None));
        } else {
            let bracketed = self.eat_op("(");
            loop {
                names.push(self.alias(false)?);
                if !self.eat_op(",") || (bracketed && self.is_op(")")) {
                    break;
                }
            }
            if bracketed {
                self.expect_op(")")?;
            }
        }
        Ok(node(What::From(module, level, names), vec![]))
    }

    fn simple_stmt(&mut self) -> R<Node> {
        let word = match self.peek(0) {
            Tok::Name(w) => w.clone(),
            _ => String::new(),
        };
        match word.as_str() {
            "pass" | "break" | "continue" => {
                self.at += 1;
                Ok(other(vec![]))
            }
            "return" => {
                self.at += 1;
                Ok(other(if self.starts_expr() {
                    vec![self.star_expressions()?]
                } else {
                    vec![]
                }))
            }
            "del" => {
                self.at += 1;
                let mut targets = vec![self.star_targets_one()?];
                while self.eat_op(",") && self.starts_expr() {
                    targets.push(self.star_targets_one()?);
                }
                Ok(other(targets))
            }
            "raise" => {
                self.at += 1;
                let mut kids = Vec::new();
                if self.starts_expr() {
                    kids.push(self.expression()?);
                    if self.eat_word("from") {
                        kids.push(self.expression()?);
                    }
                }
                Ok(other(kids))
            }
            "global" | "nonlocal" => {
                self.at += 1;
                self.ident()?;
                while self.eat_op(",") {
                    self.ident()?;
                }
                Ok(other(vec![]))
            }
            "assert" => {
                self.at += 1;
                let mut kids = vec![self.expression()?];
                if self.eat_op(",") {
                    kids.push(self.expression()?);
                }
                Ok(other(kids))
            }
            "import" => {
                self.at += 1;
                let mut names = vec![self.alias(true)?];
                while self.eat_op(",") {
                    names.push(self.alias(true)?);
                }
                Ok(node(What::Import(names), vec![]))
            }
            "from" => self.import_from(),
            "type"
                if matches!(self.peek(1), Tok::Name(_))
                    && matches!(self.peek(2), Tok::Op("=" | "[")) =>
            {
                let save = self.at;
                self.at += 1;
                let alias = (|| {
                    let name = node(What::Name(self.ident()?), vec![]);
                    let mut kids = vec![name];
                    kids.extend(self.type_params()?);
                    self.expect_op("=")?;
                    kids.push(self.expression()?);
                    Ok::<Node, String>(other(kids))
                })();
                alias.or_else(|_| {
                    self.at = save;
                    self.assignment()
                })
            }
            _ => self.assignment(),
        }
    }

    /// An expression statement, an assignment (its targets, then its value), an augmented one or an annotated one.
    fn assignment(&mut self) -> R<Node> {
        let first = self.rhs()?;
        if self.eat_op(":") {
            if !matches!(first.what, What::Name(_) | What::Attr(..) | What::Subscript) {
                return self.fail();
            }
            let names = match &first.what {
                What::Name(n) => vec![n.clone()],
                _ => vec![],
            };
            let mut kids = vec![first, self.expression()?];
            if self.eat_op("=") {
                kids.push(self.rhs()?);
            }
            return Ok(node(What::Assign(names), kids));
        }
        if AUGMENTED.iter().any(|o| self.is_op(o)) {
            if !matches!(first.what, What::Name(_) | What::Attr(..) | What::Subscript) {
                return self.fail();
            }
            self.at += 1;
            return Ok(other(vec![first, self.rhs()?]));
        }
        if !self.is_op("=") {
            return Ok(other(vec![first]));
        }
        let mut kids = vec![first];
        while self.eat_op("=") {
            kids.push(self.rhs()?);
        }
        let mut names = Vec::new();
        for target in &kids[..kids.len() - 1] {
            check_target(target)?;
            if let What::Name(n) = &target.what {
                names.push(n.clone());
            }
        }
        Ok(node(What::Assign(names), kids))
    }
}
