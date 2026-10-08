# Feature 330 - the GM's request, verbatim

2026-10-08, in the session "Diagram gm-assistant cleanup" (dictated; read as spoken):

> Thanks. Now, as we talk about cleaning things up, another thing that I think would be nice to be cleaned up is old spec kit features. Now, I don't mean deleting them, because honestly, they don't really do any harm being here unless they are old spec kit features from the GM Assistant repo which we should just delete because they are referencing things that are not part of this repo. But I would like to know which spec kit features have been filed but then not worked. Or for that matter are there spec kit features that were filed and then not finished? Like Is there outstanding work that is not currently captured in our ./future-work/ ?
>
> I think that what I would like to have is actually to get rid of ./future-work/ as a directory with its own individual listings. Everything that is there should instead become an unimplemented spec kit feature. However, we then need some way to mechanically easily see what spec kit features are open. I can think of a couple of ways of doing this. One is to simply have a makefile target like `make speckit-todo` which parses out spec kit features and then gives a listing of which ones exist that have not yet been implemented and maybe also lists the ones that are partially implemented if that is a category, etc. This seems like a fairly straightforward thing to do, which then adds to our list of makefile targets by giving us ways to kind of ask ourselves about the work that is yet to be done. If this seems like a good idea to you, then go ahead and do this as part of your audit of the existing spec kit features and the cleanup, after you finish with your current round of cleanup.

Earlier in the same session, on the ledger this feature's rule replaces:

> I'm not sure that ./future-work/closed.md actually serves any real purpose. Does that seem like something We should just get rid of? I mean, our Git history tells us what has been closed, as does our spec kit specs. So I'm not really sure what purpose this serves. I think it might predate spec kit in this project.
