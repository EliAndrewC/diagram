use serde::de::IgnoredAny;
use serde_json::value::RawValue;
use std::collections::BTreeMap;
use std::time::Instant;
fn med(mut v: Vec<f64>) -> f64 {
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    v[v.len() / 2]
}
fn main() {
    let p = std::env::args().nth(1).unwrap();
    let n = 20;
    let (mut a, mut b, mut c, mut r, mut d) = (vec![], vec![], vec![], vec![], vec![]);
    for _ in 0..n {
        let t = Instant::now();
        let s = std::fs::read_to_string(&p).unwrap();
        r.push(t.elapsed().as_secs_f64() * 1e3);
        let t = Instant::now();
        let v: serde_json::Value = serde_json::from_str(&s).unwrap();
        drop(v);
        a.push(t.elapsed().as_secs_f64() * 1e3);
        let t = Instant::now();
        let m: BTreeMap<String, &RawValue> = serde_json::from_str(&s).unwrap();
        drop(m);
        b.push(t.elapsed().as_secs_f64() * 1e3);
        let t = Instant::now();
        let _: IgnoredAny = serde_json::from_str(&s).unwrap();
        c.push(t.elapsed().as_secs_f64() * 1e3);
        // the top level as raw, then every key but the heavy ones parsed
        let t = Instant::now();
        let m: BTreeMap<String, &RawValue> = serde_json::from_str(&s).unwrap();
        let mut o = serde_json::Map::new();
        for (k, v) in m {
            if k != "dispatches" && k != "versions" && k != "seen" {
                o.insert(k, serde_json::from_str(v.get()).unwrap());
            }
        }
        drop(o);
        d.push(t.elapsed().as_secs_f64() * 1e3);
    }
    let mut e = vec![];
    #[derive(serde::Deserialize)]
    #[allow(dead_code)]
    struct Row { #[serde(default)] aid: Option<serde_json::Value>, #[serde(default)] state: Option<serde_json::Value>, #[serde(default)] wave: IgnoredAny, #[serde(default)] reply: IgnoredAny }
    #[derive(serde::Deserialize)]
    #[allow(dead_code)]
    struct Top { dispatches: BTreeMap<String, Row> }
    for _ in 0..n {
        let s = std::fs::read_to_string(&p).unwrap();
        let t = Instant::now();
        let m: Top = serde_json::from_str(&s).unwrap();
        drop(m);
        e.push(t.elapsed().as_secs_f64() * 1e3);
    }
    println!("light rows {:.2}", med(e));
    struct Skip;
    impl<'de> serde::de::Visitor<'de> for Skip {
        type Value = bool;
        fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result { f.write_str("x") }
        fn visit_bool<E>(self, v: bool) -> Result<bool, E> { Ok(v) }
        fn visit_i64<E>(self, v: i64) -> Result<bool, E> { Ok(v != 0) }
        fn visit_u64<E>(self, v: u64) -> Result<bool, E> { Ok(v != 0) }
        fn visit_f64<E>(self, v: f64) -> Result<bool, E> { Ok(v != 0.0) }
        fn visit_str<E>(self, v: &str) -> Result<bool, E> { Ok(!v.is_empty()) }
        fn visit_unit<E>(self) -> Result<bool, E> { Ok(false) }
        fn visit_seq<A: serde::de::SeqAccess<'de>>(self, mut s: A) -> Result<bool, A::Error> { let mut x = false; while s.next_element::<SkipT>()?.is_some() { x = true } Ok(x) }
        fn visit_map<A: serde::de::MapAccess<'de>>(self, mut m: A) -> Result<bool, A::Error> { let mut x = false; while m.next_key::<SkipT>()?.is_some() { m.next_value::<SkipT>()?; x = true } Ok(x) }
    }
    struct SkipT;
    impl<'de> serde::Deserialize<'de> for SkipT { fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> { d.deserialize_any(Skip).map(|_| SkipT) } }
    let mut g = vec![];
    for _ in 0..n {
        let s = std::fs::read_to_string(&p).unwrap();
        let t = Instant::now();
        let _: SkipT = serde_json::from_str(&s).unwrap();
        g.push(t.elapsed().as_secs_f64() * 1e3);
    }
    println!("skip-any {:.2}", med(g));
    println!(
        "read {:.2} full-Value {:.2} raw-top {:.2} ignored {:.2} raw-top+light {:.2}",
        med(r), med(a), med(b), med(c), med(d)
    );
}
