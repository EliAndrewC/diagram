# The GM's request, verbatim

2026-09-07, session "Diagram tooling":

> I have a question about spec kit features. I believe that I have noticed there being times when two different sessions each end up claiming the same spec kit feature number, and then this causes problems later when one clone needs to go back and update their feature to use a different number. This doesn't seem like what we want because two different features might go for a long time, and so it sounds like we need some standardized way to synchronize what features we are using. Since this all happens on the same host and indeed within the same container on the same host, then I feel like there is probably a relatively straightforward solution where we could have a makefile target that selects the next feature number or something. The SpecKit constitution could know how to interact with that, and this would essentially increment the spec kit feature number using some file locking or other kind of multiprocess locking just to make sure that we... always grab the next available feature number, and then don't end up conflicting on feature numbers. does that seem like a reasonable thing to do? If so, then please design and implement that as a tooling improvement. And then, of course, you will need to update the Speckie kit constitution and other project documentation in order to make use of that. Note that if we put this file somewhere on the volumed in directory, then we should make sure it is in our git ignore And if we put it somewhere else, then we need to make sure that it gets regenerated if the container is destroyed and recreated. Thanks.

## What the session found before specifying

- Main already carries the collision: `specs/195-cite-only-what-can-be-read` and
  `specs/195-target-descriptions-and-two-removals` both landed under 195 (2026-09-06). Feature 184 was
  claimed by two sessions on 2026-09-05; one renumbered to 186 before landing.
- The existing protocol (CLAUDE.md "Concurrent sessions", docs/session-clones.md) allocates from main's
  `specs/` after sync-in and relies on the push to surface a collision - a window of hours between two
  sessions' specify steps, which is exactly when both saw the same highest number.
- Every session's clone lives under `<main>/.clones/`, and the mirror root and the home directory are
  both host volume mounts on the same device, so a lock file and a ledger under the mirror root survive
  a container rebuild.
