//! Each form of a dependency on the guard refused, each form that is not one passed (feature 451 T66).

use super::{cli, guard_lines, section, shared_path, uncommented, Section};

fn put(dir: &std::path::Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

#[test]
fn every_form_of_a_dependency_on_the_guard_is_found() {
    for (text, lines) in [
        (
            "[dependencies]\nl7r_guard = { path = \"../guard\" }\n",
            vec![2],
        ),
        (
            "[dev-dependencies]\nl7r-guard = { path = \"../guard\" }\n",
            vec![2],
        ),
        (
            "[target.'cfg(target_os = \"a.b\")'.dependencies]\nl7r_guard.path = \"../guard\"\n",
            vec![2],
        ),
        (
            "[build-dependencies.l7r_guard]\npath = \"../guard\"\n",
            vec![1],
        ),
        (
            "[dependencies]\nhooks = { package = \"l7r_guard\", path = \"../guard\" }\n",
            vec![2],
        ),
        (
            "[dependencies.hooks]\npackage = 'l7r_guard'\npath = \"../guard\"\n",
            vec![2],
        ),
        (
            "[workspace.dependencies]\n\"l7r_guard\" = { path = \"guard\" }\n",
            vec![2],
        ),
        (
            "[dependencies]\nl7r_guard = { path = \"../gu#ard\" } # kept\n",
            vec![2],
        ),
    ] {
        assert_eq!(guard_lines(text), lines, "{text}");
    }
}

#[test]
fn a_name_a_comment_a_feature_or_another_crate_is_no_dependency() {
    for text in [
        "[package]\nname = \"l7r_guard\"\n\n[lib]\nname = \"l7r_guard\"\n\n[[bin]]\nname = \"l7r-guard\"\n",
        "# the guard (`l7r-guard`) depends on it\n[dependencies]\n# l7r_guard = { path = \"../guard\" }\nserde = \"1\" # not l7r_guard\n",
        "[features]\nl7r_guard = []\n",
        "[dependencies]\nl7r_shared = { path = \"../guard/shared\" }\n\n[dependencies.serde]\nversion = \"1\"\n",
        "[dependencies]\nnote = \"a#b\"\n",
    ] {
        assert!(guard_lines(text).is_empty(), "{text}");
    }
}

#[test]
fn a_header_opens_its_section_and_a_comment_stops_outside_a_string() {
    assert_eq!(section("[dependencies]"), Section::Table);
    assert_eq!(section("[[bin]]"), Section::Other);
    assert_eq!(
        section("[dev-dependencies.x]"),
        Section::One("x".to_owned())
    );
    assert_eq!(uncommented("a = 'b#c' # d"), "a = 'b#c' ");
    assert_eq!(uncommented("a = \"b\""), "a = \"b\"");
}

#[test]
fn the_shared_path_is_named_from_the_crate() {
    assert_eq!(
        shared_path(std::path::Path::new("rust/gate/crates/x/Cargo.toml")),
        "../../../guard/shared"
    );
    assert_eq!(
        shared_path(std::path::Path::new("rust/mode_a/Cargo.toml")),
        "../guard/shared"
    );
    assert_eq!(
        shared_path(std::path::Path::new("rust/Cargo.toml")),
        "guard/shared"
    );
}

#[test]
fn the_guard_itself_a_target_and_a_hidden_directory_are_passed_and_the_root_defaults() {
    let empty = super::super::scratch("guard-deps-empty");
    assert!(cli(&[], &empty).stdout.contains("(0 manifests read)"));
    let tree = super::super::scratch("guard-deps-walk");
    let named = "[dev-dependencies]\nl7r_guard = { path = \".\", features = [\"x\"] }\n";
    put(&tree, "rust/guard/Cargo.toml", named);
    put(&tree, "rust/target/debug/x/Cargo.toml", named);
    put(&tree, "rust/.hidden/Cargo.toml", named);
    put(
        &tree,
        "rust/mode_a/Cargo.toml",
        "[package]\nname = \"l7r_mode_a\"\n",
    );
    put(&tree, "rust/mode_a/notes.txt", "l7r_guard = 1\n");
    let passed = cli(&[], &tree);
    assert_eq!(passed.code, 0, "{}", passed.stderr);
    assert!(
        passed.stdout.contains("(2 manifests read)"),
        "{}",
        passed.stdout
    );
    put(
        &tree,
        "rust/Cargo.toml",
        "[workspace.dependencies]\nl7r_guard = { path = \"guard\" }\n",
    );
    let refused = cli(&[], &tree);
    assert!(
        refused.code == 1
            && refused
                .stderr
                .contains("rust/Cargo.toml:2: names l7r_guard")
            && refused.stderr.contains("path = \"guard/shared\""),
        "{}",
        refused.stderr
    );
}
