# The GM's request, verbatim

2026-09-07, session "Diagram html", after feature 205 (one glossary term) took 16.9 minutes of wall
clock, 10 of them the gate, and the session had broken the time down and proposed moving the glossary
to a JSON file and listed the other content living in code.

First message:

> Yes. we should definitely one hundred percent move the glossary data into a JSON file. More generally. we should probably also do an audit of what other kinds of content should be moved into JSON files in this manner. Because I imagine that there are other things that could change from string constants to docstrings or which could change from Python dictionaries to JSON files and therefore allow changes to our data to skip doing the full Ten minutes of make done tests.
>
> With that being said, I could have sworn that we got our make done tests down to well below ten minutes. Why did it take ten full minutes? I'd like to know the answer to that before we make any further changes.
>
> As regards the spec kit process, it sounds as if you are telling me that the spec kit process added about two and a half minutes to this process. If that is all, then I think I do agree that we probably do not need to eliminate the SPECT kit process for small features such as this, and that if I ever want to batch a large number of features such as this, then I can group them under a single larger SPECT kit feature. but I just want to make sure that I do understand the numbers that you have presented me. Are you telling me that we Spent about two and a half minutes using SpecKit on this, and then had we avoided SpecKit, then the entire thing would have only been about two and a half minutes shorter?

The session answered (the gate has been eight to ten minutes since feature 174 made it the whole
suite under the 100% floor; the glossary edit had also chilled the roll cache; the gate never selects
by change - `make quick` does, via testmon; a finer gate is possible in principle by keeping per-test
coverage contexts from the last full run and merging). Then:

> Okay. So it sounds like what you're telling me is that when there are no engine changes, then we do skip the lengthy eight minutes of make done tests. But if there are engine changes, then we require one hundred percent code coverage, which is basically what is taking the eight minutes. Is that correct? and we do not have very much in the way of sensitivity around only running the subset of tests where anything changed? Is that right? So, like, not only will an engine change cause all of the tests to rerun, is it the case that a change to something specific to one type of hamlet will cause all of the tests to run, including the core engine tests? Or are we doing some finer grained work, which means that if we modify a single file in a submodule of a submodule that is not in the core engine, then we will not run all eight minutes of tests?

And, after the session confirmed all three and sketched the merge of per-test coverage contexts:

> Okay. Yes. So it sounds like we do want the finer grained version that you are describing here because eight minutes is a long time, and I would really like to get that down. So how about this? You should go ahead and implement the spec kit feature that you had previously described about moving data, which is content rather than code, into data files, such as JSON files, to prevent them from showing up as engine changes. However, because that is essentially a testing efficiency improvement, then I think it makes sense to bundle that into the same spec kit feature as this other efficiency improvement about finer grained coverage detection. Please proceed with that. Thanks. I think you can take that whole thing from start to finish Unless you have any other questions for me.
