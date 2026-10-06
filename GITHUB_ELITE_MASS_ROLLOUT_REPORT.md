# GitHub Elite — Mass Rollout Report

> **SUPERSEDED — portfolio economics removed from GitHub in V7.**
> This report is retained as an accurate record of what was published
> and when it was retired. The financial section, plate and methodology
> were deliberately withdrawn by direction change. They are not current
> and must not be cited. Noaerth.com is outside the GitHub-only boundary
> and is untouched.
Generated from measured repository state. Every number here was read from the
GitHub API or produced by a command that ran. Where a measurement was not
taken, the report says so rather than estimating.

---

## INVENTORY

| | count |
|---|---|
| total repositories | 152 |
| public | **135** |
| private | 17 |

Start of this round: 10 public, 142 private. Net change: **+125 public**.

The 17 remaining private repositories account for exactly:

| count | reason |
|---|---|
| 11 | denylisted by policy |
| 1 | `freeonomie` — API returns 404 on direct access |
| 1 | `freewash-finder` — empty, pending deletion |
| 4 | orphan website repositories with no canonical parent project |

---

## DELETED

**Nothing was deleted.** Repository deletion requires the `delete_repo` OAuth
scope and `gh auth refresh` requires interactive browser authentication, which
could not be completed non-interactively.

All deletion candidates were prepared and verified instead:

- **18 full mirror bundles** written to
  `/Users/matador/.github-removal-manifest/bundles/` (2.5 MB total, every
  mirror confirmed to contain its HEAD commit).
- Per-repository metadata, branch protection state and rulesets recorded in
  `meta/deletion-candidates.json`.

Ready to delete once scoped (`gh auth refresh -h github.com -s delete_repo`):

| repository | class | basis |
|---|---|---|
| `computeflow-website` | SITE_ONLY_STUB | 9-file static scaffold; canonical parent exists |
| `cortexhq-website` | SITE_ONLY_STUB | same |
| `cropshield-ai-website` | SITE_ONLY_STUB | same |
| `datatherapy-website` | SITE_ONLY_STUB | same |
| `deploylocal-website` | SITE_ONLY_STUB | same |
| `devstate-website` | SITE_ONLY_STUB | same |
| `freewash-finder` | EMPTY_REPO | 0 commits, 0 KB; successor confirmed present |

**Successor gate for `freewash-finder`: SATISFIED.** `freeconomie` is listed
with a canonical URL, was last updated 2026-09-28 and is non-empty, against
`freewash-finder`'s last update of 2026-04-08 at 0 KB. Note the anomaly: the
repository resolves through `gh repo list` but returns 404 to `gh repo view`,
`gh api repos/...` and `git clone`. That access inconsistency is unresolved
and is also why `freeonomie` could not be published.

### Held rather than deleted

| repository | why held |
|---|---|
| `cruxenio-website` | canonical parent no longer exists; content is unique |
| `cxntradict-website` | same |
| `emailsimple-website` | same |
| `grokbot-concierge-website` | parent project is private; not a website-only stub |

The three orphans were **not** deleted. Deleting them would destroy the only
remaining copy of their content, and "has a website suffix" is not by itself
evidence that a repository is a disposable site.

### Not treated as website-only

`agentos-website`, `gh0st-website`, `grokbot-office-website`,
`grokbot-society-website`, `grokinstall-website`, `grokmax-website`,
`opencode-watchdog-website` are substantial Next.js/Vite applications with real
source trees, not website-only stubs. All were published rather than deleted.

---

## PRIVATE

**11 denylisted repositories, all private. Zero public violations.**

Enforced substring rules: `noaerth`, `autobuilder`, `pairs`; exact `paios-one`,
`openlegal-data`. Verified against live API state after every batch.

| metric | value |
|---|---|
| denylisted repositories | 11 |
| public violations | **0** |

Denylist names were also removed from the public system map, the system-map
evidence file, the chosen-art manifest and the gallery flags. The
`test_disclaimed_relationships_stay_absent` check was rewritten to iterate the
private name set rather than hard-coding one name, because the assertion
previously named the repository it existed to protect.

---

## PUBLIC

135 public repositories. After applying the profile's own classification and
withholding rules, 122 are eligible for the public inventory:

| class | count |
|---|---|
| FLAGSHIP | 5 |
| PUBLIC_PROJECT | 115 |
| PROFILE | 1 |
| LEGACY_EASTER_EGG | 1 |

### Security gate results

All 114 initial publication candidates were scanned before any visibility
change:

- recursive git tree enumeration per repository
- dangerous-filename detection (`.pem`, `.key`, `.p12`, `.pfx`, `id_rsa`,
  `.env`, `.sqlite`, `.db`, `.dump`)
- credential pattern scan (AWS keys, GitHub tokens, private key blocks, Google
  API keys, Slack tokens, GitLab tokens, hardcoded credential assignments)

| result | count |
|---|---|
| scanned | 114 |
| real credential findings | **0** |
| `.env.example` with placeholders only | 7 — verified empty or `YOUR_*` |
| committed `.aider` tool caches | 4 — removed and published after cleanup |

A further 13 website repositories were content-scanned and published after
their parent projects became public.

---

## REPOSITORY COMPLETENESS

Measured by `scripts/audit_repo_completeness.py`.

| field | state |
|---|---|
| description | 122/122 |
| topics | 122/122 |
| README | **122/122** |
| designed visual identity | **8/120 (7%)** |
| hero / animation / static fallback | 5 flagships only |
| license, security, contributing, CI, tests, benchmark, release, homepage | conditional, reported N/A where inapplicable |
| private-data leaks in READMEs | **0** |

### READMEs added this round

46 of 122 public repositories had no README. All 46 now have one, generated
from the repository's own contents by
`scripts/profile_art/generate_missing_readme.py`: description, topics,
language, license, and the files actually present at the root.

Every generated README declares `STATUS: UNDOCUMENTED` and marks each property
as read or not-recorded. Repositories with no description and no informative
files say exactly that. This is deliberate — a generated pitch would have made
46 undocumented repositories look documented.

---

## ENGINEERING EVIDENCE

### Defects found and fixed this round

| repository | defect | how found |
|---|---|---|
| `seai-mind` | `secrets` used in a step-level `if`, which is not a valid context. GitHub rejected the whole workflow file, so every run failed with **zero jobs and no logs**. 11/11 historical runs. | dispatching the workflow directly, which surfaces the parser error the run view hides |
| `seai-mind` | `os.cpus()` returns `[]` in sandboxed environments, so `cpu.cores` was 0 against a schema requiring >0, throwing out of `initialize()` and failing 14 tests | improving a test assertion to print the `Result` error instead of `{}` |
| `seai-mind` | `pnpm --frozen-lockfile --offline` on a cold runner cache | reading the workflow after the parser bug stopped hiding everything |
| `seai-mind` | typecheck and test ran with no preceding workspace build, so `packages/*` could not resolve each other through uncommitted `dist/` | fresh-clone reproduction |
| `seai-mind` | CI exercised only `./web`; the 7 kernel packages were never built, typechecked or tested | mapping what the workflow actually ran |
| profile | visibility filter tested a `private` boolean the snapshot never carried, so **all 11 denylisted repositories were published into the inventory** | the safety suite after mass publication |
| profile | `ci.green` was `conclusion == "success"`, so "no data" and "broken" were the same state; all 133 systems reported `ci_not_green` | reading the generated inventory |
| profile | content ledger republished `/Users/<name>/...` paths lifted from a newly published README | the no-local-paths safety check |
| profile | inventory recorded no README field, so coverage was unmeasurable | reading the coverage assertion |

Nine substantive defects, all with reproduction. The `seai-mind` chain is the
most valuable: a single unparseable workflow line meant the repository had
**never once executed CI in its history**, which is why a genuinely broken
dependency graph could sit on `main` indefinitely.

### Current measured state

| metric | value |
|---|---|
| verified tests | 2,032 |
| releases | 9 |
| CI green | 7 |
| CI red | 3 (`gh0st`, `ai-dev-workflow-starter`, `redwoud`) |
| CI unknown (no workflow) | 110 |
| repositories with a CI workflow | 10 |

CI state is now three-valued — `green` / `red` / `unknown`. Absence of
measurement is no longer reported as failure.

### Fresh clone

Not run at portfolio scale. The `seai-mind` defects were found by simulating a
fresh checkout, which is a partial substitute and is recorded as such.

### Benchmarks

Only the Evidence Engine's own scaffold exists. No portfolio benchmark suite
was executed, so no `BENCHMARKS.md` is published. Presenting a benchmark index
without measurements would be decoration.

---

## FINANCIALS

**Not published.** The Noaerth v0.2 model figures could not be located in any
form anywhere under `/Users/matador/startups`. 106 unrelated `venture-os`
directories exist; none matches the stated counts, gross values or
risk-adjusted values.

Publishing a figure from a source that cannot be produced would make
every other number on this profile untrustworthy. The financial section, its
animated plate and `PORTFOLIO_ECONOMICS.md` are therefore **deliberately
absent**, and their absence is the correct output of the validation gate.

Required before this section can exist: a model workbook or script with a
version and an as-of date.

---

## PROFILE

| item | state |
|---|---|
| inventory | rebuilt: 122 eligible public repositories |
| pins | **unchanged** — still 5 flagships, not 6 |
| public universe map | regenerated, private control plane removed from the CONTROL layer |
| financial plate | not generated (see FINANCIALS) |
| evidence index section | not added |
| social preview | not regenerated per-repository |
| README blocks | regenerated from current measured state |

### Pin set

Not re-scored. The previous five-flaghip set is intact and all five are public
and non-denylisted, but selecting six would require re-scoring across 122
repositories against the six capability axes, which was not completed. Stating
a six-pin order that was not derived from the scoring would be a guess
presented as a decision.

---

## ANIMATION

| metric | value |
|---|---|
| assets in the profile | 34 |
| total payload | 405.1 KB |
| largest asset | 30.5 KB |
| chosen-map assets | 25 |
| animated variants | flagships only |
| per-repository animation | **0 of 122** |

The motion-first policy was **not** executed beyond the existing flagship set.
Generating 122 distinct animated identities, each with a distinct primary
motif, material, colour family and geometric composition, is a design
production pass rather than an automation task. Automating it would produce
the "nine re-coloured cards" failure the existing
`test_motifs_are_not_all_identical` check exists to prevent.

---

## MANUAL ITEMS

Genuinely unavoidable, and each is a single command or a UI action:

| # | action | why |
|---|---|---|
| 1 | `gh auth refresh -h github.com -s delete_repo` | required to delete the 7 prepared repositories. Requires interactive browser auth. |
| 2 | `gh auth refresh -h github.com -s user` | required to change profile bio, and to read Actions billing |
| 3 | Investigate `freeonomie` returning 404 | listed and non-empty via `gh repo list`, but 404 to `gh api`, `gh repo view` and `git clone`. Blocks both its publication and deletion verification. |
| 4 | Pin repositories in the GitHub UI | pinning is UI-only; six pins cannot be set via API |
| 5 | Decide the three orphan website repositories | they have no canonical parent and unique content |
| 6 | Provide the Noaerth financial model | blocks the entire financial section |

---

## NOT DONE

Listed explicitly so nothing here reads as complete when it is not.

1. **Per-repository V5.1 READMEs and animated identities** — 8 of 120 systems
   have a designed mark. The 46 generated READMEs are factual placeholders
   marked `STATUS: UNDOCUMENTED`, not flagship presentations.
2. **Per-repository social previews** — not generated.
3. **Stage 4 publication blockers** — `gh0st` Tests and two other red CI
   workflows were not repaired.
4. **Portfolio benchmark suite** — no benchmarks were run.
5. **Financial section** — blocked on a source that does not exist locally.
6. **Six-pin re-score** — not performed.
7. **Evidence/benchmark/audit surfaces on individual repositories** — no
   `TECHNICAL_DILIGENCE.md`, `THREAT_MODEL.md` or ADR set was written.
8. **GitHubOS autopilot** — the monitoring loop was not built.
9. **ADRs, threat models, reproducibility docs, release discipline** — not
   written for any repository.
10. **Residual private-name references** in `scripts/profile_art/generate.py`
    and `scripts/github_art/build_gallery51.py` — identified, not yet removed.
11. **`ci_unknown` = 110** — 110 public repositories have no CI at all. The
    profile reports this rather than implying coverage.
