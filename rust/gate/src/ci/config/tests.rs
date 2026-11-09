//! The constants pinned, and where the secrets come from.

use super::super::fixtures::{put, scratch};
use super::{estimate_minutes, ini, load_secrets, rate_of, COMPUTE_TYPE, RATE_PER_MIN};

#[test]
fn the_rate_is_pinned_so_that_changing_it_is_deliberate() {
    assert!((RATE_PER_MIN - 0.02).abs() < f64::EPSILON);
    assert_eq!(COMPUTE_TYPE, "BUILD_GENERAL1_LARGE");
    assert!((rate_of("BUILD_GENERAL1_2XLARGE") - 0.20).abs() < f64::EPSILON);
    assert!((rate_of("unknown") - RATE_PER_MIN).abs() < f64::EPSILON);
    assert!(
        (estimate_minutes("full") - 8.0).abs() < f64::EPSILON
            && (estimate_minutes("reference") - 10.0).abs() < f64::EPSILON
    );
}

#[test]
fn the_ini_form_is_read_as_configparser_reads_it() {
    let parsed = ini("# a comment\n; another\n\n[aws]\nRegion = eu\nkey: v = w\nnot a pair\n");
    assert_eq!(parsed["aws"]["region"], "eu");
    assert_eq!(parsed["aws"]["key"], "v = w");
}

#[test]
fn the_tree_s_file_is_read_with_defaults_and_a_missing_one_names_every_place() {
    let dir = scratch("secrets");
    if let Err(refused) = load_secrets(&dir) {
        assert!(
            refused.contains("development-secrets.ini")
                && refused.contains(&dir.display().to_string())
        );
    }
    put(
        &dir,
        "development-secrets.ini",
        "[aws]\naccess_key_id = AK\n[github]\ncodebuild_pat = P\n",
    );
    assert_eq!(super::github_token(&dir).stdout, "P\n");
    let s = load_secrets(&dir).unwrap();
    assert_eq!(
        (
            s.access_key_id.as_str(),
            s.github_pat.as_str(),
            s.region.as_str(),
            s.log_group.as_str()
        ),
        ("AK", "P", "us-east-1", "/aws/codebuild/gm-assistant")
    );
}

#[test]
fn a_clone_finds_the_main_tree_s_file() {
    let main = scratch("main");
    put(
        &main,
        "development-secrets.ini",
        "[aws]\nci_bucket = main-bucket\n",
    );
    let clone = main.join(".clones/c");
    std::fs::create_dir_all(&clone).unwrap();
    assert_eq!(load_secrets(&clone).unwrap().ci_bucket, "main-bucket");
}

#[test]
fn a_tree_with_no_secrets_answers_nothing_to_the_push() {
    if std::path::Path::new("/host-l7r-repo/gm-assistant/webapp/development-secrets.ini").is_file()
    {
        return;
    }
    assert_eq!(super::github_token(&scratch("none")).code, 1);
}
