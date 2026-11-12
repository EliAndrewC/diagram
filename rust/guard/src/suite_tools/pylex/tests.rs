//! The lexer against what `ast` says of each shape; the whole repository was the differential (`m:t050-deps-differential`).

use super::read;

fn strings(src: &str) -> Vec<String> {
    read(src).unwrap().strings
}

fn imports(src: &str) -> Vec<String> {
    read(src).unwrap().imported
}

fn docs(src: &str) -> Vec<usize> {
    read(src).unwrap().docstring_lines.into_iter().collect()
}

#[test]
fn a_docstring_is_the_first_statement_of_a_module_a_function_or_a_class() {
    assert_eq!(docs("\"\"\"mod\nline\"\"\"\nx = 1\n"), [1, 2]);
    assert_eq!(docs("# c\n\n'mod'\n"), [3]);
    assert_eq!(docs("def f():\n    'doc'\n    'not'\n"), [2]);
    assert_eq!(
        docs("async def f(a: dict[str, int]) -> int:\n    'doc'\n"),
        [2]
    );
    assert_eq!(docs("class A(B):\n    'doc' 'too'\n"), [2]);
    assert_eq!(docs("def f(): 'same line'\n"), [1]);
    assert_eq!(docs("'a'; x = 1\n"), [1]);
    assert_eq!(docs("x = 1\n'not first'\n"), Vec::<usize>::new());
    assert_eq!(
        docs("if x:\n    'not a body that has one'\n"),
        Vec::<usize>::new()
    );
    assert_eq!(docs("f'not constant'\n"), Vec::<usize>::new());
    assert_eq!(docs("b'bytes'\n"), Vec::<usize>::new());
    assert_eq!(docs("'a'.join(x)\n"), Vec::<usize>::new());
    assert_eq!(docs("def"), Vec::<usize>::new());
}

#[test]
fn the_imports_are_the_last_parts_and_the_names_taken() {
    assert_eq!(imports("import a.b as c, d\n"), ["b", "d"]);
    assert_eq!(imports("from a.b import x, y as z\n"), ["b", "x", "y"]);
    assert_eq!(
        imports("from a import (\n    x,\n    y,\n)\n"),
        ["a", "x", "y"]
    );
    assert_eq!(imports("from . import x\n"), Vec::<String>::new());
    assert_eq!(imports("from .a import x\n"), ["a", "x"]);
    assert_eq!(
        imports("try: import q; import r\nexcept E: pass\n"),
        ["q", "r"]
    );
    assert_eq!(
        imports("raise X from e\nyield from z\n"),
        Vec::<String>::new()
    );
    assert_eq!(imports("from x\n"), Vec::<String>::new());
    assert_eq!(imports("from a import *\n"), ["a"]);
}

#[test]
fn strings_are_joined_and_decoded_and_comments_hold_none() {
    assert_eq!(strings("x = 'a' \"b\"  # 'c'\n"), ["ab"]);
    assert_eq!(
        strings("x = 'a\\n\\t\\r\\\\\\'\\\"\\q\\\nb'\n"),
        ["a\n\t\r\\'\"\\qb"]
    );
    assert_eq!(strings("x = r'a\\n'\n"), ["a\\n"]);
    assert_eq!(strings("x = '''a\n'b''''''c'''\n"), ["a\n'bc"]);
    assert_eq!(
        strings("x = (\n 'a'\n)\ny = \\\n 'b'\nf(1, 'c')"),
        ["a", "b", "c"]
    );
    assert_eq!(strings("x = RB'a' + U'b'\n"), ["a", "b"]);
    assert_eq!(strings("rb = 1\nf = 2\nx = rb\n"), Vec::<String>::new());
}

#[test]
fn an_f_string_is_its_literal_parts_and_the_strings_of_its_expressions() {
    assert_eq!(strings("x = f'a{b}c'\n"), ["a", "c"]);
    assert_eq!(strings("x = 'p' f'a{b}c' 'q'\n"), ["pa", "cq"]);
    assert_eq!(strings("x = f'{{a}}'\n"), ["{a}"]);
    assert_eq!(strings("x = f'{d[\"k\"]}'\n"), ["k", "", ""]);
    // a hole whose last token is a string closes its run at the hole's end (reached by the real tree's `hm_shape.py` until
    // feature 449 T129 deleted it)
    assert!(strings("x = f'{\"k\"}'\n").contains(&"k".to_owned()));
    assert_eq!(strings("x = f'{a!r:>{w}3}z'\n"), [">3", "", "z"]);
    assert_eq!(strings("x = f'{a != b}'\n"), ["", ""]);
    assert_eq!(strings("x = f'{d[1:2]}'\n"), ["", ""]);
}

#[test]
fn what_python_could_not_read_is_none() {
    assert!(read("x = 'open\n").is_none());
    assert!(read("x = '''open\n").is_none());
    assert!(read("x = (\n").is_none());
    assert!(read("x = )\n").is_none());
    assert!(read("x = f'}'\n").is_none());
    assert!(read("x = f'{a'\n").is_none());
    assert!(read("x = f'{a:b").is_none());
    assert!(read("x = f'{a;'\n").is_none());
    assert!(read("x = 'a\\").is_none());
    assert_eq!(read("").unwrap(), super::Facts::default());
}

#[test]
fn the_classes_that_set_a_key_as_ast_reads_them() {
    use super::kinds;
    let found = kinds(concat!(
        "class A(Kind):\n    \"\"\"  Doc line\n\n\t  tabbed\n      indented\n    \"\"\"\n    key = \"a k\"\n",
        "class B(X): key = 'b'; other = 1\n",
        "class C:\n    key = 1\n    key = 'late'\n",
        "class D:\n    if x:\n        key = 'nested'\n    key: str = 'annotated'\n    key += 'aug'\n    key == 'cmp'\n",
        "class E:\n    a = key = ('p' 'q')\n    b = (key) = 'r'\n",
        "class F:\n    \"\"\"\n    \"\"\"\n    key = 'x' 'y'\n    def f(self):\n        key = 'z'\n",
        "class G:\n    b'doc'\n    key = f'k{x}'\n",
        "class H:\n    key = b'bytes'\n",
        "class I:\n    key = None\n",
        "class J:\n    key = 1.5\n    key = 'after'\n",
        "class K:\n    key = -1\n    key = 'neg'\n",
        "class L:\n    key = 'l'\n",
        "def f():\n    class M:\n        key = 'inner'\n",
        "class O: pass\n",
        "class P:\n    key = [\"x\"]\n    key = 'p'\n",
        "class R:\n    key = ('a', 'b')\n    key = ('r')\n",
        "class S:\n    key = (1) + (2)\n    key = 's'\n",
    ))
    .unwrap();
    let got: Vec<(&str, &str, usize, &str)> = found
        .iter()
        .map(|k| (k.name.as_str(), k.key.as_str(), k.line, k.doc.as_str()))
        .collect();
    assert_eq!(
        got,
        [
            ("A", "a k", 1, "Doc line\n\n    tabbed\nindented"),
            ("B", "b", 8, ""),
            ("E", "pq", 18, ""),
            ("F", "xy", 21, "    "),
            ("K", "neg", 37, ""),
            ("L", "l", 40, ""),
            ("P", "p", 46, ""),
            ("R", "r", 49, ""),
            ("S", "s", 52, ""),
        ]
    );
    assert!(kinds("x = (\n").is_none());
    assert!(kinds("class Q:\n").unwrap().is_empty());
    assert!(kinds("class Q:\nx = 1\n").unwrap().is_empty());
}
