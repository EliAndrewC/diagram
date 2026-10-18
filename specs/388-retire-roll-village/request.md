# The GM's request, verbatim (2026-10-18)

Session (on the village soak failure feature 387 found), the GM: "Since we don't actually have a village tier yet, I don't understand how it is that we have failing village tests."

Session's answer, in short: the failing test exercises `Settlement.roll_village`, the feature-005 knob engine that rolls a
hamlet-scale map from a seed; no pool map ships from it any more (the scripted hamlet generator replaced it), only tests call
it, and the session offered to move the finding from 380 to 384's backlog.

The GM: "I think if nothing ships from it then we should just delete it now and not even move it into the 384 backlog."

## Amendment 1 (2026-10-18)

The session's report said four helpers were kept because frozen legacy exhibits call them, and that which exhibits must stay
runnable was the GM's call. The GM: "I am completely fine freezing old legacy maps. Especially if it streamlines our code base and reduces our support surface, etc. So yes, I believe that the frozen maps do not need to stay runnable, and therefore the four helpers can go too. Thanks. I assume that that is what you were asking for my sign-off on with the GM review?"
