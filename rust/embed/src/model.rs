//! ONNX Runtime, as `fastembed`'s `OnnxModel` opened it (feature 449 T138; `fastembed/common/onnx_model.py`, 0.9.1): the CPU provider,
//! `ORT_ENABLE_ALL`, intra- and inter-op threads both the thread count, the model's own inputs fed (`input_ids` always, `attention_mask`
//! and `token_type_ids` - zeros - where it declares them), its first output read and each row's first token taken (`PoolingType.CLS`).
//!
//! The one part of the crate only the real model and runtime reach: `#[cfg(not(test))]`, its lines run by the kept end-to-end case in
//! `tests/hooks/test-l7r-gate.sh` (the T146 pattern), the unit tests feeding [`crate::serve`] a stand-in [`crate::Network`].

#[cfg(not(test))]
use crate::{paths, Network, Options};

#[cfg(not(test))]
struct Ort {
    session: ort::session::Session,
    names: Vec<String>,
}

#[cfg(not(test))]
fn said(e: impl std::fmt::Display) -> String {
    format!("ONNX Runtime: {e}")
}

/// The model of `o` in the runtime of `o`.
///
/// # Errors
/// No runtime library where `o` names it (the message names the installer), or the runtime refused the model.
#[cfg(not(test))]
pub fn open(o: &Options) -> Result<Box<dyn Network>, String> {
    use ort::session::builder::GraphOptimizationLevel;
    if !o.runtime.is_file() {
        return Err(format!(
            "no ONNX Runtime at {} - run scripts/container/install-onnxruntime.sh (setup-dev-env.sh --ensure runs it)",
            o.runtime.display()
        ));
    }
    // NO TELEMETRY (found by feature 449 T138): Microsoft's Linux build of ONNX Runtime 1.31 carries the 1DS telemetry client - its
    // collector `mobile.events.data.microsoft.com` and a session file `$TMPDIR/.ses` named in the library's strings - on by default (the
    // Python wheel the same), where the `ort` crate's docs say only Windows builds send it. The runtime's own switch and the C API's
    // both turn it off, set before the environment is made.
    std::env::set_var("ORT_DISABLE_TELEMETRY", "1");
    ort::init_from(o.runtime.to_string_lossy())
        .with_telemetry(false)
        .commit()
        .map_err(said)?;
    let session = ort::session::Session::builder()
        .and_then(|b| b.with_optimization_level(GraphOptimizationLevel::Level3))
        .and_then(|b| b.with_intra_threads(o.threads))
        .and_then(|b| b.with_inter_threads(o.threads))
        .and_then(|b| b.commit_from_file(o.model_dir.join(paths::MODEL_FILE)))
        .map_err(said)?;
    let names = session.inputs.iter().map(|i| i.name.clone()).collect();
    Ok(Box::new(Ort { session, names }))
}

#[cfg(not(test))]
impl Network for Ort {
    fn cls(
        &mut self,
        ids: Vec<i64>,
        mask: Vec<i64>,
        n: usize,
        len: usize,
    ) -> Result<(Vec<f32>, usize), String> {
        use ort::value::Tensor;
        let mut inputs: Vec<(String, ort::session::SessionInputValue)> = Vec::new();
        let zeros = vec![0_i64; ids.len()];
        for name in &self.names {
            let data = match name.as_str() {
                "input_ids" => ids.clone(),
                "attention_mask" => mask.clone(),
                "token_type_ids" => zeros.clone(),
                _ => continue,
            };
            inputs.push((
                name.clone(),
                Tensor::from_array(([n, len], data)).map_err(said)?.into(),
            ));
        }
        let out = self.session.run(inputs).map_err(said)?;
        let (shape, data) = out[0].try_extract_tensor::<f32>().map_err(said)?;
        let dim = usize::try_from(shape.get(2).copied().unwrap_or(0)).unwrap_or(0);
        let width = usize::try_from(shape.get(1).copied().unwrap_or(0)).unwrap_or(0) * dim;
        let mut rows = Vec::with_capacity(n * dim);
        for b in 0..n {
            rows.extend_from_slice(&data[b * width..b * width + dim]);
        }
        Ok((rows, dim))
    }
}
