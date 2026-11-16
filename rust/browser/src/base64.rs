//! Base64, the protocol's encoding of a screenshot (feature 449 T146): decoded here rather than by a crate, since nothing else in the
//! workspace needs one.

const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/// The bytes `text` encodes (padding and whitespace ignored).
///
/// # Errors
/// A character outside the alphabet.
pub fn decode(text: &str) -> Result<Vec<u8>, String> {
    let mut out = Vec::with_capacity(text.len() / 4 * 3);
    let mut acc: u32 = 0;
    let mut bits = 0;
    for c in text.bytes() {
        if c == b'=' || c.is_ascii_whitespace() {
            continue;
        }
        let v = ALPHABET
            .iter()
            .position(|&a| a == c)
            .ok_or_else(|| format!("not base64: {:?}", char::from(c)))?;
        acc = (acc << 6) | u32::try_from(v).unwrap_or(0);
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            out.push(u8::try_from((acc >> bits) & 0xFF).unwrap_or(0));
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::decode;

    #[test]
    fn it_decodes_what_python_encodes() {
        assert_eq!(decode("aGVsbG8=").unwrap(), b"hello");
        assert_eq!(decode("aGVs\nbG8gd29ybGQ=").unwrap(), b"hello world");
        assert_eq!(decode("").unwrap(), b"");
        assert_eq!(decode("+/8=").unwrap(), vec![0xfb, 0xff]);
        assert!(decode("a*b").unwrap_err().contains("not base64"));
    }
}
