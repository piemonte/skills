---
name: apotheneum-pattern
description: Use when creating Java LED patterns for the Apotheneum installation — ApotheneumPattern/ApotheneumRasterPattern, cube/cylinder geometry, doors, copy/mirror utilities, layers, MIDI, optional audio, macro-knob control, and the Chromatik package build/run flow.
---

# Apotheneum Pattern Development

This reference covers writing Java LED patterns for **Apotheneum**, a visual/sonic/haptic installation built on the [Chromatik](https://chromatik.co/) (LX Studio) Digital Lighting Workstation.

Apotheneum is a Chromatik **package** (an LXPackage), not a standalone app: patterns compile into a JAR that Chromatik loads from `~/Chromatik/Packages`. The installation is two nested chambers — a **cube** (4 faces, 50×45 each) enclosing a **cylinder** (120 columns × 43) — each with **exterior and interior** surfaces, 13,280 LED nodes total.

New patterns go in package `apotheneum.piemonte` with `@LXCategory("Apotheneum/piemonte")`.

- Geometry deep-dive: [`references/geometry.md`](references/geometry.md)
- Geometry complements (cube↔cylinder, interior/exterior techniques): [`references/geometry-complements.md`](references/geometry-complements.md)
- Build, install, and run Chromatik: [`references/build-and-run.md`](references/build-and-run.md)
- Chromatik concepts (views, compositing, modulation, palette, audio): [`references/chromatik-guide.md`](references/chromatik-guide.md)

## Class Hierarchy

```
LXPattern (LX framework)
└── ApotheneumPattern              geometry-aware base; guards on Apotheneum.exists
    └── ApotheneumRasterPattern    2D Graphics2D / BufferedImage → cube faces
LXEffect (LX framework)
└── ApotheneumEffect               effects/filters over existing colors
```

| Extend… | When |
|---|---|
| `ApotheneumPattern` | Most patterns — cube/cylinder geometry, copy/mirror utilities, model-safety |
| `ApotheneumRasterPattern` | 2D drawing with `Graphics2D`, mapped to faces with per-face toggles |
| `ApotheneumEffect` | Filters/masks applied over whatever colors already exist (`render(deltaMs, enabledAmount)`) |
| `LXPattern` (direct) | General 3D or specialized patterns that don't need Apotheneum utilities |

**Almost all new patterns extend `ApotheneumPattern`** (or `ApotheneumRasterPattern` for 2D graphics).

## Full Annotated Example

```java
package apotheneum.piemonte;

import apotheneum.Apotheneum;
import apotheneum.ApotheneumPattern;
import heronarts.lx.LX;
import heronarts.lx.LXCategory;
import heronarts.lx.color.LXColor;
import heronarts.lx.model.LXPoint;
import heronarts.lx.parameter.CompoundParameter;

@LXCategory("Apotheneum/piemonte")
public class MyPattern extends ApotheneumPattern {

  public final CompoundParameter speed =
    new CompoundParameter("Speed", 1, 0.1, 5)
    .setDescription("Animation speed");

  private double phase = 0;

  public MyPattern(LX lx) {
    super(lx);                          // calls Apotheneum.initialize(lx)
    addParameter("speed", this.speed);  // every parameter must be registered
  }

  @Override
  protected void render(double deltaMs) {   // only called when Apotheneum.exists
    setColors(LXColor.BLACK);               // start from black each frame
    this.phase += deltaMs * 0.001 * this.speed.getValue();

    for (Apotheneum.Cylinder.Ring ring : Apotheneum.cylinder.exterior.rings) {
      for (LXPoint p : ring.points) {
        double b = 50 + 50 * Math.sin(this.phase + p.yn * Math.PI * 2);
        colors[p.index] = LXColor.gray(b);
      }
    }
    copyExterior();   // mirror exterior → interior (cube + cylinder)
  }
}
```

Key points: extend `ApotheneumPattern`, register every parameter in the constructor, implement `render(double deltaMs)` (the base class only calls it when `Apotheneum.exists`, otherwise it blacks out), write into `colors[p.index]`, and use the copy utilities for symmetry.

## Geometry (summary)

Full detail in [`references/geometry.md`](references/geometry.md). The essentials:

- `Apotheneum.cube` and `Apotheneum.cylinder`; each has `.exterior` and `.interior` orientations (interior may be null — check `Apotheneum.hasInterior`).
- **Cube:** `cube.exterior.faces[]` = `{front, right, back, left}` (clockwise from above); each `Face` has `columns[]` (50) and `rows[]` (45). The orientation also exposes a combined `columns[]` (200) and `rings[]` (`Cube.Ring.LENGTH = 200`).
- **Cylinder:** `cylinder.exterior.columns[]` (120, `Cylinder.Ring.LENGTH = 120`) and `rings[]`; height `CYLINDER_HEIGHT = 43`.
- Access points: `orientation.point(x, y)` == `orientation.column(x).points[y]`. **Y = 0 is the top** of a column.
- Normalized coordinates on every `LXPoint`: `p.xn`, `p.yn`, `p.zn` in 0..1 (subtract 0.5 to center).
- **Doors** shorten some columns. Use `orientation.available(columnIndex)` for the real number of lit points in a column — never assume full height. Cube doors are at local columns 20–29; cylinder doors repeat every 30 columns at offset 10–19.
- `Column`/`Row`/`Ring` share `Apotheneum.Sequence` (each exposes `.index`). Newer builds add infinite-canvas wrapping — `next()`/`previous()` on sequences and `.column(i, true)`/`.ring(i, true)` on Orientation/Face (verify availability in your checkout). See [`references/geometry.md`](references/geometry.md).

## Views & Surface Targeting

Chromatik **Views** scope a channel or device to a subset of the model — this is how artists put content on specific surfaces (interior/exterior, cube/cylinder, a single face). The example Apotheneum project ships views for the common subdivisions. Views are chosen in the UI (channel default, or the per-device View selector); selector syntax matches fixture tags (e.g. `cube exterior`, `interior , cylinder`).

**Important nuance:** patterns that use the global `Apotheneum.cube` / `Apotheneum.cylinder` helpers and write to absolute `colors[p.index]` indices render to those surfaces **regardless of the channel view** — they are *not* auto-scoped by it. So:
- Scope surfaces **in code**: pick `exterior` vs `interior`, choose which faces/orientations to write, use the `ApotheneumRasterPattern` per-face toggles, or `copyExterior()` / `copyCubeFace()`.
- Reserve Views for `model.points`-style patterns and for show routing.

Selector syntax + details: [`references/chromatik-guide.md`](references/chromatik-guide.md).

## Copy & Mirror Utilities (on `ApotheneumPattern`)

| Method | Effect |
|---|---|
| `copyExterior()` | Copy exterior → interior for **both** cube and cylinder |
| `copyCubeExterior()` / `copyCylinderExterior()` | One component only |
| `copyCubeFace(Face from)` | Copy one face to all 8 faces (4 exterior + 4 interior) |
| `copyMirror(Face from, Face to)` | Mirror copy (reverses column order) |
| `setApotheneumColor(int color)` | Fill the entire installation with one color |
| `copy(Orientation from, Orientation to)`, `copy(Face from, Face to)` | Bulk color-range copy (fast `System.arraycopy`) |
| `setColor(...)` overloads | Fill a component/orientation/face/column with a color |

Typical pattern: render one face or the exterior surfaces, then `copyCubeFace(...)` / `copyExterior()` to propagate. This is both DRY and fast (array copies, not per-point loops).

## Geometry Complements (use the nested chambers)

The cylinder sits **concentrically inside** the cube (shared center, cylinder radius ~180" vs cube half-side ~245", roughly bottom-aligned, 4 cardinally-aligned doors). Patterns that exploit this relationship feel native to the sculpture. A few signature moves — full catalog + verified facts + code in [`references/geometry-complements.md`](references/geometry-complements.md):

- **Cube glow complements the cylinder** — measure the cylinder (mean brightness / fill / dominant hue) in one pass, then wash the cube exterior with a complementary tone modulated by it, so the outer chamber responds to the inner one.
- **Continuous vertical journey** — stack heights so a wave crosses cube→cylinder as one axis (`mcslee/Wormhole`).
- **Concentric radial expansion** — a true 3D ring from the shared axis (world coords) lights the cylinder, then the cube.
- **Interior/exterior counterpoint** — render the two surfaces with *complementary* schemes (cool out / warm in); do **not** `copyExterior()` when they should differ (`piemonte/ComeUp`).
- **Cardinal door portals** — emanate from / connect the 4 aligned doors (`mcslee/DoorEmanation`, `Portals`).
- **Angular correspondence** — sweep around cube (200) and cylinder (120) in lockstep by normalized angle, not raw index (origins differ).
- **Radial/mirror symmetry** — fold a source kaleidoscopically with `copyMirror` / segment copies (`mcslee/Symmetry`).
- **Depth layering** — cylinder as foreground against a cube wash reads as depth, especially with channel composite mode.

Vertical caveat: **Y=0 is the top** and the cylinder top is ~2 nodes below the cube top — align cross-structure vertical effects by the bottom (or world `p.y`), not row index 0.

## Raster Patterns (`ApotheneumRasterPattern`)

For 2D graphics, extend `ApotheneumRasterPattern` and draw on a `Graphics2D`. The canvas is `RASTER_WIDTH × RASTER_HEIGHT` = `50 × 45` (one cube face). The framework maps the raster onto whichever faces are enabled by the per-face `BooleanParameter`s (`exteriorFront`…`interiorLeft`).

```java
package apotheneum.piemonte;

import apotheneum.ApotheneumRasterPattern;
import heronarts.lx.LX;
import heronarts.lx.LXCategory;
import java.awt.Color;
import java.awt.Graphics2D;

@LXCategory("Apotheneum/piemonte")
public class MyRaster extends ApotheneumRasterPattern {

  public MyRaster(LX lx) { super(lx); }

  @Override
  protected void render(double deltaMs, Graphics2D g) {
    clear();                       // clear the 50×45 canvas to black (or clear(Color))
    g.setColor(Color.RED);
    g.fillOval(10, 10, 20, 20);    // drawn to every enabled face
  }
}
```

Use `buildFaceControls(ui, uiDevice, size)` to add the standard face-selector UI (a grid of exterior/interior face toggles).

## Color

Write 32-bit ARGB ints into `colors[p.index]`:

| Call | Meaning |
|---|---|
| `LXColor.gray(double v)` | Grayscale, `v` in 0..100 |
| `LXColor.grayn(double v)` | Grayscale, `v` in 0..1 |
| `LXColor.rgb(int r, int g, int b)` | RGB, each 0..255 |
| `LXColor.hsb(float h, float s, float b)` | HSB |
| `LXColor.lightest(int a, int b)` | Additive-max blend (use when overlapping shapes shouldn't darken) |

- `setColors(LXColor.BLACK)` clears all points; `addColor(p.index, c)` adds (useful in layers).
- Palette-aware color: the project **Color Palette** holds swatches of up to 5 colors; the **Active Swatch** is what devices draw from (configurable start index + number of stops, with RGB/HSV blend modes for gradients). Prefer a palette-linked color parameter over hardcoded hues so patterns follow the show's color story. See [`references/chromatik-guide.md`](references/chromatik-guide.md).

## Parameters & UI

Declare parameters as `public final` fields and **register each one** in the constructor with `addParameter("key", param)` (key is the lowercase field name). Types seen across the codebase:

`CompoundParameter`, `BooleanParameter`, `TriggerParameter`, `EnumParameter<T>`, `DiscreteParameter`, `CompoundDiscreteParameter`, `ObjectParameter<T>`, `FunctionalParameter`.

```java
public final CompoundParameter size =
  new CompoundParameter("Size", 1, 0.1, 10)
  .setUnits(CompoundParameter.Units.INTEGER)
  .setDescription("Element size");

public final BooleanParameter cylinder =
  new BooleanParameter("Cylinder", true).setDescription("Render to cylinder");
```

Set good defaults, ranges, units, and `.setDescription(...)` — see the control philosophy below for why this matters.

For a custom device UI, `implements UIDeviceControls<MyPattern>` and override `buildDeviceControls(UI ui, UIDevice uiDevice, MyPattern pattern)`, using helpers like `newKnob(param)`, `newButton(param)`, `newIntegerBox(param)`, `addColumn(container, title, ...children)`, `addVerticalBreak(ui, uiDevice)`. **Max 3 controls per UI column** (project convention — keeps the device panel readable).

### Parameter ordering & a personal base class

`addParameter(...)` **call order is the de facto ordering** — it determines where controls appear in the device UI and on MIDI/remote surfaces (there is no `setRemoteControls` in this codebase). So a consistent leading order makes your whole body of work feel predictable to operate.

Recommended canonical lead: **`color`, `speed`, `size`, then pattern-specific**. The cleanest way to enforce it is a small **intermediate base class** that registers those three first; concrete patterns extend it and add the rest after `super(...)`. `mcslee/Bursts` is the in-repo precedent (abstract base → `CubeBursts`/`CylinderBursts`); `piemonte/ParameterPattern` is the example for this convention (`ApotheneumPattern → ParameterPattern → your pattern`).

Why **per-author / self-contained**, not one shared global base: on a compressed timeline it's safest for each person to roll their own — then last-minute changes are self-contained and don't ripple across other artists' content. (Sync conventions later in a "where did you put what parameter" pass.)

```java
public abstract class ParameterPattern extends ApotheneumPattern {
  public final LinkedColorParameter color =
    new LinkedColorParameter("Color").setDescription("Primary color (follows the palette)");
  public final CompoundParameter speed;
  public final CompoundParameter size;

  protected ParameterPattern(LX lx) { this(lx, 0.4, -1, 1, 0.5, 0, 1); }

  // CompoundParameter ranges are immutable after construction, so pass them in.
  protected ParameterPattern(LX lx,
      double speedDef, double speedMin, double speedMax,
      double sizeDef, double sizeMin, double sizeMax) {
    super(lx);
    this.speed = new CompoundParameter("Speed", speedDef, speedMin, speedMax).setDescription("Animation speed");
    if (speedMin < 0) this.speed.setPolarity(CompoundParameter.Polarity.BIPOLAR);
    this.size = new CompoundParameter("Size", sizeDef, sizeMin, sizeMax).setDescription("Element size");
    addParameter("color", this.color);   // canonical order: color, speed, size
    addParameter("speed", this.speed);
    addParameter("size", this.size);
    this.color.setMode(LinkedColorParameter.Mode.PALETTE); // see gotcha below
  }
}
```

Two gotchas this base encapsulates so subclasses can't trip on them:
- **`LinkedColorParameter.setMode(PALETTE)` must be called AFTER `addParameter`** — in a field initializer the parameter has no parent/LX yet and `setMode` throws an NPE (crashes the pattern when added in Chromatik). Centralizing it here fixes it once.
- **`CompoundParameter` ranges are fixed at construction** (no `setRange`), so per-pattern speed/size ranges flow through the base constructor.

The base also exposes small convenience getters — `getColor()` (resolved palette color), `getSpeed()`, `getSize()` — so subclass render code reads cleanly. To customize an inherited param's curve or units, call the chainable setters directly on the field in your constructor (lx 1.2.1 has `setExponent`/`setUnits` but **no** `setRange`/`setLabel`), e.g. `this.speed.setExponent(2)` or `this.size.setUnits(LXParameter.Units.INTEGER)`.

Multi-color patterns (e.g. two tides, interior/exterior schemes) use the inherited `color` as their **primary** slot and register extra `LinkedColorParameter`s *after* the canonical triple (each still needs its own `setMode` after `addParameter`).

## Layers (particle / entity systems)

For independent moving entities, use `LXLayer` inner classes. The host adds layers and composites in `afterLayers`:

```java
private class Particle extends LXLayer {
  private double life = 2000;  // ms
  Particle(LX lx) { super(lx); }

  @Override
  public void run(double deltaMs) {
    this.life -= deltaMs;
    if (this.life < 0) { remove(); return; }   // self-destruct when done
    // update position, then write additively, e.g. addColor(p.index, c)
  }
}

@Override
protected void render(double deltaMs) {
  setColors(LXColor.BLACK);
  if (/* spawn condition */ true) {
    addLayer(new Particle(this.lx));
  }
}

@Override
protected void afterLayers(double deltaMs) {
  copyExterior();   // composite once, after all layers have run
}
```

`Raindrops`, `Gravity`, `Wormhole`, and `CubeBlinks` are good in-repo references for this pattern.

## MIDI

To respond to MIDI notes, `implements ApotheneumPattern.Midi` and override `noteOnReceived`:

```java
public class MyTrig extends ApotheneumPattern implements ApotheneumPattern.Midi {
  @Override
  public void noteOnReceived(heronarts.lx.midi.MidiNoteOn midiNote) {
    // trigger a one-shot effect
  }

  @Override
  protected void render(double deltaMs) { /* ... */ }
}
```

## Time, Modulators & Performance

- Convert frame time to seconds with `deltaMs * 0.001`. Accumulate phase manually (`phase += deltaMs * 0.001 * speed`) so a bipolar speed control can reverse direction.
- Use LX modulators for periodic motion: `SawLFO`, `SinLFO`, etc. Start them in the constructor with `startModulator(modulator)`. A modulator's period can be driven by a parameter via `FunctionalParameter.create(() -> ...)`.
- Global wall-clock time is `lx.engine.nowMillis`.
- Precompute sin/cos lookup tables for hot inner loops.

**Performance & threading (from the project CLAUDE.md):**
- LX renders patterns on a single thread — **never use `synchronized`**; it only adds overhead.
- Don't allocate collections inside `render()` (it runs at 60+ FPS) — reuse/`clear()` pre-allocated structures or primitive arrays.
- No manual "is enabled" checks — the framework only calls `render()` on the active pattern.

**Optimization playbook** — deep techniques from the upstream `*Optimized` variants (compute one
reference face and blit ×4, partial caching, hoisting frame-invariants into pixel-function args,
`removeIf` compaction, object pools, primitive index arrays, spatial hashing, exact-math trig
elimination, phase-wrap hygiene): [`references/performance.md`](references/performance.md).
Key lifecycle gotchas that cause real bugs:
- **`LXPattern.enabled` is compositing eligibility, not "am I rendering"** — track activation via
  `onActive()`/`onInactive()` and drop MIDI/trigger input while inactive.
- Rebuild model-derived caches in `onModelChanged(LXModel)`; size them off `model.points.length`
  (the `colors` array does not exist at construction time).
- `LXColor.hsb()` does not clamp — negative brightness wraps into corrupted bright colors.

## Audio (optional, per-pattern)

Apotheneum patterns are **not** audio-reactive in code by default; audio is normally wired at the project level as modulation (see the next section). Add code-level audio only when a pattern genuinely needs sample-accurate reaction.

Chromatik exposes audio as modulation sources: a **Graphic Meter** with **16 frequency bands**, a **Decibel Meter** (overall level), and a **Beat Detect** modulator (Trigger / Average / a decaying Beat ramp, with Min/Max freq). Map any of these to parameters via ⌘M.

In code:
- Spectrum/level: `lx.engine.audio.meter` is a `GraphicMeter` (16 bands) — read per-band energy (e.g. `getBandf(i)`), overall level, and normalized values.
- Tempo/beats: `lx.engine.tempo` exposes BPM, beat basis, and beat events.

Verify exact method signatures against the `lx` jar (it's a provided dependency, not in this repo) — see [`references/build-and-run.md`](references/build-and-run.md).

## Live Control & VJing — Macro Knobs + Modulation Mapping

Apotheneum deliberately has **no TE-style "common controls" framework baked into patterns**. The recommended way to get a consistent set of "common parameters" across many patterns is at the **project level**, not in code:

> Use a **Macro Knobs modulator** to create the set of "common parameters," then use **modulation mapping** to map those macro parameters to the appropriate parameters of the patterns/effects in the project. For live VJing/busking, set up a simple controller bound to those macro knobs — they'll always roughly do what you expect, without requiring complex coordination across pattern implementations to conform to precise conventions.

What this means for how you author patterns:

- **Expose clean, well-named, sensibly-ranged `LXParameter`s** (good defaults, min/max, units, `.setDescription`). A parameter's *mappability* matters more than naming it to match a global convention.
- **Don't** invent a fixed cross-pattern control vocabulary in Java, and **don't** add a shared base class to enforce one — modulation mapping handles cross-pattern control externally.
- Audio reactivity is wired the same way by default: an audio modulator → macro/parameter via modulation mapping; reach for code-level audio only when needed.

Worked example: add a **Macro Knobs** modulator in the project → map one macro knob to several patterns' Speed/Size/Brightness-type params via modulation mapping → bind a MIDI controller to the macro knobs.

**Mapping workflow:** press **⌘M** (Parameter Map) — eligible sources highlight green, destinations blue; click source then target. ⌘-drag a target knob/slider to set modulation depth; choose Unipolar or Bipolar polarity. Audio meters and Beat Detect map the same way.

**Compositing:** a channel can run in **Composite mode**, where patterns blend top-to-bottom like a mini-mixer (per-pattern Composite Level + Composite Blend). When authoring a foreground/overlay pattern, leave unlit pixels `LXColor.BLACK` so layers beneath show through. See [`references/chromatik-guide.md`](references/chromatik-guide.md).

## Build & Run (summary)

Full detail in [`references/build-and-run.md`](references/build-and-run.md).

- Build + install: `mvn -Pinstall install` (or `./update.command`). This copies the JAR to `~/Chromatik/Packages`, where Chromatik auto-loads it. Use `mvn compile` for a quick compile check.
- Logs: `~/Chromatik/Logs`. Always log with `LX.log(...)` / `LX.error(...)` — `System.out.println` does **not** appear in Chromatik logs.
- Running Chromatik standalone (dev) needs the EULA accepted and (on macOS) `-XstartOnFirstThread`; network output to hardware is license-gated.

## Conventions & New-Pattern Checklist

Conventions:
- Package `apotheneum.piemonte`; `@LXCategory("Apotheneum/piemonte")`.
- Copyright header optional (the `mcslee` patterns carry the LX license header).
- camelCase parameter fields; the `addParameter` key equals the field name.
- ≤ 3 controls per UI column.
- **Fork, don't mutate**: when reworking or optimizing an existing pattern others may have in
  saved shows, create a new class (`FooOptimized`, `FooReborn`) and state in its Javadoc exactly
  what changed vs the original — never alter the original's behavior in place.
- **`addParameter` keys are serialization identity**: project files reference them, so keep keys
  stable across refactors even if the display label changes (register the old key with a new
  label rather than renaming the key).
- Wrap accumulated phases at their exact period (`phase %= TWO_PI`) so shows running for hours
  neither drift in float precision nor jump on wrap.

Checklist for a new pattern:
1. Create the file in `src/main/java/apotheneum/piemonte/`.
2. Add `@LXCategory("Apotheneum/piemonte")`.
3. Extend `ApotheneumPattern` (or `ApotheneumRasterPattern` for 2D).
4. Declare parameters and `addParameter(...)` each, with ranges/units/descriptions.
5. Override `render(double deltaMs)` (or `render(double deltaMs, Graphics2D g)`).
6. Write colors into `colors[p.index]`; respect `available(col)` near doors.
7. Use `copyExterior()` / `copyCubeFace(...)` for symmetry instead of re-rendering.
8. `mvn -Pinstall install`, then confirm it loads in Chromatik (`~/Chromatik/Logs`).

See `docs/PATTERNS_ROADMAP.md` for the backlog of planned patterns.
