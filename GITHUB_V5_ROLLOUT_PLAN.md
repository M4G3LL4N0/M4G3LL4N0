# GITHUB V5 ROLLOUT PLAN

Nothing in this plan has been executed. Part 1 produced the design system, the
inventories, the ledger, and validated prototype assets. Every public surface is
still exactly as Part 2 left it.

Each stage below is gated on the stage before it. No stage begins until the
previous one is green on the live profile, not merely green locally.

---

## 0. Standing constraints

These hold for the whole rollout and are not up for renegotiation per stage.

1. **Verified facts are sacred; presentation is not.** Nothing in the ledger may
   disappear. `ledger -> README` is diffed at every stage.
2. **No private surface, ever.** Private repositories, deployment-site
   repositories, private architecture, local paths, and credentials stay out of
   every generated asset. Enforced by test, not by discipline.
3. **Visibility decisions remain the user's.** The Publication Council is the
   authority on what becomes public. A beautiful design is not an argument for
   publishing something.
4. **No regression of Part 2.** The ten fixed defects stay fixed. Any stage that
   would reintroduce one is rejected.
5. **Automation stays bot-attributed**; human and OpenCode engineering commits
   are authored normally.
6. **No commit without green validation**, on a branch, through a PR.

---

## Stage 0 — merge the honest-CI fix (blocking, cross-repo)

**Why first:** the live profile currently prints `yes` in the CI column for
`gh0st`, `grokinstall`, and `seai-mind`, whose most recent workflow runs
**failed**. The profile's daily sync clones `noaerth-portfolio-os` from `main`,
so until this fix lands there, any README change will be reverted on the next
scheduled run.

| | |
| --- | --- |
| Repo | `noaerth-portfolio-os` |
| Branch | `fix/githubos-honest-ci-state` |
| Commit | `4af20c8` |
| Tests | 203 passed, 8 subtests (requires Python ≥ 3.10; the default `python3` on this machine is 3.9.6 and cannot run the suite) |
| Gate | Merged to `main` **before** any profile README change is merged |

---

## Stage 1 — design system lands, nothing public changes

Publish the system and its evidence. No README edit.

| Artefact | Purpose |
| --- | --- |
| `scripts/github_art/` | tokens, materials, geometry, typography, project identity, validators, directions |
| `GITHUB_V5_DESIGN_SYSTEM.md` | the standard, the decision, and what was rejected |
| `GITHUB_V5_PUBLIC_INVENTORY.json` | classified public inventory, public-safe by construction |
| `GITHUB_V5_CONTENT_LEDGER.json` | the preservation baseline |
| `GITHUB_V5_ROLLOUT_PLAN.md` | this file |

Local-only and never committed: `GITHUB_V5_ART_GALLERY.html`, `build/`.

**Gate:** `verify-profile` green — integrity suite, artwork reproducibility,
generated-block freshness. Plus a new V5 suite: public-information audit and
ledger coverage.

---

## Stage 2 — profile README, new composition

The first public change. Narrative rebuilt from first principles rather than
reordered:

```
ACT I    IDENTITY       hero (motion, reduced-motion twin, compact twin)
ACT II   SIGNAL         build-signal plate + text table
ACT III  SYSTEMS        six flagship identities
ACT IV   ARCHITECTURE   operating stack + constellation, evidence-backed
ACT V    PROOF          strip, full matrix in <details>
ACT VI   OPEN SOURCE    contribution path
ACT VII  LABS           only what the Council has approved
ACT VIII EASTER EGG     CRT shell, retro sub-language
```

Intensity ladder per section: `0.32 → 0.74 → 0.62 → 0.44 → 0.56`. The hero is
the peak and the content is quiet, because contrast is what creates the effect.

**Gate:** all Stage 1 tests, plus live verification at 320 / 390 / 768 / desktop
in both themes, plus a reduced-motion capture, plus
`ledger(profile) -> README` showing zero loss.

---

## Stage 3 — two truthful architecture views

Currently one map conflates two different questions. They are separated:

- **A. Operating stack** — actual runtime and integration relationships. Every
  drawn edge requires an entry in `system-map-evidence.json`. Three exist.
- **B. Noaerth constellation** — semantic grouping of public projects. Grouping
  is **not** dependency, and the plate says so.

`deliberate_non_edges` in the evidence file stays: `portfolio-os → agentos` is
*disclaimed* by `README.md:144` ("Deliberately not built: its own agent runtime")
and must never be drawn as a dependency.

**Gate:** evidence symmetry check passes in both directions; a mutation test
confirms it fails when an edge is invented.

---

## Stage 4 — flagship READMEs

Six flagships, highest visual investment, in dependency order so later stages
reuse proven components: Portfolio OS → AgentOS → GrokMax → GrokInstall →
OpenCode Watchdog → gh0st.

Each receives: theme-aware hero, project glyph, architecture plate, verified
proof strip, 1280×640 social preview, one restrained animation, status, install,
contributing, security.

`ledger(<repo>) -> README` must show **zero** loss of commands, links, caveats,
or architectural claims. A dropped `go install` line is a failed gate even if
the page looks better.

**Gate per repository:** ledger diff empty, integrity suite green, live render
verified, human review of the first two before the remaining four proceed.

---

## Stage 5 — public projects

`grokbot-office`, `grokbot-society`, `seai-mind` at public-project standard:
smaller hero, glyph, clear summary, one architecture visual, proof where
available. Not flagship complexity. Hierarchy is the point.

**Gate:** same as Stage 4, minus the social-preview requirement where GitHub
propagation has been unreliable.

---

## Stage 6 — the deliberately unpolished exception

`why-are-you-here` keeps its retro-computing sub-language. It is not made to
look like a product. Enhanced only inside that sub-language: CRT phosphor, scan
lines, a slower blink. It exists because the account once had nothing public,
and tidying it would erase the reason it is there.

**Gate:** read as a joke, not as a product. A human decides this, not a test.

---

## Stage 7 — account-wide surfaces

Only after every README is proven:

- per-repository social previews (1280×640), project-specific, no badge spam
- release plates for meaningful releases only, never for trivial patch bumps
- status chips and technical dividers in the shared vocabulary
- issue forms, PR templates, `CONTRIBUTING`, `SECURITY` — **functional only**,
  sharing vocabulary and professionalism, no decorative ASCII walls

---

## Out of scope by decision

- **Renaming the account.** `DUNG30N5` is the public identity; the handle stays
  the address.
- **Publishing private repositories** because they would look good.
- **A bio or profile-status change**, both blocked by a missing `user` scope.
- **Automated avatar changes.** Upload is manual and stays that way.
- **Release artwork for every tag.**

---

## Verification method, per stage

1. Generate locally; every validator runs during generation.
2. Render through **GitHub's own Markdown endpoint** and inspect the HTML.
3. Push a branch, open a PR, let `verify-profile` run.
4. Merge only when green.
5. Fetch the **live** profile and re-verify: images resolve, no 404s, motion
   confirmed under real elapsed time, reduced-motion serves static twins,
   contrast re-measured.
6. Capture before and after at 320 / 390 / 768 / desktop, dark and light.
7. Diff the ledger.

A successful `git push` is not evidence of anything. Step 5 is the step that
counts.

---

## Risk register

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| CI honesty fix not merged, sync reverts the README | **certain** if ignored | Stage 0 is blocking |
| Recursion reads as fractal wallpaper | medium | Module confined to one region, never behind type, three of four quadrants |
| Redesign drops a command or caveat | medium | Ledger diff is a hard gate at Stages 2 and 4 |
| Motion misbehaves on GitHub | low | Verified under real elapsed time; static twins; never load-bearing |
| Payload growth across account-wide rollout | medium | Per-plate budgets enforced in `check_budget` |
| Light mode washed out | low | Separately tuned palette; AA measured per asset |
| Private detail leaks through artwork | low | Public-information audit test; inventory excludes by construction |
| Social previews do not propagate | known | README is the priority; previews never block completion |
