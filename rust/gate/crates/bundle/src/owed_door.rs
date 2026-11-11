//! `l7r-gate owed-door`: the Python callers' one door to the record's owed tools in Rust (feature 449 T87, on the T86 door's pattern, `scripts/owed_door.py`): one process a Python run, each line on stdin `{"verb": .., "args": [..]}`, each answered in order on stdout, so a run's reads follow its own writes. It forwards and holds no logic of its own; a `Record` crosses as the key that reproduces it (root, rev, sources), no cache for the working tree.

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use l7r_guard::shared::checks::pages::{self, Page};
use serde_json::{json, Map, Value};

use crate::record::modals::{self, Modal};
use crate::record::owed::{self, Named};
use crate::record::repo::{git, Fail};
use crate::record::translation;
use crate::record::triage;
use crate::record::units::{self, Record};

fn arg(args: &[Value], i: usize) -> &str {
    args.get(i).and_then(Value::as_str).unwrap_or("")
}

fn path_arg(args: &[Value], i: usize) -> PathBuf {
    PathBuf::from(arg(args, i))
}

fn opt_str(args: &[Value], i: usize) -> Option<&str> {
    args.get(i).and_then(Value::as_str)
}

fn strings(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|s| s.as_str().map(str::to_owned))
        .collect()
}

fn unit_list(rows: &[units::Unit]) -> Value {
    Value::Array(rows.iter().map(units::Unit::json).collect())
}

fn page_json(page: &Page) -> Value {
    let blocks: Vec<Value> = page
        .blocks
        .iter()
        .map(|b| json!({"words": b.words, "marks": b.marks, "intro": b.intro}))
        .collect();
    json!({"heading": page.heading, "blocks": blocks, "intro": page.intro()})
}

fn sources_of(args: &[Value], i: usize) -> Option<HashSet<String>> {
    args.get(i).and_then(Value::as_array).map(|a| {
        a.iter()
            .filter_map(|s| s.as_str().map(str::to_owned))
            .collect()
    })
}

fn record_key(args: &[Value]) -> Result<Record, Fail> {
    let sources = sources_of(args, 2);
    owed::read_at(&path_arg(args, 0), opt_str(args, 1), sources.as_ref())
}

fn triples(rows: Vec<(String, String, String)>) -> Value {
    Value::Array(rows.into_iter().map(|(a, b, c)| json!([a, b, c])).collect())
}

fn rows_of(v: Option<&Value>) -> Option<Vec<(String, String, String)>> {
    v.and_then(Value::as_array).map(|a| {
        a.iter()
            .map(|r| {
                let at = |i: usize| r.get(i).and_then(Value::as_str).unwrap_or("").to_owned();
                (at(0), at(1), at(2))
            })
            .collect()
    })
}

fn modal_list(found: &[Modal]) -> Value {
    Value::Array(found.iter().map(Modal::json).collect())
}

fn ru_verb(verb: &str, args: &[Value]) -> Result<Option<Value>, Fail> {
    Ok(Some(match verb {
        "ru.question" => json!(units::question(arg(args, 0))),
        "ru.digest" => {
            let parts = strings(args.first());
            json!(units::digest(
                &parts.iter().map(String::as_str).collect::<Vec<_>>()
            ))
        }
        "ru.read_page" => page_json(&pages::read_page(arg(args, 0))),
        "ru.read_notes" => {
            let notes = units::read_notes(arg(args, 0), arg(args, 1));
            Value::Object(notes.iter().map(|(k, v)| (k.clone(), json!(v))).collect())
        }
        "ru.stem_matches" => json!(units::stem_of(arg(args, 0)).is_some()),
        "ru.unit" => units::Unit {
            slug: arg(args, 0).to_owned(),
            occasion: arg(args, 1).to_owned(),
            fingerprint: arg(args, 2).to_owned(),
            reading: arg(args, 3).to_owned(),
        }
        .json(),
        "ru.fingerprints_of" => {
            let rec = record_key(args)?;
            let out: Map<String, Value> = strings(args.get(3))
                .iter()
                .map(|s| (s.clone(), json!(units::fingerprint(&rec, s))))
                .collect();
            Value::Object(out)
        }
        "ru.fingerprint_and_keys" => {
            let rec = record_key(args)?;
            let out: Map<String, Value> = strings(args.get(3))
                .iter()
                .map(|s| {
                    (
                        s.clone(),
                        json!([units::fingerprint(&rec, s), units::quotation_key(&rec, s)]),
                    )
                })
                .collect();
            Value::Object(out)
        }
        _ => return Ok(None),
    }))
}

fn ro_verb(verb: &str, args: &[Value]) -> Result<Option<Value>, Fail> {
    let root = path_arg(args, 0);
    Ok(Some(match verb {
        "ro.units" => {
            let (fam, default_all) = (strings(args.get(3)), args.get(3).is_none_or(Value::is_null));
            let names: Vec<&str> = if default_all {
                owed::FAMILIES.to_vec()
            } else {
                fam.iter().map(String::as_str).collect()
            };
            unit_list(&owed::units(
                &root,
                opt_str(args, 1),
                opt_str(args, 2),
                &names,
                arg(args, 4),
            )?)
        }
        "ro.unanswered" => unit_list(&owed::unanswered(&root)?),
        "ro.merge_base" => json!(owed::merge_base(&root)),
        "ro.git" => json!(git(
            &root,
            &strings(args.get(1))
                .iter()
                .map(String::as_str)
                .collect::<Vec<_>>()
        )),
        "ro.store" => json!(owed::store(&root).to_string_lossy()),
        "ro.read_at" => {
            let rec = record_key(args)?;
            let (notes, cites) = owed::notes_of(&rec);
            json!({"notes": notes, "cites": cites})
        }
        "ro.answered" => json!(owed::answered(
            &root,
            arg(args, 1),
            arg(args, 2),
            arg(args, 3)
        )),
        "ro._read" => Value::Object(owed::read_answer(&root, arg(args, 1))),
        "ro.write_answer" => {
            owed::write_answer(&root, arg(args, 1), arg(args, 2), arg(args, 3), args.get(4))?;
            Value::Null
        }
        "ro.settle" => json!(owed::settle(
            &root,
            arg(args, 1),
            arg(args, 2),
            arg(args, 3)
        )?),
        "ro.keep_reading" => {
            owed::keep_reading(&root, arg(args, 1), arg(args, 2), arg(args, 3))?;
            Value::Null
        }
        "ro.reply_checks" => json!(owed::reply_checks(arg(args, 0))),
        "ro.fingerprints" => {
            let found = owed::fingerprints(&root, &strings(args.get(1)))?;
            Value::Object(found.into_iter().map(|(k, v)| (k, json!(v))).collect())
        }
        "ro.file_outside" => json!(owed::file_outside(&root, arg(args, 1), arg(args, 2))?),
        "ro.answer" => {
            let named = Named {
                q: arg(args, 4),
                notes: arg(args, 5),
                key: arg(args, 6),
                kind: arg(args, 7),
            };
            json!(owed::answer(
                &root,
                arg(args, 1),
                arg(args, 2),
                arg(args, 3),
                &named,
                arg(args, 8)
            )?)
        }
        _ => return Ok(None),
    }))
}

fn mo_verb(verb: &str, args: &[Value]) -> Result<Option<Value>, Fail> {
    let root = path_arg(args, 0);
    let modal = |i: usize| Modal::from_json(args.get(i).unwrap_or(&Value::Null));
    Ok(Some(match verb {
        "mo.modals_now" => modal_list(&modals::modals_now(
            &root,
            args.get(1).and_then(Value::as_bool).unwrap_or(true),
        )?),
        "mo.modals_at" => {
            let at = modals::modals_at(
                &root,
                arg(args, 1),
                args.get(2).and_then(Value::as_bool).unwrap_or(true),
            )?;
            Value::Object(at.iter().map(|(k, m)| (k.clone(), m.json())).collect())
        }
        "mo.find" => {
            let now = modals::modals_now(&root, true)?;
            modals::find(&now, arg(args, 1)).map_or(Value::Null, Modal::json)
        }
        "mo.fingerprints" => {
            let (form, research) = modals::fingerprints(&root, &modal(1))?;
            json!([form, research])
        }
        "mo.depiction_fingerprint" => json!(modals::depiction_fingerprint(&root, &modal(1))?),
        "mo.owed" => triples(modals::owed(&root, arg(args, 1), arg(args, 2))?),
        "mo.kinds_in" => Value::Array(
            modals::kinds_in(arg(args, 0))?
                .into_iter()
                .map(|(n, k, l, d)| json!([n, k, l, d]))
                .collect(),
        ),
        "mo.modal_file" => json!(modals::modal_file(arg(args, 0), arg(args, 1))),
        "mo.choice_modal" => modals::choice_modal(
            arg(args, 0),
            arg(args, 1),
            args.get(2).and_then(Value::as_bool).unwrap_or(true),
        )
        .as_ref()
        .map_or(Value::Null, Modal::json),
        "mo.depiction_owed_by" => {
            let was = args.first().filter(|v| !v.is_null()).map(Modal::from_json);
            json!(modals::depiction_owed_by(was.as_ref(), &modal(1)))
        }
        "mo.earlier_units" => json!(modals::earlier_units(&strings(args.first()))),
        _ => return Ok(None),
    }))
}

fn mt_verb(verb: &str, args: &[Value]) -> Result<Option<Value>, Fail> {
    let root = path_arg(args, 0);
    Ok(Some(match verb {
        "mt.keep" => json!(triage::keep(&root, arg(args, 1))),
        "mt.triage_only" => json!(triage::triage_only(arg(args, 0))),
        "mt.refusal" => {
            let m = Modal::from_json(args.get(1).unwrap_or(&Value::Null));
            let owed_rows = rows_of(args.get(3));
            json!(triage::refusal(
                &root,
                &m,
                arg(args, 2),
                owed_rows.as_deref()
            )?)
        }
        "mt.bundle" => match triage::bundle(&root, Path::new(arg(args, 1)), arg(args, 2))? {
            None => json!([Value::Null, 0]),
            Some((manifest, n)) => json!([manifest.to_string_lossy(), n]),
        },
        _ => return Ok(None),
    }))
}

fn constant(verb: &str) -> Option<Value> {
    Some(match verb {
        "const.QUESTIONS" => json!(units::QUESTIONS),
        "const.FORM_CHECK" => json!(modals::FORM_CHECK),
        "const.RESEARCH_CHECKS" => json!(modals::RESEARCH_CHECKS),
        "const.DEPICTION_CHECK" => json!(modals::DEPICTION_CHECK),
        "const.RESEARCH_AGENT" => json!(modals::RESEARCH_AGENT),
        "const.ORDER" => json!(modals::ORDER),
        "const.MODAL_DIRS" => json!(modals::MODAL_DIRS),
        "const.MODALS" => json!(modals::MODALS),
        "const.FIXED" => json!(owed::FIXED),
        "const.AGENT_UNITS" => {
            let out: Map<String, Value> = modals::ORDER
                .iter()
                .map(|a| ((*a).to_owned(), json!(modals::agent_units(a))))
                .collect();
            Value::Object(out)
        }
        _ => return None,
    })
}

fn answer(verb: &str, args: &[Value]) -> Result<Value, String> {
    if let Some(v) = constant(verb) {
        return Ok(v);
    }
    for family in [ru_verb, ro_verb, mo_verb, mt_verb] {
        if let Some(v) = family(verb, args)? {
            return Ok(v);
        }
    }
    if verb == "mb.research_held" {
        return Ok(json!(crate::record::bundle::modal::research_held(
            &path_arg(args, 0),
            arg(args, 1),
            arg(args, 2)
        )));
    }
    if verb == "cb.url_of" {
        return Ok(json!(crate::record::bundle::check::url_of(arg(args, 0))));
    }
    if verb == "to.owed" {
        let rows = translation::owed(&path_arg(args, 0))?;
        return Ok(Value::Array(
            rows.into_iter()
                .map(|r| json!([r.0, r.1, r.2, r.3, r.4]))
                .collect(),
        ));
    }
    Err(format!("owed-door: no verb {verb}"))
}

/// The door's loop.
pub fn serve(input: &mut dyn std::io::BufRead, output: &mut dyn std::io::Write) -> crate::Reply {
    crate::checks_door::serve_with(input, output, &answer)
}

#[cfg(test)]
mod tests;
