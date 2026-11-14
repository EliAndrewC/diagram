//! The make-target page: each part of a target's `##` line, the page's sections, and the check's verdicts and raises.

use std::path::Path;

use super::{check, cli, escape, parse, write, OUT};
use crate::checks::scratch;

const MAKEFILE: &str = "\
quick:  ## [tests] the quick tier   FILE=<test path> EXTRA=1
##  FILE=<a test path>  the one file to run
##  OTHER=  what it means with no value
\techo quick
maps: ## [maps] {internal} the pool's maps   SEED=3
\techo maps
x-y: ## [maps] {inactive: retired 2026} kept & <unused> \"q\" 'a'
\techo x
odd: ## [docs] a category no section has
\techo odd
plain: ## no tag here
\techo plain
helper:
\techo helper
two words:
\techo two
VAR := 1
var:= 2
";

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_target_s_line_gives_its_category_flag_arguments_and_their_docs() {
    let (rows, undocumented) = parse(MAKEFILE);
    let names: Vec<&str> = rows.iter().map(|r| r.name.as_str()).collect();
    assert_eq!(names, ["maps", "odd", "plain", "quick", "x-y"]);
    assert_eq!(undocumented, ["helper", "two", "words"]);
    let quick = &rows[3];
    assert_eq!(
        (quick.category.as_str(), quick.args.as_str()),
        ("tests", "EXTRA FILE OTHER")
    );
    assert_eq!(quick.argdocs.len(), 2);
    assert_eq!(
        (rows[0].flag.as_str(), rows[0].args.as_str()),
        ("internal", "SEED")
    );
    assert_eq!(
        (rows[4].flag.as_str(), rows[4].why.as_str()),
        ("inactive", "retired 2026")
    );
    assert_eq!(escape("&<>\"'"), "&amp;&lt;&gt;&quot;&#x27;");
}

#[test]
fn the_page_is_written_and_checked() {
    let root = scratch("make-docs");
    std::fs::write(root.join("Makefile"), MAKEFILE).unwrap();
    let missing = check(&root);
    assert_eq!(missing.code, 1);
    assert!(
        missing.stderr.contains("no [category] tag: plain")
            && missing.stderr.contains("does not exist")
    );
    let wrote = write(&root);
    assert_eq!(
        wrote.stdout,
        format!("make-docs: wrote {OUT} - 5 targets, 3 undocumented\n")
    );
    let page = std::fs::read_to_string(root.join(OUT)).unwrap();
    for part in [
        "<h2>Tests</h2>",
        "<span class=an>FILE=&lt;a test path&gt;</span><span class=aw>the one file to run</span>",
        "<span class=an>OTHER=1</span>",
        "<td class=n>make maps<span class=b title='called by a recipe",
        "<td class=a>SEED</td><td>the pool&#x27;s maps</td>",
        "title=\"retired 2026\">inactive</span>",
        "kept &amp; &lt;unused&gt; &quot;q&quot; &#x27;a&#x27; <span class=w>retired 2026</span>",
        "<b>Unrecognized categories:</b> docs",
        "<tr><td class=n>make helper</td></tr>",
        "<td class=a>&ndash;</td>",
    ] {
        assert!(page.contains(part), "{part}");
    }
    assert!(!page.contains("<h2>Diagnostics</h2>"));
    // untagged still fails the check once the page is current; tagged, it passes, and a stale page fails
    assert!(
        check(&root).stderr.contains("no [category] tag: plain")
            && !check(&root).stderr.contains("STALE")
    );
    let tagged = MAKEFILE.replace("## no tag here", "## [project] {inactive} now tagged");
    std::fs::write(root.join("Makefile"), &tagged).unwrap();
    assert!(check(&root).stderr.contains("STALE"));
    assert_eq!(write(&root).code, 0);
    assert_eq!(
        check(&root).stdout,
        format!("make-docs: {OUT} is current (5 targets)\n")
    );
    assert!(std::fs::read_to_string(root.join(OUT))
        .unwrap()
        .contains("title=\"currently does nothing\">inactive"));
    // the command line: the root first unless it is a flag, the mode the first flag
    assert_eq!(
        cli(&words(&[root.to_str().unwrap(), "--check"]), Path::new("/")).code,
        0
    );
    assert_eq!(cli(&words(&["--other"]), &root).code, 0);
    assert_eq!(cli(&words(&[]), &root).code, 0);
    assert_eq!(cli(&words(&[".", "--write"]), &root).code, 0);
}

#[test]
fn what_stops_the_page_before_it_is_made() {
    let root = scratch("make-docs-stops");
    let none = check(&root);
    assert_eq!(
        (none.code, none.stderr.contains("no Makefile at")),
        (2, true)
    );
    assert_eq!(write(&root).code, 2);
    std::fs::write(root.join("Makefile"), [0xff]).unwrap();
    assert_eq!(check(&root).code, 1);
    std::fs::write(root.join("Makefile"), "a: ## [tests] x\n\techo\n").unwrap();
    std::fs::write(root.join("docs"), "a file\n").unwrap();
    assert!(write(&root).stderr.contains("Traceback"));
    std::fs::remove_file(root.join("docs")).unwrap();
    std::fs::create_dir(root.join("docs")).unwrap();
    std::fs::write(root.join(OUT), [0xff]).unwrap();
    assert!(check(&root).stderr.contains("Traceback"));
    // a Makefile that cannot be read
    let mode = |m: &str| {
        std::process::Command::new("chmod")
            .arg(m)
            .arg(root.join("Makefile"))
            .status()
            .unwrap()
    };
    mode("000");
    let unread = check(&root);
    mode("644");
    assert!(unread.code == 1 && unread.stderr.contains("Traceback"));
}
