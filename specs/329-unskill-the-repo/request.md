# Request (GM, 2026-10-07, verbatim)

The GM dictated these; typos are left as written.

The GM's first message (a question):

Is there any reason any longer to keep the diagram skill as an actual skill?  I mean originally it was one of the skills in the gm-assistqant repo, but we split it out.  But I'm not sure what keepig it a skill really does for us at this point.  It's not like we invoke it via saying `/diagram hamlet` or whatever.  And even if we did, that would be no reason to put all of the code under ./.claude/skills/diagram right?  What do you think about the possibility of a refactor?

The session answered (summarized, not the GM's words): nothing consumes it as a skill any more (gm-assistant has no
`diagram` skill; nobody types `/diagram`); its only effect is the skill-list description; nested `CLAUDE.md`
loading is by directory and survives a move. Recommended: a spec-kit feature moving the engine, pool, research,
buildings and tests to the repository root, one Makefile and one config root, `SKILL.md` becoming a usage doc,
`specs/` history left as written with a moved note, the per-directory `CLAUDE.md` loading kept deliberate, caches and
path-keyed records carried over or deliberately invalidated, and the move landing as one commit between features; drop
the skill entirely rather than keep a stub.

The GM's second message (after renaming the session "Diagram unskillify"):

Yes please make the speckit feature adn then do the refactor, taking the feature from start to finish.
