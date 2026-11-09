//! What the remote path reads of the repository as it is: the buildspecs the dispatcher passes whole, the recipe the image is built from, the example secrets file and the make targets. These are not fixtures, since the point
//! of each is that two files of the real tree agree (features 175 and 177).

use std::path::{Path, PathBuf};

use super::{cachepolicy, config, imagecheck};

const FRESHNESS_PATHS: [&str; 2] = ["repo/.git/gate-green-hooks", "repo/.git/hooks-test/**/*"];

fn repo() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn read(rel: &str) -> String {
    std::fs::read_to_string(repo().join(rel)).unwrap()
}

/// The `paths:` of a buildspec's top-level `cache:` block.
fn cache_paths(text: &str) -> Vec<String> {
    let block = text.split_once("\ncache:\n").unwrap().1;
    let body = block
        .lines()
        .take_while(|l| l.is_empty() || l.starts_with([' ', '\t']));
    body.filter_map(|l| {
        l.trim()
            .strip_prefix("- '")
            .and_then(|r| r.strip_suffix('\''))
    })
    .map(str::to_owned)
    .collect()
}

fn specs() -> [String; 2] {
    [read("buildspec/check.yml"), read("buildspec/merge.yml")]
}

#[test]
fn the_two_buildspecs_cache_exactly_the_same_paths() {
    let [check, merge] = specs().map(|s| cache_paths(&s));
    assert_eq!(check, merge);
    assert!(!check.is_empty());
}

#[test]
fn the_raster_and_the_page_are_not_cached() {
    for spec in specs() {
        assert!(!cache_paths(&spec).iter().any(|p| Path::new(p)
            .extension()
            .is_some_and(|e| e == "png" || e == "html")));
    }
}

#[test]
fn the_cached_paths_are_what_a_hit_needs_and_exactly_those() {
    for spec in specs() {
        let paths = cache_paths(&spec);
        for needed in ["*.json", "*.svg", "coverage."] {
            assert!(paths.iter().any(|p| p.contains(needed)), "{needed}");
        }
        let extra: Vec<&String> = paths
            .iter()
            .filter(|p| !p.starts_with("repo/.gencache/"))
            .collect();
        assert_eq!(extra, FRESHNESS_PATHS);
    }
}

#[test]
fn the_restore_cannot_be_fooled_by_a_cache_that_contains_a_dot_git() {
    let run_sh = read("buildspec/run.sh");
    let code: String = run_sh
        .lines()
        .filter(|l| !l.trim_start().starts_with('#'))
        .collect::<Vec<_>>()
        .join("\n");
    assert!(code.contains("[ ! -e repo/.git/HEAD ]"));
    assert!(!code.contains("[ ! -d repo/.git ]"));
}

#[test]
fn the_freshness_state_is_content_keyed_so_a_changed_guard_still_runs() {
    assert!(read("Makefile").contains("deps --keys"));
}

#[test]
fn a_measurement_cannot_mint_a_push_credential() {
    let run_sh = read("buildspec/run.sh");
    let guard = run_sh.find("if [ \"$MODE\" = measure ]").unwrap();
    assert!(guard < run_sh.find("aws s3 cp --quiet /tmp/verified.json").unwrap());
    assert!(guard < run_sh.find("git push origin HEAD:main").unwrap());
    assert!(run_sh[guard..]
        .lines()
        .take(20)
        .any(|l| l.trim() == "exit 0"));
}

#[test]
fn the_measure_buildspec_matches_check_in_everything_but_its_mode() {
    let (check, measure) = (read("buildspec/check.yml"), read("buildspec/measure.yml"));
    assert!(measure.contains("MODE: measure") && !measure.contains("MODE: check"));
    assert_eq!(cache_paths(&measure), cache_paths(&check));
    assert!(
        measure.contains(FRESHNESS_PATHS[0])
            && measure.contains("--no-checkout")
            && measure.contains("buildspec/sparse-excludes.txt")
    );
}

#[test]
fn a_measurement_is_paid_and_prompted() {
    let makefile = read("Makefile");
    let body = makefile
        .split_once("\nci-measure:")
        .unwrap()
        .1
        .split_once("\nci-image:")
        .unwrap()
        .0;
    for needed in [
        "$(REMOTE_OK)",
        "Enter cancels",
        "$(LOGBYPASS) cancelled",
        "$(LOGBYPASS) permitted",
        "-t 0",
        "ci measure",
    ] {
        assert!(body.contains(needed), "{needed}");
    }
}

#[test]
fn the_input_list_matches_what_the_dockerfile_copies_and_each_exists() {
    let text = read("Dockerfile.ci");
    let copied = text
        .lines()
        .filter_map(|l| l.strip_prefix("COPY "))
        .flat_map(|l| {
            let words: Vec<&str> = l.split_whitespace().collect();
            words[..words.len() - 1].to_vec()
        });
    let missing: Vec<&str> = copied
        .filter(|p| !imagecheck::IMAGE_INPUTS.contains(p))
        .collect();
    assert_eq!(missing, Vec::<&str>::new());
    assert!(imagecheck::IMAGE_INPUTS
        .iter()
        .all(|p| repo().join(p).is_file()));
}

#[test]
fn the_example_secrets_file_names_every_key_the_reader_reads() {
    let example = config::ini(&read("development-secrets.ini.example"));
    for key in [
        "region",
        "access_key_id",
        "secret_access_key",
        "account_id",
        "ci_bucket",
        "ecr_image",
        "log_group",
    ] {
        assert!(example["aws"].contains_key(key), "{key}");
    }
    assert!(example["github"].contains_key("codebuild_pat"));
}

#[test]
fn the_lifecycle_document_s_reasons_stand_beside_it() {
    let source = include_str!("cachepolicy.rs");
    for needed in ["shortest", "expire-ci-junk", "no negative filter", "365"] {
        assert!(source.contains(needed), "{needed}");
    }
    let rules = cachepolicy::lifecycle_configuration();
    let days = |id: &str| {
        rules["Rules"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["ID"] == id)
            .unwrap()["Expiration"]["Days"]
            .as_i64()
            .unwrap()
    };
    let cache = days("expire-generation-cache");
    assert!(cache > 7 && cache <= 30);
    assert_eq!(days("expire-large-objects"), cache);
}
