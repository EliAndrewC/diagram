//! The tests' world (feature 449 T146): a repository holding the research crate's test record under `research/`, laid out as a session
//! clone (`<d>/m/.clones/c`) so the archive's home is `<d>/m/.specify` with no variable set; the archive's working copy cloned from a
//! local bare repository there (never GitHub); the GM's downloads in `<d>/gm`; and a browser that answers from tables.

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_guard::shared::tempdir::TempDir;

use crate::fetch::{Client, Fetched};
use crate::store::Archive;

/// A minimal PDF whose text `pdftotext` reads as `Hello PDF`.
pub const PDF: &[u8] = b"%PDF-1.4\n1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj\n2 0 obj <</Type/Pages/Kids[3 0 R]/Count 1>> endobj\n\
3 0 obj <</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>> endobj\n\
4 0 obj <</Length 41>> stream\nBT /F1 12 Tf 20 100 Td (Hello PDF) Tj ET\nendstream endobj\n\
5 0 obj <</Type/Font/Subtype/Type1/BaseFont/Helvetica>> endobj\ntrailer <</Root 1 0 R>>\n%%EOF\n";

/// A browser answering from tables: each request's [`Fetched`] (a URL not in the table is a dead one) and each render.
#[derive(Default)]
pub struct Fake {
    pub gets: HashMap<String, Fetched>,
    pub renders: HashMap<String, (String, String)>,
    pub asked: Vec<String>,
}

impl Fake {
    /// A page served with this type and body.
    pub fn serve(&mut self, url: &str, status: i64, content_type: &str, body: &[u8]) {
        self.gets.insert(
            url.to_owned(),
            Fetched {
                url: url.to_owned(),
                status: Some(status),
                final_url: url.to_owned(),
                content_type: content_type.to_owned(),
                body: body.to_vec(),
                ..Fetched::default()
            },
        );
    }
}

impl Client for Fake {
    fn get(&mut self, url: &str) -> Fetched {
        self.asked.push(format!("get {url}"));
        self.gets
            .get(url)
            .cloned()
            .unwrap_or_else(|| Fetched::failed(url, "APIRequestContext.get: connect ECONNREFUSED"))
    }

    fn render(&mut self, url: &str) -> (String, String) {
        self.asked.push(format!("render {url}"));
        self.renders.get(url).cloned().unwrap_or_default()
    }
}

/// `git` in `dir`, its output; a failure fails the test.
///
/// # Panics
/// git fails.
#[cfg_attr(
    not(test),
    expect(
        clippy::must_use_candidate,
        reason = "its output read where a test wants it, its run where it does not"
    )
)]
pub fn git(dir: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8_lossy(&out.stdout).into_owned()
}

/// The tests' world.
pub struct World {
    pub dir: TempDir,
    pub root: PathBuf,
    pub home: PathBuf,
    pub remote: PathBuf,
    pub gm: PathBuf,
}

impl World {
    /// A new world, its working copy cloned from a bare remote with one commit.
    ///
    /// # Panics
    /// The world cannot be made.
    #[must_use]
    pub fn new(tag: &str) -> Self {
        let dir = TempDir::new(&format!("archive-{tag}"));
        let root = dir.path().join("m/.clones/c");
        for (rel, text) in l7r_gate_research::fixture::FILES {
            l7r_gate_research::fixture::put(&root.join("research"), rel, text);
        }
        std::fs::create_dir_all(root.join(".git")).unwrap();
        let home = dir.path().join("m/.specify");
        let remote = dir.path().join("remote.git");
        git(
            dir.path(),
            &[
                "init",
                "-q",
                "--bare",
                "-b",
                "main",
                remote.to_str().unwrap(),
            ],
        );
        let seed = dir.path().join("seed");
        git(
            dir.path(),
            &[
                "clone",
                "-q",
                remote.to_str().unwrap(),
                seed.to_str().unwrap(),
            ],
        );
        std::fs::write(seed.join("README"), "seed\n").unwrap();
        for args in [
            &["config", "user.name", "t"][..],
            &["config", "user.email", "t@t"],
            &["add", "-A"],
            &["commit", "-q", "-m", "seed"],
            &["push", "-q", "origin", "HEAD:main"],
        ] {
            git(&seed, args);
        }
        let gm = dir.path().join("gm");
        std::fs::create_dir_all(&gm).unwrap();
        let world = Self {
            dir,
            root,
            home,
            remote,
            gm,
        };
        world.clone_copy();
        world
    }

    /// The working copy cloned (again), its committer set.
    ///
    /// # Panics
    /// The clone fails.
    pub fn clone_copy(&self) {
        let wc = self.home.join("source-archive");
        let _ = std::fs::remove_dir_all(&wc);
        git(
            self.dir.path(),
            &[
                "clone",
                "-q",
                self.remote.to_str().unwrap(),
                wc.to_str().unwrap(),
            ],
        );
        git(&wc, &["config", "user.name", "diagram source archive"]);
        git(&wc, &["config", "user.email", "noreply@anthropic.com"]);
    }

    /// The store over the working copy: the process's environment, the local remote, the world's GM folder.
    #[must_use]
    pub fn store(&self) -> Archive {
        let mut a = Archive::new(&self.home, None);
        a.remote = self.remote.to_string_lossy().into_owned();
        a.gm.clone_from(&self.gm);
        a
    }

    /// The research record's directory.
    #[must_use]
    pub fn research(&self) -> PathBuf {
        self.root.join("research")
    }

    /// The archive's commit subjects, newest first.
    pub fn subjects(&self) -> Vec<String> {
        git(&self.home.join("source-archive"), &["log", "--format=%s"])
            .lines()
            .map(str::to_owned)
            .collect()
    }
}
