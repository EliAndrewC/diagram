# The GM's request, verbatim

2026-09-07, session "Diagram tooling". After feature 208 the GM asked for a second memory profile of the
full run: *"Can you do another profile? of the memory usage for a full make done run? I am interested to
see whether there is more fat that we could trim if we take a closer look. because even two hundred and
fifty megabytes plus the rolled manifests they hold Seems like something that we could get down. This is
especially true if the role of benefits that they hold could be loaded into memory when needed and then
purged from memory when done. Does this sound like something that we could do in a refactor? go ahead and
do a memory profile of the full make done run, and then we'll see where we could make additional
performance improvements and particularly RAM usage improvements."*

The heap census found no manifest held (the fixtures release their rolls; the in-process roll store held
0.7 MB), but the clearance index memo in `hamletgen/clearance.py` holding about 46 MB per worker of the
last rolls' geometry, glibc keeping 14 to 68 MB freed, and the rest Python-heap fragmentation after
rolls; the session ranked three levers - clear the memo at the end of a roll, `malloc_trim` after a roll,
roll in a forked child. The GM:

> When you talk about the file cache, which is taking up more than two gigabytes, what does that refer
> to? is that, like, tempfs or something? What specifically is that?
>
> Either way, I agree that we should clear the clearance memo at the end of a roll and that we should do
> the malloc_trim after a roll. it seems like we should also role in a forked child as well, Unless there
> is some reason not to do that which I am not seeing. At the very least, this one being a larger refactor
> seems like something that we could test out by trying it in one place and then making sure that that is
> solid and that there are no undesirable side effects, etcetera. And then if that is the case, then we can
> roll it out to the rest of our places where we would want to do this kind of role in a forked child.
> Sound good?

("role" is "roll".)
