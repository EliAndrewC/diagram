# Feature 294 - rethinking the settlement review

The GM's words, verbatim (2026-09-30, during feature 291's landing):

> Hey, as a sanity check, are these settlement reviews really pulling their weight? They take up a lot of time and quite a lot of tokens. And if they are issues that I would otherwise personally have to find, then that's totally worth it. But I kind of just want to make sure that the juice is worth the squeeze, so to speak.

> Instead of reviewing only Mizuguchi and Kashikawa this time, Go ahead and skip the review process entirely. And then yes, feature, but do not work it for        possibly making the tweak that you suggest to the settlement review process. And more broadly, the spec keeps feature should involve reviewing how the settlement review in general. To think about time and and when it fires and what it is doing for us, etc. because I do think that we need to make some changes to it, and so I would prefer to have this feature land prior to rethinking all of that, which means that we can just skip it for now.

The tweak it refers to (the session's reply, 2026-09-30): review only the maps whose FORM or subject a feature changed,
rather than every pool map whose layout moved; or make the review opt-in per feature.

## 2026-10-01 - the scope, after the session's review of the process

The GM's words, verbatim (opening the session "Diagram review"):

> I would like to take a hard look at our settlement review process. [...] I am concerned about both the amount of time and the number of tokens that are spent on this review process, and so I want to take a hard look at what it is doing, what it is buying us, and also just generally how extensive it is. For example, as the number of settlements that we have in our pool grows, then the settlement review process, I think, might be taking up a progressively larger and larger amount of time and tokens if it is examining every settlement every time there is an engine change that could conceivably affect that settlement. This will become quickly untenable after we branch out into villages and towns and provincial cities and capital cities, etc. So therefore, I would like to get this procedure rock solid, both in terms of what it is checking for, but then also in terms of when we even apply it and whether we should scale it back or make it less ambitious or have it only run under certain circumstances, etc.

> One thing that I know we are doing to some degree, but I would like to focus on, is things which could be automated. like if our settlement review is checking for anything which a properly implemented placement algorithm would make impossible, then we should fix the placement algorithm and then stop checking for that thing in the settlement review. Or alternatively, there may be things that we are checking for in the settlement review today, which we have already made impossible by having previously fixed the placement algorithm, etc.

The session replied with a census of the ledger and a seven-item list (retire what is guaranteed; automate the
unchecked geometric classes and the notes' stated counts; fire on a change to what a map depicts, targeted maps only,
with a mechanical report for an engine sweep; cap rounds and refuse churn before dispatch; a ledger that measures
itself; re-test a cheaper tier on seeded faults; encode the ruling in the tooling). The GM:

> I do agree with that list, but I think that we can add on to that list as well. For example, it does look like some of the things that the reviewer caught had to do with things like ambiguities in new glyphs being added. Now that's great, but to be honest, that seems like something that should only be run when a new glyph is added, right? So I don't think that that should be part of the standard reviewer process. That should be its own review that happens anytime a new glyph is added to a map, but then not run at any other time because it's just a waste.

> Also, caste geography, agreement with a building's plan sheet, and label placement rules should be struck from the subagent review since every single one of those is something that the placement rules should handle once we have automated the generation of maps where they are relevant, right?

> go ahead and update the spec with all of these changes and then I will take a look at it before I have you begin. Thanks.

## 2026-10-01 - on the draft spec's open questions

The session's draft carried a separate glyph review and three open questions (a redrawn glyph; label wording; the report of
what moved on an engine sweep). The GM:

> So to be clear, the separate glyph review was meant to be an example of something that would be run only when a new element is added to the map and then not run it other times in order to see that it looks right. I might be wrong, but I would guess that this is not just a single thing that should be moved to its own check, but actually a category of thing which can be moved into separate checks. So I would like for this feature to be updated to include an audit of the checks that we are doing to ask ourselves whether other things follow the same logic and thus should be moved into separate checks which only run under certain circumstances just as the glyph readability and intuitiveness check is only run when new glyphs are added to maps.

> I agree with your recommendation about redrawn glyphs also being rechecked there and also if the rules for how a glyph works change substantially that should also trigger a change. For example, let's say that we realize that we've been putting tanneries inside the city instead of putting them along water sources. I think that would trigger another glyph review because we've totally changed how the glyph is being rendered.

> I agree with the label wording not needing its own check. If we find that this is something that is slipping through a lot, we can add a new type of check, which would be similar to the glyph checks in terms of only running when a new type of label is added or something.

> For the report of what moved, I'm not sure that that is super helpful, to be honest. Because I don't know that that report would do any good relative to me just looking at the new map. So I don't know that it's actually worth putting together unless that is a report which the subagent reviewers need in order to more efficiently do their job.

## 2026-10-01 - the audit's scope confirmed, and the go-ahead

The revised draft limited the audit to the three map reviews and left the research-record checks out. The GM:

> Your scoping is correct. I do not need the research reviews to change as I am happy with those and those have been reviewed and adjusted elsewhere.

And then:

> Thanks!  Please work feature 294 from start to finish and let me know when it lands on main.
