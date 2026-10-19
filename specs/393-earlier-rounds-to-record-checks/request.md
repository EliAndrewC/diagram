# Feature 393 - the request, verbatim

The GM, 2026-10-18 (dictated; no substitutions apply):

> I have a question about the way that we use subagents. Um, we've put in a lot of work to try to make it pretty efficient, and I have a note to myself that I'm embarrassed to say I can't remember when I made it, because this was either a note that I made while working on this personal project reminding me to take that benefit into my day job so that I could make use of it there, or it was something I figured out at work last week that I wanted to make sure to bring here. And the note is this:
>
> > give each reviewer the earlier rounds' verdicts and reasons to prevent reviewer loops
>
> And I know that this is advice which exists to prevent a problem that I have had on both work projects and personal projects, which is that reviewers will often get caught in loops. You know, they will like make similar suggestions, or they will, you know, kind of bounce back and forth, what we sometimes call oscillating, uh, you know, or they'll kind of fall into traps where we end up doing many more rounds of reviews than we have to, and this was shown to have some kind of benefit there and make that less likely to happen. Um, but I don't remember whether that's something I implemented at work and intended to bring here or implemented here and intended to bring to work. So can you check whether this is something that we are doing?

The session's answer (summarized): it is done here for `spec-fidelity` (feature 249: the previous verdict verbatim plus the
diff, by hook), for the map reviewers (`glyph-check`, `building-review`, `settlement-review`: the previous verdict file and the
notes' settled items) and for the round arbiter (every round marked NEW / REPEATED / REVERSING). It is NOT done for the
research-record checks (`check_bundle.py`: quote-check, record-format, source-reader, intro-check, translation-check,
entry-drift) or, beyond the wording research rounds fixed, the pop-up checks (`modal_bundle.py`: modal-form, modal-depiction,
modal-research) - where 85 of the 106 arbiter rulings feature 385's audit counted fell. Closing it: give those bundles the
earlier rounds' verdicts and reasons. "Shall I file it?"

The GM, 2026-10-18:

> Yes, please file the feature and then work it, but then can you also coordinate with the "Money" session which is also making some tooling fixes because I want to make sure that you do not end up implementing the same thing that they implemented or vice versa.
