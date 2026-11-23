//! THE RUST ENGINES' DRAWING CODE (feature 449 T237): a change to it owes the glyph-check of each element it redraws. The drawing-code
//! list (`CODE`) named only the Python and the pool's specs, so a change to a Rust stage's drawing - T234's sluice frame - owed no
//! glyph-check until an Occasions line was written by hand. The code is read item by item (a function, a constant, a type), at the
//! base and now, and an item whose comment-free tokens differ is CHANGED. What a changed item redraws:
//!
//! - a DRAW FUNCTION (it takes the engine's writer, `Svg`) redraws the kinds it names - `data-kind="..."` in the Mode A compound's
//!   marks, the whole function's; in the hamlet driver, whose writer is told the kind before the marks (`svg.kind("...")`), a changed
//!   line redraws the kind named last at or above it, which cannot be told above the first naming or past one chosen at run time
//!   (measured 2026-11-20 on T234's own change: read whole, `draw_polder`'s deleted square owed the comb's and the polder's whole
//!   legends, 19 units, where read by line it owes the sluice gate alone); one that names no kind draws its caller's; a compound mark
//!   changed on both sides owes the kinds its changed lines name by literal (a `data-kind="..."` or a caption's kind), and is read
//!   whole only where they name none (`named_by_change`, the round arbiter's `ask:glyph-wave-449-T289`: T291's genkan porch, one
//!   branch naming `genkan`, read whole owed 57 units);
//! - a WRITER method (`impl Svg`), a helper function or a constant redraws what its uses redraw (a use is its name called or read in
//!   another item); a writer method whose uses reach no element is the document every mark is written into, which cannot be told;
//! - a ROLL (it makes the writer: `Svg::default()`, `Svg::new()`) is read line by line: a changed line that does not touch the
//!   writer is the stages' plumbing and redraws nothing; one that calls a draw function redraws that function's kinds (a draw function
//!   read by line too); any other line that touches the writer redraws the kind it is drawn under, the last named above it, which
//!   cannot be told past a draw function's call or a kind chosen at run time;
//! - a type, an import or a test redraws nothing by itself: the code that fills or reads it is what changes a mark.
//!
//! Each element told is owed on the first map of the engine's kind (live pool first) whose legend draws it - the declared route's
//! choice, so the two share a slug and merge; where it cannot be told, each element of a compound's legend whose drawn marks differ
//! between its drawing at the base and now is owed, on the first map where they differ (`marks.rs`, 449 T377: the whole legend owed 53
//! units on 449 T351's bundle, 48 on marks unchanged or only displaced), and the whole legend of each such map, each element once, only
//! where the marks cannot be compared - the hamlet driver's (its marks are not read by kind), a drawing not current or not known at the
//! base, a difference no kind owns - and the occasion says which. A map's legend is its drawing now, else (not current: the change
//! itself made it stale) its drawing at the base. No size-audit is owed: a redrawn glyph is judged, its size is not new to the map. A change that redraws an element is refused
//! nothing for want of a declaration: what it owes is read from the change itself. A change of this code that redraws NO element (a
//! stage function in the driver, a roll's line handing the stages their ground) places or plumbs, and is refused undeclared, as a
//! stage's change is (`placed`, 449 T238).

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::codeid::rust_tokens;
use l7r_gate_core::difflib::matching_blocks;
use l7r_gate_pool::{Kind, LEGACY};

use super::{found, git, marks, re, Folder, Legends, Tree, Unit, NOT_ELEMENTS};
use crate::record::bundle::py_repr;
use crate::record::repo::{cat_blobs, universal};

/// How an engine names the kind of a mark: the hamlet driver's writer is told it before the marks (`svg.kind("weir")`), the Mode A
/// compound's tags each mark (`data-kind="well"`).
#[derive(Clone, Copy)]
enum Marker {
    Setter,
    Attribute,
}

impl Marker {
    /// Every naming of a kind, and a naming by a literal.
    fn patterns(self) -> (&'static Regex, &'static Regex) {
        static SET: LazyLock<Regex> = LazyLock::new(|| re(r"\.kind\("));
        static SET_LIT: LazyLock<Regex> = LazyLock::new(|| re(r#"\.kind\("([^"\\]*)"\)"#));
        static ATTR: LazyLock<Regex> = LazyLock::new(|| re(r#"data-kind=""#));
        static ATTR_LIT: LazyLock<Regex> = LazyLock::new(|| re(r#"data-kind="([^"{]*)""#));
        match self {
            Self::Setter => (&SET, &SET_LIT),
            Self::Attribute => (&ATTR, &ATTR_LIT),
        }
    }

    /// The kinds `text` names: `Some` those it names by literal (`-` among them), `None` where any is chosen at run time.
    fn named(self, text: &str) -> Option<BTreeSet<String>> {
        let (all, lit) = self.patterns();
        let told: Vec<String> = lit
            .captures_iter(text)
            .map_while(Result::ok)
            .map(|c| c[1].to_owned())
            .collect();
        (all.find_iter(text).map_while(Result::ok).count() == told.len())
            .then(|| told.into_iter().collect())
    }
}

/// An engine whose drawing code is read here: what it is called in an occasion, the maps it draws, how it names a kind, its files
/// (a directory's own `.rs` files where a path ends in `/`; a `tests.rs` never).
///
/// Measured 2026-11-20 (grep of `Svg::default`, `Svg::new`, `.kind(` and `data-kind=` over `rust/`, tests set aside): the hamlet
/// driver's marks are all written in `rust/phases/src/driver.rs` and `driver/` (`svg.rs` the writer, `draw_*` and the two rolls); the
/// stages under `rust/phases/src/` (field, sink, seat, hem, waterward, course) name no kind and touch no writer - their changes move
/// what is placed, which `placement-changed` declares, and the push is refused until one is declared (`placed`, 449 T238). The Mode A compound's `.svg` is written by `compound::sheet` alone (the one
/// `emit::Svg::new` outside tests), through `compound/emit.rs` and `emit_parts.rs`; `caption_place` places its captions after, and the
/// page writer and the raster draw the page around the sheet, never an element's mark. A hand sheet's marks are its `.svg`, its spec,
/// which `CODE` names already.
struct Engine {
    what: &'static str,
    kind: Kind,
    marker: Marker,
    paths: &'static [&'static str],
}

const ENGINES: [Engine; 2] = [
    Engine {
        what: "the hamlet driver",
        kind: Kind::Hamlet,
        marker: Marker::Setter,
        paths: &["rust/phases/src/driver.rs", "rust/phases/src/driver/"],
    },
    Engine {
        what: "the Mode A compound engine",
        kind: Kind::Compound,
        marker: Marker::Attribute,
        paths: &[
            "rust/mode_a/src/compound.rs",
            "rust/mode_a/src/compound/emit.rs",
            "rust/mode_a/src/compound/emit_parts.rs",
        ],
    },
];

impl Engine {
    fn holds(&self, path: &str) -> bool {
        Path::new(path).extension().is_some_and(|x| x == "rs")
            && !path.ends_with("tests.rs")
            && self.paths.iter().any(|p| {
                if p.ends_with('/') {
                    path.strip_prefix(p).is_some_and(|rest| !rest.contains('/'))
                } else {
                    path == *p
                }
            })
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Role {
    Writer,
    Draw,
    Roll,
    Helper,
    Constant,
    Shape,
}

/// One item of a file: its name (`Owner.name` for a method), its role, the writer's name in a roll, its lines.
#[derive(Debug)]
struct Item {
    file: String,
    name: String,
    bare: String,
    owned: bool,
    role: Role,
    binding: String,
    lines: Vec<String>,
}

static HEAD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:const|async|unsafe)\s+)*(fn|const|static|struct|enum|type|trait|impl|mod|use|macro_rules!)\s*(\w*)",
    )
});
static IMPL_FOR: LazyLock<Regex> = LazyLock::new(|| re(r"\bfor\s+(?:\w+::)*(\w+)"));
static IMPL_OF: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\s*impl\s*(?:<[^{]*?>)?\s*(?:\w+::)*(\w+)"));
static WRITER_ARG: LazyLock<Regex> =
    LazyLock::new(|| re(r"(\w+)\s*:\s*&\s*(?:mut\s+)?(?:\w+::)*Svg\b"));
static WRITER_MADE: LazyLock<Regex> =
    LazyLock::new(|| re(r"let\s+(?:mut\s+)?(\w+)\s*=\s*(?:\w+::)*Svg::(?:default|new)\s*\("));

fn comment(line: &str) -> bool {
    let t = line.trim();
    t.is_empty() || t.starts_with("//")
}

/// Past the item opening at char `start`: its matching `}`, or the `;` ending a body-less item - strings, chars and comments skipped
/// (the claims reader's `item_end`, whose crate builds on this one).
fn item_end(text: &[char], start: usize) -> usize {
    let len = text.len();
    let (mut at, mut depth, mut nest) = (start, 0i64, 0i64);
    let find = |from: usize, needle: &[char]| (from..len).find(|&k| text[k..].starts_with(needle));
    while at < len {
        let ch = text[at];
        if text[at..].starts_with(&['/', '/']) {
            at = find(at, &['\n']).unwrap_or(len);
        } else if text[at..].starts_with(&['/', '*']) {
            at = find(at + 2, &['*', '/']).map_or(len, |k| k + 2);
        } else if let Some(close) = raw_end(text, at) {
            at = close;
        } else if ch == '"' {
            let mut k = at + 1;
            while k < len && text[k] != '"' {
                k += if text[k] == '\\' { 2 } else { 1 };
            }
            at = k + 1;
        } else if ch == '\'' && at + 2 < len && (text[at + 2] == '\'' || text[at + 1] == '\\') {
            at = find(at + 2, &['\'']).map_or(len, |k| k + 1);
        } else {
            match ch {
                '{' => depth += 1,
                '}' => {
                    depth -= 1;
                    if depth == 0 {
                        return at + 1;
                    }
                }
                '(' | '[' => nest += 1,
                ')' | ']' => nest -= 1,
                ';' if depth == 0 && nest == 0 => return at + 1,
                _ => {}
            }
            at += 1;
        }
    }
    len
}

/// Past the raw string opening at char `at` (`r`, its hashes, a quote), or None where none opens there.
fn raw_end(text: &[char], at: usize) -> Option<usize> {
    if text[at] != 'r' || (at > 0 && (text[at - 1].is_alphanumeric() || text[at - 1] == '_')) {
        return None;
    }
    let hashes = text[at + 1..].iter().take_while(|&&c| c == '#').count();
    let open = at + 1 + hashes;
    if text.get(open) != Some(&'"') {
        return None;
    }
    let close: Vec<char> = std::iter::once('"')
        .chain(std::iter::repeat_n('#', hashes))
        .collect();
    Some(
        (open + 1..text.len())
            .find(|&k| text[k..].starts_with(&close))
            .map_or(text.len(), |k| k + close.len()),
    )
}

/// Each item of `text` (an `impl`'s methods and a module's items inside it; a `#[cfg(test)]` module or one named `tests` never).
fn items(text: &str, file: &str, owner: Option<&str>, out: &mut Vec<Item>) {
    let chars: Vec<char> = text.chars().collect();
    let lines: Vec<&str> = text.split_inclusive('\n').collect();
    let mut starts = vec![0usize];
    for line in &lines {
        starts.push(starts[starts.len() - 1] + line.chars().count());
    }
    let (mut k, mut in_test) = (0, false);
    while k < lines.len() {
        let Some(c) = HEAD.captures(lines[k]).ok().flatten() else {
            in_test |= lines[k].trim_start().starts_with("#[cfg(test)]");
            k += 1;
            continue;
        };
        let end = item_end(&chars, starts[k]);
        let last = (k..lines.len())
            .find(|&i| starts[i + 1] >= end)
            .unwrap_or(lines.len() - 1);
        let body: String = chars[starts[k]..end].iter().collect();
        let (word, name) = (&c[1], &c[2]);
        let inner = || {
            let open = body.find('{')?;
            body.trim_end()
                .strip_suffix('}')
                .and_then(|b| b.get(open + 1..))
        };
        match word {
            "impl" => {
                let head = body.split('{').next().unwrap_or_default();
                let target = found_in(&IMPL_FOR, head).or_else(|| found_in(&IMPL_OF, head));
                if let (Some(target), Some(inside)) = (target, inner()) {
                    items(inside, file, Some(&target), out);
                }
            }
            "mod" => {
                if let Some(inside) = inner().filter(|_| !in_test && name != "tests") {
                    items(inside, file, owner, out);
                }
            }
            "use" => {}
            _ => out.push(item(file, owner, word, name, &body, &lines[k..=last])),
        }
        in_test = false;
        k = last + 1;
    }
}

fn found_in(pattern: &Regex, text: &str) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .map(|c| c[1].to_owned())
}

fn item(
    file: &str,
    owner: Option<&str>,
    word: &str,
    name: &str,
    body: &str,
    lines: &[&str],
) -> Item {
    let signature = body.split('{').next().unwrap_or_default();
    let (handed, made) = (
        found_in(&WRITER_ARG, signature),
        found_in(&WRITER_MADE, body),
    );
    let role = match word {
        "fn" if owner == Some("Svg") => Role::Writer,
        "fn" if handed.is_some() => Role::Draw,
        "fn" if made.is_some() => Role::Roll,
        "fn" => Role::Helper,
        "const" | "static" => Role::Constant,
        _ => Role::Shape,
    };
    Item {
        file: file.to_owned(),
        name: owner.map_or_else(|| name.to_owned(), |o| format!("{o}.{name}")),
        bare: name.to_owned(),
        owned: owner.is_some(),
        role,
        binding: handed.or(made).unwrap_or_default(),
        lines: lines
            .iter()
            .map(|l| l.trim_end_matches(['\n', '\r']).to_owned())
            .collect(),
    }
}

/// What a change redraws: the kinds told, and whether some cannot be told.
#[derive(Clone, Default, Debug)]
struct Reach {
    told: BTreeSet<String>,
    whole: bool,
}

impl Reach {
    fn add(&mut self, other: &Self) {
        self.told.extend(other.told.iter().cloned());
        self.whole |= other.whole;
    }

    fn whole() -> Self {
        Self {
            told: BTreeSet::new(),
            whole: true,
        }
    }

    fn named(kinds: Option<BTreeSet<String>>) -> Self {
        kinds.map_or_else(Self::whole, |told| Self { told, whole: false })
    }

    /// Whether it redraws an element: one told that is no placeholder, or ones that cannot be told.
    fn reaches(&self) -> bool {
        self.whole
            || self
                .told
                .iter()
                .any(|k| !NOT_ELEMENTS.contains(&k.as_str()))
    }
}

/// An engine's files at one side of the delta, as items, and what each item reaches (worked out once a run).
struct World {
    marker: Marker,
    items: Vec<Item>,
    memo: Vec<Option<Reach>>,
    /// Each draw function's kinds named, read whole (`Marker::named`), and the pattern of a call of it.
    draws: Vec<(usize, Option<BTreeSet<String>>, Regex)>,
}

impl World {
    fn new(marker: Marker, files: &[(String, String)]) -> Self {
        let mut items_of = Vec::new();
        for (file, text) in files {
            items(text, file, None, &mut items_of);
        }
        let memo = vec![None; items_of.len()];
        let mut world = Self {
            marker,
            items: items_of,
            memo,
            draws: Vec::new(),
        };
        world.draws = (0..world.items.len())
            .filter(|&d| world.items[d].role == Role::Draw)
            .map(|d| {
                let call = re(&format!(r"\b{}\s*\(", world.items[d].bare));
                (d, marker.named(&world.text(d)), call)
            })
            .collect();
        world
    }

    /// Draw function `d`'s kinds named, read whole.
    fn named(&self, d: usize) -> Option<BTreeSet<String>> {
        self.draws
            .iter()
            .find(|(x, _, _)| *x == d)
            .and_then(|(_, kinds, _)| kinds.clone())
    }

    fn find(&self, file: &str, name: &str) -> Option<usize> {
        self.items
            .iter()
            .position(|i| i.file == file && i.name == name)
    }

    /// The text a draw function names its kinds in: its lines but its comments.
    fn text(&self, i: usize) -> String {
        self.items[i]
            .lines
            .iter()
            .filter(|l| !comment(l))
            .cloned()
            .collect::<Vec<_>>()
            .join("\n")
    }

    /// Each line of another function or constant that calls or reads item `i`: `(item, line)`.
    fn uses(&self, i: usize) -> Vec<(usize, usize)> {
        let it = &self.items[i];
        let n = &it.bare;
        let pattern = match it.role {
            Role::Writer => format!(r"(?:\.|\bSvg::){n}\s*\("),
            Role::Constant => format!(r"\b{n}\b"),
            _ if it.owned => format!(r"(?:\.|::){n}\s*\("),
            // a free function's call, never a method's of the same name (`toe::grow` against the writer's `self.grow`)
            _ => format!(r"(?<!\.)\b{n}\s*\("),
        };
        let (uses, defines) = (re(&pattern), re(&format!(r"\bfn\s+{n}\b")));
        let mut out = Vec::new();
        for (j, other) in self.items.iter().enumerate() {
            if j == i || other.role == Role::Shape {
                continue;
            }
            for (k, line) in other.lines.iter().enumerate() {
                if line.contains(n.as_str())
                    && !comment(line)
                    && found(&uses, line)
                    && !found(&defines, line)
                {
                    out.push((j, k));
                }
            }
        }
        out
    }

    fn through_uses(&mut self, i: usize) -> Reach {
        let mut r = Reach::default();
        for (j, k) in self.uses(i) {
            let got = self.line(j, k);
            r.add(&got);
        }
        r
    }

    /// What item `i` redraws, changed as a whole.
    fn reach(&mut self, i: usize) -> Reach {
        if let Some(known) = &self.memo[i] {
            return known.clone();
        }
        // a cycle reaches nothing more through itself
        self.memo[i] = Some(Reach::default());
        let r = match self.items[i].role {
            // a draw function redraws what it names and what the draw functions it calls draw (the compound's `buildings` calls
            // `building`, `parts` calls `well`); one naming none and calling none draws its caller's kind
            Role::Draw if self.under_caller(i) => self.through_uses(i),
            Role::Draw => {
                let mut r = Reach::named(self.named(i));
                for d in self.called_in(i) {
                    let got = self.reach(d);
                    r.add(&got);
                }
                r
            }
            Role::Writer => {
                let used = !self.uses(i).is_empty();
                let r = if used {
                    self.through_uses(i)
                } else {
                    Reach::default()
                };
                if used && r.told.iter().all(|k| NOT_ELEMENTS.contains(&k.as_str())) {
                    Reach::whole()
                } else {
                    r
                }
            }
            Role::Helper | Role::Constant => self.through_uses(i),
            Role::Roll | Role::Shape => Reach::default(),
        };
        self.memo[i] = Some(r.clone());
        r
    }

    /// The draw functions `line` calls.
    fn draws_called(&self, line: &str) -> Vec<usize> {
        self.draws
            .iter()
            .filter(|(d, _, call)| line.contains(self.items[*d].bare.as_str()) && found(call, line))
            .map(|(d, _, _)| *d)
            .collect()
    }

    /// Whether draw function `d` names no kind of its own (it draws its caller's).
    fn under_caller(&self, d: usize) -> bool {
        self.named(d).is_some_and(|k| k.is_empty()) && self.called_in(d).is_empty()
    }

    /// The other draw functions item `i` calls.
    fn called_in(&self, i: usize) -> BTreeSet<usize> {
        self.items[i]
            .lines
            .iter()
            .filter(|l| !comment(l))
            .flat_map(|l| self.draws_called(l))
            .filter(|&d| d != i)
            .collect()
    }

    /// Whether item `i` is read line by line: a roll, and a draw function where the writer is told the kind before its marks.
    fn by_line(&self, i: usize) -> bool {
        let role = self.items[i].role;
        role == Role::Roll || (role == Role::Draw && matches!(self.marker, Marker::Setter))
    }

    /// What line `k` of item `i` redraws, changed. A roll's line that does not touch the writer is plumbing and redraws nothing;
    /// in a roll or a draw function read by line, a line calling a draw function redraws that function's kinds, and any other the
    /// kind it is drawn under. Any other item's line redraws what the item does.
    fn line(&mut self, i: usize, k: usize) -> Reach {
        if !self.by_line(i) {
            return self.reach(i);
        }
        let writer = re(&format!(r"\b{}\b", self.items[i].binding));
        let lines = self.items[i].lines.clone();
        let roll = self.items[i].role == Role::Roll;
        if comment(&lines[k])
            || (roll && (!found(&writer, &lines[k]) || found(&WRITER_MADE, &lines[k])))
        {
            return Reach::default();
        }
        let called: Vec<usize> = self
            .draws_called(&lines[k])
            .into_iter()
            .filter(|&d| d != i)
            .collect();
        let mut r = Reach::default();
        let mut drawn_under = called.is_empty();
        for d in called {
            if self.under_caller(d) {
                drawn_under = true;
            } else {
                let got = self.reach(d);
                r.add(&got);
            }
        }
        if drawn_under {
            let got = self.kind_above(i, &lines, &writer, k);
            r.add(&got);
        }
        r
    }

    /// The kind line `k` of item `i` is drawn under: the last its lines name at or above it, unknown past a draw function's call
    /// that names kinds of its own. Above the first a roll names it is unknown; above the first a draw function names, its
    /// caller's where it names none, else unknown (the line may feed any of its marks).
    fn kind_above(&mut self, i: usize, lines: &[String], writer: &Regex, k: usize) -> Reach {
        let all = self.marker.patterns().0;
        for (j, above) in lines[..=k].iter().enumerate().rev() {
            if comment(above) || !found(writer, above) {
                continue;
            }
            if found(all, above) {
                return Reach::named(self.marker.named(above));
            }
            if j < k
                && self
                    .draws_called(above)
                    .iter()
                    .any(|&d| d != i && !self.under_caller(d))
            {
                return Reach::whole();
            }
        }
        if self.items[i].role == Role::Draw && self.under_caller(i) {
            return self.through_uses(i);
        }
        Reach::whole()
    }
}

/// The lines of `now` that are not in `was` (`was`'s own when `added` is false): which lines a changed roll changed, comments aside.
fn changed_lines(was: &[String], now: &[String], added: bool) -> Vec<usize> {
    let mut kept = BTreeSet::new();
    for (a, b, size) in matching_blocks(was, now) {
        kept.extend(if added { b..b + size } else { a..a + size });
    }
    let side = if added { now } else { was };
    (0..side.len())
        .filter(|k| !kept.contains(k) && !comment(&side[*k]))
        .collect()
}

/// What item `i` of `world`, changed, redraws: an item read by line its changed lines (a roll's every line when the other side has
/// none), any other item - and a draw function added or deleted whole - as a whole. And whether some of the change redraws no element
/// (449 T238): a function or constant as a whole, or a changed line of an item read by line - a roll's line that hands the stages their
/// ground, a line drawn under the placeholder mark `-` - which places or plumbs, and is the feature's to declare; a type never.
fn redraws(world: &mut World, i: usize, other: Option<&[String]>, added: bool) -> (Reach, bool) {
    if !world.by_line(i) || (other.is_none() && world.items[i].role == Role::Draw) {
        let r = world.reach(i);
        // a type redraws and places nothing by itself - the code that fills or reads it does (T234's `SluiceFrame`, which only the
        // sluice's drawing fills, was read as placement and its redraw refused undeclared)
        let silent = !r.reaches() && world.items[i].role != Role::Shape;
        return (r, silent);
    }
    let own = world.items[i].lines.clone();
    let lines = match other {
        Some(o) if added => changed_lines(o, &own, true),
        Some(o) => changed_lines(&own, o, false),
        None => (0..own.len()).collect(),
    };
    let (mut r, mut silent) = (Reach::default(), false);
    for k in lines {
        let got = world.line(i, k);
        silent |= !got.reaches();
        r.add(&got);
    }
    (r, silent)
}

/// The kinds the lines `at` of `lines` name by literal - a `data-kind="..."`, or a caption's kind (`.caption("words", "kind", ...)`),
/// a placeholder (`-`) never - and, where they name one, what the draw functions those lines call redraw.
fn literal_kinds(world: &mut World, i: usize, lines: &[String], at: &[usize]) -> Reach {
    static CAPTION: LazyLock<Regex> =
        LazyLock::new(|| re(r#"\.caption\(\s*"[^"\\]*"\s*,\s*"([^"\\{]*)""#));
    let (_, attr) = Marker::Attribute.patterns();
    let mut r = Reach::default();
    for &k in at {
        for pattern in [attr, &*CAPTION] {
            r.told.extend(
                pattern
                    .captures_iter(&lines[k])
                    .map_while(Result::ok)
                    .map(|c| c[1].to_owned())
                    .filter(|k| !NOT_ELEMENTS.contains(&k.as_str())),
            );
        }
    }
    if r.told.is_empty() {
        return r;
    }
    for &k in at {
        for d in world.draws_called(&lines[k]) {
            if d != i {
                let got = world.reach(d);
                r.add(&got);
            }
        }
    }
    r
}

/// A Mode A compound mark changed on both sides (449 T289's arbiter ruling, `ask:glyph-wave-449-T289`): it owes the kinds its
/// changed lines name by literal, the added lines' first and the deleted lines' where the added name none, and `None` - read whole,
/// its whole legend where it draws a kind chosen at run time - only where they name none. Measured on T291's genkan porch: one
/// branch added to `buildings`' door loop, naming `genkan`, read whole owed 57 units (the call to `building`, a kind chosen at run
/// time, made it the whole legend), where its changed lines owe the genkan alone. A deleted line's literal is set aside where the
/// added lines name one: the kind it drew is now drawn by the added lines (here the plain door, its attributes unchanged, under the
/// porch's `{kind}`) or not by this function at all, so nothing of it is redrawn here.
fn named_by_change(now: &mut World, a: usize, was: &mut World, b: usize) -> Option<Reach> {
    if !matches!(now.marker, Marker::Attribute)
        || now.items[a].role != Role::Draw
        || was.items[b].role != Role::Draw
    {
        return None;
    }
    let (n_lines, w_lines) = (now.items[a].lines.clone(), was.items[b].lines.clone());
    let added = literal_kinds(now, a, &n_lines, &changed_lines(&w_lines, &n_lines, true));
    if !added.told.is_empty() {
        return Some(added);
    }
    let deleted = literal_kinds(was, b, &w_lines, &changed_lines(&w_lines, &n_lines, false));
    (!deleted.told.is_empty()).then_some(deleted)
}

fn tokens(item: &Item) -> Vec<u8> {
    rust_tokens(item.lines.join("\n").as_bytes())
}

/// The files of the delta (committed, staged, unstaged or untracked).
pub(super) fn delta_paths(root: &Path, base: &str) -> BTreeSet<String> {
    let diff = if base.is_empty() {
        String::new()
    } else {
        git(root, &["diff", "--name-only", base]).unwrap_or_default()
    };
    let untracked = git(root, &["ls-files", "--others", "--exclude-standard"]).unwrap_or_default();
    diff.lines()
        .chain(untracked.lines())
        .filter(|p| !p.is_empty())
        .map(str::to_owned)
        .collect()
}

/// An engine's files now (from the working tree) and at the base: `(path, text)` each.
/// Files as `(path, text)`.
type Files = Vec<(String, String)>;

fn sides(root: &Path, base: &str, e: &Engine) -> (Files, Files) {
    sides_of(root, base, e.paths, &|p| e.holds(p))
}

/// The files under `paths` that `holds`, now and at the base.
fn sides_of(
    root: &Path,
    base: &str,
    paths: &[&str],
    holds: &dyn Fn(&str) -> bool,
) -> (Files, Files) {
    let mut args = vec![
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
    ];
    args.extend(paths);
    let now: Files = git(root, &args)
        .unwrap_or_default()
        .lines()
        .filter(|p| holds(p))
        .filter_map(|p| Some((p.to_owned(), std::fs::read_to_string(root.join(p)).ok()?)))
        .collect();
    let mut args = vec!["ls-tree", "-r", "--name-only", base, "--"];
    args.extend(paths);
    let listed: Vec<String> = git(root, &args)
        .unwrap_or_default()
        .lines()
        .filter(|p| holds(p))
        .map(str::to_owned)
        .collect();
    let asked: Vec<String> = listed.iter().map(|p| format!("{base}:{p}")).collect();
    let was = listed.into_iter().zip(cat_blobs(root, &asked)).collect();
    (now, was)
}

/// What the delta's change to engine `e` reaches: each element told with the items that redraw it, the items whose elements cannot be
/// told, and the files with a change that redraws no element (`redraws`' silent part, 449 T238).
struct EngineReach {
    told: BTreeMap<String, BTreeSet<String>>,
    whole: BTreeSet<String>,
    silent: BTreeSet<String>,
}

fn engine_reach(
    e: &Engine,
    now_files: &[(String, String)],
    was_files: &[(String, String)],
    touched: &BTreeSet<String>,
) -> EngineReach {
    let (mut now, mut was) = (
        World::new(e.marker, now_files),
        World::new(e.marker, was_files),
    );
    let mut keys: BTreeSet<(String, String)> = BTreeSet::new();
    for w in [&now, &was] {
        keys.extend(
            w.items
                .iter()
                .filter(|i| touched.contains(&i.file))
                .map(|i| (i.file.clone(), i.name.clone())),
        );
    }
    let (mut told, mut whole, mut silent) = (
        BTreeMap::<String, BTreeSet<String>>::new(),
        BTreeSet::new(),
        BTreeSet::new(),
    );
    for (file, name) in keys {
        let (n, w) = (now.find(&file, &name), was.find(&file, &name));
        let (n_lines, w_lines) = (
            n.map(|i| now.items[i].lines.clone()),
            w.map(|i| was.items[i].lines.clone()),
        );
        if let (Some(a), Some(b)) = (n, w) {
            if tokens(&now.items[a]) == tokens(&was.items[b]) {
                continue;
            }
        }
        let by_change = n
            .zip(w)
            .and_then(|(at_now, at_was)| named_by_change(&mut now, at_now, &mut was, at_was));
        let read_whole = by_change.is_none();
        let mut r = by_change.unwrap_or_default();
        for (world, i, other, added) in [
            (&mut now, n, w_lines.as_deref(), true),
            (&mut was, w, n_lines.as_deref(), false),
        ] {
            if let Some(i) = i.filter(|_| read_whole) {
                let (got, quiet) = redraws(world, i, other, added);
                r.add(&got);
                if quiet {
                    silent.insert(file.clone());
                }
            }
        }
        let label = format!("{file} {name}");
        for k in r
            .told
            .iter()
            .filter(|k| !NOT_ELEMENTS.contains(&k.as_str()))
        {
            told.entry(k.clone()).or_default().insert(label.clone());
        }
        if r.whole {
            whole.insert(label);
        }
    }
    EngineReach {
        told,
        whole,
        silent,
    }
}

/// The kinds whose drawn marks on compound `d` differ between its drawing at the base and now (`marks.rs`, 449 T377), or why they
/// cannot be compared: the hamlet driver's marks are not read by kind, a drawing not current is known only by its base legend, one with
/// no drawing at the base (its blob, else the mirror's copy, as `base_legends` reads it) has nothing to compare, and a difference no kind
/// owns cannot be told.
fn compared(
    tree: &Tree,
    base: &str,
    e: &Engine,
    d: &Folder,
    current: bool,
) -> Result<BTreeSet<String>, &'static str> {
    if e.kind != Kind::Compound {
        return Err("its marks are not read by kind");
    }
    if !current {
        return Err("its drawing is not current, so only its legend at the base is known");
    }
    let path = super::rel(tree.root, &d.file(".svg"));
    let was = cat_blobs(tree.root, &[format!("{base}:{path}")])
        .pop()
        .filter(|t| !t.is_empty())
        .map(|t| universal(&t))
        .or_else(|| super::mirror_copy(tree.root, &path))
        .ok_or("its drawing at the base is not known")?;
    let now = super::read_replace(&d.file(".svg"));
    marks::differing(&marks::read(&was), &marks::read(&now))
        .ok_or("what differs in its drawing is drawn under no kind")
}

/// The glyph-checks the delta's change to an engine's drawing code owes (`before`: each standing folder's legend at the base).
pub(super) fn units(tree: &Tree, base: &str, before: &Legends) -> Vec<Unit> {
    if base.is_empty() {
        return Vec::new();
    }
    let touched = delta_paths(tree.root, base);
    let mut out: Vec<Unit> = Vec::new();
    for e in &ENGINES {
        let mine: BTreeSet<String> = touched.iter().filter(|p| e.holds(p)).cloned().collect();
        if mine.is_empty() {
            continue;
        }
        let (now, was) = sides(tree.root, base, e);
        let EngineReach { told, whole, .. } = engine_reach(e, &now, &was, &mine);
        // each map of the engine's kind with its legend: its drawing now where current, else its drawing at the base
        let maps: Vec<(&Folder, &BTreeSet<String>, bool)> = tree
            .folders
            .iter()
            .filter(|d| d.kind == e.kind && d.tree != LEGACY)
            .filter_map(|d| match tree.legends.get(&d.name) {
                Some(legend) => Some((d, legend, true)),
                None => before.get(&d.name).map(|legend| (d, legend, false)),
            })
            .collect();
        let mut push = |element: &str, on: &str, why: String| {
            let u = Unit::new("glyph-check", element, on, why);
            if !out.iter().any(|p| p.slug() == u.slug()) {
                out.push(u);
            }
        };
        for (element, by) in &told {
            if let Some((d, _, _)) = maps.iter().find(|(_, l, _)| l.contains(element)) {
                let by: Vec<&str> = by.iter().map(String::as_str).collect();
                let why = format!(
                    "{} is redrawn: {}'s drawing code changed ({})",
                    py_repr(element),
                    e.what,
                    by.join(", ")
                );
                push(element, &d.name, why);
            }
        }
        if whole.is_empty() {
            continue;
        }
        let by: Vec<&str> = whole.iter().map(String::as_str).collect();
        let changed = format!(
            "{}'s drawing code changed ({}) and the elements it redraws cannot be told from the code (a kind chosen at run time, or \
             the document every mark is written into)",
            e.what,
            by.join(", ")
        );
        let mut seen: BTreeSet<&str> = BTreeSet::new();
        for (d, legend, current) in &maps {
            let (on, differ) = (d.name.as_str(), compared(tree, base, e, d, *current));
            for element in legend
                .iter()
                .filter(|k| !NOT_ELEMENTS.contains(&k.as_str()))
            {
                if differ.as_ref().is_ok_and(|kinds| !kinds.contains(element)) {
                    continue;
                }
                if seen.insert(element.as_str()) {
                    let why = match &differ {
                        Ok(_) => format!(
                            "{changed}, and its drawn marks on {on} differ from the base's drawing (449 T377)"
                        ),
                        Err(cannot) => format!("{changed}, so the whole legend of {on} is owed: {cannot}"),
                    };
                    push(element, on, why);
                }
            }
        }
    }
    out
}

mod placed;
pub(super) use placed::placed;

#[cfg(test)]
mod tests;
