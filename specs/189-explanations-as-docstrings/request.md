# The GM's request, verbatim

2026-09-05, session "Diagram html", after feature 188 reported that a modal's explanation in
`classes.py` still costs the full gate because "a string constant is part of the semantic key the gate
hashes":

> When you say that a string constant is part of the semantic key the gain hashes, then I guess my question is why a model's explanation is stored in a string constant rather than being stored in a docstring. Because if it was stored in a docstring, then I believe that would make it not part of the semantic key the gate hashes, right? So can we make that change? that has a bunch of really nice properties. like, in general, I am a fan of docstrings. making their way into the content of things because then the documentation within the code is literally the documentation that is visible in the user interface. Any reason not to do that? Go ahead and make that change if you agree.
