# buildspec/ - the remote runner's build definitions (AWS CodeBuild)

**Dormant: the remote is OFF** (GM 2026-09-05, `dev/switches.json`; `make switches` shows it). Nothing here runs
until it is switched back on with `make ci-on`. Every gate today runs locally (`make done`).

What these files are: the CodeBuild jobs the dispatcher in `l7r/diagram/ci/` starts (feature 130). The AWS projects
hold a placeholder; each build receives the file named here as its buildspec, so a build runs whatever the tree under
test says.

| file | what it is |
|---|---|
| `check.yml`, `merge.yml` | the iteration check and the merge gate; both call `run.sh`, and `MODE` is their only difference |
| `run.sh` | what a build does: fetch the tree, restore the caches, run the target, record the result |
| `image.yml` | builds the custom CI image from `Dockerfile.ci` (`make ci-image`) |
| `measure.yml` | a measurement build (`make ci-measure`) |
| `sparse-excludes.txt` | what a build's sparse checkout leaves out, each pattern with the size and the reason |
| `verified-deny-policy.json` | the S3 bucket policy that lets only a build write `verified/` |

When the remote is on it runs `make soak` (`tests/soak/`), the tier above the local gate - not `make done` again. The
why of each condition a paid run must pass, and what it costs: `l7r/diagram/ci/CLAUDE.md` and `dev/ci.md`.
