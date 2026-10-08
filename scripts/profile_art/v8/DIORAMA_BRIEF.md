# Master Brief — Diorama Plates (profile only)

The ten reference images are the single source of truth for this pass. Nothing
is invented that is not in them. The earlier street/city plates and the clay.py
adobe system are superseded for the profile; the 136 per-repository surfaces in
clay_renderers.py are untouched and stay as they are.

---

## 1. What these photos are

Each photo is a **device-in-the-wild diorama**: one piece of technology standing
at hero scale inside a red-rock canyon, and the canyon doing all the set-dressing
work around it. No streets, no apartments, no shopfronts, no people, no lab
equipment. The technology is always the guest and the land is always the host.

The ten photos, in order:

| # | Device hero | Setting | Light |
| --- | --- | --- | --- |
| 1 | laptop, screen shows a mesa lake at sunset | red butte, waterfall, river | day, warm |
| 2 | satellite dish on a mesa platform | pine forest, mesa steps | day |
| 3 | floor-standing server rack | cliff face, waterfall, river | day |
| 4 | tilted solar panel on a mount | cactus flat at sunset | golden hour |
| 5 | rocket on a gantry, engines lit | red rock wall, lit base buildings | dusk |
| 6 | smartphone, screen shows mesa + `9:41` | river bend at golden hour | golden hour |
| 7 | quadcopter drone, camera down | canyon river, pine forest | day |
| 8 | observatory dome, slit open, glowing | red cliff under the milky way | night |
| 9 | desktop monitor + keyboard + mouse, screen shows canyon | flower meadow, cactus | day |
| 10 | satellite + ground dish by a lake, lit building | pines, lake, dusk building | dusk |

## 2. The visual grammar, exactly as the photos show it

### Sky
Day plates: flat vivid blue (`#2e7bd6` at zenith) warming toward the horizon,
one or two cream block clouds (`#f6e7ce`, three blobs + a base bar). No dusk
gradient except plates 4–6 and 10, which run golden-hour. Plate 8 alone is
night: deep blue `#0b1c3f` with a visible milky-way band and a white moon disc.

### Red rock
Saturated sandstone `#d65a3c`, shading to `#a8402a`, with **strata**: 4–7
horizontal bands alternating `#e88a5c` / `#c74f33` that step the mass like
geology, never like architecture. Edges are crisp chamfers, not rounded clay
blobs. Masses are tall backdrops, never foreground boxes. The floor is packed
sand `#e8c88a` with scattered single-block rocks, never paver seams.

### Green
Coniferous tiers in bright two-tone green: light tier `#6faf4a` over dark tier
`2e6b2a`, five to seven stacked tiers on a brown trunk. Cactus in `#4f9138` with
lighter cap tips. Agave and scrub in muted sage. Trees sit at the foot of the
cliff walls and along the water, medium depth, never foreground.

### Water
Vivid blue `#2aa3d8`, never turquoise. Rivers run horizontal silver-white foam
streaks; waterfalls are two vertical white bars with a foam pool at the base;
lakes carry one or two long highlight bars. Banks get one block of wet sand.

### Blooms
Small five-petal flowers in red `#e84a5f`, pink `#f2768c`, orange `#f5a623`,
each a flat rosette of five circles round a yellow centre, plus single grass
blades. They live in the lower foreground and at the foot of devices. Never a
field, always scattered punctuation.

### Devices
Big, central, blocky, matte. Bodies in cream `#f2e8d8` or adobe `#e2725b` with
square vents, square lamps, chunky stands. **Screens show miniature landscapes**
(a mesa lake on the laptop, a mesa on the phone, a canyon on the desktop). This
is the photos' own signature and must be kept: every screen gets its own tiny
scene, never a blank gradient.

### Light
Every plate has exactly one warm source and one cool ambient: day sun `#ffd966`
high, golden-hour sun low and large, the rocket plume and the launch-pad
floodlights at dusk, dish and observatory accent lamps at night. Where the
reference has a lit base (rocket, ground station), the pad buildings glow.

## 3. What each photo says (copy rewritten from scratch per photo)

The copy is the diorama's trail label: it names what is standing in front of
the reader and why it is here. Every plate keeps title + role + one data slab
+ footer, but the *words* belong to the photo.

| Plate | Photo | Title | Role line | Data slab says |
| --- | --- | --- | --- | --- |
| hero | laptop in the rocks | `DUNG30N5 × NOAERTH` | `COMPUTE IN THE WILD` | 3 headline figures |
| terminal | desktop in the marigolds | `DUNG30N5 × NOAERTH` | `THE WORKBENCH` | the five entry points |
| architecture | server rack in the cliff | `DUNG30N5 × NOAERTH` | `MACHINES IN THE ROCK` | module roots |
| data_flow | river and waterfall | `DUNG30N5 × NOAERTH` | `DATA FLOWS DOWNHILL` | route endpoints in order |
| state_machine | observatory under stars | `DUNG30N5 × NOAERTH` | `WATCHING THE SKY` | primitives as watched bodies |
| component_map | solar panel in the cactus flat | `DUNG30N5 × NOAERTH` | `EVERY PANEL COUNTS` | declared dependencies |
| build | rocket on the pad at dusk | `DUNG30N5 × NOAERTH` | `CLEARED FOR LAUNCH` | tests, CI, launch checks |
| workflow | drone over the canyon river | `DUNG30N5 × NOAERTH` | `THE FLIGHT PATH` | ordered steps as waypoints |
| domain | satellite + ground dish by the lake | `DUNG30N5 × NOAERTH` | `THE LINK` | what this portfolio is for |
| footer | smartphone by the river | `DUNG30N5 × NOAERTH` | `IN YOUR POCKET` | wordmark only |

Vocabulary swaps follow the photo, not the codebase: routes read as
tributaries, modules as racks, tests as launch checks, steps as waypoints,
dependencies as panels, primitives as watched bodies.

## 4. Text that looks like it belongs in these photos

The photos contain no overlaid text, so the text must look native to the world:
**park trail signage**. A cream board `#f7ecd4`, fully opaque, chamfered, on
dark wood posts `#3a2a1e`, carrying dark brown `#4a3226` type in the same bold
blocky sans, wide-tracked, never below 12px. Data figures right-aligned in
burnt red `#a8402a` so the numbers scan as a column. Backing posts are drawn
behind the board so the sign stands *in* the scene. Night plate swaps the board
to deep plank brown with cream type.

Nothing ever floats as bare text over sky, sand or machine; check_legibility.py
already enforces containment plus contrast (4.5:1 body, 3:1 display ≥22px) and
keeps enforcing it here.

## 5. Motion, unchanged

Closed seamless loops on coprime periods (7, 9, 11, 13, 17, 19, 23) exactly as
before. The photo-appropriate moves: water shimmer is a travelling highlight on
a loop, the flame/trace flickers, clouds drift, the drone bobs, the dish and
the satellite drift a degree or two, rotor discs spin. Static-frame fidelity
holds: the reduced variant draws every element.

## 6. What is not touched

- `clay_renderers.py` and the 136 per-repository surfaces. Profile only.
- `assets/profile/**`, owned by generate.py and art-locked.
- Copy truth: figures remain the measured portfolio totals. Only the words
  around them are rewritten to match the photos.
