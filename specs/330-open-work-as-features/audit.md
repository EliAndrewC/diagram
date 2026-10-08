# Feature 330 - the audit: every feature settled, every future-work entry accounted for

## A. The gm-assistant check (T02, FR-005, SC-005)

**Searched** (2026-10-08): every `specs/*/` directory's `spec.md`, `request.md` and `gm-request.md`, for
gm-assistant's own subjects - `webapp`, `Obsidian Portal`, `Discord`, `backstor`, `chargen`, `character sheet`,
`cherrypy`, `playwright screenshot`, the relic and temple skills, the `frontend-review` and `backstory-review`
agents - flagging any directory with three or more hits.

**Found**: four, each read:

| feature | hits | what it is about |
|---|---|---|
| `119-l7r-diagram-namespace` | 27 | the diagram's `l7r.diagram` namespace, which shares its parent package with the webapp's `l7r.app` - diagram work |
| `127-gated-make-commands` | 3 | the diagram's make-only guards; the webapp is named as what the guards leave alone - diagram work |
| `130-codebuild-merge-gate` | 5 | the diagram's CodeBuild merge gate; gm-assistant's resources it reused - diagram work |
| `131-split-diagram-repo` | 19 | splitting the diagram out of gm-assistant into this repository - diagram work |

**Result**: no feature belongs to gm-assistant; none deleted. The split (feature 131) carried over only the features
that concern the diagram, as the root `CLAUDE.md` says ("features 001-131 that concern the diagram live here").
