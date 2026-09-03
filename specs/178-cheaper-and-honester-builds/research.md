# Feature 178 - research

## R1 - The per-minute rates, VERIFIED against actual billing (FR-015)

The AWS Pricing API returns nothing with these credentials (`get_products` on `AWSCodeBuild` yields
0 products, no error - presumably `pricing:GetProducts` is not granted). Cost Explorer is the better
instrument anyway: a price list says what AWS charges in general, and this says what THIS ACCOUNT was
charged. Read with the `[aws_admin]` key, 14 days to 2026-09-03:

| day | usage type | minutes | cost | derived rate |
|---|---|---|---|---|
| 2026-08-24 | `g1.xlarge` | 2.0 | $0.1596 | **$0.0798/min** |
| 2026-08-25 | `g1.2xlarge` | 18.0 | $3.6000 | **$0.2000/min** |
| 2026-08-25 | `g1.medium` | 5.0 | $0.0500 | **$0.0100/min** |
| 2026-08-25 | `g1.xlarge` | 130.0 | $10.3740 | $0.0798/min |
| 2026-08-31 | `g1.medium` | 2.0 | $0.0200 | $0.0100/min |
| 2026-08-31 | `g1.xlarge` | 22.0 | $1.7556 | $0.0798/min |
| 2026-09-03 | `g1.xlarge` | 69.0 | $5.5062 | $0.0798/min |

**`config.RATES` is accurate**: `XLARGE` 0.08 against a billed 0.0798 (0.25% high, and rounding UP is
the safe direction for an estimate the GM reads before spending), `2XLARGE` 0.20 exact, `MEDIUM` 0.01
exact. **`LARGE` (`g1.large`, 0.02) has never been billed in this account and is therefore
UNVERIFIED** - item 5's own measurement will produce the first row for it, and this table is where the
check gets closed.

Source: AWS Cost Explorer `get_cost_and_usage`, `SERVICE = CodeBuild`, grouped by `USAGE_TYPE`, read
2026-09-03. Not a published price list - the account's own invoice lines.

## R2 - A CORRECTION to feature 177's reported spend

Feature 177's closing report told the GM *"$7.44 across eight builds"*. **The true figure is $5.51.**
Cost Explorer for 2026-09-03 shows 69.0 billed minutes at $5.5062, and the six builds that day account
for exactly 69 minutes: `19ff1147` 1, `cf341865` 9, `3937fe7c` 15, `9f760907` 8, `76087221` 24,
`ab43bfac` 12. The per-build figures reported were each correct; the total was added wrong, and no
record carried the error - it was stated in conversation only.

The lesson is the one this repository already applies to timings: a number that can be read off an
artifact should be, rather than accumulated by hand. `make ci-status` sums the run log for exactly
this reason, and the run log agrees with the invoice.
