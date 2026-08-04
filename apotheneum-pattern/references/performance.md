# Performance Techniques

Idioms distilled from the upstream `*Optimized` / `*Continuous` / `*Reborn` variants and the
`drmrrdmr` set (PR #40) — each keeps its original untouched and documents its changes in the
class Javadoc. At 13,280+ points × 60 FPS, per-pixel work dominates: these techniques are the
difference between a pattern that holds frame rate and one that doesn't.

## Compute once per surface type, then copy

The 4 cube faces (and often interior) share one u/v grid. If per-pixel math depends only on
position + global frame state, compute a single reference face into a cache and blit:

```java
Face ref = Apotheneum.cube.exterior.faces[0];
computePattern(ref);                       // expensive, once per frame
for (Face face : Apotheneum.cube.exterior.faces) {
  copyFromCache(face);                     // cheap array copy, ×4
}
```

Lazily (re)allocate the cache only on size change — never per frame:

```java
if (cache == null || cache.length != cols * rows) {
  cache = new int[cols * rows];
}
```

If exterior == interior pixel-for-pixel, skip even that: render exterior and use
`copyExterior()` / `copyCubeExterior()` / `copyCylinderExterior()`.

**Partial caching** (DustPulseWhiteout): when a final step must stay per-face (e.g. an
independent sparkle roll), cache the pre-sparkle components as separate float arrays (hue, sat,
brightness — not a packed int, avoiding an RGB round-trip) and redo only the cheap random step
per face. Use a `boolean[]` for "literal transparent 0" vs "opaque black" — `LXColor.hsb(h,s,0)`
is opaque black, not transparent.

## Hoist frame-invariants out of the pixel loop

Anything depending only on time/params is computed once in `render()` and **passed as arguments**
to the per-pixel function so it physically cannot be re-read:

- Trig of animated phases (ExMachina cached all root sin/cos per frame — "previously up to 18
  trig calls per rendered pixel")
- `param.getValuef()` reads — hoist to locals; parameter reads have overhead
- Column-only / row-only terms: precompute `dxCache[x]` and `dyCache[y]` arrays once per frame
  so the inner loop does only genuinely 2D work (BurstsOptimized)

## Skip predetermined work

- A param at zero often makes a whole computation moot: `Sat == 0` → skip hue math entirely and
  return `LXColor.gray(...)` via a `boolean whiteout` fast path
- A brightness param at 0 → `setColor(orientation, LXColor.BLACK)` and skip the surface

## No per-frame allocation

- **Object pools**: preallocate `Star[] pool` + `activeCount` cursor; compact dead entries by
  in-place swap; carry fractional spawns in an accumulator (HyperspaceOptimized, 5000 stars)
- Indexed `for` over `ArrayList` on hot paths (for-each allocates an Iterator)
- Reuse scratch collections: `list.clear()`, never `new` in `render()`
- **`removeIf` for prune-while-render**: `list.removeAll(collected)` is O(n²) and
  `Iterator.remove()` on ArrayList shifts the tail each call; `removeIf(e -> { e.render(dt);
  return e.done(); })` renders and compacts in one linear pass

## Primitive arrays instead of HashMap on point lookups

Key by `LXPoint.index` into plain arrays with `-1` sentinels — no boxing, no hashing:

```java
int[] cubeFace = new int[allPoints.length];   // -1 = not a cube LED
Arrays.fill(cubeFace, -1);
```

Rebuild these in `onModelChanged(LXModel)` — stale caches risk index-out-of-bounds on model swap.

## Spatial hash for neighbor queries

Bucket points into a grid with **cell size == query radius** so a lookup visits 3×3×3 cells,
not 7×7×7. Pack coords into a long key: `(gx << 42) | (gy << 21) | gz`. Return results in a
reused list (HyperspaceOptimized.LEDSpatialGrid).

## Cheap exact math (not approximations)

- Avoid `atan2` when only direction matters: `sinθ = y/r`, `cosθ = x/r` (guard `r < MIN_R`)
- `sin(n·θ)` for integer n via the angle-addition recurrence on `(sinθ, cosθ)` — exact, no trig
- `sin(a + b(t))`: expand via angle addition, computing `sin/cos(b)` once per frame
- `z^N` for small N by repeated complex multiply, not `pow`; compare squared magnitudes to skip
  `sqrt` in convergence/distance tests
- Range-reduce phases in O(1): `x %= TWO_PI` (+ fold into [-π, π]) — a `while (x > PI) x -= …`
  loop degrades over hours of runtime

## Phase hygiene for long shows

Wrap every accumulated phase at its **exact** period (`phase %= TWO_PI`, `t %= 1f`) so the wrap
never introduces a visual jump. If the consuming function's period depends on a parameter, don't
wrap at an arbitrary constant (it will glitch) — track unwrapped time or wrap at the true period.

## Lifecycle gotchas

- **`LXPattern.enabled` is compositing eligibility, not "am I rendering."** Track real activation
  with `onActive()`/`onInactive()` and drop MIDI/trigger input while inactive, or queued triggers
  dump all at once on reactivation
- `colors` is not allocated at construction time — size caches off `model.points.length`, and do
  it lazily or in `onModelChanged`
- `LXColor.hsb()` does **not** clamp: negative brightness wraps into corrupted bright colors —
  `LXUtils.clampf(b, 0, 100)` anything computed
