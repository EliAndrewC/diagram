//! The AWS boundary (feature 449 T064, the round arbiter's `ask:449-T064-slices`): a small trait, with the `aws` CLI behind it. `buildspec/run.sh` already uses the CLI, and it speaks the same API under the same names; the
//! dispatcher's tests drive the adapter through a fake `aws` on the path. **The live adapter is unproven**: no paid run may prove it, and the first paid run after remote is turned on is its proof (`dev/rust-tooling.md`).

use std::path::PathBuf;
use std::process::Command;

use serde_json::{json, Value};

use super::config::Secrets;
use crate::codeid::{parsed, stated};

/// An AWS failure, with the operation it named when the service denied it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum AwsError {
    Denied { operation: String, message: String },
    Other(String),
}

impl AwsError {
    pub(crate) fn text(&self) -> String {
        match self {
            Self::Denied { message, .. } | Self::Other(message) => message.clone(),
        }
    }
}

pub(crate) trait Aws {
    fn start_build(&self, request: &Value) -> Result<Value, AwsError>;
    fn batch_get_builds(&self, id: &str) -> Result<Value, AwsError>;
    fn stop_build(&self, id: &str) -> Result<(), AwsError>;
    fn get_log_events(
        &self,
        group: &str,
        stream: &str,
        token: Option<&str>,
    ) -> Result<Value, AwsError>;
    fn put_object(&self, bucket: &str, key: &str, body: &[u8]) -> Result<(), AwsError>;
    fn get_object(&self, bucket: &str, key: &str) -> Result<Option<Vec<u8>>, AwsError>;
    fn list_prefix(&self, bucket: &str, prefix: &str) -> Result<Vec<String>, AwsError>;
    fn delete_object(&self, bucket: &str, key: &str) -> Result<(), AwsError>;
}

pub(crate) struct CliAws {
    pub program: PathBuf,
    pub secrets: Secrets,
}

/// The code in the CLI's `An error occurred (Code) when calling the Op operation: message`.
fn error_code(stderr: &str) -> &str {
    stderr
        .split_once("An error occurred (")
        .and_then(|(_, r)| r.split_once(')'))
        .map_or("", |(code, _)| code)
}

impl CliAws {
    fn run(&self, args: &[&str]) -> Result<String, String> {
        let done = Command::new(&self.program)
            .args(args)
            .args(["--output", "json"])
            .env("AWS_ACCESS_KEY_ID", &self.secrets.access_key_id)
            .env("AWS_SECRET_ACCESS_KEY", &self.secrets.secret_access_key)
            .env("AWS_DEFAULT_REGION", &self.secrets.region)
            .env("AWS_PAGER", "")
            .output();
        let done = stated(
            done,
            "the aws CLI (install it: scripts/container/setup-dev-env.sh)",
        )?;
        if done.status.success() {
            Ok(String::from_utf8_lossy(&done.stdout).into_owned())
        } else {
            Err(String::from_utf8_lossy(&done.stderr).trim().to_owned())
        }
    }

    /// A call whose denial names `operation`.
    fn call(&self, args: &[&str], operation: &str) -> Result<String, AwsError> {
        self.run(args).map_err(|message| {
            if error_code(&message) == "AccessDeniedException" {
                AwsError::Denied {
                    operation: operation.to_owned(),
                    message,
                }
            } else {
                AwsError::Other(message)
            }
        })
    }

    fn json(&self, args: &[&str], operation: &str) -> Result<Value, AwsError> {
        parsed(&self.call(args, operation)?, operation).map_err(AwsError::Other)
    }

    fn scratch() -> PathBuf {
        use std::sync::atomic::{AtomicUsize, Ordering};
        static SEQ: AtomicUsize = AtomicUsize::new(0);
        std::env::temp_dir().join(format!(
            "l7r-gate-aws-{}-{}",
            std::process::id(),
            SEQ.fetch_add(1, Ordering::Relaxed)
        ))
    }
}

impl Aws for CliAws {
    fn start_build(&self, request: &Value) -> Result<Value, AwsError> {
        self.json(
            &[
                "codebuild",
                "start-build",
                "--cli-input-json",
                &request.to_string(),
            ],
            "codebuild:StartBuild",
        )
    }

    fn batch_get_builds(&self, id: &str) -> Result<Value, AwsError> {
        self.json(
            &["codebuild", "batch-get-builds", "--ids", id],
            "codebuild:BatchGetBuilds",
        )
    }

    fn stop_build(&self, id: &str) -> Result<(), AwsError> {
        self.call(
            &["codebuild", "stop-build", "--id", id],
            "codebuild:StopBuild",
        )
        .map(|_| ())
    }

    fn get_log_events(
        &self,
        group: &str,
        stream: &str,
        token: Option<&str>,
    ) -> Result<Value, AwsError> {
        let mut args = vec![
            "logs",
            "get-log-events",
            "--log-group-name",
            group,
            "--log-stream-name",
            stream,
            "--start-from-head",
        ];
        if let Some(t) = token {
            args.extend(["--next-token", t]);
        }
        match self.call(&args, "logs:GetLogEvents") {
            Ok(text) => parsed(&text, "logs:GetLogEvents").map_err(AwsError::Other),
            // the stream does not exist until the build starts writing
            Err(e) if error_code(&e.text()) == "ResourceNotFoundException" => {
                Ok(json!({"events": [], "nextForwardToken": token}))
            }
            Err(e) => Err(e),
        }
    }

    fn put_object(&self, bucket: &str, key: &str, body: &[u8]) -> Result<(), AwsError> {
        let file = Self::scratch();
        stated(std::fs::write(&file, body), "a scratch file").map_err(AwsError::Other)?;
        let path = file.to_string_lossy().into_owned();
        let done = self.call(
            &[
                "s3api",
                "put-object",
                "--bucket",
                bucket,
                "--key",
                key,
                "--body",
                &path,
            ],
            "s3:PutObject",
        );
        let _ = std::fs::remove_file(&file);
        done.map(|_| ())
    }

    fn get_object(&self, bucket: &str, key: &str) -> Result<Option<Vec<u8>>, AwsError> {
        let file = Self::scratch();
        let path = file.to_string_lossy().into_owned();
        let done = self.call(
            &[
                "s3api",
                "get-object",
                "--bucket",
                bucket,
                "--key",
                key,
                &path,
            ],
            "s3:GetObject",
        );
        let body = std::fs::read(&file).ok();
        let _ = std::fs::remove_file(&file);
        match done {
            Ok(_) => Ok(body),
            Err(e) if ["NoSuchKey", "404"].contains(&error_code(&e.text())) => Ok(None),
            Err(e) => Err(e),
        }
    }

    fn list_prefix(&self, bucket: &str, prefix: &str) -> Result<Vec<String>, AwsError> {
        let text = self.call(
            &[
                "s3api",
                "list-objects-v2",
                "--bucket",
                bucket,
                "--prefix",
                prefix,
            ],
            "s3:ListBucket",
        )?;
        // the CLI prints nothing at all for an empty listing
        let listed = if text.trim().is_empty() {
            Value::Null
        } else {
            parsed(&text, "s3:ListBucket").map_err(AwsError::Other)?
        };
        Ok(listed["Contents"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|o| o["Key"].as_str().map(str::to_owned))
            .collect())
    }

    fn delete_object(&self, bucket: &str, key: &str) -> Result<(), AwsError> {
        self.call(
            &["s3api", "delete-object", "--bucket", bucket, "--key", key],
            "s3:DeleteObject",
        )
        .map(|_| ())
    }
}

#[cfg(test)]
mod tests;
