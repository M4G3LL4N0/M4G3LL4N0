# GITHUB V6 — PART 1 FINAL REPORT

**19 of 21 assertion gates pass.** The two that do not, and the exact queue
behind them, are at the end. Nothing below rounds up.

Every number in this report was produced by a committed script against a
committed artifact. The commands are listed so each figure can be reproduced.

---

## ART REVERSION

### Root cause

The scheduled profile sync ran `scripts/profile_art/generate.py`, which rewrites
the entire art directory — hero, system map, terminal, every flagship window —
then staged the directory with `git add README.md assets/profile` and committed
under a message asserting:

> Automated refresh of measured metrics and generated artwork. Housekeeping only;
> **no hand-authored content is modified.**

That assertion was false. An approved hero could be replaced by whatever the
generator emitted that day: silently, on a schedule, under a commit message
denying it had happened.

### Fix

Architectural, not cosmetic.

1. `sync-profile.yml` no longer invokes the design generator. It updates only
   the factual signal.
2. Staging narrowed from the `assets/profile` directory to three named files.
3. `.github-art/art-lock.json` hash-locks **49** design-controlled assets.
4. `verify()` cannot self-authorise. An earlier version treated "a design source
   changed" as permission, so adding *any* file to the source set — the lock file
   included — unlocked every asset and a tampered hero passed. The baseline moves
   only on an explicit `--lock`.

### Regression test

```
$ python3 scripts/profile_art/art_lock.py --verify
ART LOCK
  design assets tracked   : 49
  factual assets tracked  : 3
  bounded regions tracked : 4
  violations              : 0
  art lock holds
```

Tamper, then restore:

```
$ printf '\n<!-- tampered -->\n' >> assets/profile/hero-dark.svg
$ python3 scripts/profile_art/art_lock.py --verify
  violations : 1
    DESIGN ASSET ALTERED without an explicit --lock: assets/profile/hero-dark.svg
  exit 1

$ cp /tmp/hero-backup.svg assets/profile/hero-dark.svg
$ python3 scripts/profile_art/art_lock.py --verify
  violations : 0
  art lock holds
  exit 0
```

CI additionally asserts that `sync-profile.yml` neither runs the generator nor
stages the directory. The defect is detectable, not merely documented.

---

## THE THREE REPORTED DEFECTS

Full analysis with line-level causes: `GITHUB_V6_PART1_ROOTCAUSE.md`.

### 1 — Artwork reverted — **FIXED, VERIFIED**

Above. Root cause was found, the generator was removed from the scheduled path,
and the lock was rebuilt and proven by a tamper test.

### 2 — Little or no actual animation — **FIXED**

The previously "animated" hero was the static hero plus a drifting rectangle and
a sweeping gradient. Of the 43 repository heroes already published, the motion
was one opacity fade and a no-op rotation:

```xml
<animateTransform attributeName="transform" type="rotate"
  values="-0.0 980 210;0.0 980 210;-0.0 980 210" dur="26s"/>
```

Two thirds of the portfolio had no animation at all.

Now, measured on the committed assets:

| asset | animation elements |
| --- | --- |
| 126 × `hero-motion.svg` | **2,356** animate elements |
| heroes whose only motion is an opacity fade | **0** |
| static variants containing any animation element | **0** |
| distinct hero structures (text and names stripped) | **126 / 126** |

Each identity family has a motion primitive that shows work happening: packets
crossing a boundary that admits some and holds others, value allocating across a
ledger and settling, records traversing channels into an index that fills, nodes
advertising to a coordinator, claims rising into checkable tiers, a cursor
walking this project's real command list while a rail extends.

The static variants carry **no animation element at all** — verified by scan, not
assumed. `prefers-reduced-motion` is served a genuinely still image rather than
an animated one that respects a media query.

### 3 — Identity not adapted to the repositories — **FIXED**

This was the deepest. The dossier is supposed to be the input to the visual
identity. All 126 dossiers had **nineteen semantic fields hardcoded empty** — not
mostly empty, all of them:

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

Three causes, each fixed at its source:

**The venture scraper never read Source B.** It matched the card wrapper, took a
name and a URL, and hardcoded `positioning`, `category` and `status` to `""`. 108
ventures were cached and not one carried a field. The card markup has all of it:

```
category 107/107 · status 107/107 · positioning 106/107 · milestone 107/107
```

One subtlety that produced a real misparse: the enclosing `<article>` opens
*after* the wrapping `<a>`, so searching backwards from the anchor finds the
*previous* card and shifts every field by one row. SunsetX's pitch was being read
as AgentOS's.

**The dossier builder loaded the evidence and discarded it.** `inspect_local()`
already collected README, `ARCHITECTURE.md`, the module map, manifests, CLI
source and the test tree. None of it reached the dossier.
`scripts/profile_art/comprehension.py` now derives the fields from that evidence.

**The terminal metaphor was a boolean.** `"a cursor running real commands" if
local["scripts"]` is true of every repository with a `package.json`, so 108 of 126
dossiers received the same string. It is now the **real commands**, parsed from
the argument parser with subcommand nesting resolved — `$ agentos objective
create`, not `$ agentos create` — plus Node bin entries and `package.json`
scripts. Eleven projects now carry a verified command list; a project with no CLI
carries none, because a fabricated command is worse than no terminal.

### Measurement bugs found along the way

Each of these was shipping a false claim, and each was caught against source:

| bug | effect |
| --- | --- |
| GitHub topics decided the product category | every repo carried the same `security` topic → **59 projects classified as security systems**, including cloudcastle, TherapyUX and ForeverLuvd |
| Next.js API handlers matched no interface pattern | 79 of 86 `DATA_FLOW` dossiers reported no interfaces; **blitzproof ships 8 route handlers and claimed none** |
| `create-next-app` scaffolding read as prose | **43 dossiers took the framework's opening paragraph as their problem statement**, 42 more a "Learn More" link list |
| untested components filed as experimental features | would have shipped **719 maturity claims the code does not support** |
| `route` treated as logistics vocabulary | **32 Next.js apps classified as logistics systems** |
| `build` treated as developer-tooling vocabulary | 21 repositories, from `npm run build` alone |
| `pricing` in the derived route list | 13 projects classified as capital systems |
| default branch not passed to the tree fetch | 15 repositories measured against `main` instead of their own branch; **3 with published art recorded as having none** |
| ledger tree fetch not retried | one 502 made 15 repositories with art record as having none |
| `ART_PUBLISHED` absent from the terminal state set | 126 finished repositories reported as 126 pending; the queue could never drain |
| hero block referenced `computational-*.svg` | the generator never produced those files — every published README rendered a broken image |

### Identity now resolves from the project, not the name

`generative_identity.py` picked the family from the repository **name and GitHub
topics**, then a node-id hash for everything else — the inverse of what section
22 requires. `scripts/profile_art/v6_identity.py` resolves the family from the
dossier fingerprint (architecture, interfaces, declared persistence, verified
CLI, security mechanisms, route handler names) and lets the stable seed vary
motif, material, topology, depth and accent *inside* that family. The report
proves the inversion by stripping a project's evidence and showing its family
change.

Getting the family right also changed the category. `agentos` resolved to
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
| **matched a public venture card** | **94** (was 0 — Source B was never read) |

The ten refusals are recorded with evidence in `resolve_unmapped.py`, not
guessed:

| resolution | repositories |
| --- | --- |
| PROFILE | `M4G3LL4N0` |
| MISNAMED_WORK | `src`, `styles`, `why-are-you-here` |
| ARTIFACT | `node_modules` — `.DS_Store`, `.package-lock.json`, and installed packages (`@supabase`, `@types`, `clsx`, `tslib`, `undici-types`, `ws`). A committed dependency directory, not source. **Owner decision required**; deletion is not authorised and it is not featured. |
| UNRESOLVED_REVIEW | `imessage`, `FundMind`, `STRxGNTH`, `Zaeus`, `ai-dev-workflow-starter` |

---

## DOSSIERS

**126 of 126.** Field population, measured:

| field | filled | field | filled |
| --- | --- | --- | --- |
| `major_components` | **126** | `frameworks` | 116 |
| `known_limitations` | 120 | `data_flow` | 107 |
| `problem` | 113 | `output_types` | 105 |
| `input_types` | 101 | `primary_user` | 94 |
| `state_model` | 83 | `security_characteristics` | 21 |
| `benchmark_dimensions` | 10 | `terminal_metaphor` | 11 |
| `verified_features` | 2 | `primary_workflow` | 6 |

`verified_features` at 2 is not a gap in the extractor: 103 of 126 repositories
have **no test tree at all**, confirmed against the live recursive tree, not just
the local checkout. A component is listed as verified only when a test file names
it. `primary_workflow` is low because most projects state no workflow at all —
their README is create-next-app scaffolding.

Every remaining gap is recorded per dossier in `unresolved` rather than guessed. A
guess here becomes an artwork and therefore a claim about the project.

---

## ART

| metric | value |
| --- | --- |
| projects with an art plan | **126** |
| assets generated | **630** (5 per project) |
| distinct drawn structures per variant | **126 / 126** — 0 collisions |
| identity composition collisions | **0** of 126 |
| design families | **9** |
| distinct motifs | **28** |
| distinct materials | **11** |
| distinct topologies | 7 |
| distinct motion stories (text) | 15 |
| heroes whose only motion is a fade | **0** |

### Design family, not template

Shared DNA across the portfolio: the same type stack, the same spacing
discipline, the same token logic, the same material treatment, the same motion
discipline. Variable per project: the subject (family), the motif, the material,
the topology, the depth, the accent, the geometry phase, the stage names, the
motion primitive, the palette weighting.

Four identity fields — motif, material, accent and depth — were originally
resolved, recorded and then **ignored by the renderer**, so projects differing
only in those values drew identically. All four now reach the drawing. Four
further collisions came from a character-sum digest where `soft_tiles` and
`modular_grid` reduce to the same remainder; replaced with a digest over
`motif:phase:material`.

### The art has a design source

43 repositories shipped `assets/hero/*.svg` whose commit messages read "Generated
from this project's dossier", with **no script on disk that emits that string**:

```
$ grep -rl "Generated from this project's dossier" /srv/noaerth
(nothing)
```

That art could not be regenerated, verified, or protected — the exact conditions
that let unreproducible artwork into the portfolio.
`scripts/profile_art/repo_art.py` is now that design source, and
`.github-art/repo-art-manifest.json` commits a SHA-256 per asset.

---

## PROFILE

| item | state |
| --- | --- |
| art locked | **yes**, 49 design assets |
| scheduled automation can regenerate design art | **no**, and CI asserts it |
| artwork reverted by automation | **impossible by construction** |
| portfolio economics published and labelled | **yes**, all five labels |
| financial plate animated + static dark/light + reduced motion | **yes** |

Financial geometry is honest by construction: the scenarios differ by roughly
12×, so nothing encodes magnitude as volume or perspective. Every mark is a flat
bar proportional to value on a **printed linear scale**. The owner's arithmetic was
verified — the 25% haircut reproduces the stated risk-adjusted values to within
$250 on low and base, exactly on high — and `PORTFOLIO_ECONOMICS.md` states that
internal consistency is not the same as verification.

---

## REPRODUCING EVERY NUMBER

```bash
python3 scripts/profile_art/fetch_noaerth_ventures.py     # Source B
python3 scripts/profile_art/comprehension.py --all --apply --report
python3 scripts/profile_art/v6_identity.py --write
python3 scripts/profile_art/repo_art.py --all --outdir build/repo-art
python3 scripts/profile_art/repo_art.py --all --outdir /tmp/x --check   # determinism
python3 scripts/profile_art/gallery.py                    # GITHUB_V6_DOSSIER_GALLERY.html
python3 scripts/profile_art/build_art_plan.py             # + --audit-only for the gate
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

**126 repositories** have a mapping, a dossier, an identity, an animation
concept, a terminal concept, a README plan, a metadata plan and published art.
All 126 are published and verified live.

---

## BLOCKERS

Exact blockers only. Every one of these needs an owner decision; none can be
resolved by automation, and generating art for an unidentified project is the
failure this work exists to prevent.

| # | blocker | blocks | resolution |
| --- | --- | --- | --- |
| 1 | `node_modules` is a committed dependency directory, not a project | 1 repository | owner decision; deletion not authorised |
| 2 | `ai-dev-workflow-starter`, `FundMind`, `imessage`, `STRxGNTH`, `Zaeus` have no local source | 5 repositories | owner supplies the project path |
| 3 | `src` and `styles` are real engineering under directory-style names | 2 repositories | owner confirms the intended names |
| 4 | `delete_repo` scope absent | 18 prepared deletions | `gh auth refresh -h github.com -s delete_repo` (interactive) |
| 5 | pinning is UI-only | six pins | manual |

Two assertion gates therefore remain `[FAIL]`, and both are the same blocker set
seen from different angles:

```
1. generate per-repository art: 9 repositories
   ['ai-dev-workflow-starter', 'FundMind', 'imessage', 'node_modules', 'src', ...]
2. process: 4 site-only repositories plus the same unresolved set
```

The remaining 9 are precisely the repositories in blockers 1–3. They have no
dossier because they have not been identified, and they have no art because art
is generated from a dossier.
