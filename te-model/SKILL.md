---
name: te-model
description: Use when working with LXStudio-TE vehicle models and fixture files — .lxf fixture format, vehicle architecture, edge/panel/window fixtures, transforms, ArtNet output, and Java model classes.
---

# TE Vehicle Model & Fixture System

Vehicle geometry, LED fixture mapping, and hardware addressing in LXStudio-TE are defined by `.lxf` fixture files (JSON-based Chromatik format). Each vehicle has its own fixture hierarchy with vehicle-specific component types.

## Architecture Overview

```
te-app/Fixtures/
├── TE/                          Titanic's End vehicle
│   ├── TE.lxf                   Master wrapper — references all edges and panels
│   ├── edge/                    205 edge fixtures (LED strips between vertices)
│   │   └── Edge9-12.lxf ...
│   ├── panel/                   70 panel fixtures (triangular LED surfaces)
│   │   └── FA.lxf ...
│   └── module/                  Module-level groupings
├── Mothership/                  Mothership vehicle
│   ├── Mothership.lxf           Master wrapper — references all slices
│   └── window/                  Window/slice fixtures (radial segments)
│       └── Slice01P.lxf ...
├── Beacons/                     Shared beacon fixtures
├── Grids/                       Grid/display fixtures
└── Utility/                     Common utilities
```

**Key point:** Vehicle components are vehicle-specific. TE uses panels and edges; Mothership uses windows and slices. A new vehicle would define its own fixture types — you would not reuse TE's panel and edge fixtures.

### Data Flow

```
.lxf fixture files → LX framework loads and parses → TEWholeModelDynamic post-processes
→ Wraps into TEEdgeModel / TEPanelModel / TEVertex → Available to patterns via modelTE
```

## .lxf Fixture File Format

Fixture files use JSON (with comments allowed). Every `.lxf` file has this general structure:

```jsonc
{
  label: "Display Name",
  tags: [ "tag1", "tag2" ],
  parameters: { /* configurable values */ },
  transforms: [ /* 3D positioning and rotation */ ],
  meta: { /* metadata linking to the Java model */ },
  components: [ /* LED geometry definition */ ],
  outputs: [ /* ArtNet controller routing */ ]
}
```

### Parameters

Typed, configurable values with defaults. Referenced elsewhere via `$name` syntax.

```jsonc
parameters: {
  "points": { default: 188, type: "int", min: 1, label: "Points", description: "Number of points in the edge" },
  "host": { default: "10.7.19.120", type: "string", label: "Host", description: "Controller IP address or hostname" },
  "output": { default: 1, type: "int", min: 1, max: 4, label: "Output", description: "Controller output 1-4" },
  "ledOffset": { default: 233, type: "int", min: 0, label: "LED Offset", description: "0-based starting position in pixels" },
  "reverse": { default: true, type: "boolean", label: "Reverse", description: "Reverse the output direction" },
  "onCar": { default: true, type: "boolean", label: "On Car", description: "True = Locate to position on car, False = Locate to origin" },
  "artnetSequence": { default: false, type: "boolean", label: "ArtNet Sequence", description: "Enable ArtNet sequence packets" }
}
```

| Type | Example |
|------|---------|
| `int` | `{ default: 188, type: "int", min: 1, max: 4 }` |
| `float` | `{ default: 7.53, type: "float" }` |
| `string` | `{ default: "10.7.19.120", type: "string" }` |
| `boolean` | `{ default: true, type: "boolean" }` |

### Transforms

Sequential 3D positioning. Each entry applies one transformation. Use `enabled: "$param"` to make transforms conditional.

```jsonc
transforms: [
  { x: "-177.0161", enabled: "$onCar" },     // translate X
  { y: "12.0000", enabled: "$onCar" },        // translate Y
  { z: "90.0000", enabled: "$onCar" },         // translate Z
  { yaw: "0.0000", enabled: "$onCar" },        // rotate around Y axis
  { roll: "0.0000", enabled: "$onCar" },       // rotate around Z axis
  { pitch: "-167.3002", enabled: "$onCar" },   // rotate around X axis
  { x: "$xOffset" }                            // parameter-driven offset
]
```

Transforms support expressions: `{ roll: "(-6.5 - ($radial - 1)) * 360 / 24" }`

### Meta

Metadata that links the fixture to the Java model. The `TEWholeModelDynamic` class reads these fields to build domain objects.

**Edge meta:**
```jsonc
meta: {
  "edgeId": "9-12",
  "v0": "9",
  "v1": "12",
  "module": "19"
}
```

**Panel meta:**
```jsonc
meta: {
  "panelId": "FA",
  "v0": "91", "v1": "89", "v2": "126",
  "edge1": "89-91", "edge2": "89-126", "edge3": "91-126",
  "leadingEdge": "91->89",
  "module": "21"
}
```

### Components

Define LED geometry. Component types are vehicle-specific.

**Edge — single strip:**
```jsonc
components: [
  { type: "strip", numPoints: "$points", spacing: "0.6562" }
]
```

**Panel — rows of LEDs with a backing surface:**
```jsonc
components: [
  { type: "panelRow", row: "0", offset: "0", numPoints: "59" },
  { type: "panelRow", row: "1", offset: "1", numPoints: "57" },
  // ... rows decrease in width toward the triangle apex
  { type: "panelRow", row: "41", offset: "8", numPoints: "2" },
  { type: "panelBacking", rows: "41", offset: "8", numPointsLast: "2", numPointsFirst: "59",
    showBacking: "$showBacking", flipBacking: "$flipBacking" }
]
```

**Mothership window — references window sub-fixtures:**
```jsonc
components: [
  { type: "Window1", id: "w1", extraLEDs: "$w1extraLEDs", ledOffset: "$w1ledOffset" },
  { type: "Window2", id: "w2", extraLEDs: "$w2extraLEDs", ledOffset: "$w2ledOffset" },
  // ... up to Window8B
]
```

### Outputs

ArtNet controller routing. Supports expressions for universe/channel calculation.

**Edge output (single strip):**
```jsonc
outputs: [
  { enabled: "$hasOutput",
    host: "$host",
    universe: "$output*10+(($ledOffset*3)/510)",
    channel: "($ledOffset*3)%510",
    protocol: "artnet",
    sequenceEnabled: "$artnetSequence",
    reverse: "$reverse"
  }
]
```

**Panel output (multi-strand with segments):**
```jsonc
outputs: [
  { host: "$strand1host",
    universe: "$strand1output*10",
    protocol: "artnet",
    sequenceEnabled: "$artnetSequence",
    segments: [
      { componentIndex: 0, reverse: false },
      { componentIndex: 1, reverse: true },
      { componentIndex: 2, reverse: false },
      { componentIndex: 3, reverse: true, padPre: 1 },
      { componentIndex: 4, reverse: false, length: 22 }
    ]
  }
  // Additional strand outputs follow the same pattern
]
```

Segments map component rows to physical LED strands, handling serpentine wiring (alternating `reverse`) and partial rows (`start`, `length`, `padPre`).

## Master Wrapper Files

Each vehicle has a master `.lxf` that references all sub-fixtures.

**TE.lxf** — references edges and panels by relative path:
```jsonc
{
  label: "TE",
  tags: [ "te", "car" ],
  parameters: {
    "artnetSequence": { default: false, type: "boolean" },
    "showBacking": { type: "boolean", default: "true" }
  },
  components: [
    { type: "edge/Edge9-12", artnetSequence: "$artnetSequence" },
    { type: "edge/Edge9-83", artnetSequence: "$artnetSequence" },
    // ... 205 edges
    { type: "panel/FA", artnetSequence: "$artnetSequence", showBacking: "$showBacking" },
    { type: "panel/FB", artnetSequence: "$artnetSequence", showBacking: "$showBacking" },
    // ... 70 panels
  ]
}
```

**Mothership.lxf** — references slices:
```jsonc
{
  label: "Mothership",
  tag: "mothership",
  components: [
    { type: "window/Ramp" },
    { type: "window/Slice01P" },
    { type: "window/Slice01S" },
    // ... 40 slices (20 port + 20 starboard)
  ]
}
```

## Vehicle Comparison

| Aspect | Titanic's End | Mothership |
|--------|--------------|------------|
| Fixture path | `Fixtures/TE/` | `Fixtures/Mothership/` |
| Primary components | Edges (strips) + Panels (triangles) | Windows (LED rings) in Slices |
| Component count | 205 edges, 70 panels | ~40 slices with 8-9 windows each |
| Geometry | Vertices + edges forming triangulated surfaces | Radial slices around a central axis |
| Positioning | XYZ translation + yaw/roll/pitch | Y translation + radial roll expression |
| Tags | `edge`, `panel`, module (`m19`), position (`bottom`) | `slice`, `port`/`starboard`, slice ID |

## Java Model Classes

These classes wrap fixture data at runtime. They are populated from fixture metadata by `TEWholeModelDynamic` — not from the legacy text files.

### TEWholeModel (Interface)

```java
public interface TEWholeModel extends DmxWholeModel {
    List<LXPoint> getPoints();
    List<LXPoint> getEdgePoints();
    List<LXPoint> getPanelPoints();

    TEVertex getVertex(int id);
    Map<Integer, TEVertex> getVertexes();

    TEEdgeModel getEdge(String edgeId);
    Map<String, TEEdgeModel> getEdges();
    Map<Integer, List<TEEdgeModel>> getEdgesBySymmetryGroup();

    TEPanelModel getPanel(String panelId);
    Map<String, TEPanelModel> getPanels();

    List<DmxModel> getBeacons();
    List<DmxModel> getDjLights();
    List<TELaserModel> getLasers();

    boolean isStatic();  // false for current dynamic fixture system
}
```

### TEEdgeModel

Represents an LED strip between two vertices. `edgeId` from fixture meta (e.g., `"9-12"`).

```java
public class TEEdgeModel extends TEModel {
    public static class Point {
        public final LXPoint point;
        public final int i;      // index along edge
        public final float n;    // fractional position 0.0..1.0
    }

    public final Point[] edgePoints;
    public final int size;
    public final TEVertex v0, v1;
    public final LXVector centroid;
    public Set<TEPanelModel> connectedPanels;
    public List<TEEdgeModel> symmetryGroup;
}
```

### TEPanelModel

Represents a triangular LED surface. `panelId` from fixture meta (e.g., `"FA"`).

```java
public class TEPanelModel extends TEModel {
    public static class Point {
        public final LXPoint point;
        public final double r;     // distance from centroid
        public final double rn;    // normalized 0.0..1.0
    }

    public final Point[] panelPoints;
    public final LXVector centroid;
    public final TEVertex v0, v1, v2;
    public final TEEdgeModel e0, e1, e2;
    public List<TEPanelModel> neighbors;       // share an edge
    public List<TEPanelModel> vertexNeighbors; // share only a vertex
}
```

### TEVertex

3D junction point. Coordinates derived from fixture transforms (not from `vertexes.txt`).

```java
public class TEVertex extends LXVector {
    public final int id;
    public Set<TEEdgeModel> edges;
    public Set<TEPanelModel> panels;
}
```

## Common Patterns Using Model Data

### Iterate All Edge Points

```java
for (TEEdgeModel edge : modelTE.getEdges().values()) {
    for (TEEdgeModel.Point ep : edge.edgePoints) {
        // ep.n = fractional position (0.0 at v0, 1.0 at v1)
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

## Legacy Reference Files

The `te-app/resources/vehicle/` directory contains text files (`vertexes.txt`, `edges.txt`, `panels.txt`, `views.txt`, `tags.properties`, `modules.txt`) from the original configuration system. These are **not used at runtime** — all vehicle mapping is now done through `.lxf` fixture files. The text files are retained for historical reference only.
