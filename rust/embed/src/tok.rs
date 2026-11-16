//! The tokenizer as `fastembed`'s `load_tokenizer` set it up (feature 449 T138; `fastembed/common/preprocessor_utils.py`, 0.9.1):
//! `tokenizer.json` with truncation at the stricter of `tokenizer_config.json`'s `model_max_length` and `max_length`, the special tokens
//! of `special_tokens_map.json` added, and padding to the batch's longest with the pad token's id - so a batch's ids and attention mask,
//! padding included, are the ones the Python fed the model (BGE-M3's 8-bit build quantizes each batch's activations together, so a text's
//! vector depends on the batch it rides in: alone against batched, up to 0.031 apart, observed 2026-11-16, method: the probes of
//! `onnxruntime.pin` through `fastembed`).

use std::path::Path;

use serde_json::{Map, Value};
use tokenizers::{
    AddedToken, PaddingDirection, PaddingParams, PaddingStrategy, Tokenizer, TruncationDirection,
    TruncationParams,
};

/// The tokenizer's own error, in words.
fn said(e: impl std::fmt::Display) -> String {
    e.to_string()
}

fn json_file(path: &Path) -> Result<Map<String, Value>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    match serde_json::from_str(&text) {
        Ok(Value::Object(m)) => Ok(m),
        _ => Err(format!("{} is not a JSON object", path.display())),
    }
}

/// `_valid_context`: an integer limit above 0 (a bool, a float or `1e30` is none).
fn valid(v: Option<&Value>) -> Option<usize> {
    v.and_then(Value::as_u64)
        .filter(|&n| n > 0 && i64::try_from(n).is_ok())
        .and_then(|n| usize::try_from(n).ok())
}

fn side(v: Option<&Value>) -> Option<&str> {
    v.and_then(Value::as_str).filter(|s| !s.is_empty())
}

/// One entry of the special tokens map as `fastembed` adds it: a string as itself, a dict as `AddedToken(**token)`.
fn added(token: &Value) -> Option<AddedToken> {
    if let Some(s) = token.as_str() {
        return Some(AddedToken::from(s, true));
    }
    let m = token.as_object()?;
    let flag = |k: &str, default: bool| m.get(k).and_then(Value::as_bool).unwrap_or(default);
    Some(
        AddedToken::from(m.get("content")?.as_str()?, true)
            .single_word(flag("single_word", false))
            .lstrip(flag("lstrip", false))
            .rstrip(flag("rstrip", false))
            .normalized(flag("normalized", true)),
    )
}

/// The tokenizer in `dir`, set up as `fastembed` set it up.
///
/// # Errors
/// A file is missing or unreadable, or no limit or pad token can be found (`fastembed`'s own refusals).
pub fn load(dir: &Path) -> Result<Tokenizer, String> {
    let path = dir.join("tokenizer.json");
    if !path.is_file() {
        return Err(format!(
            "Could not find tokenizer.json in {}",
            dir.display()
        ));
    }
    let config_path = dir.join("tokenizer_config.json");
    if !config_path.is_file() {
        return Err(format!(
            "Could not find tokenizer_config.json in {}",
            dir.display()
        ));
    }
    let config = if dir.join("config.json").is_file() {
        json_file(&dir.join("config.json"))?
    } else {
        Map::new()
    };
    let tc = json_file(&config_path)?;
    let max = [
        valid(tc.get("model_max_length")),
        valid(tc.get("max_length")),
    ]
    .into_iter()
    .flatten()
    .min()
    .ok_or_else(|| {
        format!(
            "Could not determine the maximum context length for {}",
            dir.display()
        )
    })?;
    let special = if dir.join("special_tokens_map.json").is_file() {
        json_file(&dir.join("special_tokens_map.json"))?
    } else {
        Map::new()
    };
    let mut t = Tokenizer::from_file(&path).map_err(said)?;
    let truncation_side = side(tc.get("truncation_side")).map_or_else(
        || {
            t.get_truncation()
                .map_or(TruncationDirection::Right, |p| p.direction)
        },
        |s| {
            if s == "left" {
                TruncationDirection::Left
            } else {
                TruncationDirection::Right
            }
        },
    );
    t.with_truncation(Some(TruncationParams {
        max_length: max,
        direction: truncation_side,
        ..TruncationParams::default()
    }))
    .map_err(said)?;
    for v in special.values() {
        let tokens: Vec<AddedToken> = match v {
            Value::Array(list) => list.iter().filter_map(added).collect(),
            other => added(other).into_iter().collect(),
        };
        t.add_special_tokens(tokens).map_err(said)?;
    }
    pad(&mut t, &tc, &config, dir)?;
    Ok(t)
}

/// Padding to the batch's longest, as `fastembed` set it: the pad token and its id from the tokenizer's own padding, else the configs,
/// else the vocabulary; the side from `tokenizer_config.json`'s `padding_side`.
fn pad(
    t: &mut Tokenizer,
    tc: &Map<String, Value>,
    config: &Map<String, Value>,
    dir: &Path,
) -> Result<(), String> {
    let padding = t.get_padding().cloned();
    let pad_token = padding
        .as_ref()
        .map(|p| p.pad_token.clone())
        .or_else(|| side(tc.get("pad_token")).map(str::to_owned))
        .ok_or_else(|| format!("Could not find a pad token for {}", dir.display()))?;
    let pad_id = padding
        .as_ref()
        .map(|p| p.pad_id)
        .or_else(|| {
            config
                .get("pad_token_id")
                .and_then(Value::as_u64)
                .and_then(|n| u32::try_from(n).ok())
        })
        .or_else(|| t.token_to_id(&pad_token))
        .ok_or_else(|| {
            format!(
                "Could not resolve an id for the pad token {pad_token:?} in {}",
                dir.display()
            )
        })?;
    let direction = side(tc.get("padding_side")).map_or_else(
        || {
            padding
                .as_ref()
                .map_or(PaddingDirection::Right, |p| p.direction)
        },
        |s| {
            if s == "left" {
                PaddingDirection::Left
            } else {
                PaddingDirection::Right
            }
        },
    );
    t.with_padding(Some(PaddingParams {
        strategy: PaddingStrategy::BatchLongest,
        direction,
        pad_to_multiple_of: padding.as_ref().and_then(|p| p.pad_to_multiple_of),
        pad_id,
        pad_type_id: padding.as_ref().map_or(0, |p| p.pad_type_id),
        pad_token,
    }));
    Ok(())
}

/// One batch: its ids and attention mask, row after row, its rows and their length (`onnx_embed`'s `input_ids` and `attention_mask`).
pub struct Batch {
    pub ids: Vec<i64>,
    pub mask: Vec<i64>,
    pub rows: usize,
    pub len: usize,
}

/// `texts` encoded together, special tokens added (`encode_batch`).
///
/// # Errors
/// The tokenizer refused a text.
pub fn encode(t: &Tokenizer, texts: &[String]) -> Result<Batch, String> {
    let enc = t.encode_batch(texts.to_vec(), true).map_err(said)?;
    let len = enc.first().map_or(0, |e| e.get_ids().len());
    let mut b = Batch {
        ids: Vec::with_capacity(enc.len() * len),
        mask: Vec::with_capacity(enc.len() * len),
        rows: enc.len(),
        len,
    };
    for e in &enc {
        b.ids.extend(e.get_ids().iter().map(|&i| i64::from(i)));
        b.mask
            .extend(e.get_attention_mask().iter().map(|&i| i64::from(i)));
    }
    Ok(b)
}

#[cfg(test)]
mod tests;
