# The GM's request (verbatim)

2026-10-08, closing feature 111:

> You can close feature 111 because we've replaced "decompose for readability" with a mechanical cap on function length and file length.

2026-10-10:

> But do we really not have a gate on function length? I could have sworn that we already did. Did we just not implement that? How many functions fail that length? Or have we even selected a length for our maximum?

> As for the length, what do you suggest? Like, is there a standard best practice for projects like this? actually implemented this kind of rough check before, but I do like the idea of just doing that in our linter, because that does seem good. So um, when people set that option, what kinds of things do they usually set it to? If there is a really common standard, then how many of our functions would that fail?

> Yeah, go ahead and do a GitHub code search for max statements across public pyproject.toml and pylint rc files. [...] if that's kind of just not something that anyone is doing, then that would probably flip me back to thinking that we should go with a default of 50. But if, as you say, people do kind of set between 60 and 100 commonly, you know, even if it's a minority of projects, if it's just a thing that is done quite often, then yeah, like 100 sounds good.

> That sounds great. Please go with 100. And we can document why 100 is the number that we went with, like that it is the second most common value on GitHub from our initial survey. And then yes, implement feature 370, then 371, then 361.
