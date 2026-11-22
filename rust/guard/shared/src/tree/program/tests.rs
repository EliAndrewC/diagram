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
/// two, a joined pair's (triple-quoted text read by shape's scan, which builds none, 451 T112); none for a program that defines a
/// function, or names `def` in a string, its calls' literals bound by plain code (451 T110).
const BUILDS: [(&str, usize); 12] = [
    ("print(1)", 0),
    ("print('def f(p):')", 0),
    (
        "root='src/'\ndef sub(p): open(root+p,'w').write('x')\nsub('lib.rs')",
        0,
    ),
    ("root='src/'\nopen(root+'lib.rs','w').write('x')", 0),
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

/// T92's builder's command, whole (2026-11-21 20:34Z, its transcript's tool call `toolu_01MiKPTqkMFMHohRjnX9tfYu`): a heredoc's program
/// whose `sub` writes `root+path`, `root` the module's literal (451 T110).
const T92: &str = r###"printf '\nmod accept;\n' >> rust/gate/crates/plan/src/plan/record/tests.rs && python3 - <<'EOF'
import re
root='/diagram/.clones/diagram-backlog/rust/gate/crates/'
def sub(path, old, new, count=1):
    p=root+path; s=open(p).read()
    assert s.count(old)>=1, (path, old)
    s=s.replace(old,new,count); open(p,'w').write(s)
# step 1: the type only, HEAD's behavior kept
sub('plan/src/plan/record.rs', """/// Past the plan-round cap (feature 385 T16)""", """/// What an accept recorded (feature 451 T92): the blocks recorded CLEAR, the tasks whose verdict it now is, and whether its question was
/// the whole plan.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Accepted {
    pub blocks: Vec<String>,
    pub tasks: Vec<String>,
    pub whole: bool,
}

/// Past the plan-round cap (feature 385 T16)""")
sub('plan/src/plan/record.rs', """    when: Option<&str>,
) -> Result<Vec<String>, Stop> {
    let lines = std::fs::read_to_string(spec_dir.join("arbiter.jsonl"))""", """    when: Option<&str>,
) -> Result<Accepted, Stop> {
    let lines = std::fs::read_to_string(spec_dir.join("arbiter.jsonl"))""")
sub('plan/src/plan/record.rs', """    let _ = std::fs::write(spec_dir.join(RECORD), pretty(&out));
    Ok(sorted)
}""", """    let _ = std::fs::write(spec_dir.join(RECORD), pretty(&out));
    Ok(Accepted {
        blocks: sorted,
        tasks: Vec::new(),
        whole: true,
    })
}""")
sub('plan/src/plan.rs', """                Ok(named) => said(format!("arbiter-accept: {} block(s) of {}'s plan recorded CLEAR on {}\\n", named.len(),""", """                Ok(named) => said(format!("arbiter-accept: {} block(s) of {}'s plan recorded CLEAR on {}\\n", named.blocks.len(),""")
sub('plan/src/plan.rs', """pub fn arbiter_accept_listed(dir: &Path, trigger: &str) -> Vec<String> {""", """pub fn arbiter_accept_listed(dir: &Path, trigger: &str) -> Accepted {""")
sub('plan/src/plan.rs', """mod record;\n""", """mod record;\npub use record::Accepted;\n""")
sub('plan/src/plan/record/tests.rs', """    assert_eq!(named, ["## A", "preamble"]);""", """    assert_eq!(named.blocks, ["## A", "preamble"]);""")
sub('plan/src/plan/record/tests.rs', """    assert_eq!(arbiter_accept(&dir, asked, None).unwrap(), ["preamble"]);""", """    assert_eq!(arbiter_accept(&dir, asked, None).unwrap().blocks, ["preamble"]);""")
sub('plan/src/plan/tests.rs', """    assert!(super::arbiter_accept_listed(&root, "t").is_empty());""", """    assert!(super::arbiter_accept_listed(&root, "t").blocks.is_empty());""")
sub('arbiter/src/arbiter.rs', """                named.len()
            );""", """                named.blocks.len()
            );""")
EOF
git -C /diagram/.clones/diagram-backlog diff --stat -- rust/gate/crates/plan rust/gate/crates/arbiter"###;

/// 451 T110, red first on T92's own command, read as the event log reads it (the walk's program, resolved where it runs): each
/// `sub(..)` call's path is placed on the module's `root`, where it was placed where the shell stood, naming no file of the three it
/// wrote; make-only's reading, fail-closed, names both.
#[test]
fn a_parameter_written_onto_a_module_root_is_placed_there() {
    let clone = "/diagram/.clones/diagram-backlog";
    let walk = crate::tree::walk_judged(T92, Some(clone), "", "/home/x");
    let found = walk
        .targets
        .iter()
        .find_map(|t| t.program.clone().zip(t.path.clone()));
    let (program, dir) = found.unwrap_or_default();
    let got = all_program_names(&program, Some(&dir), true, true, &rs);
    let files = [
        "plan/record.rs",
        "plan.rs",
        "plan/record/tests.rs",
        "plan/tests.rs",
    ];
    let mut want: Vec<String> = files
        .iter()
        .map(|f| format!("{clone}/rust/gate/crates/plan/src/{f}"))
        .collect();
    want.push(format!("{clone}/rust/gate/crates/arbiter/src/arbiter.rs"));
    assert_eq!(got, want);
    let closed = all_program_names(&program, Some(&dir), true, false, &rs);
    let here = format!("{clone}/plan/src/plan.rs");
    let both = closed.contains(&here) && closed.ends_with(&want);
    assert!(both, "{closed:?}");
}

/// 451 T110: each form of a root, a join and a write the binding reads, placed, and each shape it leaves to the literal's own reading
/// (in `/w`, `placed`): a root the program computes or binds twice, a function defined twice, a star, a parameter handed on or rebound,
/// a read, another sink, a shadowed root, an f-string's expression, mixed or floor joins, a method's call, a call of another function;
/// and a write joining a root and literals alone, with no function, placed as well (its literal a tail the plain reading drops).
const BINDS: [(&str, &[&str]); 46] = [
    ("root='src/'\ndef edit(p, old, new): s=open(root+p).read(); open(root+p,'w').write(s)\nedit('a.rs', 'x', 'y')", &["/w/src/a.rs"]),
    ("root = '/r/'  # the crates\ndef sub(path, old, count=1):\n    p=root+path; s=open(p).read()\n\n    open(p, 'w').write(s)\nsub('b.rs', '')\nsub(path='c.rs', old='')\nx = 1", &["/r/b.rs", "/r/c.rs"]),
    ("R = Path('l7r/')\ndef f(path):\n    p = R / path\n    p.write_text('x')\nf('x/b.py')\nf('/abs/d.py')", &["/w/l7r/x/b.py", "/abs/d.py"]),
    ("R = pathlib.Path('/k')\ndef f(rel, *, mode):\n    open(os.path.join(R, rel), mode='a').write('x')\nf('e.json', mode=1)", &["/k/e.json"]),
    ("R = \"/r\"\ndef edit(rel, old):\n    p=f\"{R}/{rel}\"; s=open(p).read()\n    open(p,'w').write(s)\nedit('v.html', 'o')", &["/r/v.html"]),
    ("R = '/q'\ndef f(p, s):\n    Path(R, p).write_text(s)\n    (Path(R) / 'sub' / p).write_bytes(s)\n    return (R + '/' + p).write_text(s)\nf('g.rs', '')", &["/q/g.rs", "/q/sub/g.rs"]),
    ("root='t/'\ndef f(p):\n    p = root + p\n    open(p, 'x')\nf('h.rs')", &["/w/t/h.rs"]),
    ("def f(p, /, q): open('src/' + p, 'w'); open(f'{p}', 'w')\nf('i.rs', 1)", &["/w/src/i.rs"]),
    ("R = '/q'\ndef f(p): (R / Path(p)).write_text(s)\nf('j.rs')", &["/q/j.rs"]),
    ("r = pathlib.Path(sys.argv[1])\ndef sub(rel):\n    p = r/rel; p.write_text('x')\nsub('k1.rs')", &["/w/k1.rs"]),
    ("root='a/'\nroot='b/'\ndef f(p): open(root+p,'w')\nf('k2.rs')", &["/w/k2.rs"]),
    ("root='a/'\nfor root in xs: pass\ndef f(p): open(root+p,'w')\nf('k3.rs')", &["/w/k3.rs"]),
    ("x = 1; root = 'a/'\nR = 'a' + 'b'\nQ = Path('a', 'b')\ndef f(p): open(root+p,'w'); open(R+p,'w'); open(Q/p,'w')\nf('k4.rs')", &["/w/k4.rs"]),
    ("root='a/'\ndef f(p): open(root+p,'w')\ndef f(p): pass\nf('k5.rs')", &["/w/k5.rs"]),
    ("root='a/'\ndef f(*ps): open(root+ps,'w')\nf('k6.rs')", &["/w/k6.rs"]),
    ("root='a/'\ndef f(p): open(root+p,'w')\nf(*xs, 'k7.rs')", &["/w/k7.rs"]),
    ("root='a/'\ndef f(*, p): open(root+p,'w')\nf('k8.rs')", &["/w/k8.rs"]),
    ("root='a/'\ndef f(p): g(root + p)\nf('k9.rs')", &["/w/k9.rs"]),
    ("root='a/'\ndef f(p):\n    p = p.strip()\n    open(root+p,'w')\nf('l1.rs')", &["/w/l1.rs"]),
    ("root='a/'\ndef f(p):\n    q = root + p\n    q = q + 'x'\n    open(q,'w')\nf('l2.rs')", &["/w/l2.rs"]),
    ("root='a/'\ndef f(p): return open(root+p).read() + open(root+p, 'r').read()\nf('l3.rs')", &["/w/l3.rs"]),
    ("root='a/'\ndef f(p): os.open(root+p, 1); p.write_text(s); a.p.write_text(s); g(root+p).write_text(s)\nf('l4.rs')", &["/w/l4.rs"]),
    ("root='a/'\ndef f(root, p): open(root+p,'w')\nf('x', 'l5.rs')", &["/w/l5.rs"]),
    ("R='/r'\ndef f(p): open(f\"{R}/{p.upper()}\", 'w'); open(f\"{R}}}/{p}\", 'w'); open(f\"{R}/{p}}}\", 'w')\nf('l6.rs')", &["/w/l6.rs"]),
    ("R='/r'\ndef f(p): open(f\"{R}\" + \"{p}\", 'w'); open(f\"\", 'w'); open(fx + p, 'w'); open(f'{R}', 'w')\nf('l7.rs')", &["/w/l7.rs"]),
    ("R='/r'\ndef f(p): open(R + p / 'x', 'w'); open(R // p, 'w'); open((p), 'w'); open(Path(R) / 'x', 'w'); open(R / Path(p, 'b'), 'w')\nf('l8.rs')", &["/w/l8.rs"]),
    ("root='a/'\ndef f(p): open(root+p,'w')\nobj.f('l9.rs'); subf('m1.rs'); f ('a.json', 'x')", &["/w/l9.rs", "/w/m1.rs", "/w/a/a.json"]),
    ("root='a/'\n# def g(p): open(root+p,'w')\ndefine = 1\ndef x\ndef h(p) x\ndef f(p): open(root+p,'w')\ng('m2.rs'); f(", &["/w/m2.rs"]),
    ("root='a/'\ndef f(p): open(", &[]),
    ("def f(p", &[]),
    ("root='a/'\ndef f(p):\n    x = (1,\n2)\n    open(root+p, 'w')\n  \nf('m3.rs')", &["/w/a/m3.rs"]),
    ("root='a/'\nclass C:\n    def f(self, p):\n        open(root+p, 'w')\n    x = 1\nf(None, 'm4.rs')", &["/w/a/m4.rs"]),
    ("root='a/'\ndef f(p): open(root+p, 'w')\nf()\nf(p)\nf(\"it's\", 'x')", &[]),
    ("root='/a/'\ndef f(p): open(root + p, 'w')\nf('$HOME/x.rs'); f('{C}.rs')", &[]),
    ("root='a#b/'\ndef f(p): open(root + p, 'w')\nf('m5.rs')", &[]),
    ("root='/a/'\ndef f(p): open(root + p, 'w')\nf('m6.rs')\nopen('m6.rs', 'w')", &["/w/m6.rs", "/a/m6.rs"]),
    ("root='/a/'\ndef f(p): open(root + p, 'w')\nopen('m7.rs', 'w')\nf('m7.rs')", &["/w/m7.rs", "/a/m7.rs"]),
    ("root='/a/'\ndef f(p, q): open(root + p, 'w'); open(root + q, 'w')\nf('m8.rs', q='m9.rs')", &["/a/m8.rs", "/a/m9.rs"]),
    ("root='/a/'\ndef f(p):\n    \"\"\"open(root + p, 'w')\"\"\"\n    open(root + p, 'w')\nf('n1.rs')", &["/a/n1.rs"]),
    ("root='/a/'\ndef f(p): open(root + p, 'w')\nf('n2.py' 'x')", &["/w/n2.py"]),
    ("root='/c/'\nopen(root+'x1.rs','w').write(s)\n(Path(root) / 'x2.rs').write_text(s)\ns=open(root+'x3.rs').read()", &["/c/x1.rs", "/c/x2.rs"]),
    ("R='/c'\nopen(f\"{R}/x4.rs\", 'w'); open(f\"{R}\", 'w'); open(f\"{Q}/x5.rs\", 'w')", &["/c/x4.rs"]),
    ("root='/c/'\ndef f(root): open(root + 'y.rs', 'w')", &[]),
    ("x = 1\nopen(base + 'z.rs', 'w')", &[]),
    ("root='/c/'\np = root + 'x6.rs'\nopen(p, 'w')\nq = root + 'x7.rs'\nq = 1\nopen(q, 'w')", &["/c/x6.rs"]),
    ("root='/c/'\np = root + 'x8.rs'\ndef f(p): open(p, 'w')", &[]),
];

/// 451 T110: the binding's places, each `BINDS` program read as gate-write and the event log read it; make-only, fail-closed, names
/// every literal where the shell stands too.
#[test]
fn a_parameter_is_placed_by_each_form_and_fails_open_beside_them() {
    let wrong: Vec<_> = BINDS
        .into_iter()
        .map(|(body, want)| {
            (
                body,
                all_program_names(body, Some("/w"), true, true, &rs),
                want,
            )
        })
        .filter(|(_, got, want)| got != want)
        .collect();
    assert!(wrong.is_empty(), "{wrong:#?}");
    let body = BINDS[0].0;
    let closed = all_program_names(body, Some("/w"), true, false, &rs);
    assert_eq!(closed, ["/w/a.rs", "/w/src/a.rs"], "{body}");
    // the first a caller stops at: the bound write, the program's only one under `placed`
    let first = program_names(body, Some("/w"), true, true, &rs);
    assert_eq!(first.as_deref(), Some("/w/src/a.rs"), "{body}");
}
