//! 451 T96: the Python literal reader, moved from make-only's `interp`, by its own tests (make-only's, readme's and gate-write's suites
//! still judge it through their guards).

use std::path::Path;
use std::process::Command;

use super::{all_program_names, program_names, without_text};

/// The variable naming the program a child run reads (`tree/tests/builds.rs`' form, 451 T97).
const CHILD: &str = "L7R_PROGRAM_BUILDS_OF";

/// Each program and the reader's patterns it builds, read as the event log reads it - every name, in the crate's directory, each an
/// existing file: none for a program whose literals name no file or name one only assigned (its literals read by plain code), a `/`
/// or a `join(` beside quotes that join no two literals among them; else only the patterns its uses reach - `open(`'s two, `Path(`'s
/// two, a joined pair's (triple-quoted text read by shape's scan, which builds none, 451 T112).
const BUILDS: [(&str, usize); 9] = [
    ("print(1)", 0),
    ("import json\nprint(json.dumps({'k': 1}))", 0),
    (
        "print('/'.join(x).split('/'), a + '/' + b, p.join(\"read.sh\"))",
        0,
    ),
    ("p='nofile.rs'; s=open(p).read()\nopen(p,'w').write(s)", 0),
    (
        "p='Cargo.toml'; s=open(p).read()\nopen(p,'w').write(s.replace('a', 'b'))",
        0,
    ),
    ("open('Cargo.toml', 'w').write(s)", 2),
    ("Path('Cargo.toml').write_text(s)", 2),
    ("(Path('src') / 'lib.rs').write_text(s)", 1),
    ("s = \"\"\"x\"\"\"\nopen('Cargo.toml', 'w').write(s)", 2),
];

/// A hook event is a process of its own and a pattern is built on its first use in it, so a program builds only the patterns its own
/// text reaches (451 T96: every program built three, and a literal naming a file the scans' eight and a pattern of its own each call;
/// the literals themselves are read by plain code, `literals`).
#[test]
fn a_program_builds_only_the_patterns_it_reaches() {
    let dir = env!("CARGO_MANIFEST_DIR");
    if let Some(body) = std::env::var_os(CHILD) {
        let names = all_program_names(&body.to_string_lossy(), Some(dir), true, true, &|p| {
            Path::new(p).is_file()
        });
        let built = crate::regex::BUILT.lock().unwrap().clone();
        println!("T96 built {}", serde_json::to_string(&built).unwrap());
        println!("T96 names {}", serde_json::to_string(&names).unwrap());
        return;
    }
    for (body, want) in BUILDS {
        let out = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "tree::program::tests::a_program_builds_only_the_patterns_it_reaches",
                "--nocapture",
            ])
            .env(CHILD, body)
            .output()
            .unwrap();
        let said = String::from_utf8_lossy(&out.stdout);
        let read = |key: &str| -> Vec<String> {
            let line = said.lines().find_map(|l| l.strip_prefix(key));
            assert!(line.is_some(), "{body}: the child said {said}");
            serde_json::from_str(line.unwrap_or_default()).unwrap()
        };
        let built = read("T96 built ");
        assert_eq!(built.len(), want, "{body} built {built:#?}");
        // what it names is what the reader names in this process
        let names = all_program_names(body, Some(dir), true, true, &|p| Path::new(p).is_file());
        assert_eq!(read("T96 names "), names, "{body}");
    }
}

fn rs(p: &str) -> bool {
    matches!(
        Path::new(p).extension().and_then(|e| e.to_str()),
        Some("rs" | "json" | "py" | "html")
    )
}

/// Every name once, in order - each single literal, then each joined pair - and the first alone.
#[test]
fn every_name_once_in_order_and_the_first() {
    let body =
        "p='a.rs'; open(p,'w')\nopen('a.rs', 'a')\nq = 'b.rs'\nos.path.join('dev', 'x.json')";
    assert_eq!(
        all_program_names(body, Some("/w"), true, false, &rs),
        ["/w/a.rs", "/w/b.rs", "/w/x.json", "/w/dev/x.json"]
    );
    assert_eq!(
        program_names(body, Some("/w"), true, false, &rs).as_deref(),
        Some("/w/a.rs")
    );
    // a hit the joined pairs alone give
    let joined = "(Path('dev') / 'y.json').write_text(s)";
    assert_eq!(
        program_names(joined, Some("/w"), true, true, &|p| p
            .ends_with("dev/y.json"))
        .as_deref(),
        Some("/w/dev/y.json")
    );
    assert_eq!(program_names("print(1)", Some("/w"), true, true, &rs), None);
}

/// A literal every use of which is a read names nothing with `reads`; every one of them does without.
#[test]
fn a_literal_only_read_names_nothing() {
    let body = "open('r1.rs')\nopen('r2.rs', 'r')\nPath('r3.rs').read_text()\nrun(['x', 'r4.rs'])\nd = {'file_path': 'r5.rs'}\n\
                spec_from_file_location('m', 'r6.rs')\nopen('w.rs', 'w')";
    assert_eq!(
        all_program_names(body, Some("/w"), true, true, &rs),
        ["/w/w.rs"]
    );
    assert_eq!(
        all_program_names(body, Some("/w"), false, false, &rs).len(),
        7
    );
    // past the windows' 200 and 300 characters of context, each read from its own start
    let long = format!("{}open('r.rs')\nopen('w2.rs', 'w')", "x = 1\n".repeat(60));
    assert_eq!(
        all_program_names(&long, Some("/w"), true, true, &rs),
        ["/w/w2.rs"]
    );
}

/// `placed` takes a literal that is a path where the shell stands: not an f-string's placeholder, not a tail on a computed base or a
/// string method's text; a shell variable's text is never one; an absolute literal is itself, a relative one with no directory under
/// `/`; triple-quoted text names nothing.
#[test]
fn placed_takes_a_literal_that_is_a_path_where_the_shell_stands() {
    let body = "open('{C}/x.py', 'w')\nopen(R + '/y.html', 'w')\ns.replace('z.rs', 'q')\nopen('$HOME/v.rs', 'w')";
    assert!(all_program_names(body, Some("/w"), true, true, &rs).is_empty());
    assert_eq!(
        all_program_names(body, Some("/w"), true, false, &rs),
        ["/w/{C}/x.py", "/y.html", "/w/z.rs"]
    );
    assert_eq!(
        all_program_names(
            "open('/abs/f.rs', 'w'); open('g.rs', 'w')",
            None,
            true,
            true,
            &rs
        ),
        // Python's `normpath` keeps two leading slashes, as make-only always resolved a relative literal with no directory
        ["/abs/f.rs", "//g.rs"]
    );
    assert!(all_program_names(
        "x = \"\"\"open('t.rs', 'w')\"\"\"",
        Some("/w"),
        true,
        false,
        &rs
    )
    .is_empty());
    // a joined pair whose second part is absolute is no path under the first
    assert_eq!(
        all_program_names("(Path('a') / '/b.rs').touch()", Some("/w"), true, true, &rs),
        Vec::<String>::new()
    );
}

/// Programs holding each shape the reader's patterns read, and their near misses, with Unicode whitespace where `\s` stands.
const SHAPES: [&str; 10] = [
    "x.split('/'); '/'.join(p); a + '/' + b; p.join(\"read.sh\"); join('a'); join( 'a'\u{3000}, 'b'); 'a'/\"b\"; '' / 'b'; 'a' / ''; 'a b' / 'c'; join('a' 'b',",
    "x = os.path.join('dev', 'x.json')\n(Path('a') / 'b.rs').touch(); y = d / 'c.rs'; z = R + '/y.html'\njoin(  \"a\" ,'b') ; '\\n'.join(l)",
    "f == 'SOURCES.html' or f != \"x\"\nPath(RESEARCH_DIR, 'S.html'); os.path.join(base,\n  'k.rs')\nPath(a, b)('c'); g = 'd' ) \t/\n 'e'",
    "re.findall(r'summary.only', s); f.endswith('.html'); s.replace('a', 'b'); s.rstrip(u'x'); x.rsplit(b'y'); re.sub_2(\"z\"",
    "open('r1.rs')\nopen( 'r2.rs' , mode = 'rb' )\nPath('r3.rs') . read_bytes()\nsubprocess.run(['x', 'r4.rs'])\nPopen(\n  ['y', 'r5.rs'])",
    "d = {'file_path': 'r5.rs'}\nspec_from_file_location('m', 'r6.rs')\nopen('w.rs', 'w')\nshutil.copy('a.rs', 'b.rs'); os.remove('c.rs')",
    "x = \"\"\"open('t.rs', 'w')\"\"\"\ny = '''z \\''' q'''\nrun([a[0], 'v.rs']) ; check_output( [\n'w.rs'])",
    "open(\u{3000}'a.rs'\u{a0})\nPath(\u{2028}'b.rs'\u{85}).read_text()\nd[\"k-1\"]:\u{2003}'c.rs'\ns.strip(\u{a0}'d') + \u{3000}'e.rs'",
    "p='Cargo.toml'; s=open(p).read()\nopen(p,'w').write(s.replace('a', 'b'))\nPath('x.rs').write_text(s)",
    "json.dump(x, open('o.json', 'w')); f.write(\"q\"); os.open('z'); a.re.x('y'); re .y('z'); re.x y('w'); g(h), i('j')",
];

/// Each gate is a necessary condition: wherever its pattern matches - on every prefix and every suffix of `SHAPES`, the windows the
/// scans ask of them - the gated pattern matches too, and it answers alike where its pattern does not.
#[test]
fn each_gate_passes_wherever_its_pattern_matches() {
    use super::{
        ARGV_BEFORE, JOINED, OPEN_AFTER, OPEN_BEFORE, PATH_AFTER, PATH_BEFORE, SPEC_BEFORE,
        TAIL_BEFORE, VALUE_BEFORE,
    };
    let gated = [
        (&JOINED, "join('a',"),
        (&OPEN_BEFORE, "open("),
        (&OPEN_AFTER, ")"),
        (&PATH_BEFORE, "Path("),
        (&PATH_AFTER, ")"),
        (&ARGV_BEFORE, "["),
        (&VALUE_BEFORE, ":"),
        (&SPEC_BEFORE, "spec_from_file_location(,"),
        (&TAIL_BEFORE, "/"),
    ];
    let mut matched = vec![0_usize; gated.len()];
    for body in SHAPES {
        let cuts = body.char_indices().map(|(i, _)| i).chain([body.len()]);
        for text in cuts.flat_map(|i| [&body[..i], &body[i..]]) {
            for (n, (lazy, witness)) in gated.iter().enumerate() {
                let raw = lazy.on(witness).unwrap().is_match(text).unwrap();
                assert_eq!(lazy.is_match(text), raw, "pattern {n} on {text:?}");
                matched[n] += usize::from(raw);
            }
        }
    }
    // every pattern matched somewhere, so each gate was asked where it must pass
    assert!(matched.iter().all(|&m| m > 0), "{matched:?}");
}

/// The plain read of a program's literals answers as the pattern it replaced (`(['"])([^'"\s\\]+)\1`, built here): each `SHAPES`
/// program and each of its suffixes, the quotes' and backslashes' near misses, and every character to U+3100 (every `White_Space` one
/// among them), U+180E, U+200B and U+FEFF inside a literal, alone and beside a word.
#[test]
fn the_literals_are_what_the_literal_pattern_found() {
    let pattern = crate::regex::build(r#"(['"])([^'"\s\\]+)\1"#).unwrap();
    let found = |body: &str| -> Vec<(usize, String)> {
        pattern
            .captures_iter(body)
            .map_while(Result::ok)
            .filter_map(|c| c.get(2).map(|m| (m.start(), m.as_str().to_owned())))
            .collect()
    };
    let read = |body: &str| -> Vec<(usize, String)> {
        super::literals(body)
            .map(|(at, lit)| (at, lit.to_owned()))
            .collect()
    };
    let near = [
        "", "'", "\"", "''", "''a'", "'a''b'", "'a\"b'", "\"a'b\"", "'a\\'b'", "'a b'", "'''x'''",
        "'a'b'c'", "x'é'y", "'a\n'b'",
    ];
    for body in SHAPES
        .iter()
        .flat_map(|b| b.char_indices().map(|(i, _)| &b[i..]))
        .chain(near)
    {
        assert_eq!(read(body), found(body), "{body:?}");
    }
    let chars = (0..=0x3100_u32)
        .chain([0x180E, 0x200B, 0xFEFF])
        .filter_map(char::from_u32);
    for c in chars {
        for body in [
            format!("'{c}'"),
            format!("x\"a{c}b\"'{c}"),
            format!("'{c}\"z'"),
        ] {
            assert_eq!(read(&body), found(&body), "U+{:04X}", u32::from(c));
        }
    }
}

/// The variable that makes a child run read the program (451 T112).
const TRIPLE_CHILD: &str = "L7R_PROGRAM_TRIPLE_IN_TIME";

/// A program writing a file, then a triple quote nothing later closes and forty escapes: 2^40 tries for `TRIPLE`'s backtracking
/// search, which held make-only, readme, gate-write (while a `make done` ran) and the event log's end past 10 s on the program run
/// from a heredoc (measured 2026-11-21, the T112 plan section). A lone quote after the escapes closes the single-quoted reading.
fn unclosed_triple() -> String {
    format!(
        "open('f.txt', 'w').write('x')\ns = '''it {} '",
        "\\n".repeat(40)
    )
}

#[test]
fn a_triple_quote_nothing_closes_is_read_in_time() {
    if std::env::var_os(TRIPLE_CHILD).is_some() {
        let names = all_program_names(&unclosed_triple(), Some("/w"), true, false, &|_| true);
        println!("T112 named {names:?}");
        return;
    }
    let name = "tree::program::tests::a_triple_quote_nothing_closes_is_read_in_time";
    let (passed, said) = crate::tree::tests::answers_in_time(name, TRIPLE_CHILD, 10);
    assert!(passed, "the program was not read in 10 s: {said}");
    let named = said.contains(r#"T112 named ["/w/f.txt""#);
    assert!(named, "{said}");
}

/// The program's triple-quoted text blanked as `TRIPLE` (`(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''`, built here) blanked
/// it, on every text of up to 5 pieces over a triple of each quote, each quote alone, a backslash, a letter, a newline and a
/// character of two bytes, and on the empty text.
#[test]
fn triple_quoted_text_is_blanked_as_the_pattern_blanked_it() {
    let pattern = r#"(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''"#;
    let pattern = crate::regex::build(pattern).unwrap();
    let pieces = ["\"\"\"", "'''", "\"", "'", "\\", "a", "\n", "é"];
    let mut texts = vec![String::new()];
    let mut longest = vec![String::new()];
    for _ in 0..5 {
        longest = longest
            .iter()
            .flat_map(|t| pieces.map(|p| format!("{t}{p}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let (scan, old) = (
            without_text(text),
            pattern.replace_all(text, "\"\"").into_owned(),
        );
        assert_eq!(scan, old, "{text:?}");
    }
}
