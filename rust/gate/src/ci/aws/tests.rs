//! The adapter, driven through a fake `aws` at the process boundary; whether the real CLI answers so is the first paid run's to prove.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::super::fixtures::{scratch, secrets};
use super::{error_code, Aws, AwsError, CliAws};

/// A fake `aws` running `body`, its arguments logged to `calls`.
fn fake(dir: &Path, body: &str) -> CliAws {
    let path = dir.join("aws");
    crate::write_executable(&path, &format!("#!/bin/bash\necho \"$AWS_ACCESS_KEY_ID $AWS_DEFAULT_REGION $*\" >> \"{}/calls\"\n{body}\n", dir.display()));
    CliAws {
        program: path,
        secrets: secrets(),
    }
}

fn calls(dir: &Path) -> String {
    std::fs::read_to_string(dir.join("calls")).unwrap_or_default()
}

const DENIED: &str = "echo 'An error occurred (AccessDeniedException) when calling the StartBuild operation: no' >&2; exit 254";

#[test]
fn a_build_is_started_with_the_request_as_input_and_the_credentials_in_its_environment() {
    let dir = scratch("start");
    let client = fake(&dir, "echo '{\"build\": {\"id\": \"p:1\"}}'");
    let got = client.start_build(&json!({"projectName": "p"})).unwrap();
    assert_eq!(got["build"]["id"], "p:1");
    let log = calls(&dir);
    assert!(log.starts_with("AK us-east-1 codebuild start-build --cli-input-json {\"projectName\":\"p\"} --output json"), "{log}");
}

#[test]
fn a_denial_carries_its_operation_and_anything_else_is_its_text() {
    let dir = scratch("deny");
    let denied = fake(&dir, DENIED).start_build(&json!({})).unwrap_err();
    assert_eq!(denied, AwsError::Denied { operation: "codebuild:StartBuild".to_owned(), message: "An error occurred (AccessDeniedException) when calling the StartBuild operation: no".to_owned() });
    assert!(denied.text().contains("no"));
    let other = fake(&dir, "echo throttled >&2; exit 1")
        .stop_build("x")
        .unwrap_err();
    assert_eq!(other, AwsError::Other("throttled".to_owned()));
    assert_eq!(error_code("nothing here"), "");
    assert!(fake(&dir, "echo not json").batch_get_builds("x").is_err());
}

#[test]
fn a_missing_program_says_how_to_install_it() {
    let client = CliAws {
        program: PathBuf::from("/no/such/aws"),
        secrets: secrets(),
    };
    assert!(client
        .stop_build("x")
        .unwrap_err()
        .text()
        .contains("setup-dev-env.sh"));
}

#[test]
fn the_build_and_log_calls_name_what_the_api_names() {
    let dir = scratch("names");
    let client = fake(&dir, "echo '{\"events\": [], \"nextForwardToken\": \"n\"}'");
    client.batch_get_builds("p:1").unwrap();
    client.stop_build("p:1").unwrap();
    client.get_log_events("g", "s", None).unwrap();
    client.get_log_events("g", "s", Some("tok")).unwrap();
    let log = calls(&dir);
    assert!(
        log.contains("codebuild batch-get-builds --ids p:1")
            && log.contains("codebuild stop-build --id p:1")
    );
    assert!(log.contains("logs get-log-events --log-group-name g --log-stream-name s --start-from-head --output json") && log.contains("--start-from-head --next-token tok"));
}

#[test]
fn a_stream_that_does_not_exist_yet_is_an_empty_page() {
    let dir = scratch("stream");
    let client = fake(
        &dir,
        "echo 'An error occurred (ResourceNotFoundException) when calling' >&2; exit 254",
    );
    assert_eq!(
        client.get_log_events("g", "s", Some("t")).unwrap(),
        json!({"events": [], "nextForwardToken": "t"})
    );
    assert!(fake(&dir, DENIED).get_log_events("g", "s", None).is_err());
    assert!(fake(&dir, "echo not json")
        .get_log_events("g", "s", None)
        .is_err());
}

#[test]
fn an_object_goes_up_from_a_file_and_comes_back_from_one() {
    let dir = scratch("s3");
    let up = fake(&dir, "for a; do last=\"$p\"; p=\"$a\"; done; [ \"$1\" = s3api ] && cat \"$(echo \"$@\" | sed 's/.*--body //; s/ .*//')\" > \"$(dirname \"$0\")/got\"");
    up.put_object("b", "go/1", b"go").unwrap();
    assert_eq!(std::fs::read(dir.join("got")).unwrap(), b"go");
    assert!(calls(&dir).contains("s3api put-object --bucket b --key go/1 --body "));
    let down = fake(&dir, "echo data > \"$7\"; echo '{}'");
    assert_eq!(down.get_object("b", "k").unwrap(), Some(b"data\n".to_vec()));
    assert!(fake(&dir, "exit 1").put_object("b", "k", b"x").is_err());
}

#[test]
fn a_missing_object_is_none_and_a_real_failure_is_an_error() {
    let dir = scratch("miss");
    for code in ["NoSuchKey", "404"] {
        let client = fake(
            &dir,
            &format!("echo 'An error occurred ({code}) when calling' >&2; exit 254"),
        );
        assert_eq!(client.get_object("b", "k").unwrap(), None);
    }
    assert!(fake(&dir, DENIED).get_object("b", "k").is_err());
}

#[test]
fn a_listing_may_be_empty_output_and_a_delete_is_a_call() {
    let dir = scratch("list");
    assert_eq!(
        fake(&dir, "true").list_prefix("b", "p/").unwrap(),
        Vec::<String>::new()
    );
    assert_eq!(
        fake(
            &dir,
            "echo '{\"Contents\": [{\"Key\": \"p/a\"}, {\"Key\": \"p/b\"}]}'"
        )
        .list_prefix("b", "p/")
        .unwrap(),
        ["p/a", "p/b"]
    );
    assert!(fake(&dir, "echo oops").list_prefix("b", "p/").is_err());
    fake(&dir, "true").delete_object("b", "k").unwrap();
    assert!(calls(&dir).contains("s3api delete-object --bucket b --key k"));
    assert!(calls(&dir).contains("s3api list-objects-v2 --bucket b --prefix p/"));
}
