# skills

My public collection of agentic skills for creative coding and development.

Each skill is a self-contained directory with a `SKILL.md` entry point, installable in both [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://openai.com/index/introducing-codex/).

## Apple Platform Engineering

Focused skills for building production-quality software on Apple platforms — Swift 6, SwiftUI, Metal, RealityKit, and visionOS.

| Skill | Description |
|-------|-------------|
| [`swift-concurrency`](swift-concurrency/) | Actors, Sendable, AsyncSequence, task cancellation, synchronization, state machines, and strict concurrency |
| [`swiftui-architecture`](swiftui-architecture/) | MVVM architecture, ViewModel/View guidelines, service layer patterns, state management, and App Intents |
| [`metal-graphics`](metal-graphics/) | Compute and render pipelines, buffer management, textures, compute dispatch, ring buffers, and shaders |
| [`realitykit-visionos`](realitykit-visionos/) | Entity-component-system architecture, custom Systems, immersive spaces, hand tracking, and multi-window scenes |
| [`advanced-swift-patterns`](advanced-swift-patterns/) | Property wrappers, interpolation/animation primitives, custom collections, Combine bridging, and async abstractions |

## Lighting — Chromatix / LXStudio-TE

Skills for the [LXStudio-TE](https://github.com/titanicsend/LXStudio-TE) codebase, the LED art vehicle platform powering [Titanic's End](https://www.titanicsend.com) and adaptable vehicles like Mothership. These cover Java pattern development, GLSL GPU shaders, 3D vehicle model definition, show file configuration, and end-to-end vehicle bootstrapping.

| Skill | Description |
|-------|-------------|
| [`te-pattern`](te-pattern/) | Java LED pattern development — TEPerformancePattern, audio reactivity, color system, and variable-speed time |
| [`te-shader`](te-shader/) | GLSL shader development — uniform reference, pragma system, audio textures, and auto-registration |
| [`te-model`](te-model/) | Vehicle model definition — vertex/edge/panel file formats, DMX addressing, and Java model classes |
| [`te-show`](te-show/) | Show file configuration — .lxp JSON structure, channel setup, and view definitions |
| [`te-vehicle-bootstrap`](te-vehicle-bootstrap/) | End-to-end vehicle bootstrapping — geometry, fixtures, show files, test patterns, and troubleshooting |

## Live Music Coding

Skills for live coding music and algorithmic composition with [Sonic Pi](https://sonic-pi.net) and [Strudel](https://strudel.cc).

| Skill | Description |
|-------|-------------|
| [`sonic-pi`](sonic-pi/) | Synthesis, samples, live_loop, FX chains, MIDI/OSC, rings, sequencing, and performance techniques |
| [`strudel`](strudel/) | Browser-based algorithmic music — mini-notation, pattern transformation, synths, samples, effects, scales, and MIDI/OSC |

## Developer Tools

| Skill | Description |
|-------|-------------|
| [`github`](github/) | Interact with GitHub using the `gh` CLI — issues, PRs, CI runs, workflow debugging, and API queries |

## Installation

Each skill is independently installable. Choose the platform that matches your environment.

### Claude Code (via Plugin Marketplace)

Add the marketplace once, then install the skills you want.

```bash
/plugin marketplace add piemonte/skills
```

| Skill | Install command |
|-------|-----------------|
| `swift-concurrency` | `/plugin install skills@swift-concurrency` |
| `swiftui-architecture` | `/plugin install skills@swiftui-architecture` |
| `metal-graphics` | `/plugin install skills@metal-graphics` |
| `realitykit-visionos` | `/plugin install skills@realitykit-visionos` |
| `advanced-swift-patterns` | `/plugin install skills@advanced-swift-patterns` |
| `te-pattern` | `/plugin install skills@te-pattern` |
| `te-shader` | `/plugin install skills@te-shader` |
| `te-model` | `/plugin install skills@te-model` |
| `te-show` | `/plugin install skills@te-show` |
| `te-vehicle-bootstrap` | `/plugin install skills@te-vehicle-bootstrap` |
| `sonic-pi` | `/plugin install skills@sonic-pi` |
| `strudel` | `/plugin install skills@strudel` |
| `github` | `/plugin install skills@github` |

### Codex

Clone once, then symlink the skills you want.

```bash
git clone https://github.com/piemonte/skills.git ~/.codex/piemonte-skills
mkdir -p ~/.agents/skills
```

| Skill | Install command |
|-------|-----------------|
| `swift-concurrency` | `ln -s ~/.codex/piemonte-skills/swift-concurrency ~/.agents/skills/swift-concurrency` |
| `swiftui-architecture` | `ln -s ~/.codex/piemonte-skills/swiftui-architecture ~/.agents/skills/swiftui-architecture` |
| `metal-graphics` | `ln -s ~/.codex/piemonte-skills/metal-graphics ~/.agents/skills/metal-graphics` |
| `realitykit-visionos` | `ln -s ~/.codex/piemonte-skills/realitykit-visionos ~/.agents/skills/realitykit-visionos` |
| `advanced-swift-patterns` | `ln -s ~/.codex/piemonte-skills/advanced-swift-patterns ~/.agents/skills/advanced-swift-patterns` |
| `te-pattern` | `ln -s ~/.codex/piemonte-skills/te-pattern ~/.agents/skills/te-pattern` |
| `te-shader` | `ln -s ~/.codex/piemonte-skills/te-shader ~/.agents/skills/te-shader` |
| `te-model` | `ln -s ~/.codex/piemonte-skills/te-model ~/.agents/skills/te-model` |
| `te-show` | `ln -s ~/.codex/piemonte-skills/te-show ~/.agents/skills/te-show` |
| `te-vehicle-bootstrap` | `ln -s ~/.codex/piemonte-skills/te-vehicle-bootstrap ~/.agents/skills/te-vehicle-bootstrap` |
| `sonic-pi` | `ln -s ~/.codex/piemonte-skills/sonic-pi ~/.agents/skills/sonic-pi` |
| `strudel` | `ln -s ~/.codex/piemonte-skills/strudel ~/.agents/skills/strudel` |
| `github` | `ln -s ~/.codex/piemonte-skills/github ~/.agents/skills/github` |

See each skill's `.codex/INSTALL.md` (e.g. [`swift-concurrency/.codex/INSTALL.md`](swift-concurrency/.codex/INSTALL.md)) for Windows instructions.

### Cursor (via Plugin Marketplace)

```text
/plugin install piemonte/skills
```

### Verify Installation

Ask your AI assistant:

> "What concurrency primitive should I use for a shared stateful component in Swift?"

It should recommend using an `actor` — referencing the swift-concurrency skill.

## Updating

**Claude Code / Cursor:**

```bash
/plugin update skills
```

**Codex:**

```bash
cd ~/.codex/piemonte-skills && git pull
```

## Adding a New Skill

1. Create a directory with a `SKILL.md` (YAML frontmatter: `name`, `description`)
2. Add `.claude-plugin/plugin.json` and `.codex/INSTALL.md` for cross-AI support
3. Run `python3 scripts/build_skills_index.py` to regenerate `skills.json`

## License

MIT
