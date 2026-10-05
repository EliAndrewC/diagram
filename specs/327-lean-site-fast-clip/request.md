# The GM's request (2026-10-05), verbatim

> Memory has been tight even after our changes, so let's go ahead and make a new feature that includes both of these. Which is
> to say both the site build thing and also the render speed follow-up. Thanks. And then go ahead and after filing that feature,
> work the feature from start to finish and Land it on the main checkout. Thanks.

"Both of these" - the session's two follow-ups, verbatim from its answer:

> **What the 148 MB is.** The site build returns every page as a Python string: 2,698 pages, 72.6 million characters. Python
> stores a whole string at 2 bytes per character as soon as it contains one character beyond Latin-1, and nearly every page
> carries some Japanese. So 69 million characters cost 132 MB instead of about 70. The single all-in-one page (`all.html`) alone
> is 42 MB of that.
>
> **Two ways to shrink it:**
> 1. **Hold pages as UTF-8 bytes instead of strings.** At rest the site would take about 75-80 MB instead of 148 (mostly 1 byte
>    per character, 3 for Japanese).
>    - Writing files gets slightly simpler, since they're written as UTF-8 anyway.
>    - The cost is the readers: about 30 tests search page text. They'd need the build to hand back a dictionary that decodes a
>      page when a test reads it. That's a modest wrapper, but each read briefly re-creates that page as a string.
>    - Saves about 70 MB.
> 2. **Stream pages to disk as they're built, never holding the whole site.** `make record` would peak near the size of one page
>    plus the single page's pieces, perhaps 100 MB instead of 236.
>    - This changes what the build is: the tests would read pages back from a temporary directory instead of from memory.
>    - It's a bigger rewrite of the build and of the test helpers.
>
> **On the render-speed follow-up:** I agree it's the better one. Clipping costs about 0.9 s of Python per render because each
> of the 9 tiles re-parses the whole page text. Measuring each line's extent once and reusing it for every tile should recover
> most of that, with no memory cost.
