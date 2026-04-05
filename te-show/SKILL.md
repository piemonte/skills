---
name: te-show
description: Use when configuring show files for LXStudio-TE — .lxp JSON structure, channel setup, view definitions, and project naming conventions.
---

# TE Show File Configuration

Show files (`.lxp`) define the complete runtime state of an LXStudio-TE session — patterns, channels, effects, views, and parameter values. This reference covers the file format, configuration workflow, and project conventions.

## File Location

All show files live in `te-app/Projects/`:

```
te-app/Projects/
├── BootupTemplate.lxp          # Default startup template
├── BM25_TE_8channel.lxp        # Burning Man 2025, 8-channel
├── CoachellaMaster.lxp         # Coachella show
├── MothershipTest.lxp          # Mothership vehicle test
├── MShipStartupLooks.lxp       # Mothership startup looks
├── DJLights.lxp                # DJ lights only
├── PanelCalibration.lxp        # Panel calibration utility
├── Shader3DTest.lxp            # Shader 3D testing
├── Archive/                    # Older show files (~30 files)
└── Grids/                      # Grid resolution presets
    ├── 1024x1024.lxp
    ├── 1280x240.lxp
    └── 1280x720.lxp
```

## .lxp JSON Structure

An `.lxp` file is a JSON document with this top-level structure:

```json
{
  "version": "1.0.1.TE.2-SNAPSHOT",
  "timestamp": 1709000000000,
  "model": { ... },
  "engine": { ... },
  "externals": { ... }
}
```

### Top-Level Keys

| Key | Description |
|-----|-------------|
| `version` | LX engine version string |
| `timestamp` | Unix timestamp (milliseconds) of last save |
| `model` | Vehicle model structure configuration |
| `engine` | Pattern engine state (channels, effects, tempo) |
| `externals` | External integrations (MIDI, OSC, DMX output) |

### Model Section

```json
{
  "model": {
    "id": 2,
    "class": "heronarts.lx.structure.LXStructure",
    "internal": {
      "modulationColor": 0,
      "modulationControlsExpanded": true,
      "modulationsExpanded": true,
      "showNormalizationBounds": false
    },
    "parameters": {
      "label": "LX",
      "syncModelFile": false,
      "allWhite": false,
      "mute": false,
      "normalizationMode": 0,
      "normalizationX": 0.0,
      "normalizationY": 0.0,
      "normalizationZ": 0.0,
      "normalizationWidth": 1.0,
      "normalizationHeight": 1.0,
      "normalizationDepth": 1.0
    },
    "children": {
      "views": {
        "class": "heronarts.lx.structure.view.LXViewEngine",
        "views": [
          {
            "class": "heronarts.lx.structure.view.LXViewDefinition",
            "parameters": {
              "label": "Fixtures",
              "enabled": true,
              "selector": "912;983;9114;...",
              "normalization": 2,
              "priority": false
            }
          }
        ]
      }
    }
  }
}
```

### Views in .lxp vs views.txt

Views defined in `te-app/resources/vehicle/views.txt` are loaded at model initialization. The `.lxp` file can override or extend these with additional view definitions. The `selector` field in both uses the same syntax:

- Numeric IDs: `912;983;9114` (component fixture IDs)
- Special selectors: `Edge`, `Panel`
- Named sections: `fore;aft;starboard-fore;port-aft`
- Edge ranges: `11-98,98-99,99-101`

### Engine Section

The engine section contains the complete runtime state:

```json
{
  "engine": {
    "channels": [
      {
        "label": "Channel-1",
        "patterns": [
          {
            "class": "titanicsend.pattern.piemonte.Afterglow",
            "parameters": {
              "te_speed": 0.5,
              "te_size": 5.0,
              "te_quantity": 0.3
            }
          }
        ],
        "effects": [...],
        "blendMode": 0,
        "fader": 1.0
      }
    ],
    "tempo": {
      "bpm": 120.0,
      "tap": false,
      "nudgeUp": false,
      "nudgeDown": false
    },
    "mixer": { ... },
    "modulation": { ... }
  }
}
```

Key engine sub-sections:

| Section | Description |
|---------|-------------|
| `channels` | Array of mixing channels, each with patterns and effects |
| `tempo` | BPM and tap-tempo state |
| `mixer` | Cross-fader and blend settings |
| `modulation` | LFOs, envelopes, and parameter mappings |
| `audio` | Audio input configuration |
| `output` | DMX/network output settings |

## Starting a New Show

### From BootupTemplate.lxp

The recommended starting point for a new show:

1. Open LXStudio-TE
2. Load `BootupTemplate.lxp` from the Projects menu
3. Add channels and assign patterns
4. Configure views for your target fixture groups
5. Save As with a descriptive name

### From Scratch

1. Create a minimal `.lxp` with the required top-level keys
2. The model section will auto-populate from `te-app/resources/vehicle/` files
3. Add channels programmatically or through the UI

### Naming Convention

Show files follow the pattern:

```
[Event][Year]_[Vehicle]_[Config].lxp
```

Examples:
- `BM25_TE_8channel.lxp` — Burning Man 2025, Titanic's End, 8 channels
- `BM2024_Mship.lxp` — Burning Man 2024, Mothership
- `CoachellaMaster.lxp` — Coachella master show

## Channel Configuration

Each channel in the `channels` array holds:

```json
{
  "label": "Channel-1",
  "enabled": true,
  "fader": 1.0,
  "blendMode": 0,
  "crossfadeGroup": 0,
  "patterns": [
    {
      "class": "titanicsend.pattern.piemonte.Afterglow",
      "parameters": {
        "label": "Afterglow",
        "te_speed": 0.5,
        "te_size": 5.0,
        "te_quantity": 0.3,
        "te_wow1": 0.7,
        "te_brightness": 1.0
      }
    }
  ],
  "effects": [
    {
      "class": "heronarts.lx.effect.BlurEffect",
      "parameters": {
        "amount": 0.5
      }
    }
  ]
}
```

### Blend Modes

| Value | Mode |
|-------|------|
| 0 | Normal (replace) |
| 1 | Add |
| 2 | Multiply |
| 3 | Highlight |
| 4 | Subtract |

### Pattern Parameters

Pattern parameters in the JSON use the `path` value from `TEControlTag`:

| JSON Key | Control | Default |
|----------|---------|---------|
| `te_speed` | Speed | 0.5 |
| `te_xpos` | X Position | 0.0 |
| `te_ypos` | Y Position | 0.0 |
| `te_size` | Size | 1.0 |
| `te_quantity` | Quantity | 0.5 |
| `te_spin` | Spin | 0.0 |
| `te_brightness` | Brightness | 1.0 |
| `te_wow1` | Wow1 | 0.0 |
| `te_wow2` | Wow2 | 0.0 |
| `te_wowtrigger` | WowTrigger | false |
| `te_angle` | Angle | 0.0 |
| `te_level` | LvlReact | 0.1 |
| `te_freq` | FreqReact | 0.1 |
| `te_twist` | Twist | false |

## View Configuration

Views control which fixtures a pattern renders to. Defined in `views.txt` and optionally overridden in `.lxp`.

### Built-in Views

| View | Description |
|------|-------------|
| Fixtures | All LED fixtures (edges + panels) |
| Edges | All edge strips only |
| Panels | All panel surfaces only |
| Panel Sections | Grouped by vehicle section (fore, aft, starboard, port) |
| Outline | Front/back silhouette edges |
| Outline DJ | Ground-level DJ area edges |

### Panel Sections

Available section selectors for `Panel Sections` view:

- `fore` — Front panels (FA, FB, FSA-FSC, FPA-FPC)
- `aft` — Rear panels (AA, AB, ASA-ASC, APA-APC)
- `starboard-fore` — Right front panels
- `starboard-aft` — Right rear panels
- `port-fore` — Left front panels
- `port-aft` — Left rear panels
- `starboard-fore-single` — Right front, individually normalized
- `starboard-aft-single` — Right rear, individually normalized
- `port-fore-single` — Left front, individually normalized
- `port-aft-single` — Left rear, individually normalized

## Archive Conventions

- Move superseded show files to `Projects/Archive/`
- Keep active show files in the root `Projects/` directory
- `Grids/` contains resolution-specific test configurations
- The `Autosave/` directory is managed automatically by LXStudio

## Troubleshooting

### Show file won't load
- Verify the `version` string matches the current LX engine version
- Check for JSON syntax errors (trailing commas, missing quotes)
- Ensure all referenced pattern classes exist in the classpath

### Patterns not appearing
- Verify the full class path in the `class` field (e.g., `titanicsend.pattern.piemonte.Afterglow`)
- Check that the pattern is registered in the LX registry
- Confirm parameter paths match `TEControlTag` values

### Views not working
- View selectors must match fixture component IDs exactly
- Section names are case-sensitive
- Semicolons in view labels enable relative normalization per fixture
