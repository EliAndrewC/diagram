//! The read judgment on the shapes the corpora hold (451 T31) and the writes it must still see.

use super::{call_args, expansions, imports, literal, outside_literals, reads};

/// window#307's second heredoc, verbatim: a read that lists tracked files through `git ls-files` (451 T44).
const WINDOW_307: &str = r#"import subprocess, pathlib, collections
root = "/diagram/.clones/diagram-kuwabata"
SUF = {".md",".html",".py",".sh",".txt",".toml",".json",".js",".css",".yml",".yaml"}
out = subprocess.run(["git","-C",root,"ls-files"],capture_output=True,text=True).stdout.split()
ex = [f for f in out if pathlib.Path(f).suffix not in SUF]
c = collections.Counter(pathlib.Path(f).suffix or "(none)" for f in ex)
print("tracked:",len(out),"excluded by suffix:",len(ex))
print(c.most_common(12))
print([f for f in ex if pathlib.Path(f).suffix==""][:12])
"#;

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

/// 451 T44: a subprocess call whose argv is one literal list naming a read-only command is a read (window#307, refused or
/// rewritten on `subprocess` before); every other subprocess shape stays a write.
#[test]
fn a_subprocess_call_with_a_read_only_argv_is_a_read() {
    let read = reads(WINDOW_307, '\'', Some("/nonexistent-t44"));
    assert!(read, "window#307");
    for body in [
        // the corpora's other read-only argvs (window#112, parse#173, #229, refusals#27, #42), each alone
        "import subprocess; print(subprocess.run([\"git\",\"show\",f\"HEAD:a/{p}\"],capture_output=True,text=True).stdout)",
        "import subprocess; s = subprocess.check_output([\"git\", \"rev-parse\", \"--short\", \"HEAD\"], text=True)",
        "import subprocess; r = subprocess.run([\"git\",\"log\",\"--reverse\",\"--format=%ct\\t%s\"],capture_output=True,text=True)",
        "import re, subprocess\nr = subprocess.run([\"git\", \"-C\", str(skill), \"rev-parse\", \"--show-toplevel\"], capture_output=True, text=True)",
        "import subprocess; o = subprocess.run([\"grep\",\"-n\",\"engine-key\\\\|worktree\",\"-A2\",\"x.py\"],capture_output=True,text=True).stdout",
        // the rest of the list, the constants and the other calls
        "import subprocess\nsubprocess.check_call(['git', 'cat-file', '-p', 'HEAD'], stdout=subprocess.DEVNULL)",
        "import subprocess; subprocess.call(['git', 'ls-tree', 'HEAD',], stderr=subprocess.STDOUT, timeout=5)",
        "import subprocess; subprocess.run(['grep', '-n', 'x'], stdout=subprocess.PIPE, check=True, cwd='a')",
        "import subprocess; [subprocess.run([c, 'f']) for c in ()]; subprocess.run(['ls', '-la'])",
        "import subprocess; subprocess.run(['cat', 'a']); subprocess.run(['head', '-5', 'a']); subprocess.run(['wc', '-l', 'a'])",
        "import subprocess; subprocess.run(['git', '-C', a, '-C', 'b', 'log', '--oneline'], input='', encoding='utf-8', errors='replace')",
    ] {
        let one = body.contains("[c, 'f']");
        assert_eq!(reads(body, '\'', Some("/nonexistent-t44")), !one, "{body}");
    }
}

/// 451 T44: what a subprocess call can run or write stays a write - pinned, each judged a write before T44 and after.
#[test]
fn a_subprocess_call_that_can_write_stays_a_write() {
    let writes = [
        "import subprocess; subprocess.run(['git', 'commit', '-m', 'x'])",
        "import subprocess; subprocess.run(['git', 'status'])",
        "import subprocess; subprocess.run(['make', 'done'])",
        "import subprocess; subprocess.run(['rm', 'f'])",
        "import subprocess; subprocess.run(['./git', 'log'])",
        "import subprocess; subprocess.run('git log', shell=True)",
        "import subprocess; subprocess.run('git log')",
        "import subprocess; subprocess.run(['git', 'log'], shell=True)",
        "import subprocess; subprocess.run(['git', 'log'], env={'GIT_PAGER': 'x'})",
        "import subprocess; subprocess.run(['git', 'log'], executable='/bin/rm')",
        "import subprocess; subprocess.run(['git', 'log'], 1)",
        "import subprocess; subprocess.run(argv)",
        "import subprocess; subprocess.run()",
        "import subprocess; subprocess.run(['git', *a])",
        "import subprocess; subprocess.run(['git', 'log', *a])",
        "import subprocess; subprocess.run(['git', sub])",
        "import subprocess; subprocess.run(['git', 'log', x])",
        "import subprocess; subprocess.run(['git', 'log'] + extra)",
        "import subprocess; subprocess.run(['git', 'log', '--output=o'])",
        "import subprocess; subprocess.run(['git', 'log', '-p', '--out', 'o'])",
        "import subprocess; subprocess.run(['git', 'show', '--ext-diff'])",
        "import subprocess; subprocess.run(['git', 'cat-file', '--textconv', 'HEAD:f'])",
        "import subprocess; subprocess.run(['git', 'cat-file', '--filters', 'HEAD:f'])",
        // `status` and `diff` rewrite the index (measured 2026-11-20); `git grep -O` runs a program (spec-fidelity, 2026-11-20)
        "import subprocess; d = subprocess.run([\"git\",\"diff\",\"abc07d9f\",\"--\",\".\"], capture_output=True, text=True).stdout",
        "import subprocess; subprocess.run(['git', 'grep', '-Otouch PWNED', 'hi'])",
        "import subprocess; subprocess.run(['git', 'grep', '--open=touch ABBR', 'hi'])",
        // this container's grep (ugrep) runs a filter, a pager or a viewer, writes a config, or loads options from one
        "import subprocess; subprocess.run(['grep', '--filter=pdf:sh -c x', 'p', '.'])",
        "import subprocess; subprocess.run(['grep', '--pag', 'p', 'f'])",
        "import subprocess; subprocess.run(['grep', '--save-config=o', 'p'])",
        "import subprocess; subprocess.run(['grep', '-nQ', 'p'])",
        "import subprocess; subprocess.run(['grep', '---cfg', 'p', 'f'])",
        "import subprocess; subprocess.run(['git', 'show', f'{flag}'])",
        "import subprocess; subprocess.run(['git', 'show', f'--{o}'])",
        "import subprocess; subprocess.run(['git', '-c', 'core.pager=rm', 'log'])",
        "import subprocess; subprocess.run(['git', '-C'])",
        "import subprocess; subprocess.run(['git', '-C', *d, 'log'])",
        "import subprocess; subprocess.run(['git'])",
        // rg runs a program by `--pre` or `--hostname-bin` (spec-fidelity, 2026-11-20): not on the list at all
        "import subprocess; subprocess.run(['rg', '--pre', 'sh', 'x'])",
        "import subprocess; subprocess.run(['rg', '--hostname-bin=./x', '--hyperlink-format=default', 'p'])",
        "import subprocess; subprocess.run(['rg', '-n', 'x'])",
        "import subprocess; subprocess.run(['git', 'log' if c else 'push'])",
        "import subprocess; subprocess.run(['git', '$SUB'])",
        "import subprocess; subprocess.run(['git', 'log', \"a\\\"b\"])",
        "import subprocess; subprocess.run(['git', 'log'], input=os.remove('f'))",
        "import subprocess; subprocess.run(['git', 'log'], stdout=open('o', 'w'))",
        "import subprocess; subprocess.Popen(['git', 'log'])",
        "import subprocess; subprocess.getoutput('git log')",
        "import subprocess as sp; sp.run('rm f', shell=True)",
        "from subprocess import run; run(['rm', 'f'])",
        "import subprocess; s = subprocess; s.run(['rm', 'f'])",
        "import subprocess; subprocess.run(args=['git', 'log'])",
    ];
    let misread: Vec<&str> = writes
        .into_iter()
        .filter(|body| reads(body, '\'', Some("/nonexistent-t44")))
        .collect();
    assert!(misread.is_empty(), "judged reads: {misread:#?}");
}

/// 451 T44: window#307 whole, through the walk: neither heredoc is a write where the shell stands.
#[test]
fn window_307_runs_as_typed() {
    let file = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../tests/hooks/fixtures/command-window-2026-09-13.json"
    );
    let v: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(file).unwrap()).unwrap();
    let cmd = v["commands"][307]
        .as_str()
        .unwrap()
        .replace("/diagram", "/nonexistent-t44");
    assert!(cmd.contains("\"git\",\"-C\",root,\"ls-files\""));
    let w =
        crate::shared::tree::walk_judged(&cmd, Some("/nonexistent-t44"), "/nonexistent-t44", "/h");
    assert!(w.targets.is_empty(), "window#307 judged a write"); // every segment a read: no target at all
}
