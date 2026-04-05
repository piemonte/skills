---
name: te-model
description: Use when defining vehicle models for LXStudio-TE — vertex, edge, and panel file formats, DMX addressing, Java model classes, coordinate system, and symmetry groups.
---

# TE Vehicle Model Definition

This reference covers the complete vehicle model system for Titanic's End (and adaptable vehicles like Mothership). The model defines 3D geometry, LED fixture mapping, and DMX hardware addressing.

## Architecture Overview

```
TEWholeModel (Interface)
├── TEVertex (60+ vertices with 3D coordinates)
├── TEEdgeModel (LED strips between vertices)
│   └── TEEdgeModel.Point[] (individual LEDs with position)
├── TEPanelModel (triangular LED surfaces)
│   └── TEPanelModel.Point[] (LEDs with distance from centroid)
├── DmxModel (Beacons, DJ Lights)
└── TELaserModel (Laser fixtures)
```

## Resource Files

All vehicle definition files live in `te-app/resources/vehicle/`.

### general.txt

Simple key-value metadata:

```
name: Titanic's End
```

### vertexes.txt

Defines 3D vertex positions. Four space-separated columns:

| Column | Description |
|--------|-------------|
| Vertex ID | Integer identifier (e.g., 9, 10, 25) |
| X | Left-right position in microns |
| Y | Vertical position in microns |
| Z | Front-back position in microns |

```
9      2286000    304799     4496209
10    -2286000    304799     4496209
11    -2286000    304800      996900
12     2286000    304800      996900
25     2286000   3962400     5872727
26    -2286000   3962400     5872727
27     1346200   3962400     7366000
28    -1346200   3962400     7366000
30            0  11430000     4870002
31    -1219200   8873911     3613224
```

**Coordinate system:**
- X: -2.3M to +2.3M (port to starboard)
- Y: 0 to 11.4M (ground to apex)
- Z: -9.8M to +7.4M (aft to fore)
- Units: microns (1,000,000 = 1 meter)

### edges.txt

Defines LED strips connecting two vertices. Tab-separated columns:

| Column | Description |
|--------|-------------|
| V0-V1 | Vertex pair (e.g., `9-12`) |
| Orientation | `default` or `reversed` (LED wiring direction) |
| Pixel Count | Number of addressable LEDs on this strip |
| Module Address | Pixelblaze controller address (see DMX Addressing) |

```
9-12    reversed   188    x10.7.19.120#1:233
9-83    reversed    48    x10.7.19.121#1
9-114   default    119    x10.7.19.121#1:48
9-116   reversed   158    x10.7.19.123#2:249
10-11   reversed   188    10.7.11.120#1:234
10-100  reversed    48    10.7.11.121#1
10-115  default    119    10.7.11.121#1:48
10-117  reversed   158    10.7.11.123#1:249
```

- `reversed` means LED data flows from V1 toward V0
- Edge IDs are always formatted as `smallerID-largerID`

### panels.txt

Defines triangular LED surfaces. Tab-separated columns:

| Column | Description |
|--------|-------------|
| Panel ID | Alphanumeric name (e.g., `FA`, `SCA`) |
| Pixel Count | Total addressable LEDs |
| Edge 1 | First bounding edge (vertex pair) |
| Edge 2 | Second bounding edge |
| Edge 3 | Third bounding edge |
| Winding Order | Leading edge direction (e.g., `91->89`) |
| Flip | `unflipped` or `flipped` (texture mirroring) |
| Module Address | DMX controller(s), `/` separates multi-module panels |

```
FA      1270    89-91   89-126  91-126  91->89  unflipped  10.7.21.215#1/10.7.21.214#3
FB      1198    81-89   81-91   89-91   91->89  unflipped  10.7.21.213#1/10.7.21.214#1
FSA      774    89-125  89-126  125-126 126->125 unflipped 10.7.10.14#1
FSB      489    70-81   81-89   70-89   81->89  unflipped  10.7.21.212#1
```

**Panel ID naming convention:**
- `F` = Fore (front)
- `A` = Aft (back)
- `S` = Starboard (right side) or Sub-section
- `P` = Port (left side)
- Additional: `C` (center), `E` (edge), `U` (upper), `D` (down)
- Examples: `SCA` = Starboard Center A, `PFA` = Port Fore A

### views.txt

Groups of fixtures for selective rendering. Tab-separated:

| Column | Description |
|--------|-------------|
| Label | View name (`;` suffix = relative normalization) |
| Relative Norm | `true` for relative coordinate normalization |
| Selector | Comma or semicolon-separated fixture IDs |

```
Fixtures;    true    912;983;9114;9116;1011;...
Edges        true    Edge
Panels       true    Panel
Panel Sections    true    fore;aft;starboard-fore;starboard-aft;port-fore;port-aft;...
Outline      true    113117,28113,28111,111119,...
Outline DJ   true    11-98,98-99,99-101,44-101,...
```

- `Edge` and `Panel` are special selectors matching all edges/panels
- Numeric selectors reference fixture component IDs
- Semicolons in the label enable per-fixture relative normalization

### tags.properties

Semantic groupings for choreography. Key-value format:

```properties
top-e=44-101,44-47,39-44,39-101,44-50,47-50
dj-e=44-101,44-47,39-44,39-101,44-50,47-50,10-11,10-100,11-100,...
left-p=ASA,ASB,ASC,SAA,SAB,SAC,SAD,SBA,SBB,SBC,SBD,SBE,SCA,SCB,SCC
right-p=APA,APB,APC,PAA,PAB,PAC,PAD,PBA,PBB,PBC,PBD,PBE,PCA,PCB,PCC
outline=113-117,28-113,28-111,111-119,...
```

- `-e` suffix = edge tags
- `-p` suffix = panel tags
- Tags: `top`, `dj`, `left`, `right`, `port`, `starboard`, `outline`

### modules.txt

Groups edges by physical construction module (numbered 1-13):

```
1: 81-89-91-81 70-81-82-92 92-81-73
2: 84-86-88-120 84-88-25-84 88-110-25-27-110 88-119-110 ...
```

Each module groups spatially adjacent edges for installation tracking.

### Additional Resource Files

| File | Purpose |
|------|---------|
| `beacons.txt` | Beacon fixtures (B1-B3, BJKB) with IP/DMX |
| `djLights.txt` | DJ light fixtures (DJ1, DJ2, DJJKB) |
| `lasers.txt` | Laser positions (HP1-HP4, AS1-AS8) |
| `boxes.txt` | 3D bounding boxes (8 entries) |
| `panel_adjustments.txt` | Panel distortion corrections |
| `striping-instructions.txt` | Panel pixel sequencing instructions |

## DMX Addressing

TE uses Pixelblaze Output Expander controllers. Address format:

```
IP#UNIVERSE:CHANNEL
```

| Component | Description |
|-----------|-------------|
| IP | Controller IP address (e.g., `10.7.19.120`) |
| `#` | Separator |
| UNIVERSE | Output universe number (1-8) |
| `:CHANNEL` | Optional starting channel offset |

Examples:
- `10.7.19.120#1:233` — IP 10.7.19.120, universe 1, starting at channel 233
- `x10.7.19.121#1` — `x` prefix marks controllers needing special handling
- `10.7.21.215#1/10.7.21.214#3` — Panel spans two controllers

## Java Model Classes

### TEWholeModel (Interface)

**Path:** `te-app/src/main/java/titanicsend/model/TEWholeModel.java`

The top-level model interface. Extends `DmxWholeModel`.

```java
public interface TEWholeModel extends DmxWholeModel {
    // Listeners
    void addListener(TEModelListener listener);
    void removeListener(TEModelListener listener);

    // Point access
    List<LXPoint> getPoints();
    List<LXPoint> getEdgePoints();
    List<LXPoint> getPanelPoints();
    List<LXPoint> getPointsBySection(TEPanelSection section);

    // Bounding box
    float minX(); float maxX();
    float minY(); float maxY();
    float minZ(); float maxZ();

    // Vertex access
    TEVertex getVertex(int id);
    Map<Integer, TEVertex> getVertexes();

    // Edge access
    boolean hasEdge(String edgeId);
    TEEdgeModel getEdge(String edgeId);
    Map<String, TEEdgeModel> getEdges();
    Map<Integer, List<TEEdgeModel>> getEdgesBySymmetryGroup();

    // Panel access
    boolean hasPanel(String panelId);
    TEPanelModel getPanel(String panelId);
    Map<String, TEPanelModel> getPanels();

    // Special fixtures
    List<DmxModel> getBeacons();
    List<DmxModel> getDjLights();
    List<TELaserModel> getLasers();

    // Model type
    boolean isStatic();  // true = 2022-23 static, false = 2024+ dynamic
}
```

### TEVertex

**Path:** `te-app/src/main/java/titanicsend/model/TEVertex.java`

Extends `LXVector`. Represents a 3D junction point.

```java
public class TEVertex extends LXVector {
    public final int id;
    public Set<TEEdgeModel> edges;    // Connected edges (unmodifiable)
    public Set<TEPanelModel> panels;  // Connected panels (unmodifiable)

    // Static registry
    static Map<Integer, LXVector> vertexLookup;
    static void registerVertex(Integer id, LXVector position);

    // Constructors
    TEVertex(LXVector vector, int id);  // Static model (explicit coords)
    TEVertex(int id);                    // Dynamic model (coords from edges)

    // Methods
    void addEdge(TEEdgeModel edge);
    void addPanel(TEPanelModel panel);
    void nudgeToward(LXVector target, float fraction);
}
```

### TEEdgeModel

**Path:** `te-app/src/main/java/titanicsend/model/TEEdgeModel.java`

Extends `TEModel`. Represents an LED strip between two vertices.

```java
public class TEEdgeModel extends TEModel {
    public static final String TE_MODEL_TYPE = "Edge";

    // Point wrapper with position metadata
    public static class Point {
        public final LXPoint point;
        public final int i;      // Index along edge (0..size)
        public final float n;    // Fractional position (0.0..1.0)
    }

    // Fields
    public final Point[] edgePoints;
    public final int size;           // Number of LEDs
    public final TEVertex v0, v1;    // Endpoint vertices
    public final LXVector centroid;
    public Set<TEPanelModel> connectedPanels;
    public List<TEEdgeModel> symmetryGroup;

    // Metadata keys: "edgeId", "v0", "v1", "module"
}
```

### TEPanelModel

**Path:** `te-app/src/main/java/titanicsend/model/TEPanelModel.java`

Extends `TEModel`. Represents a triangular LED surface.

```java
public class TEPanelModel extends TEModel {
    public static final String TE_MODEL_TYPE = "Panel";

    // Point wrapper with distance metadata
    public static class Point {
        public final LXPoint point;
        public final double r;     // Distance from centroid
        public final double rn;    // Normalized distance (0.0..1.0)
    }

    // Fields
    public final Point[] panelPoints;
    public final LXVector centroid;
    public final TEVertex v0, v1, v2;         // Triangle vertices
    public final String edge0id, edge1id, edge2id;
    public final TEEdgeModel e0, e1, e2;      // Bounding edges
    public final List<TEEdgeModel> edges;      // Unmodifiable
    public List<TEPanelModel> neighbors;       // Share an edge
    public List<TEPanelModel> vertexNeighbors; // Share only a vertex

    // Metadata keys: "panelId", "v0", "v1", "v2",
    //   "edge1", "edge2", "edge3", "leadingEdge", "module"
}
```

## Adapting for a New Vehicle

When defining a new vehicle (e.g., Mothership):

1. **Create a new vehicle directory** under `te-app/resources/vehicle/` or a parallel path
2. **Define `general.txt`** with the vehicle name
3. **Plot vertices** — measure or CAD-export all junction points in microns
4. **Map edges** — for each LED strip, record:
   - Which two vertices it connects
   - Wiring direction (`default` or `reversed`)
   - LED pixel count
   - Controller IP and universe/channel
5. **Map panels** — for each triangular surface:
   - Three bounding edges
   - Winding order (leading edge direction)
   - Flip status
   - Controller address(es)
6. **Define views** — group fixtures for selective rendering
7. **Add tags** — semantic groupings (top, bottom, left, right, etc.)
8. **Verify in LXStudio** — load the model and confirm geometry renders correctly

### Coordinate Tips

- Use consistent units (microns recommended for precision)
- Orient Y-axis as vertical (ground = 0)
- Center X-axis on the vehicle's symmetry plane
- Z-axis runs front-to-back
- Vertex IDs must be unique integers
- Edge IDs auto-format as `smallerID-largerID`

### Symmetry Groups

Edges with matching geometry reflected about the XY or YZ planes are automatically grouped. This enables symmetric pattern application — animate one side and mirror to the other.

## Common Patterns Using Model Data

### Iterate All Edge Points
```java
for (TEEdgeModel edge : modelTE.getEdges().values()) {
    for (TEEdgeModel.Point ep : edge.edgePoints) {
        // ep.n = fractional position (0.0 at v0, 1.0 at v1)
        // ep.point = LXPoint with x, y, z coordinates
        colors[ep.point.index] = calcColor();
    }
}
```

### Iterate All Panel Points
```java
for (TEPanelModel panel : modelTE.getPanels().values()) {
    for (TEPanelModel.Point pp : panel.panelPoints) {
        // pp.rn = normalized distance from centroid (0.0 = center, 1.0 = edge)
        colors[pp.point.index] = getGradientColor((float) pp.rn);
    }
}
```

### Query by Tag
```java
// Tags are accessible through the view/selector system
// Use TEShaderView enum for pattern-level view selection
```

### Check Model Type
```java
if (modelTE.isStatic()) {
    // 2022-23 static model with explicit coordinates
} else {
    // 2024+ dynamic model with metadata-driven coordinates
}
```
