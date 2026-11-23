//! The round settles (`apply_edits.Round` and `settle_round`, feature 335's round arbiter, features 375 FR-019, 385 and 399): what the
//! settling needs from before the blocks are applied - the owed fingerprints of the reply's own checks and of the checks before them in the
//! pop-up order, a record-format round's prepass words, the quote-check notes another check's blocks may move - and, after, each unit the
//! blocks alone moved, settled or said to stay owed. The owed tools are the `owed` crate's, asked in process where the Python asked them
//! through `scripts/owed_door.py`; a failure to read or to settle is reported and never stops the edits, as the Python's was.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;

use l7r_shared::env::Rooted;

use l7r_shared::checks::reply::factual;

use super::{apply, text, touched_questions, unapply_by_hand, words_of, Block};
use crate::record::owed::answers;
use crate::record::{modals, owed, units};
use crate::Reply;

/// `Round`: the fingerprints, words and quote-check notes read before the blocks.
struct Round {
    checks: Vec<String>,
    earlier: Vec<String>,
    before: BTreeMap<String, String>,
    words: BTreeMap<String, HashSet<String>>,
    quotes: BTreeMap<String, (String, String)>,
    quote_owed: HashSet<String>,
    /// The round has a wording EDIT (451 T188): the units of every check are read, and one that only its wording EDITs moved and that
    /// was answered before them settles, so a wording finding re-owes nothing and cascades to nothing, whatever else the reply holds.
    wide: bool,
    /// Its factual EDITs, applied after the wording ones where it has both, so `mid` (every fingerprint between the two passes) tells a
    /// unit only wording moved (`mid` = after) from one a factual EDIT moved.
    factual: HashSet<usize>,
    mid: Option<BTreeMap<String, String>>,
}

/// The numbers of `found`'s EDITs not held back that fix a fact by the reply's checks (451 T188): with no check named, every one, as
/// an untold category is.
fn factual_blocks(checks: &[String], found: &[Block], skip: &HashSet<usize>) -> HashSet<usize> {
    found
        .iter()
        .filter_map(|b| {
            if let Block::Edit(e) = b {
                Some(e)
            } else {
                None
            }
        })
        .filter(|e| !skip.contains(&e.n))
        .filter(|e| checks.is_empty() || checks.iter().any(|c| factual(c, &e.category)))
        .map(|e| e.n)
        .collect()
}

/// Every owed unit's fingerprint, whatever its check (a wide round, 451 T188).
fn every_fingerprint(root: &Path) -> Result<BTreeMap<String, String>, String> {
    Ok(owed::units(root, None, None, &owed::FAMILIES, "")?
        .into_iter()
        .map(|u| (u.slug, u.fingerprint))
        .collect())
}

fn fingerprints(root: &Path, checks: &[String]) -> Result<BTreeMap<String, String>, String> {
    Ok(owed::fingerprints(root, checks)?.into_iter().collect())
}

/// `quote_notes`: every note of `questions` as its quote-check slug, with its fingerprint and quotation key, in the tree now.
fn quote_notes(
    root: &Path,
    questions: &HashSet<String>,
) -> Result<BTreeMap<String, (String, String)>, String> {
    let rec = owed::read_at(root, None, Some(&HashSet::new()))?;
    let mut out = BTreeMap::new();
    for (stem, notes) in rec.notes.iter() {
        if !questions.contains(&units::question(stem)) {
            continue;
        }
        for (k, _) in notes.iter() {
            let slug = format!("quote-check:{stem}#{k}");
            let pair = (
                units::fingerprint(&rec, &slug),
                units::quotation_key(&rec, &slug),
            );
            out.insert(slug, pair);
        }
    }
    Ok(out)
}

impl Round {
    fn read(
        root: &Path,
        report: &str,
        found: &[Block],
        skip: &HashSet<usize>,
    ) -> Result<Self, String> {
        let checks = owed::reply_checks(report);
        let factual = factual_blocks(&checks, found, skip);
        let wide = !checks.is_empty()
            && found.iter().any(
                |b| matches!(b, Block::Edit(e) if !skip.contains(&e.n) && !factual.contains(&e.n)),
            );
        let earlier = if checks.is_empty() {
            Vec::new()
        } else {
            modals::earlier_units(&checks)
        };
        let all: Vec<String> = checks.iter().chain(&earlier).cloned().collect();
        let reads_quotes = !checks.is_empty() && !checks.iter().any(|c| c == "quote-check");
        // one reading of what is owed for the round's checks and, where the quote-check notes are read below, for quote-check too: each
        // reading is nine git processes, and a record-format round asked twice (feature 449 T167)
        let mut asked = all.clone();
        if reads_quotes {
            asked.push("quote-check".to_owned());
        }
        let mut owed_now = if checks.is_empty() {
            BTreeMap::new()
        } else if wide {
            every_fingerprint(root)?
        } else {
            fingerprints(root, &asked)?
        };
        // a unit's check as `Unit::check` reads its slug
        let check_of = |slug: &str| slug.split_once(':').map_or(slug, |p| p.0).to_owned();
        let before: BTreeMap<String, String> = owed_now
            .iter()
            .filter(|(slug, _)| wide || all.contains(&check_of(slug)))
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();
        owed_now.retain(|slug, _| check_of(slug) == "quote-check");
        let touched: HashSet<String> = touched_questions(found).into_iter().collect();
        let mut sorted_touched: Vec<String> = touched.iter().cloned().collect();
        sorted_touched.sort();
        let words = if checks.iter().any(|c| c == "record-format") {
            words_of(root, &sorted_touched)?
        } else {
            BTreeMap::new()
        };
        let quotes = if reads_quotes {
            quote_notes(root, &touched)?
        } else {
            BTreeMap::new()
        };
        let quote_owed = if quotes.is_empty() {
            HashSet::new()
        } else {
            owed_now.into_keys().collect()
        };
        Ok(Self {
            checks,
            earlier,
            before,
            words,
            quotes,
            quote_owed,
            wide,
            factual,
            mid: None,
        })
    }

    fn joined(&self) -> String {
        self.checks.join("/")
    }

    /// `settle_quotes`: each quote-check note this run's blocks moved, settled where its quotation and claim stand as before.
    fn settle_quotes(&self, root: &Path, store: &Path) -> Result<Vec<String>, String> {
        let questions: HashSet<String> = self
            .quotes
            .keys()
            .map(|s| units::question(s.split_once(':').map_or("", |p| p.1)))
            .collect();
        let after = quote_notes(root, &questions)?;
        let why = format!(
            "{}: the {} round's EDIT blocks",
            answers::FIXED,
            self.joined()
        );
        let mut out = Vec::new();
        for (slug, (fp, key)) in &self.quotes {
            let (fp2, key2) = after.get(slug).cloned().unwrap_or_default();
            if fp2.is_empty() || fp2 == *fp {
                continue;
            }
            if key2 != *key {
                out.push(format!(
                    "  {slug}: still owed - its quotation or its claim changed"
                ));
            } else if self.quote_owed.contains(slug) && !answers::answered(store, slug, fp, "") {
                out.push(format!(
                    "  {slug}: still owed - not answered at the words before these blocks"
                ));
            } else {
                let was = answers::read_answer(store, slug);
                let result = format!(
                    "{why}; was: {}",
                    text(was.get("result"), "unchanged since main")
                );
                answers::write_answer(store, slug, &fp2, &result, was.get("pages"))?;
                answers::keep_reading(store, slug, &key2, "qkeys")?;
                out.push(format!(
                    "  {slug}: settled - another check's fix, outside its quotation and its claim"
                ));
            }
        }
        Ok(out)
    }

    /// `settle`: each owed unit the blocks alone moved, answered or pending; a record-format unit raising a new word stays owed.
    fn settle(&self, root: &Rooted) -> Result<Vec<String>, String> {
        let all: Vec<String> = self.checks.iter().chain(&self.earlier).cloned().collect();
        // run only for a round that names its checks (`run`), so the Python's `if self.checks else {}` has no other side here
        let after = if self.wide {
            every_fingerprint(root)?
        } else {
            fingerprints(root, &all)?
        };
        let store = answers::store_in(root);
        let mut out = Vec::new();
        for (slug, fp) in &after {
            let before = self.before.get(slug).cloned().unwrap_or_default();
            if before.is_empty() || before == *fp {
                continue;
            }
            let (check, q) = slug.split_once(':').unwrap_or((slug, ""));
            if !all.iter().any(|c| c == check) {
                // another check's unit, read only by a wording round: settled where it was answered (quote-check's are the
                // quotation's, ruled by `settle_quotes`)
                let only_wording = self.mid.as_ref().is_none_or(|m| m.get(slug) == Some(fp));
                if check != "quote-check"
                    && only_wording
                    && answers::answered(&store, slug, &before, "")
                {
                    answers::settle(&store, slug, &before, fp)?;
                    out.push(format!("  {slug}: settled with its answer - a wording round's EDITs alone moved it, no fact changed (451 T188)"));
                }
                continue;
            }
            if self.earlier.iter().any(|e| e == check) {
                if answers::answered(&store, slug, &before, "") {
                    answers::settle(&store, slug, &before, fp)?;
                    out.push(format!("  {slug}: settled with its answer - the {} round's blocks alone moved it (it runs before them)", self.joined()));
                } else {
                    out.push(format!(
                        "  {slug}: still owed - not answered at the words before these blocks"
                    ));
                }
                continue;
            }
            if let (true, Some(was)) = (slug.starts_with("record-format:"), self.words.get(q)) {
                let now = words_of(root, &[q.to_owned()])?
                    .remove(q)
                    .unwrap_or_default();
                let mut unruled: Vec<&String> = now.difference(was).collect();
                unruled.sort();
                if !unruled.is_empty() {
                    let shown: Vec<&str> = unruled.iter().take(8).map(|s| s.as_str()).collect();
                    out.push(format!("  {slug}: still owed - its prepass now raises {}, which the round never ruled on", shown.join(", ")));
                    continue;
                }
            }
            let said = answers::settle(&store, slug, &before, fp)?;
            let how = if said == "answered" {
                "settled with its answered round"
            } else {
                "settles when `make record-checked` records this round"
            };
            out.push(format!("  {slug}: {how}"));
        }
        if !self.quotes.is_empty() {
            // the store settle already found, not asked of git again (feature 449 T167)
            out.extend(self.settle_quotes(root, &store)?);
        }
        Ok(out)
    }
}

/// The kind and words of a failure, as `{type(e).__name__}: {e}` named it (the words the Rust's, `ask:449-T066-json-message`).
pub(super) fn named(e: &str) -> String {
    if e.split_once(": ")
        .is_some_and(|(k, _)| !k.is_empty() && k.chars().all(char::is_alphanumeric))
    {
        e.to_owned()
    } else {
        format!("ValueError: {e}")
    }
}

/// The blocks applied for a round: in one pass, or for a mixed round its wording EDITs (and GLOSSARY blocks) first, every fingerprint
/// read into `mid`, then its factual ones (451 T188).
fn apply_round(
    root: &Rooted,
    found: &[Block],
    (skip, refused): (&HashSet<usize>, &BTreeMap<usize, String>),
    rnd: Option<&mut Round>,
    (dry, form): (bool, bool),
    said: &mut String,
) -> Result<super::Tally, String> {
    let Some(r) = rnd.filter(|r| r.wide && !r.factual.is_empty()) else {
        return apply(
            root,
            found,
            (skip, refused, &HashSet::new()),
            dry,
            form,
            said,
        );
    };
    let wording: HashSet<usize> = found
        .iter()
        .map(super::Block::n)
        .filter(|n| !r.factual.contains(n))
        .collect();
    let a = apply(root, found, (skip, refused, &r.factual), dry, form, said)?;
    r.mid = every_fingerprint(root).ok();
    let b = apply(root, found, (skip, refused, &wording), dry, form, said)?;
    Ok(a.plus(&b))
}

/// `main` from the blocks on: the hand-applied pass, the blocks applied inside the settling, the tally.
pub(super) fn run(
    root: &Rooted,
    report: &str,
    found: &[Block],
    skip: &HashSet<usize>,
    dry: bool,
    form: bool,
) -> Reply {
    let mut said = String::new();
    let fail = |said: String, e: String| Reply {
        stdout: said,
        stderr: e + "\n",
        code: 1,
    };
    // an EDIT putting back what an earlier round replaced is refused before anything is applied (451 T190), and is no block of the round
    let refused = super::settled::refusals(root, report, found, skip);
    let held: HashSet<usize> = skip.iter().chain(refused.keys()).copied().collect();
    let skip = &held;
    if !dry {
        if let Err(e) = unapply_by_hand(root, found, skip, &mut said) {
            return fail(said, e);
        }
    }
    let edits = found.iter().any(|b| matches!(b, Block::Edit(_)));
    let tally = if dry || !edits {
        apply(
            root,
            found,
            (skip, &refused, &HashSet::new()),
            dry,
            form,
            &mut said,
        )
    } else {
        let mut rnd = if super::is_repo(root) {
            match Round::read(root, report, found, skip) {
                Ok(r) => Some(r),
                Err(e) => {
                    let _ = writeln!(
                        said,
                        "apply-edits: could not read the round's units ({}) - its units stay owed",
                        named(&e)
                    );
                    None
                }
            }
        } else {
            None
        };
        let tally = apply_round(
            root,
            found,
            (skip, &refused),
            rnd.as_mut(),
            (dry, form),
            &mut said,
        );
        if let (Ok(t), Some(rnd)) = (&tally, &rnd) {
            if !rnd.checks.is_empty() && t.edited > 0 {
                let lines = rnd.settle(root).unwrap_or_else(|e| {
                    vec![format!(
                        "  could not settle ({}) - its units stay owed",
                        named(&e)
                    )]
                });
                if !lines.is_empty() {
                    let _ = writeln!(
                        said,
                        "apply-edits: the {} round's own EDITs, applied verbatim:\n{}",
                        rnd.joined(),
                        lines.join("\n")
                    );
                }
            } else if t.edited > 0 {
                said.push_str("apply-edits: the reply names no check, so the units it answered stay owed - put the agent's counts line (`modal-form: <name> - 2 findings`, `quote-check: ...`) at the top of the reply file and run this again; the blocks already in are settled, not applied twice\n");
            }
        }
        tally
    };
    let t = match tally {
        Ok(t) => t,
        Err(e) => return fail(said, e),
    };
    let tail = if t.terms > 0 {
        " - then `make glossary`"
    } else {
        ""
    };
    let dry_note = if dry {
        " (dry run, nothing written)"
    } else {
        ""
    };
    let _ = writeln!(
        said,
        "apply-edits: {} block(s), {} refused{dry_note}{tail}",
        found.len(),
        t.refused
    );
    Reply {
        stdout: said,
        stderr: String::new(),
        code: i32::from(t.refused > 0),
    }
}
