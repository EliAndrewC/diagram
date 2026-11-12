//! The parser held to `CPython`'s `ast` on the shapes the audit reads (feature 449 T134's differential: 1,038 files, the standard
//! library, this repository and 197 snippets, 0 differing): each snippet here parses, or fails, as `ast.parse` does.

use super::{is_number, parse, scope_names, walk, Callee, Module, What};

fn calls(m: &Module) -> Vec<String> {
    walk(m)
        .into_iter()
        .filter_map(|n| match &n.what {
            What::Call(Callee::Name(x)) => Some(x.clone()),
            What::Call(Callee::Attr(b, a)) => Some(format!("{b}.{a}")),
            What::Call(Callee::Other) => Some("?".to_owned()),
            _ => None,
        })
        .collect()
}

fn defined(m: &Module) -> Vec<String> {
    walk(m)
        .into_iter()
        .filter_map(|n| match &n.what {
            What::Def(x) | What::Class(x, _) => Some(x.clone()),
            _ => None,
        })
        .collect()
}

fn ok(src: &str) -> Module {
    parse(src).expect("ast.parse reads it")
}

#[test]
fn calls_come_in_ast_walks_breadth_first_order() {
    assert_eq!(calls(&ok("x = f(g(h()))\n")), ["f", "g", "h"]);
    // the body's call is deeper than the next statement's
    assert_eq!(
        calls(&ok("def a():\n    deep()\nshallow()\n")),
        ["shallow", "deep"]
    );
    // an IfExp's test before its body; a dict's keys before its values; keywords after every positional argument
    assert_eq!(calls(&ok("x = a() if b() else c()\n")), ["b", "a", "c"]);
    assert_eq!(
        calls(&ok("x = {k1(): v1(), k2(): v2(), **e()}\n")),
        ["k1", "k2", "v1", "v2", "e"]
    );
    assert_eq!(calls(&ok("f(k=a(), *b())\n")), ["f", "b", "a"]);
    // a function's arguments, body, decorators, returns and type parameters in that order, each a level of its own (`CPython` 3.14)
    assert_eq!(
        calls(&ok("@dec()\ndef f[T: tb()](a: an() = df(), *v: va(), k=kd(), **kw: kwa()) -> ret():\n    body()\n")),
        ["dec", "ret", "kd", "df", "body", "tb", "an", "va", "kwa"]
    );
    assert_eq!(
        calls(&ok("self.m()\ns.n()\nu.v.w()\nf()()\n(a)()\n")),
        ["self.m", "s.n", "?", "?", "a", "f"]
    );
}

#[test]
fn definitions_imports_and_names_are_read() {
    let m = ok("from .. import a as b\nfrom ...x.y import (z, w as v,)\nfrom m import *\nimport a.b.c as d, e\nclass A:\n    xyz = 1\n    ab = 2\n    qq: int\n    (pp_name) = 3\n    t1, t2 = 4, 5\n    def f(self): pass\n    class B:\n        inner_name = 1\nmodule_name = other_name = 1\nif x:\n    hidden_name = 2\n");
    assert_eq!(defined(&m), ["A", "f", "B"]);
    let mut names = scope_names(&m);
    names.sort();
    assert_eq!(
        names,
        [
            "ab",
            "inner_name",
            "module_name",
            "other_name",
            "pp_name",
            "qq",
            "xyz"
        ]
    );
    let imports: Vec<&What> = walk(&m)
        .into_iter()
        .map(|n| &n.what)
        .filter(|w| matches!(w, What::Import(_) | What::From(..)))
        .collect();
    assert_eq!(
        imports[0],
        &What::From(
            String::new(),
            2,
            vec![("a".to_owned(), Some("b".to_owned()))]
        )
    );
    assert_eq!(
        imports[1],
        &What::From(
            "x.y".to_owned(),
            3,
            vec![
                ("z".to_owned(), None),
                ("w".to_owned(), Some("v".to_owned()))
            ]
        )
    );
    assert_eq!(
        imports[2],
        &What::From("m".to_owned(), 0, vec![("*".to_owned(), None)])
    );
    assert_eq!(
        imports[3],
        &What::Import(vec![
            ("a.b.c".to_owned(), Some("d".to_owned())),
            ("e".to_owned(), None)
        ])
    );
}

#[test]
fn numbers_are_pythons() {
    for n in [
        "0x_ff", "0o7", "0b1", "1_000", "1.5e-3", "2j", ".5", "5.", "1e5", "00", "0_0", "0.0_1",
        "1e1_0", "1J",
    ] {
        assert!(is_number(n), "{n}");
    }
    for n in ["007", "1__0", "1_", "0x", "1_e1", "."] {
        assert!(!is_number(n), "{n}");
    }
}

/// Programs `ast.parse` reads.
const VALID: &[&str] = &[
    "", "\n\n\n", "# only a comment\n", "x = 1; y = 2;\n", "if x: y = 1; z = 2\n", "class A: x = 1; yy = 2\n", "x = 1 \\\n  + 2\n",
    "x = [i for i in range(3) for j in range(i) if i if j]\n", "x = (i for i in a)\n", "f((x for x in y))\n", "f(x for x in y)\n", "x = {**a}\n", "x = {}\n",
    "x = {1}\n", "x = {1: 2}\n", "x = {*a(), b()}\n", "{k(): v() for k in a}\n", "{k for k in a}\n", "x = a if b else c if d else e\n", "x = lambda: (yield)\n",
    "x = ...\n", "x = None, True, False\n", "x = 'a' 'b'\n", "x = b'a' b'b'\n", "x = lambda x=f(): g(x)\n", "x = lambda *a, b=c(), **k: d()\n",
    "a.b.c(d)\nf(x)(y)\n", "f(*a, k=g(), *b, **c)\n", "x = [f(i) for i in g() if h(i)]\n", "(yield f())\n", "def g():\n    x = yield f()\n    yield from h()\n",
    "class C[T]: pass\n", "type X = f()\n", "type X[T, *Ts, **P] = list[T]\n", "type = 5\n", "type(x)\n", "class C[T: int = str, *Ts = x, **P = y]: pass\n",
    "match f():\n    case [a, b] if g(a):\n        h()\n    case {'k': v}:\n        pass\n    case P(x=1):\n        q()\n    case _:\n        r()\n",
    "match = 1\nmatch(x)\n", "match a, b:\n    case (1, 2):\n        pass\n",
    "try:\n    f()\nexcept (A, B) as e:\n    g()\nexcept C:\n    h()\nelse:\n    i()\nfinally:\n    j()\n", "try:\n    f()\nexcept A, B:\n    g()\n",
    "try:\n    f()\nexcept* A:\n    g()\n", "try:\n    f()\nexcept:\n    g()\n", "try:\n    f()\nfinally:\n    g()\n",
    "with f() as a, g() as (b, c):\n    h()\n", "with (f() as a, g()):\n    pass\n", "with (f(), g(),):\n    pass\n", "with (f(), g()) as x:\n    pass\n", "with (a):\n    pass\n",
    "with a as b.c, d as e[0], g as *h:\n    pass\n", "with (yield):\n    pass\n",
    "async def f():\n    async with a() as b:\n        await c()\n    async for x in d():\n        e()\n    return [y async for y in z()]\n",
    "for i, (j, k) in enumerate(f()):\n    g()\nelse:\n    h()\n", "for x, in y:\n    pass\n", "while f():\n    break\nelse:\n    g()\n",
    "if a():\n    b()\nelif c():\n    d()\nelif e():\n    f()\nelse:\n    g()\n",
    "x = f'{a()} {b()!r:>{c()}} {d()=}'\n", "x = f'''{\na()\n}'''\n", "x = f'{f\"{g()}\"}'\n", "x = 'a' f'{b()}' 'c'\n", "x = t'{a()}'\n", "x = rb'\\x'\n",
    "x = f'{x:{y}.{z}}'\n", "x = f'{{}}'\n", "x = f'{a = }'\n", "x = f'{a:=10}'\n", "x = f'{a!=b}'\n", "x = f'{(lambda: 1)()}'\n", "x = f'{a,b}'\n",
    "x = '\\''\n", "x = r'\\''\n", "x = \"\"\"a\"b\"\"\"\n", "x = Rb'a' BR'b'\n", "x = 'a' \\\n  'b'\n",
    "from . import a\nimport a.b as c\n", "del a[f()], b.c\n", "del (a, b)\n", "del a,\n", "x += f()\n", "a, *b = c()\n", "[a, b] = c\n", "x: int\n", "x.y: int = 1\n",
    "x[0]: int = yield\n", "global a, b\nnonlocal c\n", "assert f(), g()\n", "assert f()\n", "raise A() from B()\n", "raise\n", "return\n", "return 1, 2\n", "pass\ncontinue\n",
    "x = *a, *b\n", "x = 1,\n", "x = ()\n", "x = (1,)\n", "x = [*a, 1,]\n", "x = a[1:2, ::3, f():]\n", "x = a[*b]\n", "x = a[b:=1]\n", "x = a[::]\n", "x = a[:]\n",
    "x = a[1,]\n", "x = a[1:]\n", "x = a[:2:]\n", "(x := f())\n", "f(x := g())\n", "x = [y := 1, 2]\n", "x = -a ** -b\n", "x = not a == b < c is not d not in e in f is g\n",
    "x = a or b and not c or d\n", "x = a | b ^ c & d << e >> f + g - h * i / j // k % l @ m\n", "x = ~a + +b\n", "x = await f()\n",
    "x = 0x_ff + 0o7 + 0b1 + 1_000 + 1.5e-3 + 2j + .5 + 5. + 1e5 + 1E+5 + 1e-5\n", "x = 1 .real\n", "x = 1.0.hex()\n", "x = 1if y else 2\n", "x =\x0c1\n",
    "if x:\n    pass\n# c\n  # d\nelse:\n    pass\n", "\x0cx = 1\n", "if x:\n\ty\n\tz\n", "for x in *a, b:\n    pass\n", "print(f(*[g()]), **{'a': h()})\n",
    "class A(*b, **c): pass\n", "class A(): pass\n", "def f() -> 'X': pass\n", "x = yield\n", "x = [\n    1,\n    2,\n]\n", "x = (\n# c\n1)\n",
    "def f(\n    a,\n    b,\n):\n    pass\n", "def f(a, /, b, *, c): pass\n", "def f(*args): pass\n", "def f(**kw,): pass\n", "lambda: 0\n",
    "@a\n@b.c(d)\nasync def f(): pass\n", "@a\nclass B: pass\n", "if x:\n    if y:\n        pass\nz = 1\n", "def f():\n    return\n    \n\n    x = 1\n",
    "for *a, b in x:\n    pass\n", "x = 1", "raise A\n", "x = u'a'\n", "x = 'a' # c\n", "f(a)[b](c).d(e)\n", "print(x, end='')\n", "a = b = c = d\n", "a.b = c[d] = e\n", "x = y if z else (yield)\n",
];

/// Programs `ast.parse` refuses.
const INVALID: &[&str] = &[
    "f(a=1, b)\n",
    "f(**a, *b)\n",
    "f(x for x in y, 1)\n",
    "f(1, x for x in y)\n",
    "match x:\n    pass\n",
    "match x:\n    case :\n        pass\n",
    "match x:\n    case a\n",
    "try:\n    pass\n",
    "try:\n    f()\nexcept A:\n    g()\nexcept* B:\n    h()\n",
    "try:\n    f()\nexcept*:\n    g()\n",
    "x = f'{'\n",
    "x = f'}'\n",
    "x = f'{a!x}'\n",
    "x = f'{a:'\n",
    "x = f'{}'\n",
    "x = f'{a b}'\n",
    "from . import\n",
    "from import x\n",
    "import\n",
    "del f()\n",
    "f() += 1\n",
    "f() = 1\n",
    "a, b: int\n",
    "x = 007\n",
    "x = 1__0\n",
    "x = 1.real\n",
    "x = 0x\n",
    "x = 1 2\n",
    "x = (1\n",
    "x = 1)\n",
    "x = [1, 2\n",
    "x = (1]\n",
    "x = 'abc\n",
    "x = '''abc\n",
    "x = $\n",
    "x = a ? b\n",
    "def f(:\n    pass\n",
    "if x:\npass\n",
    "if x:\n        a\n    b\n",
    "  x = 1\n",
    "x = 1\n  y = 2\n",
    "if x:\n\ty\n        z\n",
    "if x:\n        y\n\tz\n",
    "class A:\n    def f(self):\n        pass\n  x = 1\n",
    "x = 1 \\ 2\n",
    "@a\nx = 1\n",
    "@a b\ndef f(): pass\n",
    "async x\n",
    "def f(a, b=1, c): pass\n",
    "def f(**kw, a): pass\n",
    "def f(a, /, b, /): pass\n",
    "def f(/): pass\n",
    "def f(*, *a): pass\n",
    "def f(*a, /): pass\n",
    "x = a not b\n",
    "x = a is not not b\n",
    "x = not\n",
    "if x\n    pass\n",
    "else:\n    pass\n",
    "elif x:\n    pass\n",
    "except:\n    pass\n",
    "with a as f():\n    pass\n",
    "for f() in x:\n    pass\n",
    "x = [f() for g() in y]\n",
    "x = 1_e1\n",
    "x = 0xG\n",
    "\u{feff}x = 1\n",
    "x = 1\0\n",
    "x = 1e\n",
    "x = 0o8\n",
    "x = 0b2\n",
    "if x:\n",
    "class A:\n",
    "x = f'{a!r'\n",
    "x = f'{a:{b'\n",
    "x = 1 +\n",
    "x = [1 for]\n",
    "x = {1: 2, 3}\n",
    "x = {1, 2: 3}\n",
    "x = (yield\n",
    "x = a.\n",
    "x = a[]\n",
    "x = a[1 2]\n",
    "for x in y\n",
    "while x\n",
    "lambda x: \n",
    "x = lambda (x): 1\n",
    "global\n",
    "import a as\n",
    "from x import (a\n",
    "from x import a b\n",
    "x: = 1\n",
    "type X\n",
    "x = yield from\n",
    "with a as (b, f()):\n    pass\n",
    "if x:\n    pass\n  else:\n    pass\n",
    "x = 1 if 2\n",
    "x = !a\n",
    "f(a=1, a)\n",
    "x = '\n'\n",
    "def f() -> : pass\n",
    "x = [a, *]\n",
    "case x:\n    pass\n",
    "x = a.if\n",
    "def if(): pass\n",
    "x = 0x1for\n",
    "x = a\x0cb\n",
    "x = a\x0b\n",
    "if x:\n    if y:\n\tz\n",
    "match x: pass\n",
    "x = f'{a",
    "type X = yield\n",
];

#[test]
fn programs_parse_as_ast_parse_reads_them() {
    for src in VALID {
        assert!(parse(src).is_ok(), "{src:?}: {:?}", parse(src));
    }
    for src in INVALID {
        assert!(parse(src).is_err(), "{src:?} parsed");
    }
}
