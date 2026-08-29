# The GM's request, verbatim (2026-08-29)

Session: Diagram (Kuwabata). Recorded before the spec was written, so the spec review
(constitution XVI) has the words as written rather than a paraphrase.

> There is currently only one item on our Hamlet maps, which comes with a label, and that is the
> notice board. However, this means that getting the notice board labeling correct is important
> because the code that we write to apply labels will be generally reused for other map features on
> other types of settlements once we get to them. With this in mind, I notice that the label for the
> notice board on the Kuwabata Map is surprisingly far away from the noticeport itself. It is
> correctly aligned with the noticeport, and the distance of the line on which the label rests is the
> correct distance from the noticeport. But for some reason, rather than being directly below the
> noticeport, it's off to the right a bit, and I'm not really sure why or how that happened. This is
> especially puzzling given that the notice board is the very last item that is placed on the map, so
> it is not as if the label got moved during a later phase. In fact, something that we should
> probably do right now, because this will matter later, is add a phase at the very end of every
> settlement creation process, which is putting down the labels for things. Thus, after the final map
> feature is added, which on a hamlet is the notice board, there is a final phase in which we add
> labels for whatever map features get labels. This is because how we place labels will always depend
> on what else is on the map. When we begin putting labels on maps that have many labels, we can
> assign a priority to each type of thing to ensure that when we have to make difficult decisions
> about which labels get to make use of the empty space, which is available, then the higher priority
> labels get placed first. and thus get their choice of that empty space. However, that will not
> apply here. And, also, there is plenty of empty space to put the label directly next to the notice
> board. So I would like for you to correct the placement algorithm in these ways. First, by moving
> label placement so that the notice board itself is placed during a separate phase than the labels
> for the map are placed. even though in this case, that does not really matter because there is only
> one label on the map. and then second to correct the placement of the notice board label so that it
> is actually directly next to the notice board itself.

("noticeport" is dictation for "notice board".)
