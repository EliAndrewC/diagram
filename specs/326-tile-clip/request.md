# The GM's request (2026-10-05), verbatim

> sure, go shead and file that as a feature and then work the feaure, thanks

("shead" and "feaure" are typing slips for "ahead" and "feature".)

"That" - the session's answer the GM was replying to, verbatim (its closing question was "Want me to do it as a feature, or
leave it for now?"):

> **What it would mean for a whole render**, which currently peaks at ~575 MB with 3 tiles at a time:
> - **Clip only, 3×3:** about 60 MB less at the peak, and the render about 0.3 s faster, winning back part of the second
>   feature 324 added.
> - **Clip plus a 5×5 grid:** about 150 MB less at the peak (to roughly 425 MB), at about today's render time; more, smaller
>   tiles cost more total CPU, but clipping offsets it.
>
> So it's real but modest: 10-25% of a map render's peak, mostly worth it as "clip plus smaller tiles".

And what the clipping is, as the session described it: "Clipping means first removing every element that lies wholly outside
the tile's window, so each process gets only roughly its own share."
