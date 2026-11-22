//! The parse of a Python program on its mask: its statements, roots, functions and the places each builds from its parameter,
//! its writes and their receivers (451 T110; split out of `program.rs` by 451 T118, file-scale's 1,000-line bar).

use super::literal_at;

/// One piece of a path a function builds: a literal's text (the root's, or one the program spells) or the parameter.
#[derive(Clone)]
pub(super) enum Part {
    Text(String),
    Param,
}

/// How a function builds the path it writes from its parameter: its parts, concatenated (`+`, an f-string) or joined as a path (`/`,
/// `os.path.join`, `Path(a, b)`: a part starting with `/` restarts it).
#[derive(Clone)]
pub(super) struct Place {
    pub(super) slash: bool,
    pub(super) parts: Vec<Part>,
}

impl Place {
    /// The path, the parameter bound to the call's literal `lit`.
    pub(super) fn with(&self, lit: &str) -> String {
        let mut out = String::new();
        for part in &self.parts {
            let v = match part {
                Part::Text(t) => t.as_str(),
                Part::Param => lit,
            };
            if self.slash && v.starts_with('/') {
                out.clear();
            } else if self.slash && !out.is_empty() && !out.ends_with('/') {
                out.push('/');
            }
            out.push_str(v);
        }
        out
    }
}

/// A function the program defines: its name, each parameter a call can bind (its name and its position, `None` keyword-only), and the
/// span of its body.
pub(super) struct Def<'a> {
    pub(super) name: &'a str,
    pub(super) params: Vec<(&'a str, Option<usize>)>,
    pub(super) body: (usize, usize),
}

/// A program read for its functions: its text (`without_text`'s copy), the same with each string's content `~` and each comment
/// blank (`mask`), and its roots - each top-level name bound once, to a literal, and that literal.
pub(super) struct Program<'a> {
    pub(super) text: &'a str,
    pub(super) mask: String,
    pub(super) roots: Vec<(&'a str, &'a str)>,
}

/// Whether `c` can be in a Python name.
pub(super) fn word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// Whether `s` is a Python name.
pub(super) fn name(s: &str) -> bool {
    s.chars().next().is_some_and(|c| !c.is_numeric()) && s.chars().all(word)
}

/// The program byte for byte with each string's content `~` and each comment blank, so its brackets, commas, `def`s and calls are
/// its code's alone (a parenthesis or a `def` inside a string or a comment is neither; gate-write's `masked`, read here as plain code):
/// quotes single, double and triple, a backslash's escape, and a single-quoted string the line ends before it closes.
pub(super) fn mask(body: &str) -> String {
    let b = body.as_bytes();
    let mut out = b.to_vec();
    let mut i = 0;
    while let Some(&ch) = b.get(i) {
        match ch {
            b'#' => {
                while let Some(o) = out.get_mut(i).filter(|o| **o != b'\n') {
                    *o = b' ';
                    i += 1;
                }
            }
            q @ (b'\'' | b'"') => {
                let triple = b.get(i + 1..i + 3) == Some(&[q, q][..]);
                i += if triple { 3 } else { 1 };
                while let Some(&c) = b.get(i) {
                    let closes = c == q && (!triple || b.get(i + 1..i + 3) == Some(&[q, q][..]));
                    if closes || (!triple && c == b'\n') {
                        i += if closes && triple { 2 } else { 0 };
                        break;
                    }
                    let skip = if c == b'\\' { 2 } else { 1 };
                    for o in out.iter_mut().skip(i).take(skip) {
                        *o = b'~';
                    }
                    i += skip;
                }
            }
            _ => {}
        }
        i += 1;
    }
    // every byte replaced is ASCII and every one replaced is a whole character's, so the copy stays UTF-8
    String::from_utf8(out).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The index of the bracket closing the one at `open`.
pub(super) fn closing(mask: &str, open: usize) -> Option<usize> {
    let mut depth = 0;
    for (i, c) in mask.bytes().enumerate().skip(open) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' => {
                depth -= 1;
                if depth == 0 {
                    return Some(i);
                }
            }
            _ => {}
        }
    }
    None
}

/// The spans of `mask[from..to]` between its `sep` bytes outside brackets.
pub(super) fn split(mask: &str, (from, to): (usize, usize), sep: &[u8]) -> Vec<(usize, usize)> {
    let (mut out, mut depth, mut at) = (Vec::new(), 0, from);
    for (i, c) in mask.bytes().enumerate().take(to).skip(from) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' => depth -= 1,
            _ if depth == 0 && sep.contains(&c) => {
                out.push((at, i));
                at = i + 1;
            }
            _ => {}
        }
    }
    out.push((at, to));
    out
}

/// The span with the whitespace at its ends dropped, read on the mask, so a comment ends a statement as a blank does.
pub(super) fn trimmed(text: &str, (from, to): (usize, usize)) -> (usize, usize) {
    let s = &text[from..to];
    let start = from + (s.len() - s.trim_start().len());
    (start, start + s.trim().len())
}

impl<'a> Program<'a> {
    pub(super) fn new(text: &'a str) -> Self {
        let mut p = Program {
            text,
            mask: mask(text),
            roots: Vec::new(),
        };
        for (s, e) in p.statements((0, text.len())) {
            let at_line = s == 0 || p.mask[..s].ends_with('\n');
            let Some((n, rhs)) = p.assigned((s, e)).filter(|_| at_line) else {
                continue;
            };
            let value = p.literal(rhs).or_else(|| {
                p.call(rhs, &["Path", "pathlib.Path"])
                    .filter(|args| args.len() == 1)
                    .and_then(|args| p.literal(args[0]))
            });
            if let Some(v) = value.filter(|_| p.binds((0, text.len()), n) == 1) {
                p.roots.push((n, v));
            }
        }
        p
    }

    /// The statements of a span: its pieces between newlines and `;`, outside brackets, each trimmed, none empty.
    pub(super) fn statements(&self, span: (usize, usize)) -> Vec<(usize, usize)> {
        split(&self.mask, span, b"\n;")
            .into_iter()
            .map(|s| trimmed(&self.mask, s))
            .filter(|(s, e)| s < e)
            .collect()
    }

    /// `NAME = <rhs>`: the name and the span of what it is bound to.
    pub(super) fn assigned(&self, (s, e): (usize, usize)) -> Option<(&'a str, (usize, usize))> {
        let eq = s + self.mask[s..e].find('=')?;
        let n = self.text[s..eq].trim_end();
        (name(n) && !self.mask[eq + 1..e].starts_with('='))
            .then(|| (n, trimmed(&self.mask, (eq + 1, e))))
    }

    /// The literal a span is, whole (a quote, a path's characters, the same quote).
    pub(super) fn literal(&self, (s, e): (usize, usize)) -> Option<&'a str> {
        let t = &self.text[s..e];
        (literal_at(t) == Some(t.len())).then(|| &t[1..t.len() - 1])
    }

    /// The arguments of a span that is wholly a call of one of `callees`.
    pub(super) fn call(
        &self,
        (s, e): (usize, usize),
        callees: &[&str],
    ) -> Option<Vec<(usize, usize)>> {
        let open = s + self.mask[s..e].find('(')?;
        let callee = self.text[s..open].trim_end();
        (callees.contains(&callee) && closing(&self.mask, open) == Some(e - 1)).then(|| {
            split(&self.mask, (open + 1, e - 1), b",")
                .into_iter()
                .map(|a| trimmed(&self.mask, a))
                .collect()
        })
    }

    /// How many times `n` is bound in a span: assigned (`n =`, `n +=`, `n :=`; a keyword argument `n=` too, failing open), or named
    /// after `def`, `class`, `for`, `as`, `import`, `global` or `nonlocal`.
    pub(super) fn binds(&self, (from, to): (usize, usize), n: &str) -> usize {
        self.mask[from..to]
            .match_indices(n)
            .filter(|&(i, _)| {
                let (before, after) = (&self.mask[..from + i], &self.mask[from + i + n.len()..]);
                if before.ends_with(|c: char| word(c) || c == '.') || after.starts_with(word) {
                    return false;
                }
                let prior = before.trim_end().rsplit(|c: char| !word(c)).next();
                let rest = after.trim_start().trim_start_matches([
                    '+', '-', '*', '/', '%', '&', '|', '^', '@', '<', '>', ':', '!',
                ]);
                matches!(
                    prior,
                    Some("def" | "class" | "for" | "as" | "import" | "global" | "nonlocal")
                ) || (rest.starts_with('=') && !rest.starts_with("=="))
            })
            .count()
    }

    /// The functions the program defines once (`def NAME(..):` beginning a line), each with its parameters and its body: the rest of
    /// its line, or the lines indented past it.
    pub(super) fn defs(&self) -> Vec<Def<'a>> {
        let mut out = Vec::new();
        for (s, e) in self.statements((0, self.text.len())) {
            let Some(rest) = self.mask[s..e].strip_prefix("def") else {
                continue;
            };
            let Some(open) = rest
                .starts_with([' ', '\t'])
                .then(|| rest.find('('))
                .flatten()
                .map(|i| s + 3 + i)
            else {
                continue;
            };
            let n = self.text[s + 3..open].trim();
            let Some(close) = closing(&self.mask, open) else {
                continue;
            };
            let colon = split(&self.mask, (close + 1, e), b":")[0].1;
            if !name(n) || colon == e || self.binds((0, self.text.len()), n) != 1 {
                continue;
            }
            let mut params = Vec::new();
            let mut position = Some(0);
            for a in split(&self.mask, (open + 1, close), b",") {
                let a = trimmed(&self.mask, a);
                let t = &self.text[a.0..a.1];
                if t.starts_with('*') {
                    position = None;
                    continue;
                }
                let p = t.split([':', '=']).next().unwrap_or(t).trim();
                if name(p) {
                    params.push((p, position));
                    position = position.map(|p| p + 1);
                }
            }
            out.push(Def {
                name: n,
                params,
                body: self.body_of(s, colon),
            });
        }
        out
    }

    /// A def's body: the rest of its line past the colon if it holds code (its `;`s' statements too), else every line after it indented
    /// past the def's own.
    pub(super) fn body_of(&self, s: usize, colon: usize) -> (usize, usize) {
        let eol = split(&self.mask, (colon + 1, self.text.len()), b"\n")[0].1;
        if !self.mask[colon + 1..eol].trim().is_empty() {
            return (colon + 1, eol);
        }
        let indent = s - self.mask[..s].rfind('\n').map_or(0, |i| i + 1);
        let mut end = eol;
        for (ls, le) in split(&self.mask, (eol, self.text.len()), b"\n")
            .into_iter()
            .skip(1)
        {
            let line = &self.mask[ls..le];
            if !line.trim().is_empty() && line.len() - line.trim_start().len() <= indent {
                break;
            }
            end = le;
        }
        (eol, end)
    }

    /// Each place `def` writes its parameter `param` onto a root: each write in its body whose path is the parameter joined onto a
    /// root, or a name the body binds once to that join. A parameter the body rebinds counts only as the name of its one join.
    pub(super) fn places(&self, def: &Def, param: &str) -> Vec<Place> {
        let mut names: Vec<(&str, Place)> = Vec::new();
        for st in self.statements(def.body) {
            if let Some((n, rhs)) = self.assigned(st) {
                if let Some(place) = self
                    .join(rhs, Some(param), &def.params)
                    .filter(|_| self.binds(def.body, n) == 1)
                {
                    names.push((n, place));
                }
            }
        }
        let rebound = self.binds(def.body, param) > 0;
        let local = |n: &str| names.iter().find(|(m, _)| *m == n).map(|(_, p)| p.clone());
        let mut out = Vec::new();
        for path in self.writes(def.body) {
            let t = &self.text[path.0..path.1];
            let place = if name(t) {
                local(t)
            } else if rebound {
                None
            } else {
                self.join(path, Some(param), &def.params)
            };
            out.extend(place);
        }
        out
    }

    /// Each write whose path joins a root and literals alone, no parameter (`open(root+'x.rs', 'w')`): where its path starts, and the
    /// path. The literal's own reading drops it as a tail on a base it cannot see (`joined_on`), so here is where `placed` names it.
    /// A name the program binds once to such a join, and no parameter's, stands for it (`p = root + 'x.rs'; open(p, 'w')`: 18 writes
    /// in 8 of the session's commands, 0 of T93's, measured 2026-11-21, `/tmp/t110/scripts/toplevel-named.py`).
    pub(super) fn constants(&self, shadow: &[(&str, Option<usize>)]) -> Vec<(usize, String)> {
        let all = (0, self.text.len());
        let mut names: Vec<(&str, Place)> = Vec::new();
        for st in self.statements(all) {
            if let Some((n, rhs)) = self.assigned(st) {
                // the join first: the count of its bindings scans the whole program
                let free =
                    |_: &Place| self.binds(all, n) == 1 && !shadow.iter().any(|(p, _)| *p == n);
                names.extend(self.join(rhs, None, shadow).filter(free).map(|p| (n, p)));
            }
        }
        let mut out = Vec::new();
        for path in self.writes(all) {
            let t = &self.text[path.0..path.1];
            let place = if name(t) {
                names.iter().find(|(m, _)| *m == t).map(|(_, p)| p.clone())
            } else {
                self.join(path, None, shadow)
            };
            out.extend(place.map(|p| (path.0, p.with(""))));
        }
        out
    }

    /// The span of each path a write in `span` writes: `open(X, <w, a or x>)`, `X.write_text(`, `X.write_bytes(`.
    pub(super) fn writes(&self, span: (usize, usize)) -> Vec<(usize, usize)> {
        let m = &self.mask[span.0..span.1];
        let mut out = Vec::new();
        for (i, _) in m.match_indices("open(") {
            let at = span.0 + i;
            if self.mask[..at].ends_with(|c: char| word(c) || c == '.') {
                continue;
            }
            let Some(close) = closing(&self.mask, at + 4) else {
                continue;
            };
            let args: Vec<_> = split(&self.mask, (at + 5, close), b",")
                .into_iter()
                .map(|a| trimmed(&self.mask, a))
                .collect();
            let mode = args.iter().skip(1).find_map(|&(s, e)| {
                let t = &self.text[s..e];
                let t = t
                    .strip_prefix("mode")
                    .map_or(Some(t), |r| r.trim_start().strip_prefix('='));
                t.and_then(|t| literal_at(t.trim()).map(|_| t.trim()))
            });
            if mode.is_some_and(|t| t.contains(['w', 'a', 'x'])) {
                out.push(args[0]);
            }
        }
        for (i, _) in m
            .match_indices(".write_text(")
            .chain(m.match_indices(".write_bytes("))
        {
            out.extend(self.receiver(span.0 + i));
        }
        out
    }

    /// What a method is called on, ending at `dot`: a name, a parenthesized expression, or a call of `Path` - none for another call.
    pub(super) fn receiver(&self, dot: usize) -> Option<(usize, usize)> {
        let end = self.mask[..dot].trim_end().len();
        if self.mask[..end].ends_with(')') {
            let mut depth = 0;
            let (open, _) = self.mask[..end].char_indices().rev().find(|&(_, c)| {
                depth += match c {
                    ')' | ']' | '}' => 1,
                    '(' | '[' | '{' => -1,
                    _ => 0,
                };
                depth == 0
            })?;
            // the dotted name the parenthesis follows with nothing between: none is a parenthesized expression
            let start = self.mask[..open]
                .trim_end_matches(|c: char| word(c) || c == '.')
                .len();
            return match &self.text[start..open] {
                "" | "Path" | "pathlib.Path" => Some((start, end)),
                _ => None,
            };
        }
        let start = self.mask[..end].trim_end_matches(word).len();
        (start < end && !self.mask[..start].ends_with('.')).then_some((start, end))
    }

    /// The place a span builds from `param` (none: from no parameter) and a root: a join of operands, one the parameter where there is
    /// one, and one or more a root or a literal. `shadow` holds the parameters whose names are no root's here.
    pub(super) fn join(
        &self,
        span: (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Place> {
        let (s, e) = trimmed(&self.mask, span);
        let m = &self.mask[s..e];
        if m.starts_with('(') && closing(&self.mask, s) == Some(e - 1) {
            return self.join((s + 1, e - 1), param, shadow);
        }
        let (slash, operands) = if let Some(args) = self.call((s, e), &["Path", "pathlib.Path"]) {
            if let [one] = args[..] {
                return self.join(one, param, shadow);
            }
            (true, args)
        } else if let Some(args) = self.call((s, e), &["os.path.join", "path.join", "join"]) {
            (true, args)
        } else if let Some(parts) = self.fstring((s, e), param, shadow) {
            return Some(parts);
        } else {
            let plus = split(&self.mask, (s, e), b"+");
            let slash = split(&self.mask, (s, e), b"/");
            match (plus.len(), slash.len()) {
                (1, n) if n > 1 && !m.contains("//") => (true, slash),
                (n, 1) if n > 1 => (false, plus),
                _ => return None,
            }
        };
        let parts = operands
            .into_iter()
            .map(|o| self.operand(o, param, shadow))
            .collect::<Option<Vec<_>>>()?;
        Self::valid(Place { slash, parts }, param.is_some())
    }

    /// A place of two parts or more, one of them the parameter where there is one (`param`), else none.
    pub(super) fn valid(place: Place, param: bool) -> Option<Place> {
        let params = place
            .parts
            .iter()
            .filter(|p| matches!(p, Part::Param))
            .count();
        (params == usize::from(param) && place.parts.len() > 1).then_some(place)
    }

    /// One operand of a join: the parameter, a root (no parameter in `shadow` of its name), a literal, or `Path(` one of them `)`.
    pub(super) fn operand(
        &self,
        span: (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Part> {
        let (s, e) = trimmed(&self.mask, span);
        let t = &self.text[s..e];
        if param == Some(t) {
            return Some(Part::Param);
        }
        if let Some(v) = self.root(t, shadow) {
            return Some(Part::Text(v.to_owned()));
        }
        if let Some(lit) = self.literal((s, e)) {
            return Some(Part::Text(lit.to_owned()));
        }
        match self.call((s, e), &["Path", "pathlib.Path"])?[..] {
            [one] => self.operand(one, param, shadow),
            _ => None,
        }
    }

    /// The literal a root name is bound to, where no parameter in `shadow` has that name.
    pub(super) fn root(&self, n: &str, shadow: &[(&str, Option<usize>)]) -> Option<&'a str> {
        let shadowed = shadow.iter().any(|(p, _)| *p == n);
        self.roots
            .iter()
            .find(|(r, _)| *r == n && !shadowed)
            .map(|(_, v)| *v)
    }

    /// An f-string the span wholly is, each placeholder a bare name - the parameter or a root - and its text between: a concatenation.
    pub(super) fn fstring(
        &self,
        (s, e): (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Place> {
        let t = &self.text[s..e];
        let quote = t
            .strip_prefix(['f', 'F'])?
            .chars()
            .next()
            .filter(|q| matches!(q, '\'' | '"'))?;
        let inner = t[2..].strip_suffix(quote)?;
        if self.mask[s + 2..e - 1].contains(['\'', '"']) {
            return None;
        }
        let mut parts = Vec::new();
        let mut rest = inner;
        while let Some(open) = rest.find('{') {
            let close = open + rest[open..].find('}')?;
            let (text, n) = (&rest[..open], &rest[open + 1..close]);
            if text.contains('}') {
                return None;
            }
            if !text.is_empty() {
                parts.push(Part::Text(text.to_owned()));
            }
            parts.push(if param == Some(n) {
                Part::Param
            } else {
                Part::Text(self.root(n, shadow)?.to_owned())
            });
            rest = &rest[close + 1..];
        }
        if rest.contains('}') {
            return None;
        }
        if !rest.is_empty() {
            parts.push(Part::Text(rest.to_owned()));
        }
        Self::valid(
            Place {
                slash: false,
                parts,
            },
            param.is_some(),
        )
    }

    /// Each call of the function `f` that hands its parameter `param` (at `pos`, or by keyword) a literal: the literal's start and the
    /// path `place` builds from it.
    pub(super) fn calls(
        &self,
        f: &str,
        param: &str,
        pos: Option<usize>,
        place: &Place,
    ) -> Vec<(usize, String)> {
        let mut out = Vec::new();
        for (i, _) in self.mask.match_indices(f) {
            let before = &self.mask[..i];
            let after = self.mask[i + f.len()..].trim_start();
            if before.ends_with(|c: char| word(c) || c == '.')
                || before.trim_end().ends_with("def")
                || !after.starts_with('(')
            {
                continue;
            }
            let open = self.mask.len() - after.len();
            let Some(close) = closing(&self.mask, open) else {
                continue;
            };
            let mut at = Some(0);
            for a in split(&self.mask, (open + 1, close), b",") {
                let (s, e) = trimmed(&self.mask, a);
                let value = match self.assigned((s, e)) {
                    Some((kw, v)) => (kw == param).then_some(v),
                    None if self.text[s..e].starts_with('*') => {
                        at = None;
                        None
                    }
                    None => {
                        let here = at.is_some() && at == pos;
                        at = at.map(|n| n + 1);
                        here.then_some((s, e))
                    }
                };
                if let Some((v, lit)) = value.and_then(|v| Some((v, self.literal(v)?))) {
                    out.push((v.0 + 1, place.with(lit)));
                }
            }
        }
        out
    }
}
