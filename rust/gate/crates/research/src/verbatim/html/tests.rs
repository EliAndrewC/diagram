//! `CPython`'s `HTMLParser` as `_Visible` read a page (feature 449 T145; each expected value `CPython` 3.14.4's on the same markup, 2026-11-16).

use super::visible;

const CASES: [(&str, &str); 38] = [
    ("a</a b='x>c", "a"),
    ("<p>a &amp; b</p><div>c</div>", " a & b  c "),
    ("x<script>if (a<b) {}</script>y<style>p{}</style>z<noscript>n</noscript>w", "xyzw"),
    ("<SCRIPT>a</Script >b", "b"),
    ("<br/>a<br />b<script/>c", "  a  bc"),
    ("<plaintext><p>raw &amp;", "<p>raw &amp;"),
    ("<textarea>a &amp; <b></textarea>t<title>T &lt;</title>", "a & <b>tT <"),
    ("a<!-- c -->b<!--c--!>d<!-->e<!--->f", "abdf"),
    ("a<!-- never closed", "a"),
    ("a<?pi?>b<!DOCTYPE html>c<![CDATA[x]]>d<!bogus>e", "abcde"),
    ("a</>b</ x>c</", "abc</"),
    ("a<b", "a"),
    ("a < b", "a < b"),
    ("a<", "a<"),
    ("<a href='x>y' title=\"q\">link</a> z", "link z"),
    ("<a href=x =junk>t</a>", "t"),
    ("<div class=\"x\"/ >y", " y"),
    ("<p a b c>t", " t"),
    ("x<script>never", "x"),
    ("x<script>a</script", "x"),
    ("tail &amp", "tail &"),
    ("t &ampx; &#65; &#x41;", "t &x; A A"),
    ("<p>1</p >2<P>3", " 1 2 3"),
    ("<a\"b c>q</a\"b>", "q"),
    ("<h1>H</h1><li>i</li><td>t</td><tr></tr><pre>p</pre><figcaption>f</figcaption><span>s</span>", " H  i  t    p  f s"),
    ("<ul><li>a<ul><li>b</li></ul></li></ul>", "  a  b    "),
    ("<x y='unclosed>z", ""),
    ("a<!doctype", "a"),
    ("a<![CDATA[open", "a"),
    ("a<?pi", "a"),
    ("a<!x", "a"),
    ("<style>a</style", ""),
    ("<iframe>i</iframe>j<xmp><b>x</b></xmp>k", "ij<b>x</b>k"),
    ("<script>x</scripty></script>z", "z"),
    ("</script>after", "after"),
    ("", ""),
    ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa &x", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa &x"),
    ("&bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "&bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
];

#[test]
fn every_construct_is_read_as_cpython_reads_it() {
    for (markup, seen) in CASES {
        assert_eq!(visible(markup), seen, "{markup}");
    }
}
