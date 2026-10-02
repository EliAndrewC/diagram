# Request (GM, 2026-10-02, verbatim)

The GM wrote:

I've been reading through our research, and there are a few sections that I've noticed that could use a little rework just basically to make it clear what the section actually is for. So like, here's what I'm talking about as an example:

[the GM pasted the built page of `research/questions/0094-rooms-for-a-parley-across-a-border.html`: its heading "Rooms for a parley across a border", its "Not to be confused with" block, its opening paragraph and its bullets, as the record held them on 2026-10-02]

Now, to be clear, this is all very good information. It's well explained, it's well cited. But the problem is, someone reading this section would have an obvious question, which is, why is this question here? Why am I being told about a thing which does not exist?

Of course, the answer is that we have a map that has such a room. And we did this research to see whether this was just an invention of the setting or not. And it turns out that it is just a fun invention. So that's fine. It is totally fine for us to have the Ubame map show a parlay room on the border. Because it's just kind of a cool thing, and... You know, it's neat. And our rule of thumb is that anytime we show something cool like that, we research the degree to which it is realistic and the degree to which it is a deliberate thing that we have added while noting what the real historical findings were. All good stuff. But the problem is that this section in particular says nothing about why the question was asked or whatnot. So, I think that this is the kind of section that needs an introductory paragraph that explains why this section is even here. Something like this:

> In Rokugan, certain negotiations sometimes take place in a parley room directly on a border, such that each side enters through a door in their own lands and sits across from each other at a table placed precisely on the border, allowing each clan to negotiate from their "home domain" while still sipping tea together.  This is an invention of the setting, and the research below shows what we were able to find about how things were actually done in the historical records we were able to find.

I think we probably need a new subagent check to run on research sections in order to see whether an explanation such as this is warranted for a section. I believe it is the case that our project rules for subagent checks such as this is that they would run on everything applicable when they are first created, but then after that, they would only run on a research section which has been edited or which is new. Is that correct? Like, is that how this works, and do we kind of automatically dispatch this or decline to dispatch this? And do we have a way to exempt certain subagent checks from firing when we are making an edit? This seems relevant here because, for example, we are adding here is definitionally something that is not citing any research. So it would be a waste of time and tokens for us to add the kind of paragraph that I just explained and then rerun all of the other subagent checks for things like whether the research accurately characterizes its source or... whether our quotations match word for word what is in the original source. Because nothing like that is being touched. So is our tooling and processes already good enough to have us do the correct thing here? And I guess not just do the correct thing, to kind of enforce us doing the correct thing. Because I do worry about a future session making some extremely minor formatting tweak or something and then having that literally rerun every subagent check for all 2,000 something of our resources just because like the tooling was not preventing it or was too dumb to to flag what things actually needed to be rechecked, etc.

The session answered (summarized here, not the GM's words): the map review checks are owed by occasion and enforced at push
(feature 294); among the record checks, `translation-check` is owed per changed pair and `entry-drift` per modal whose section
body changed (push refuses, a reason discharges), while `quote-check` and `record-format` have only the doctrine "every new or
changed entry", with no script naming what is owed and no push refusal; nothing refuses a needless re-run either. It proposed
one feature: (1) a script naming what each record check owes from what the delta touched - notes changed owe quote-check on
those notes only; prose with no footnote marks, like the proposed intro, owes record-format only; a new question owes every
check; a move or retag owes nothing - enforced at push, with each owed check discharged by a record or a stated reason, and no
check demanded that is not owed; (2) a new check judging whether a question needs an introductory paragraph saying why it is
asked, run once over every question as a backfill, then owed only when a question is new or its heading changes, with the intros
it calls for written in the GM's style; and the Ubame parley-room intro added.

The GM replied:

Yes, please implement that as a spec kit feature and then work the feature from start to finish. Thanks.
