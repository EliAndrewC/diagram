# The GM's request (verbatim, 2026-09-27, session "Diagram supplemental")

The question that started it:

> Since we have now done quite a few research passes with the new system, are you able to analyze how many tokens it is taking to do each research pass and whether there is anything else that we should do in order to optimize it? The way that we got to this point is that we found that it was very inefficient, and so we spent a lot of time doing one research pass at a time on individual items, and then looking at how many tokens were spent and what they were spent on, and then we made tweaks and adjustments to make that more efficient. For example, we split out the files that we were saving the results in into much smaller files so that each pass only needs to load and look at the things relevant to it, and we shortened our Claude.md files and reduced the number of instructions that we were giving to subagents, and then we took some care to reduce the number of subagent passes that needed to be done and things of that nature. So basically, over the last day or so, ever since those changes landed, we have now done many, many research passes, and although we had previously run out of tweaks to make, I wonder if anything else has become evident as we have now made just a ton of research passes. What do you think? Does anything jump out at you, or are we pretty much optimized now? It seems like it's better to ask than to assume.

The request, after the session reported the measurement (research.md) and three suggestions:

> Well, you can change the research process without its feature being separate. It's just that changing the research process must itself always be a feature. But in general, yes, please do implement all three of your suggestions and not just one and two. And then after this has landed on main, I would like for you to inform the other sessions that are doing research about the changes so that they can make use of them immediately. Thanks.

The three suggestions, as the session put them to the GM:

1. Cap a write session at about 4 questions (or 10 new registry keys); a larger group is split into several write sessions.
2. A session reads only its own lines of the coordination files (the claims file, its group's handoff, its checks report), through a `make` target, and appends to a report without reading it.
3. A slimmer CLAUDE.md for the headless page sessions.
