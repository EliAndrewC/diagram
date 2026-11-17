//! A URL's host against `CPython` 3.14.4's (feature 449 T148): `cpython.jsonl` holds `blocked.host`'s answer on 3,844 URLs - tabs, CR and
//! LF anywhere, leading controls, characters NFKC turns into `/?#@:`, good and bad brackets, IPv6 and `IPvFuture` hosts, user names,
//! ports, the case-blind scheme test, and 3,700 random ones - written by the generator in feature 449 T148's scratch (`host/gen.py`).

use super::{host, ipv4, ipv6};

#[test]
fn every_host_is_cpythons() {
    let mut n = 0;
    for line in include_str!("cpython.jsonl").lines() {
        let (url, want): (String, String) = serde_json::from_str(line).unwrap();
        n += 1;
        assert_eq!(host(&url), want, "{url:?}");
    }
    assert_eq!(n, 3844);
}

#[test]
fn the_address_readers_refuse_as_ipaddress_does() {
    assert!(ipv4("1.2.3").is_err());
    assert!(ipv4("1.2.3.256").is_err());
    assert!(ipv4("1.2.3.04").is_err());
    assert_eq!(ipv4("1.2.3.4"), Ok(0x0102_0304));
    for bad in [
        "fe80::1%",
        "fe80::1%a%b",
        "",
        "1:2",
        "::1.2.3.256",
        "1:2:3:4:5:6:7:8:9:10",
        "1::2::3",
        ":1::2",
        "1::2:",
        ":1:2:3:4:5:6:7",
        "1:2:3:4:5:6:7:",
        "1:2:3:4:5:6:7::8",
        "1:2:3:4:5:6:7",
        "12345::",
        "::g",
    ] {
        assert!(ipv6(bad).is_err(), "{bad}");
    }
    for good in [
        "::1",
        "fe80::1%eth0",
        "::ffff:1.2.3.4",
        "1:2:3:4:5:6:7:8",
        "1::",
        "::",
    ] {
        assert!(ipv6(good).is_ok(), "{good}");
    }
}
