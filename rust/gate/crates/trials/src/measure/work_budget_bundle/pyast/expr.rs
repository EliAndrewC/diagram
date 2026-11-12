//! Python's expressions, as the grammar of `ast.parse` reads them (feature 449 T134): each node in `CPython`'s shape, its children
//! in `CPython`'s field order (an `IfExp`'s test before its body, a `Dict`'s keys before its values, a call's keywords after every
//! positional argument), so `ast.walk`'s order holds.

use super::lex::{Hole, Tok};
use super::{node, other, Callee, Node, Parser, What, KEYWORDS, R};

/// The binary operators, loosest first: each level's operands are the next level's.
const LEVELS: [&[&str]; 6] = [
    &["|"],
    &["^"],
    &["&"],
    &["<<", ">>"],
    &["+", "-"],
    &["*", "/", "//", "%", "@"],
];

const COMPARE: [&str; 6] = ["==", "!=", "<", "<=", ">", ">="];

impl Parser {
    /// Whether the next token can open an expression.
    pub(super) fn starts_expr(&self) -> bool {
        match self.peek(0) {
            Tok::Name(w) => {
                !KEYWORDS.contains(&w.as_str())
                    || matches!(
                        w.as_str(),
                        "True" | "False" | "None" | "lambda" | "not" | "await"
                    )
            }
            Tok::Num | Tok::Str(..) => true,
            Tok::Op(o) => matches!(*o, "(" | "[" | "{" | "-" | "+" | "~" | "..." | "*"),
            _ => false,
        }
    }

    /// Items joined by commas, a tuple when there is a comma: `item` reads each.
    fn listed(&mut self, item: fn(&mut Self) -> R<Node>) -> R<Node> {
        let first = item(self)?;
        if !self.is_op(",") {
            return Ok(first);
        }
        let mut elts = vec![first];
        while self.eat_op(",") && self.starts_expr() {
            elts.push(item(self)?);
        }
        Ok(node(What::Tuple, elts))
    }

    /// `star_expressions`.
    pub(super) fn star_expressions(&mut self) -> R<Node> {
        self.listed(Self::star_expression)
    }

    /// `star_named_expressions` as a `match` subject or a `for` loop's iterable reads them.
    pub(super) fn star_named_list(&mut self) -> R<Node> {
        self.listed(Self::star_named_expression)
    }

    pub(super) fn star_expression(&mut self) -> R<Node> {
        if self.eat_op("*") {
            return Ok(node(What::Starred, vec![self.bitwise_or()?]));
        }
        self.expression()
    }

    pub(super) fn star_named_expression(&mut self) -> R<Node> {
        if self.eat_op("*") {
            return Ok(node(What::Starred, vec![self.bitwise_or()?]));
        }
        self.named_expression()
    }

    /// `name := value`, or an expression.
    pub(super) fn named_expression(&mut self) -> R<Node> {
        if matches!(self.peek(1), Tok::Op(":=")) && matches!(self.peek(0), Tok::Name(_)) {
            let target = self.ident()?;
            self.at += 1;
            let value = self.expression()?;
            return Ok(other(vec![node(What::Name(target), vec![]), value]));
        }
        self.expression()
    }

    /// A lambda, a conditional expression (`IfExp`: test, body, orelse), or a disjunction.
    pub(super) fn expression(&mut self) -> R<Node> {
        if self.eat_word("lambda") {
            let args = self.params(true)?;
            self.expect_op(":")?;
            let body = self.expression()?;
            return Ok(other(vec![args, body]));
        }
        let body = self.disjunction()?;
        if !self.eat_word("if") {
            return Ok(body);
        }
        let test = self.disjunction()?;
        self.expect_word("else")?;
        let orelse = self.expression()?;
        Ok(other(vec![test, body, orelse]))
    }

    /// `a or b or c` (one `BoolOp`), and below it `and`.
    pub(super) fn disjunction(&mut self) -> R<Node> {
        self.bool_op("or")
    }

    fn bool_op(&mut self, word: &str) -> R<Node> {
        let operand = |p: &mut Self| {
            if word == "or" {
                p.bool_op("and")
            } else {
                p.inversion()
            }
        };
        let first = operand(self)?;
        if !self.is_word(word) {
            return Ok(first);
        }
        let mut values = vec![first];
        while self.eat_word(word) {
            values.push(operand(self)?);
        }
        Ok(other(values))
    }

    fn inversion(&mut self) -> R<Node> {
        if self.eat_word("not") {
            return Ok(other(vec![self.inversion()?]));
        }
        self.comparison()
    }

    fn compare_op(&mut self) -> bool {
        let word = |p: &Self, n: usize, w: &str| matches!(p.peek(n), Tok::Name(x) if x == w);
        let width = match self.peek(0) {
            Tok::Op(o) if COMPARE.contains(o) => 1,
            _ if word(self, 0, "in") => 1,
            _ if word(self, 0, "not") && word(self, 1, "in") => 2,
            _ if word(self, 0, "is") => 1 + usize::from(word(self, 1, "not")),
            _ => 0,
        };
        self.at += width;
        width > 0
    }

    /// `a < b < c`: one `Compare`, its left then its comparators.
    fn comparison(&mut self) -> R<Node> {
        let first = self.bitwise_or()?;
        let mut kids = vec![first];
        while self.compare_op() {
            kids.push(self.bitwise_or()?);
        }
        Ok(if kids.len() == 1 {
            kids.remove(0)
        } else {
            other(kids)
        })
    }

    pub(super) fn bitwise_or(&mut self) -> R<Node> {
        self.binary(0)
    }

    /// A left-associative level of binary operators: `a + b + c` is `(a + b) + c`.
    fn binary(&mut self, level: usize) -> R<Node> {
        let operand = |p: &mut Self| {
            if level + 1 < LEVELS.len() {
                p.binary(level + 1)
            } else {
                p.factor()
            }
        };
        let mut left = operand(self)?;
        while LEVELS[level].iter().any(|o| self.is_op(o)) {
            self.at += 1;
            left = other(vec![left, operand(self)?]);
        }
        Ok(left)
    }

    fn factor(&mut self) -> R<Node> {
        if self.eat_op("-") || self.eat_op("+") || self.eat_op("~") {
            return Ok(other(vec![self.factor()?]));
        }
        let base = if self.eat_word("await") {
            other(vec![self.primary()?])
        } else {
            self.primary()?
        };
        if self.eat_op("**") {
            return Ok(other(vec![base, self.factor()?]));
        }
        Ok(base)
    }

    /// An atom and its trailers: `.name`, a call, a subscript.
    fn primary(&mut self) -> R<Node> {
        let mut cur = self.atom()?;
        loop {
            if self.eat_op(".") {
                let attr = self.ident()?;
                let base = match &cur.what {
                    What::Name(id) => Some(id.clone()),
                    _ => None,
                };
                cur = node(What::Attr(base, attr), vec![cur]);
            } else if self.eat_op("(") {
                let callee = match &cur.what {
                    What::Name(id) => Callee::Name(id.clone()),
                    What::Attr(Some(b), a) => Callee::Attr(b.clone(), a.clone()),
                    _ => Callee::Other,
                };
                let mut kids = vec![cur];
                kids.extend(self.call_args()?);
                cur = node(What::Call(callee), kids);
            } else if self.eat_op("[") {
                let slice = self.slices()?;
                cur = node(What::Subscript, vec![cur, slice]);
            } else {
                return Ok(cur);
            }
        }
    }

    fn atom(&mut self) -> R<Node> {
        match self.peek(0).clone() {
            Tok::Name(w) if matches!(w.as_str(), "True" | "False" | "None") => {
                self.at += 1;
                Ok(other(vec![]))
            }
            Tok::Name(_) => Ok(node(What::Name(self.ident()?), vec![])),
            Tok::Num | Tok::Op("...") => {
                self.at += 1;
                Ok(other(vec![]))
            }
            Tok::Str(..) => self.strings(),
            Tok::Op("(") => self.paren(),
            Tok::Op("[") => self.bracket(),
            Tok::Op("{") => self.brace(),
            _ => self.fail(),
        }
    }

    /// `(...)`: a tuple, a generator expression, a parenthesized yield, or a group (no node of its own).
    fn paren(&mut self) -> R<Node> {
        self.at += 1;
        if self.eat_op(")") {
            return Ok(node(What::Tuple, vec![]));
        }
        if self.is_word("yield") {
            let y = self.yield_expr()?;
            self.expect_op(")")?;
            return Ok(y);
        }
        let first = self.star_named_expression()?;
        if self.starts_comprehension() {
            let mut kids = vec![first];
            kids.extend(self.comprehensions()?);
            self.expect_op(")")?;
            return Ok(other(kids));
        }
        if !self.is_op(",") {
            self.expect_op(")")?;
            return Ok(first);
        }
        let mut elts = vec![first];
        while self.eat_op(",") && !self.is_op(")") {
            elts.push(self.star_named_expression()?);
        }
        self.expect_op(")")?;
        Ok(node(What::Tuple, elts))
    }

    /// `[...]`: a list or a list comprehension.
    fn bracket(&mut self) -> R<Node> {
        self.at += 1;
        if self.eat_op("]") {
            return Ok(node(What::List, vec![]));
        }
        let first = self.star_named_expression()?;
        if self.starts_comprehension() {
            let mut kids = vec![first];
            kids.extend(self.comprehensions()?);
            self.expect_op("]")?;
            return Ok(other(kids));
        }
        let mut elts = vec![first];
        while self.eat_op(",") && !self.is_op("]") {
            elts.push(self.star_named_expression()?);
        }
        self.expect_op("]")?;
        Ok(node(What::List, elts))
    }

    /// `{...}`: a dict (its keys, then its values), a set, or either's comprehension.
    fn brace(&mut self) -> R<Node> {
        self.at += 1;
        if self.eat_op("}") {
            return Ok(other(vec![]));
        }
        let (mut keys, mut values) = (Vec::new(), Vec::new());
        if self.eat_op("**") {
            values.push(self.bitwise_or()?);
        } else {
            let first = self.star_named_expression()?;
            if !self.eat_op(":") {
                if self.starts_comprehension() {
                    let mut kids = vec![first];
                    kids.extend(self.comprehensions()?);
                    self.expect_op("}")?;
                    return Ok(other(kids));
                }
                let mut elts = vec![first];
                while self.eat_op(",") && !self.is_op("}") {
                    elts.push(self.star_named_expression()?);
                }
                self.expect_op("}")?;
                return Ok(other(elts));
            }
            let value = self.expression()?;
            if self.starts_comprehension() {
                let mut kids = vec![first, value];
                kids.extend(self.comprehensions()?);
                self.expect_op("}")?;
                return Ok(other(kids));
            }
            keys.push(first);
            values.push(value);
        }
        while self.eat_op(",") && !self.is_op("}") {
            if self.eat_op("**") {
                values.push(self.bitwise_or()?);
            } else {
                keys.push(self.expression()?);
                self.expect_op(":")?;
                values.push(self.expression()?);
            }
        }
        self.expect_op("}")?;
        keys.extend(values);
        Ok(other(keys))
    }

    fn starts_comprehension(&self) -> bool {
        matches!(self.peek(0), Tok::Name(w) if w == "for")
            || (matches!(self.peek(0), Tok::Name(w) if w == "async")
                && matches!(self.peek(1), Tok::Name(w) if w == "for"))
    }

    /// Each `for target in iter if cond` clause: a `comprehension` (target, iter, ifs).
    fn comprehensions(&mut self) -> R<Vec<Node>> {
        let mut out = Vec::new();
        while self.starts_comprehension() {
            self.eat_word("async");
            self.at += 1;
            let target = self.star_targets()?;
            self.expect_word("in")?;
            let mut kids = vec![target, self.disjunction()?];
            while self.eat_word("if") {
                kids.push(self.disjunction()?);
            }
            out.push(other(kids));
        }
        Ok(out)
    }

    /// A `for` loop's or a comprehension's targets: a tuple when there is a comma.
    pub(super) fn star_targets(&mut self) -> R<Node> {
        let target = self.listed(|p| {
            if p.eat_op("*") {
                return Ok(node(What::Starred, vec![p.bitwise_or()?]));
            }
            p.bitwise_or()
        })?;
        check_target(&target)?;
        Ok(target)
    }

    /// A call's arguments to its `)`: its positional ones, then its keywords (each a `keyword` node).
    pub(super) fn call_args(&mut self) -> R<Vec<Node>> {
        let (mut args, mut keywords, mut keyword_seen, mut unpacked) =
            (Vec::new(), Vec::new(), false, false);
        while !self.is_op(")") {
            if self.eat_op("*") {
                if unpacked {
                    return self.fail();
                }
                args.push(node(What::Starred, vec![self.expression()?]));
            } else if self.eat_op("**") {
                keywords.push(other(vec![self.expression()?]));
                unpacked = true;
            } else if matches!(self.peek(1), Tok::Op("=")) && matches!(self.peek(0), Tok::Name(_)) {
                self.ident()?;
                self.at += 1;
                keywords.push(other(vec![self.expression()?]));
                keyword_seen = true;
            } else {
                let mut arg = self.named_expression()?;
                if self.starts_comprehension() {
                    let mut kids = vec![arg];
                    kids.extend(self.comprehensions()?);
                    arg = other(kids);
                    if !args.is_empty() || !keywords.is_empty() || !self.is_op(")") {
                        return self.fail();
                    }
                }
                if keyword_seen || unpacked {
                    return self.fail();
                }
                args.push(arg);
            }
            if !self.eat_op(",") {
                break;
            }
        }
        self.expect_op(")")?;
        args.extend(keywords);
        Ok(args)
    }

    /// A subscript's slices: one, or a tuple of them.
    fn slices(&mut self) -> R<Node> {
        let mut items = vec![self.slice()?];
        let mut comma = false;
        while self.eat_op(",") {
            comma = true;
            if self.is_op("]") {
                break;
            }
            items.push(self.slice()?);
        }
        self.expect_op("]")?;
        Ok(if comma {
            node(What::Tuple, items)
        } else {
            items.remove(0)
        })
    }

    /// `lower:upper:step` (a `Slice` of the parts given), or an index.
    fn slice(&mut self) -> R<Node> {
        if self.eat_op("*") {
            return Ok(node(What::Starred, vec![self.bitwise_or()?]));
        }
        let mut kids = Vec::new();
        if !self.eat_op(":") {
            let lower = self.named_expression()?;
            if !self.eat_op(":") {
                return Ok(lower);
            }
            kids.push(lower);
        }
        if self.starts_expr() {
            kids.push(self.expression()?);
        }
        if self.eat_op(":") && self.starts_expr() {
            kids.push(self.expression()?);
        }
        Ok(other(kids))
    }

    /// A function's or a lambda's parameters to its `)` or `:`: an `arguments` node, its children `posonlyargs`, `args`, `vararg`,
    /// `kwonlyargs`, `kw_defaults`, `kwarg`, `defaults` (each `arg` holding its annotation).
    pub(super) fn params(&mut self, lambda: bool) -> R<Node> {
        let end = if lambda { ":" } else { ")" };
        let (
            mut posonly,
            mut args,
            mut vararg,
            mut kwonly,
            mut kw_defaults,
            mut kwarg,
            mut defaults,
        ) = (
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
        );
        let mut star = false;
        let annotation = |p: &mut Self, starred: bool| -> R<Vec<Node>> {
            if lambda || !p.eat_op(":") {
                return Ok(vec![]);
            }
            Ok(vec![if starred {
                p.star_expression()?
            } else {
                p.expression()?
            }])
        };
        while !self.is_op(end) {
            if !kwarg.is_empty() {
                return self.fail();
            }
            if self.eat_op("/") {
                if star || !posonly.is_empty() || args.is_empty() {
                    return self.fail();
                }
                posonly.append(&mut args);
            } else if self.eat_op("**") {
                self.ident()?;
                kwarg.push(other(annotation(self, false)?));
            } else if self.eat_op("*") {
                if star {
                    return self.fail();
                }
                star = true;
                if matches!(self.peek(0), Tok::Name(_)) {
                    self.ident()?;
                    vararg.push(other(annotation(self, true)?));
                }
            } else {
                self.ident()?;
                let arg = other(annotation(self, false)?);
                let default = if self.eat_op("=") {
                    Some(self.expression()?)
                } else {
                    None
                };
                if star {
                    kwonly.push(arg);
                    kw_defaults.extend(default);
                } else {
                    if default.is_none() && !defaults.is_empty() {
                        return self.fail();
                    }
                    args.push(arg);
                    defaults.extend(default);
                }
            }
            if !self.eat_op(",") {
                break;
            }
        }
        let mut kids = posonly;
        for part in [args, vararg, kwonly, kw_defaults, kwarg, defaults] {
            kids.extend(part);
        }
        Ok(other(kids))
    }

    /// `yield from x` or `yield [values]`.
    pub(super) fn yield_expr(&mut self) -> R<Node> {
        self.expect_word("yield")?;
        if self.eat_word("from") {
            return Ok(other(vec![self.expression()?]));
        }
        if self.starts_expr() {
            return Ok(other(vec![self.star_expressions()?]));
        }
        Ok(other(vec![]))
    }

    /// An assignment's value: a yield or the expressions.
    pub(super) fn rhs(&mut self) -> R<Node> {
        if self.is_word("yield") {
            return self.yield_expr();
        }
        self.star_expressions()
    }

    /// A run of adjacent string literals: one constant, or one `JoinedStr` whose children are each replacement field
    /// (`FormattedValue`: its value, then its format spec's own `JoinedStr`).
    fn strings(&mut self) -> R<Node> {
        let mut holes = Vec::new();
        let mut formatted = false;
        while let Tok::Str(f, h) = self.peek(0).clone() {
            formatted |= f;
            holes.extend(h);
            self.at += 1;
        }
        if !formatted {
            return Ok(other(vec![]));
        }
        Ok(other(holes.iter().map(field).collect::<R<Vec<Node>>>()?))
    }
}

/// A replacement field's `FormattedValue`.
fn field(hole: &Hole) -> R<Node> {
    let mut p = Parser {
        toks: hole.toks.clone(),
        at: 0,
    };
    let value = p.rhs()?;
    if p.peek(0) != &Tok::End {
        return p.fail();
    }
    let mut kids = vec![value];
    if let Some(spec) = &hole.spec {
        kids.push(other(spec.iter().map(field).collect::<R<Vec<Node>>>()?));
    }
    Ok(other(kids))
}

/// A target `ast.parse` accepts: a name, an attribute, a subscript, or a tuple, list or starred of targets.
///
/// # Errors
///
/// `cannot assign to` anything else.
pub(super) fn check_target(n: &Node) -> R<()> {
    match n.what {
        What::Name(_) | What::Attr(..) | What::Subscript => Ok(()),
        What::Tuple | What::List | What::Starred => n.kids.iter().try_for_each(check_target),
        _ => Err("SyntaxError: cannot assign to expression".to_owned()),
    }
}
