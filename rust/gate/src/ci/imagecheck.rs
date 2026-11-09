//! Is the pushed `CodeBuild` image still built from the tree's current recipe? (feature 175, from `ci/imagecheck.py`). The image is a derived artifact with no link back to its files, so this warns, naming them; it never
//! refuses, since rebuilding costs money on a prompted target that is the GM's to authorize.

/// What the image is built from: the recipe and the two lockfiles it copies.
pub(crate) const IMAGE_INPUTS: [&str; 3] =
    ["Dockerfile.ci", "requirements.txt", "requirements-dev.txt"];

/// The commit the pushed image was built from; a malformed marker is unknown, never an error, because this is a diagnostic.
pub(crate) fn marker_commit(marker: &str) -> Option<String> {
    let sha = marker.split_whitespace().next()?;
    (sha.len() >= 7 && sha.chars().all(|c| c.is_ascii_hexdigit())).then(|| sha.to_owned())
}

/// The one line a session should see, or None when the image is current.
pub(crate) fn staleness_line(changed: &str) -> Option<String> {
    let mut stale: Vec<&str> = changed
        .split_whitespace()
        .filter(|p| IMAGE_INPUTS.contains(p))
        .collect();
    stale.sort_unstable();
    stale.dedup();
    (!stale.is_empty()).then(|| format!("image STALE: {} changed since the image was built - `make ci-image` rebuilds it (~$0.16, prompts). A build may fail on a tool the tree expects and the image lacks.", stale.join(", ")))
}

#[cfg(test)]
mod tests {
    use super::{marker_commit, staleness_line};

    #[test]
    fn a_marker_names_its_commit_or_nothing() {
        assert_eq!(
            marker_commit("abc1234 2026-01-01"),
            Some("abc1234".to_owned())
        );
        assert_eq!(marker_commit(""), None);
        assert_eq!(marker_commit("short 1"), None);
        assert_eq!(marker_commit("nothexxx 1"), None);
    }

    #[test]
    fn only_the_image_s_inputs_make_it_stale() {
        assert_eq!(staleness_line("docs/a.md\nl7r/x.py\n"), None);
        let line = staleness_line("requirements.txt Dockerfile.ci requirements.txt").unwrap();
        assert!(line.starts_with("image STALE: Dockerfile.ci, requirements.txt changed"));
    }
}
