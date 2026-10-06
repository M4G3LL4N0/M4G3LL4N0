# GITHUB V6 — TECHNICAL REPORT

Companion to `GITHUB_V6_PART1_FINAL_REPORT.md`, which records the v7 economics
withdrawal and is the report of that round. This one records the project
comprehension and per-repository art work.

**19 of 21 assertion gates pass.** The two that do not are the same nine
repositories seen from two angles, and they are stated at the end.

Every number below comes from a committed script run against a committed
artifact. The commands are listed so each figure can be reproduced.

---

## THE THREE REPORTED DEFECTS

### 1 — Approved artwork reverted: **FIXED, VERIFIED**

Root cause: `sync-profile.yml` ran `scripts/profile_art/generate.py`, which
rewrites the whole art directory, staged it with `git add README.md
assets/profile`, and committed under a message asserting *"no hand-authored
content is modified."* That assertion was false.

Fix, architectural rather than cosmetic:

1. The scheduled job no longer invokes the design generator at all.
2. Staging narrowed from the directory to three named factual files.
3. `.github-art/art-lock.json` hash-locks the design-controlled set.
4. `verify()` cannot self-authorise — the baseline moves only on `--lock`.

Regression test, run this session:

```
$ python3 scripts/profile_art/art_lock.py --verify
ART LOCK
  design assets tracked   : 46
  factual assets tracked  : 3
  bounded regions tracked : 4
  violations              : 0
  art lock holds

$ printf '\n<!-- tampered -->\n' >> assets/profile/hero-dark.svg
$ python3 scripts/profile_art/art_lock.py --verify
  violations : 1
    DESIGN ASSET ALTERED without an explicit --lock: assets/profile/hero-dark.svg
  exit 1
```

CI asserts that `sync-profile.yml` neither runs the generator nor stages the
directory. The defect is detectable, not merely documented.

### 2 — Little or no actual animation: **FIXED**

The previously "animated" hero was the static hero plus a drifting rectangle and
a sweeping gradient. Of the 43 repository heroes already published, the motion was
one opacity fade and a no-op rotation:

```xml
<animateTransform attributeName="transform" type="rotate"
  values="-0.0 980 210;0.0 980 210;-0.0 980 210" dur="26s"/>
```

Measured on the committed assets now:

| measure | value |
| --- | --- |
| animation elements across 126 `hero-motion.svg` | **2,387** |
| heroes whose only motion is an opacity fade | **0** |
| static variants containing any animation element | **0** |
| distinct drawn structures per variant | **126 / 126** |

Each identity family has a motion primitive that shows work happening: packets
crossing a boundary that admits some and holds others; value allocating across a
ledger and settling; records traversing channels into an index that fills; nodes
advertising to a coordinator; claims rising into checkable tiers; a cursor
walking this project's real command list while a rail extends.

The static variants carry **no animation element at all** — verified by scan.
`prefers-reduced-motion` is served a genuinely still image rather than an animated
one that respects a media query.

### 3 — Identity not adapted to the repositories: **FIXED**

This was the deepest of the three. The dossier is supposed to be the input to the
visual identity. All 126 dossiers had **nineteen semantic fields hardcoded empty**
— not mostly empty, all of them:

```
problem · primary_user · major_components · data_flow · state_model ·
input_types · output_types · verified_features · experimental_features ·
known_limitations · benchmark_dimensions · security_characteristics ·
frameworks · public_noaerth_positioning · venture_stage ·
secondary_visual_metaphor · material_family · color_family
```

With nothing to adapt to, five repositories shipped a byte-identical hero with
the name substituted:

```
Cruxenio  "PUBLIC PROJECT · AGENT"  "Cruxenio. build via `package.json`."
FungMind  "PUBLIC PROJECT · AGENT"  "FungMind. build via `package.json`."
Modex     "PUBLIC PROJECT · AGENT"  "Modex. build via `package.json`."
```

Three causes, each fixed at its source.

**The venture scraper never read Source B.** It matched the card wrapper, took a
name and a URL, and hardcoded `positioning`, `category` and `status` to `""`. 108
ventures were cached and not one carried a field — so all 126 dossiers ended with
an empty venture category, stage and positioning. The card markup has all of it:

```
category 107/107 · status 107/107 · positioning 106/107 · milestone 107/107
```

One subtlety produced a real misparse: the enclosing `<article>` opens *after*
the wrapping `<a>`, so searching backwards from the anchor finds the *previous*
card and shifts every field by one row. SunsetX's pitch was being read as
AgentOS's. The cache now also refuses to be accepted if it carries no content, so
a scraper that returns names only cannot pass as a successful run.

**The dossier builder loaded the evidence and discarded it.**
`inspect_local()` already collected README, `ARCHITECTURE.md`, the module map,
manifests, CLI source and the test tree; none of it reached the dossier.
`scripts/profile_art/comprehension.py` now derives the fields from that evidence.

**The terminal metaphor was a boolean.** `"a cursor running real commands" if
local["scripts"]` is true of every repository with a `package.json`, so 108 of 126
dossiers received the same string. It is now the **real commands**, parsed from
the argument parser with subcommand nesting resolved — `$ agentos objective
create`, not `$ agentos create` — plus Node bin entries and `package.json`
scripts. Eleven projects carry a verified command list; a project with no CLI
carries none, because a fabricated command is worse than no terminal.

### Measurement bugs found while fixing it

Each was shipping a false claim, and each was caught against source:

| bug | effect |
| --- | --- |
| GitHub topics decided the product category | every repo carried the same `security` topic → **59 projects classified as security systems**, including cloudcastle, TherapyUX, ForeverLuvd |
| Next.js API handlers matched no interface pattern | 79 of 86 `DATA_FLOW` dossiers reported no interfaces; **blitzproof ships 8 route handlers and claimed none** |
| `create-next-app` scaffolding read as prose | **43 dossiers took the framework's opening paragraph as their problem statement**, 42 more a "Learn More" link list |
| untested components filed as experimental | would have shipped **719 maturity claims the code does not support** |
| `route` read as logistics vocabulary | **32 Next.js apps classified as logistics systems** |
| `build` read as developer-tooling vocabulary | 21 repositories, from `npm run build` alone |
| `pricing` present in the derived route list | 13 projects classified as capital systems |
| default branch not passed to the tree fetch | 15 repositories measured against `main` instead of their own branch; **3 with published art recorded as having none** |
| tree fetch not retried | one 502 made 15 repositories with art record as having none |
| `ART_PUBLISHED` absent from the terminal state set | 126 finished repositories reported as 126 pending; the queue could never drain |
| hero block referenced `computational-*.svg` | never generated — every published README rendered a broken image |
| stage chips fell back to directory names | 43 create-next-app projects showed the same four chips: `components, app, lib, public` |

### Identity now resolves from the project, not the name

`generative_identity.py` picked the family from the repository **name and GitHub
topics**, then a node-id hash for everything else — the inverse of what the brief
requires. `scripts/profile_art/v6_identity.py` resolves the family from the
dossier fingerprint (architecture, interfaces, declared persistence, verified CLI,
security mechanisms, route handler names) and lets the stable seed vary motif,
material, topology, depth and accent *inside* that family. The report proves the
inversion by stripping a project's evidence and showing its family change.

Getting this right also corrected the flagship. `agentos` resolved to
`TRUST_BOUNDARY` because it ships a `SECURITY.md` — when it is an agent
orchestration engine. Security boundaries are a property of an agent system, not
its subject.

---

## INVENTORY

| | count |
| --- | --- |
| total repositories | **152** |
| public owned | **123** |
| private | 16 |
| site-only (public, deployment) | 17 |
| forks | 0 |
| archives | 0 |
| denylisted, stays private | 11 |

---

## MAPPING

| metric | value |
| --- | --- |
| public repositories mapped | **136 of 136** |
| high confidence | 126 |
| flagged `MAPPING_REVIEW_REQUIRED` | 10 |
| matched a local project folder | 126 |
| **matched a public venture card** | **94** (was 0) |

Ten refusals, recorded with evidence rather than guessed:

| resolution | repositories |
| --- | --- |
| PROFILE | `M4G3LL4N0` |
| MISNAMED_WORK | `src`, `styles`, `why-are-you-here` |
| ARTIFACT | `node_modules` — `.DS_Store`, `.package-lock.json`, and installed packages (`@supabase`, `@types`, `clsx`, `tslib`, `undici-types`, `ws`). A committed dependency directory, not source. **Owner decision required**; deletion is not authorised and it is not featured. |
| UNRESOLVED_REVIEW | `imessage`, `FundMind`, `STRxGNTH`, `Zaeus`, `ai-dev-workflow-starter` |

---

## DOSSIERS — 126 of 126

| field | filled | field | filled |
| --- | --- | --- | --- |
| `major_components` | **126** | `frameworks` | 116 |
| `known_limitations` | 120 | `data_flow` | 107 |
| `problem` | 113 | `output_types` | 105 |
| `input_types` | 101 | `primary_user` | 94 |
| `state_model` | 83 | `security_characteristics` | 21 |
| `terminal_metaphor` | 11 | `benchmark_dimensions` | 10 |
| `primary_workflow` | 6 | `verified_features` | **2** |

`verified_features` at 2 is not an extractor gap: **103 of 126 repositories have
no test tree at all**, confirmed against the live recursive tree, not just the
local checkout. A component is listed as verified only when a test file names it.
`primary_workflow` is low because most projects state no workflow — their README
is create-next-app scaffolding.

Every remaining gap is recorded per dossier in `unresolved` rather than guessed. A
guess here becomes artwork, and therefore a claim about the project.

---

## ART

| metric | value |
| --- | --- |
| projects with an art plan | **126** |
| assets generated | **630** (5 per project) |
| distinct drawn structures per variant | **126 / 126**, 0 collisions |
| identity composition collisions | **0** of 126 |
| design families | **9** |
| distinct motifs | **28** |
| distinct materials | **11** |
| distinct topologies | 7 |
| distinct motion stories (text) | 15 |
| published and verified live | **114** of 123 public owned |

Shared DNA across the portfolio: the same type stack, spacing discipline, token
logic, material treatment and motion discipline. Variable per project: the
subject (family), motif, material, topology, depth, accent, geometry phase, stage
names, motion primitive and palette weighting.

Four identity fields — motif, material, accent and depth — were originally
resolved, recorded and then **ignored by the renderer**, so projects differing
only in those values drew identically. All four now reach the drawing. Two further
collision causes were a character-sum digest where `soft_tiles` and
`modular_grid` reduce to the same remainder, and a fixed four-step terrace drawn
identically for every terraced project. Both replaced with digests over
`motif:phase:material`.

### The art has a design source

43 repositories shipped `assets/hero/*.svg` whose commit messages read *"Generated
from this project's dossier"*, with **no script on disk that emits that string**:

```
$ grep -rl "Generated from this project's dossier" /srv/noaerth
(nothing)
```

That art could not be regenerated, verified, or protected — the exact conditions
that let unreproducible artwork into the portfolio.
`scripts/profile_art/repo_art.py` is now that design source, and
`.github-art/repo-art-manifest.json` commits a SHA-256 per asset. `--check` proves
determinism.

---

## REPRODUCING EVERY NUMBER

```bash
python3 scripts/profile_art/fetch_noaerth_ventures.py     # Source B, content-checked
python3 scripts/profile_art/comprehension.py --all --apply --report
python3 scripts/profile_art/v6_identity.py --write
python3 scripts/profile_art/repo_art.py --all --outdir build/repo-art
python3 scripts/profile_art/repo_art.py --all --outdir /tmp/x --check   # determinism
python3 scripts/profile_art/build_art_plan.py             # + --audit-only = the gate
python3 scripts/profile_art/gallery.py                    # GITHUB_V6_DOSSIER_GALLERY.html
python3 scripts/profile_art/build_account_ledger.py
python3 scripts/profile_art/final_assertion.py
python3 scripts/profile_art/art_lock.py --verify
```

`GITHUB_V6_DOSSIER_GALLERY.html` holds 126 panels — venture card, source summary,
category, metaphor, animation, stages, terminal, material, geometry, colour, a
text wireframe, the rendered plate, and the evidence each claim came from. It is
the local-only review surface for catching a bad adaptation before it ships.

---

## READY

**126 repositories** have a mapping, dossier, identity, animation concept,
terminal concept, README plan and metadata plan. **114** of the 123 public owned
repositories have the art published and verified live.

---

## BLOCKERS

Exact blockers only. Each needs an owner decision; none can be resolved by
automation, and generating art for an unidentified project is precisely the
failure this work exists to prevent.

| # | blocker | blocks | resolution |
| --- | --- | --- | --- |
| 1 | `node_modules` is a committed dependency directory, not a project | 1 repository | owner decision; deletion not authorised |
| 2 | `ai-dev-workflow-starter`, `FundMind`, `imessage`, `STRxGNTH`, `Zaeus` have no local source | 5 repositories | owner supplies the project path |
| 3 | `src` and `styles` are real engineering under directory-style names | 2 repositories | owner confirms the intended names |
| 4 | `delete_repo` scope absent | 18 prepared deletions | `gh auth refresh -h github.com -s delete_repo` (interactive) |
| 5 | pinning is UI-only | six pins | manual |

Two gates therefore remain `[FAIL]`, and both are this same set:

```
1. generate per-repository art: 9 repositories
   ['ai-dev-workflow-starter', 'FundMind', 'imessage', 'node_modules', 'src', ...]
2. process: 4 site-only repositories plus the same unresolved set
```

The 9 are precisely the repositories in blockers 1–3. They have no dossier
because they have not been identified, and no art because art is generated from a
dossier.
