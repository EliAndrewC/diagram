//! The port's half of each page writer case (feature 449 T150; part A's lockstep, its Python half deleted by part B): [`call`] runs the
//! case's function on its arguments as the Python's `CALLS` did, and [`pj`] writes the result in the Python's `pj` shape - an object as its ordered pairs, a float by its `repr`.
//!
//! Research: the page writer's lockstep calls - NONE: the port's functions run on the cases, deciding nothing about a building

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::{Arc, Mutex};

use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::Error;
use l7r_guard::shared::pyjson::py_float;
use serde_json::{json, Map, Value};

use crate::notes::{self, MapNotes};
use crate::page::{self, hits, Page};
use crate::place;
use crate::raster::{self, Host, Rendered};
use crate::sheet::page as sp;
use crate::tags::{ClsTag, Key};

/// What a case runs against: the repository, the two vocabularies and the renderer.
pub struct World {
    pub tree: std::path::PathBuf,
    pub hamlet: Vec<FeatureClass>,
    pub sheet: Vec<FeatureClass>,
}

/// A value in the Python's `pj` shape.
#[must_use]
pub fn pj(v: &Value) -> Value {
    match v {
        Value::Number(n) if n.is_f64() => {
            Value::String(format!("f:{}", py_float(n.as_f64().unwrap_or(0.0))))
        }
        Value::Array(items) => Value::Array(items.iter().map(pj).collect()),
        Value::Object(map) => {
            json!({"d": map.iter().map(|(k, x)| json!([k, pj(x)])).collect::<Vec<_>>()})
        }
        other => other.clone(),
    }
}

/// A tag from its JSON form (the Python's `tag_of`): a list is `Parts`, an object a planted key or a `Split`, text a key, null none.
#[must_use]
pub fn tag_of(j: &Value) -> ClsTag {
    let key = |v: &Value| match v.get("planted").and_then(Value::as_str) {
        Some(k) => Some(Key {
            name: k.to_owned(),
            planted: true,
        }),
        None => v.as_str().map(Key::plain),
    };
    match j {
        Value::Array(parts) => ClsTag::Parts(
            parts
                .iter()
                .map(|p| (key(&p[0]), super::text_of(&p[1])))
                .collect(),
        ),
        Value::Object(m) if !m.contains_key("planted") => ClsTag::Split {
            fill: super::text_of(&m["fill"]),
            stroke: super::text_of(&m["stroke"]),
        },
        other => key(other).map_or(ClsTag::Unruled, ClsTag::Key),
    }
}

fn texts(v: &Value) -> Vec<String> {
    v.as_array()
        .into_iter()
        .flatten()
        .map(super::text_of)
        .collect()
}

fn tags(v: &Value) -> Vec<ClsTag> {
    v.as_array().into_iter().flatten().map(tag_of).collect()
}

fn set(v: &Value) -> BTreeSet<String> {
    texts(v).into_iter().collect()
}

fn pairs(v: &Value) -> notes::Dict {
    v.as_array()
        .into_iter()
        .flatten()
        .map(|p| (super::text_of(&p[0]), super::text_of(&p[1])))
        .collect()
}

fn vb(v: &Value) -> raster::Viewbox {
    let f = |i: usize| v[i].as_f64().unwrap_or(0.0);
    (f(0), f(1), f(2), f(3))
}

fn notes_json(n: &MapNotes) -> Value {
    let d =
        |p: &notes::Dict| json!({"d": p.iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>()});
    json!({"d": [["place", d(&n.place)], ["features", d(&n.features)]]})
}

fn census_json(c: &sp::Census) -> Value {
    json!({"d": [
        ["counts", {"d": c.counts.iter().map(|(k, n)| json!([k, n])).collect::<Vec<_>>()}],
        ["unclassed", c.unclassed], ["unregistered", c.unregistered],
    ]})
}

/// A sheet's pieces as the Python's `tag_json` writes them: each carries a key or none.
fn pieces_json(ps: &[sp::Piece]) -> Value {
    let key = |t: &ClsTag| t.as_key().map(|k| k.name.clone());
    Value::Array(ps.iter().map(|(s, t, w)| json!([s, key(t), w])).collect())
}

/// A host whose renders are kept, and the log they are kept in.
fn logged(_: &World) -> (Host, Arc<Mutex<Vec<Rendered>>>) {
    let log = Arc::new(Mutex::new(Vec::new()));
    let host = Host {
        vars: Vec::new(),
        log: Some(Arc::clone(&log)),
    };
    (host, log)
}

/// `{"out": ..., "renders": [...]}`, the renders sorted as the Python sorts its list.
fn rendered(out: &Value, log: &Mutex<Vec<Rendered>>) -> Value {
    let mut rows: Vec<Value> = log
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner)
        .iter()
        .map(|(d, a, p)| json!([d, a, p]))
        .collect();
    rows.sort_by_key(ToString::to_string);
    json!({"d": [["out", out], ["renders", rows]]})
}

fn bytes(b: Option<&[u8]>) -> Value {
    b.map_or(Value::Null, |b| json!({"b64": raster::encode::base64(b)}))
}

impl World {
    /// A value `load(ref)` reads: a file of the repository, or a key of it, or the value itself.
    fn load(&self, r: &Value) -> Value {
        let Some(path) = r.get("file").and_then(Value::as_str) else {
            return r.clone();
        };
        let text = std::fs::read_to_string(self.tree.join(path)).unwrap_or_default();
        let v: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
        match r.get("key").and_then(Value::as_str) {
            Some(k) => v.get(k).cloned().unwrap_or(Value::Null),
            None => v,
        }
    }

    /// A notes text `txt(ref)` reads.
    fn txt(&self, r: &Value) -> String {
        match r.get("file").and_then(Value::as_str) {
            Some(path) => std::fs::read_to_string(self.tree.join(path)).unwrap_or_default(),
            None => super::text_of(r),
        }
    }

    fn reg(&self, name: &Value) -> &[FeatureClass] {
        if name.as_str() == Some("hamlet") {
            &self.hamlet
        } else {
            &self.sheet
        }
    }

    fn kind(&self, scale: &Value) -> Result<place::Kind, Error> {
        let scale = super::text_of(scale);
        place::kinds(&self.tree)?
            .into_iter()
            .find(|(k, _)| *k == scale)
            .map(|(_, k)| k)
            .ok_or_else(|| Error::new("KeyError", scale))
    }

    /// A sheet's page, no picture, as the Python's `sheet_page_of` writes it.
    fn sheet_page(&self, svg: &str) -> Result<String, Error> {
        let ps = sp::pieces(svg)?;
        let mut strings: Vec<String> = ps.iter().map(|p| p.0.clone()).collect();
        strings[0] = strings[0].replacen("<svg ", "<svg data-sheet=\"mode-a\" ", 1);
        let within: Vec<Vec<String>> = ps.iter().map(|p| p.2.clone()).collect();
        let p = Page {
            strings,
            tags: ps.into_iter().map(|p| p.1).collect(),
            name: "Fixture",
            meta: None,
            manifest: None,
            notes: MapNotes::default(),
            with_raster: false,
            registry: &self.sheet,
            within: Some(&within),
        };
        page::render_page(&self.tree, &raster::Host::default(), &p)
    }

    fn render(&self, a: &[Value]) -> Result<Value, Error> {
        let (host, log) = logged(self);
        let meta = self.load(&a[3]);
        let manifest = self.load(&a[4]);
        let within: Option<Vec<Vec<String>>> =
            a[8].as_array().map(|w| w.iter().map(texts).collect());
        let p = Page {
            strings: texts(&a[0]),
            tags: tags(&a[1]),
            name: a[2].as_str().unwrap_or_default(),
            meta: meta.as_object(),
            manifest: (!manifest.is_null()).then_some(&manifest),
            notes: notes::parse_map_notes(&self.txt(&a[5])),
            with_raster: a[6].as_bool().unwrap_or(false),
            registry: self.reg(&a[7]),
            within: within.as_deref(),
        };
        let html = page::render_page(&self.tree, &host, &p)?;
        Ok(rendered(&json!(html), &log))
    }

    /// The port's result of one case, in the Python's shape.
    ///
    /// # Errors
    /// The port's refusal, compared with the Python's by its last traceback line.
    #[expect(
        clippy::too_many_lines,
        reason = "one arm per case name, each the Python's `CALLS` entry"
    )]
    pub fn call(&self, case: &Value) -> Result<Value, Error> {
        let name = case[0].as_str().unwrap_or_default().trim_start_matches('!');
        let a: &[Value] = case.as_array().map_or(&[], |c| &c[1..]);
        let empty = Map::new();
        let obj = |v: &Value| v.as_object().cloned().unwrap_or_default();
        Ok(match name {
            "merge" => json!(page::merge_primitives(&super::text_of(&a[0]))?),
            "hit_copies" => {
                let w = a.get(1).map_or(hits::HIT_DEFAULT, |w| {
                    (
                        w[0].as_f64().unwrap_or(0.0),
                        w[1].as_f64().unwrap_or(0.0),
                        w[2].as_f64().unwrap_or(0.0),
                    )
                });
                json!(hits::hit_copies(&super::text_of(&a[0]), w)?)
            }
            "wrap" => json!(hits::wrap(&super::text_of(&a[0]), &tag_of(&a[1]))?),
            "part_of" => json!(hits::part_of(&super::text_of(&a[0]), &texts(&a[1]))?),
            "census" => {
                let (ss, ts) = (texts(&a[0]), tags(&a[1]));
                if ss.len() != ts.len() {
                    return Err(Error::new(
                        "ValueError",
                        "zip() argument 2 is longer than argument 1",
                    ));
                }
                let (counts, unclassed) = page::ink_census(&ss, &ts);
                json!([{"d": counts.iter().map(|(k, n)| json!([k, n])).collect::<Vec<_>>()}, unclassed])
            }
            "present" => json!(page::present_classes(&tags(&a[0]))),
            "unregistered" => {
                let counts: Vec<(String, i64)> = a[0]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .map(|p| (super::text_of(&p[0]), p[1].as_i64().unwrap_or(0)))
                    .collect();
                json!(page::unregistered_classes(&counts, self.reg(&a[1])))
            }
            "hit_regions" => json!(hits::hit_regions(Some(&self.load(&a[0])), &set(&a[1]))?),
            "hit_layer" => {
                let top = texts(&a[3]);
                let top: Vec<&str> = top.iter().map(String::as_str).collect();
                json!(hits::hit_layer_with(
                    &texts(&a[0]),
                    &tags(&a[1]),
                    Some(&self.load(&a[2])),
                    &top
                )?)
            }
            "keep_clear" => {
                let (clip, attr) = hits::keep_clear_clip(Some(&self.load(&a[0])))?;
                json!([clip, attr])
            }
            "explain" => {
                let meta = self.load(&a[3]);
                let data = page::explanations(
                    &self.tree,
                    &set(&a[0]),
                    &notes::parse_map_notes(&self.txt(&a[1])),
                    self.reg(&a[2]),
                    meta.as_object().unwrap_or(&empty),
                )?;
                let glossary =
                    page::glossary_for(&data, &l7r_gate_research::glossary::load(&self.tree)?);
                pj(&json!({"data": data, "glossary": glossary}))
            }
            "render" => self.render(a)?,
            "place_card" => {
                let card = place::place_card(
                    &self.tree,
                    &obj(&self.load(&a[0])),
                    &set(&a[1]),
                    &notes::parse_map_notes(&self.txt(&a[2])),
                    &self.load(&a[3]),
                )?;
                pj(&card.unwrap_or(Value::Null))
            }
            "size_sentence" => json!(place::size_sentence(
                &self.kind(&a[0])?,
                &obj(&self.load(&a[1])),
                a[2].as_i64().unwrap_or(0)
            )?),
            "where" => json!(place::where_sentences(
                &super::text_of(&a[0]),
                &pairs(&a[1])
            )),
            "lane_default" => json!(place::lane_default(&super::text_of(&a[0]), &pairs(&a[1]))),
            "windbreak" => json!(place::windbreak_default(&obj(&self.load(&a[0])))),
            "retirement" => json!(place::retirement_fact(&obj(&self.load(&a[0])))),
            "grove" => json!(place::homestead_grove_default(&obj(&self.load(&a[0])))),
            "crops" => json!(place::crop_sentence(&self.tree, &set(&a[0]))?),
            "join" => json!(place::join(&texts(&a[0]))),
            "dwellings_shown" => json!(place::dwellings_shown(
                &self.load(&a[0]),
                &self.kind(&a[1])?
            )?),
            "kinds" => {
                let ks = place::kinds(&self.tree)?;
                pj(&Value::Object(ks.into_iter().map(|(k, v)| (k, json!({
                    "noun": v.noun, "what": v.what, "houses_noun": v.houses_noun, "excludes_farms": v.excludes_farms,
                    "population_note": v.population_note, "default_population": v.default_population,
                }))).collect()))
            }
            "notes" => notes_json(&notes::parse_map_notes(&super::text_of(&a[0]))),
            "read_notes" => notes_json(&notes::read_map_notes(
                &self.tree.join(super::text_of(&a[0])),
            )),
            "section" => json!(notes::section(
                &super::text_of(&a[0]),
                &super::text_of(&a[1])
            )),
            "viewbox" => pj(&json!(
                raster::viewbox_of(&super::text_of(&a[0]))?.map(|v| [v.0, v.1, v.2, v.3])
            )),
            "drop_offmap" => json!(raster::drop_offmap(&super::text_of(&a[0]), vb(&a[1]))?),
            "tile_count" => json!(raster::tile_count(vb(&a[0]), a[1].as_f64().unwrap_or(0.0))?),
            "tile_boxes" => {
                let boxes = raster::tile_boxes(vb(&a[0]), a[1].as_i64().unwrap_or(0))?;
                pj(&json!(boxes
                    .iter()
                    .map(|(i, j, b)| json!([i, j, [b.0, b.1, b.2, b.3]]))
                    .collect::<Vec<_>>()))
            }
            "tile_doc" => json!(raster::tile_doc(
                &raster::prepare_doc(&super::text_of(&a[0]))?,
                vb(&a[1])
            )),
            "class_keys" => json!(raster::class_keys(&super::text_of(&a[0]))),
            "recolor" => json!(raster::recolor_group(
                &super::text_of(&a[0]),
                &super::text_of(&a[1])
            )),
            "unpaint" => json!(raster::unpaint(&super::text_of(&a[0]))),
            "without_text" => json!(raster::without_text(&super::text_of(&a[0]))),
            "id_map" => {
                let (host, log) = logged(self);
                let svg = super::text_of(&a[0]);
                let (png, palette) = raster::id_map(
                    &host,
                    &svg,
                    &raster::class_keys(&svg),
                    a[1].as_bool().unwrap_or(false),
                )?;
                let palette =
                    json!({"d": palette.iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>()});
                rendered(&json!([bytes(Some(&png)), palette]), &log)
            }
            "picture" => {
                let (host, log) = logged(self);
                let tiles = a[2].as_i64();
                let pic = raster::picture(
                    &host,
                    &super::text_of(&a[0]),
                    a[1].as_f64().unwrap_or(0.0),
                    tiles,
                )?;
                rendered(&bytes(Some(&pic)), &log)
            }
            "palette" => {
                let (r, g) = raster::palette_rgb(a[0].as_i64().unwrap_or(0));
                json!([[r, g], raster::palette_key(r, g)])
            }
            "refuse" => {
                let host = Host {
                    vars: a[1]
                        .as_str()
                        .map(|s| vec![("DIAGRAM_SKIP_RENDER".to_owned(), s.to_owned())])
                        .unwrap_or_default(),
                    ..Host::default()
                };
                host.refuse_render_in_a_test(
                    "the page's raster picture",
                    a[0].as_f64().unwrap_or(0.0),
                )?;
                Value::Null
            }
            "data_uri" => json!(raster::data_uri(
                &super::text_of(&a[0]),
                super::text_of(&a[1]).as_bytes()
            )),
            "pieces" => pieces_json(&sp::pieces(&super::text_of(&a[0]))?),
            "sheet_page" => json!(self.sheet_page(&super::text_of(&a[0]))?),
            "sheet_census" => census_json(&sp::census(&super::text_of(&a[0]), &self.sheet)?),
            "title_of" => json!(sp::title_of(&super::text_of(&a[0]))),
            // the last name a case has: `consts`
            _ => super::consts::consts(&self.tree)?,
        })
    }
}

/// The page writer's result for one pool sheet, as `page_sheet(path)` returns it: the text the page is drawn from (the Python's, where its
/// generator places captions, handed here), the pieces, the page and its renders, the census.
///
/// # Errors
/// The port's refusal.
pub fn page_sheet(w: &World, path: &Path, text: &str, placed: bool) -> Result<Value, Error> {
    let ps = sp::pieces(text)?;
    let mut strings: Vec<String> = ps.iter().map(|p| p.0.clone()).collect();
    strings[0] = strings[0].replacen("<svg ", "<svg data-sheet=\"mode-a\" ", 1);
    let within: Vec<Vec<String>> = ps.iter().map(|p| p.2.clone()).collect();
    let (host, log) = logged(w);
    let name = sp::title_of(&path.to_string_lossy());
    let base = path.to_string_lossy();
    let notes = notes::read_map_notes(Path::new(&format!("{}.notes.md", &base[..base.len() - 4])));
    let p = Page {
        strings,
        tags: ps.iter().map(|p| p.1.clone()).collect(),
        name: &name,
        meta: None,
        manifest: None,
        notes,
        with_raster: true,
        registry: &w.sheet,
        within: Some(&within),
    };
    let html = page::render_page(&w.tree, &host, &p)?;
    let census = sp::census(text, &w.sheet)?;
    let renders = rendered(&Value::Null, &log)["d"][1][1].clone();
    Ok(
        json!({"text": placed.then_some(text), "pieces": pieces_json(&ps), "html": html, "census": census_json(&census), "renders": renders}),
    )
}
