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

```bash
# Add the marketplace (one-time)
/plugin marketplace add piemonte/skills

# Install individual skills
/plugin install skills@swift-concurrency
/plugin install skills@sonic-pi
/plugin install skills@te-pattern
```

### Codex

```bash
# Clone the repository
git clone https://github.com/piemonte/skills.git ~/.codex/piemonte-skills

# Create symlinks for the skills you need
ln -s ~/.codex/piemonte-skills/swift-concurrency ~/.agents/skills/swift-concurrency
ln -s ~/.codex/piemonte-skills/sonic-pi ~/.agents/skills/sonic-pi
```

See each skill's [`.codex/INSTALL.md`](.codex/INSTALL.md) for Windows instructions and more details.

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
