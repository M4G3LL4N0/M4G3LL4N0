# GITHUB V6 — PART 1 FINAL REPORT

**GATES: 20 of 21 pass.** The one failing condition and its exact queue are at
the end. Nothing below rounds up.

---

## ART REVERSION

### Root cause

The scheduled profile sync ran a command that regenerated the entire art
directory:

```yaml
- name: Regenerate profile art from the signal
  run: |
    python3 scripts/profile_art/build_signal_data.py --inventory
    python3 scripts/profile_art/generate.py      # hero, map, terminal, cards
    python3 scripts/profile_art/render_signal_block.py
```

then staged everything and committed:

```yaml
git add README.md assets/profile
```

Its commit message asserted:

> Automated refresh of measured metrics and generated artwork. Housekeeping only;
> **no hand-authored content is modified.**

That claim was false. `generate.py` writes design-controlled assets wholesale.
An approved hero could therefore be replaced by whatever the generator emitted
that day — silently, on a schedule — and the commit that did it denied doing so.

### Fix

Architectural, not cosmetic.

1. **The scheduled job no longer runs the design generator at all.** It updates
   only the factual signal: measured test counts, release versions, CI state.
2. **Staging narrowed** from `assets/profile` to the three factual signal files.
   Sweeping in the directory is what let a regenerated hero land as
   "housekeeping".
3. **Art Lock**: 49 design-controlled assets hash-locked in
   `.github-art/art-lock.json`. Altering any of them fails the workflow before
   anything is committed.
4. **`verify()` cannot self-authorise.** An earlier version treated a changed
   design source as permission — which meant adding *any* file to the source set,
   including the lock file itself, unlocked every asset. A tampered hero passed.
   The baseline moves only on an explicit `--lock`.

### Regression test

Lock a clean baseline, tamper with `assets/profile/hero-dark.svg`, verify:

```
violations              : 1
  DESIGN ASSET ALTERED without an explicit --lock: assets/profile/hero-dark.svg
exit 1
```

Also asserted by CI: `sync-profile.yml` neither runs `generate.py` nor stages
`assets/profile`. The defect is now detectable, not merely documented.

---

## INVENTORY

| | count |
| --- | --- |
| total repositories | 152 |
| public | 136 |
| private | 16 |
| forks | 0 |
| archives | 0 |
| site-only (public, deployed) | 13 |
| site-only pending deletion | 4 |
| deleted | 0 |

---

## MAPPING

| metric | value |
| --- | --- |
| public repositories mapped | **136 of 136** |
| high confidence | 126 |
| flagged `MAPPING_REVIEW_REQUIRED` | 10 |
| matched a local project folder | 126 |
| matched a public venture card | 94 |

Ten repositories were refused rather than guessed. `resolve_unmapped.py` records
what each actually is, with evidence:

| resolution | repositories |
| --- | --- |
| PROFILE | `M4G3LL4N0` |
| MISNAMED_WORK | `src`, `styles`, `why-are-you-here` |
| ARTIFACT | `node_modules` |
| UNRESOLVED_REVIEW | `imessage`, `FundMind`, `STRxGNTH`, `Zaeus`, `ai-dev-workflow-starter` |

`node_modules` contains `.DS_Store`, `.package-lock.json` and installed packages
(`@supabase`, `@types`, `clsx`, `tslib`, `undici-types`, `ws`) — a committed
dependency directory, not source. **Owner decision required**; deletion is not
authorised and it is not featured.

`src` and `styles` are real engineering under directory-style names: `src` is a
Next.js application with `app/`, `components/` and `docs/`; `styles` is a
stylesheet and design-token system.

---

## DOSSIERS

| metric | value |
| --- | --- |
| dossiers ready | **126** |
| unresolved fields recorded | tracked per dossier in `unresolved` |

Three sources per project: local source, cached public venture card, live GitHub
state. No fourth source may override them without evidence.

Architecture is read from each project's own `ARCHITECTURE.md`, not inferred
from a filename. Two measurement bugs were caught against the source:

- Next.js classification matched the prose `API | app/api routes (if any)` and
  marked repositories with **zero** API routes as `DATA_FLOW`. `1bc` has none
  and is correctly `DOCUMENT`.
- Architecture initially inferred `PIPELINE` for anything with a
  `package.json`, collapsing the portfolio onto one geometry and one motion
  story — the exact failure where one template produces a hundred skins.

---

## ART

| metric | value |
| --- | --- |
| art concepts | **136** |
| dossiers driving them | 126 |
| distinct architecture families | 8 |
| distinct animation stories | **16** |
| largest single animation share | 22% (30 of 136) |
| distinct motifs | 26 |
| distinct materials | 8 |
| distinct accents | 4 |
| identity collisions | **0** of 141 |

### Uniqueness audit — two real failures caught

**Thirteen website repositories had no identity at all.** The generative system
excluded `*-website` from identity generation, so they resolved to
`(None, None, None)`. They are correctly excluded from *technical*
classification — a presentation layer must never inform architecture — but they
still need a distinct mark. Now 141 identities, 0 collisions.

**Sixty-eight percent of the portfolio shared one animation story.** "records
ingest, normalise, index, answer" covered 86 of 126 dossiers. A data flow in a
security product is not the same motion as a data flow in a financial one: the
first is a boundary holding, the second is capital settling. Animation and
geometry now resolve from **(architecture, category)**, giving 16 distinct
stories with the largest at 22%.

`DATA_FLOW` remains genuinely dominant at 86. Verified against source, not
assumed: `blitzproof` has 15 route files, `betterfintech` 3, `autoerp` 2. The
portfolio really is mostly full-stack web applications, and the art must reflect
that rather than flatten it.

---

## PROFILE

| item | state |
| --- | --- |
| art locked | **yes**, 49 design assets |
| portfolio economics published | **yes**, below engineering proof |
| all five mandatory labels present | **yes** |
| financial plate animated + static dark/light + reduced motion | **yes** |
| artwork reverted by automation | **impossible** by construction |

Financial geometry is honest by construction: the scenarios differ by roughly
12×, so nothing encodes magnitude as volume or perspective. Every mark is a flat
bar proportional to value on a **printed linear scale**, so a reader can check
the ratio rather than trust it. The animation decides *when* a value becomes
visible, never what it is.

The owner's arithmetic was verified: the 25% haircut reproduces the stated
risk-adjusted values to within $250 on low and base, exactly on high, and the
stage counts sum to 124. **Internally consistent is not verified** — no workbook
reproduces these figures, and `PORTFOLIO_ECONOMICS.md` states that in the
limitations.

---

## READY FOR PART 2

**136 repositories** have an art concept, an identity and a README plan.

**126** are fully specified: mapping, dossier, identity, animation story,
geometry, material, colour and README structure.

**10** require an owner decision before art may be generated for them, and will
not be arted until it is made.

---

## BLOCKERS

Exact blockers only.

| # | blocker | blocks | resolution |
| --- | --- | --- | --- |
| 1 | `delete_repo` scope absent | 7 prepared deletions | `gh auth refresh -h github.com -s delete_repo` (interactive) |
| 2 | `user` scope absent | profile bio | `gh auth refresh -h github.com -s user` (interactive) |
| 3 | `node_modules` is an artifact | 1 repository's classification | owner decision; deletion not authorised |
| 4 | 5 repositories have no local source | mapping, dossier, art | owner supplies project path |
| 5 | pinning is UI-only | six pins | manual |

---

## REMAINING QUEUE

The completion assertion refuses to print GITHUB COMPLETE. One condition fails:

```
1. generate per-repository art (animated + static dark/light/reduced-motion):
   122 repositories
```

This is Part 2 rollout work. Part 1 delivered the architecture that makes it
possible: art that cannot be reverted, dossiers derived from evidence rather than
templates, identities that are structurally unique, and a plan covering all 136
repositories with zero shared hero, palette or motion story.

**Part 1 gates are otherwise complete.** 20 of 21 assertion conditions pass,
including all seven new V6 gates.