# GITHUB V6 PART 1 — BLOCKING DEFECT ROOT CAUSE ANALYSIS

Three defects were reported. All three are reproduced and traced to a specific
line of automation. This file records the cause so the fix can be verified
against it rather than against a symptom.

---

## DEFECT 1 — APPROVED ARTWORK REVERTED

### Status: ROOT CAUSE FOUND, FIX PRESENT, VERIFIED

The scheduled profile sync ran `scripts/profile_art/generate.py`, which
regenerates the whole art directory, then staged it with:

```yaml
git add README.md assets/profile
```

and committed with a message asserting:

> Automated refresh of measured metrics and generated artwork. Housekeeping only;
> **no hand-authored content is modified.**

That assertion was false. `generate.py` rewrites `hero-*.svg`,
`system-map-*.svg`, `terminal-*.svg` and every `windows/` panel wholesale, so an
approved hero could be replaced by whatever the generator emitted that day —
silently, on a schedule, under a commit message denying it.

### Architecture of the fix

1. `sync-profile.yml` no longer invokes `generate.py` at all. It updates only
   the factual signal.
2. Staging narrowed from the `assets/profile` directory to three named files.
   Sweeping the directory is what let a regenerated hero land as "housekeeping".
3. `.github-art/art-lock.json` hash-locks 49 design-controlled assets.
   `art_lock.py --verify` fails the workflow before any commit.
4. `verify()` cannot self-authorise. An earlier version treated "a design source
   changed" as permission, so adding *any* file to the source set — including the
   lock file itself — unlocked every asset and a tampered hero passed. The
   baseline now moves only on an explicit `--lock`.

### Verified this session

```
$ python3 scripts/profile_art/art_lock.py --verify
ART LOCK
  design assets tracked   : 49
  factual assets tracked  : 3
  bounded regions tracked : 4
  violations              : 0
  art lock holds
```

Tamper test, then restore:

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

The defect is now detectable in CI, not merely documented.

---

## DEFECT 2 — LITTLE OR NO ACTUAL ANIMATION

### Status: PARTIALLY FIXED, SCOPE GAP CONFIRMED

The previously shipped "animated" hero was the static hero plus a drifting
rectangle and a sweeping gradient. Sixteen of seventeen profile assets carried
no animation at all. That is why the result read as no animation.

### What now exists

`scripts/github_art/computational_hero.py` (commit `81554e5`) replaced ambient
motion with a depiction of the account's actual build pipeline: dependency graph
resolution, ordered compile stages, a test run advancing to completion, artifact
tagging. Verified in the committed asset:

| asset | `<animate*>` elements |
| --- | --- |
| `hero-motion.svg` | 55 (54 `<animate>` + 1 `<animateMotion>`) |
| `terminal-motion.svg` | 14 |
| `hero-dark.svg` (static) | 0 |
| `hero-light.svg` (static) | 0 |

Static variants carry no animation, so the reduced-motion path is honest.

### The scope gap

The final assertion reports `122 repositories without per-repository art`. Live
inspection against the GitHub API disagrees with the number, and the ledger
disagrees with both. Three separate accounting layers are out of step:

| layer | claim |
| --- | --- |
| live API: `assets/hero/` present | **43 of 123** public repos |
| `github-account-ledger.json` `hero_complete` | **1** `COMPLETE`, 122 `NOT_APPLICABLE` |
| final assertion | 122 pending |

The ledger records `NOT_APPLICABLE` with the reason *"no hero asset at repository
root"*. The art lives at `assets/hero/`, not at the repository root, so the
ledger's own probe looks in the wrong place and reports absence where art
exists. The assertion then reads the ledger and inherits the error. A completion
report built on that number cannot be trusted, which is why this is being fixed
before Part 2 rather than reported around.

---

## DEFECT 3 — IDENTITY NOT ADAPTED TO THE PUBLIC REPOSITORIES

### Status: ROOT CAUSE FOUND, NOT YET FIXED

This is the deepest of the three. The dossier is supposed to be the input to
the visual identity. In practice the dossier carries almost no project-specific
content, so the art had nothing to adapt to.

Measured across all 126 dossiers:

| field | dossiers empty |
| --- | --- |
| `problem` | **126 / 126** |
| `primary_user` | **126 / 126** |
| `major_components` | **126 / 126** |
| `data_flow` | **126 / 126** |
| `state_model` | **126 / 126** |
| `input_types` | **126 / 126** |
| `output_types` | **126 / 126** |
| `verified_features` | **126 / 126** |
| `known_limitations` | **126 / 126** |
| `security_characteristics` | **126 / 126** |
| `frameworks` | **126 / 126** |
| `public_noaerth_positioning` | **126 / 126** |
| `venture_stage` | **126 / 126** |
| `material_family` | **126 / 126** |
| `color_family` | **126 / 126** |
| `terminal_metaphor` | 108 / 126 |

**All 126 dossiers have every one of these nineteen fields empty.** Only `purpose`
is populated, and it is copied verbatim from the GitHub `description`.

### Cause A — the fields are hardcoded empty

`scripts/profile_art/build_dossiers.py`, `build_dossier()`:

```python
"problem": "",
"primary_user": "",
"frameworks": [],
"major_components": [],
"data_flow": "",
"state_model": "",
"input_types": [],
"output_types": [],
"verified_features": [],
"experimental_features": [],
"known_limitations": [],
"benchmark_dimensions": [],
"security_characteristics": [],
"public_noaerth_positioning": (venture or {}).get("positioning", ""),
"venture_stage": (venture or {}).get("status", ""),
"secondary_visual_metaphor": "",
"material_family": "",
"color_family": "",
```

The builder never derives them. It reads the local source, then discards
everything except language, architecture keyword, category keyword and the GitHub
description. `inspect_local()` already collects `architecture_doc`, `readme_text`,
`src`, `tests`, `scripts` and `manifests` — the evidence is loaded and then not
used.

### Cause B — the venture cache is empty where it matters

`.noaerth-public-ventures.json` holds 108 venture records. Every one of them has:

```
positioning : ""   (0 of 108 populated)
category    : ""   (0 of 108)
status      : ""   (0 of 108)
```

`fetch_noaerth_ventures.py` extracts name and site URL only. It hardcodes the
three remaining fields to `""`:

```python
"positioning": "",
"category": "",
"status": "",
```

The real card markup on `noaerth.com/portfolio` carries all of it — 107 cards,
each with a category, a status and a pitch line:

```html
<div class="venture-info-outline category-box">
  <span>Category</span><strong title="Developer tools">Developer tools</strong></div>
<div class="venture-info-outline status-box">
  <span>Status</span><strong>Live</strong></div>
...
<p class="nx-vos-pitch">Requested is not verified.</p>
```

So Source B of the project truth triangle was never actually read. The scraper
matched the cards and threw away their content.

### Cause C — the terminal metaphor is a boolean

```python
"terminal_metaphor": ("a cursor running real commands"
                      if local.get("scripts") else ""),
```

`local["scripts"]` is non-empty for any repository with a `package.json`, so
108 of 126 dossiers received the same string. Section 11 of the brief forbids
exactly this: a command that cannot be verified must not appear in animation.
The field asserts a capability instead of naming the real commands.

### Consequence, visible in shipped art

Because the dossier is empty, the generator falls back to counted facts. Five
distinct repositories ship a byte-identical hero layout with only the name
substituted:

```
Cruxenio   "PUBLIC PROJECT · AGENT"  "Cruxenio. build via `package.json`."
FungMind   "PUBLIC PROJECT · AGENT"  "FungMind. build via `package.json`."
Modex      "PUBLIC PROJECT · AGENT"  "Modex. build via `package.json`."
ShopRight  "PUBLIC PROJECT · AGENT"  "ShopRight. build via `package.json`."
SoulMayte  "PUBLIC PROJECT · AGENT"  "SoulMayte. build via `package.json`."
```

That is the "generic card generator" the brief prohibits, and it is a direct
downstream consequence of the empty dossier. Fixing the art without fixing the
dossier would produce 122 near-identical heroes with better animation.

Structural-signature analysis of `hero-motion.svg` across the 43 repositories
that have art: **30 distinct signatures**, with the largest collision group at 5
repositories and three further groups at 4, 3 and 2.

---

## SECONDARY DEFECT — THE ART GENERATOR IS NOT REPRODUCIBLE

`assets/hero/*.svg` was committed to each repository by a process whose source
is not present on this machine. Verified:

```
$ grep -rl "Generated from this project's dossier" /srv/noaerth 2>/dev/null
(no results)
```

The commit message on `M4G3LL4N0/agentos@9a6515de` reads:

> Generated from this project's dossier: DISTRIBUTED / INFRASTRUCTURE. The
> animation depicts the real state transition, not a decorative loop.

The commits are real and dated `2026-10-06T17:15`, but no script in
`github-profile`, `portfolio-os` or anywhere under `/srv/noaerth` emits that
string, and no local project folder contains `assets/hero/`. Consequences:

- The 43 existing heroes **cannot be regenerated**, so they cannot be verified.
- They are **not covered by any art lock** — `art-lock.json` tracks the profile
  repository's assets only.
- They violate section 15 of the brief: committed assets must be generated *from*
  a versioned design source. There is no design source.

This is the most dangerous of the findings, because it means Part 2 would
reproduce exactly the failure mode that caused the original complaint: art that
exists but cannot be traced, reproduced or protected.

---

## FIX ORDER

1. Restore a versioned, reproducible per-repository art generator, and bring the
   43 untracked heroes under the lock. Nothing else can be trusted until art has
   a source.
2. Repair the venture scraper so Source B carries category, status and pitch.
3. Derive the nineteen empty dossier fields from local source instead of
   hardcoding them empty.
4. Replace the boolean `terminal_metaphor` with commands verified against each
   repository's own CLI.
5. Fix the ledger's `assets/hero` probe so completion accounting is truthful.
6. Re-run the uniqueness audit. It cannot pass until 1–5 are done, because the
   collisions are downstream of the empty dossier.
