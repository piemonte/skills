# Apotheneum Geometry Reference

Everything a pattern needs to address LEDs on the cube and cylinder. All facts are from `src/main/java/apotheneum/Apotheneum.java`.

## Constants

| Constant | Value | Meaning |
|---|---|---|
| `GRID_WIDTH` | 50 | Columns per cube face |
| `GRID_HEIGHT` | 45 | Points per cube column |
| `CYLINDER_HEIGHT` | 43 | Points per cylinder column |
| `DOOR_WIDTH` | 10 | Door width in columns |
| `DOOR_HEIGHT` | 11 | Door cutout height in points |
| `Cube.Ring.LENGTH` | 200 | Columns around the cube (4 × 50) |
| `Cylinder.Ring.LENGTH` | 120 | Columns around the cylinder |
| `Cube.DOOR_START_COLUMN` | 20 | First door column on each face |
| `Cylinder.DOOR_START_COLUMN` | 10 | First door column in each 30-col group |

## Physical nesting

The cylinder is **concentric inside** the cube — both centered at `cubeSide*0.5` ≈ (245.5", 245.5") (`Apotheneum.lxf:291-292`). Cube side 491"; cylinder radius 180" (Ø 360"), leaving a ~65" annular gap to each cube wall. Both nets hang from near the top (cube top 444"; cylinder top ≈ 425.25"), so they are roughly **bottom-aligned with tops offset by ~2 nodes**. The 4 doors on each structure are cardinally aligned (0°/90°/180°/270°). Co-rotating (CW from above) but **column 0 differs** between structures — align cross-structure work by world coords / normalized angle, not raw index. Techniques that exploit all this: [`geometry-complements.md`](geometry-complements.md).

## Object model

```
Apotheneum
├── cube      : Cube
│   ├── exterior : Cube.Orientation
│   ├── interior : Cube.Orientation   (may be null)
│   └── faces    : Face[]             (all ext + int faces)
└── cylinder  : Cylinder
    ├── exterior : Cylinder.Orientation
    └── interior : Cylinder.Orientation (may be null)
```

Flags: `Apotheneum.exists` (model loaded), `Apotheneum.hasInterior` (interior present). `ApotheneumPattern.render()` is only called when `exists` is true, so you don't re-check it; but **do** guard interior access with `hasInterior` if you touch interior directly.

### Orientation (shared API)

Both `Cube.Orientation` and `Cylinder.Orientation` extend `Apotheneum.Orientation`:

- `Column[] columns()` / `column(int x)` — vertical sequences
- `Ring[] rings()` / `ring(int y)` — horizontal sequences
- `LXPoint point(int x, int y)` == `column(x).points[y]`
- `int available(int columnIndex)` — lit points in that column (door-aware)
- `int width()` (column count), `int height()` (points per column)
- Constants `EXTERIOR = 0`, `INTERIOR = 1`

A `Column` wraps the underlying `LXModel`: `column.points` (`LXPoint[]`), `column.size`, `column.index`, `column.model`.

## Sequences: Column, Row, Ring

`Column`, `Row`, and `Ring` share a common base, `Apotheneum.Sequence`, which gives every one of them:

- `points` — the `LXPoint[]` for that sequence
- `index` — its position relative to its siblings (so `column.index`, `row.index`, `ring.index` all work the same way)

A `Column` additionally wraps the LXModel it was built from: `column.model`, `column.size`.

> **Migration note:** columns used to be raw `LXModel`s; they are now `Apotheneum.Column`. Update loops accordingly:
> ```java
> // old
> for (LXModel column : face.columns) { ... }
> // new
> for (Apotheneum.Column column : face.columns) { ... }
> for (Apotheneum.Column column : Apotheneum.cylinder.interior.columns) { ... }
> ```
> If you work directly against the repo, pull latest — this is a minor breaking change.

## Wrapping / infinite canvas

> ⚠️ **Latest `main` / may be unreleased.** These wrapping APIs are not present in every build (e.g. not in the v2.0.0 snapshot). Verify they exist in your checkout before using; otherwise wrap indices manually with `Math.floorMod(i, n)`.

Surfaces can be treated as an infinite canvas:

- `Column`, `Row`, and `Ring` expose `next()` and `previous()`, which advance to the adjacent sequence with automatic wrap-around.
- `Orientation` and `Face` offer index-based wrapping overloads: `.column(index, true)` and `.ring(index, true)` — the `true` enables wrapping, so out-of-range indices wrap instead of throwing.

Manual equivalent when the wrapping API isn't available:
```java
int n = orientation.width();
Apotheneum.Column c = orientation.column(Math.floorMod(i, n));
```

## Cube

Four faces in clockwise order viewed from above: **front, right, back, left**.

```java
for (Apotheneum.Cube.Face face : Apotheneum.cube.exterior.faces) {
  for (Apotheneum.Column col : face.columns) {     // 50 columns
    for (LXPoint p : col.points) {                 // 45 points, Y=0 at top
      colors[p.index] = LXColor.gray(50);
    }
  }
}
```

- `face.columns` — 50 `Column`s (validated; throws if not 50×45).
- `face.rows` — 45 `Row`s (horizontal slices of one face).
- The orientation's combined `columns` (200) concatenates front+right+back+left, and `rings` (200-wide) wrap horizontally around all four faces — use these for effects that travel around the cube.

**Global vs local column index:** within a face, columns are 0..49. For a global index across the orientation, `globalColumn = face * GRID_WIDTH + localColumn` (face: front=0, right=1, back=2, left=3).

## Cylinder

```java
for (Apotheneum.Cylinder.Ring ring : Apotheneum.cylinder.exterior.rings) {  // 43 rings
  for (LXPoint p : ring.points) {                                            // 120 around
    colors[p.index] = LXColor.gray(50);
  }
}
```

- `cylinder.exterior.columns` — 120 `Column`s, each 43 tall (validated).
- `cylinder.exterior.rings` — 43 `Ring`s, each 120 points around the circumference. Use rings for horizontal bands/scrolls, columns for vertical effects.

## Coordinate orientation

- **Y = 0 is the top** of every column; `points[height-1]` is the bottom (inverted from typical screen coordinates).
- Each `LXPoint` carries world coordinates `p.x/p.y/p.z` and normalized `p.xn/p.yn/p.zn` in 0..1. Center with `p.xn - 0.5f`, etc. `p.yn` runs along the column height; useful for vertical gradients.

## Doors

Doors physically cut some columns short, so those columns have fewer points. **Always** size vertical work to `available(col)` rather than `GRID_HEIGHT`/`CYLINDER_HEIGHT`.

```java
Apotheneum.Cube.Orientation ext = Apotheneum.cube.exterior;
for (int col = 0; col < ext.width(); col++) {
  int h = ext.available(col);        // 45 normally, 34 on a door column
  for (int y = 0; y < h; y++) {
    colors[ext.point(col, y).index] = LXColor.gray(50);
  }
}
```

How `available` is computed:
- **Cube:** if `columnIndex % GRID_WIDTH` is in `[20, 29]` → `GRID_HEIGHT - DOOR_HEIGHT` = `45 - 11 = 34`; else 45. So each face has one door spanning local columns 20–29.
- **Cylinder:** if `columnIndex % 30` is in `[10, 19]` → `CYLINDER_HEIGHT - DOOR_HEIGHT` = `43 - 11 = 32`; else 43. So there are 4 doors around the 120 columns (at 10–19, 40–49, 70–79, 100–109).

**Tracing around doors:** when drawing a continuous edge/path, use the last full column before a door to ascend, traverse across the (shortened) door-column tops, and the first full column after the door to descend. The `mcslee` door patterns (`Portals`, `DoorEmanation`) are good references.

## 3D distance across surfaces

For thickness effects that span multiple surfaces, iterate `model.points` and use Euclidean distance in world space:

```java
double dist3D = Math.sqrt(
    Math.pow(p.x - cx, 2) +
    Math.pow(p.y - cy, 2) +
    Math.pow(p.z - cz, 2));
```

Apply a falloff on `dist3D` for soft edges, or a threshold for hard edges.
