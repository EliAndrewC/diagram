# Feature 321 - back up each clone's unlanded work to a GitHub branch (GM, 2026-10-04, verbatim)

Context: a sync had left a session's clone mid-merge with its map page missing. The GM asked:

Thanks. Now, as a side question, out of curiosity, when we do work in a clone, does that get pushed to GitHub in a branch? This experience has made me realize that we probably should do that, although to be honest, I'm not totally sure what the appropriate time is because, you know, we shouldn't take the time to do a GitHub push like literally every time that we save a change to a file or whatever. But maybe if we're running sync with main, which I think we do on a more limited basis, like any time we are finishing work or whatever, then we could push to a branch on GitHub, and then maybe when we sync back into main, then after our changes land in main, then we can delete our work from the remote branch or something. To be clear, I am not asking you to implement any changes here. I am just wondering about what we are currently doing and whether what I am describing seems like a sensible solution to make sure that things are backed up, but then also eventually cleaned up when changes land.

The session answered (a summary, not the GM's words): nothing in a clone reaches GitHub until it lands
(`sync-with-main.sh` pushes only `HEAD:main`; GitHub has only `main`; branches are blocked by `no-branch-hooks.sh`, the
GM's 2026-07-27 ruling; a feature with open tasks cannot land, so its work exists only in its clone on the host's disk).
It proposed: push at the stop-work step (`sync-with-main.sh done`), skipping when nothing is new; a remote-only branch
`backup/<clone-name>` with no local branch, the branch and push-safety guards allowing exactly that pattern; never
forced; deleted when `done` lands the work on main, plus a sweep deleting any backup branch already contained in main;
and asked whether the repository being public mattered. The GM:

Yes, please go ahead and file this as a feature, but then do not actually work the feature. I just want to capture it as a spec kit feature to hand off to a different session to implement before we move forward with more iteration on our feature. [...] And for your thing to decide, then uh, the repository is public, but I don't mind people being able to see branches in progress, so that's not a problem. as long as the branches get cleaned up, which is to say deleted after their contents have been merged into main, just to keep the branches that are visible manageable from an organizational perspective and such.

(The "[...]" elides a sentence about a separate, unrelated modal-formatting change the GM will raise in another session.)
