//! The tests' world (feature 449 T147): the archive crate's (a clone at `<d>/m/.clones/c` holding the research crate's test record, its
//! home `<d>/m/.specify`, the archive's working copy from a local bare remote), with its row given a URL, and helpers to put pages in
//! the cache, rows on the ledger and lines on the filter's lists; a browser answering from tables; a reservation that writes the stub.

use std::path::{Path, PathBuf};
use std::sync::Mutex;

use l7r_gate_archive::fetch::Client;
use l7r_gate_archive::testkit::{Fake, World};
use l7r_gate_research::pages::{put, Stored};
use serde_json::Value;

/// The world.
pub struct W {
    pub w: World,
}

impl W {
    pub fn new(tag: &str) -> Self {
        let w = World::new(&format!("uncited-{tag}"));
        let me = Self { w };
        // the research fixture's one row has no URL, which every reader of the rows refuses
        me.put("research/archive/a1/a1b2c3d4e5f6.json", r#"{"url": "https://e.org/a", "outcome": "archived", "keys": ["src-a"], "path": "a1/x"}"#);
        me
    }

    pub fn root(&self) -> &Path {
        &self.w.root
    }

    pub fn home(&self) -> &Path {
        &self.w.home
    }

    /// A file under the root.
    pub fn put(&self, rel: &str, text: &str) {
        let p = self.w.root.join(rel);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, text).unwrap();
    }

    /// A file's text under the root, "" where it is missing.
    pub fn read(&self, rel: &str) -> String {
        std::fs::read_to_string(self.w.root.join(rel)).unwrap_or_default()
    }

    /// A page in the cache, saved long ago, from `origin`.
    pub fn page(&self, url: &str, text: &str, origin: &str) {
        let how = Stored {
            fetched: Some("2026-01-01T00:00:00+00:00"),
            exact: true,
            origin,
        };
        put(&self.w.home, url, text, &how, &self.w.root.join("research")).unwrap();
    }

    /// Rows on the sources-consulted ledger.
    pub fn ledger(&self, rows: &[Value]) {
        let text: String = rows.iter().map(|r| r.to_string() + "\n").collect();
        std::fs::create_dir_all(&self.w.home).unwrap();
        std::fs::write(self.w.home.join("sources-consulted.jsonl"), text).unwrap();
    }

    /// Lines of one of the lists, whole.
    pub fn lines(&self, rel: &str, rows: &[Value]) {
        self.put(
            rel,
            &rows
                .iter()
                .map(|r| r.to_string() + "\n")
                .collect::<String>(),
        );
    }

    /// An uncited entry.
    pub fn uncited(&self, name: &str, text: &str) {
        self.put(&format!("research/sources/040-uncited-works/{name}"), text);
    }
}

/// A long text of `n` words beginning with `head`.
pub fn long(head: &str, n: usize) -> String {
    let mut t = format!("{head}\n");
    for i in 0..n {
        let _ = std::fmt::Write::write_fmt(&mut t, format_args!("word{i} "));
    }
    t
}

/// A browser start answering from `fake`'s tables, each start counted.
pub fn starter(
    fake: impl Fn() -> Fake + Sync,
) -> impl Fn(&Path) -> crate::Result<Box<dyn Client>> + Sync {
    move |_| Ok(Box::new(fake()) as Box<dyn Client>)
}

/// Where a line goes that no test reads.
pub fn quiet(_: &str) {}

/// A browser that will not start.
pub fn no_browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    Err(crate::Error::new("Error", "BrowserType.launch: none"))
}

/// The lines said, collected.
#[derive(Default)]
pub struct Said(pub Mutex<Vec<String>>);

impl Said {
    pub fn say(&self, l: &str) {
        self.0.lock().unwrap().push(l.to_owned());
    }

    pub fn all(&self) -> Vec<String> {
        self.0.lock().unwrap().clone()
    }
}

/// The reservation `record` hands in, stood in for: the next free number's stub under the uncited works, a key in `held` refused as
/// held elsewhere and `boom` as a failure of another kind.
pub fn reserve(key: &str, root: &Path, _url: &str) -> crate::Result<PathBuf> {
    if key == "held" {
        return Err(crate::Error::new(
            "Refusal",
            "KEY held is already reserved by another clone",
        ));
    }
    if key == "boom" {
        return Err(crate::Error::new("OSError", "disk full"));
    }
    let d = root.join("research/sources/040-uncited-works");
    std::fs::create_dir_all(&d).unwrap();
    let n = std::fs::read_dir(&d).unwrap().count() + 1;
    let p = d.join(format!("{:04}-{key}.html", 9000 + n));
    std::fs::write(&p, "stub").unwrap();
    Ok(p)
}
