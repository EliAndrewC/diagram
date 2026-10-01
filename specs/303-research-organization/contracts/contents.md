# Contract - tags.json and contents.json

tags.json:
  {"subject": {"<id>": {"name": "...", "description": "..."}},
   "setting": {"countryside": {...}, "town": {...}, "city": {...}},
   "level": [{"id": "foundational", "name": "..."}, {"id": "subtype"}, {"id": "detail"}, {"id": "counts-and-measurements"}]}

contents.json:
  {"sections": [{"id": "tiers", "title": "The settlement tiers", "description": "<html>",
                  "takes": [{"primary": "tiers"}], "sections": []}, ...]}

A clause matches when every key matches: `primary` (the first subject), `subject` (any subject), `setting` (any
setting), `level`; a value may be a string or a list (any of). Order within a section: level order, then number.
