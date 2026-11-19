//! The search's reach and its exclusions (T204): where a search starts (`Root`), how it reaches a held file, and what each tool's
//! flags leave out (`Filter`), as each tool was measured doing (the parent module's doc).

use std::path::Path;

use fancy_regex::Regex;

use crate::guards::finished_run_hooks::runs::realpath;
/// Where a search starts: the checkout-relative path or glob, as written, and whether it descends.
pub(super) struct Root {
    pub(super) written: String,
    pub(super) rel: Option<String>,
    pub(super) glob: Option<Regex>,
    pub(super) recursive: bool,
}

/// How a held file is reached from a root: named itself, or below it at this relative path.
pub(super) enum Reach {
    Named,
    Below(String),
}

impl Root {
    pub(super) fn new(written: &str, cwd: &str, top: &str, recursive: bool) -> Root {
        let joined = Path::new(cwd).join(written);
        let has_glob = written.contains(['*', '?', '[']);
        let (rel, glob) = if has_glob {
            let (dir, rest) = split_glob(&joined.to_string_lossy());
            let base = rel_to(&realpath(Path::new(&dir)).to_string_lossy(), top);
            let pattern = base.map(|b| {
                if b.is_empty() {
                    rest.clone()
                } else {
                    format!("{b}/{rest}")
                }
            });
            (None, pattern.and_then(|p| glob_re(&p, Style::SHELL)))
        } else {
            (rel_to(&realpath(&joined).to_string_lossy(), top), None)
        };
        Root {
            written: written.to_owned(),
            rel,
            glob,
            recursive,
        }
    }

    pub(super) fn reach(&self, file: &str) -> Option<Reach> {
        if let Some(glob) = &self.glob {
            if is(glob, file) {
                return Some(Reach::Named);
            }
            // without recursion only the directories the glob names directly are listed (`ls dir/*`, a grep with no -r below)
            let mut at = file;
            while let Some((up, _)) = at.rsplit_once('/') {
                if (self.recursive || at == file) && is(glob, up) {
                    return Some(Reach::Below(file[up.len() + 1..].to_owned()));
                }
                at = up;
            }
            return None;
        }
        let rel = self.rel.as_deref()?;
        let (parent, base) = file.rsplit_once('/').unwrap_or(("", file));
        if rel == file {
            Some(Reach::Named)
        } else if !self.recursive {
            // KEPT FROM BEFORE T204: a grep named at the held file's own directory is refused, although with no -r GNU grep reads
            // nothing there - a cheap refusal, never a leak, and the guard's suite pins it
            (parent == rel).then(|| Reach::Below(base.to_owned()))
        } else if rel.is_empty() {
            Some(Reach::Below(file.to_owned()))
        } else {
            file.strip_prefix(rel)
                .and_then(|r| r.strip_prefix('/'))
                .map(|r| Reach::Below(r.to_owned()))
        }
    }
}

/// `/a/b/*/c` as its last directory with no glob character, `/a/b`, and the rest, `*/c`.
pub(super) fn split_glob(path: &str) -> (String, String) {
    let first = path.find(['*', '?', '[']).unwrap_or(path.len());
    let cut = path[..first].rfind('/').unwrap_or(0);
    (path[..cut.max(1)].to_owned(), path[cut + 1..].to_owned())
}

/// `path` relative to the checkout `top` ('' for the top itself), None outside it.
pub(super) fn rel_to(path: &str, top: &str) -> Option<String> {
    let top = realpath(Path::new(top));
    Path::new(path)
        .strip_prefix(&top)
        .ok()
        .map(|r| r.to_string_lossy().into_owned())
}

/// How a tool reads a glob: `*` and `?` within one path component unless `cross` (`find -path`, a pathspec); `{a,b}` alternatives
/// only where `braces` (ripgrep, and bash before the command sees it - GNU grep, find, ag and git take a brace literally, measured
/// 2026-11-19); case folded where `fold` (`rg --iglob`, `find -iname`).
#[derive(Clone, Copy)]
pub(super) struct Style {
    pub(super) cross: bool,
    pub(super) braces: bool,
    pub(super) fold: bool,
}

impl Style {
    /// `fnmatch` over a name: GNU grep's `--exclude`, ag's `--ignore`.
    pub(super) const NAME: Style = Style {
        cross: false,
        braces: false,
        fold: false,
    };
    /// A shell word's glob, its braces expanded by bash.
    pub(super) const SHELL: Style = Style {
        cross: false,
        braces: true,
        fold: false,
    };
    /// `fnmatch` over a whole path: a pathspec.
    pub(super) const PATH: Style = Style {
        cross: true,
        braces: false,
        fold: false,
    };
}

/// A glob as an anchored regex: `**/` any directories, `**` anything, `*` and `?`, `[...]` a class, braces, as `style` reads them.
/// None for a glob it cannot read.
pub(super) fn glob_re(glob: &str, style: Style) -> Option<Regex> {
    let c: Vec<char> = glob.chars().collect();
    let one = if style.cross { "." } else { "[^/]" };
    let start = if style.fold { "(?i)^" } else { "^" };
    let (mut out, mut depth, mut i) = (String::from(start), 0usize, 0);
    while let Some(&ch) = c.get(i) {
        match ch {
            '*' if c.get(i + 1) == Some(&'*') => {
                let dirs = c.get(i + 2) == Some(&'/');
                out.push_str(if dirs { "(?:.*/)?" } else { ".*" });
                i += 1 + usize::from(dirs);
            }
            '*' => {
                out.push_str(one);
                out.push('*');
            }
            '?' => out.push_str(one),
            '[' => {
                let close = (i + 2..c.len()).find(|&j| c[j] == ']')?;
                let body: String = c[i + 1..close].iter().collect();
                let body = body
                    .strip_prefix(['!', '^'])
                    .map_or(body.clone(), |b| format!("^{b}"));
                out.push('[');
                out.push_str(&body.replace('\\', r"\\").replace('[', r"\["));
                out.push(']');
                i = close;
            }
            '{' if style.braces => {
                depth += 1;
                out.push_str("(?:");
            }
            ',' if depth > 0 => out.push('|'),
            '}' if depth > 0 => {
                depth -= 1;
                out.push(')');
            }
            _ => out.push_str(&fancy_regex::escape(&ch.to_string())),
        }
        i += 1;
    }
    out.push('$');
    (depth == 0)
        .then(|| crate::shared::regex::build(&out).ok())
        .flatten()
}

pub(super) fn is(re: &Regex, text: &str) -> bool {
    re.is_match(text).unwrap_or(false)
}

pub(super) fn glob_is(glob: &str, text: &str, style: Style) -> bool {
    glob_re(glob, style).is_some_and(|re| is(&re, text))
}

/// A held file as one search reaches it.
pub(super) struct Hit<'a> {
    pub(super) file: &'a str,
    pub(super) below: Option<&'a str>,
    pub(super) cwd_rel: Option<String>,
    pub(super) abs: String,
    pub(super) printed: String,
}

impl Hit<'_> {
    pub(super) fn base(&self) -> &str {
        self.file.rsplit('/').next().unwrap_or(self.file)
    }

    /// The directories between the root and the file, by name.
    fn dirs(&self) -> Vec<&str> {
        let below = self.below.unwrap_or("");
        let mut parts: Vec<&str> = below.split('/').collect();
        parts.pop();
        parts
    }

    /// `path` and each directory above it, the file first.
    fn with_parents(path: &str) -> Vec<&str> {
        let mut out = vec![path];
        let mut at = path;
        while let Some((up, _)) = at.rsplit_once('/') {
            out.push(up);
            at = up;
        }
        out
    }
}

/// What each tool's flags say about which found files it searches.
#[derive(Default)]
pub(super) struct Filter {
    pub(super) grep_ex: Vec<String>,
    pub(super) grep_in: Vec<String>,
    pub(super) grep_ex_dir: Vec<String>,
    pub(super) globs: Vec<RgGlob>,
    pub(super) types_in: Vec<String>,
    pub(super) types_out: Vec<String>,
    pub(super) ag_ignore: Vec<String>,
    pub(super) ag_regex: Vec<String>,
    pub(super) find: Vec<FindTest>,
    pub(super) find_or: bool,
    pub(super) specs_out: Vec<String>,
    pub(super) bypass_named: bool,
}

/// One of ripgrep's `-g` or `--iglob` globs: whether it excludes (`!`), the glob, and whether it folds case.
pub(super) struct RgGlob {
    pub(super) neg: bool,
    pub(super) glob: String,
    pub(super) fold: bool,
}

impl RgGlob {
    pub(super) fn new(text: &str, fold: bool) -> RgGlob {
        let (neg, glob) = text.strip_prefix('!').map_or((false, text), |g| (true, g));
        RgGlob {
            neg,
            glob: glob.to_owned(),
            fold,
        }
    }
}

pub(super) struct FindTest {
    pub(super) path: bool,
    /// `find -name` and `-path` read `*` across `/`, braces literally; `-iname` and `-ipath` fold case.
    pub(super) style: Style,
    pub(super) glob: String,
    pub(super) neg: bool,
    pub(super) prune: bool,
}

/// A type's extensions as ripgrep's `-t` names them (the ones this repository holds); None for a type not listed here.
pub(super) fn type_exts(name: &str) -> Option<&'static [&'static str]> {
    Some(match name {
        "py" | "python" => &["py", "pyi"],
        "rust" | "rs" => &["rs"],
        "md" | "markdown" => &["md", "markdown"],
        "sh" => &["sh", "bash"],
        "json" => &["json", "jsonl"],
        "toml" => &["toml"],
        "html" => &["html", "htm"],
        "css" => &["css"],
        "js" => &["js", "mjs", "cjs"],
        "ts" => &["ts", "tsx"],
        "yaml" => &["yaml", "yml"],
        "txt" => &["txt"],
        "svg" => &["svg"],
        "make" => &["mk", "mak"],
        _ => return None,
    })
}

impl Filter {
    pub(super) fn excludes(&self, hit: &Hit) -> bool {
        if hit.below.is_none() && self.bypass_named {
            return false;
        }
        let base = hit.base();
        let ext = base.rsplit_once('.').map_or("", |(_, e)| e);
        let typed = |names: &[String]| {
            names
                .iter()
                .any(|t| type_exts(t).is_none_or(|exts| exts.contains(&ext)))
        };
        self.grep_ex.iter().any(|g| glob_is(g, base, Style::NAME))
            || self
                .grep_ex_dir
                .iter()
                .any(|g| hit.dirs().iter().any(|d| glob_is(g, d, Style::NAME)))
            || (!self.grep_in.is_empty()
                && !self.grep_in.iter().any(|g| glob_is(g, base, Style::NAME)))
            || self.glob_excludes(hit)
            || (!self.types_in.is_empty() && !typed(&self.types_in))
            || (self
                .types_out
                .iter()
                .any(|t| type_exts(t).is_some_and(|exts| exts.contains(&ext))))
            || self.ag_ignore.iter().any(|p| ag_ignores(p, hit))
            || (!self.ag_regex.is_empty() && !self.ag_regex.iter().any(|r| ag_selects(r, hit)))
            || self.find_excludes(hit)
            || self.specs_out.iter().any(|s| spec_holds(s, hit.file))
    }

    /// ripgrep's globs: the last that matches decides; none matching leaves a file out only where a positive glob was given.
    fn glob_excludes(&self, hit: &Hit) -> bool {
        let found = self.globs.iter().rev().find(|g| rg_glob(g, hit));
        found.map_or_else(|| self.globs.iter().any(|g| !g.neg), |g| g.neg)
    }

    fn find_excludes(&self, hit: &Hit) -> bool {
        self.find.iter().any(|t| {
            let name_of = |p: &str| p.rsplit('/').next().unwrap_or(p).to_owned();
            let texts: Vec<String> = if t.prune {
                Hit::with_parents(&hit.printed)
                    .into_iter()
                    .map(str::to_owned)
                    .collect()
            } else {
                vec![hit.printed.clone()]
            };
            let matched = texts.iter().any(|p| {
                glob_is(
                    &t.glob,
                    &if t.path { p.clone() } else { name_of(p) },
                    t.style,
                )
            });
            (matched && (t.neg || t.prune)) || (!matched && !t.neg && !t.prune && !self.find_or)
        })
    }
}

/// A ripgrep glob (its `!` taken off): no `/` matches the base name, or a directory's name when it excludes; with one, the path from
/// the working directory (or the absolute path, which only a `**/` glob matches), and its directories when it excludes.
pub(super) fn rg_glob(rg: &RgGlob, hit: &Hit) -> bool {
    let (neg, style) = (
        rg.neg,
        Style {
            cross: false,
            braces: true,
            fold: rg.fold,
        },
    );
    let glob = rg.glob.trim_end_matches('/');
    if !glob.contains('/') {
        return glob_is(glob, hit.base(), style)
            || (neg && hit.dirs().iter().any(|d| glob_is(glob, d, style)));
    }
    let glob = glob.trim_start_matches('/');
    [hit.cwd_rel.as_deref(), Some(hit.abs.as_str())]
        .into_iter()
        .flatten()
        .any(|path| {
            let paths = if neg {
                Hit::with_parents(path)
            } else {
                vec![path]
            };
            paths.into_iter().any(|p| glob_is(glob, p, style))
        })
}

/// ag's `--ignore`: no `/` matches the base name or a directory's name; a plain path, the tail of the path from the working directory;
/// a `**` or a glob beside a `/`, nothing (measured).
pub(super) fn ag_ignores(pattern: &str, hit: &Hit) -> bool {
    if !pattern.contains('/') {
        return !pattern.contains("**")
            && (glob_is(pattern, hit.base(), Style::NAME)
                || hit.dirs().iter().any(|d| glob_is(pattern, d, Style::NAME)));
    }
    let tail = format!("/{}", pattern.trim_matches('/'));
    !pattern.contains(['*', '?', '['])
        && hit.cwd_rel.as_deref().is_some_and(|p| {
            Hit::with_parents(p)
                .iter()
                .any(|q| format!("/{q}").ends_with(&tail))
        })
}

/// ag's `-G`: a regex searched in the path.
pub(super) fn ag_selects(regex: &str, hit: &Hit) -> bool {
    crate::shared::regex::build(regex).is_ok_and(|re| {
        [hit.cwd_rel.as_deref(), Some(hit.abs.as_str())]
            .into_iter()
            .flatten()
            .any(|p| is(&re, p))
    })
}

/// A checkout-relative pathspec holds `file`: the file itself, a directory above it, or a glob matching it.
pub(super) fn spec_holds(spec: &str, file: &str) -> bool {
    spec.is_empty()
        || spec == file
        || file.strip_prefix(spec).is_some_and(|r| r.starts_with('/'))
        || (spec.contains(['*', '?', '[']) && glob_is(spec, file, Style::PATH))
}
