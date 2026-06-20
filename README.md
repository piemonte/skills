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

Skills for the [LXStudio-TE](https://github.com/titanicsend/LXStudio-TE) codebase, the LED art vehicle platform powering [Titanic's End](https://www.titanicsend.com) and adaptable vehicles like Mothership. These cover Java pattern development, GLSL GPU shaders, and show file configuration.

| Skill | Description |
|-------|-------------|
| [`te-pattern`](te-pattern/) | Java LED pattern development — TEPerformancePattern, audio reactivity, color system, and variable-speed time |
| [`te-shader`](te-shader/) | GLSL shader development — uniform reference, pragma system, audio textures, and auto-registration |
| [`te-show`](te-show/) | Show file configuration — .lxp JSON structure, channel setup, and view definitions |

## Lighting — Apotheneum

Skill for the [Apotheneum](https://github.com/Apotheneum/Apotheneum) installation (cube + cylinder) on Chromatik.

| Skill | Description |
|-------|-------------|
| [`apotheneum-pattern`](apotheneum-pattern/) | Apotheneum LED pattern development — cube/cylinder geometry, doors, copy/mirror utilities, layers, MIDI, optional audio, and macro-knob control |

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

## Thinking & Ideation

| Skill | Description |
|-------|-------------|
| [`idea-framing`](idea-framing/) | Frame a concept using a five-section template — Concept, Problem, Why interesting, State of the art, Solution; supports guided Q&A, structuring a dump, or critiquing a draft |

## Installation

Each skill is independently installable. Choose the platform that matches your environment.

### Claude Code (via Plugin Marketplace)

Add the marketplace once, then install the skills you want.

```bash
/plugin marketplace add piemonte/skills
```

| Skill | Install command |
|-------|-----------------|
| `swift-concurrency` | `/plugin install swift-concurrency@skills` |
| `swiftui-architecture` | `/plugin install swiftui-architecture@skills` |
| `metal-graphics` | `/plugin install metal-graphics@skills` |
| `realitykit-visionos` | `/plugin install realitykit-visionos@skills` |
| `advanced-swift-patterns` | `/plugin install advanced-swift-patterns@skills` |
| `te-pattern` | `/plugin install te-pattern@skills` |
| `te-shader` | `/plugin install te-shader@skills` |
| `te-show` | `/plugin install te-show@skills` |
| `apotheneum-pattern` | `/plugin install apotheneum-pattern@skills` |
| `sonic-pi` | `/plugin install sonic-pi@skills` |
| `strudel` | `/plugin install strudel@skills` |
| `github` | `/plugin install github@skills` |
| `idea-framing` | `/plugin install idea-framing@skills` |

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
| `te-show` | `ln -s ~/.codex/piemonte-skills/te-show ~/.agents/skills/te-show` |
| `apotheneum-pattern` | `ln -s ~/.codex/piemonte-skills/apotheneum-pattern ~/.agents/skills/apotheneum-pattern` |
| `sonic-pi` | `ln -s ~/.codex/piemonte-skills/sonic-pi ~/.agents/skills/sonic-pi` |
| `strudel` | `ln -s ~/.codex/piemonte-skills/strudel ~/.agents/skills/strudel` |
| `github` | `ln -s ~/.codex/piemonte-skills/github ~/.agents/skills/github` |
| `idea-framing` | `ln -s ~/.codex/piemonte-skills/idea-framing ~/.agents/skills/idea-framing` |

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
