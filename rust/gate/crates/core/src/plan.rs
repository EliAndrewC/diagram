//! What the plan gates share with the rest of the gate (feature 449 T066, from `plan.rs`, split out by T92): a record file's JSON, and
//! git's one line.

use std::path::Path;
use std::process::Command;

use serde_json::Value;

/// A value as the record files write it: one-space indent, a final newline.
#[must_use]
pub fn pretty(value: &Value) -> String {
    use serde::Serialize as _;
    let mut out = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(
        &mut out,
        serde_json::ser::PrettyFormatter::with_indent(b" "),
    );
    let _ = value.serialize(&mut writer);
    String::from_utf8_lossy(&out).into_owned() + "\n"
}

/// `git <args>`'s stdout, trimmed; empty where git cannot start.
#[must_use]
pub fn git_line(root: &Path, args: &[&str]) -> String {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    done.map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{git_line, pretty};

    #[test]
    fn a_record_is_written_one_space_deep_and_git_answers_one_line() {
        assert_eq!(pretty(&json!({"a": [1]})), "{\n \"a\": [\n  1\n ]\n}\n");
        assert!(git_line(std::path::Path::new("."), &["--version"]).starts_with("git version"));
    }
}
