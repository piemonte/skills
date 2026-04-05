---
name: te-pattern
description: Use when creating Java LED patterns for LXStudio-TE — TEPerformancePattern, audio reactivity, color system, variable-speed time, common controls, and pattern organization.
---

# TE Pattern Development

This reference covers creating Java patterns for Titanic's End, from basic LED animation through audio-reactive performance patterns and GPU shader wrappers.

## Class Hierarchy

```
LXPattern (LX framework)
    └── DmxPattern (titanicsend.dmx.pattern)
        └── TEPattern (titanicsend.pattern)
            └── TEAudioPattern (titanicsend.pattern)
                └── TEPerformancePattern (titanicsend.pattern)
                    ├── GLShaderPattern (titanicsend.pattern.glengine)
                    └── [Your Pattern Here]
```

| Class | Use When |
|-------|----------|
| `TEPattern` | Direct model access, no audio, no common controls |
| `TEAudioPattern` | Need audio analysis but custom control layout |
| `TEPerformancePattern` | Full-featured: common controls + audio + color + time |
| `GLShaderPattern` | Wrapping a GLSL fragment shader |

**Almost all new patterns should extend `TEPerformancePattern`.**

## Full Annotated Example: Afterglow.java

```java
package titanicsend.pattern.piemonte;

import heronarts.lx.LX;
import heronarts.lx.LXCategory;
import heronarts.lx.color.LXColor;
import heronarts.lx.modulator.SawLFO;
import heronarts.lx.parameter.LXParameter;
import java.util.*;
import titanicsend.model.TEEdgeModel;
import titanicsend.pattern.TEControlTag;
import titanicsend.pattern.TEPerformancePattern;

@LXCategory("Edge FG")                          // UI category
public class Afterglow extends TEPerformancePattern {

  // Modulator: sawtooth wave cycling 0..1
  private final SawLFO phase = new SawLFO(0, 1, 1000);
  private Map<Integer, Float> edgePhaseOffsets = new HashMap<>();
  private final Random random = new Random();

  public Afterglow(LX lx) {
    super(lx);                                   // Always call super(lx)

    // Start the phase modulator
    startModulator(phase);

    // Configure common control ranges for this pattern
    controls.setRange(TEControlTag.SPEED, 0.5, 0, 1);
    controls.setRange(TEControlTag.SIZE, 5, 1, 20);
    controls.setRange(TEControlTag.QUANTITY, 0.3, 0, 1);
    controls.setRange(TEControlTag.WOW1, 0.75, 0.5, 1.0);
    controls.setRange(TEControlTag.WOW2, 5, 1.0, 10.0);
    controls.setUnits(TEControlTag.SIZE, LXParameter.Units.INTEGER);

    // Hide controls this pattern doesn't use
    controls.markUnused(TEControlTag.ANGLE);
    controls.markUnused(TEControlTag.XPOS);
    controls.markUnused(TEControlTag.YPOS);
    controls.markUnused(TEControlTag.SPIN);
    controls.markUnused(TEControlTag.WOWTRIGGER);

    // Add controls to UI (must call after configuration)
    addCommonControls();
  }

  @Override
  protected void runTEAudioPattern(double deltaMs) {
    // Read common control values
    double speed = getSpeed();
    double dotSize = getSize();
    double fadeDistance = getQuantity();
    double spacing = getWow1();
    int density = (int) Math.ceil(getWow2());

    // Update phase rate based on speed
    phase.setPeriod(1000.0 / Math.max(speed, 0.001));

    // Iterate edges
    for (TEEdgeModel edge : modelTE.getEdges().values()) {
      float offset = edgePhaseOffsets.computeIfAbsent(
          edge.hashCode(), k -> random.nextFloat());

      for (TEEdgeModel.Point ep : edge.edgePoints) {
        // ep.n = fractional position along edge (0.0..1.0)
        double pos = (ep.n + phase.getValue() + offset) % 1.0;

        // Calculate brightness based on dot pattern
        double brightness = 0;
        for (int d = 0; d < density; d++) {
          double dotPos = (d * spacing / density) % 1.0;
          double dist = Math.abs(pos - dotPos);
          dist = Math.min(dist, 1.0 - dist); // Wrap around
          brightness = Math.max(brightness,
              1.0 - (dist / Math.max(fadeDistance * dotSize / 100.0, 0.001)));
        }

        brightness = Math.max(0, Math.min(1, brightness));
        colors[ep.point.index] = LXColor.gray(brightness * 100);
      }
    }
  }
}
```

## TEPattern Base Class

**Path:** `te-app/src/main/java/titanicsend/pattern/TEPattern.java`

### Key Fields

```java
public TEWholeModel modelTE;     // The complete vehicle model
```

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getModelTE()` | `TEWholeModel` | Access the vehicle model |
| `wholeNote()` | `double` | Fraction into current measure (0..1) |
| `phrase()` | `double` | Fraction into current phrase (0..1) |
| `sinePhaseOnBeat()` | `double` | Sine modulator synced to beat (0..1) |
| `measure()` | `double` | Fraction into variable-length measure |
| `getTempo()` | `Tempo` | Engine tempo object |
| `getEqualizer()` | `GraphicMeter` | Frequency analyzer |
| `getSwatchColor(TEColorType)` | `int` | Color from current palette |
| `setEdges(int color)` | `void` | Set all edge points to color |
| `clearEdges()` | `void` | Clear all edge points |
| `clearPixels()` | `void` | Clear all pixels (uses `Arrays.fill`, faster than looping) |
| `getXn(LXPoint p)` | `float` | Normalized X coordinate for point |

## TEAudioPattern

**Path:** `te-app/src/main/java/titanicsend/pattern/TEAudioPattern.java`

Extends `TEPattern` with real-time audio analysis.

### Audio Fields

| Field | Type | Description |
|-------|------|-------------|
| `volumeLevel` | `double` | Instantaneous normalized volume (0..1) |
| `bassLevel` | `double` | Average of low frequency bands |
| `trebleLevel` | `double` | Average of high frequency bands |
| `volumeRatio` | `double` | Current volume / moving average |
| `bassRatio` | `double` | Current bass / moving average |
| `trebleRatio` | `double` | Current treble / moving average |
| `bassHit` | `boolean` | True if bass transient detected this frame |

### Audio Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `computeAudio(deltaMs)` | `void` | Update audio analysis (call once per frame) |
| `getBassLevel()` | `double` | Current bass level |
| `getTrebleLevel()` | `double` | Current treble level |
| `bassHit()` | `boolean` | Is this frame a bass transient? |
| `resetBassGate()` | `void` | Reset beat detection timing |
| `getVolumeRatiof()` | `float` | Volume ratio as float |
| `getBassRatio()` | `double` | Bass ratio |
| `getTrebleRatio()` | `double` | Treble ratio |

### Bass Hit Detection

The bass hit detector triggers when:
1. Current bass > 1.2x the moving average
2. Current bass > previous frame's bass (rising edge)
3. Retrigger timeout has elapsed (default: 80% of eighth note duration)

```java
@Override
protected void runTEAudioPattern(double deltaMs) {
    computeAudio(deltaMs);  // Update audio state

    if (bassHit()) {
        // Trigger visual effect on beat
    }

    // Use volumeRatio for reactive brightness
    double brightness = Math.min(1.0, volumeRatio);
}
```

## TEPerformancePattern

**Path:** `te-app/src/main/java/titanicsend/pattern/TEPerformancePattern.java`

The primary base class for new patterns. Provides common controls, variable-speed time, color system, and audio reactivity.

### Constructor Pattern

```java
public MyPattern(LX lx) {
    super(lx);
    // or: super(lx, TEShaderView.ALL_EDGES);  // Set default view

    // Configure controls (before addCommonControls)
    controls.setRange(TEControlTag.SIZE, 1.0, 0.1, 10.0);
    controls.setLabel(TEControlTag.WOW1, "Glow");
    controls.markUnused(TEControlTag.SPIN);

    addCommonControls();  // Must call after configuration
}

@Override
protected void runTEAudioPattern(double deltaMs) {
    // Pattern logic here
    // Use getSpeed(), getSize(), calcColor(), etc.
}
```

### Variable-Speed Time

Time advances at a rate linked to tempo and the Speed control.

| Method | Returns | Description |
|--------|---------|-------------|
| `getTime()` | `double` | Current time in seconds (can be negative) |
| `getTimeMs()` | `double` | Current time in milliseconds |
| `getDeltaMs()` | `double` | Time delta since last frame (ms) |

**Speed-to-Tempo Mapping:**

| Speed Value | Musical Duration | Beats |
|-------------|-----------------|-------|
| 0.25 | Whole note | 4 beats |
| 0.5 | Half note | 2 beats |
| 1.0 | Quarter note | 1 beat |
| 2.0 | Eighth note | 1/2 beat |
| 3.0 | Eighth triplet | 1/3 beat |
| 4.0 | Sixteenth note | 1/4 beat |

Speed is multiplied by BPM (converted to beats/sec) to scale virtual time. At 120 BPM with speed=1.0, time advances at 2x real-time (2 beats/sec).

```java
// Enable reverse playback (negative speed values)
allowBidirectionalTime(true);

// Get tempo-synced time for animation
double t = getTime();  // Continuous, speed-adjusted seconds
```

### Rotation

| Method | Returns | Description |
|--------|---------|-------------|
| `getRotationAngleFromSpeed()` | `double` | Beat-linked rotation from Speed (radians) |
| `getRotationAngleFromSpin()` | `double` | Beat-linked rotation from Spin (radians) |
| `getStaticRotationAngle()` | `double` | Static offset from Angle control (radians) |
| `setMaxRotationSpeed(rps)` | `void` | Set max rotation (radians/sec) |
| `retrigger(TEControlTag)` | `void` | Restart SPEED or SPIN timer |

### Color System

#### Primary & Secondary Colors

| Method | Returns | Description |
|--------|---------|-------------|
| `calcColor()` | `int` | Primary color with brightness applied |
| `calcColor(setBrightness)` | `int` | Primary color, optional brightness |
| `calcColor2()` | `int` | Secondary color with brightness |
| `calcColor2(setBrightness)` | `int` | Secondary color, optional brightness |
| `getGradientColor(lerp)` | `int` | Interpolated palette color (0..1) |
| `getSwatchColor(TEColorType)` | `int` | Color from swatch by type |
| `getCurrentPalette()` | `FloatBuffer` | 5 RGB colors (15 floats) |

Colors are cached per frame and only recalculated when the palette changes. Call `expireColors()` to force recalculation.

```java
// Use primary color
int color = calcColor();

// Use gradient across a normalized position
int gradColor = getGradientColor((float) ep.n);

// Get secondary color (offset from primary)
int color2 = calcColor2();
```

#### LinkedColorParameter

For patterns needing direct palette access, use `TEColorParameter` which integrates with the swatch system and supports both static colors and palette-linked modes.

### Control Getters

| Method | Range | Description |
|--------|-------|-------------|
| `getSpeed()` | -4..4 | Speed with global sync support |
| `getXPos()` | -1..1 | X position |
| `getYPos()` | -1..1 | Y position |
| `getSize()` | 0.01..5.0 | Size multiplier |
| `getQuantity()` | 0..1 | Quantity/density |
| `getSpin()` | -1..1 | Spin control |
| `getBrightness()` | 0..1 | Brightness |
| `getWow1()` | 0..1 | First WoW parameter |
| `getWow2()` | 0..1 | Second WoW parameter |
| `getWowTrigger()` | boolean | WoW trigger state |
| `getTwist()` | boolean | Axis swap state |
| `getLevelReactivity()` | 0..1 | Audio level reactivity |
| `getFrequencyReactivity()` | 0..1 | Frequency reactivity |

### Event Callbacks

```java
@Override
protected void onWowTrigger(boolean on) {
    // Called when WoW trigger activates/deactivates
    if (on) {
        // Trigger one-shot effect
    }
}

@Override
protected void onTwist(boolean on) {
    // Called when Twist toggles
}
```

## TECommonControls

**Path:** `te-app/src/main/java/titanicsend/pattern/TECommonControls.java`

Manages the standardized control interface for all performance patterns.

### Control Tags (TEControlTag)

| Tag | Path | Label | Default | Range |
|-----|------|-------|---------|-------|
| `SPEED` | `te_speed` | Speed | 0.5 | -4..4 (bipolar, exp 1.75) |
| `XPOS` | `te_xpos` | xPos | 0 | -1..1 (bipolar, center-biased) |
| `YPOS` | `te_ypos` | yPos | 0 | -1..1 (bipolar, center-biased) |
| `SIZE` | `te_size` | Size | 1.0 | 0.01..5.0 |
| `QUANTITY` | `te_quantity` | Quantity | 0.5 | 0..1 |
| `SPIN` | `te_spin` | Spin | 0 | -1..1 (bipolar, exp 2) |
| `BRIGHTNESS` | `te_brightness` | Brightness | 1.0 | 0..1 |
| `WOW1` | `te_wow1` | Wow1 | 0 | 0..1 |
| `WOW2` | `te_wow2` | Wow2 | 0 | 0..1 |
| `WOWTRIGGER` | `te_wowtrigger` | WowTrigger | false | boolean |
| `ANGLE` | `te_angle` | Angle | 0 | -PI..PI (displays degrees) |
| `LEVELREACTIVITY` | `te_level` | LvlReact | 0.1 | 0..1 |
| `FREQREACTIVITY` | `te_freq` | FreqReact | 0.1 | 0..1 |
| `TWIST` | `te_twist` | Twist | false | boolean |

### Configuration Methods

```java
// Change range and default value
controls.setRange(TEControlTag.SIZE, 5.0, 1.0, 20.0);

// Change display label
controls.setLabel(TEControlTag.WOW1, "Glow");

// Set response curve exponent
controls.setExponent(TEControlTag.SPEED, 2.0);

// Mark unused (hides from UI)
controls.markUnused(TEControlTag.SPIN);

// Set display units
controls.setUnits(TEControlTag.SIZE, LXParameter.Units.INTEGER);

// Set normalization curve
controls.setNormalizationCurve(TEControlTag.SPEED,
    LXParameter.NormalizationCurve.BIAS_CENTER);
```

### Remote Controls Order (MIDI Surface)

Controls appear on MIDI surfaces in this order:
1. LEVELREACTIVITY
2. FREQREACTIVITY
3. View
4. SPEED
5. XPOS
6. YPOS
7. QUANTITY
8. SIZE
9. ANGLE
10. SPIN
11. PANIC
12. Preset
13. WOW1
14. WOW2
15. WOWTRIGGER
16. Color Offset
17. Capture Defaults

### Panic Button

The panic control resets all parameters:
- Position, size, quantity, angle, spin → defaults
- Brightness → 100%
- Color saturation → 100%
- WoW and reactivity → cleared

## TEShaderView

**Path:** `te-app/src/main/java/titanicsend/pattern/yoffa/framework/TEShaderView.java`

Controls which model points a pattern renders to.

| Enum Value | Description |
|------------|-------------|
| `ALL_POINTS` | All points (edges + panels), default |
| `ALL_EDGES` | Edge strips only |
| `ALL_PANELS` | Panel surfaces only |
| `ALL_PANELS_INDIVIDUAL` | Panels with per-panel normalization |
| `DOUBLE_LARGE` | Large panel sections |
| `SPLIT_PANEL_SECTIONS` | Split panel variation |

```java
// Set in constructor
public MyPattern(LX lx) {
    super(lx, TEShaderView.ALL_EDGES);
    // ...
}

// Or override
@Override
public TEShaderView getDefaultView() {
    return TEShaderView.ALL_PANELS;
}
```

## GLShaderPattern (Shader Wrapper)

**Path:** `te-app/src/main/java/titanicsend/pattern/glengine/GLShaderPattern.java`

Wraps GLSL fragment shaders as TE patterns. Extends `TEPerformancePattern`.

### Minimal Java Wrapper

```java
package titanicsend.pattern.glengine;

import heronarts.lx.LX;
import heronarts.lx.LXCategory;

@LXCategory("Native Shaders")
public class MyShaderPattern extends GLShaderPattern {
    public MyShaderPattern(LX lx) {
        super(lx, TEShaderView.ALL_POINTS);
        addShader("my_shader.fs");
    }
}
```

The wrapper automatically:
- Maps all TECommonControls to shader uniforms
- Updates audio data each frame
- Transfers rendered pixels to the LX color buffer

### Shader Chaining

```java
public MyChainedPattern(LX lx) {
    super(lx);
    addShader("background.fs");  // Renders first
    addShader("overlay.fs");     // Composites on top
}
```

### Auto Shaders (No Java Wrapper Needed)

Add `#pragma auto` to any `.fs` file in `te-app/resources/shaders/` and it will automatically appear in the "Auto Shaders" UI category. See `te-shader.md` for details.

## GLEngine Audio (Static Getters)

**Path:** `te-app/src/main/java/titanicsend/pattern/glengine/GLEngine.java`

Global audio state accessible from any pattern:

| Static Method | Description |
|---------------|-------------|
| `GLEngine.getVolume()` | Instantaneous volume (0..1) |
| `GLEngine.getBassLevel()` | Bass level |
| `GLEngine.getTrebleLevel()` | Treble level |
| `GLEngine.getVolumeRatio()` | Volume / moving average |
| `GLEngine.getBassRatio()` | Bass / moving average |
| `GLEngine.getTrebleRatio()` | Treble / moving average |
| `GLEngine.getSinPhaseOnBeat()` | Sine wave on beat (0..1) |
| `GLEngine.getAvgBass()` | Bass moving average |

Audio texture (for shaders): 512x2 pixels, GL_R32F format.
- Row 0: FFT frequency bins (0-511)
- Row 1: Waveform samples (-1.0 to 1.0)

## Audio Stem Uniforms

The PerFrameBlock includes audio stem splitter values (range -1.0 to 1.0):

| Uniform | Description |
|---------|-------------|
| `stemBass` | RMS energy of bass stem |
| `stemDrums` | RMS energy of drums stem |
| `stemVocals` | RMS energy of vocals stem |
| `stemOther` | RMS energy of other/instrumental content |
| `stemDrumHits` | RMS energy of drum hits/transients |

## File Organization

Patterns are organized by developer under `te-app/src/main/java/titanicsend/pattern/`:

```
titanicsend/pattern/
├── TEPattern.java
├── TEAudioPattern.java
├── TEPerformancePattern.java
├── TECommonControls.java
├── TEControlTag.java              # in jon/ subdirectory
├── glengine/
│   ├── GLShaderPattern.java
│   └── GLEngine.java
├── piemonte/
│   └── Afterglow.java
├── jon/
│   └── ...
├── yoffa/
│   └── framework/
│       └── TEShaderView.java
└── [your-name]/
    └── YourPattern.java
```

### Conventions

1. **Package by developer:** `titanicsend.pattern.yourname`
2. **@LXCategory annotation:** Required. Common categories:
   - `"Edge FG"` — Edge foreground patterns
   - `"Edge BG"` — Edge background patterns
   - `"Panel FG"` — Panel foreground patterns
   - `"Panel BG"` — Panel background patterns
   - `"Combo FG"` — Both edges and panels
   - `"Mothership"` — Mothership-specific patterns
   - `"Native Shaders"` — Java-wrapped GLSL shaders
   - `"Auto Shaders"` — Auto-loaded GLSL shaders
3. **Code style:** Spotless with Google Java Format (enforced by CI)
4. **Always extend `TEPerformancePattern`** unless you have a specific reason not to
5. **Call `addCommonControls()`** after all control configuration in the constructor
6. **Call `computeAudio(deltaMs)`** at the start of `runTEAudioPattern()` if you need audio data
7. **Use `clearPixels()`** to clear the frame — never manually loop over `model.points` setting `TRANSPARENT`
8. **Use helpers from the class hierarchy** — check `TEPattern`, `TEAudioPattern`, and `TEPerformancePattern` for existing utility methods (e.g., `clearPixels()`, `clearEdges()`, `setEdges()`, `calcColor()`, `getGradientColor()`) before writing manual loops
9. **Speed parameter is bipolar** — range it from `-value` to `+value` so the dial centers at zero (no movement). Negative speed should reverse the animation direction. Avoid using `SawLFO` with speed-dependent period when bipolar speed is needed; instead, accumulate phase manually:
   ```java
   // Bipolar speed: negative reverses, zero stops
   controls.setRange(TEControlTag.SPEED, 0.5, -1, 1);

   // In runTEAudioPattern:
   phase += (deltaMs / periodMs) * getSpeed();
   phase = phase - Math.floor(phase); // wrap to 0..1
   ```

## Creating a New Pattern: Checklist

1. Create file at `te-app/src/main/java/titanicsend/pattern/[yourname]/PatternName.java`
2. Set package to `titanicsend.pattern.[yourname]`
3. Add `@LXCategory("...")` annotation
4. Extend `TEPerformancePattern`
5. In constructor:
   - Call `super(lx)` or `super(lx, TEShaderView.ALL_EDGES)`
   - Configure controls via `controls.setRange()`, `controls.setLabel()`, `controls.markUnused()`
   - Call `addCommonControls()`
6. Override `runTEAudioPattern(double deltaMs)`
7. Use `getSpeed()`, `getSize()`, `calcColor()`, etc. for control values
8. Write to `colors[point.index]` for each LED
9. Run `mvn spotless:apply` before committing
