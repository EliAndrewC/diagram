//! The read judgment on the shapes the corpora hold (451 T31) and the writes it must still see.

use super::{call_args, expansions, imports, literal, outside_literals, reads};

#[test]
fn a_program_that_only_reads_is_a_read() {
    for (body, q) in [
        (
            "\ndata = open('$SP/x.html','rb').read()\nprint(len(data))",
            '"',
        ),
        (
            "import json; print(json.load(open(\"a.json\", encoding=\"utf-8\", errors='replace')))",
            '\'',
        ),
        ("import sys,json; print(json.load(sys.stdin).get('x'))", '"'),
        ("print(open(p, mode='rt').read())", '"'),
        (
            "import codecs; print(codecs.open('x.txt', 'r').read())",
            '"',
        ),
        (
            "from PIL import Image; print(Image.open(f'/tmp/{m}.png').size)",
            '"',
        ),
        (
            "import pathlib; print(pathlib.Path('x').open().read())",
            '"',
        ),
        ("print(open(\\\"a\\\").read().replace('a', 'b'))", '"'),
        ("import ast; ast.literal_eval('1')", '"'),
        ("print(1)", '\''),
        // 451 T42: `re.compile` builds a pattern, no code - window#307's first heredoc, a read judged a write on it
        (
            "import re; R = re.compile(r'x'); print(R.findall(open('a').read()))",
            '\'',
        ),
        // an unquoted heredoc's body (`'h'`): `$X` inside a literal, `\"` two characters there
        ("print(\"a\\\"$X\")", 'h'),
        ("print('$HOME')", 'h'),
    ] {
        assert!(reads(body, q, Some("/nonexistent-t31")), "{body}");
    }
    assert!(reads("print(1)", '"', None));
}

#[test]
fn a_program_that_can_write_is_a_write() {
    let writes = [
        ("open('o.txt','w').write('x')", '"'),
        ("open('o.txt', 'r+')", '"'),
        ("open('o.txt', mode='a')", '"'),
        ("m = 'w'; open('o.txt', m)", '"'),
        ("open('o.txt', 'w' if x else 'r')", '"'),
        ("open(file='o.txt')", '"'),
        ("open('o.txt', opener=f)", '"'),
        ("import pathlib; pathlib.Path('o').open('w')", '"'),
        ("import pathlib; pathlib.Path('o').open(m)", '"'),
        ("import pathlib; pathlib.Path('a').replace('b')", '"'),
        ("import os; os.replace('a', 'b')", '"'),
        ("import os; os.remove('f')", '"'),
        ("import json; json.dump({}, f)", '"'),
        ("import subprocess; subprocess.run(['rm', 'f'])", '"'),
        ("print('$(rm f)')", '"'),
        // 451 T42: the builtin `compile` (and `re.compile` named by anything but `re`) stays a write
        ("exec(compile('x', 'f', 'exec'))", '\''),
        ("c = compile; pre.compile('x')", '\''),
        ("import sre; sre.compile('x')", '\''),
        ("print('$(rm f)')", 'h'),
        ("print(`rm f`)", 'h'),
        ("$CODE", 'h'),
        ("print('`rm f`')", '"'),
        ("from . import x", '\''),
        // the shell expands a name outside Python's literals into code before Python sees it
        ("$PROG", '"'),
        ("import json; ${CODE}", '"'),
        ("print(1) # $X", '"'),
        // a call or argument list the mode cannot be read from
        ("open(*a)", '"'),
        ("open('o.txt', **kw)", '"'),
        // known writers the first list missed
        (
            "import urllib.request as u; u.urlretrieve('http://x', 'o')",
            '"',
        ),
        ("import io; io.FileIO('o', 'w')", '"'),
        ("import gzip; gzip.GzipFile('o', 'wb')", '"'),
        (
            "import fileinput; [print(l) for l in fileinput.input('f', inplace=True)]",
            '"',
        ),
        ("import numpy as np; np.savetxt('o', a)", '"'),
        ("import numpy as np; np.savez('o', a=a)", '"'),
        ("a.tofile('o')", '"'),
        ("import os; getattr(os, 'rem' + 'ove')('f')", '"'),
        ("import os; os.link('a', 'b')", '"'),
        ("vars(__builtins__)['op' + 'en']('o', 'w')", '"'),
    ];
    // every program misjudged named at once, not the first alone
    let mut misread: Vec<&str> = writes
        .iter()
        .filter_map(|&(body, q)| reads(body, q, Some("/nonexistent-t31")).then_some(body))
        .collect();
    // a name the shell expands INSIDE a Python literal is a path or a word, as `$SP` is; one escaped is Python's own `$`
    assert!(reads("print(open('$SP/x').read(), \"${N}\")", '"', None));
    assert!(reads("print(\\$X)", '"', None));
    assert!(reads("print($X)", '\'', None));
    assert!(!reads("import json", '"', None)); // an import where the directory is unknown
    let d = crate::shared::tempdir::TempDir::new("guard-py-c");
    std::fs::create_dir_all(d.join("l7r")).unwrap();
    std::fs::write(d.join("mod.py"), "").unwrap();
    let at = d.to_string_lossy().into_owned();
    assert!(!reads("import l7r.diagram as d", '"', Some(&at)));
    assert!(!reads("import json, mod", '"', Some(&at)));
    assert!(!reads("from l7r.diagram import x", '"', Some(&at)));
    // an import after a `:` or inside a block is still an import
    let blocks = [
        "try: import l7r\nexcept ImportError: pass",
        "if True:\n    from l7r import x",
        "x = 1; import json,mod",
    ];
    misread.extend(
        blocks
            .into_iter()
            .filter(|body| reads(body, '"', Some(&at))),
    );
    assert!(reads("import json, re as r", '"', Some(&at)));
    assert!(misread.is_empty(), "judged reads: {misread:#?}");
}

#[test]
fn the_parts_read_python_as_python_does() {
    assert_eq!(
        expansions(r#"a \"b\" \\ \$x \` \n"#, '"').0,
        "a \"b\" \\ $x ` \\n"
    );
    assert_eq!(expansions(r#"a \"b\""#, '\'').0, r#"a \"b\""#);
    assert_eq!(
        expansions(r"a $X \$Y ${Z} $ é$1", '"'),
        ("a $X $Y ${Z} $ é$1".to_owned(), vec![2, 8, 17])
    );
    assert!(!outside_literals(
        "print('é$', \"\"\"\n$\\\"\"\"\")",
        &[9, 17]
    ));
    assert!(outside_literals("s = 'a' + $", &[10]));
    // a comment's apostrophe opens no literal, so the expansion on the next line is code (451 T31); a `#` in a string is no comment
    assert!(outside_literals("# don't\n$", &[8]));
    assert!(!reads("# don't\n$CODE", '"', None));
    assert!(!outside_literals("s = '#' + '$'", &[11]));
    assert_eq!(
        call_args("'a, b', f(x, y), [1, 2], 'q\\'s') + 1", 0),
        ["'a, b'", "f(x, y)", "[1, 2]", "'q\\'s'"]
    );
    assert!(call_args(")", 0).is_empty());
    assert_eq!(literal("rb'x'").as_deref(), Some("x"));
    assert_eq!(literal("x"), None);
    assert_eq!(
        imports("import a.b as c, d\nfrom e.f import g; import h"),
        Some(vec!["a".into(), "d".into(), "h".into(), "e".into()])
    );
    assert_eq!(imports("from .x import y"), None);
}
