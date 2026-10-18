# The GM's request, verbatim (2026-10-18)

Context (feature 388 amendment 1, the GM): "I am completely fine freezing old legacy maps. Especially if it streamlines our code base and reduces our support surface, etc. So yes, I believe that the frozen maps do not need to stay runnable, and therefore the four helpers can go too."

The session's proposal, in its report of 388 amendment 1: since the frozen maps need not run, about 71 more engine
functions and classes are now called only by frozen maps - most of the town and city drawing code (trades, castle and civic
buildings, walls, moat, canals, waterfront, the city budget planner) plus the hill-rice field builders. Deleting them would
cut the support surface a lot; the cost is that the scripted town and city tiers (381, 382) would rebuild them or recover
them from git instead of reusing them. "Do you want that filed as a feature?"

The GM: "Yes please file that feature and then execute it."
