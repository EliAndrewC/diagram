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
