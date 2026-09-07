# The GM's request, verbatim

2026-09-07, session "Diagram tooling". The GM had asked why a full gate costs 6.8 GiB and for a memory
profile; the profile found that a worker rests at about 250 MB and spikes to 600-800 MB for about seven
seconds every time a rolled hamlet writes its HTML page, the spike being the page's raster picture (PIL
decoding an 18.6-megapixel PNG and libwebp encoding it lossless), paid on every roll whether or not any test
reads the page, and that the resting floor is freed C memory the allocator keeps. The GM:

> Okay. Wow. So it sounds like we could really improve our efficiency then. because we're doing a whole lot
> of rasterizing that is completely pointless and not actually needed for the tests. Right? please do an
> audit, and then Make the change to write the picture in a subprocess. And, also, to not write it at all
> for test roles where it is not needed. If writing in a subprocess is not enough to free the one hundred
> and thirty megabytes of memory, then, yes, please also do the malloc_trim or whatever is needed in order
> to. make this more efficient. Thanks.

("test roles" is "test rolls" - the hamlet rolls the tests make.)
