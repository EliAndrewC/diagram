//! The repository reads and the Python seam.

use std::path::Path;

use super::{cat_blobs, git, git_show, python, read_text, read_universal, universal, utc_now};
use crate::record::testkit::{record, PAGE};

#[test]
fn git_reads() {
    let root = record("repo-reads");
    assert!(git(&root, &["rev-parse", "HEAD"]).len() > 30);
    assert_eq!(git(&root, &["no-such-command"]), "");
    assert!(git_show(&root, "HEAD", PAGE).is_some());
    assert!(git_show(&root, "HEAD", "none").is_none());
    assert!(git_show(Path::new("/nonexistent/x"), "HEAD", "none").is_none());
    let got = cat_blobs(
        &root,
        &[
            format!("HEAD:{PAGE}"),
            "HEAD:none".to_owned(),
            "HEAD:research/questions/0095-other.html".to_owned(),
        ],
    );
    assert!(got[0].contains("Trade") && got[1].is_empty() && got[2].contains("Other"));
    assert!(cat_blobs(&root, &[]).is_empty());
    assert_eq!(
        cat_blobs(Path::new("/nonexistent/x"), &["HEAD:a".to_owned()]),
        [String::new()]
    );
}

#[test]
fn files_and_the_seam() {
    let root = record("repo-files");
    assert_eq!(universal("a\r\nb\rc"), "a\nb\nc");
    std::fs::write(root.join("crlf.txt"), "a\r\nb").unwrap();
    assert_eq!(read_text(&root.join("crlf.txt")).unwrap(), "a\nb");
    assert!(read_text(&root.join("none")).is_err());
    assert_eq!(read_universal(&root.join("none")).unwrap(), None);
    std::fs::write(root.join("bad.txt"), [0xff, 0xfe]).unwrap();
    assert!(read_universal(&root.join("bad.txt")).is_err());
    assert_eq!(
        python(
            "import sys; print(sys.stdin.read() + sys.argv[1])",
            &["x"],
            "in"
        )
        .unwrap(),
        "inx\n"
    );
    assert!(python("raise SystemExit('said')", &[], "")
        .unwrap_err()
        .contains("said"));
    assert_eq!(utc_now().len(), 20);
}
