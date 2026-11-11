//! What a guard keeps between calls: a file a session under its state directory (`<DIR>/<session id>.<ext>`, the id made
//! file-safe as the shells' `${SID//[^A-Za-z0-9_-]/_}` made it), and a field of the hook input read as text.

use std::path::PathBuf;

use serde_json::Value;

/// `input[k]` as text, or "".
#[must_use]
pub fn field<'a>(input: &'a Value, k: &str) -> &'a str {
    input.get(k).and_then(Value::as_str).unwrap_or("")
}

/// This session's file `<dir>/<id>.<ext>` - `dir` the guard's `*_STATE_DIR` where set, else `default` - its directory made.
#[must_use]
pub fn session_file(input: &Value, dir: Option<String>, default: &str, ext: &str) -> PathBuf {
    let sid = Some(field(input, "session_id"))
        .filter(|s| !s.is_empty())
        .unwrap_or("nosession");
    let safe: String = sid
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '_' || c == '-' {
                c
            } else {
                '_'
            }
        })
        .collect();
    let dir = PathBuf::from(dir.unwrap_or_else(|| default.to_owned()));
    let _ = std::fs::create_dir_all(&dir);
    dir.join(format!("{safe}.{ext}"))
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{field, session_file};

    #[test]
    fn a_sessions_file_is_named_safely_in_its_directory() {
        let d = crate::shared::tempdir::TempDir::new("guard-state");
        assert_eq!(
            session_file(
                &json!({"session_id": "a/b c"}),
                Some(d.to_string_lossy().into_owned()),
                "/x",
                "subset"
            ),
            d.join("a_b_c.subset")
        );
        assert_eq!(
            session_file(&json!({}), None, "/tmp/l7r-guard-default", "m"),
            std::path::Path::new("/tmp/l7r-guard-default/nosession.m")
        );
        assert_eq!(
            (field(&json!({"k": "v"}), "k"), field(&json!({}), "k")),
            ("v", "")
        );
    }
}
