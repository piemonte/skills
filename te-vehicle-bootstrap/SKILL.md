---
name: te-vehicle-bootstrap
description: Use when bootstrapping a new vehicle for LXStudio-TE — end-to-end guide covering geometry, fixtures, show files, test patterns, and troubleshooting.
---

# TE Vehicle Bootstrap

Step-by-step guide for bringing a new vehicle (like Mothership) into the LXStudio-TE system. Each step references the relevant skill file for detailed instructions.

## Prerequisites

- Java 17+ and Maven installed
- LXStudio-TE repository cloned and building (`mvn package`)
- Vehicle dimensions measured or available from CAD
- LED strip layout planned (pixel counts, controller assignments)
- Network addresses for Pixelblaze Output Expander controllers

## Step 1: Define Model Geometry

> **Reference:** [te-model.md](te-model.md) — Resource file formats, coordinate system

### 1.1 Create Vehicle Directory

```bash
mkdir -p te-app/resources/vehicle-mothership/
```

### 1.2 Write general.txt

```
name: Mothership
```

### 1.3 Plot Vertices (vertexes.txt)

Measure or export all structural junction points:

```
# VertexID  X(microns)  Y(microns)  Z(microns)
1    0         0         0
2    2000000   0         0
3    1000000   2000000   0
```

**Tips:**
- Use microns for maximum precision (1,000,000 = 1 meter)
- Y-axis = vertical (ground = 0)
- Center X on the vehicle's symmetry plane
- Vertex IDs must be unique integers

### 1.4 Verify Geometry

Load the model in LXStudio to confirm vertex positions render correctly before proceeding to edges and panels.

## Step 2: Map Fixtures and DMX

> **Reference:** [te-model.md](te-model.md) — Edge/panel formats, DMX addressing

### 2.1 Define Edges (edges.txt)

For each LED strip:

```
# V0-V1    orientation    pixel_count    controller_address
1-2        default        150            10.0.0.10#1
2-3        reversed       200            10.0.0.10#1:450
```

**Checklist:**
- [ ] Every edge connects two defined vertices
- [ ] Orientation matches physical LED wiring direction
- [ ] Pixel count matches actual strip length
- [ ] Controller IP is reachable on the network
- [ ] Universe and channel numbers don't overlap on the same controller

### 2.2 Define Panels (panels.txt)

For each triangular LED surface:

```
# PanelID  pixels  edge1  edge2  edge3  winding  flip     address
P1         500     1-2    2-3    1-3    2->1     unflipped  10.0.0.11#1
```

**Checklist:**
- [ ] Three edges form a closed triangle
- [ ] All referenced edges exist in edges.txt
- [ ] Winding order matches physical panel orientation
- [ ] Flip status set correctly for texture mapping
- [ ] Multi-controller panels use `/` separator

### 2.3 Define Supporting Files

**modules.txt** — Group edges by physical construction module:
```
1: 1-2-3-1 4-5-6
2: 7-8-9-10
```

**tags.properties** — Semantic groupings:
```properties
top-e=1-2,2-3
left-p=P1,P2,P3
right-p=P4,P5,P6
```

**views.txt** — Fixture groupings for rendering:
```
Fixtures;    true    112;123;213;...
Edges        true    Edge
Panels       true    Panel
```

### 2.4 Additional Fixtures

If the vehicle has beacons, DJ lights, or lasers, create the corresponding files:
- `beacons.txt` — Beacon positions and DMX addresses
- `djLights.txt` — DJ light fixtures
- `lasers.txt` — Laser fixture positions

## Step 3: Configure Show File

> **Reference:** [te-show.md](te-show.md) — .lxp structure, channel setup

### 3.1 Create Base Show File

Start from `BootupTemplate.lxp`:

1. Open LXStudio-TE
2. Load `BootupTemplate.lxp`
3. Verify the new vehicle model loads correctly
4. Save As `MshipStartup.lxp` (or similar)

### 3.2 Configure Channels

Set up initial mixing channels:

| Channel | Purpose | Suggested Patterns |
|---------|---------|-------------------|
| 1 | Edge background | Solid color, slow gradient |
| 2 | Edge foreground | Afterglow, chase patterns |
| 3 | Panel background | Color wash, breathing |
| 4 | Panel foreground | Shader patterns |

### 3.3 Set Up Views

Ensure views match the new vehicle's fixture layout. Views from `views.txt` load automatically; customize in the UI as needed.

## Step 4: Write First Test Patterns

> **Reference:** [te-pattern.md](te-pattern.md) — Class hierarchy, controls, audio

### 4.1 Solid Color Test

The simplest pattern to verify model connectivity:

```java
package titanicsend.pattern.vehicle;

import heronarts.lx.LX;
import heronarts.lx.LXCategory;
import heronarts.lx.model.LXPoint;
import titanicsend.pattern.TEPerformancePattern;

@LXCategory("Test")
public class SolidTest extends TEPerformancePattern {
    public SolidTest(LX lx) {
        super(lx);
        addCommonControls();
    }

    @Override
    protected void runTEAudioPattern(double deltaMs) {
        int color = calcColor();
        for (LXPoint p : modelTE.getPoints()) {
            colors[p.index] = color;
        }
    }
}
```

### 4.2 Edge Chase Test

Verify edge geometry and LED direction:

```java
@LXCategory("Test")
public class EdgeChaseTest extends TEPerformancePattern {
    public EdgeChaseTest(LX lx) {
        super(lx);
        addCommonControls();
    }

    @Override
    protected void runTEAudioPattern(double deltaMs) {
        clearPixels();
        double t = getTime();
        int color = calcColor();

        for (TEEdgeModel edge : modelTE.getEdges().values()) {
            for (TEEdgeModel.Point ep : edge.edgePoints) {
                // Traveling dot based on fractional position
                double dist = Math.abs(ep.n - (t % 1.0));
                if (dist < 0.05) {
                    colors[ep.point.index] = color;
                }
            }
        }
    }
}
```

### 4.3 Panel Distance Test

Verify panel geometry and centroid calculations:

```java
@LXCategory("Test")
public class PanelDistTest extends TEPerformancePattern {
    public PanelDistTest(LX lx) {
        super(lx);
        addCommonControls();
    }

    @Override
    protected void runTEAudioPattern(double deltaMs) {
        for (TEPanelModel panel : modelTE.getPanels().values()) {
            for (TEPanelModel.Point pp : panel.panelPoints) {
                // Gradient from centroid to edge
                colors[pp.point.index] = getGradientColor((float) pp.rn);
            }
        }
    }
}
```

### 4.4 Run and Verify

```bash
mvn spotless:apply && mvn package
# Launch LXStudio and load your show file
# Activate each test pattern and verify:
# - All LEDs light up (no missing fixtures)
# - Edge chase moves in expected direction
# - Panel gradients radiate from center
```

## Step 5: Add Shader Patterns

> **Reference:** [te-shader.md](te-shader.md) — Uniforms, pragmas, includes

### 5.1 Create Test Shader

Create `te-app/resources/shaders/mship_test.fs`:

```glsl
#pragma auto
#pragma LXCategory("Mothership")

#include <include/constants.fs>
#include <include/colorspace.fs>

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution;
    float d = length(uv - 0.5) * iScale;
    float wave = sin(d * TAU * iQuantity - iTime * TAU) * 0.5 + 0.5;
    vec3 col = getGradientColor(wave);
    fragColor = vec4(col, wave);
}
```

### 5.2 Verify Shader

1. Restart LXStudio (or hot-reload)
2. Find pattern in "Mothership" category (or "Auto Shaders" without `#pragma LXCategory`)
3. Verify it renders on the new vehicle's fixtures
4. Test control responsiveness (Speed, Size, Quantity)

### 5.3 Add Audio-Reactive Shader

```glsl
#pragma auto
#pragma LXCategory("Mothership")
#pragma TEControl.WOW1.Label("Pulse Depth")
#pragma TEControl.WOW1.Value(0.5)

#include <include/constants.fs>
#include <include/colorspace.fs>

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution;

    // Audio-reactive pulse
    float pulse = sin(uv.y * TAU * 3.0 - iTime * TAU) * 0.5 + 0.5;
    pulse = mix(pulse, pulse * bassRatio, levelReact);

    // Stem-aware color shift
    float hueShift = stemDrums * 0.1;
    vec3 col = getGradientColor(pulse + hueShift);

    float alpha = smoothstep(1.0 - iWow1, 1.0, pulse);
    fragColor = vec4(col, alpha);
}
```

## Step 6: Troubleshooting

### Model Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No LEDs visible | Model files not found | Check vehicle directory path |
| LEDs in wrong position | Vertex coordinates wrong | Verify units (microns) and axis orientation |
| Edge LEDs reversed | Wrong orientation in edges.txt | Swap `default`/`reversed` |
| Panel missing | Edge IDs don't form triangle | Verify three edges share vertices |
| Partial panel | Pixel count mismatch | Match count to physical LED strip |

### DMX Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No output to LEDs | Controller unreachable | Ping controller IP address |
| Wrong LEDs light up | Universe/channel overlap | Check address assignments |
| Flickering | Multiple patterns on same fixture | Check channel/blend configuration |
| Partial strip | Channel offset wrong | Verify `:CHANNEL` values in address |

### Pattern Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Pattern not in UI | Missing `@LXCategory` | Add annotation to class |
| Controls don't appear | Missing `addCommonControls()` | Call in constructor |
| Colors wrong | Not using `calcColor()` | Use color system methods |
| Timing off | Not using `getTime()` | Use variable-speed time |
| Shader compile error | GLSL syntax | Check console for error messages |

### Build Issues

```bash
# Format check (must pass for CI)
mvn spotless:check

# Auto-format
mvn spotless:apply

# Full build
mvn package -DskipTests
```

## Checklist Summary

- [ ] **Model files** — general.txt, vertexes.txt, edges.txt, panels.txt
- [ ] **Supporting files** — views.txt, tags.properties, modules.txt
- [ ] **Geometry verified** — All vertices render at correct 3D positions
- [ ] **DMX verified** — All controllers reachable, no address conflicts
- [ ] **Show file created** — Saved from BootupTemplate.lxp
- [ ] **Channels configured** — Edge BG/FG and Panel BG/FG channels
- [ ] **Test patterns working** — Solid, edge chase, panel distance
- [ ] **Shader patterns working** — Auto shader renders correctly
- [ ] **Audio reactivity confirmed** — Bass hit and level reactivity visible
- [ ] **Code formatted** — `mvn spotless:apply` passes
