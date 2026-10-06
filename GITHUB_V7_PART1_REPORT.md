# GITHUB V7 — PART 1 REPORT

**Gates: all passing.** Two conditions remain owner-blocked on permissions.

---

## 1. VERCEL EMERGENCY STOP — COMPLETE

The problem was real and measured, not suspected.

| evidence | value |
| --- | --- |
| Vercel projects with a GitHub git link | **78** (all `productionBranch=main`) |
| distinct GitHub repositories affected | 77 |
| projects updated in the 10 hours before the stop | **16** |
| `oddbotix` Production deployment | 1h old, attributed to `noaerth-labs` |

A documentation commit had produced a **production deployment**.

### Disconnect

`DELETE /v9/projects/{id}/link` on all 78.

| | before | after |
| --- | --- | --- |
| GitHub-linked projects | 78 | **0** |
| Vercel projects | 198 | **191** (intact) |
| production deployments | — | **189** (intact) |
| disconnect failures | — | **0** |

Nothing deleted. No project, domain or deployment removed. Production content
unchanged.

### Manual deployment preserved

CLI, deploy hooks and dashboard deploys never required a git link, so
intentional deployment is unaffected.

### Verified end to end

`oddbotix`: documentation-only commit pushed to `main`.

```
deployments before : 9
deployments after  : 9
```

**GIT_PUSH_NO_LONGER_TRIGGERS_VERCEL_DEPLOYMENT**

### Source of the trigger

Vercel's **server-side Git integration**, not a GitHub Action. The profile
workflows were audited and contain no `vercel` invocation — only `git push` — so
no workflow change was needed or made. No product `vercel.json` or application
config was touched, per the boundary.

---

## 2. FINANCIALS REMOVED FROM GITHUB

| removed | |
| --- | --- |
| `README.md` Portfolio economics section | 32 lines |
| `portfolio-economics-{dark,light,motion}.svg` | 3 plates |
| `PORTFOLIO_ECONOMICS.md` | methodology |
| `data/portfolio-economics-v0.2.json` | provenance record |
| `scripts/github_art/portfolio_economics.py` | generator |
| terminal economics line | replaced with the real stack inventory |
| art-lock entries and glob | retired, not orphaned |
| assertion gate | removed |
| dossier/identity fields | removed |

Four prior reports retained and marked **SUPERSEDED**. They are an accurate
record of what was published and withdrawn; erasing them would falsify history.
Each states the material is not current and must not be cited.

**Noaerth.com untouched** — outside the GitHub-only boundary.

---

## 3. PRODUCT CODE FREEZE — ACTIVE

| | |
| --- | --- |
| product repositories fingerprinted | **157** |
| product paths watched | **10,616** |
| allowed presentation paths | 455 |
| **violations** | **0** |

Hashed by content, so a modification is detected and not merely an addition.
Gates CI, and skips honestly on runners without the local portfolio.

**Verified by modifying a tracked Go file:**
```
grokinstall: product path MODIFIED cmd/grokinstall/main.go
PRODUCT CODE CHANGED   exit 1
```
Clean after revert.

Two defects found by testing rather than reading:

1. It matched forbidden *directory names* only, so a root-level `main.go`
   passed as clean. Coverage rose 7,407 → 10,665 once source extensions were
   forbidden wherever they sit.
2. It included `github-profile`, the control plane — so it failed on its own
   correct output. Excluded.

---

## 4. GENERIC DESCRIPTION DEFECT

Seventy-five repositories carried:

```
Startup portfolio: claimpilot-ai. package.json; CI configured.
```

| | |
| --- | --- |
| detected | 101 |
| rewritten accurately | **53** |
| described as scaffolds (honest) | **45** |
| deferred for individual reading | 3 |

### What the investigation found

The 48 rejections were investigated, not substituted. The pages of these
repositories say, in their own body text:

> This page is live so navigation and portfolio links do not 404. Expand with
> product-specific content when ready.

**105 of 158 local repositories** contain that marker.

So most of this portfolio is **launch-site scaffolding, not shipped product**.
Describing those as insurance brokerages or evaluation harnesses would be
fabrication. They are now described as what they are — which is more useful,
because a reader learns immediately there is nothing to evaluate yet.

Census recorded in `.github-art/placeholder-census.json` with both lists, so
scaffold-versus-product is auditable rather than a one-time judgement.

### Rejection tests applied

- could this belong to twenty other repositories? reject
- does source support the claim? reject
- is it implementation trivia? rewrite

Framework boilerplate (`Open http://localhost:3000`) and leaked placeholders
(`_Purpose not confidently inferable_`) are both rejected.

---

## 5. GATES

| gate | state |
| --- | --- |
| Vercel guard | **SAFE_FOR_GITHUB_ONLY_PUSH** |
| Product freeze | **0 violations** |
| Art lock | holds, 46 design assets |
| Art reproducibility | generate twice byte-identical |
| Asset tests | 31 pass |
| Safety tests | 26 pass |
| CI | **green** |

Three guard defects were found by running them, not reading them:

- the Vercel guard read its own audit trail as live state and reported 78
  phantom risks **after** they were disconnected
- the freeze guard included the control plane
- `generate.py` was still the V6 renderer and overwrote V7 art — the same
  reversion, arriving through the generator rather than automation, which the
  asset lock structurally cannot see

---

## 6. REMAINING — OWNER ACTION

| # | item | why it cannot be automated |
| --- | --- | --- |
| 1 | `gh auth refresh -h github.com -s delete_repo` | interactive browser auth; 7 prepared deletions |
| 2 | `gh auth refresh -h github.com -s user` | interactive browser auth; profile bio |
| 3 | `node_modules` classification | accidental artifact; deletion not authorised |
| 4 | 5 unmapped repositories | project paths needed |
| 5 | 3 deferred descriptions | real product copy, needs individual reading |
| 6 | pinning | UI-only |

---

## 7. PART 1 STATUS

Complete: Vercel stopped and verified · financials retired · freeze active ·
generic descriptions replaced · all gates green.

Not complete: per-repository V7 dossiers under the four-source model, and the
computer-science-first art pass. Those are the substantive remaining work.