//! The constants pinned, and where the secrets come from.

use super::super::fixtures::{put, scratch};
use std::path::PathBuf;

use super::{candidates, ini, load_from, load_secrets};

#[test]
fn the_ini_form_is_read_as_configparser_reads_it() {
    let parsed = ini("# a comment\n; another\n\n[aws]\nRegion = eu\nkey: v = w\nnot a pair\n");
    assert_eq!(parsed["aws"]["region"], "eu");
    assert_eq!(parsed["aws"]["key"], "v = w");
}

#[test]
fn the_tree_s_file_is_read_with_defaults_and_a_missing_one_names_every_place() {
    let dir = scratch("secrets");
    let place = [dir.join("development-secrets.ini")];
    let refused = load_from(&place).unwrap_err();
    assert!(
        refused.contains(&dir.display().to_string())
            && refused.contains("copy development-secrets.ini.example")
    );
    put(
        &dir,
        "development-secrets.ini",
        "[aws]\naccess_key_id = AK\n[github]\ncodebuild_pat = P\n",
    );
    assert_eq!(super::github_token(&dir).stdout, "P\n");
    assert_eq!(load_from(&place).unwrap().github_pat, "P");
}

#[test]
fn the_environment_s_file_comes_first_and_an_empty_one_is_none() {
    let dir = scratch("env");
    assert_eq!(
        candidates(&dir, Some(PathBuf::from("/x")))[0],
        PathBuf::from("/x")
    );
    assert_eq!(
        candidates(&dir, Some(PathBuf::new()))[0],
        dir.join("development-secrets.ini")
    );
}

#[test]
fn a_clone_finds_the_main_tree_s_file() {
    let main = scratch("main");
    put(
        &main,
        "development-secrets.ini",
        "[github]\ncodebuild_pat = main-token\n",
    );
    let clone = main.join(".clones/c");
    std::fs::create_dir_all(&clone).unwrap();
    assert_eq!(load_secrets(&clone).unwrap().github_pat, "main-token");
}

#[test]
fn no_secrets_is_a_failure_with_its_reason() {
    assert_eq!(super::token_reply(Err("why".to_owned())).code, 1);
}

#[test]
fn a_file_with_neither_section_loads_empty_and_the_environment_comes_first_over_the_tree() {
    let dir = scratch("empty");
    put(&dir, "s.ini", "# nothing\n");
    let places = [dir.join("s.ini")];
    let s = load_from(&places).unwrap();
    assert_eq!(s.github_pat, "");
    put(
        &dir,
        "development-secrets.ini",
        "[github]\ncodebuild_pat = tree\n",
    );
    put(&dir, "first.ini", "[github]\ncodebuild_pat = env\n");
    assert_eq!(
        load_from(&candidates(&dir, Some(dir.join("first.ini"))))
            .unwrap()
            .github_pat,
        "env"
    );
}
