//! The push's credential, from the secrets file; the only thing the repository still reads from it.

use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Secrets {
    pub github_pat: String,
}

fn candidates(root: &Path, from_env: Option<PathBuf>) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = from_env
        .into_iter()
        .filter(|e| !e.as_os_str().is_empty())
        .collect();
    out.push(root.join("development-secrets.ini"));
    if root
        .parent()
        .and_then(Path::file_name)
        .is_some_and(|n| n == ".clones")
    {
        out.extend(
            root.parent()
                .and_then(Path::parent)
                .map(|main| main.join("development-secrets.ini")),
        );
    }
    out.push(PathBuf::from(
        "/host-l7r-repo/gm-assistant/webapp/development-secrets.ini",
    ));
    out
}

/// `section -> key -> value`, as `configparser` reads this file: `key = value` or `key: value`, a `#` or `;` line a comment.
#[must_use]
pub fn ini(text: &str) -> HashMap<String, HashMap<String, String>> {
    let mut sections: HashMap<String, HashMap<String, String>> = HashMap::new();
    let mut current = String::new();
    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') || line.starts_with(';') {
            continue;
        }
        if let Some(name) = line.strip_prefix('[').and_then(|l| l.strip_suffix(']')) {
            name.clone_into(&mut current);
        } else if let Some((key, value)) = line.split_once(['=', ':']) {
            sections
                .entry(current.clone())
                .or_default()
                .insert(key.trim().to_lowercase(), value.trim().to_owned());
        }
    }
    sections
}

/// The first readable candidate wins; a missing file is an error naming every place looked.
fn load_from(places: &[PathBuf]) -> Result<Secrets, String> {
    let Some(text) = places.iter().find_map(|p| std::fs::read_to_string(p).ok()) else {
        let looked = places
            .iter()
            .map(|p| p.display().to_string())
            .collect::<Vec<_>>()
            .join("\n  ");
        return Err(format!("no development-secrets.ini found; looked in:\n  {looked}\n(copy development-secrets.ini.example at the repository root and fill the [github] key)"));
    };
    let parsed = ini(&text);
    let of = |section: &str, key: &str, default: &str| {
        parsed
            .get(section)
            .and_then(|s| s.get(key))
            .map_or(default, String::as_str)
            .to_owned()
    };
    Ok(Secrets {
        github_pat: of("github", "codebuild_pat", ""),
    })
}

/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn load_secrets(root: &Path) -> Result<Secrets, String> {
    load_from(&candidates(
        root,
        std::env::var_os("DIAGRAM_SECRETS").map(PathBuf::from),
    ))
}

/// `l7r-gate github-token`: the push's credential, from the same file; a tree with no secrets answers nothing, and the push then reports its own failure.
#[must_use]
pub fn github_token(root: &Path) -> crate::Reply {
    token_reply(load_secrets(root))
}

fn token_reply(found: Result<Secrets, String>) -> crate::Reply {
    match found {
        Ok(s) => crate::Reply {
            stdout: format!("{}\n", s.github_pat),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("{why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
