//! A record on a scratch git repository, for the owed tools' tests: the questions, a write-up and the pop-ups.

use std::path::{Path, PathBuf};
use std::process::Command;

/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
#[expect(
    clippy::must_use_candidate,
    reason = "a fixture runs git for what it does; most callers drop what it printed"
)]
pub fn git(dir: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

#[expect(
    clippy::must_use_candidate,
    reason = "a fixture commits for what it does; most callers drop the commit it names"
)]
pub fn commit(root: &Path, msg: &str) -> String {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", msg, "--allow-empty"]);
    git(root, &["rev-parse", "HEAD"])
}

pub const PAGE: &str = "research/questions/0094-trade.html";
pub const NOTES: &str = "research/questions/0094-trade.notes.html";
pub const DRAWING: &str = "research/questions/0094-trade.drawing.html";
pub const WELL: &str = "l7r/diagram/interactive/assets/modals/hamlet/well.md";

/// A repository holding a small record, committed once and set as origin/main.
pub fn record(tag: &str) -> crate::checks::TempDir {
    let dir = crate::checks::scratch(tag);
    let _ = record_at(&dir);
    dir
}

/// [`record`], at `root`.
#[must_use]
///
/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn record_at(root: &Path) -> PathBuf {
    let root = root.to_path_buf();
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q"]);
    // the identity written into the repository's config file, not by three `git config` runs: a git process costs 2-3 ms here, and
    // FR-008 holds each owed test to a tenth of a second (feature 449 T164)
    let config = root.join(".git/config");
    let mut text = std::fs::read_to_string(&config).unwrap();
    text.push_str("[user]\n\temail = t@example.org\n\tname = t\n[commit]\n\tgpgsign = false\n");
    std::fs::write(&config, text).unwrap();
    put(&root, PAGE, "<h2 id=\"t\">Trade</h2>\n<p class=\"intro\">Why it is asked.</p>\n<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>An unmarked claim.</p>\n");
    put(&root, NOTES, "<ol>\n<li data-note=\"k\">\"a passage\" <a href=\"https://e.org/a\"><code>key-a</code></a></li>\n<li data-note=\"t\">\"the hedge\" \u{300c}\u{57a3}\u{6839}\u{300d} (translated)<span class=\"orig\" data-orig=\"o1\"></span></li>\n<li data-note=\"z\">no publicly readable source</li>\n</ol>\n");
    put(
        &root,
        "research/questions/0094-trade.originals.html",
        "<ol><li data-orig=\"o1\">\u{300c}\u{57a3}\u{6839}\u{306e}\u{5916}\u{300d}</li></ol>\n",
    );
    put(
        &root,
        DRAWING,
        "<h2>How drawn</h2>\n<p>Drawn as a line.<sup class=\"fn\" data-note=\"d\"></sup></p>\n",
    );
    put(
        &root,
        "research/questions/0095-other.html",
        "<h2>Other</h2>\n<p class=\"intro\">Old intro.</p>\n<p>Body.</p>\n",
    );
    put(
        &root,
        "research/sources/010-works-cited/0001-key-a.html",
        "<p>Write-up A.</p>\n",
    );
    put(
        &root,
        "research/sources/010-works-cited/README.md",
        "not a write-up\n",
    );
    // an engine module, the one `.py` the claims walk of a scratch record reads (the class modules were it before feature 449 T149)
    put(&root, "l7r/diagram/m.py", "ROUND_CAP = 12\n");
    // the kinds are the registry's (feature 449 T149): a kind is a real key with its modal file, and no class carries a docstring
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/hamlet/notice-board.md",
        "About: a notice board from its file\nEntry: research/questions/0095-other.html\n",
    );
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/hamlet/wood-shed.md",
        "Name: no About here\n",
    );
    put(&root, WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/sheet/well.md",
        "Name: Sheet well\nAbout: A sheet's well.\nEntry: research/questions/0095-other.html\n",
    );
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/choice/bamboo--both.md",
        "Name: Bamboo\nAbout: Both kinds.\nDrawing: research/questions/0094-trade.drawing.html\n",
    );
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/choice/plain.md",
        "No tags at all.\n",
    );
    let base = commit(&root, "base");
    // origin/main as a loose ref written by hand, which is all `update-ref` writes in a fresh repository of git's default `files` ref
    // backend (feature 449 T164, as above)
    put(&root, ".git/refs/remotes/origin/main", &format!("{base}\n"));
    root
}

/// Every kind of edit the owed rules read, in the working tree.
pub fn edit_everything(root: &Path) {
    put(root, PAGE, "<h2 id=\"t\">Trade routes</h2>\n<p class=\"intro\">Why it is asked now.</p>\n<p>A short distance apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>\n<p>An unmarked claim, reworded.</p>\n<p><!-- c --></p>\n");
    put(root, NOTES, "<ol>\n<li data-note=\"k\">\"a passage\" <a href=\"https://e.org/b\"><code>key-a</code></a></li>\n<li data-note=\"t\">\"the hedges\" \u{300c}\u{57a3}\u{6839}\u{300d} (translated)<span class=\"orig\" data-orig=\"o1\"></span></li>\n<li data-note=\"z\">no publicly readable source, still</li>\n<li data-note=\"n\">\"new\" \u{300c}more\u{300d} <a href=\"https://e.org/n\"><code>key-b</code></a> \u{6728}(ki, \"tree\")</li>\n</ol>\n");
    put(root, DRAWING, "<h2>How drawn</h2>\n<p>Drawn as a line, thin.<sup class=\"fn\" data-note=\"d\"></sup></p>\n");
    put(
        root,
        "research/questions/0095-other.html",
        "<h2>Other</h2>\n<p>Body.</p>\n",
    );
    put(
        root,
        "research/sources/010-works-cited/0001-key-a.html",
        "<p>Write-up A, revised.</p>\n",
    );
    put(
        root,
        "research/sources/040-uncited-works/20501-key-c.html",
        "<p>New.</p>\n",
    );
    put(root, "l7r/diagram/interactive/assets/modals/sheet/well.md", "Name: Sheet well\nAbout: A sheet's well, changed.\nEntry: research/questions/0095-other.html\n");
}
