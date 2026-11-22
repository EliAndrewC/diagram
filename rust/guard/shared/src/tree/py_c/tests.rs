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

/// T58's heredoc of 2026-11-21T05:51:53Z, verbatim: a read of the event logs whose `git log` names its window by two f-string
/// options (451 T63: the one read-only program among the 250 make-only refusals the guard log replayed, measured 2026-11-21).
const T58_0551: &str = r#"import json,glob,subprocess,re,collections
from datetime import datetime
seen=set(); wide=[]
for f in glob.glob('.git/l7r-events/*.jsonl'):
    for line in open(f,errors='replace'):
        if '"cover-build"' not in line: continue
        e=json.loads(line)
        if len(e.get('crates',[]))<24 or e['t0'] in seen: continue
        seen.add(e['t0']); wide.append(e)
wide.sort(key=lambda e:e['t0'])
gm=('rust/guard/src/guards/event_log_hooks','rust/guard/src/guards/house_style_hooks','rust/guard/src/guards/feature_approval_hooks','rust/guard/src/guards/set_down_hooks','rust/guard/src/guards/conflict_marker_hooks','rust/guard/src/suite_tools/pylex','rust/guard/src/protocol')
def istest(r): return bool(re.search(r'(^|/)tests(\.rs|/)',r))
prev=None; tally=collections.Counter(); secs=collections.Counter()
for w in wide:
    d=round((datetime.fromisoformat(w['t1'].replace('Z','+00:00'))-datetime.fromisoformat(w['t0'].replace('Z','+00:00'))).total_seconds())
    if prev is None: prev=w; continue
    out=subprocess.run(['git','-C','/diagram/.clones/diagram-backlog','log','--format=@','--name-only',f'--since={prev["t0"]}',f'--until={w["t0"]}','--','rust/'],capture_output=True,text=True).stdout
    files=set(l for l in out.split('\n') if l.startswith('rust/'))
    gl=[f for f in files if f.startswith('rust/guard/') and not istest(f) and (f.startswith('rust/guard/src/shared') or f.startswith(gm))]
    gh=[f for f in files if f.startswith('rust/guard/src/') and not istest(f) and f not in gl]
    gt=[f for f in files if f.startswith('rust/guard/') and istest(f)]
    ga=[f for f in files if f.startswith('rust/gate/')]
    k=('guard-lib ' if gl else '')+('guard-hook ' if gh else '')+('guard-test ' if gt and not gl and not gh else '')+('gate ' if ga else '')
    k=k.strip() or 'nothing in rust/'
    tally[k]+=1; secs[k]+=d
    prev=w
for k in tally: print(k, tally[k], 'builds', secs[k], 's')
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
    let d = crate::tempdir::TempDir::new("guard-py-c");
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
        // 451 T63: an f-string option is its name with a placeholder value only where the name is literal and the value calls
        // nothing, so a writing option's name, a call, an escape, a short option or a name the value can reach stays a write
        "import subprocess; subprocess.run(['git', 'log', f'--output={p}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--out={p}'])",
        "import subprocess; subprocess.run(['git', 'show', F'--ext-diff={x}'])",
        "import subprocess; subprocess.run(['grep', f'--filter={x}', 'p'])",
        "import subprocess; subprocess.run(['grep', f'---c={x}', 'p'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since={f()}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since={d[g()]}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since={x}\\n'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since=$X{x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--{o}={x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since{x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since {x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'-{x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'-S={x}'])",
        "import subprocess; subprocess.run(['git', f'--git-dir={d}', 'log'])",
        "import subprocess; subprocess.run([f'--since={x}', 'log'])",
        "import subprocess; subprocess.run(['git', 'push', f'--since={x}'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since={open(\"Makefile\", \"w\")}'])",
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

/// 451 T63: an f-string option whose name is literal and whose value calls nothing is judged as that option with a placeholder
/// value - T58's heredoc of 05:51:53Z, refused as a guard write for its `f'--since={prev["t0"]}'`, and the shapes beside it.
#[test]
fn an_f_string_option_whose_value_calls_nothing_is_that_option() {
    // T58 05:51:53Z's heredoc reads
    assert!(reads(T58_0551, '\'', Some("/nonexistent-t63")));
    let cmd = format!("python3 -I - <<'EOF'\n{T58_0551}EOF");
    let w = crate::tree::walk_judged(&cmd, Some("/nonexistent-t63"), "/nonexistent-t63", "/h");
    assert!(w.targets.is_empty(), "T58 05:51:53Z judged a write");
    for body in [
        "import subprocess; subprocess.run(['git', 'log', f'--since={prev[\"t0\"]}', f\"--until={w['t0']}\"])",
        "import subprocess; subprocess.run(['git', 'log', F'--format={fmt}', rf'--author={a}', '--', 'rust/'])",
        "import subprocess; subprocess.run(['git', 'log', f'--since=2026-11-21'])",
        "import subprocess; subprocess.run(['grep', f'--max-count={n}', 'p', 'f'])",
    ] {
        assert!(reads(body, '\'', Some("/nonexistent-t63")), "{body}");
    }
}

/// 451 T44: window#307 whole, through the walk: neither heredoc is a write where the shell stands.
#[test]
fn window_307_runs_as_typed() {
    let file = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../tests/hooks/fixtures/command-window-2026-09-13.json"
    );
    let v: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(file).unwrap()).unwrap();
    let cmd = v["commands"][307]
        .as_str()
        .unwrap()
        .replace("/diagram", "/nonexistent-t44");
    assert!(cmd.contains("\"git\",\"-C\",root,\"ls-files\""));
    let w = crate::tree::walk_judged(&cmd, Some("/nonexistent-t44"), "/nonexistent-t44", "/h");
    assert!(w.targets.is_empty(), "window#307 judged a write"); // every segment a read: no target at all
}

/// The mirror the argv walks stand in (451 T89): a path no test makes, as `window_307_runs_as_typed`'s.
const M: &str = "/nonexistent-t89";

/// 451 T89: (path, class, how) of each write a walk standing in the mirror finds - its reads (`how` "read") left out, as every
/// guard leaves them out.
fn argv_written(cmd: &str) -> Vec<(Option<String>, &'static str, &'static str)> {
    crate::tree::walk_judged(cmd, Some(M), M, "/h")
        .targets
        .into_iter()
        .filter(|t| t.how != "read")
        .map(|t| (t.path, t.class, t.how))
        .collect()
}

fn placed(
    path: Option<&str>,
    class: &'static str,
    how: &'static str,
) -> Vec<(Option<String>, &'static str, &'static str)> {
    vec![(path.map(str::to_owned), class, how)]
}

/// 451 T89, found by T79 (2026-11-21): a program that writes through `sys.argv[N]` writes the command's N-th word after the program,
/// placed as the walk places a word - T79's probes (`/tmp/t79b/judge/probe-mt.jsonl` #2-#4) and bx#54240's, bx#58694's and
/// bx#29969's shapes, each refused standing in the mirror at HEAD as a write where the shell stood.
#[test]
fn a_program_writes_the_word_its_argv_names() {
    let q = format!("{M}/research/questions");
    let p = "\"import sys; open(sys.argv[2],'w').write('x')\"";
    let one = format!("cd {q}; python3 -I -c {p} a /tmp/q/a.txt");
    let one_got = argv_written(&one);
    let scratch = placed(Some("/tmp/q/a.txt"), "elsewhere", "named");
    assert_eq!(one_got, scratch, "{one}");
    let looped = format!("cd {q}; for f in 0005*; do python3 -I -c {p} a /tmp/q/txt/$f.txt; done"); // a glob's value as the word
    let looped_got = argv_written(&looped);
    assert_eq!(looped_got, placed(None, "elsewhere", "named"), "{looped}");
    let pair = format!("cd {q}; for f in a b; do python3 -I -c {p} $f /tmp/q/txt/$f.txt; done");
    let pair_got = argv_written(&pair);
    let pair_want = vec![
        (Some("/tmp/q/txt/a.txt".to_owned()), "elsewhere", "named"),
        (Some("/tmp/q/txt/b.txt".to_owned()), "elsewhere", "named"),
    ];
    assert_eq!(pair_got, pair_want, "{pair}");
    let held = format!("cd {q}; python3 -I -c {p} \"a b\" /tmp/q/a.txt"); // a quoted word with a blank is one word
    let held_got = argv_written(&held);
    assert_eq!(held_got, scratch, "{held}");
    let dumped = "python3 -I -c \"import json,sys;d=json.load(open(sys.argv[1]));d.pop('k');json.dump(d,open(sys.argv[1],'w'))\" /tmp/q/r.json";
    let dumped_got = argv_written(dumped);
    let dumped_want = placed(Some("/tmp/q/r.json"), "elsewhere", "named");
    assert_eq!(dumped_got, dumped_want, "{dumped}");
}

/// 451 T89, its review (2026-11-21): a name bound once to `sys.argv[N]`, its every other mention an `open` of it, is `sys.argv[N]`
/// there - bx#58999's shape, refused standing in the mirror at HEAD as a write where the shell stood - and a mirror word bound so
/// is the mirror's.
#[test]
fn a_name_bound_to_argv_writes_the_word_it_holds() {
    let q = format!("{M}/research/questions");
    let p = "\"import sys,json\np=sys.argv[1]; t=open(p).read()\nfor a,b in [('x','y')]: t=t.replace(a,b)\njson.loads(t); open(p,'w').write(t)\"";
    let scratch = format!("cd {q}; python3 -I -c {p} /tmp/q/f.json");
    let scratch_got = argv_written(&scratch);
    let scratch_want = placed(Some("/tmp/q/f.json"), "elsewhere", "named");
    assert_eq!(scratch_got, scratch_want, "{scratch}");
    let mirror = format!("cd /tmp; python3 -I -c {p} {M}/x");
    let mirror_got = argv_written(&mirror);
    let mirror_want = placed(Some(&format!("{M}/x")), "main", "named");
    assert_eq!(mirror_got, mirror_want, "{mirror}");
}

/// 451 T89: the word is placed as any other - a mirror path is the mirror's (named, so refused, never moved), a relative one lands
/// where the shell stands; a redirect is no word of argv, and an unset name's unquoted expansion is none either, as in bash.
#[test]
fn an_argv_word_is_placed_as_the_walk_places_a_word() {
    let p = "\"import sys; open(sys.argv[2],'w').write('x')\"";
    let mirror = format!("cd /tmp; python3 -c {p} a {M}/x");
    let mirror_got = argv_written(&mirror);
    let mirror_x = placed(Some(&format!("{M}/x")), "main", "named");
    assert_eq!(mirror_got, mirror_x, "{mirror}");
    let relative = format!("cd {M}/q; python3 -c {p} a out.txt");
    let relative_got = argv_written(&relative);
    let relative_want = placed(Some(&format!("{M}/q/out.txt")), "main", "shell");
    assert_eq!(relative_got, relative_want, "{relative}");
    let unset = format!("cd /tmp; python3 -c {p} $UNSET_T89 /tmp/q/a {M}/x");
    let unset_got = argv_written(&unset);
    assert_eq!(unset_got, mirror_x, "{unset}");
    let redirected = format!("cd {M}; python3 -c {p} a > /tmp/q/log /tmp/q/a.txt");
    let redirected_got = argv_written(&redirected);
    let redirected_want = vec![
        (Some("/tmp/q/a.txt".to_owned()), "elsewhere", "named"),
        (Some("/tmp/q/log".to_owned()), "elsewhere", "named"),
    ];
    assert_eq!(redirected_got, redirected_want, "{redirected}");
}

/// 451 T89: where the binding cannot say which word the program writes, or the walk cannot place it, the program keeps HEAD's
/// reading, D5's write where the shell stands (here the mirror's `q`, so a guard moves or refuses it as before).
#[test]
fn an_argv_write_the_walk_cannot_bind_keeps_heads_reading() {
    let p = "\"import sys; open(sys.argv[2],'w').write('x')\"";
    let cases = [
        format!("python3 -c {p} a"),                                    // an index past the words
        format!("python3 -c {p} $(ls) /tmp/q/a"),                       // a word before it that may be many, or none
        format!("python3 -c {p} *.txt /tmp/q/a"),                       // a glob
        format!("python3 -c {p} \"$@\" /tmp/q/a"),                      // the shell's own arguments
        format!("python3 -c {p} {{a,b}} /tmp/q/a"),                     // a brace expansion
        format!("python3 -c {p} x\"a b\"$X /tmp/q/a"),                  // a word quoted in part
        format!("X='a b'; python3 -c {p} $X /tmp/q/a"),                 // a value that splits, or not, as it is quoted
        format!("E=; python3 -c {p} $E /tmp/q/a"),                      // a value that vanishes, or not
        format!("read D; python3 -c {p} a $D/x"),                       // a word nothing is known of
        format!("python3 -c {p} a $(cat w)"),                           // a word led by a substitution
        format!("python3 -c {p} a > /tmp/q/a"),                         // the redirect is no word: an index past the words
        format!("for f in Seeing*; do python3 -c {p} $f /tmp/q/$f.txt; done"), // a glob's value before it, bash's split shifting it
        format!("for f in 0005*; do python3 -I -c {p} $f /tmp/q/txt/$f.txt; done"), // bx#58694's, though its matches hold no blank
        format!("for f in 0053-*; do python3 -c {p} \"$f\" /tmp/q/txt/$f.txt; done"), // quoted, which the walk cannot see (T140)
        format!("for f in \"a b\"; do python3 -c {p} $f /tmp/q/a; done"), // a loop's value with a blank, `bind`'s `a_b`
        format!("read f; python3 -c {p} $f /tmp/q/a"),                  // a value read from input
        "python3 -c \"import sys; open(sys.argv[0],'w').write('x')\" /tmp/q/a".to_owned(), // the `-c` itself
        "python3 -c \"import sys; open(sys.argv[1],'w').write('x'); open('y','w')\" /tmp/q/a".to_owned(), // another write
        "python3 -c \"import sys; f=open(sys.argv[1],'w'); f.write('x')\" /tmp/q/a".to_owned(), // a write through a name
        "python3 -c \"import sys; p=sys.argv[1]; open(p,'w').write(p)\" /tmp/q/a".to_owned(), // a bound name used otherwise
        "python3 -c \"import sys; p=sys.argv[1]; p=p+'x'; open(p,'w').write('x')\" /tmp/q/a".to_owned(), // bound again
        "python3 -c \"import sys; p=sys.argv[1]+'x'; open(p,'w').write('x')\" /tmp/q/a".to_owned(), // bound to more than argv
        "python3 -c \"import io,sys; p=sys.argv[1]; io.open(p,'w').write('x')\" /tmp/q/a".to_owned(), // another module's open
        "python3 -c \"import sys; sys.argv[1]='/tmp/z'; open(sys.argv[1],'w').write('x')\" /tmp/q/a".to_owned(), // argv assigned
        "python3 -c \"import sys; del sys.argv[1]; open(sys.argv[1],'w').write('x')\" /tmp/q/a /tmp/q/b".to_owned(), // deleted from
        "python3 -c \"import sys; a=sys.argv; open(sys.argv[1],'w').write('x')\" /tmp/q/a".to_owned(), // aliased
        "python3 -c \"from sys import argv; open(argv[1],'w').write('x')\" /tmp/q/a".to_owned(), // imported by name
        "python3 -c \"import os as sys; open(sys.argv[1],'w').write('x')\" /tmp/q/a".to_owned(), // another module as `sys`
        "python3 -c \"open(sys.argv[1],'w').write('x')\" /tmp/q/a".to_owned(), // `sys` never imported
        "python3 -c \"import sys; open(sys.argv[1],'w',opener=lambda p,f: os.open('x',f)).write('x')\" /tmp/q/a".to_owned(), // its opener writes
    ];
    let head = placed(Some(&format!("{M}/q")), "main", "shell");
    for case in cases {
        let cmd = format!("cd {M}/q; {case}");
        let got = argv_written(&cmd);
        let shell: Vec<_> = got.into_iter().filter(|w| w.2 == "shell").collect();
        assert_eq!(shell, head, "{cmd}");
    }
}

/// 451 T89: the binding read alone - the `sys.argv[N]` a program writes, where it writes nowhere else, and the word each N holds
/// (`tree::program`'s reader is to call `argv_word` too, T125).
#[test]
fn the_binding_reads_argv_as_python_and_bash_make_it() {
    let env = super::Env::new();
    let after = ["a", ">", "/tmp/log", "2>&1", "\"\"", "/tmp/q/b"];
    let got: Vec<_> = (0..5)
        .map(|n| super::argv_word(n, &after, &env, "/h"))
        .collect();
    let want = [None, Some("a"), Some("\"\""), Some("/tmp/q/b"), None];
    assert_eq!(got, want);
    // a word bash may split - a loop's or a read's value (`$__unread__`), `bind`'s `_` for a blank - is the word where it is the
    // one asked for, its first piece where its start lies, and shifts every index past it, so none past it is known
    let split = ["0005$__unread__", "sweet_potato", "$__unread__", "/tmp/q/b"];
    let split_got: Vec<_> = (0..4)
        .map(|k| super::argv_word(1, &split[k..], &env, "/h"))
        .collect();
    let split_want = [
        Some("0005$__unread__"),
        Some("sweet_potato"),
        Some("$__unread__"),
        Some("/tmp/q/b"),
    ];
    assert_eq!(split_got, split_want);
    let past: Vec<_> = split[..3]
        .iter()
        .map(|w| super::argv_word(2, &[w, "/tmp/q/b"], &env, "/h"))
        .collect();
    assert_eq!(past, [None, None, None]);
    let process = super::argv_word(2, &["<(x)", "/tmp/q/b"], &env, "/h");
    assert_eq!(process, None); // a process substitution is a word, its path the shell's
    let s = |p: &str| super::argv_writes(p, '\'', Some(M)); // run in a place no module of its imports lies in
    for (program, want) in [
        ("import sys; open(sys.argv[2],'w').write('x')", Some(vec![2])),
        ("import sys; print(1, file=open(sys.argv[1], 'a'))", Some(vec![1])),
        ("import json,sys; json.dump({}, open(sys.argv[1],'w'), indent=1)", Some(vec![1])),
        ("import sys; open(sys.argv[3],'w').write(open(sys.argv[1]).read()); open(sys.argv[2], mode='w').writelines([])", Some(vec![2, 3])),
        ("import sys; open(sys.argv[1],'w').write(str(open(sys.argv[2],'w')))", Some(vec![1, 2])),
        ("import sys; open(sys.argv[1],'w').write(str(open(sys.argv[2],'w'))); open('y','w')", None),
        ("import sys; print(open(sys.argv[1]).read())", None),
        ("import sys,pickle; pickle.dump(1, open(sys.argv[1],'wb'))", None),
        ("import sys; open(sys.argv[1],'w').write(x); os.remove('z')", None),
        ("import sys; open(sys.argv[1] + '.bak','w').write('x')", None),
        ("import sys; open(sys.argv[1],'w').write('x'); sys.argv[1:]", None),
    ] {
        let got = s(program);
        assert_eq!(got, want, "{program}");
    }
}
