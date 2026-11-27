//! THE VIEWS' KEY HOLDS EVERY FUNCTION THEY CALL (feature 451 T434): the views cache is stamped by the hash of the files `SOURCES`
//! names, so a view computed by code outside them could stand stale after that code moved. Each file the set names is read here for
//! everything that could reach outside it - a path through `super`, `crate` or another crate, a `use` of one, a module file, a cfg but
//! the test module's, a macro std does not give, a function or closure handed in - and each such reach is a finding. A function the
//! views call that is added outside the set therefore fails `the_views_reach_nothing_outside_their_hashed_sources` until its file is
//! named in `SOURCES` (and so hashed).

use super::super::{char_end, included, literal_end, raw_start, stamp_of, word_at, View, SOURCES};

/// The macros std gives, which a hashed file may call.
const STD_MACROS: [&str; 16] = [
    "format",
    "matches",
    "vec",
    "write",
    "writeln",
    "assert",
    "assert_eq",
    "assert_ne",
    "debug_assert",
    "debug_assert_eq",
    "panic",
    "unreachable",
    "include_str",
    "include_bytes",
    "include",
    "macro_rules",
];

/// The derives std gives.
const STD_DERIVES: [&str; 9] = [
    "Clone",
    "Copy",
    "PartialEq",
    "Eq",
    "PartialOrd",
    "Ord",
    "Hash",
    "Debug",
    "Default",
];

/// The roots a path may start from without a `use`: std's crates, the prelude's types and the primitive types.
const ROOTS: [&str; 33] = [
    "std", "core", "alloc", "Self", "self", "String", "Vec", "Option", "Result", "Box", "Some",
    "None", "Ok", "Err", "Iterator", "char", "str", "bool", "u8", "u16", "u32", "u64", "u128",
    "usize", "i8", "i16", "i32", "i64", "i128", "isize", "f32", "f64", "ToString",
];

fn ident(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// The text with its comments (doc comments too) gone and every literal emptied, so only code is read.
fn code_only(text: &str) -> Vec<char> {
    let code: String = super::super::code_text(text)
        .lines()
        .filter(|l| !l.trim_start().starts_with("///") && !l.trim_start().starts_with("//!"))
        .map(|l| format!("{l}\n"))
        .collect();
    let chars: Vec<char> = code.chars().collect();
    let mut out = Vec::with_capacity(chars.len());
    let mut i = 0;
    while i < chars.len() {
        if chars[i] == '"' || raw_start(&chars, i) {
            out.extend(['"', '"']);
            i = literal_end(&chars, i);
        } else if chars[i] == '\'' && char_end(&chars, i) > i + 1 {
            out.extend(['\'', ' ', '\'']);
            i = char_end(&chars, i);
        } else {
            out.push(chars[i]);
            i += 1;
        }
    }
    out
}

/// The word that starts at `at`.
fn word(chars: &[char], at: usize) -> String {
    chars[at..].iter().take_while(|&&c| ident(c)).collect()
}

/// Does a word start at `at` (no identifier character before it)?
fn starts_word(chars: &[char], at: usize) -> bool {
    ident(chars[at]) && !at.checked_sub(1).is_some_and(|b| ident(chars[b]))
}

/// The next character after `at` that is not whitespace, and where.
fn next_at(chars: &[char], at: usize) -> Option<(usize, char)> {
    (at..chars.len())
        .find(|&i| !chars[i].is_whitespace())
        .map(|i| (i, chars[i]))
}

/// The text from the file's test module on cut away - a finding where a `cfg(test)` item is anything but that module, last.
fn cut_tests(chars: &[char], found: &mut Vec<String>) -> Vec<char> {
    let mark: Vec<char> = "#[cfg(test)]".chars().collect();
    let Some(at) = chars.windows(mark.len()).position(|w| w == mark.as_slice()) else {
        return chars.to_vec();
    };
    let after = next_at(chars, at + mark.len());
    let module = after
        .filter(|&(i, _)| word_at(chars, i, "mod"))
        .and_then(|(i, _)| {
            let (n, _) = next_at(chars, i + 3)?;
            (word(chars, n) == "tests").then(|| next_at(chars, n + 5))?
        });
    let end = match module {
        Some((i, ';')) => Some(i + 1),
        Some((i, '{')) => super::super::balanced(chars, i),
        _ => None,
    };
    if !end.is_some_and(|e| chars[e..].iter().all(|c| c.is_whitespace())) {
        found.push("a cfg(test) item that is not the file's last item, its test module".to_owned());
    }
    chars[..at].to_vec()
}

/// The names a file defines (its items' and its macros') and those its `use`s bring in, each `use` judged.
fn names(chars: &[char], sources: &[&str], found: &mut Vec<String>) -> Vec<String> {
    let mut known = Vec::new();
    for i in (0..chars.len()).filter(|&i| starts_word(chars, i)) {
        let w = word(chars, i);
        let defines = [
            "fn",
            "struct",
            "enum",
            "type",
            "trait",
            "union",
            "const",
            "static",
            "macro_rules",
        ];
        if defines.contains(&w.as_str()) {
            let skip = usize::from(w == "macro_rules");
            if let Some((n, _)) = next_at(chars, i + w.len() + skip) {
                known.push(word(chars, n));
            }
        }
        if w == "use" {
            let end = chars[i..]
                .iter()
                .position(|&c| c == ';')
                .map_or(chars.len(), |p| i + p);
            let path: String = chars[i + 3..end]
                .iter()
                .filter(|c| !c.is_whitespace())
                .collect();
            let shared = path
                .strip_prefix("l7r_shared::")
                .map(|m| word(&m.chars().collect::<Vec<_>>(), 0));
            let ok = ["std::", "core::", "alloc::"]
                .iter()
                .any(|r| path.starts_with(r))
                || shared.is_some_and(|m| {
                    sources.contains(&format!("rust/guard/shared/src/{m}.rs").as_str())
                });
            if !ok {
                found.push(format!("use {path}"));
            }
            // the names it brings in, never its first segment: a crate's name stays a root, judged where it is used
            let parts: Vec<char> = path.chars().collect();
            known.extend(
                (0..parts.len())
                    .filter(|&j| j > 0 && starts_word(&parts, j))
                    .map(|j| word(&parts, j)),
            );
        }
    }
    known
}

/// Every way the file at `path` reaches outside the files `sources` names.
fn reach(path: &str, text: &str, sources: &[&str]) -> Vec<String> {
    let mut found: Vec<String> = included(path, text)
        .into_iter()
        .filter(|p| !sources.contains(&p.as_str()))
        .map(|p| format!("compiles in {p}"))
        .collect();
    let chars = cut_tests(&code_only(text), &mut found);
    let known = names(&chars, sources, &mut found);
    // a path from the crate root (`::other::f`): a `::` after neither a name nor a type's `>`
    for i in (0..chars.len().saturating_sub(1)).filter(|&i| chars[i..i + 2] == [':', ':']) {
        let before = chars[..i].iter().rev().find(|c| !c.is_whitespace());
        if !before.is_some_and(|&c| ident(c) || c == '>') {
            found.push("a path from the crate root ::".to_owned());
        }
    }
    for i in (0..chars.len()).filter(|&i| starts_word(&chars, i)) {
        let w = word(&chars, i);
        let rest: String = chars[i + w.len()..].iter().take(2).collect();
        let next = next_at(&chars, i + w.len()).map(|(_, c)| c);
        let colons = rest == "::" && !(i >= 2 && chars[i - 2..i] == [':', ':']);
        let module = || word(&chars, i + w.len() + 2);
        let shared = w == "l7r_shared"
            && sources.contains(&format!("rust/guard/shared/src/{}.rs", module()).as_str());
        if colons && !(ROOTS.contains(&w.as_str()) || known.contains(&w) || shared) {
            found.push(format!("the path {w}::"));
        }
        if rest.starts_with('!')
            && rest != "!="
            && !STD_MACROS.contains(&w.as_str())
            && !known.contains(&w)
        {
            found.push(format!("the macro {w}!"));
        }
        if ["cfg", "cfg_attr"].contains(&w.as_str()) {
            found.push(format!("a {w} but the test module's"));
        }
        if w == "mod" || (w == "path" && i > 1 && chars[i - 2..i] == ['#', '[']) {
            found.push(format!("{w}, a file outside the set"));
        }
        if ["dyn", "Fn", "FnMut", "FnOnce"].contains(&w.as_str())
            || (w == "fn" && next == Some('('))
        {
            found.push(format!("{w}, code handed in"));
        }
        if w == "fn" {
            let n = next_at(&chars, i + 2).map_or(i, |(n, _)| n);
            if next_at(&chars, n + word(&chars, n).len()).is_some_and(|(_, c)| c == '<') {
                found.push(format!("the generic fn {}", word(&chars, n)));
            }
        }
        if w == "derive" && next == Some('(') {
            let close = chars[i..]
                .iter()
                .position(|&c| c == ')')
                .map_or(chars.len(), |p| i + p);
            let list: String = chars[i + w.len()..close].iter().collect();
            for d in list
                .split(|c: char| !ident(c))
                .filter(|d| !d.is_empty() && !STD_DERIVES.contains(d))
            {
                found.push(format!("the derive {d}"));
            }
        }
    }
    found
}

fn source_names() -> Vec<&'static str> {
    SOURCES.iter().map(|(p, _)| *p).collect()
}

#[test]
fn the_views_reach_nothing_outside_their_hashed_sources() {
    let names = source_names();
    for (path, text) in SOURCES {
        let found = reach(path, text, &names);
        assert!(found.is_empty(), "{path} reaches outside the views' hashed sources (name its file in SOURCES): {found:?}");
    }
    // the set compiles in its own file, so an edit of the views code moves the stamp
    assert!(included(SOURCES[0].0, SOURCES[0].1).contains(&SOURCES[0].0.to_owned()));
}

/// Each rule fires on a file that breaks it, and on nothing in one that keeps it.
#[test]
fn each_reach_rule_fires_on_a_file_that_breaks_it() {
    let names = ["a/code.rs", "rust/guard/shared/src/sha256.rs"];
    let at = "a/code.rs";
    let clean = "use std::fmt::Write as _;\nuse l7r_shared::sha256;\n#[derive(Clone, Debug)]\nstruct V { a: u8 }\nconst S: &str = include_str!(\"code.rs\");\nmacro_rules! m { () => {} }\nfn f(x: &str) -> String { m!(); let c = '\"'; format!(\"{x}{c}\") + &sha256::hex(b\"\") + &String::new() + &V::g() }\n#[cfg(test)]\nmod tests {\n    use super::f;\n}\n";
    assert_eq!(reach(at, clean, &names), Vec::<String>::new());
    for (bad, says) in [
        ("fn f() { super::g() }", "the path super::"),
        ("fn f() { crate::g() }", "the path crate::"),
        ("use super::g;", "use super::g"),
        ("use l7r_shared::regex;", "use l7r_shared::regex"),
        ("use fancy_regex::Regex;", "use fancy_regex::Regex"),
        (
            "fn f() { fancy_regex::Regex::new(\"\") }",
            "the path fancy_regex::",
        ),
        ("mod other;", "mod, a file outside the set"),
        (
            "#[path = \"x.rs\"]\nconst A: u8 = 1;",
            "path, a file outside the set",
        ),
        (
            "#[cfg(feature = \"x\")]\nfn f() {}",
            "a cfg but the test module's",
        ),
        ("fn f() { if cfg!(unix) {} }", "a cfg but the test module's"),
        (
            "const S: &str = include_str!(\"other.rs\");",
            "compiles in a/other.rs",
        ),
        ("fn f() { other!() }", "the macro other!"),
        ("fn f(g: &dyn Fn(u8)) {}", "dyn, code handed in"),
        ("fn f(g: impl FnOnce()) {}", "FnOnce, code handed in"),
        ("fn f(g: fn(u8) -> u8) {}", "fn, code handed in"),
        ("fn f<T>(t: T) {}", "the generic fn f"),
        (
            "use l7r_shared::sha256;\nfn f() { l7r_shared::regex::build(\"\") }",
            "the path l7r_shared::",
        ),
        (
            "fn f() { ::fancy_regex::Regex::new(\"\") }",
            "a path from the crate root ::",
        ),
        (
            "const S: &str = include_str!(concat!(\"a\", \".rs\"));",
            "the macro concat!",
        ),
        (
            "#[derive(Clone, Serialize)]\nstruct V;",
            "the derive Serialize",
        ),
        (
            "#[cfg(test)]\nmod tests {}\nfn late() {}",
            "a cfg(test) item that is not the file's last item, its test module",
        ),
        (
            "#[cfg(test)]\nfn helper() {}",
            "a cfg(test) item that is not the file's last item, its test module",
        ),
    ] {
        let found = reach(at, bad, &names);
        assert!(found.iter().any(|f| f == says), "{bad}: {found:?}");
    }
    // a word in a comment or a string is no reach, and `!=` is no macro
    assert!(reach(
        at,
        "// super::g()\nfn f(a: u8) -> bool { let s = \"crate::x other!()\"; a != 1 }",
        &names
    )
    .is_empty());
}

/// The stamp moves with each hashed file's text and with the Unicode version, and stands while they do.
#[test]
fn the_stamp_moves_with_every_hashed_source_and_the_unicode_version() {
    let one = [("a.rs", "fn a() {}"), ("b.rs", "fn b() {}")];
    let base = stamp_of(&one, (16, 0, 0));
    assert_eq!(base, stamp_of(&one, (16, 0, 0)));
    assert!(base.starts_with("l7r-rust views "));
    assert_ne!(
        base,
        stamp_of(&[("a.rs", "fn a() { }"), one[1]], (16, 0, 0))
    );
    assert_ne!(base, stamp_of(&[one[0], ("b.rs", "fn c() {}")], (16, 0, 0)));
    assert_ne!(base, stamp_of(&one, (17, 0, 0)));
    // a text moved across the boundary between two files is another set
    assert_ne!(
        base,
        stamp_of(&[("a.rs", "fn a() {}f"), ("b.rs", "n b() {}")], (16, 0, 0))
    );
    assert_eq!(
        super::super::stamp(),
        stamp_of(&SOURCES, char::UNICODE_VERSION)
    );
}

/// A view's kept line reads back as the view it was written from, its compiled-in files or none.
#[test]
fn a_kept_line_reads_back_as_its_view() {
    for text in [
        "fn f() {}\n",
        "const S: &str = include_str!(\"x.txt\");\ninclude!(\"../y.rs\");\n",
    ] {
        let view = View::of("rust/a/src/lib.rs", text);
        let line = view.line("rust/a/src/lib.rs id1");
        let (at, back) = View::parse(line.trim_end_matches('\n')).unwrap();
        assert_eq!((at.as_str(), &back), ("rust/a/src/lib.rs id1", &view));
    }
    assert_eq!(
        View::of("a/b.rs", "include!(\"../y.rs\");").includes(),
        ["y.rs"]
    );
    assert!(View::parse("no tabs").is_none());
    // a view is a function of its file's path and text alone: nothing else is handed in to build one
    let of = SOURCES[0].1.matches("fn of(").count();
    assert!(
        of == 1
            && SOURCES[0]
                .1
                .contains("pub(super) fn of(path: &str, text: &str) -> Self {")
    );
}

/// The compiled-in paths read by hand as the pattern before them read them (`\binclude(?:_str|_bytes)?!\s*\(\s*"([^"\n]+)"`).
#[test]
fn a_compiled_in_path_is_read_as_the_pattern_read_it() {
    let at = "r/s/t.rs";
    for (text, paths) in [
        ("include!(\"a.rs\")", vec!["r/s/a.rs"]),
        (
            "include_str! ( \"./b/c.txt\" ) include_bytes!(\n\"../d\")",
            vec!["r/s/b/c.txt", "r/d"],
        ),
        (
            "myinclude!(\"x\") include_strx!(\"x\") include_str!(\"\") include_str!(\"a\nb\")",
            vec![],
        ),
        (
            "include_str!(x) include_str!\"x\" include_str!(\"open",
            vec![],
        ),
        ("include", vec![]),
        (
            "include_str!(\"one\")include_str!(\"two\")",
            vec!["r/s/one", "r/s/two"],
        ),
    ] {
        assert_eq!(included(at, text), paths, "{text}");
    }
}
