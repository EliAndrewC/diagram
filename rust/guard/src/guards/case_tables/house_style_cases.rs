//! `house_style_hooks`'s cases; a British word here is the point of the case, so this file is exempt from that guard. The cases moved here from `tests/hooks/test_hooks_cases.py` (feature 449 T050), each one's history kept above it.
//!
//! TWO DIRECTIONS FOR EVERY GUARD: each table carries the cases it must FIRE on and the cases it must stay QUIET on, and the quiet half is deliberately the longer one. Every false
//! positive this project has paid for is in these tables as a regression case. **A mention is not an invocation.**

use super::{cmd, edit, write, Case};

pub(super) fn cases() -> Vec<Case> {
    vec![
        // feature 164 - these five are CORRECTED now rather than refused (GM 2026-08-30).
        // Both rules are exact substitutions from CLAUDE.md, and a session refused for one of them simply
        // retyped the same edit with the fix - 3 firings, 3 identical re-edits. The rule is unchanged: an
        // edit the table cannot fully fix still refuses, and the GM own writing is never corrected at all.
        ("a British spelling in a spec", edit("/r/specs/x/spec.md", "", "the licence is granted"), "rewritten:the license is granted"),
        ("another, in prose", edit("/r/docs/a.md", "", "the centre of the map"), "rewritten:the center of the map"),
        ("the archaic territory word", edit("/r/docs/a.md", "", "the lord demesne"), "rewritten:the lord domain"),
        ("an em-dash", edit("/r/docs/a.md", "", "a dash \u{2014} here"), "rewritten:a dash - here"),
        ("an en-dash", edit("/r/docs/a.md", "", "a range 1\u{2013}2"), "rewritten:a range 1 - 2"),
        // ...and the two the correction must NEVER touch
        ("a backticked MENTION is not a use", edit("/r/docs/a.md", "", "the word `colour` is British"), "ok"),
        // GM 2026-09-06 - A QUOTATION IS SOMEONE ELSE'S TEXT: *"The house style should not normalize
        // british spellings or em-dashes inside things we are quoting, because that requires us to edit other
        // people's quotes"*. Corner brackets, curly quotes and the HTML quotation elements are held out everywhere;
        // straight double quotes only in a prose file - in code they delimit a string. (Some words below are
        // written with \u escapes because the hook of the day corrected this file's own cases as they were typed.)
        // feature 303 - the record file in two cases takes the flat layout's path; the cases are unchanged.
        ("a British spelling inside a footnote quotation", edit("/r/research/site/q/a.html", "", "<li id=\"fn-3\">「depressional centres」 (gloss)</li>"), "ok"),
        ("an en-dash inside curly quotes", edit("/r/docs/a.md", "", "Wikipedia: “Tang (618\u{2013}907)”"), "ok"),
        ("a straight-quoted passage in prose", edit("/r/docs/a.md", "", "the chapter reads \"a draught animal\" on the page"), "ok"),
        ("an HTML <q> element", edit("/r/research/site/q/a.html", "", "<q>a plain-colour sheath</q>"), "ok"),
        ("a straight-quoted string in CODE is still corrected", edit("/r/l7r/x.py", "", "label = \"the colour\""), "rewritten:label = \"the color\""),
        ("a quotation beside a plain violation: only the plain one is corrected", edit("/r/docs/a.md", "", "「colour」 and the colour"), "rewritten:「colour」 and the color"),
        ("the GM verbatim request is refused, not corrected", edit("/r/specs/164-x/request.md", "", "fix the colour"), "blocked"),
        ("American spellings", edit("/r/docs/a.md", "", "the center is gray, the color honors judgment"), "ok"),
        // the files that must QUOTE the forbidden words in order to state the rule
        ("CLAUDE.md stating the rule", edit("/r/CLAUDE.md", "", "never write colour or centre"), "ok"),
        ("the constitution stating it", edit("/gm/.specify/memory/constitution.md", "", "forbid licence"), "ok"),
        // the GM's own writing is theirs
        ("the GM's canonical file", edit("/host-l7r-repo/setting/l7r.md", "", "the colour of the sky"), "ok"),
        ("a SOURCE block in our file", edit("/r/docs/a.md", "", "<!-- SOURCE: GM NOTES - DO NOT MODIFY -->the colour<!-- END SOURCE -->"), "ok"),
        // A BASH HEREDOC IS A WRITE. The first version matched only the Edit/Write tools, and the author
        // walked straight past it minutes after shipping the guard by writing a spec with a python
        // heredoc. Same hole layer 3 had, and the same lesson: guard the ACTION, not one route to it.
        // ...and since feature 236 a Bash payload is TOLD rather than refused (spec D2): the payload is
        // often itself the spelling fix, and `make quick` is the half that fails.
        // ...and since feature 236's amendment the payload is CORRECTED like an edit (the GM 2026-09-12:
        // *"warn when it is the sed shape, and for other shapes just correct it"*). What the command only
        // NAMES is held out by `_hm_house`: a search, a path, a quoted token, a code span, a quotation.
        ("prose written by heredoc", cmd("cat > docs/a.md <<'EOF'\nthe colour is grey\nEOF"), "rewritten:cat > docs/a.md <<'EOF'\nthe color is gray\nEOF"),
        ("clean prose by heredoc", cmd("cat > docs/a.md <<'EOF'\nthe color is gray\nEOF"), "ok"),
        // FEATURE 405 T109 - A REPLY WRITTEN OUTSIDE THE PROJECT IS A QUOTATION, whatever shares its command: the checker's own
        // words were rewritten in replies recorded verbatim, because `make claims-checked` sat in the same command
        ("a reply heredoc to /tmp beside its recording", cmd("cat > /tmp/s/r.txt <<'EOF'\nVERDICT a DRIFTED - labelled centre\nEOF\nmake claims-checked BUNDLE=/tmp/b REPLY=/tmp/s/r.txt"), "ok"),
        ("a /tmp heredoc beside a project one: only the project's is corrected", cmd("cat > /tmp/s/r.txt <<'EOF'\ncentre\nEOF\ncat > docs/a.md <<'EOF'\ncentre\nEOF"), "rewritten:cat > /tmp/s/r.txt <<'EOF'\ncentre\nEOF\ncat > docs/a.md <<'EOF'\ncenter\nEOF"),
        // THE WHOLE PAYLOAD, not only its heredoc bodies (feature 236 FR-007): the measured hole was a
        // write that travelled by some other route through Bash
        ("an echo append", cmd("echo 'the centre of it' >> docs/a.md"), "rewritten:echo 'the center of it' >> docs/a.md"),
        // THE SED SHAPE IS THE GM'S OWN EXEMPTION, and a replacement pair written any other way is the
        // same shape: correcting either would replace a word with itself and the fix would do nothing.
        ("a sed fix is left exactly as typed", cmd("sed -i 's/centre/center/g' docs/a.md"), "warned:centre"),
        ("a sed replacement that INTRODUCES one", cmd("sed -i 's/center/centre/g' docs/a.md"), "warned:centre"),
        ("a replacement pair in a Python sweep", cmd("python3 - <<'PY'\nt = t.replace(\"the centre of\", \"the center of\")\nPY"), "warned:centre"),
        // ...and the shapes where the word is NAMED rather than written, each one measured on the real
        // commands this hook had warned on (`specs/236-catch-mistakes-early-and-cheaply/research.md` R10)
        ("a sweep's own word list", cmd("python3 - <<'PY'\nWORDS = {'colour', 'centre'}\nPY"), "ok"),
        ("a regex alternation", cmd("python3 -c \"re.compile(r'(colour|centre)')\""), "ok"),
        ("a path that carries the word in its name", cmd("cat docs/colour-notes.md"), "ok"),
        ("a negated search is still a search", cmd("! grep -qiE 'colour|centre' docs/a.md"), "ok"),
        // A SEPARATOR INSIDE QUOTES IS NOT A SEPARATOR (feature 239, found in the guard log): a research
        // session's `grep -oE '(HIGH|MEDIUM)|— \*\*'` was split on every `|`, its fragments stopped
        // looking like a search, and the em-dash in the PATTERN was corrected to a hyphen - so the grep
        // silently searched for the wrong character. The search is left exactly as typed now.
        ("a quoted alternation holding a dash is one search", cmd("grep -oE '\\*\\*(HIGH|MEDIUM|LOW)\\*\\*|\u{2014} \\*\\*(HIGH|LOW)' a.md"), "ok"),
        ("the research session's exact sweep is not rewritten", cmd("for f in *.md; do echo \"=== $f\"; grep -oE '\\*\\*(HIGH|MEDIUM|LOW)\\*\\*|\u{2014} \\*\\*(HIGH|LOW)' \"$f\" | sed 's/[\u{2014}*]//g' | sort; done"), "warned:\u{2014}"),
        // THE SESSION STATE DIRECTORY IS OUTSIDE THE PROJECT, as `/tmp` is: the auto-memory's own index
        // line format uses an em-dash, and the correction was rewriting that format as it was written.
        ("the auto-memory index", cmd("cat >> /home/agent/.claude/projects/-diagram/memory/MEMORY.md <<'EOF'\n- [A](b.md) \u{2014} the hook\nEOF"), "ok"),
        // ...and the exemption is decided by where the write LANDS. Judging every path the command
        // MENTIONS got this wrong in both directions: the case above mentions `b.md` in its own body, and
        // the case below mentions the memory file while writing a project file. The amendment review found
        // the second (the whole command went silent); its first fix produced the first.
        ("a memory read beside a project write", cmd("grep -c x /home/agent/.claude/projects/-diagram/memory/MEMORY.md; cat > docs/x.md <<'EOF'\nthe colour of it\nEOF"), "rewritten:grep -c x /home/agent/.claude/projects/-diagram/memory/MEMORY.md; cat > docs/x.md <<'EOF'\nthe color of it\nEOF"),
        ("a scratchpad write", cmd("cat > /tmp/claude-1000/x/notes.md <<'EOF'\nthe colour of it\nEOF"), "ok"),
        // ...and the WRITE TARGET is read the way `_hm_tree` reads one for the main-tree guard, because a
        // scanner of the raw text got four shapes of the record wrong at once (amendment round 2, measured
        // over the window: 7 outside-the-project writes newly corrected, 4 project writes newly silenced).
        ("a memory write behind a variable", cmd("M=/home/agent/.claude/projects/-diagram/memory/MEMORY.md; cat >> $M <<'EOF'\n- [A](b.md) \u{2014} the colour\nEOF"), "ok"),
        ("a memory directory behind a variable", cmd("M=/home/agent/.claude/projects/-diagram/memory; cat > $M/project_x.md <<'EOF'\nthe colour of it\nEOF"), "ok"),
        ("a scratchpad heredoc whose body carries a quote line", cmd("cat > /tmp/claude-1000/x/b.md <<'EOF'\n> the colour, quoted from the page\nEOF"), "ok"),
        // D11: a program heredoc can write anywhere, and where every target that CAN be resolved is
        // outside the project the command is left alone. The two mistakes are not equal - a correction
        // that should not have happened rewrites someone else's text silently, while one that did not
        // happen leaves a spelling `make quick` fails on in the delta. Treating this as unknowable acted on
        // 21 window commands whose every resolvable target was outside, 7 of them the auto-memory index.
        ("a program heredoc beside a /tmp log", cmd("python3 - <<'PY' > /tmp/gate.log\np.write_text(\"the centre of it\")\nPY"), "ok"),
        // ...but a commit message is not unknowable: the write lands in the repository, and `_hm_tree`
        // says so, so this one is corrected even though its only redirect goes to /tmp.
        ("a commit message beside a /tmp log", cmd("git commit -m 'the centre of it' && make test-full > /tmp/g.log"), "rewritten:git commit -m 'the center of it' && make test-full > /tmp/g.log"),
        // ...and the two shapes that must stay quiet, or the guard fires on correct work
        ("searching for the word", cmd("git grep -n \"centre\" -- docs/"), "ok"),
        ("a code span NAMING the word", cmd("echo 'the token `colour` is British' >> docs/a.md"), "ok"),
        ("a prose quotation keeps its own characters", cmd("cat >> docs/a.md <<'EOF'\n「a plain colour sheath」\nEOF"), "ok"),
        // gm-request.md is a verbatim transcript of the GM speaking; correcting it defeats its purpose
        ("the GM's own words, by heredoc", cmd("cat > specs/128-x/gm-request.md <<'EOF'\nthey wrote colour\nEOF"), "ok"),
        ("merely GREPPING for one", cmd("grep -n colour docs/a.md"), "ok"),
        // a session scratchpad is outside the project (2026-09-06: three reader agents had verbatim page text in
        // /tmp result files rewritten and each worked around the guard)
        ("a file under /tmp is not project content", edit("/tmp/claude-1000/x/scratchpad/result.json", "", "{\"t\": \"the colour\"}"), "ok"),
        // feature 236 - A FIXTURE IS A VERBATIM RECORD: `tests/hooks/fixtures/` holds corpora of commands that
        // really ran, several of them house-style sweeps, and correcting one falsifies the measurement it
        // reproduces. The exemption is in the hook AND in the delta check; this is the hook half, which the
        // amendment review noticed had no case of its own and would have been lost silently.
        // feature 239: the decision module carries the word table itself, so an edit to it must never be
        // corrected - the hook would otherwise Americanize its own list of what to correct
        ("the decision module's own word table", edit("/r/scripts/hooks/lib/hm_house.py", "", "PAIRS = {\"colour\": \"color\"}"), "ok"),
        ("a recorded command corpus", write("/r/tests/hooks/fixtures/corpus.json", "{\"command\": \"sed -i s/centre/center/ docs/a.md\"}"), "ok"),
    ]
}
