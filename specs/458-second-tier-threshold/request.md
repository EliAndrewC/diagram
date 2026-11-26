# The GM's request (verbatim)

2026-11-26, in the session "Diagram backlog", after the second tier's threshold was talked through:

> Yeah, it seems like once we move to the two-tier system, we could begin pushing to a branch prior to landing things on main. So for instance, since this session is named `Diagram backlog` then pushing to a `diagram-backlog` branch to ensure work is not lost seems pretty straightforward. And then anytime we land on main, we can delete that remote branch or whatever so that things don't accumulate over on GitHub.
>
> your suggestion for the threshold seems sensible for now, but this also seems like something where it's probably worth filing a backlog feature to evaluate how things are going after a day or two, just to make sure that whatever it is that we have picked is working out in practice and that we don't need to make any tweaks. You can also mention the stronger version in that feature as something that we can evaluate to see whether it seems like it would in fact be better, or if it actually just doesn't seem necessary or like it would be helping us.

The branch he describes exists as `backup/<session clone's name>` (`scripts/sync-with-main.sh backup`), pushed today only when a
push is refused and deleted once its work is on main; under the two tiers it is pushed after every carry.
