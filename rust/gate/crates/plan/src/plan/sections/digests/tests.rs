//! THE DIGESTS' STAMP HOLDS EVERY FILE THEY CALL (451 T474): the digest index on disk is stamped by the hash of the files `SOURCES`
//! names, so a digest computed by code outside them could stand stale after that code moved. Each hashed file is read here for what
//! could reach outside the set - a `use` or a path through `super`, `crate`, `l7r_shared` or another crate but std and `fancy_regex`
//! (pinned by `Cargo.lock`, hashed), a path from the crate root, a module file, a cfg but the test module's, a macro neither std's
//! nor the file's, a compiled-in file outside the set - and each such reach is a finding, so a function the digests call added in
//! another file fails `the_digests_reach_nothing_outside_their_hashed_sources` until its file is named in `SOURCES`. Narrower than
//! T434's views test (`rustc/kept/code/tests/reach.rs`): no rule on code handed in, since the one way in, `of`, takes a text alone.

use super::{block_digest, digest, of, stamp, stamp_of, strip_archive, SOURCES};
use l7r_shared::regex::build;

const STD_MACROS: [&str; 12] = [
    "format",
    "matches",
    "vec",
    "write",
    "writeln",
    "panic",
    "unreachable",
    "include_str",
    "include_bytes",
    "include",
    "macro_rules",
    "concat",
];

/// The roots a path may start from without a `use`: std's crates, `fancy_regex`, the file itself, the primitive types and the lint
/// tool's attributes (`clippy::`, which compile nothing).
const ROOTS: [&str; 23] = [
    "clippy",
    "std",
    "core",
    "alloc",
    "fancy_regex",
    "self",
    "Self",
    "str",
    "char",
    "bool",
    "u8",
    "u16",
    "u32",
    "u64",
    "u128",
    "usize",
    "i8",
    "i16",
    "i32",
    "i64",
    "i128",
    "isize",
    "f64",
];

fn ident(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// The text with every comment gone and every literal emptied, so only code is read.
fn code_only(text: &str) -> String {
    let chars: Vec<char> = text.chars().collect();
    let mut out = String::new();
    let mut i = 0;
    while i < chars.len() {
        let (c, next) = (chars[i], chars.get(i + 1).copied());
        let raw = c == 'r'
            && !i
                .checked_sub(1)
                .is_some_and(|b| ident(chars[b]) && chars[b] != 'b')
            && chars[i + 1..].iter().find(|&&x| x != '#') == Some(&'"');
        if c == '/' && next == Some('/') {
            i = chars[i..]
                .iter()
                .position(|&x| x == '\n')
                .map_or(chars.len(), |p| i + p);
        } else if c == '/' && next == Some('*') {
            let mut depth = 0;
            while i < chars.len() {
                let pair = (chars[i], chars.get(i + 1).copied());
                depth += i32::from(pair == ('/', Some('*'))) - i32::from(pair == ('*', Some('/')));
                i += if matches!(pair, ('/', Some('*')) | ('*', Some('/'))) {
                    2
                } else {
                    1
                };
                if depth == 0 {
                    break;
                }
            }
        } else if raw {
            let hashes = chars[i + 1..].iter().take_while(|&&x| x == '#').count();
            let close: String = std::iter::once('"')
                .chain(std::iter::repeat_n('#', hashes))
                .collect();
            let body: String = chars[i + 2 + hashes..].iter().collect();
            i += 2
                + hashes
                + body
                    .find(&close)
                    .map_or(body.len(), |p| body[..p].chars().count() + close.len());
            out.push_str("\"\"");
        } else if c == '"' {
            i += 1;
            while i < chars.len() && chars[i] != '"' {
                i += if chars[i] == '\\' { 2 } else { 1 };
            }
            i += 1;
            out.push_str("\"\"");
        } else if c == '\'' && (next == Some('\\') || chars.get(i + 2) == Some(&'\'')) {
            let close = chars[i + 2..]
                .iter()
                .position(|&x| x == '\'')
                .map_or(chars.len(), |p| i + 2 + p);
            i = close + 1;
            out.push_str("' '");
        } else {
            out.push(c);
            i += 1;
        }
    }
    out
}

/// Is `body` (what follows `mod tests`) one item to the text's end: `;`, or a block whose brace closes last?
fn last_item(body: &str) -> bool {
    if body.trim_end() == ";" {
        return true;
    }
    let mut depth = 0;
    for (i, c) in body.char_indices() {
        depth += i32::from(c == '{') - i32::from(c == '}');
        if depth == 0 {
            return c == '}' && body[i + 1..].trim().is_empty();
        }
    }
    false
}

/// Every way the file at `path` reaches outside the files `sources` names.
fn reach(path: &str, text: &str, sources: &[&str]) -> Vec<String> {
    let mut found = Vec::new();
    let dir: Vec<&str> = path.split('/').collect();
    let include = build(r#"\binclude(?:_str|_bytes)?!\s*\(\s*"([^"\n]+)""#).unwrap();
    for name in include
        .captures_iter(text)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1))
    {
        let mut at: Vec<&str> = dir[..dir.len() - 1].to_vec();
        for part in name.as_str().split('/') {
            match part {
                ".." => drop(at.pop()),
                p => at.push(p),
            }
        }
        let at = at.join("/");
        if !sources.contains(&at.as_str()) {
            found.push(format!("compiles in {at}"));
        }
    }
    let mut code = code_only(text);
    if let Some(at) = code.rfind("#[cfg(test)]") {
        let rest = code[at + "#[cfg(test)]".len()..].trim_start();
        if let Some(body) = rest.strip_prefix("mod tests") {
            if !last_item(body.trim_start()) {
                found.push("a test module that is not the file's last item".to_owned());
            }
            code.truncate(at);
        }
    }
    // a shared module is in the set where its file is; `crate` is `l7r_shared` in a shared file
    let shared = path.starts_with("rust/guard/shared/src/");
    let in_set = |root: &str, module: &str| {
        (root == "l7r_shared" || (root == "crate" && shared))
            && sources.contains(&format!("rust/guard/shared/src/{module}.rs").as_str())
    };
    let words = build(r"\b([A-Za-z_][A-Za-z0-9_]*)\b").unwrap();
    let all: Vec<(usize, String)> = words
        .captures_iter(&code)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1).map(|m| (m.start(), m.as_str().to_owned())))
        .collect();
    let mut known: Vec<String> = Vec::new();
    for (at, w) in &all {
        let after = &code[at + w.len()..];
        let before = code[..*at].trim_end();
        let statement = before.is_empty()
            || before.ends_with([';', '{', '}', ']', ')'])
            || before.ends_with("pub");
        if w == "use" && statement {
            let path: String = after[..after.find(';').unwrap_or(after.len())]
                .chars()
                .filter(|c| !c.is_whitespace())
                .collect();
            let mut parts = path.split("::");
            let (root, module) = (parts.next().unwrap_or(""), parts.next().unwrap_or(""));
            if !(["std", "core", "alloc", "fancy_regex"].contains(&root) || in_set(root, module)) {
                found.push(format!("use {path}"));
            }
            known.extend(path.split(|c: char| !ident(c)).skip(1).map(str::to_owned));
        }
        if w == "macro_rules" {
            known.extend(
                after
                    .trim_start_matches('!')
                    .split(|c: char| !ident(c))
                    .find(|s| !s.is_empty())
                    .map(str::to_owned),
            );
        }
    }
    for (at, w) in &all {
        let after = &code[at + w.len()..];
        let before = code[..*at].trim_end();
        if after.starts_with("::") && !before.ends_with("::") {
            let module: String = after[2..].chars().take_while(|&c| ident(c)).collect();
            let typed = w.starts_with(|c: char| c.is_uppercase());
            if !(ROOTS.contains(&w.as_str()) || typed || known.contains(w) || in_set(w, &module)) {
                found.push(format!("the path {w}::"));
            }
        }
        if after.starts_with('!')
            && !after.starts_with("!=")
            && !STD_MACROS.contains(&w.as_str())
            && !known.contains(w)
        {
            found.push(format!("the macro {w}!"));
        }
        // a cfg(test) item is compiled in the file's own crate's tests alone, never in the binary that writes an index
        if (w == "cfg" && !after.starts_with("(test)")) || w == "cfg_attr" {
            found.push(format!("a {w} but the test module's"));
        }
        if w == "mod" || (w == "path" && before.ends_with("#[")) {
            found.push(format!("{w}, a file outside the set"));
        }
    }
    let rooted = build(r"(?:^|[^A-Za-z0-9_>\s])\s*::").unwrap();
    if rooted.is_match(&code).unwrap_or(false) {
        found.push("a path from the crate root ::".to_owned());
    }
    found
}

#[test]
fn the_digests_reach_nothing_outside_their_hashed_sources() {
    let names: Vec<&str> = SOURCES.iter().map(|(p, _)| *p).collect();
    for (path, text) in SOURCES.iter().filter(|(p, _)| {
        std::path::Path::new(p)
            .extension()
            .is_some_and(|e| e == "rs")
    }) {
        let found = reach(path, text, &names);
        assert!(found.is_empty(), "{path} reaches outside the digests' hashed sources (name its file in SOURCES): {found:?}");
    }
    // the set compiles in its own file, so an edit of the digest code moves the stamp; and a text is the one thing handed in
    assert_eq!(
        SOURCES[0].0,
        "rust/gate/crates/plan/src/plan/sections/digests.rs"
    );
    assert_eq!(
        SOURCES[0]
            .1
            .matches("pub(crate) fn of(plan: &str) -> Digested {")
            .count(),
        1
    );
    assert!(SOURCES
        .iter()
        .any(|(p, t)| *p == "rust/Cargo.lock" && t.contains("name = \"fancy-regex\"")));
}

/// Each rule fires on a file that breaks it, and on nothing in one that keeps it.
#[test]
fn each_reach_rule_fires_on_a_file_that_breaks_it() {
    let names = ["a/d.rs", "rust/guard/shared/src/sha256.rs"];
    let clean = "use std::sync::LazyLock;\nuse fancy_regex::Regex;\nuse l7r_shared::sha256;\nmacro_rules! m { () => {} }\nconst S: &str = include_str!(\"d.rs\");\nfn f(x: &str) -> String { m!(); let c = '\"'; let r = r#\"crate::x\"#; let b = br\"super::y\"; /* super::z */ format!(\"{x}{c}{r}{b:?}\") + &sha256::hex(b\"\") + &String::new() + &str::repeat(\"\", 1) + &Self::g() + &std::env::args().count().to_string() }\nfn g(a: u8) -> bool { a != 1 && '\\'' != ' ' }\n#[cfg(test)]\nmod tests {\n    use super::f;\n}\n";
    assert_eq!(reach("a/d.rs", clean, &names), Vec::<String>::new());
    // a cfg(test) item that is no test module is no finding of the last-item rule
    assert!(reach("a/d.rs", "#[cfg(test)]\nfn t() {}\n", &names).is_empty());
    let shared_ok = "fn f() { crate::sha256::hex(b\"\") }";
    assert!(reach("rust/guard/shared/src/x.rs", shared_ok, &names).is_empty());
    for (bad, says) in [
        ("fn f() { super::g() }", "the path super::"),
        ("fn f() { crate::g() }", "the path crate::"),
        ("use super::g;", "use super::g"),
        ("use crate::regex::build;", "use crate::regex::build"),
        ("use l7r_shared::regex;", "use l7r_shared::regex"),
        ("use serde_json::Value;", "use serde_json::Value"),
        (
            "fn f() { serde_json::to_string(\"\") }",
            "the path serde_json::",
        ),
        (
            "fn f() { l7r_shared::regex::build(\"\") }",
            "the path l7r_shared::",
        ),
        (
            "fn f() { ::fancy_regex::escape(\"\") }",
            "a path from the crate root ::",
        ),
        ("mod other;", "mod, a file outside the set"),
        (
            "#[path = \"x.rs\"]\nconst A: u8 = 1;",
            "path, a file outside the set",
        ),
        ("#[cfg(unix)]\nfn f() {}", "a cfg but the test module's"),
        (
            "const S: &str = include_str!(\"../other.rs\");",
            "compiles in other.rs",
        ),
        ("fn f() { other!() }", "the macro other!"),
        (
            "#[cfg(test)]\nmod tests {}\nfn late() {}",
            "a test module that is not the file's last item",
        ),
        (
            "#[cfg(test)]\nmod tests",
            "a test module that is not the file's last item",
        ),
        (
            "#[cfg(test)]\nmod tests { fn a() {}",
            "a test module that is not the file's last item",
        ),
        (
            "#[cfg_attr(test, allow(x))]\nfn f() {}",
            "a cfg_attr but the test module's",
        ),
    ] {
        let found = reach("a/d.rs", bad, &names);
        assert!(found.iter().any(|f| f == says), "{bad}: {found:?}");
    }
}

/// The stamp moves with each hashed file's text and with the Unicode version, and stands while they do.
#[test]
fn the_stamp_moves_with_every_hashed_source_and_the_unicode_version() {
    let one = [("a.rs", "fn a() {}"), ("b.rs", "fn b() {}")];
    let base = stamp_of(&one, (16, 0, 0));
    assert_eq!((base.clone(), base.len()), (stamp_of(&one, (16, 0, 0)), 64));
    assert_ne!(
        base,
        stamp_of(&[("a.rs", "fn a() { }"), one[1]], (16, 0, 0))
    );
    assert_ne!(base, stamp_of(&[one[0], ("b.rs", "fn c() {}")], (16, 0, 0)));
    assert_ne!(base, stamp_of(&one, (17, 0, 0)));
    assert_ne!(
        base,
        stamp_of(&[("a.rs", "fn a() {}f"), ("b.rs", "n b() {}")], (16, 0, 0))
    );
    assert_eq!(stamp(), stamp_of(&SOURCES, char::UNICODE_VERSION));
}

/// A plan's digests: each block's with its archive lines out, each task section's whole.
#[test]
fn a_plan_s_digests_are_its_blocks_and_its_sections() {
    let plan = "## A\n\none\n<!-- plan-archive: plan-done.md -->\n\n### T01 x\n\ntwo\n";
    let (blocks, sections) = of(plan);
    let a = &blocks.iter().find(|(k, _, _)| k == "## A").unwrap();
    assert_eq!(
        (a.1.clone(), strip_archive(&a.2)),
        (digest(b"## A\n\none\n\n"), "## A\n\none\n\n".to_owned())
    );
    assert_eq!(block_digest(&a.2), a.1);
    assert_eq!(
        sections,
        vec![(
            "T01".to_owned(),
            digest(b"### T01 x\n\ntwo\n"),
            "### T01 x\n\ntwo\n".to_owned()
        )]
    );
}
