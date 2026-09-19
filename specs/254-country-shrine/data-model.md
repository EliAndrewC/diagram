# Data model - feature 254

## BuildingType (one object in `l7r/diagram/buildings/types.json`)

| field | type | meaning |
|---|---|---|
| `tier` | string, kebab | the pool folder under `pool/`; the type's name everywhere |
| `title` | string | the pool index's section title |
| `program` | string | the `programs.md` heading the reviewers read |
| `hand_drawn` | bool | the tier's `.svg` is tracked source (negated in `.gitignore`) |
| `generated_exceptions` | list of stems | maps in a hand-drawn tier whose gen writes the svg (re-ignored) |
| `required` | list of RequiredItem | the program's required items |
| `checks` | list of check names | per-type checks from the registry that apply to this tier |
| `notes` | string | the why, rendered under the required-items table in `programs.md` |

## RequiredItem

| field | type | meaning |
|---|---|---|
| `id` | string | stable id (`sanctuary`, `hall`, `dwelling`, ...) |
| `label` | string, regex | case-insensitive; a sheet text label matching it is the item |
| `band_ft` | object | `w: [min, max]`, `h: [min, max]` or `area: [min, max]`, in feet / sq ft |
| `optional` | bool | governed by a knob; absence is not a finding |
| `class` | one of accurate / deviation / convention / guess | the band's label, with `why` |
| `why` | string | the finding the band rests on (a research section anchor) |

Validation: `tier` unique and kebab; every `checks` name exists in the registry; a `label` compiles;
a band's min <= max; `class` in the four; a `generated_exceptions` stem exists under the tier.

## Check (a registry row in `tools/pack_audit/registry.py`)

| field | type | meaning |
|---|---|---|
| `name` | string | the check's name, printed on failure |
| `run` | callable(ParsedPlan, BuildingType) -> list of findings | the check |
| `types` | None or frozenset of tiers | None = shared layer |
| `fixture` | filename under `tests/fixtures/` | the red fixture it fires on |
| `fix` | string | the compliant fix a failure prints |

Validation (a test): every registered check's fixture exists, the check fires on it, and passes on
every pool sheet of a tier it covers; every `checks` name in a declaration is registered.

## ParsedPlan (existing, one field's meaning changes)

`interior` becomes the rects marked `id="precinct"`; parsing a sheet with none raises, naming the sheet.

## Notes file keys read by a check

`**Program type**: <program>` (existing, the pool index reads it); `**Form**: one roof | two buildings`
(new; `check_program` reads it to count a combined building as hall and dwelling).
