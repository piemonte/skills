---
name: te-shader
description: Use when writing GLSL shaders for LXStudio-TE — uniform reference, pragma system, include library, audio textures, palette functions, and auto-registration.
---

# TE Shader Development

This reference covers writing GLSL fragment shaders for the TE shader framework. Shaders render to the vehicle's LED model through a GPU pipeline that maps 2D shader output to 3D model coordinates.

## Shader Location

All shaders live in `te-app/resources/shaders/`:

```
te-app/resources/shaders/
├── framework/
│   ├── template.fs              # Framework wrapper (auto-included)
│   └── default.vs               # Vertex shader
├── include/
│   ├── constants.fs             # Math constants (PI, TAU, etc.)
│   ├── colorspace.fs            # Color conversion & palette functions
│   └── debug.fs                 # On-screen debug printing
├── metal_grinder.fs             # Example: pragma usage
├── polyspiral2.fs               # Example: iUniform usage
└── [your_shader].fs             # Your shaders here
```

## Entry Point

Every TE shader implements the Shadertoy-compatible entry point:

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // fragCoord: 2D pixel coordinates (scaled to iResolution)
    // fragColor: output RGBA color

    vec2 uv = fragCoord / iResolution;  // Normalize to 0..1

    fragColor = vec4(uv.x, uv.y, 0.5, 1.0);
}
```

The framework's `template.fs` wraps your `mainImage()`:
1. Looks up normalized 3D model coordinates for the current fragment
2. Skips pixels outside the model (NaN check)
3. Scales coordinates by `iResolution`
4. Calls your `mainImage()` with translated coordinates
5. Applies post-processing via `_blendFix()`

## Complete Uniform Reference

### Per-Run Block (Set Once)

```glsl
layout (std140) uniform PerRunBlock {
    vec4 iMouse;         // Mouse coordinates (unused, always zero)
    vec2 iResolution;    // Pixel resolution of render surface
};
```

### Per-Frame Block (Set Each Frame, Shared Across Patterns)

```glsl
layout (std140) uniform PerFrameBlock {
    // Audio analysis
    float beat;              // Sawtooth 0-1 synced to beat
    float sinPhaseBeat;      // Sine wave 0-1 synced to beat
    float bassLevel;         // Low frequency average
    float trebleLevel;       // High frequency average

    float volumeRatio;       // Current volume / moving average
    float bassRatio;         // Current bass / moving average
    float trebleRatio;       // Current treble / moving average

    // Audio stem splitter (range -1.0 to 1.0)
    float stemBass;          // Bass stem RMS energy
    float stemDrums;         // Drums stem RMS energy
    float stemVocals;        // Vocals stem RMS energy
    float stemOther;         // Other/instrumental stem RMS energy
    float stemDrumHits;      // Drum hit/transient RMS energy

    // Palette
    float iPaletteSize;      // Number of active palette entries (max 5)
    vec3 iPalette[5];        // Palette colors as RGB (0..1)
};
```

### Per-Pattern Uniforms (Set Each Frame, Per Pattern)

```glsl
// Time
uniform float iTime;            // Variable-speed time in seconds (linked to Speed control)

// Colors
uniform vec3 iColorRGB;         // Primary color (RGB, 0.0-1.0)
uniform vec3 iColorHSB;         // Primary color (HSB, 0.0-1.0)
uniform vec3 iColor2RGB;        // Secondary color (RGB, 0.0-1.0)
uniform vec3 iColor2HSB;        // Secondary color (HSB, 0.0-1.0)
uniform float iPaletteOffset;   // Palette animation offset (-1 if static color)

// Common controls
uniform float iSpeed;           // Speed control value
uniform float iScale;           // Size/scale control
uniform float iQuantity;        // Quantity control
uniform vec2 iTranslate;        // (xPos, yPos) translation vector
uniform float iSpin;            // Spin control value
uniform float iRotationAngle;   // Computed rotation angle in radians
uniform float iBrightness;      // Brightness (used as contrast in _blendFix)
uniform float iWow1;            // Special feature parameter 1
uniform float iWow2;            // Special feature parameter 2
uniform bool iWowTrigger;       // Momentary trigger button

// Audio reactivity
uniform float levelReact;       // Audio level reactivity (0..1)
uniform float frequencyReact;   // Frequency reactivity (0..1)
```

### Texture Samplers

```glsl
uniform sampler2D iChannel0;     // Audio texture (512x2, reserved)
uniform sampler2D iChannel1;     // User texture (via #pragma)
uniform sampler2D iChannel2;     // User texture
uniform sampler2D iChannel3;     // User texture

// TE-specific
uniform sampler2D iBackbuffer;   // Previous frame output (linear pixel order)
uniform sampler2D lxModelCoords; // Normalized 3D model coordinates
uniform sampler2D lxModelIndex;  // Model pixel index mapping
```

## Pragma System

Pragmas are preprocessor directives that configure shader behavior.

### Shader Identity

```glsl
#pragma name "MyShaderName"          // Java class name (must be unique, valid identifier)
#pragma LXCategory("Panel FG")      // UI category name
```

### Auto Registration

```glsl
#pragma auto                         // Auto-register without Java wrapper
                                     // Appears in "Auto Shaders" category
```

### Control Configuration

```glsl
#pragma TEControl.TAG.OPERATION(parameters)
```

**Available Tags:** `SPEED`, `XPOS`, `YPOS`, `SIZE`, `QUANTITY`, `SPIN`, `ANGLE`, `BRIGHTNESS`, `WOW1`, `WOW2`, `WOWTRIGGER`, `LEVELREACTIVITY`, `FREQREACTIVITY`, `TWIST`

**Operations:**

| Operation | Syntax | Description |
|-----------|--------|-------------|
| `Value` | `Value(0.5)` | Set initial value |
| `Range` | `Range(default, min, max)` | Set range and default |
| `Label` | `Label("Glow")` | Custom display label |
| `Exponent` | `Exponent(2.0)` | Response curve exponent |
| `NormalizationCurve` | `NormalizationCurve(BIAS_CENTER)` | Curve shape |
| `Disable` | `Disable` | Hide control from UI |

**Examples from metal_grinder.fs:**
```glsl
#pragma name "MetalGrinder"
#pragma TEControl.SIZE.Range(0.75, 0.1, 1.25)
#pragma TEControl.QUANTITY.Range(400.0, 100.0, 500.0)
#pragma TEControl.SPIN.Range(0.75, -5.0, 5.0)
#pragma TEControl.WOW1.Range(1.0, 2.0, 0.5)
#pragma TEControl.WOWTRIGGER.Disable
#pragma TEControl.LEVELREACTIVITY.Disable
#pragma TEControl.FREQREACTIVITY.Disable
```

### Translation Mode

```glsl
#pragma TEControl.TranslateMode(DRIFT)    // Continuous unbounded movement
#pragma TEControl.TranslateMode(NORMAL)   // Standard bounded translation (default)
```

Drift mode is useful for noise/cloud patterns where position should continuously scroll rather than snap to a bounded range.

### Texture Loading

```glsl
#pragma iChannel1 "path/to/texture.png"           // Absolute resource path
#pragma iChannel1 <textures/noise256.png>          // Relative to shaders dir
```

Supports channels 1-9. Channel 0 is reserved for audio.

## iUniform Syntax (VSCode/Shadertoy Compatible)

Alternative control configuration compatible with the ShaderToy VSCode extension:

```glsl
#iUniform float variableName=defaultValue in {min, max}
#iUniform color3 iColorRGB=vec3(0.964, 0.144, 0.519)
```

**Supported types:** `float`, `vec2`, `vec3`, `color3`

**Examples from polyspiral2.fs:**
```glsl
#pragma name "PolySpiral2"
#iUniform color3 iColorRGB=vec3(0.964, 0.144, 0.519)
#iUniform color3 iColor2RGB=vec3(0.226, 0.046, 0.636)
#iUniform float iRotationAngle=0.0 in {0.0, 6.28}
#iUniform float iQuantity=7.0 in {3.0, 12.0}
#iUniform float iScale=0.85 in {0.5, 0.99}
#iUniform float iSpeed=0.1 in {-1.0, 1.0}
#pragma TEControl.YPOS.Value(-0.07)
#pragma TEControl.SPIN.Value(0.1)
```

`#iUniform` lines are removed during preprocessing — use the standard uniform names in your shader code.

## Include System

```glsl
#include <include/constants.fs>      // Relative to shaders directory
#include <include/colorspace.fs>     // Color conversion functions
#include <include/debug.fs>          // Debug printing utilities
```

Supports up to 9 levels of nesting.

### constants.fs

```glsl
const float PI = asin(1.) * 2.;
const float TAU = PI * 2.;
const float HALFPI = PI / 2.;
#define TWO_PI TAU
```

### colorspace.fs — Color Conversion

```glsl
vec3 hsv2rgb(vec3 c);              // HSV to RGB
vec3 rgb2hsv(vec3 c);              // RGB to HSV
vec3 lrgb_to_srgb(vec3 c);        // Linear to sRGB gamma
vec3 srgb_to_lrgb(vec3 c);        // sRGB to linear
```

### colorspace.fs — Color Interpolation

```glsl
vec3 oklab_mix(vec3 colA, vec3 colB, float h);    // Perceptually uniform (default)
vec3 hsv_mix(vec3 colA, vec3 colB, float h);      // HSV space interpolation
```

### colorspace.fs — Palette Functions

```glsl
vec3 getPaletteColor(int index);                   // Get color at palette index (0..4)
vec3 getGradientColor(float h);                    // Interpolate palette (0.0..1.0)
vec3 getGradientColor_oklab(float h);              // Oklab interpolation
vec3 getGradientColor_hsv(float h);                // HSV interpolation
vec3 getGradientColor_linear(float h);             // Linear RGB interpolation
```

`getGradientColor()` uses Oklab by default when a palette is active, or returns the static color if `iPaletteOffset == -1`.

### Usage Pattern

```glsl
#include <include/constants.fs>
#include <include/colorspace.fs>

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution;

    // Use palette gradient based on position
    vec3 col = getGradientColor(uv.x);

    fragColor = vec4(col, 1.0);
}
```

## Audio in Shaders

### Audio Texture (iChannel0)

512x2 pixel texture, GL_R32F format:

| Row | Content | Range |
|-----|---------|-------|
| 0 | FFT frequency bins | 0.0+ (magnitude) |
| 1 | Waveform samples | -1.0 to 1.0 |

```glsl
// Read FFT bin
float freq = texelFetch(iChannel0, ivec2(binIndex, 0), 0).x;

// Read waveform sample
float wave = texelFetch(iChannel0, ivec2(sampleIndex, 1), 0).x;

// Common: 16 frequency bands
#define TEXTURE_SIZE 512.0
#define CHANNEL_COUNT 16.0
#define pixPerBin (TEXTURE_SIZE / CHANNEL_COUNT)

// Get level of band i (0-15)
float bandLevel = texelFetch(iChannel0, ivec2(int(float(i) * pixPerBin), 0), 0).x;
```

### Audio Uniforms (PerFrameBlock)

Available without texture sampling:

```glsl
// Beat-synced animation
float pulse = sinPhaseBeat;           // Smooth 0-1 on beat

// Audio-reactive scaling
float scale = 1.0 + bassLevel * levelReact;

// Audio-reactive color shift
vec3 col = getGradientColor(beat);

// Stem-aware effects
float drumsIntensity = max(0.0, stemDrums);
float vocalGlow = max(0.0, stemVocals);
```

## Alpha and Blending

### _blendFix()

The framework's `_blendFix()` function optimizes output for LED blending:

- If alpha == 1.0: substitutes `max(r,g,b)` for alpha (brightness-as-alpha)
- Applies `iBrightness` as contrast multiplier
- Enables proper compositing when patterns are layered

### Preprocessor Controls

```glsl
#define TE_ALPHATHRESHOLD 0.5      // Pixels above threshold → fully opaque
#define TE_NOALPHAFIX              // Use pre-2023 alpha behavior
#define TE_NOPOSTPROCESSING        // Disable all post-processing entirely
#define TE_EFFECTSHADER            // Mark as effect shader (not pattern)
#define TE_NOTRANSLATE             // Disable automatic iTranslate application
```

**When to use each:**
- `TE_ALPHATHRESHOLD` — Hard-edged patterns (text, geometric shapes)
- `TE_NOPOSTPROCESSING` — When you need exact RGB values (calibration, debug)
- `TE_NOTRANSLATE` — Drift mode patterns that handle translation internally
- `TE_EFFECTSHADER` — Post-processing effects applied to other patterns

## Backbuffer (Previous Frame)

Access the previous frame for feedback/trail effects:

```glsl
// Get previous frame pixel at current position
vec4 prev = _getBackbufferPixel();

// Get neighboring pixel (using model index mapping)
vec4 neighbor = _getMappedPixel(iBackbuffer, ivec2(x, y));
```

**Important:** `iBackbuffer` is NOT a rectangular image. Pixels are in linear model order matching the LXModel point array.

## Helper Functions (from template.fs)

```glsl
vec4 _getModelCoordinates();          // Normalized 3D coords for current fragment
vec4 _getBackbufferPixel();           // Previous frame at current position
vec4 _getMappedPixel(sampler2D, ivec2); // Pixel from mapped texture by coordinate
vec4 _blendFix(vec4 col);            // Apply alpha/brightness post-processing
```

## Minimal Complete Example

```glsl
// Pulsing gradient pattern with audio reactivity
#pragma auto
#pragma TEControl.SIZE.Range(1.0, 0.1, 5.0)
#pragma TEControl.WOW1.Label("Pulse Depth")
#pragma TEControl.WOW1.Value(0.5)

#include <include/constants.fs>
#include <include/colorspace.fs>

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution;

    // Distance from center
    float d = length(uv - 0.5) * iScale;

    // Time-based pulse with audio reactivity
    float pulse = sin(d * TAU * iQuantity - iTime * TAU) * 0.5 + 0.5;
    pulse = mix(pulse, pulse * bassRatio, levelReact);

    // Color from palette gradient
    vec3 col = getGradientColor(pulse);

    // Apply Wow1 as pulse depth
    float alpha = smoothstep(1.0 - iWow1, 1.0, pulse);

    fragColor = vec4(col, alpha);
}
```

## Development Workflow

1. Create `.fs` file in `te-app/resources/shaders/`
2. Add `#pragma auto` for auto-registration (or write a Java wrapper)
3. Implement `void mainImage(out vec4 fragColor, in vec2 fragCoord)`
4. Add `#pragma` directives for control configuration
5. Include `constants.fs` and `colorspace.fs` as needed
6. Save and restart LXStudio (or delete & re-add pattern for hot reload)
7. Pattern appears in "Auto Shaders" category (or custom `#pragma LXCategory`)

### Hot Reload

After initial load, saving a shader file triggers automatic recompilation. If compilation fails, the previous working version continues to render and errors appear in the console.

## Shader Configuration Opcodes (Internal Reference)

| Opcode | Source | Effect |
|--------|--------|--------|
| `AUTO` | `#pragma auto` | Auto-register pattern class |
| `SET_VALUE` | `#pragma TEControl.TAG.Value(val)` | Set initial value |
| `SET_RANGE` | `#pragma TEControl.TAG.Range(v,min,max)` | Set control range |
| `SET_LABEL` | `#pragma TEControl.TAG.Label("text")` | Custom label |
| `SET_EXPONENT` | `#pragma TEControl.TAG.Exponent(exp)` | Non-linear scaling |
| `SET_NORMALIZATION_CURVE` | `#pragma TEControl.TAG.NormalizationCurve(type)` | Curve shape |
| `DISABLE` | `#pragma TEControl.TAG.Disable` | Hide from UI |
| `SET_TEXTURE` | `#pragma iChannel[1-9]` | Load texture file |
| `SET_CLASS_NAME` | `#pragma Name("Class")` | Java class name |
| `SET_LX_CATEGORY` | `#pragma LXCategory("Name")` | UI category |
| `SET_TRANSLATE_MODE_NORMAL` | `#pragma TEControl.TranslateMode(NORMAL)` | Bounded translation |
| `SET_TRANSLATE_MODE_DRIFT` | `#pragma TEControl.TranslateMode(DRIFT)` | Continuous drift |
