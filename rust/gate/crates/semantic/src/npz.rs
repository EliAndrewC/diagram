//! A shard of the index as `semantic_index.py`'s `save_shard` wrote it and `load_shard` read it (feature 449 T138): `np.savez` of four
//! arrays - `fps` (`<U20`), `vecs` (`<f2`, rows of 1,024), `paths` (`<U` its longest), `spans` (`<i8`, rows of two) - a zip whose members
//! are stored, not compressed, each an `.npy` file. Read here from any zip `np.savez` writes (its local headers carry the zip64 extra
//! `force_zip64` puts there); written as numpy writes the `.npy` members, byte for byte, in a plain stored zip whose times are the
//! write's (Python's are too, so no two writes of a shard were ever the same bytes: the index is compared by its arrays, never its files).

use std::path::Path;

use crate::{Error, Result};

/// One shard's arrays: `vecs` as half-precision bits, `rows * dim`.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Shard {
    pub fps: Vec<String>,
    pub vecs: Vec<u16>,
    pub dim: usize,
    pub paths: Vec<String>,
    pub spans: Vec<[i64; 2]>,
}

fn bad(what: &str, path: &Path) -> Error {
    Error(format!("{}: {what}", path.display()))
}

fn u16_at(b: &[u8], at: usize) -> Option<usize> {
    Some(usize::from(u16::from_le_bytes(
        b.get(at..at + 2)?.try_into().ok()?,
    )))
}

fn u32_at(b: &[u8], at: usize) -> Option<usize> {
    usize::try_from(u32::from_le_bytes(b.get(at..at + 4)?.try_into().ok()?)).ok()
}

/// The stored members of a zip: (name, bytes), in the central directory's order.
fn members<'a>(z: &'a [u8], path: &Path) -> Result<Vec<(String, &'a [u8])>> {
    let tail = z.len().saturating_sub(65_557);
    let end = (tail..z.len().saturating_sub(21))
        .rev()
        .find(|&i| z[i..].starts_with(&[0x50, 0x4b, 5, 6]))
        .ok_or_else(|| bad("File is not a zip file", path))?;
    let count = u16_at(z, end + 10).unwrap_or(0);
    let mut at = u32_at(z, end + 16).unwrap_or(usize::MAX);
    let mut out = Vec::new();
    for _ in 0..count {
        let entry = (|| {
            if !z.get(at..)?.starts_with(&[0x50, 0x4b, 1, 2]) {
                return None;
            }
            let method = u16_at(z, at + 10)?;
            let size = u32_at(z, at + 20)?;
            let (n, e, c) = (
                u16_at(z, at + 28)?,
                u16_at(z, at + 30)?,
                u16_at(z, at + 32)?,
            );
            let local = u32_at(z, at + 42)?;
            let name = String::from_utf8_lossy(z.get(at + 46..at + 46 + n)?).into_owned();
            let start = local + 30 + u16_at(z, local + 26)? + u16_at(z, local + 28)?;
            at += 46 + n + e + c;
            Some((name, method, z.get(start..start + size)?))
        })()
        .ok_or_else(|| bad("a damaged zip directory", path))?;
        if entry.1 != 0 {
            return Err(bad("a compressed member (np.savez stores them)", path));
        }
        out.push((entry.0, entry.2));
    }
    Ok(out)
}

/// One `.npy` member: its `descr`, its shape and its data.
fn npy<'a>(b: &'a [u8], path: &Path) -> Result<(String, Vec<usize>, &'a [u8])> {
    if !b.starts_with(b"\x93NUMPY") || b.len() < 10 {
        return Err(bad("an array member that is not .npy", path));
    }
    let (len, at) = if b[6] == 1 {
        (u16_at(b, 8).unwrap_or(0), 10)
    } else {
        (u32_at(b, 8).unwrap_or(0), 12)
    };
    let header = String::from_utf8_lossy(b.get(at..at + len).unwrap_or_default()).into_owned();
    let field = |key: &str| {
        let i = header.find(&format!("'{key}':"))? + key.len() + 3;
        Some(header[i..].trim_start().to_owned())
    };
    let descr = field("descr")
        .and_then(|d| d.strip_prefix('\'')?.split('\'').next().map(str::to_owned))
        .unwrap_or_default();
    if field("fortran_order").is_some_and(|f| f.starts_with("True")) {
        return Err(bad("a Fortran-ordered array", path));
    }
    let shape = field("shape")
        .and_then(|s| Some(s.strip_prefix('(')?.split(')').next()?.to_owned()))
        .unwrap_or_default()
        .split(',')
        .filter_map(|n| n.trim().parse().ok())
        .collect();
    Ok((descr, shape, b.get(at + len..).unwrap_or_default()))
}

/// A `<U{n}` array's strings, numpy's trailing NULs dropped.
fn strings(descr: &str, shape: &[usize], data: &[u8], path: &Path) -> Result<Vec<String>> {
    let width = descr
        .strip_prefix("<U")
        .and_then(|n| n.parse::<usize>().ok())
        .ok_or_else(|| bad(&format!("strings of type {descr}"), path))?;
    let rows = shape.first().copied().unwrap_or(0);
    let mut out = Vec::with_capacity(rows);
    for r in 0..rows {
        let cell = data
            .get(r * width * 4..(r + 1) * width * 4)
            .ok_or_else(|| bad("a short string array", path))?;
        let mut s: String = cell
            .chunks(4)
            .map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]]))
            .map(|u| char::from_u32(u).unwrap_or('\u{fffd}'))
            .collect();
        s.truncate(s.trim_end_matches('\0').len());
        out.push(s);
    }
    Ok(out)
}

/// The shard at `path`, or none where there is no file (`load_shard`).
///
/// # Errors
/// The file cannot be read or is not a shard `np.savez` wrote.
pub fn read(path: &Path) -> Result<Option<Shard>> {
    if !path.is_file() {
        return Ok(None);
    }
    let z = std::fs::read(path).map_err(|e| bad(&e.to_string(), path))?;
    let mut s = Shard::default();
    for (name, body) in members(&z, path)? {
        let (descr, shape, data) = npy(body, path)?;
        match name.as_str() {
            "fps.npy" => s.fps = strings(&descr, &shape, data, path)?,
            "paths.npy" => s.paths = strings(&descr, &shape, data, path)?,
            "vecs.npy" if descr == "<f2" => {
                s.dim = shape.get(1).copied().unwrap_or(0);
                let n = shape.first().copied().unwrap_or(0) * s.dim;
                s.vecs = data
                    .chunks(2)
                    .take(n)
                    .map(|c| u16::from_le_bytes([c[0], c.get(1).copied().unwrap_or(0)]))
                    .collect();
            }
            "spans.npy" if descr == "<i8" => {
                s.spans = data
                    .chunks(16)
                    .take(shape.first().copied().unwrap_or(0))
                    .map(|c| {
                        let at =
                            |i: usize| i64::from_le_bytes(c[i..i + 8].try_into().unwrap_or([0; 8]));
                        [at(0), at(8)]
                    })
                    .collect();
            }
            other => {
                return Err(bad(
                    &format!("an unexpected member {other} ({descr})"),
                    path,
                ))
            }
        }
    }
    Ok(Some(s))
}

/// numpy's `.npy` file of `descr`, `shape` and `data` (`format.write_array`, version 1.0: the header's keys sorted, room for the first
/// axis to grow to 21 digits, padded to 64 bytes with spaces and a newline).
fn npy_file(descr: &str, shape: &[usize], data: &[u8]) -> Vec<u8> {
    let dims = match shape {
        [n] => format!("({n},)"),
        _ => format!(
            "({})",
            shape
                .iter()
                .map(ToString::to_string)
                .collect::<Vec<_>>()
                .join(", ")
        ),
    };
    let mut header = format!("{{'descr': '{descr}', 'fortran_order': False, 'shape': {dims}, }}");
    let first = shape.first().map_or(0, |n| n.to_string().len());
    header.push_str(&" ".repeat(21usize.saturating_sub(first)));
    let hlen = header.len() + 1;
    let pad = 64 - (10 + hlen) % 64;
    let mut out = b"\x93NUMPY\x01\x00".to_vec();
    out.extend(u16::try_from(hlen + pad).unwrap_or(u16::MAX).to_le_bytes());
    out.extend(header.as_bytes());
    out.extend(std::iter::repeat_n(b' ', pad));
    out.push(b'\n');
    out.extend(data);
    out
}

/// `np.array(rows, dtype=str)`, its width its longest (at least one), or `dtype="U<fixed>"`.
fn unicode(rows: &[String], fixed: Option<usize>) -> (String, Vec<u8>) {
    let longest = rows
        .iter()
        .map(|s| s.chars().count())
        .max()
        .unwrap_or(0)
        .max(1);
    let width = fixed.unwrap_or(longest);
    let mut data = Vec::with_capacity(rows.len() * width * 4);
    for s in rows {
        let n = s.chars().count().min(width);
        data.extend(
            s.chars()
                .take(width)
                .flat_map(|c| u32::from(c).to_le_bytes()),
        );
        data.extend(std::iter::repeat_n(0, (width - n) * 4));
    }
    (format!("<U{width}"), data)
}

/// `zlib.crc32`.
fn crc32(data: &[u8]) -> u32 {
    let mut crc = !0u32;
    for &b in data {
        crc ^= u32::from(b);
        for _ in 0..8 {
            crc = if crc & 1 == 1 {
                (crc >> 1) ^ 0xEDB8_8320
            } else {
                crc >> 1
            };
        }
    }
    !crc
}

/// A stored zip of `files`, its times `(date, time)` in DOS form.
fn zip(files: &[(&str, Vec<u8>)], when: (u16, u16)) -> Vec<u8> {
    let mut out = Vec::new();
    let mut central = Vec::new();
    let le16 = |v: usize| u16::try_from(v).unwrap_or(u16::MAX).to_le_bytes();
    let le32 = |v: usize| u32::try_from(v).unwrap_or(u32::MAX).to_le_bytes();
    for (name, body) in files {
        let offset = out.len();
        let crc = crc32(body).to_le_bytes();
        let common = |out: &mut Vec<u8>| {
            out.extend([20, 0, 0, 0, 0, 0]);
            out.extend(when.1.to_le_bytes());
            out.extend(when.0.to_le_bytes());
            out.extend(crc);
            out.extend(le32(body.len()));
            out.extend(le32(body.len()));
            out.extend(le16(name.len()));
            out.extend([0, 0]);
        };
        out.extend([0x50, 0x4b, 3, 4]);
        common(&mut out);
        out.extend(name.as_bytes());
        out.extend(body);
        central.extend([0x50, 0x4b, 1, 2, 20, 3]);
        common(&mut central);
        // no comment, disk 0, no internal attributes, a regular file's mode 0o100644 as the external ones
        central.extend([0, 0, 0, 0, 0, 0, 0, 0, 0xa4, 0x81]);
        central.extend(le32(offset));
        central.extend(name.as_bytes());
    }
    let at = out.len();
    out.extend(&central);
    out.extend([0x50, 0x4b, 5, 6, 0, 0, 0, 0]);
    out.extend(le16(files.len()));
    out.extend(le16(files.len()));
    out.extend(le32(central.len()));
    out.extend(le32(at));
    out.extend([0, 0]);
    out
}

/// The DOS date and time of `secs` since the epoch, in UTC (the container's local time).
#[must_use]
pub fn dos_time(secs: u64) -> (u16, u16) {
    let days = i64::try_from(secs / 86_400).unwrap_or(0);
    let rem = secs % 86_400;
    // the civil date of a day count (Howard Hinnant's `civil_from_days`)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let day_of_era = z - era * 146_097;
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let mp = (5 * day_of_year + 2) / 153;
    let d = day_of_year - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = year_of_era + era * 400 + i64::from(m <= 2);
    let date = ((y - 1980).clamp(0, 127) << 9) | (m << 5) | d;
    let time = ((rem / 3600) << 11) | (((rem % 3600) / 60) << 5) | ((rem % 60) / 2);
    (
        u16::try_from(date).unwrap_or(0),
        u16::try_from(time).unwrap_or(0),
    )
}

/// `save_shard`: the four arrays written to `path`, its folder made.
///
/// # Errors
/// The folder or the file cannot be written.
pub fn write(path: &Path, s: &Shard, when: (u16, u16)) -> Result<()> {
    let (fd, fdata) = unicode(&s.fps, Some(20));
    let (pd, pdata) = unicode(&s.paths, None);
    let vdata: Vec<u8> = s.vecs.iter().flat_map(|v| v.to_le_bytes()).collect();
    let sdata: Vec<u8> = s
        .spans
        .iter()
        .flat_map(|[a, b]| a.to_le_bytes().into_iter().chain(b.to_le_bytes()))
        .collect();
    let rows = s.fps.len();
    let files = [
        ("fps.npy", npy_file(&fd, &[rows], &fdata)),
        ("vecs.npy", npy_file("<f2", &[rows, s.dim], &vdata)),
        ("paths.npy", npy_file(&pd, &[s.paths.len()], &pdata)),
        ("spans.npy", npy_file("<i8", &[s.spans.len(), 2], &sdata)),
    ];
    let dir = path.parent().unwrap_or(Path::new("."));
    std::fs::create_dir_all(dir).map_err(|e| bad(&e.to_string(), dir))?;
    std::fs::write(path, zip(&files, when)).map_err(|e| bad(&e.to_string(), path))
}

/// The half-precision `h` as a float (numpy's `npy_halfbits_to_floatbits`).
#[must_use]
pub fn half_to_f32(h: u16) -> f32 {
    let sign = u32::from(h & 0x8000) << 16;
    let exp = h & 0x7c00;
    let sig = u32::from(h & 0x03ff);
    let bits = match exp {
        0 if sig == 0 => sign,
        0 => {
            let mut sig = sig << 1;
            let mut e = 0u32;
            while sig & 0x0400 == 0 {
                sig <<= 1;
                e += 1;
            }
            sign + ((127 - 15 - e) << 23) + ((sig & 0x03ff) << 13)
        }
        0x7c00 => sign + 0x7f80_0000 + (sig << 13),
        _ => sign + ((u32::from(h & 0x7fff) + 0x1_c000) << 13),
    };
    f32::from_bits(bits)
}

/// The float `x` in half precision, rounded to nearest even (numpy's `npy_floatbits_to_halfbits`, the `astype(np.float16)` of
/// `save_shard`).
#[must_use]
pub fn f32_to_half(x: f32) -> u16 {
    let f = x.to_bits();
    let sign = u16::try_from((f >> 16) & 0x8000).unwrap_or(0);
    let exp = f & 0x7f80_0000;
    let low = |v: u32| u16::try_from(v & 0xffff).unwrap_or(0);
    if exp >= 0x4780_0000 {
        let sig = f & 0x007f_ffff;
        if exp == 0x7f80_0000 && sig != 0 {
            let r = 0x7c00 + low(sig >> 13);
            return sign + if r == 0x7c00 { r + 1 } else { r };
        }
        return sign + 0x7c00;
    }
    if exp <= 0x3800_0000 {
        if exp < 0x3300_0000 {
            return sign;
        }
        let mut sig = (0x0080_0000 + (f & 0x007f_ffff)) >> (113 - (exp >> 23));
        if (sig & 0x3fff) != 0x1000 || (f & 0x7ff) != 0 {
            sig += 0x1000;
        }
        return sign + low(sig >> 13);
    }
    let h_exp = low((exp - 0x3800_0000) >> 13);
    let mut sig = f & 0x007f_ffff;
    if (sig & 0x3fff) != 0x1000 {
        sig += 0x1000;
    }
    sign + (h_exp + low(sig >> 13))
}

#[cfg(test)]
mod tests;
