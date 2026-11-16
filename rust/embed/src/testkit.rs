//! The tests' model (feature 449 T138): a small tokenizer in BGE-M3's form (a Unigram vocabulary under Metaspace, `<s> A </s>`) and a
//! stand-in network, so every path of the crate but ONNX Runtime itself runs without the model.

use std::path::Path;

use crate::Network;

/// A tokenizer of eleven pieces, `<pad>` at 1 as XLM-R has it.
pub const TOKENIZER: &str = r#"{"version": "1.0", "truncation": null, "padding": null,
 "added_tokens": [
  {"id": 0, "content": "<s>", "single_word": false, "lstrip": false, "rstrip": false, "normalized": false, "special": true},
  {"id": 1, "content": "<pad>", "single_word": false, "lstrip": false, "rstrip": false, "normalized": false, "special": true},
  {"id": 2, "content": "</s>", "single_word": false, "lstrip": false, "rstrip": false, "normalized": false, "special": true},
  {"id": 3, "content": "<unk>", "single_word": false, "lstrip": false, "rstrip": false, "normalized": false, "special": true}],
 "normalizer": null,
 "pre_tokenizer": {"type": "Metaspace", "replacement": "▁", "prepend_scheme": "always", "split": true},
 "post_processor": {"type": "TemplateProcessing",
  "single": [{"SpecialToken": {"id": "<s>", "type_id": 0}}, {"Sequence": {"id": "A", "type_id": 0}}, {"SpecialToken": {"id": "</s>", "type_id": 0}}],
  "pair": [{"SpecialToken": {"id": "<s>", "type_id": 0}}, {"Sequence": {"id": "A", "type_id": 0}}, {"SpecialToken": {"id": "</s>", "type_id": 0}},
           {"Sequence": {"id": "B", "type_id": 0}}, {"SpecialToken": {"id": "</s>", "type_id": 0}}],
  "special_tokens": {"<s>": {"id": "<s>", "ids": [0], "tokens": ["<s>"]}, "</s>": {"id": "</s>", "ids": [2], "tokens": ["</s>"]}}},
 "decoder": null,
 "model": {"type": "Unigram", "unk_id": 3, "byte_fallback": false,
  "vocab": [["<s>", 0.0], ["<pad>", 0.0], ["</s>", 0.0], ["<unk>", 0.0], ["▁a", -1.0], ["▁b", -1.0], ["a", -2.0], ["b", -2.0],
            ["▁", -3.0], ["<mask>", 0.0], ["c", -2.0]]}}"#;

/// The model directory: the tokenizer, its config with `config`'s fields, the special tokens map `map` (none where empty).
pub fn model_dir(dir: &Path, config: &str, map: &str) {
    std::fs::create_dir_all(dir).unwrap();
    std::fs::write(dir.join("tokenizer.json"), TOKENIZER).unwrap();
    std::fs::write(dir.join("tokenizer_config.json"), config).unwrap();
    if !map.is_empty() {
        std::fs::write(dir.join("special_tokens_map.json"), map).unwrap();
    }
}

/// BGE-M3's own config and map, cut to what `fastembed` reads.
pub const CONFIG: &str = r#"{"model_max_length": 8192, "pad_token": "<pad>"}"#;
pub const MAP: &str = r#"{"bos_token": {"content": "<s>", "lstrip": false, "normalized": false, "rstrip": false, "single_word": false},
 "mask_token": {"content": "<mask>", "lstrip": true, "normalized": false, "rstrip": false, "single_word": false},
 "pad_token": "<pad>", "additional_special_tokens": ["</s>", 7]}"#;

/// A network whose first-token state is the row's ids summed, its length and its mask summed; `fail` refuses every batch.
pub struct Stand {
    pub fail: bool,
    pub batches: Vec<usize>,
}

impl Network for Stand {
    fn cls(
        &mut self,
        ids: Vec<i64>,
        mask: Vec<i64>,
        n: usize,
        len: usize,
    ) -> Result<(Vec<f32>, usize), String> {
        if self.fail {
            return Err("refused\nwhole".to_owned());
        }
        self.batches.push(n);
        let mut out = Vec::new();
        for r in 0..n {
            let row = r * len..(r + 1) * len;
            #[expect(clippy::cast_precision_loss, reason = "small test numbers")]
            out.extend([
                ids[row.clone()].iter().sum::<i64>() as f32,
                len as f32,
                mask[row].iter().sum::<i64>() as f32,
            ]);
        }
        Ok((out, 3))
    }
}
