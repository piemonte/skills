# Chromatik Concepts for Apotheneum Pattern Authors

Distilled from the official [Chromatik Guide](https://chromatik.co/guide/) — the parts that matter when writing/operating Apotheneum patterns. Links point to the authoritative pages.

## Views — targeting surfaces ([guide](https://chromatik.co/guide/model-definition/))

Views are Chromatik's mechanism for running a device/channel against **only a subset of the model** — exactly how you put content on a specific Apotheneum surface (interior/exterior, cube/cylinder, a single face). The example Apotheneum project ships views for the common subdivisions.

- A View is selected per **channel** (default for all its patterns) or per **device** (override, via the View selector in the device's left bar).
- View **selector syntax** (CSS-esque, matches fixtures by tag):
  - `cube` — fixtures tagged `cube`
  - `cube exterior` — `exterior` descendants under `cube`
  - `cube > square` — direct children only
  - `interior , cylinder` — union; `square & polygon` — intersection
  - `strip*` — each match normalized independently; `a ; b` — both, normalized separately
  - ranges: `tag[n]`, `tag[n-m]`, `tag[n:i]`, `tag[even]`, `tag[odd]`
- **Normalization** in a view: *constrain to view bounds* (re-normalize `xn/yn/zn` to the view's 0..1) or *preserve absolute bounds* (keep whole-model coordinates). Also absolute vs view-group orientation for rotated groups.

**Apotheneum nuance:** patterns that drive geometry through the global `Apotheneum.cube` / `Apotheneum.cylinder` helpers and write to absolute `colors[p.index]` indices address those surfaces **regardless of the channel view** — they aren't auto-scoped by the view. Use views for `model.points`-style patterns and for show routing; use explicit surface selection in code (e.g. choose `exterior` vs `interior`, the `ApotheneumRasterPattern` per-face toggles, or `copyExterior()`) for Apotheneum-helper patterns.

Coordinate system: left-handed — `+X` right, `+Y` up, `+Z` away from viewer; rotations are Yaw (Y), Pitch (X), Roll (Z).

## Devices & compositing ([guide](https://chromatik.co/guide/devices/))

A **pattern** is a light instrument generating animated output; a **channel** holds a Pattern Bin + Effects. Each device's left bar has: Recall (pattern)/Enabled (effect), **View selector**, **MIDI** filter, label, **Modulation** expander, expand/collapse.

Channels run in one of two modes — this changes how your pattern coexists with others:

- **Playlist mode** (default): one **Active Pattern** at a time, with **transitions** (Transition Blend + Transition Time) and optional Auto-Cycle.
- **Composite mode**: all patterns render **simultaneously**, compositing **top → bottom** like a mini-mixer. Per-pattern: Composite Level (fader), Damping/Damping Time (fade on toggle), **Composite Blend** (blend mode), Cue (solo preview).

**Author takeaway:** in composite mode your pattern is a *layer*. Leave unlit pixels black (`LXColor.BLACK`) so layers beneath show through, and design "FG" patterns to be sparse. Effects target either a single **Pattern** or the whole **Channel**, processed left→right. Presets are `.lxd` files in `~/Chromatik/Presets/` (store params + device modulation).

## Modulation & mapping ([guide](https://chromatik.co/guide/modulation/))

How "common controls" and audio reactivity are wired **without code** (the recommended Apotheneum approach):

- **Parameter Map** workflow: press **⌘M** (or the Parameter Map button in the MODULATION tab). Eligible **sources highlight green**, eligible **destinations highlight blue** — click source, then target.
- **Depth**: ⌘-drag on a target knob/slider to set the modulation range directly (shown in the source's color).
- **Polarity**: *Unipolar* applies the full range one direction; *Bipolar* applies both directions (0.5 = center).
- Boolean/trigger targets support Direct / Invert / On→Toggle behaviors.
- Sources include **Macro Knobs** (your hand-built "common parameters"), LFOs, envelopes, and audio meters (below). Map a MIDI controller → Macro Knobs, then Macro Knobs → many pattern params.

## Audio ([guide](https://chromatik.co/guide/audio/))

Audio is exposed as **modulation sources** you map to parameters (default approach), or read in code when a pattern needs sample-accurate reaction.

- **Graphic Meter**: **16 frequency bands**, each a modulation source. Configurable Gain, Range, Attack/Release, Slope.
- **Decibel Meter** (top bar): overall amplitude as a modulation source.
- **Beat Detect** modulator: outputs **Trigger** (fires on beat), **Average** (band-range level), and **Beat** (downward linear ramp with a Decay time). Min Freq / Max Freq target a band.
- Code-level: `lx.engine.audio.meter` (a `GraphicMeter`) and `lx.engine.tempo`. Verify exact signatures against the `lx` jar (see [`build-and-run.md`](build-and-run.md)).

## Color palette & swatches ([guide](https://chromatik.co/guide/color-palette/))

- The **Color Palette** holds **Swatches**; each swatch has up to **5 colors**. The **Active Swatch** is what devices draw from.
- Per-color modes: **Fixed** (static HSB), **Osc** (oscillates between two HSB values), **Cycle** (sweeps hue 0–360°).
- Devices can draw from the Active Swatch with a customizable **starting Index** and **number of Stops**, using blend modes **RGB / HSV / HSV-Min / HSV-CW / HSV-CCW** for gradients.

**Author takeaway:** prefer palette-linked color over hardcoded hues so patterns follow the show's color story. Expose a color parameter that reads the active swatch (and a gradient across stops) rather than baking in RGB.

## Other guide pages worth knowing

Mixer, Snapshots, Grid + Clips, MIDI, OSC, DMX, Performance Mode, and the device references (Patterns / Effects / Modulators), plus tutorials for Ableton, Vezér, and Beat Link Trigger. See the [guide index](https://chromatik.co/guide/).
