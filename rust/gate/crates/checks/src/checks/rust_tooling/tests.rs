//! Every reader of source and every Python-only recipe has its row.

use super::super::tests::{commit, put, repo};
use super::{cli, fnmatches, keys, problems, tool_targets, unproven, INVENTORY};

const ROW: &str = "| check | today | rust | fate | keys |\n|---|---|---|---|---|\n";

fn say(dir: &std::path::Path) -> Vec<String> {
    problems(dir)
}

/// One repository for every kind (feature 449 T167: a repository and two commits a kind took 230 ms against FR-008's tenth of a
/// second). The check lists the index (`ls-files`) and reads each listed file from disk, and the inventory under `dev/` is never a
/// reader, so `scripts/x.py` staged once is what each kind's two commits gave it: each kind is its text written there, its row added
/// and taken away again.
#[test]
fn a_reader_of_each_kind_with_no_row_fails_and_a_row_clears_it() {
    let dir = repo("reader");
    put(&dir, "scripts/x.py", "");
    put(&dir, INVENTORY, "");
    commit(&dir);
    for text in [
        "import ast\n",
        "from tokenize import x\n",
        "glob('*.py')\n",
        "p.endswith('.py')\n",
        "p.suffix == '.rs'\n",
        "code = compile(src, 'x', 'exec')\n",
        "find . -name '*.py'\n",
        "p.suffix == '.py'\n",
    ] {
        let _ = std::fs::remove_file(dir.join(INVENTORY));
        put(&dir, "scripts/x.py", text);
        assert_eq!(say(&dir).len(), 1, "{text}");
        put(
            &dir,
            INVENTORY,
            &format!("{ROW}| a | b | c | dropped | `scripts/x.py` |\n"),
        );
        assert_eq!(say(&dir), Vec::<String>::new(), "{text}");
    }
}

#[test]
fn a_dotted_compile_a_mention_in_specs_and_another_kind_of_file_are_not_readers() {
    let dir = repo("not");
    put(
        &dir,
        "scripts/x.py",
        "R = re.compile('x')\nthing.compile('x')\n",
    );
    put(&dir, "specs/1/y.py", "import ast\n");
    put(&dir, "scripts/z.txt", "import ast\n");
    commit(&dir);
    assert_eq!(say(&dir), Vec::<String>::new());
}

#[test]
fn a_glob_row_names_what_it_matches() {
    assert!(
        fnmatches("scripts/a/b.py", "scripts/*")
            && fnmatches("ab", "a?")
            && !fnmatches("abc", "a?")
            && !fnmatches("x.py", "scripts/*")
            && fnmatches("a.b", "a.b")
            && !fnmatches("axb", "a.b")
    );
}

#[test]
fn a_make_recipe_running_a_python_or_rust_tool_needs_its_row() {
    assert_eq!(tool_targets("a:\n\tpython3 -m ruff x\nb:\n\techo hi\nc := 1\nd: ## help\n\tcargo test\n\ne:\n\tfind . -name '*.py'\n"), ["a", "d", "e"]);
    let dir = repo("make");
    put(&dir, "Makefile", "lint:\n\truff check\n");
    commit(&dir);
    assert_eq!(say(&dir), ["make lint: its recipe runs a Python-only or Rust tool, and no row of dev/rust-tooling.md names it"]);
    put(
        &dir,
        INVENTORY,
        &format!("{ROW}| a | b | c | dropped | `make lint` |\n"),
    );
    assert_eq!(say(&dir), Vec::<String>::new());
}

#[test]
fn the_keys_are_the_last_cell_s_backticks() {
    assert_eq!(
        keys(&format!(
            "{ROW}| `a` | b | c | d | `x` and `make y` |\nprose `z`\n"
        )),
        ["x", "make y"]
    );
}

#[test]
fn a_rust_phase_cannot_land_while_a_row_is_unproven() {
    let inventory = format!("{ROW}| one | b | c | one for one | `k` |\n| two | b | c | dropped | `l` |\n| row | proof |\n|---|---|\n| three | yes |\n");
    assert_eq!(unproven(&inventory), ["one"]);
    assert_eq!(
        unproven(&format!("{inventory}| one | yes |\n")),
        Vec::<String>::new()
    );
    let dir = repo("phase");
    put(&dir, INVENTORY, &inventory);
    assert_eq!(say(&dir), Vec::<String>::new());
    put(&dir, "rust/a.rs", "fn f() {}\n");
    commit(&dir);
    assert!(say(&dir)[0].contains("the row `one` of dev/rust-tooling.md is not proven"));
}

#[test]
fn no_inventory_names_nothing_and_the_command_line_says_how_to_add_a_row() {
    let dir = repo("cli");
    assert!(cli(&[], &dir)
        .stdout
        .contains("every Python-only check has its row"));
    put(&dir, "scripts/x.py", "import ast\n");
    commit(&dir);
    let refused = cli(
        &["--root".to_owned(), dir.display().to_string()],
        std::path::Path::new("/nowhere"),
    );
    assert_eq!(refused.code, 1);
    assert!(
        refused.stderr.contains("scripts/x.py: reads")
            && refused.stderr.contains("add a row to dev/rust-tooling.md")
    );
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the check's detector over the live repository's tracked files, which must find
/// a real reader of Python source (`scripts/gates/codeid.py`); its time grows with the tree, held by SC-003's suite total, not the bar.
#[test]
fn the_detector_finds_a_real_reader_on_the_real_tree() {
    let real = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let listed = super::super::git_text(&real, &["ls-files"]);
    let files: Vec<&str> = listed.split_whitespace().collect();
    assert!(super::readers(&real, &files)
        .iter()
        .any(|f| f == "scripts/gates/codeid.py"));
}
