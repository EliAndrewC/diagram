//! The command lines the record's owed tools take, read as `argparse` reads them (feature 449 T87): a long flag exact or by a unique prefix, `--flag=value`, a value that looks like a flag refused with the exit 2 argparse gives.

use fancy_regex::Regex;
use std::sync::LazyLock;

/// One flag of a parser.
#[derive(Clone, Copy)]
pub(crate) struct Spec {
    name: &'static str,
    kind: Arity,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Arity {
    Flag,
    Value,
    Pair,
    List,
}

impl Spec {
    pub(crate) fn value(name: &'static str) -> Self {
        Self {
            name,
            kind: Arity::Value,
        }
    }

    pub(crate) fn flag(name: &'static str) -> Self {
        Self {
            name,
            kind: Arity::Flag,
        }
    }

    pub(crate) fn pair(name: &'static str) -> Self {
        Self {
            name,
            kind: Arity::Pair,
        }
    }

    /// `nargs="*"`: every argument after it up to the next flag.
    pub(crate) fn list(name: &'static str) -> Self {
        Self {
            name,
            kind: Arity::List,
        }
    }
}

/// What a parser read.
#[derive(Default)]
pub(crate) struct Parsed {
    values: Vec<(String, String)>,
    flags: Vec<String>,
    pairs: Vec<(String, (String, String))>,
    lists: Vec<(String, Vec<String>)>,
    /// The positional arguments, in order.
    pub(crate) positional: Vec<String>,
}

impl Parsed {
    /// The last value given for `name`, or `default`.
    pub(crate) fn text<'a>(&'a self, name: &str, default: &'a str) -> &'a str {
        self.values
            .iter()
            .rev()
            .find(|(k, _)| k == name)
            .map_or(default, |(_, v)| v.as_str())
    }

    pub(crate) fn on(&self, name: &str) -> bool {
        self.flags.iter().any(|f| f == name)
    }

    pub(crate) fn pair(&self, name: &str) -> Option<(&str, &str)> {
        self.pairs
            .iter()
            .rev()
            .find(|(k, _)| k == name)
            .map(|(_, (a, b))| (a.as_str(), b.as_str()))
    }

    /// The last list given for `name`, or none.
    pub(crate) fn list(&self, name: &str) -> &[String] {
        self.lists
            .iter()
            .rev()
            .find(|(k, _)| k == name)
            .map_or(&[][..], |(_, v)| v.as_slice())
    }
}

static NEGATIVE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^-\d+$|^-\d*\.\d+$").unwrap_or_else(|e| unreachable!("{e}")));

fn resolve<'a>(specs: &'a [Spec], word: &str) -> Result<Option<&'a Spec>, String> {
    if let Some(s) = specs.iter().find(|s| s.name == word) {
        return Ok(Some(s));
    }
    let hits: Vec<&Spec> = specs.iter().filter(|s| s.name.starts_with(word)).collect();
    if hits.len() > 1 {
        return Err(format!("ambiguous option: {word}"));
    }
    Ok(hits.first().copied())
}

/// Whether `arg` is taken as an option by argparse, given these specs.
fn looks_like_flag(arg: &str, specs: &[Spec]) -> bool {
    if !arg.starts_with('-') || arg.len() == 1 {
        return false;
    }
    let head = arg.split('=').next().unwrap_or(arg);
    if resolve(specs, head).is_ok_and(|s| s.is_some()) {
        return true;
    }
    !(NEGATIVE.is_match(arg).unwrap_or(false) || arg.contains(' '))
}

/// Reads `args` against `specs`: an argument no spec names, a missing value or an ambiguous prefix is argparse's exit 2.
pub(crate) fn parse(args: &[String], specs: &[Spec]) -> Result<Parsed, String> {
    parse_with(args, specs, 0)
}

/// [`parse`], taking up to `positionals` arguments that are no flag as positional ones (`nargs="?"` each).
pub(crate) fn parse_with(
    args: &[String],
    specs: &[Spec],
    positionals: usize,
) -> Result<Parsed, String> {
    let mut out = Parsed::default();
    let mut i = 0;
    while i < args.len() {
        let arg = &args[i];
        i += 1;
        if !looks_like_flag(arg, specs) && out.positional.len() < positionals {
            out.positional.push(arg.clone());
            continue;
        }
        if !arg.starts_with("--") || arg.len() == 2 {
            return Err(format!("unrecognized arguments: {arg}"));
        }
        let (word, inline) = arg
            .split_once('=')
            .map_or((arg.as_str(), None), |(w, v)| (w, Some(v)));
        let Some(spec) = resolve(specs, word)? else {
            return Err(format!("unrecognized arguments: {arg}"));
        };
        match spec.kind {
            Arity::Flag => {
                if inline.is_some() {
                    return Err(format!("ignored explicit argument for {word}"));
                }
                out.flags.push(spec.name.to_owned());
            }
            Arity::Value => {
                if let Some(v) = inline {
                    out.values.push((spec.name.to_owned(), v.to_owned()));
                } else {
                    match args.get(i) {
                        Some(v) if !looks_like_flag(v, specs) => {
                            out.values.push((spec.name.to_owned(), v.clone()));
                            i += 1;
                        }
                        _ => return Err(format!("argument {word}: expected one argument")),
                    }
                }
            }
            Arity::List => {
                let mut got: Vec<String> = inline.map(str::to_owned).into_iter().collect();
                while inline.is_none() && args.get(i).is_some_and(|v| !looks_like_flag(v, specs)) {
                    got.push(args[i].clone());
                    i += 1;
                }
                out.lists.push((spec.name.to_owned(), got));
            }
            Arity::Pair => {
                if inline.is_some() {
                    return Err(format!("argument {word}: expected 2 arguments"));
                }
                match (args.get(i), args.get(i + 1)) {
                    (Some(a), Some(b))
                        if !looks_like_flag(a, specs) && !looks_like_flag(b, specs) =>
                    {
                        out.pairs
                            .push((spec.name.to_owned(), (a.clone(), b.clone())));
                        i += 2;
                    }
                    _ => return Err(format!("argument {word}: expected 2 arguments")),
                }
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
