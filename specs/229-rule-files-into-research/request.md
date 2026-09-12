# Feature 229 - the GM's request, verbatim (2026-09-12)

The GM opened the session "Diagram research" with this:

> I'd like to talk about our research files because as I am reviewing things, I am noticing that The way that
> things are currently structured is something of a holdover from how things used to be. For example, we have a
> settlements/homesteads.md and also a research/homesteads.html where the first one is the original file that
> explained why we placed our map features the way we did. And the research file is the documentation where we
> show our work on why we think this is historically accurate or when we made a deliberate choice to deviate from
> historical accuracy, etcetera. But here's the thing. The first file was mainly there to explain the placement
> rules to the Claude code session performing the manual map placement. But now we are scripting things. So is
> there any reason for that to exist anymore? I mean, I guess we don't want to get rid of all of those files. when
> we have not yet created the scripted versions of everything. For example, if we just deleted the files relating
> to villages and towns and provincial cities and capital cities, then we would just lose all of that because we
> have not yet scripted any of those things. We have only scripted the creation of hemlets so far. But for things
> like homesteads, which are already scripted, then is there actually any benefit to keeping that original file?
> or is it just that at this point, the Research file is the only one that matters. And so for anything that we
> have already completely scripted, The original markdown file is pointless and can be deleted and references to
> it removed. What do you think? Take a look and tell me whether you think we need to get rid of those or whether
> there is data in there that is worth preserving in some other form, etcetera. my general thinking is that if
> there are... explanations in the markdown versions of the files that explain what we are doing, and the research
> is explaining why, then that would best be combined just into the research files. So, for example, the research
> file could be restructured so that all of our... explanations of what are tied to the research showing the why.
> That is just one idea, and I am not telling you to do that at this exact moment, but that is the kind of
> question that I would like you to answer as you perform an audit of what is in the markdown files versus the
> research files. Let me know what you think, and then we can decide how to proceed from there. Thanks.

The session audited every `settlements/*.md` rule file against its `research/*.html` page (seven independent
readers; the reports are in `audit/`) and reported: for the scripted hamlet tier the rule files are no longer
operative but carry decision records that exist nowhere else; the "why" is already on the research pages; the
"what" for scripted features is in the engine with its reasoning; a large stale layer describes the validator
deleted in feature 166; the rule files contradict the research or the engine in several places; the unscripted
tiers' rule files are the only statement of what to build. It proposed two homes rather than one (the research
page for finding + decision + GM ruling, the engine for the number at the point of change), and asked whether to
run one sweep or several and whether the unscripted-tier briefs should stay Markdown or move onto the research
pages now. The GM:

> Yeah. Let's do this as a spec kit feature. I think we can do it as just one spec kit feature and one sweep. As
> for what to do with the unscripted things, I think that moving those into the research pages as well is the
> right move. So let's just go ahead and do that. As you say, that does mean that there will be some
> specifications in there, and those specifications will move into the scripted generators once those exist.
> Please proceed with that. You can do item number one and fix the contradictions, then item number two and
> migrate the decision records, then do what you specified for item number three, but for all of the settlement
> types. in the manner that we have just established in which you are retiring all of the rule files with any
> content that needs to be preserved, such as specifications for things that you have scripted moved into the
> research files. Thanks.

The "item number one / two / three" the GM names are the session's proposed order, which read:

> 1. Fix the contradictions and the stale layer first. A migration that copies wrong numbers and broken anchors
>    forward is worse than none.
> 2. Migrate the decision records file by file into the research pages, starting with the ones another page
>    already cites.
> 3. Retire the hamlet-tier rule files after migration, splitting out their village and city paragraphs into
>    whichever brief survives.
> 4. Keep the unscripted-tier files as labeled briefs until each tier is scripted.

The GM's answer replaces item 4: nothing stays a labeled brief; every tier's specification moves onto the
research pages, and item 3 applies to all of the settlement types.
