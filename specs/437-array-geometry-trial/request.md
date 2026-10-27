# Feature 437 - the GM's request, verbatim

The GM, 2026-10-27, after feature 436 (`make perf-ab` quick first, one run a version) landed, answering the open decision
from feature 435's closing report: whether to trial feature 417 T57's item 10 - the shared geometry layer's one-value-at-a-
time Python moved into arrays - as T57 recommended, a short spike first ("one predicate (`seg_dist` over many candidates)
vectorized and measured in its hottest caller - to put a measured number on the large item before committing to it"):

> Sounds good, let's go with trialing the array-based geometry.  Do the trial and also report on how long it took to do the trial, so we can see what other tooling or process improvements we might need to speed up not only the code itself but our iteration toward better performance.
