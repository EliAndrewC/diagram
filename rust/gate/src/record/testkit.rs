//! A record on a scratch git repository, for the owed tools' tests: the questions, a write-up, the pop-ups and the Python seams' stubs.

use std::path::{Path, PathBuf};
use std::process::Command;

pub(crate) fn git(dir: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

pub(crate) fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

pub(crate) fn commit(root: &Path, msg: &str) -> String {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", msg, "--allow-empty"]);
    git(root, &["rev-parse", "HEAD"])
}

pub(crate) const PAGE: &str = "research/questions/0094-trade.html";
pub(crate) const NOTES: &str = "research/questions/0094-trade.notes.html";
pub(crate) const DRAWING: &str = "research/questions/0094-trade.drawing.html";
pub(crate) const WELL: &str = "l7r/diagram/interactive/assets/modals/hamlet/well.md";

const ENTRY_STUB: &str = "import json\nfrom pathlib import Path\n\ndef owed(root):\n    f = Path(root) / 'entry-lines.json'\n    if (Path(root) / 'entry-noise').exists():\n        print('noise')\n    if (Path(root) / 'entry-raise').exists():\n        raise ImportError('no engine here')\n    return 'stub', json.loads(f.read_text()) if f.exists() else []\n";
const QV_STUB: &str = "import re\n\ndef _strip(body):\n    return re.sub('<[^>]+>', '', body)\n\ndef passages(text):\n    return [{'quote': q, 'original': o, 'language': 'ja', **({'more': ['x']} if o == 'more' else {})} for q, o in re.findall(r'\"([^\"]+)\" *\\u300c([^\\u300d]+)\\u300d', text)] + [{'quote': 'plain'}]\n";
const SP_STUB: &str = "import re\n\ndef glosses(html):\n    return re.findall(r'(\\S)\\(([a-z]+), \"([^\"]+)\"\\)', html)\n";
const AE_STUB: &str = "def reply_of(path):\n    return path.read_text()\n";

/// A repository holding a small record, committed once and set as origin/main; the stubs of every Python seam under `scripts/record/`.
pub(crate) fn record(tag: &str) -> PathBuf {
    record_at(&crate::checks::scratch(tag))
}

/// [`record`], at `root`.
pub(crate) fn record_at(root: &Path) -> PathBuf {
    let root = root.to_path_buf();
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q"]);
    git(&root, &["config", "user.email", "t@example.org"]);
    git(&root, &["config", "user.name", "t"]);
    git(&root, &["config", "commit.gpgsign", "false"]);
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
    put(&root, "l7r/diagram/interactive/classes/__init__.py", "");
    put(&root, "l7r/diagram/interactive/classes/homestead.py", "class Well(Kind):\n    \"\"\"About: docstring well\"\"\"\n    key = \"well\"\n\n\nclass Barn(Kind):\n    \"\"\"About: a barn from its docstring\n    Entry: research/questions/0095-other.html\n    \"\"\"\n    key = \"barn\"\n\n\nclass Shed(Kind):\n    \"\"\"Name: no About here\"\"\"\n    key = \"shed\"\n\n\nclass Blank(Kind):\n    key = \"blank\"\n");
    put(
        &root,
        "l7r/diagram/interactive/compound_kinds/office.py",
        "class Well(Kind):\n    key = \"well\"\n",
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
    stubs(&root);
    let base = commit(&root, "base");
    git(&root, &["update-ref", "refs/remotes/origin/main", &base]);
    root
}

/// The stubs of every Python seam, under `scripts/record/`.
pub(crate) fn stubs(root: &Path) {
    put(root, "scripts/record/entry_owed.py", ENTRY_STUB);
    put(root, "scripts/record/quote_verbatim.py", QV_STUB);
    put(root, "scripts/record/style_prepass.py", SP_STUB);
    put(root, "scripts/record/apply_edits.py", AE_STUB);
}

/// Every kind of edit the owed rules read, in the working tree.
pub(crate) fn edit_everything(root: &Path) {
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
