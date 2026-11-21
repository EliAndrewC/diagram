//! What the ported Python said when it failed (feature 449 T168): an exception it did not catch ended the run with a traceback whose last
//! line is `<class>: <message>` and exit 1, so the port prints that line and exits 1 - the frames above it name Python files that no
//! longer exist. The differential (FR-002) compares the line byte for byte, the frames stripped.
//!
//! And what the ported Python computed and printed with its own built-ins (T170, T174, T175): `float()`, `min`, `max`, `sum`, `round`,
//! `int`, `//`, `%`, `** 0.5`, `math.hypot`, a fixed, grouped or `g` format - each as `CPython` reckons it, to the bit, so a port's figure
//! and its printing are the Python's (the locksteps hold them so).
//!
//! Research:
//!     the ported Python's failures and arithmetic - NONE: how an error is printed, and Python's float arithmetic, rounding and formatting reproduced to the bit, deciding nothing about a building

use l7r_gate_research::{digit_value, Error};
use l7r_shared::py_text::{py_float_text, repr};
use serde_json::Value;

/// The last line of the traceback `err` would have ended a Python run with: a `KeyError`'s message is its key's `repr`.
#[must_use]
pub fn uncaught(err: &Error) -> String {
    let message = if err.kind == "KeyError" {
        l7r_shared::py_text::repr(&err.message)
    } else {
        err.message.clone()
    };
    if message.is_empty() {
        format!("{}\n", err.kind)
    } else {
        format!("{}: {message}\n", err.kind)
    }
}

/// The `OSError` subclass and message Python's `open(path)` raised for `err`: `[Errno N] <strerror>: '<path>'`.
#[must_use]
pub fn os_error(err: &std::io::Error, path: &str) -> Error {
    if err.kind() == std::io::ErrorKind::InvalidData {
        // `l7r_gate_core::record::read_text`'s word for bytes that are not UTF-8; the codec's own words name a byte and a position the
        // differential normalizes as the library's
        return Error::new(
            "UnicodeDecodeError",
            "'utf-8' codec can't decode the file: invalid utf-8",
        );
    }
    let code = err.raw_os_error().unwrap_or(0);
    let kind = match code {
        2 => "FileNotFoundError",
        13 | 1 => "PermissionError",
        20 => "NotADirectoryError",
        21 => "IsADirectoryError",
        _ => "OSError",
    };
    let text = err.to_string();
    let strerror = text.split(" (os error").next().unwrap_or(&text);
    Error::new(
        kind,
        format!(
            "[Errno {code}] {strerror}: {}",
            l7r_shared::py_text::repr(path)
        ),
    )
}

/// Python's type name of what `json.load` made of `value`, for a `TypeError` or `AttributeError`.
#[must_use]
pub fn type_name(value: &Value) -> &'static str {
    match value {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// What a Python `for x in value` walks: a list's items, a string's characters, a dict's keys; anything else is the `TypeError`.
///
/// # Errors
/// `value` is `None`, a bool or a number.
pub fn iterate(value: &Value) -> Result<Vec<Value>, Error> {
    match value {
        Value::Array(items) => Ok(items.clone()),
        Value::String(s) => Ok(s.chars().map(|c| Value::from(c.to_string())).collect()),
        Value::Object(map) => Ok(map.keys().map(|k| Value::from(k.as_str())).collect()),
        other => Err(Error::new(
            "TypeError",
            format!("'{}' object is not iterable", type_name(other)),
        )),
    }
}

/// Python's `float(text)`: [`py_float_text`]'s reading, a decimal digit of any script read as its value (`float("\u{661}")` is 1.0 to
/// Python, and the regex's `\d` takes such digits where a sheet's pattern does).
///
/// # Errors
/// The `ValueError` Python raised, its message naming the text by its `repr`.
pub fn float(text: &str) -> Result<f64, Error> {
    // an ASCII text is read as it is: asking each character's digit value cost a pattern match per character (the parse of a pool
    // sheet spent most of its time there, observed 2026-11-17, feature 449 T170)
    let ascii: std::borrow::Cow<'_, str> = if text.is_ascii() {
        text.into()
    } else {
        text.chars()
            .map(|c| match digit_value(c) {
                Some(d) if !c.is_ascii() => char::from_digit(d, 10).unwrap_or(c),
                _ => c,
            })
            .collect::<String>()
            .into()
    };
    py_float_text(&ascii).ok_or_else(|| {
        Error::new(
            "ValueError",
            format!("could not convert string to float: {}", repr(text)),
        )
    })
}

/// Python's `max(a, b)`: `b` only when strictly greater, so a NaN first stays (where `f64::max` drops it).
#[must_use]
pub fn max(a: f64, b: f64) -> f64 {
    if b > a {
        b
    } else {
        a
    }
}

/// Python's `min(a, b)`: `b` only when strictly less.
#[must_use]
pub fn min(a: f64, b: f64) -> f64 {
    if b < a {
        b
    } else {
        a
    }
}

/// Python's `sum()` over floats (`CPython` 3.12 and later): Neumaier's compensated sum, the compensation added at the end when it is
/// finite and not zero - a plain left fold differs from it in the last place.
#[must_use]
pub fn sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let (mut total, mut c) = (0.0_f64, 0.0_f64);
    for x in values {
        let t = total + x;
        if total.abs() >= x.abs() {
            c += (total - t) + x;
        } else {
            c += (x - t) + total;
        }
        total = t;
    }
    if c != 0.0 && c.is_finite() {
        total += c;
    }
    total
}

/// Python's `f"{v:g}"`: [`l7r_shared::py_text::fmt_g`], a NaN named as Python names it (feature 449 T174, the size table's pixel
/// positions).
#[must_use]
pub fn fmt_g(v: f64) -> String {
    if v.is_nan() {
        "nan".to_owned()
    } else {
        l7r_shared::py_text::fmt_g(v)
    }
}

/// Python's `f"{v:.{places}f}"`: Rust's fixed formatting (the exact binary value rounded half to even, a negative zero signed), a NaN
/// named as Python names it (feature 449 T175, every figure the audit's findings print).
#[must_use]
pub fn fixed(v: f64, places: usize) -> String {
    if v.is_nan() {
        "nan".to_owned()
    } else {
        format!("{v:.places$}")
    }
}

/// Python's `f"{v:,.0f}"`: [`fixed`] at no places, its integer digits grouped by threes with commas (the report's square feet).
#[must_use]
pub fn grouped(v: f64) -> String {
    let text = fixed(v, 0);
    let (sign, digits) = text
        .strip_prefix('-')
        .map_or(("", text.as_str()), |d| ("-", d));
    if !digits.bytes().all(|b| b.is_ascii_digit()) {
        return text;
    }
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    format!("{sign}{out}")
}

/// Python's `(a + b) / 2` of two floats: the sum rounded, then halved - not `f64::midpoint`, which halves first where the sum would
/// overflow and so parts from it at the range's ends (feature 449 T175, the audit's middles of gaps and openings).
#[must_use]
#[expect(clippy::manual_midpoint, reason = "Python's arithmetic, in its order")]
pub fn half_sum(a: f64, b: f64) -> f64 {
    (a + b) / 2.0
}

/// Python's `x ** 0.5` of a float: libm's `pow`, which differs from a square root in the last place about once in a thousand (observed
/// 2026-11-17, method: 6,970 floats through `CPython` 3.14.4, six differing, scratchpad `t175/a/pow_half_probe.py`) - the exponent passed through
/// `black_box` so the compiler cannot fold the call into `sqrt` (LLVM does for a constant 0.5). A negative base is no figure the audit
/// squares, and reads NaN where Python made a complex number.
#[must_use]
pub fn pow_half(x: f64) -> f64 {
    x.powf(std::hint::black_box(0.5))
}

/// Python's `a % b` of two floats: the remainder with the divisor's sign (`CPython`'s `float_rem`), a zero signed as the divisor.
#[must_use]
pub fn modulo(a: f64, b: f64) -> f64 {
    let m = a % b;
    if m == 0.0 {
        0.0_f64.copysign(b)
    } else if (b < 0.0) != (m < 0.0) {
        m + b
    } else {
        m
    }
}

/// Python's `round(x, n)`: the exact binary value rounded half to even at `n` places (Rust's fixed formatting rounds the same way), read
/// back as the nearest float, as `CPython`'s correctly rounded `round` returns it (feature 449 T174, the size table's feet).
#[must_use]
pub fn round_to(x: f64, n: usize) -> f64 {
    format!("{x:.n$}").parse().unwrap_or(x)
}

/// The `OverflowError` or `ValueError` Python's `int()` and `round()` raise on a float with no integer.
fn no_integer(x: f64) -> Error {
    if x.is_nan() {
        Error::new("ValueError", "cannot convert float NaN to integer")
    } else {
        Error::new("OverflowError", "cannot convert float infinity to integer")
    }
}

/// Python's `round(x)`: the nearest integer, half to even, held as the float it equals (an integer beyond `i64` stays exact).
///
/// # Errors
/// An infinity or a NaN, as Python's.
pub fn round_int(x: f64) -> Result<f64, Error> {
    if x.is_finite() {
        Ok(x.round_ties_even())
    } else {
        Err(no_integer(x))
    }
}

/// Python's `int(x)` of a float, as an index: toward zero.
///
/// # Errors
/// An infinity or a NaN, as Python's; a whole number past `i64`, which Python held and then could not allocate a grid of
/// (its `MemoryError`).
#[expect(
    clippy::cast_possible_truncation,
    reason = "the value is whole and inside i64's range, checked first"
)]
pub fn int(x: f64) -> Result<i64, Error> {
    if !x.is_finite() {
        return Err(no_integer(x));
    }
    let t = x.trunc();
    if t.abs() >= 9.2e18 {
        return Err(Error::new("MemoryError", ""));
    }
    Ok(t as i64)
}

/// Python's `math.floor(x)` of a float, as an index (feature 449 T150, the page's merge cells and raster tiles).
///
/// # Errors
/// As [`int`]: an infinity or a NaN, as Python's.
pub fn floor(x: f64) -> Result<i64, Error> {
    int(x.floor())
}

/// Python's `math.ceil(x)` of a float, as an index.
///
/// # Errors
/// As [`floor`].
pub fn ceil(x: f64) -> Result<i64, Error> {
    int(x.ceil())
}

/// Python's `a // b` of two floats: `CPython`'s `float_floor_div`, the floor of `(a - fmod(a, b)) / b` with its sign fix and its
/// rounding of a quotient within a half of the next integer up - not `(a / b).floor()`, which an inexact quotient can carry across an
/// integer.
///
/// # Errors
/// `b` zero: Python's `ZeroDivisionError`.
pub fn floordiv(a: f64, b: f64) -> Result<f64, Error> {
    if b == 0.0 {
        return Err(Error::new("ZeroDivisionError", "division by zero"));
    }
    let m = a % b;
    let mut div = (a - m) / b;
    if m != 0.0 && ((b < 0.0) != (m < 0.0)) {
        div -= 1.0;
    }
    if div == 0.0 {
        return Ok(0.0_f64.copysign(a / b));
    }
    let mut floor = div.floor();
    if div - floor > 0.5 {
        floor += 1.0;
    }
    Ok(floor)
}

/// Python's `math.hypot(x, y)`: `CPython`'s `vector_norm` (3.10 on), a scaled sum of squares carried in double length and one Newton
/// correction - not libm's `hypot`, which can differ from it in the last place.
#[must_use]
pub fn hypot(x: f64, y: f64) -> f64 {
    let v = [x.abs(), y.abs()];
    // `CPython`'s running largest from 0.0: a NaN never takes its place, so an infinity beside one is found
    let max = v.iter().fold(0.0, |m, &x| if x > m { x } else { m });
    if max.is_infinite() {
        return max;
    }
    if v[0].is_nan() || v[1].is_nan() {
        return f64::NAN;
    }
    if max == 0.0 {
        return max;
    }
    norm(v, max)
}

/// `vector_norm` over two finite magnitudes, `max` the larger and not zero.
fn norm(mut v: [f64; 2], max: f64) -> f64 {
    let max_e = frexp_exp(max);
    if max_e < -1023 {
        // a subnormal largest: scaled up by the least normal first, as `CPython` does
        for x in &mut v {
            *x /= f64::MIN_POSITIVE;
        }
        return f64::MIN_POSITIVE * norm(v, max / f64::MIN_POSITIVE);
    }
    let scale = pow2(-max_e);
    let (mut csum, mut frac1, mut frac2) = (1.0_f64, 0.0_f64, 0.0_f64);
    for magnitude in v {
        let scaled = magnitude * scale;
        let (square, square_lo) = (scaled * scaled, scaled.mul_add(scaled, -(scaled * scaled)));
        let (total, lost) = fast_sum(csum, square);
        csum = total;
        frac1 += square_lo;
        frac2 += lost;
    }
    let mut root = (csum - 1.0 + (frac1 + frac2)).sqrt();
    let (square, square_lo) = (-root * root, (-root).mul_add(root, root * root));
    let (total, lost) = fast_sum(csum, square);
    csum = total;
    frac1 += square_lo;
    frac2 += lost;
    let residual = csum - 1.0 + (frac1 + frac2);
    root += residual / (2.0 * root);
    root / scale
}

/// `ldexp(1.0, e)` for `e` in -1074..=1023, exact (`powi` reaches 2^-1024 through an overflowing 2^1024).
fn pow2(e: i32) -> f64 {
    let bits = if e >= -1022 {
        u64::try_from(e + 1023).unwrap_or(0) << 52
    } else {
        1_u64 << u32::try_from(e + 1074).unwrap_or(0)
    };
    f64::from_bits(bits)
}

/// Dekker's fast two-sum: the rounded sum and what rounding dropped (`|a| >= |b|`).
fn fast_sum(a: f64, b: f64) -> (f64, f64) {
    let x = a + b;
    let z = x - a;
    (x, b - z)
}

/// `frexp(x)`'s exponent: `x = m * 2^e` with `0.5 <= |m| < 1` (a subnormal's below -1022).
fn frexp_exp(x: f64) -> i32 {
    let bits = x.to_bits();
    let biased = i32::try_from((bits >> 52) & 0x7ff).unwrap_or(0);
    if biased == 0 {
        // subnormal: the exponent its leading bit gives
        let mantissa = bits & ((1_u64 << 52) - 1);
        let lead = 63 - i32::try_from(mantissa.leading_zeros()).unwrap_or(63);
        return lead - 1073;
    }
    biased - 1022
}

#[cfg(test)]
mod tests {
    use super::{
        fixed, float, floordiv, fmt_g, frexp_exp, grouped, half_sum, hypot, int, iterate, max, min,
        modulo, os_error, pow2, pow_half, round_int, round_to, sum, type_name, uncaught,
    };
    use l7r_gate_research::Error;
    use serde_json::json;

    #[test]
    fn an_uncaught_error_is_its_traceback_s_last_line() {
        assert_eq!(uncaught(&Error::new("ValueError", "x")), "ValueError: x\n");
        assert_eq!(uncaught(&Error::new("KeyError", "k")), "KeyError: 'k'\n");
        assert_eq!(uncaught(&Error::new("ValueError", "")), "ValueError\n");
    }

    #[test]
    fn an_open_that_fails_is_python_s_os_error() {
        let e = |code| std::io::Error::from_raw_os_error(code);
        assert_eq!(
            uncaught(&os_error(&e(2), "/x")),
            "FileNotFoundError: [Errno 2] No such file or directory: '/x'\n"
        );
        assert_eq!(os_error(&e(13), "a").kind, "PermissionError");
        assert_eq!(os_error(&e(1), "a").kind, "PermissionError");
        assert_eq!(os_error(&e(20), "a").kind, "NotADirectoryError");
        assert_eq!(os_error(&e(21), "a").kind, "IsADirectoryError");
        assert_eq!(os_error(&e(5), "a").kind, "OSError");
        let bad = std::io::Error::from(std::io::ErrorKind::InvalidData);
        assert_eq!(os_error(&bad, "a").kind, "UnicodeDecodeError");
    }

    #[test]
    fn a_value_iterates_and_is_named_as_python_s() {
        assert_eq!(iterate(&json!("ab")).unwrap(), vec![json!("a"), json!("b")]);
        assert_eq!(iterate(&json!({"k": 1})).unwrap(), vec![json!("k")]);
        assert_eq!(iterate(&json!([1])).unwrap(), vec![json!(1)]);
        assert_eq!(
            iterate(&json!(null)).unwrap_err().message,
            "'NoneType' object is not iterable"
        );
        let names: Vec<&str> = [json!(true), json!(1), json!(1.5), json!("s"), json!({})]
            .iter()
            .map(type_name)
            .collect();
        assert_eq!(names, ["bool", "int", "float", "str", "dict"]);
    }

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
    fn a_float_a_min_a_max_and_a_sum_are_python_s() {
        assert_eq!(float(" 1_0.5 ").unwrap(), 10.5);
        assert_eq!(float("\u{661}\u{662}.5").unwrap(), 12.5);
        assert_eq!(
            uncaught(&float("1.2.3").unwrap_err()),
            "ValueError: could not convert string to float: '1.2.3'\n"
        );
        assert!(max(f64::NAN, 2.0).is_nan() && min(f64::NAN, 2.0).is_nan());
        assert_eq!(
            (max(1.0, 2.0), min(1.0, 2.0), max(2.0, 1.0), min(2.0, 1.0)),
            (2.0, 1.0, 2.0, 1.0)
        );
        // `CPython`'s compensated sum: a left fold gives 0.6000000000000001
        assert_eq!(sum([0.1, 0.2, 0.3]), 0.6);
        assert_eq!(sum([1e100, 1.0, -1e100]), 1.0);
        assert!(sum([f64::INFINITY, 1.0]).is_infinite());
        assert_eq!(sum([]), 0.0);
    }

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
    fn round_int_floordiv_and_hypot_are_python_s() {
        assert_eq!(
            (round_to(0.25, 1), round_to(-0.04, 1), round_to(2.675, 2)),
            (0.2, -0.0, 2.67)
        );
        assert!(round_to(-0.04, 1).is_sign_negative());
        assert_eq!(
            (round_int(2.5).unwrap(), round_int(-3.5).unwrap()),
            (2.0, -4.0)
        );
        assert_eq!(round_int(1e300).unwrap(), 1e300);
        let e = |r: Result<f64, l7r_gate_research::Error>| uncaught(&r.unwrap_err());
        assert_eq!(
            e(round_int(f64::INFINITY)),
            "OverflowError: cannot convert float infinity to integer\n"
        );
        assert_eq!(
            e(round_int(f64::NAN)),
            "ValueError: cannot convert float NaN to integer\n"
        );
        assert_eq!((int(-2.7).unwrap(), int(2.7).unwrap()), (-2, 2));
        assert_eq!(int(f64::NAN).unwrap_err().kind, "ValueError");
        assert_eq!(int(1e30).unwrap_err().kind, "MemoryError");
        // `CPython`'s `//`: 0.3 // 0.1 is 2.0 where (0.3 / 0.1).floor() is also 2.0 but 1 // 0.1 is 9.0 where (1 / 0.1).floor() is 10.0
        assert_eq!(floordiv(1.0, 0.1).unwrap(), 9.0);
        // a quotient a hair under an integer rounds up to it, as `CPython` rounds it
        assert_eq!(floordiv(18.230_687_000_260_787, 0.1).unwrap(), 182.0);
        assert_eq!(floordiv(-7.0, 2.0).unwrap(), -4.0);
        assert_eq!(floordiv(7.0, -2.0).unwrap(), -4.0);
        assert!(floordiv(-0.0, 2.0).unwrap().is_sign_negative());
        assert!(floordiv(f64::INFINITY, 2.0).unwrap().is_nan());
        assert_eq!(
            e(floordiv(1.0, 0.0)),
            "ZeroDivisionError: division by zero\n"
        );
        // the figures are `CPython` 3.14.4's `math.hypot`
        assert_eq!(hypot(3.0, 4.0), 5.0);
        assert_eq!(hypot(-1e308, 1e308), 1.414_213_562_373_095_1e308);
        assert_eq!(hypot(3e-320, 4e-320), 5e-320);
        assert_eq!(hypot(0.0, -0.0), 0.0);
        assert!(hypot(f64::NAN, 1.0).is_nan());
        assert_eq!(hypot(f64::NAN, f64::NEG_INFINITY), f64::INFINITY);
        assert_eq!(
            (frexp_exp(1.0), frexp_exp(0.75), frexp_exp(5e-324)),
            (1, 0, -1073)
        );
        assert_eq!(
            [fmt_g(f64::NAN), fmt_g(-0.0), fmt_g(1_234_567.0), fmt_g(0.5)],
            ["nan", "-0", "1.23457e+06", "0.5"]
        );
        assert_eq!(
            (pow2(-1024), pow2(1023), pow2(0)),
            (2.0_f64.powi(-1023) / 2.0, 2.0_f64.powi(1023), 1.0)
        );
        // the largest a 2^1024 scale reaches: `CPython`'s figure
        assert_eq!(hypot(1.5e-308, 1e-308), 1.802_775_637_731_994_5e-308);
    }

    #[test]
    #[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
    fn the_audit_s_figures_are_printed_and_reckoned_as_python_s() {
        assert_eq!(
            [
                fixed(f64::NAN, 1),
                fixed(-0.04, 1),
                fixed(2.5, 0),
                fixed(f64::INFINITY, 1)
            ],
            ["nan", "-0.0", "2", "inf"]
        );
        assert_eq!(
            [
                grouped(1_234_567.4),
                grouped(-1_234.0),
                grouped(999.0),
                grouped(f64::NAN)
            ],
            ["1,234,567", "-1,234", "999", "nan"]
        );
        assert_eq!(
            (pow_half(4.0), pow_half(0.0), half_sum(1.0, 2.0)),
            (2.0, 0.0, 1.5)
        );
        // `CPython`'s `float_rem`: the divisor's sign, a zero signed as the divisor
        assert_eq!(
            [
                modulo(-1.0, 360.0),
                modulo(1.0, -360.0),
                modulo(725.0, 360.0)
            ],
            [359.0, -359.0, 5.0]
        );
        assert!(
            modulo(-360.0, 360.0).is_sign_positive() && modulo(360.0, -360.0).is_sign_negative()
        );
    }
}
