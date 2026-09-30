# Feature Specification: Hook misfires and silent stalls

**Feature Branch**: `295-hook-misfires-and-silent-stalls`
**Created**: 2026-09-30
**Status**: Requested - NOT STARTED. The GM asked for this feature to be filed and not implemented (request.md). It is
specified from request.md when it is taken up.

## Summary

Fix the four tooling problems feature 291's landing hit (request.md): the finished-run hook's false alarm on a covered
chained run; the review-round hook routing an exception check into a later review round; a headless page session that
never wakes for its own background agents' results; the missing watchdog outside the session; and (item 5, added at
the GM's request from feature 292's session) a periodic report kept as a backgrounded one-shot watcher, which loses its
schedule across a usage-limit window - to be steered to `CronCreate`, by a hook if one can.
