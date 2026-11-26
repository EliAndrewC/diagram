# The GM's request (verbatim)

2026-11-26, in the session "Diagram backlog":

> Also, as for the first tier and the amount of parallelization, what we are doing seems very good for now, where we have only one session running. But I do want to be able to run multiple sessions in the future. I don't currently have any plans to do that right now or even probably today, but it is something that I want to be able to do. So I think our parallelization, whatever is optimal, is probably something that needs to have a system in place for handling multiple concurrent sessions, so that if the optimal number of simultaneous builders was 4, then the two sessions could coordinate about that in some kind of automated tooling-based way or whatever. This is something that probably can be its own spec kit feature that we don't worry about right now, because I think that we should be more focused on just kind of getting everything working to start with and then resuming our port eventually, since I don't have any need for multiple sessions between now and then. But I want to make sure that this is something that we are thinking about.

2026-11-26, later, on whether two sessions filing tasks in one feature would conflict:

> It sounds like this would only be a problem for multiple sessions if multiple sessions were working the same feature. And to be honest, I'm just not concerned about that because that is not an actual use case. every circumstance under which I would have multiple sessions running is one in which they would be working different features.
