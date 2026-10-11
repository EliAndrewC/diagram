# Feature 379 - the GM's request

The GM, 2026-10-10, after the hourly check found that the round arbiter's recommended tooling fix in the "Diagram research"
session (the gate should refuse to start while another make done runs in the same clone) had been recorded only in the
ruling's prose and filed nowhere:

> I guess I'm a little concerned that the arbiter recommended that tooling fix be made, and then maybe it just got lost, because that is the kind of thing that I would want to know about. [...] I really don't want sessions just filing new features to be done later without telling me or without my say-so. But I also don't want this kind of thing to get lost. And the longer the session, the more likely it is that it will get lost. [...] or worst of all, having the session stop work to ask me a question, thus blocking for many hours until I return. [...] I almost wonder whether it would be worth making a rule that says to always implement this kind of tooling change when recommended by the arbiter. Before proceeding with the rest of your implementation, and to incorporate it into whatever feature it is that you were working on when it happened. Like, that could be a project rule or something. And it could be something that the arbiter is programmed to explicitly tell the session to do.

The session proposed: the fix as a field of the ruling, the next `make tick` held until it is made (with its test) in the current
feature or declined as an overhaul, a decline going to the GM's review rather than a feature filed or a question asked. The GM:

> I agree with your recommendations around the arbiter tooling fixes as well, by the way. So yeah, please go ahead and implement that as well. Where kind of things that overhaul the process are not done in line and do require GM review in the way that you mean, but that smaller things like the one that we are doing now for making sure that make done cannot be run twice at the same time get done very very soon with tool enforcement about that.

## Amendment 1 (2026-10-10, same session)

The hourly check found both monitored sessions fixing shared tooling partway through a feature - the round cap, a ruling
filed under the wrong feature, an "accept" ruling deadlocking a check a later change owed - with each fix held in its own
clone until the whole feature closes (a feature with open tasks lands nothing but its spec). Meanwhile hooks run from
`/diagram`, so other sessions hit the same misfire, fixes were copied by hand between clones, and both sessions were editing
`hm_arbiter.py` and `hm_checks.py`, the files this feature changed. The session proposed letting a commit that touches only
tooling (`scripts/`, `tests/`, the agent instruction files) land on its own in the middle of a feature, through the normal
checks, added to 379 rather than filed as a new feature. The GM:

> yes please

## Amendment 2 (2026-10-10, same session)

The hourly check asked whether a code unit's impl-drift rounds should go to the round arbiter like the record checks'.
The GM:

> I mean, the rule should basically be that things should go to the arbiter at the point where they were previously coming to me. So if there is something that currently in the process gets escalated to be prior to going to the arbiter, then we should change that so that it goes to the arbiter first.

(Dictated: "escalated to be prior to going to the arbiter" reads as "escalated to me prior to going to the arbiter".)

## Amendment 3 (2026-10-10, same session)

Amendment 2 left the band-3 performance sign-off with the GM, on the GM's earlier words "I must personally sign off on this
before it is committed back to main", and asked whether the new rule covers it. The GM:

> yes it covers the band-3 perf signoff too
