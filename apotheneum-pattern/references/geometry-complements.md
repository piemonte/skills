# Geometry Complements — leveraging Apotheneum's nested chambers

Apotheneum is not two unrelated canvases — it's a **cylinder nested concentrically inside a cube**, each with exterior and interior surfaces. Patterns that *acknowledge that relationship* read as part of the sculpture; patterns that treat each surface as a flat screen feel generic. This file catalogs the spatial relationships and a series of "complement" techniques that exploit them.

All structural facts below are verified against `src/main/resources/fixtures/Apotheneum.lxf` and `Apotheneum.java`.

## The physical nesting (verified)

| Fact | Value | Source |
|---|---|---|
| Cube side | 491" | `Apotheneum.lxf:14` |
| Cylinder radius | 180" (Ø 360") | `Apotheneum.lxf:15` |
| Shared center (X,Z) | `cubeSide*0.5` = **(245.5, 245.5)** | `Apotheneum.lxf:291-292` |
| Cube top / cylinder top | 444" / `cubeTop - 2*nodeSpacing` ≈ 425.25" | `Apotheneum.lxf:13,293` |
| Node spacing | 9.375" | `Apotheneum.lxf:11` |
| Cube height / cylinder height | 45 / 43 rows | `Apotheneum.java:39-40` |
| Cube ring length / cylinder ring length | 200 / 120 | `Apotheneum.java:271,350` |

Consequences for design:
- **Concentric.** The cylinder sits dead-center in the cube. A radial effect from the shared vertical axis reaches the cylinder wall (r≈180") *before* the cube wall (r≈245"). There's a ~65" annular gap between them.
- **Roughly bottom-aligned, tops offset.** Both nets hang from the top; the cylinder starts ~2 nodes lower. Because **Y=0 is the top of every column** (`points[0]` top, `points[len-1]` bottom), align cross-structure vertical effects by the **bottom** (or by world `p.y`), not by row index 0.
- **Cardinal doors line up.** Both structures have **4 doors at 0°/90°/180°/270°** (cube door per 50-wide face at cols 20–29; cylinder door per 30-wide quadrant at cols 10–19 — `Apotheneum.java:228-230,340-342`). Doors are natural portals between chambers.
- **Co-rotating, different origins.** Cube faces order front→right→back→left, cylinder columns advance the same rotational direction (CW from above), but **column 0 of each structure is not at the same world angle**. For precise cross-structure alignment use world coordinates or a normalized angle (with a tunable offset), not raw column indices.

## Complement techniques

### 1. Cube glow complementing the cylinder (the canonical example)
Derive the **cube's color/brightness from the cylinder's state** (or vice versa) so the outer chamber "responds" to the inner one. Pattern: compute an aggregate of the cylinder (mean brightness, dominant hue, fill level) in one pass, then wash the cube exterior with a complementary tone.

```java
// Pass 1: render the cylinder (and measure it)
double energy = 0; int n = 0;
for (Apotheneum.Column c : Apotheneum.cylinder.exterior.columns()) {
  for (LXPoint p : c.points) {
    // ... compute & write the cylinder color ...
    energy += /* brightness 0..1 */; n++;
  }
}
energy /= Math.max(1, n);

// Pass 2: cube exterior glows a complementary color, modulated by cylinder energy
int glow = LXColor.hsb(complementHue, 60, (float)(20 + 60 * energy));
setColor(Apotheneum.cube.exterior, glow);   // fast fill helper
copyCubeExterior();                          // mirror to interior if desired
```
Variations: complementary hue (palette color + 180°), brightness "breathing" with cylinder fill, or a slow cube ambient that lags the cylinder for an afterglow feel.

### 2. Continuous vertical journey (cube → cylinder)
Treat the two structures as one tall axis so a wave travels seamlessly across both. `Wormhole` does this with `JOURNEY = GRID_HEIGHT + CYLINDER_HEIGHT + 1` (`mcslee/Wormhole.java`): map a single position `pos = JOURNEY * basis` onto cube rings (0..44) then continue onto cylinder rings (45..87). Because tops are offset, decide whether the journey reads top-down or bottom-up and align accordingly.

### 3. Concentric radial expansion from the shared axis
Use **world coordinates** and the shared center to send a true 3D ring outward: it lights the cylinder first, crosses the gap, then the cube. Iterate `model.points`, compute `r = hypot(p.x - cx, p.z - cz)` (cx,cz = 245.5 with defaults; better: read model bounds center), and light points where `|r - waveRadius| < width`. This is the one effect that genuinely uses the nesting in 3D rather than per-surface.

### 4. Cardinal door portals
The 4 aligned doors are the only places the chambers "connect" visually. Emanate from them (`mcslee/DoorEmanation.java`), draw concentric rings around them (`mcslee/Portals.java`), or treat a cube door and the cylinder door at the same cardinal angle as two ends of one tunnel. Door columns are shortened — always honor `orientation.available(col)`.

### 5. Interior / exterior counterpoint
The interior cube faces *inward toward the cylinder*; the cylinder interior faces *inward toward the viewer in the sanctum*. Render exterior and interior with **complementary schemes** instead of mirroring them — e.g. cool outside, warm inside (`piemonte/ComeUp.java` runs two independently-colored tides this way). **Do not** call `copyExterior()` when you want them to differ — it overwrites interior with exterior (`ApotheneumPattern.java:64-75`).

### 6. Angular correspondence (sweep around both in lockstep)
To make a vertical "lighthouse" beam sweep around the cube and cylinder together, drive both by a normalized angle rather than index. For a target angle `a` in [0,1): cube perimeter column ≈ `a*200`, cylinder column ≈ `a*120` (plus a tunable origin offset, since column 0 differs). Use `LXUtils.wrapdistf(a, pointAngle, 1f)` for seam-free falloff (see `mcslee/CylinderRings.java`).

### 7. Radial & mirror symmetry
`mcslee/Symmetry.java` (an `ApotheneumEffect`) folds each structure independently: N-fold radial segments (cube divisors of 50: 2/4/5/10/…; cylinder divisors of 120: 2/3/4/5/6/…) and a vertical "horizon" mirror. The building block is `copyMirror(from, to)` which copies a face reversing column order (`ApotheneumPattern.java:77-87`). Use these to turn an asymmetric source into kaleidoscopic structure.

### 8. Depth layering (nested radii as fore/background)
Because the cylinder is physically inside the cube, you can stage **foreground/background by surface**: a sparse bright pattern on the cylinder against a slow wash on the cube reads as depth. Combined with channel **composite mode**, separate channels per surface let an operator cross-fade the "near" and "far" layers live.

## Reusable geometry idioms (building blocks)

These appear across the codebase and underpin the techniques above:

- **Radial / polar fields** — `x=p.xn-0.5, y=p.yn-0.5; r=hypot(x,y); θ=atan2(y,x)`; combine `sin(k*r)` + `sin(m*θ)` for blooms/interference (`thesilveresa/RadialBloom1`, `QuasicrystalForest`).
- **Seam-free ring/row sweeps** — animate around rings with `LXUtils.wrapdistf(angle, pointAngle, period)` so there's no seam at the wrap (`mcslee/CylinderRings`, `Raindrops`).
- **Per-face render-once-then-copy** — render the front face, then `copyCubeFace(front)` (all 8 faces) or `copyExterior()`; far cheaper than per-point loops and enforces symmetry (`mcslee/Abacus`, `CubeSparkles`).
- **Door-aware edge tracing** — clamp to `available(col)`, route around door tops using adjacent full columns (`doved/patterns/EdgeTracer`).
- **Organic fields via noise** — `LXUtils.noise(x,y,z)` or `heronarts.lx.utils.Noise.stb_perlin_fbm_noise3(...)` / `stb_perlin_turbulence_noise3(...)` for fluid/cloud surfaces (`mcslee/Enso`, `DNAHelix`, `piemonte/ComeUp`).
- **Lookup tables** — precompute sin/cos (and noise) in the constructor for hot loops (`thesilveresa/CrystallineLife`, `DustPulse`).
- **Distance-falloff glows** — squared 3D distance + linear/exponential falloff, blended with `LXColor.lightest(...)` so overlapping sources don't darken (`mcslee/CubeSparkles`).

See [`geometry.md`](geometry.md) for the base model API and [`chromatik-guide.md`](chromatik-guide.md) for views, compositing, palette, and audio.
