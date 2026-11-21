//! The command lines (feature 449 T138): `l7r-gate record semantic build|find` (`semantic_index.py`'s two, `make semantic-index` and `make
//! semantic-find`) and `l7r-gate record search` (`research_search.py`, `make research-search`), their arguments read as argparse read
//! them (`ask:449-usage-text`: argparse's own words on exit 2 are one line naming the verb and the complaint).
//!
//! - `record semantic build [--shard S ...] [--limit N]`
//! - `record semantic find "<question>" [--k K]`
//! - `record search --q "<question>" [--q "<in another language>" ...] [--terms "a|b" ...] [--key K] [--limit N] [--record-limit N]`

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_archive::store::Archive;
use l7r_gate_core::record::args::{parse_with, Spec};

use crate::embed::Embed;
use crate::index::{build, commit, find, preview};
use crate::search::{render, search, LIMIT, RECORD_LIMIT};
use crate::Reply;

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

fn usage(verb: &str, said: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate record {verb}: error: {said}\n"),
        2,
    )
}

/// argparse's `type=int`: Python's whitespace around, a sign, an underscore only between digits.
fn py_int(flag: &str, raw: &str) -> Result<i64, String> {
    let t = l7r_shared::py_text::strip(raw);
    let digits = t.strip_prefix(['+', '-']).unwrap_or(t);
    let b = digits.as_bytes();
    let ok = !b.is_empty()
        && b.iter().enumerate().all(|(i, c)| {
            c.is_ascii_digit()
                || (*c == b'_'
                    && i > 0
                    && b[i - 1].is_ascii_digit()
                    && b.get(i + 1).is_some_and(u8::is_ascii_digit))
        });
    ok.then(|| t.replace('_', "").parse::<i64>().ok())
        .flatten()
        .ok_or_else(|| format!("argument {flag}: invalid int value: '{raw}'"))
}

/// What the commands reach beyond the repository: the archive's working copy (with the push's credential for a build), the embedder,
/// where a build's lines go, and the shards' write time (the real ones in [`cli`], a test's stand-ins otherwise).
pub struct Reach<'a> {
    pub store: &'a dyn Fn(&Path, bool) -> Archive,
    pub embed: &'a dyn Fn(&Path, &Path) -> Box<dyn Embed>,
    pub say: &'a dyn Fn(&str),
    pub when: &'a dyn Fn() -> (u16, u16),
}

/// The sources home: the archive's working copy and the model cache beside the page cache (`archive.home_of`).
fn home_of(root: &Path) -> PathBuf {
    l7r_shared::consulted::home(root)
}

/// `l7r-gate record semantic <build|find> ...` from `cwd`'s repository, with the real working copy and embedder.
#[cfg(not(test))]
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    cli_with(args, cwd, &production())
}

/// `l7r-gate record search ...` from `cwd`'s repository, with the real working copy and embedder.
#[cfg(not(test))]
#[must_use]
pub fn search_cli(args: &[String], cwd: &Path) -> Reply {
    search_with(args, cwd, &production())
}

#[cfg(not(test))]
fn production() -> Reach<'static> {
    Reach {
        store: &|root, push| {
            let env = push
                .then(|| l7r_gate_archive::store::git_env(&l7r_gate_archive::store::token(root)));
            Archive::new(&home_of(root), env)
        },
        embed: &|root, home| {
            Box::new(crate::embed::Program::new(
                &l7r_gate_archive::client::launcher(root),
                &home.join(crate::CACHE),
            ))
        },
        say: &l7r_gate_archive::cli::print_now,
        when: &|| {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| d.as_secs());
            crate::npz::dos_time(now)
        },
    }
}

/// [`cli`] with what it reaches handed in.
#[must_use]
pub fn cli_with(args: &[String], cwd: &Path, reach: &Reach<'_>) -> Reply {
    let root = l7r_shared::consulted::repo_root(Some(cwd));
    let home = home_of(&root);
    let rest = args.get(1..).unwrap_or(&[]);
    match args.first().map(String::as_str) {
        Some("build") => {
            let p = match parse_with(rest, &[Spec::value("--shard"), Spec::value("--limit")], 0) {
                Ok(p) => p,
                Err(e) => return usage("semantic build", &e),
            };
            let limit = match py_int("--limit", p.text("--limit", "0")) {
                Ok(n) => n,
                Err(e) => return usage("semantic build", &e),
            };
            let only: Vec<String> = p.all("--shard").into_iter().map(str::to_owned).collect();
            let store = (reach.store)(&root, true);
            let mut embed = (reach.embed)(&root, &home);
            let mut say = |line: &str| (reach.say)(line);
            let built = build(
                &store.dir,
                &root,
                embed.as_mut(),
                &only,
                limit,
                (reach.when)(),
                &mut say,
            );
            drop(embed);
            let written = match built {
                Ok(w) => w,
                Err(e) => return reply(String::new(), format!("semantic-index: {e}\n"), 1),
            };
            say(&format!(
                "semantic-index: {} shard(s) written",
                written.len()
            ));
            match commit(&store, &written, &mut say) {
                Ok(why) => reply(String::new(), String::new(), i32::from(!why.is_empty())),
                Err(e) => reply(String::new(), format!("semantic-index: {e}\n"), 1),
            }
        }
        Some("find") => {
            let p = match parse_with(rest, &[Spec::value("--k")], 1) {
                Ok(p) if p.positional.len() == 1 => p,
                Ok(_) => {
                    return usage(
                        "semantic find",
                        "the following arguments are required: question",
                    )
                }
                Err(e) => return usage("semantic find", &e),
            };
            let k = match py_int("--k", p.text("--k", "10")) {
                Ok(n) => n,
                Err(e) => return usage("semantic find", &e),
            };
            let dir = (reach.store)(&root, false).dir;
            let mut embed = (reach.embed)(&root, &home);
            let mut out = String::new();
            let hits = match find(&dir, &p.positional[0], embed.as_mut(), k) {
                Ok(h) => h,
                Err(e) => return reply(out, format!("semantic-find: {e}\n"), 1),
            };
            if hits.is_empty() {
                return reply(
                    out,
                    "semantic-find: no index yet - run `make semantic-index`\n".to_owned(),
                    1,
                );
            }
            for (sim, rel, s, e) in hits {
                match preview(&dir, &root, &rel, s, e, 240) {
                    Ok(words) => {
                        let _ = writeln!(
                            out,
                            "{:.3}  {rel} [{s}:{e}]\n       {words}",
                            f64::from(sim)
                        );
                    }
                    Err(err) => return reply(out, format!("semantic-find: {err}\n"), 1),
                }
            }
            reply(out, String::new(), 0)
        }
        _ => usage(
            "semantic",
            "argument cmd: invalid choice (choose from 'build', 'find')",
        ),
    }
}

/// The search's first line: what was asked, what was found, what a key held back and what is left.
fn header(
    questions: &[String],
    term_sets: &[Vec<String>],
    found: &crate::search::Found,
    key: &str,
) -> String {
    let mut out = format!(
        "research-search: {} question(s), {} term set(s) - {} of {} source(s)",
        questions.len(),
        term_sets.len(),
        found.rows.len(),
        found.found
    );
    if !key.is_empty() {
        let _ = write!(
            out,
            ", {} already shown under key {}",
            found.held,
            l7r_shared::py_text::repr(key)
        );
    }
    if found.found - found.held > found.rows.len() {
        let _ = write!(
            out,
            "; {} more not printed - call again under KEY= for the next",
            found.found - found.held - found.rows.len()
        );
    }
    out.push('\n');
    out
}

/// The terms a measure is scored by: every term of every set, then each question's words of four ASCII letters or more
/// (`re.findall(r"[A-Za-z]{4,}", q)`).
fn terms_of(term_sets: &[Vec<String>], questions: &[String]) -> Vec<String> {
    let mut terms: Vec<String> = term_sets.iter().flatten().cloned().collect();
    for q in questions {
        let mut word = String::new();
        for c in q.chars().chain(std::iter::once(' ')) {
            if c.is_ascii_alphabetic() {
                word.push(c);
            } else {
                if word.len() >= 4 {
                    terms.push(word.clone());
                }
                word.clear();
            }
        }
    }
    terms
}

/// [`search_cli`] with what it reaches handed in.
#[must_use]
pub fn search_with(args: &[String], cwd: &Path, reach: &Reach<'_>) -> Reply {
    let specs = [
        Spec::value("--q"),
        Spec::value("--terms"),
        Spec::value("--key"),
        Spec::value("--limit"),
        Spec::value("--record-limit"),
    ];
    let p = match parse_with(args, &specs, 0) {
        Ok(p) => p,
        Err(e) => return usage("search", &e),
    };
    let (limit, record_limit) = (LIMIT.to_string(), RECORD_LIMIT.to_string());
    let limits = match (
        py_int("--limit", p.text("--limit", &limit)),
        py_int("--record-limit", p.text("--record-limit", &record_limit)),
    ) {
        (Ok(a), Ok(b)) => (a, b),
        (Err(e), _) | (_, Err(e)) => return usage("search", &e),
    };
    let strip = l7r_shared::py_text::strip;
    let questions: Vec<String> = p
        .all("--q")
        .into_iter()
        .filter(|q| !strip(q).is_empty())
        .map(str::to_owned)
        .collect();
    let term_sets: Vec<Vec<String>> = p
        .all("--terms")
        .into_iter()
        .flat_map(|arg| arg.split(';'))
        .map(|s| {
            s.split('|')
                .filter(|t| !strip(t).is_empty())
                .map(str::to_owned)
                .collect::<Vec<_>>()
        })
        .filter(|s| !s.is_empty())
        .collect();
    if questions.is_empty() && term_sets.is_empty() {
        return reply(
            String::new(),
            "make research-search: Q=, Q_JA=, Q_ZH=, Q_KO= or TERMS= is required\n".to_owned(),
            2,
        );
    }
    let root = l7r_shared::consulted::repo_root(Some(cwd));
    let home = home_of(&root);
    let dir = (reach.store)(&root, false).dir;
    if !questions.is_empty() && !crate::index_dir(&dir).is_dir() {
        return reply(
            String::new(),
            "research-search: no index yet - run `make semantic-index`\n".to_owned(),
            1,
        );
    }
    let key = p.text("--key", "");
    let mut embed = (reach.embed)(&root, &home);
    let found = match search(
        &dir,
        &root,
        &home,
        &questions,
        &term_sets,
        embed.as_mut(),
        key,
        limits,
    ) {
        Ok(f) => f,
        Err(e) => return reply(String::new(), format!("research-search: {e}\n"), 1),
    };
    let mut out = header(&questions, &term_sets, &found, key);
    let terms = terms_of(&term_sets, &questions);
    match render(&dir, &root, &found.rows, &terms) {
        Ok(lines) => {
            out.push_str(&lines.join("\n"));
            out.push('\n');
            reply(out, String::new(), 0)
        }
        Err(e) => reply(out, format!("research-search: {e}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
