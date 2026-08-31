# Feature 173 - the GM's request, verbatim

The GM opened with the census from their own laptop, of every `.py` under the skill outside
`legacy-hand-authored-pool`, sorted by raw line count, tail -20 - topped by
`hamletgen/ways.py` at 4,369 lines.

> This project has a set of guidelines that revolve around not letting files grow too large, but it
> looks like we have allowed that to drift:
>
> [the census]
>
> I think the solution is to build checks for this into our tooling. one of the things that can run
> whenever we do a make done can be to check the size of our files. And if any of them are too large,
> which is to say over one thousand lines of code, then we fail the gate with a message that explains
> that the clone responsible for this work must split up the file in the manner prescribed in our
> project guidelines. For example, it looks like hamletgen/ways.py should become hamletgen/ways/ with
> many sub-modules, as we have done elsewhere, etc. Let me know if my meeting is not clear in this
> case because while I believe that our project guidelines do explain in detail the specific manner in
> which we are meant to break things up and then create a Claude dot MD file in each relevant
> directory to serve as an index explaining which file to load when looking for each category of
> thing. I have not actually verified this for myself, so it'd be good to know that that is, in fact,
> present.
>
> Of course, in addition to building this tooling, we will need to actually do these refactors in
> order for the tooling to pass, since we won't be able to merge the tooling into main until the check
> actually passes.  That's fine, since this is a fairly straightforward refactor we have done a number
> of times already; this change is merely about enforcing it at the project level.

("my meeting" is dictation for "my meaning".)
