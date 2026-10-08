# Master Prompt — NOAERTH Profile Visual System

The single brief every profile image is generated from. Kept in the repository
because the generator reads its palette and its legibility rules, and because a
style that only exists in someone's head cannot be checked.

---

## 1. The one-line intent

**A chunky clay diorama where nature and retro machines share the same desert,
and the information sits on solid slabs in front of it like signage bolted to
the scene.**

The scene is the mood. The slab is the message. They must never compete.

---

## 2. Style DNA (unchanged, do not drift)

- Super-simplified 3D geometry. Toy-like, sculptural, blocky, handcrafted.
- Flat-shaded volumes: lit top, mid front, shaded side. One chamfer strip on
  the top-front edge and one on the right edge. Five planes, no gradients on
  the solids.
- Matte surfaces. Gentle highlight, no specular hotspot, no bloom.
- Bold blocky type. Geometric sans, wide tracking, sturdy — never thin,
  never elegant, never a hairline weight.
- Reduced detail. No filigree, no circuitry filigree, no fractal noise, no
  hyper-real surface. Mass and proportion carry the read.

## 3. Palette (New Mexico: adobe, desert light, sunset warmth)

| Role | Colour |
| --- | --- |
| dusk sky (deep) | `#1b2a4a` |
| dusk sky (mid) | `#2e4a6b` |
| horizon glow | `#f3b594` / `#f4c5a6` |
| adobe orange | `#e2725b` |
| terracotta | `#c1683f` |
| dusty clay red | `#a8543c` |
| sand | `#e3c08d` |
| warm beige | `#d9b98c` |
| cream | `#f6e7ce` |
| sunset peach | `#f2a07b` |
| dusty coral | `#e08467` |
| muted turquoise | `#5b9a97` |
| cactus green | `#7a9a5c` |
| sage | `#9bb07a` |
| warm yellow light | `#f5c95c` |
| deep shadow | `#8a5a44` |

Nothing outside this list is introduced. Scenery is drawn from the *cool and
muted* half; information is drawn from the *warm and light* half. That split is
the main legibility mechanism.

---

## 4. Nature vocabulary

Desert first, because it is the region's own language and it matches the clay.

- **Massing:** stepped mesa, Pueblo terraced adobe, distant ridge layers,
  canyon wall, butte.
- **Sky:** dusk gradient, low sun with a soft halo, cream clouds, night stars
  with a moon, thin horizon haze band.
- **Flora:** saguaro cactus, low-poly conifer, agave rosette, scrub boulder,
  bare branched tree.
- **Ground:** sand plane, receding paver floor with seams converging on a
  vanishing point, water pool, dry wash, scattered rocks.
- **Weather:** dust haze, drifting sand wisp, heat shimmer over the horizon.

Nature is always *behind* and *quieter*. Distant ridges use at most 20–45%
opacity. No element in the scenery may cross the information slab.

## 5. Retro technology vocabulary

Chunky machines rendered as clay blocks. The reference era is 1970s–1980s
personal computing and early spaceflight, not sleek modern hardware.

- **Terminals:** CRT with a bezel, a recessed screen, a chunky stand, a vent
  grille, two knobs. The lit screen is the warm focal point.
- **Input:** thick keyboard with square keycaps, trackball, chunky buttons,
  toggle switches, a punch-card strip.
- **Storage:** floppy disk with a shutter, tape reel, cartridge, punch tape.
- **Compute:** mainframe cabinet with vent slots, rack units, a patch panel,
  a cooling grille, an indicator lamp.
- **Output:** dot-matrix printer, paper spool, plotter drum.
- **Instruments:** oscilloscope with a trace, a dial gauge, a seven-segment
  readout, a toggle bank.
- **Spaceflight:** satellite with solar wings, an antenna dish, a launch gantry,
  a rover with a dish.
- **Signals:** a pixel grid, a scanline sweep, a blocky waveform, an antenna
  mast with a blinking lamp.
- **Robotics:** a blocky robot arm, a wheeled rover, a little box robot with an
  antenna and two eye-lights.

Retro tech is *chunkier and more tactile* than the nature forms: square keys,
square vents, square indicator lamps. It is what makes the era legible.

## 6. How the two meet

The compositions interleave, never separate:

- A **CRT monitor planted in the desert** at the same scale as a cactus.
- A **satellite dish** on the mesa roof, tracking the same sun as the scene.
- A **mainframe cabinet half-buried in sand**, vents still running.
- **Punch cards as adobe bricks** stacked into a wall.
- A **rover parked at a water pool**, antenna up, one lamp lit.
- **Cactus shaped from circuit blocks**; conifer tiers as stacked hard drives.
- A **pixel grid fading into dunes** at the horizon.
- **Oscilloscope trace** rendered as a ribbon of clay blocks across the sky.

Rule: the technology must look like it was *built by the same hands* as the
clay landscape. Same palette, same chamfer, same matte finish.

---

## 7. Information hierarchy (this is the part that must not fail)

```
LAYER 3  slab        opaque clay card, chamfered, cast shadow
LAYER 2  type        cream on slab, dark dusk on light slab
LAYER 1  furniture   the glyphs, figures and labels that carry the meaning
LAYER 0  scenery     nature + retro tech, low contrast, never over the slab
```

### Hard rules

1. **Every string sits on an opaque slab.** No text is ever placed directly on
   sky, sand or a machine. The slab fill is fully opaque (`opacity` 1.0).
2. **Minimum contrast 4.5:1** for body and label type, **3:1** for display type
   at 22px and above.
3. **Slab and type come from opposite ends of the palette.** Light slab takes
   dusk-blue type; dark slab takes cream type.
4. **The slab reserves its own quiet zone.** Scenery is composed *around* the
   slab footprint, not underneath it.
5. **One message per slab.** A slab is a sentence, not a dashboard.
6. **Numbers get their own tile** when they are the point of the plate.
7. **The figure is the hero, the chrome is not.**

### Measured slab colours

These are solved, not eyeballed. Cream ink needs a slab at or below roughly
0.14 relative luminance to clear 4.5:1, which rules out the bright adobe and
terracotta as slab fills.

| Role | Dark variant | Light variant |
| --- | --- | --- |
| title slab | `terracotta -0.28` | `cream` |
| data slab | `clay_red -0.10` | `beige` |
| figure tile | `ember -0.30` | `sand` |
| footer bar | `dusk_deep` | `cream` |
| primary type | `cream` | `dusk_deep` |
| secondary type | `cream` | `clay_red -0.44` |

**Secondary type on a dark slab is the same cream as primary.** Only pure cream
clears 4.5:1 against a slab dark enough to carry cream at all, so the second
level of hierarchy comes from size and weight, never from a dimmer colour. On
light slabs there is room for a genuinely darker second level.

The consequence is the whole point of the system: the scene stays bright, warm
and busy, and the information sits on it as **dark signage**. Slabs are never
the same colour as the thing behind them.

## 8. Ten plates, ten scenes

Each plate gets a different setting so the profile does not read as one
template ten times.

| Plate | Nature | Retro tech | Slab carries |
| --- | --- | --- | --- |
| hero | mesa settlement, sun, clouds | CRT on the terrace | identity + 3 headline figures |
| terminal | dusk, scrub, low ridge | CRT console, keyboard | entry points / measured totals |
| architecture | terraced mesa, cactus | stacked rack units | module roots |
| data_flow | dry wash, road of pavers | packets as lit blocks | route endpoints |
| state_machine | twilight, stars, moon | tokens through an arch gate | detected primitives |
| component_map | pale morning, long shadows | brick wall of drives | declared dependencies |
| build | quarry, boulders | crates + lit instrument bay | tests and CI |
| workflow | canyon steps, sun | stepped servers | ordered steps |
| domain | water pool, agave, big sky | rover by the water | the problem |
| footer | single mark on the horizon | the mark itself | wordmark |

## 9. Motion (unchanged rules)

- Every animation is a **closed loop**: first and last value equal,
  `repeatCount="indefinite"`, `calcMode="spline"` easing that settles at both
  ends. No `fill="freeze"`, no one-shot settle.
- Motion is slow and few. Things breathe, drift, bob, and blink. Nothing spins
  for attention.
- Scenery motion is slower and smaller than furniture motion, so the eye lands
  on the information.
- Reduced-motion variant contains **no** animation at all.
- Static-frame fidelity is mandatory: every element visible in the animated
  plate must be visible in the reduced plate. GitHub rasterises these as stills.

## 10. Generation and verification

Rendered by `clay3d.py` (primitives), `profile_surfaces.py` (the ten plates)
and `profile_hero.py` (the banner). Verified by:

- `validate_art.py` — XML, motion semantics, paint validity, static fidelity.
- `check_legibility.py` — every text run is inside an opaque slab, and the
  measured contrast of type against its slab meets section 7. This gate found
  the light-variant dark-on-dark bug and the clipped data row.
- `clay_guard.py` — no unresolved palette name reaches an SVG paint attribute.
- Byte-identical output across `PYTHONHASHSEED` values.