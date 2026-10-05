# GITHUB V5 DESIGN SYSTEM

**DUNG30N5 × NOAERTH** — hyperreal computational design, applied across the public GitHub.

This document describes the system, not the intent. Every value below is
declared once in `scripts/github_art/tokens.py` and reaches the artwork through
that file; `validators.py` fails generation if a colour appears in an SVG that
the token module does not declare.

---

## 1. The primary rule

**The interface remains an interface first.**

Readability, credibility, information hierarchy, navigation, accessibility,
performance, and technical accuracy are never traded for spectacle. What the
system adds on top of that is depth, luminosity, recursion, and geometric
intelligence — and a viewer should read it in that order: *this is an
exceptionally well-designed technical GitHub*, then *I have not seen a GitHub
profile quite like this*.

Never: a psychedelic profile. Never a gaming profile, a badge wall, a template,
or a cyberpunk wallpaper.

### Public vocabulary

The finished artefact is described with: **hyperreal computational design**,
**optical computing**, **dimensional systems**, **computational material**,
**generative system geometry**.

The internal design process uses language that never ships. It is listed in
`tokens.FORBIDDEN_PUBLIC_VOCABULARY` and `validators.check_forbidden_vocabulary`
fails any generated asset or document that contains one.

---

## 2. Identity

| Rank | Token | Where it appears |
| --- | --- | --- |
| 1 | `DUNG30N5` | Largest element on every plate. The only display-scale type. |
| 2 | `NOAERTH` | Eyebrow: `NOAERTH // SYSTEMS LAB`. Studio, not person. |
| 3 | `@M4G3LL4N0` | Tertiary metadata, never a headline, never an `<h1>`. |

Enforced by `tests/test_profile_assets.py::TestIdentity`, which fails if handle
type is ever greater than or equal to wordmark type in the same asset.

Positioning line: **systems builder · hacker · creative technologist**.

Tagline: **Build systems. Prove them. Compound what works.**
Two alternates are held in `tokens.TAGLINES` and were scored, not adopted:
"Build the layer underneath…" and "Engineering you can reproduce…". The chosen
line wins because it is the only one that states a method rather than an
ambition.

---

## 3. The chosen direction, and what was rejected

Three directions were drawn and rendered before anything was chosen. All three
passed every automated check; they were judged on composition, which no
validator can do.

| | A — Optical Topology | B — Deep Computational Glass | C — Recursive System Material |
| --- | --- | --- | --- |
| Hero payload | 11.0 KB | 9.0 KB | 35.4 KB |
| Crispness | highest | lowest | good |
| Depth | low | highest | medium |
| Identity | semantically right, visually inert | weakest | strongest |
| Main risk | reads as a wireframe | drifts to rejected glassmorphism | fractal wallpaper |
| Mobile | simplest to reduce | depth is lost at 320 | survives reduction well |

### Chosen: **A, OPTICAL TOPOLOGY, RECURSIVE**

A won on the first criterion in the standard — crispness. Its hairline rules and
tick rails stayed sharp where B softened and C weighed in. It is also the
cheapest, and its primitives are semantic rather than atmospheric.

Two defects in A were real and are fixed rather than tolerated:

1. **The hero motif rendered as an empty rectangle.** Semantically correct for
   CONTROL, visually inert as an identity. It is now a recursive module set
   inside a containment frame — C's strongest idea repairing A's weakest
   surface.
2. **Depth was A's one missing quality.** It now takes B's strata, but only on
   the CONTROL layer, where a surface that governs should read as containing
   space.

### Rejected, on the record

- **B — Deep Computational Glass.** Best atmosphere, worst identity. Its
  concentric-circle motif is the most generic shape available, and identity is
  the one thing this system cannot afford to be generic about. It also drifts
  toward exactly the glassmorphism the standard refuses.
- **C — Recursive System Material.** The best single idea and the heaviest by
  3.2×. Its module is kept; its habit of filling every surface with recursion
  is not. Recursion earns its place only where the system genuinely is
  self-similar.

Rejects are importable in `github_art/directions/` so the decision stays
auditable, and are never written into a public repository.

---

## 4. Materials

A material is a recipe resolving to concrete SVG defs for one theme, not an
adjective. Geometry asks for `deep_glass` and receives the correct gradients,
specular edges, and internal structure for obsidian or pearl without knowing
which palette it is drawing into.

| Material | Layer | Why |
| --- | --- | --- |
| `optical_glass` | CONTROL | Governance. Clear dimensional surface, enclosure reads as authority. |
| `deep_glass` | EXECUTE | Execution. Contains visible internal space and its own floor. |
| `spectral_glass` | ECONOMY | Routing. Narrow refracted band, one spectrum, no rainbow wash. |
| `obsidian_compute` | GUARD | Containment. Near-black with a hard precision bevel. |
| `luminous_ceramic` | SURFACE | Human-facing output. Soft, matte, internally lit. |
| `liquid_crystal` | RESEARCH | Layered evidence. Fine structured interference. |
| `computational_material` | EXPERIMENTAL | Unresolved. Surface texture reflects state. |

Material follows meaning, not preference. A guard surface does not get the
luminous material; that would be decoration overriding semantics.

**Optical realism** comes from four things together: interior gradient, lit top
edge, shaded bottom edge, internal structure. Weight only the highlight and it
reads as plastic; weight only the shade and it reads as a hole.

---

## 5. Colour

Spectral DNA carried forward, not reinvented:

```
mint    #5EE7D0     execution, verified
indigo  #7C8CFF     economy, routing
violet  #C084FC     control, research
```

Neutrals: `obsidian #0A0E14`, `canvas_deep #070A0F`, `graphite`, `silver`,
`pearl #FCFDFE`, `off-white`. Status colours exist and are used only for status:
`warn #F0B429`, `fail #F2777A`.

**Two palettes, separately tuned.** Dark is obsidian; light is pearl. A value
that reads well on graphite turns to mud on white, so light is not an inversion.

### The mint split

The vivid spectral mint is **12.45:1 on obsidian and 3.07:1 on pearl**. So:

- `mint` → 2px rules, node fills, traces. Geometry.
- `mint_text` → any glyph. `#0B7A6E` on pearl at **5.47:1**.

`tokens.readable(theme, key)` is the only sanctioned way to ask for a colour
destined for text. A validator caught the first attempt at getting this wrong.

**Colour encodes layer, activity, relationship, focus, verification, and
status.** It never decorates. A rainbow across unrelated panels is refused by
the standard and would fail review.

---

## 6. Typography

The most stable object in the system. Everything else moves; type stays put.

```
display   -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif
mono      ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace
```

No webfonts — a profile that depends on a font request renders as Times on any
un-cached machine, and an SVG in an `<img>` cannot load one anyway. Note the
**single quotes**: this value is interpolated into a double-quoted XML
attribute, and a nested double quote produces a file that does not parse. That
shipped once during Part 1 prototyping and is now guarded.

Modular scale, `micro 9 → monolith 128`. Every size comes from
`typography.scale()`, which multiplies a scale key by a density factor. That is
what keeps a card and a hero feeling like one object.

Tracking is a four-step vocabulary: `tight`, `none`, `wide`, `label`, `shell`.

**The wordmark is never distorted.** Crispness is mandatory; `DUNG30N5` is set
clean and strong, because an illegible logo is a worse failure than a plain one.

---

## 7. Semantic geometry

Every primitive encodes a claim. That is the difference between a diagram and
decoration.

| Primitive | Layer | Reads as |
| --- | --- | --- |
| `nested_frames` | CONTROL | Something governs, from the outside in. |
| `signal_path` | EXECUTE | Directed flow, one way, with a terminus. |
| `branching` | ECONOMY | One input, several priced paths. |
| `closed_topology` | GUARD | Containment; nothing crosses the boundary. |
| `layered_evidence` | RESEARCH | Stacked strata you could peel apart. |
| `generative_field` | EXPERIMENTAL | Unresolved, self-similar, unfinished. |

Lines are never added because they look technical. A guard ring is drawn as a
continuous path rather than chords, because a guard that leaks is not a guard.

`generative_field` uses a fixed LCG rather than `random`: non-deterministic art
would make every regeneration a diff, and this repository commits its output.

---

## 8. Recursive organisation

Fractal **organisation**, not fractal decoration.

The module — a square whose three of four quadrants repeat it a quarter the
size — appears at three scales on the hero, at one scale in each project mark,
and at its smallest as the state pips on a flagship plate. Macro structure and
micro structure echo each other.

Three of four quadrants recurse so the field has a *direction*; four of four
would be wallpaper. Each level is fainter than the last, so the eye reads
structure rather than texture. Recursion is confined to a region, never behind
the type.

Clean at arm's length. Intricate under inspection. Never cluttering content.

---

## 9. Impossible depth without JavaScript

GitHub is static. Depth is translated through occlusion, layering, perspective,
nested frames, scale, edge light, density, and transparency.

There is no JavaScript. There are no `<foreignObject>` elements — the least
portable thing an SVG can contain. There is no blur under type, no bloom, no
chromatic fringe on glyphs. Depth is built from geometry and edge light, which
is what keeps it crisp instead of soft.

---

## 10. Motion

Ambient, structural, and sparse: **3–5 moving assets across the whole profile.**

- signal propagates between validated nodes (hero)
- hero material slowly refracts (one sweep, one breath)
- terminal cursor blinks (0.6 Hz)
- no parallax, no aggressive zoom, no parallax, no unbounded speed

Durations live in `tokens.MOTION`. The floor is 1 second, and
`check_motion_is_ambient` enforces it. The caret is 1.6 s — roughly an order of
magnitude below the 3 Hz flash threshold.

**Where the gate lives.** Reduced motion is honoured at the README layer with
`<source media="(prefers-reduced-motion: reduce)">`, because that is where it was
*verified* to work. GitHub's Markdown sanitizer preserves the query, including
compound `and` forms.

It does **not** reach an SVG loaded through `<img>` in Chrome. That was measured
with an isolated test SVG, and an in-SVG media query was written, measured, and
then **deleted** rather than shipped as a claim that does not hold. Every
animated asset has a static twin selected by the same gate.

---

## 11. Visual intensity

Contrast between sections is what creates the effect. Running everything at
maximum is how a profile becomes wallpaper.

| Surface | Target |
| --- | --- |
| General content | 0.25 – 0.45 |
| Cards and diagrams | 0.35 – 0.55 |
| Profile hero | 0.65 – 0.80 |
| System graphic | 0.55 – 0.70 |
| Easter egg | 0.50 – 0.70 |

Chosen direction: `0.32 / 0.44 / 0.74 / 0.62 / 0.56`.

---

## 12. Project identity grammar

Every public system gets a mark derived from the master grammar — not a
re-coloured card. Nine identical cards communicate nothing.

| System | Primitive | Material | Reads as |
| --- | --- | --- | --- |
| Portfolio OS | nested frames + queue | optical glass | Governance from the outside in |
| AgentOS | signal path | deep glass | Objective in, verified outcome out |
| GrokInstall | branching | spectral glass | The smallest useful capability |
| GrokMax | branching | spectral glass | The cheapest sufficient path |
| gh0st | closed topology | obsidian compute | Sealed by default |
| OpenCode Watchdog | closed topology | obsidian compute | Containment before cost |
| GrokBot Office | nested frames | optical glass | Workforce above the substrate |
| GrokBot Society | generative field | computational material | Persistent actors, governed |
| SEAI Mind | layered evidence | liquid crystal | Memory as inspectable strata |

Every mark is recognisable **in silhouette alone**, because a 28 px tile cannot
afford detail that only reads at 200 px.

Each identity also owns a `headline` written to fit. An earlier version sliced
the statement at a fixed width and truncated mid-word in all three prototype
directions.

Flagships are an explicit reviewed allowlist. They are the only systems that
receive flagship-level visual investment.

---

## 13. Performance budget

| Item | Budget | Chosen direction |
| --- | --- | --- |
| Profile README text | < 75 KB | ~12 KB |
| Single plate | < 48 KB | hero 38 KB, map 28 KB |
| Ordinary SVG | < 200 KB | ≤ 38 KB |
| Animation | < 2 MB | 38 KB |
| Animated profile payload | < 5 MB | ~38 KB of motion |
| Card | < 24 KB | ~10 KB |

No image bloat for microscopic visual gain. The recursive module costs bytes; it
earns them by being the thing a viewer notices.

---

## 14. Accessibility strategy

Understanding is mandatory; visual novelty is optional.

- Every generated SVG carries `<title>` and `<desc>`, enforced by the scaffold.
- All text fills are measured against the background that asset actually paints
  and clear **WCAG AA**; the current minimum across the set is 5.47:1.
- Decorative microtext may sit lower, but never carries information that exists
  nowhere else. The README repeats every measured figure as text.
- Motion is gated and every animated asset has a static twin.
- Dark and light are separately tuned, never inverted.
- No essential information is encoded only in colour. CI state is a word.
- `role="img"` plus `aria-label` on every plate.

---

## 15. Validation

`github_art/validators.py` runs during generation, not after:

`check_parses` · `check_orphan_animation` · `check_no_external_resources` ·
`check_accessible_name` · `check_opaque_canvas` · `check_text_contrast` ·
`check_no_stray_literals` · `check_forbidden_vocabulary` · `check_budget` ·
`check_motion_is_ambient`

Each exists because the corresponding failure is **silent**: an orphaned
`<animate>` parses cleanly and renders nothing; a badge that says "404 badge not
found" returns HTTP 200; an SVG with no background inherits the host page and
puts dark ink on a dark theme.

`check_no_stray_literals` is what makes "one token source" enforceable rather
than aspirational.
