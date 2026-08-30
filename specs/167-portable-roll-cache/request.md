# The GM's request, verbatim and unedited

This file is the authority for `spec.md`. Nothing here is paraphrased.

---

Yeah. I think that idea seems worth pursuing. Go ahead and proceed with continuing that investigation. And then if it looks like there are real savings above and beyond twenty one seconds once per clone, then please proceed with implementing it. Also, I am assuming that the twenty one seconds once per clone is not something that gets completely invalidated whenever there is an engine change or something. such that in practice, in this twenty one seconds, like every third run of the quick tests or whatever. Right? like it is actually just what's per clone? If that is the case, then I agree that we should not attempt to sync or commit a file such as this.

---

## The idea being pursued, from the message the GM was answering

The GM had asked, of the testmon database: *"why can't we just have the test itself encode a fixture
with the values that it needs? like, as part of the make done when we merge into the main checkout.
The main checkout could refresh that cache or something. so that every clone automatically gets it."*
The session answered that the testmon database is portable but worth only ~21 s per clone, and that
**the roll cache is the larger prize of the two and would be the one to price first**. The GM's reply
above authorizes that pricing, and authorizes implementation **conditional on the measured savings**.

## The two conditions the ruling sets, and how they were answered

1. *"if it looks like there are real savings above and beyond twenty one seconds once per clone"* -
   MEASURED, in a throwaway clone at main's tip: a cold clone pays **30 s** for the reference
   settlement and **122 s** for the map-rolling gate tests, against **1 s** and **21 s** warm. About
   **two minutes per clone**, six times the testmon bar. Condition met.
2. *"I am assuming that the twenty one seconds ... is actually just what's per clone"* - CONFIRMED, by
   measurement rather than reasoning: touching the most depended-on engine module in the tree (79 of
   2,394 recorded test executions) costs `make quick` **10 s** against **4 s** warm, because testmon
   re-runs only the tests that executed the changed code. The cold 25 s is one-time construction.
   **So the testmon database is NOT synced or committed**, exactly as the GM concluded.
