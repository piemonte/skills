---
name: strudel
description: Use when live coding music with Strudel — pattern-based algorithmic music in the browser using mini-notation, synths, samples, effects, scales, MIDI/OSC, and Euclidean rhythms.
---

# Strudel Live Coding Reference

Comprehensive reference for Strudel (v1.2), a browser-based live coding environment for algorithmic music. JavaScript port of TidalCycles, runs entirely in the browser at [strudel.cc](https://strudel.cc) with no installation required.

## Core Concepts

1. **Patterns, not sequences** — code generates repeating time patterns, not linear note lists.
2. **Cycles, not bars** — default 0.5 CPS (1 cycle = 2 seconds). Use `setcps()` or `setcpm()` to change tempo.
3. **Mini-notation** — rhythm/timing syntax inside quoted strings: `"bd sd hh oh"`.
4. **Method chaining** — functions chain left to right: `note("c3 e3").sound("piano").lpf(800)`.
5. **Orbits** — patterns on the same orbit share delay/reverb. Default orbit is 1.
6. **Hot-reload** — edit code while it plays; changes take effect on the next cycle.

## Mini-Notation

The pattern language used inside quoted strings.

### Basics

| Syntax | Meaning | Example |
|--------|---------|---------|
| Space | Sequence events in one cycle | `"bd sd hh oh"` |
| `~` or `-` | Rest (silence) | `"bd ~ sd ~"` |
| `*N` | Speed up / repeat N times | `"hh*8"` = 8 hi-hats per cycle |
| `/N` | Slow down over N cycles | `"bd/2"` = kick every 2 cycles |
| `<a b c>` | One per cycle, rotate | `"<bd sd cp>"` |
| `[a b]` | Subdivide time | `"[bd bd] sd"` = 2 kicks + 1 snare |
| `,` | Play simultaneously (stack) | `"bd, hh*8"` |
| `@N` | Elongate (weight) | `"bd@3 sd"` = kick takes 3/4 of cycle |
| `!N` | Replicate without speeding | `"bd!3 sd"` = 3 kicks + snare, evenly spaced |
| `:N` | Sample variant | `"bd:3"` = 4th variant of bass drum |
| `?` or `?0.N` | Random skip | `"hh*8?0.3"` = 30% chance each hh is silent |
| `(p,s)` | Euclidean rhythm | `"bd(3,8)"` = 3 hits spread over 8 steps |
| `(p,s,o)` | Euclidean with offset | `"bd(3,8,2)"` |

### Nesting

Brackets nest arbitrarily deep for complex subdivisions:

```
"[bd [sd sd]] hh [oh [hh hh hh]]"
```

### Chords in Mini-Notation

```
"[c3,e3,g3] [d3,f3,a3]"    // two chords per cycle
```

## Pattern Constructors

| Function | Purpose | Example |
|----------|---------|---------|
| `cat(a, b, c)` | Sequence, 1 cycle each | `cat("bd sd", "hh hh hh")` |
| `seq(a, b, c)` | Sequence, all in 1 cycle | `seq("bd sd", "hh hh hh")` |
| `stack(a, b)` | Play simultaneously | `stack(s("bd*4"), s("hh*8"))` |
| `silence` | Empty pattern | — |
| `run(N)` | Numbers 0 to N-1 | `run(8)` = 0 1 2 3 4 5 6 7 |
| `arrange(...)` | Cycle-range sections | `arrange([4, "bd sd"], [2, "hh*8"])` |

## Sound Sources

### Triggering Samples

```
s("bd sd hh oh")              // short form
sound("bd sd hh oh")          // long form
```

### Built-in Drum Abbreviations

| Name | Sound |
|------|-------|
| `bd` | Bass drum (kick) |
| `sd` | Snare drum |
| `hh` | Closed hi-hat |
| `oh` | Open hi-hat |
| `cp` | Clap |
| `cr` | Crash cymbal |
| `sh` | Shaker |
| `cb` | Cowbell |
| `tb` | Tambourine |
| `rim` | Rim click |

Variants via `:N` — `"bd:0 bd:1 bd:2 bd:3"` cycles through different kicks.

### Drum Machine Banks

```
s("bd sd hh oh").bank("RolandTR808")
s("bd sd hh oh").bank("RolandTR909")
```

### Synth Oscillators

```
note("c3 e3 g3").sound("sine")
note("c3 e3 g3").sound("sawtooth")
note("c3 e3 g3").sound("square")
note("c3 e3 g3").sound("triangle")
```

Noise types: `white`, `pink`, `brown`

### Sample Manipulation

| Opt | Effect |
|-----|--------|
| `begin(0-1)` / `end(0-1)` | Trim playback region |
| `speed(N)` | Playback rate (negative = reverse) |
| `loopAt(N)` | Fit sample to N cycles |
| `chop(N)` | Granular: cut into N pieces |
| `slice(N)` | Divide into N segments |
| `cut(group)` | Stop previous sample in same cut group |

### Loading Custom Samples

```
samples('github:user/repo')                     // from GitHub
samples({ name: 'https://url/to/file.wav' })    // direct URL
```

## Synths and Synthesis

### FM Synthesis

```
note("c3 e3 g3")
  .sound("sine")
  .fmh(2)               // harmonicity ratio (integer = tonal, decimal = metallic)
  .fmenv(4)              // modulation envelope
  .fmdecay(0.2)          // modulation decay
```

### Wavetable Synthesis

Over 1000 waveforms from the AKWF library via `wt_` prefix:

```
note("c3 e3 g3").sound("wt_piano")
```

### Additive Synthesis

```
note("c3").sound("sine")
  .partials("0.5 0.3 0.1")    // harmonic magnitudes
```

### Vibrato

```
note("c4").sound("sine").vib(4).vibmod(0.5)
```

## Notes, Scales, and Chords

### Note Formats

```
note("c3 e3 g3 c4")           // letter notation (sharps: c#3, flats: eb3)
note("48 52 55 60")            // MIDI numbers (decimals for microtonal)
freq("261 329 392 523")        // frequency in Hz
```

### Scales

Numbers become scale degrees (zero-indexed). Any number "should sound good":

```
note("0 2 4 6 3 1 5 7").scale("C:major")
note("0 1 2 3 4 5 6 7").scale("A:minor:pentatonic")
```

Common scales: `major`, `minor`, `dorian`, `mixolydian`, `lydian`, `phrygian`, `locrian`, `major:pentatonic`, `minor:pentatonic`, `blues`, `chromatic`, `whole:tone`, `harmonic:minor`, `melodic:minor`

### Transposition

```
note("0 2 4").scale("C:major").add("<0 1 2 3>")    // transpose by scale degrees
note("c3 e3").transpose(7)                           // transpose by semitones
note("0 2 4").scale("C:major").scaleTranspose(2)     // move within scale
```

### Chords and Voicings

```
chord("Am C F G")                                    // chord symbols
chord("Am C F G").voicing()                          // smart voice leading
note("<Am C F G>").voicing().sound("piano")          // idiomatic usage
```

Voicing modes: `below` (default), `above`, `duck`, `root`

Extract bass notes: `.rootNotes(2)` (octave 2)

## Tempo

```
setcps(0.5)              // cycles per second (default)
setcpm(30)               // cycles per minute (default)
```

### Converting from BPM

```
// BPM / beats per cycle = CPM
setcpm(120 / 4)          // 120 BPM with 4 beats per cycle = 30 CPM
```

## Time Modifiers

| Function | Effect | Example |
|----------|--------|---------|
| `fast(N)` | Speed up by N | `.fast(2)` = double speed |
| `slow(N)` | Slow down by N | `.slow(2)` = half speed |
| `early(N)` | Shift earlier | `.early(0.25)` |
| `late(N)` | Shift later | `.late(0.25)` |
| `rev()` | Reverse pattern | `.rev()` |
| `palindrome()` | Alternate forward/backward | `.palindrome()` |
| `iter(N)` | Rotate subdivisions each cycle | `.iter(4)` |
| `ply(N)` | Repeat each event N times | `.ply(2)` |
| `swingBy(amt, div)` | Add swing | `.swingBy(1/6, 4)` |

## Euclidean Rhythms

```
s("bd").euclid(3, 8)              // 3 hits over 8 steps (Cuban tresillo)
s("hh").euclid(5, 8)             // 5 over 8 (rumba)
s("cp").euclid(7, 16)            // 7 over 16
```

Also available in mini-notation: `"bd(3,8)"`, `"hh(5,8,2)"` (with offset).

## Effects

### Filters

| Function | Purpose | Example |
|----------|---------|---------|
| `lpf(freq)` / `lowpass(freq)` | Low pass filter | `.lpf(800)` |
| `hpf(freq)` / `highpass(freq)` | High pass filter | `.hpf(200)` |
| `bandpass(freq)` | Band pass filter | `.bandpass(1000)` |
| `lpenv(a, d, s, r)` | Filter envelope (LP) | `.lpf(2000).lpenv(0.01, 0.2, 0, 0)` |
| `hpenv(a, d, s, r)` | Filter envelope (HP) | `.hpf(200).hpenv(...)` |

Resonance: `.lpf(800).lpq(10)` (or `.resonance(10)`)

### Distortion

| Function | Purpose |
|----------|---------|
| `distort(amount)` | Harmonic distortion |
| `crush(bits)` | Bit-crush |
| `shape(amount)` | Waveshaper |

### Spatial

| Function | Purpose | Example |
|----------|---------|---------|
| `pan(0-1)` | Stereo position (0=L, 0.5=center, 1=R) | `.pan(sine)` |
| `jux(fn)` | Apply fn to right channel only | `.jux(rev)` |
| `delay(time, feedback, wet)` | Echo | `.delay(0.5, 0.6, 0.3)` |
| `room(size)` | Reverb room size | `.room(0.8)` |
| `dry(amount)` | Dry/wet mix | `.dry(0.5)` |

### Modulation

| Function | Purpose |
|----------|---------|
| `tremolo(rate, depth)` | Amplitude modulation |
| `phaser(rate, depth)` | Phaser effect |
| `vibrato(rate, depth)` | Pitch modulation |

### Amplitude

| Function | Purpose |
|----------|---------|
| `gain(0-1)` | Volume control |
| `velocity(0-1)` | Multiplied with gain |
| `env(adsrPattern)` | ADSR amplitude envelope |
| `attack`, `decay`, `sustain`, `release` | Individual ADSR components |

### Ducking / Sidechain

```
s("bd*4").orbit(0)
note("c2 c2 c2 c2").sound("sawtooth").orbit(1).duckorbit(0)
```

## Pattern Transformation

### Layering and Offset

```
// Copy pattern, shift in time, and transform
note("0 [4 3]").scale("C:minor")
  .off(1/8, x => x.add(4))          // offset + transpose copy
  .off(1/4, x => x.add(7))          // another layer
```

### Conditional Modifiers

| Function | Probability | Example |
|----------|-------------|---------|
| `sometimes(fn)` | 50% | `.sometimes(rev)` |
| `often(fn)` | 75% | `.often(x => x.add(12))` |
| `rarely(fn)` | 25% | `.rarely(x => x.crush(4))` |
| `almostAlways(fn)` | 90% | — |
| `almostNever(fn)` | 10% | — |
| `sometimesBy(p, fn)` | custom | `.sometimesBy(0.3, rev)` |
| `someCyclesBy(p, fn)` | per-cycle | `.someCyclesBy(0.5, fast(2))` |

### Degradation

```
s("hh*16").degradeBy(0.5)      // randomly remove 50% of events
s("hh*16").degrade()            // shortcut for 50%
```

### Structure

```
s("hh").struct("1 0 1 1 0 1 0 1")     // apply binary rhythm
s("bd sd").mask("1 1 0 1")             // silence where mask = 0
```

### Arithmetic

| Function | Purpose | Example |
|----------|---------|---------|
| `add(N)` | Add / transpose | `.add("<0 3 5 7>")` |
| `sub(N)` | Subtract | `.sub(2)` |
| `mul(N)` | Multiply | `.mul(2)` |
| `div(N)` | Divide | `.div(2)` |

### Selection

```
pick(["bd sd", "hh oh", "cp cr"], "0 1 2 1")    // select by index
```

## MIDI

### Sending MIDI Out

```
note("c3 e3 g3 c4").midi()         // send to default MIDI output
note("c3 e3 g3").midi().channel(2)  // specific channel (1-16)
```

### Receiving MIDI In

```
// MIDI keyboard input
midikeys().sound("piano")

// MIDI CC input
midin(1).range(200, 2000)           // CC 1 mapped to range
```

### MIDI Mapping

Custom CC mappings: `midimaps({ cutoff: 74, resonance: 71 })`

## OSC

```
note("c3 e3 g3").osc()             // send as OSC to SuperCollider/SuperDirt
```

Requires SuperCollider + SuperDirt running locally.

## Visualization

Built-in inline visualizations:

```
note("0 2 4 6").scale("C:major").pianoroll()
s("bd sd hh oh").punchcard()
note("c3").scope()
```

## Idioms and Patterns

### Minimal Techno

```
stack(
  s("bd*4"),
  s("~ cp").delay(0.5, 0.4, 0.3),
  s("hh*8").gain(0.6).sometimes(x => x.speed(2)),
  note("c2 ~ c2 ~").sound("sawtooth").lpf("<800 400 1200 600>").decay(0.1).sustain(0)
).setcpm(132/4)
```

### Ambient

```
stack(
  note("<Am C F G>").voicing().sound("sine")
    .release(4).room(0.9).delay(0.5, 0.7, 0.4),
  note("0 2 4 7").scale("A:minor").slow(2).sound("triangle")
    .gain(0.3).room(0.9)
).setcpm(60/4)
```

### Drum & Bass

```
stack(
  s("[bd ~ bd ~] [~ sd ~ sd]").fast(2),
  s("hh*16").gain("0.8 0.4").sometimes(x => x.speed(1.5)),
  note("[c2 ~ c2 c2] [~ c2 ~ ~]").sound("sawtooth").lpf(600).fast(2)
).setcpm(170/4)
```

### Euclidean Polyrhythm

```
stack(
  s("bd").euclid(3, 8),
  s("sd").euclid(5, 8).gain(0.7),
  s("hh").euclid(7, 16).gain(0.5),
  s("cp").euclid(2, 8).delay(0.25, 0.5, 0.3)
)
```

### Generative Melody

```
note("0 1 2 3 4 5 6 7")
  .scale("C:minor:pentatonic")
  .sound("sine")
  .sometimesBy(0.3, x => x.add(7))
  .sometimesBy(0.2, x => x.rev())
  .off(1/8, x => x.add(12).gain(0.4))
  .room(0.5)
  .delay(0.25, 0.4, 0.3)
```

## Strudel vs Sonic Pi

| Aspect | Strudel | Sonic Pi |
|--------|---------|----------|
| Language | JavaScript | Ruby |
| Runs in | Browser (no install) | Desktop app |
| Time model | Cycles (CPS) | Beats (BPM) |
| Core abstraction | Pattern transformation | live_loop + sleep |
| Rhythm notation | Mini-notation strings | Rings + tick/look |
| Audio engine | Web Audio API | SuperCollider (scsynth) |
| Euclidean rhythms | `euclid(3,8)` or `"bd(3,8)"` | `spread(3,8)` ring |
| FX | Method chain | `with_fx` blocks |
| MIDI | `.midi()` | `midi_note_on` / `midi` |
| Randomness | `sometimes`, `degrade`, `choose` | `one_in`, `choose`, seeds |
| Collaboration | Multi-user via Flok | Single-user |
