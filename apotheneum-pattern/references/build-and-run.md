# Apotheneum Build & Run Reference

## Build & install

| Command | Effect |
|---|---|
| `mvn compile` | Quick compile check |
| `mvn -Pinstall install` | Build the JAR and copy it to `~/Chromatik/Packages` (preferred) |
| `./update.command` | Convenience wrapper around `mvn install` |

Always use `mvn -Pinstall install` when iterating on patterns — it refreshes the package Chromatik loads. Requirements: Java 21+, Maven. The LX libraries (`lx`, `glx`, `glxstudio`, currently version 1.2.1) are `provided`-scope dependencies supplied by the Chromatik runtime.

The `install` profile copies `target/apotheneum-<version>.jar` into `~/Chromatik/Packages/`; Chromatik auto-loads packages from that directory at startup.

## Logging

- Log files: `~/Chromatik/Logs`.
- Log from patterns with `LX.log("message")` / `LX.error(x, "message")`.
- `System.out.println` does **not** appear in Chromatik logs — never rely on it for debugging.

## Running Chromatik for dev verification

Normal workflow: install the JAR and open Chromatik (the licensed desktop app). To launch Chromatik directly from the Maven-resolved jars (e.g. when the app isn't installed but the libraries are in `~/.m2`):

```bash
cd /Users/piemonte/Source/Apotheneum

# Resolve the full provided-scope runtime classpath
mvn -q dependency:build-classpath \
  -DincludeScope=provided \
  -Dmdep.outputFile=/tmp/apoth_cp.txt

# Launch (macOS requires -XstartOnFirstThread for GLFW)
# --accept-eula and the optional project file are PROGRAM args: they go AFTER
# the main class. Placing --accept-eula before -cp makes the JVM reject it
# ("Unrecognized option: --accept-eula").
java -XstartOnFirstThread \
  -cp "$(cat /tmp/apoth_cp.txt)" \
  heronarts.lx.studio.Chromatik --accept-eula
```

Notes:
- Main class: `heronarts.lx.studio.Chromatik`. Renderer is BGFX/Metal on Apple Silicon.
- macOS needs `-XstartOnFirstThread` or GLFW window creation fails.
- The engine is **disabled until the EULA is accepted** — pass `--accept-eula` as a **program arg (after the main class)**, or accept in-app. EULA: <https://chromatik.co/license/>.
- The Apotheneum **model itself is license-gated**: without a developer license the model may not authorize, so `Apotheneum.exists` stays false and patterns render black. Visual testing needs a licensed Chromatik with the model loaded.
- Without a developer license: features are limited and **network output (ArtNet/sACN) is gated** — fine for on-screen simulation, not for driving hardware.
- The Apotheneum package auto-loads from `~/Chromatik/Packages`; confirm via the log line `Loading package content from: …/apotheneum-<version>.jar`.

This direct-launch path is for development/verification only; for real shows use a properly installed, licensed Chromatik.

## Resolving the LX API for reference

The LX framework source isn't in this repo. To inspect the provided API (e.g. exact `GraphicMeter` / `Tempo` / `LXColor` signatures when adding audio):

```bash
mvn -q dependency:build-classpath -DincludeScope=provided -Dmdep.outputFile=/tmp/apoth_cp.txt
# then inspect the lx jar, e.g.:
unzip -l "$(tr ':' '\n' < /tmp/apoth_cp.txt | grep '/lx-')"
```
