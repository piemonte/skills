---
name: sonic-pi
description: Use when live coding music with Sonic Pi — synthesis, samples, live_loop, FX chains, MIDI/OSC, rings, sequencing, and performance techniques.
---

# Sonic Pi Live Coding Reference

Comprehensive reference for Sonic Pi (v4.6), a code-based music creation and live performance tool built on SuperCollider.

## Core Concepts

1. **Everything is beats** — `sleep`, envelope times, and `phase:` opts are all in beats, scaled by BPM.
2. **live_loop is the foundation** — One `live_loop` per musical element. Must contain `sleep`.
3. **Rings wrap around** — `(ring 1,2,3)[5]` returns element at index `5 % 3 = 2`. Use `.tick` and `.look` to step through them.
4. **Deterministic randomness** — Same `use_random_seed` produces identical sequences every run.
5. **FX wrap blocks** — `with_fx :reverb do ... end`. FX apply to everything inside the block.
6. **Control running synths** — Capture nodes with `sn = synth :prophet, ...` then `control sn, cutoff: 130`.

## Quick Reference: Synths

| Synth | Character | Key Params |
|-------|-----------|------------|
| `:beep` / `:sine` | Pure sine wave | — |
| `:saw` | Bright saw wave | `cutoff` |
| `:square` | Hollow square | `cutoff` |
| `:pulse` | Variable pulse | `cutoff`, `pulse_width` |
| `:tri` | Soft triangle | `cutoff`, `pulse_width` |
| `:dsaw` | Detuned saw (thick) | `cutoff`, `detune` |
| `:dpulse` | Detuned pulse | `cutoff`, `detune`, `pulse_width` |
| `:dtri` | Detuned triangle | `cutoff`, `detune` |
| `:supersaw` | Trancy supersaw | `cutoff`, `res` |
| `:tb303` | Acid bass (303) | `cutoff`, `cutoff_min`, `res`, `wave`, `pulse_width`, cutoff ADSR |
| `:hoover` | 90s rave stab | `cutoff`, `res` |
| `:prophet` | Dark PWM pad | `cutoff`, `res` |
| `:blade` | Blade Runner strings | `cutoff`, `vibrato_rate`, `vibrato_depth`, `vibrato_delay` |
| `:hollow` | Breathy pad | `cutoff`, `res`, `noise`, `norm` |
| `:dark_ambience` | Slow rolling bass | `cutoff`, `res`, `detune1`, `detune2`, `noise`, `ring`, `room` |
| `:growl` | Deep rumble | `cutoff`, `res` |
| `:zawa` | Oscillating timbre | `cutoff`, `res`, `phase`, `wave`, `range` |
| `:fm` | FM synthesis | `cutoff`, `divisor`, `depth` |
| `:pluck` | Karplus-Strong string | `noise_amp`, `pluck_decay`, `coef` |
| `:piano` | Basic piano | `vel`, `hard`, `stereo_width` |
| `:rhodey` | 60s/70s electric piano | — |
| `:gabberkick` | Gabber kick | — |
| `:noise` | White noise | `cutoff`, `res` |
| `:pnoise` | Pink noise (-3dB/oct) | `cutoff`, `res` |
| `:bnoise` | Brown noise (-6dB/oct) | `cutoff`, `res` |

### 808 Percussive Synths (v4.5+)

`:sc808_bassdrum`, `:sc808_snare`, `:sc808_clap`, `:sc808_tomlo`, `:sc808_tommid`, `:sc808_tomhi`, `:sc808_congalo`, `:sc808_congamid`, `:sc808_congahi`, `:sc808_rimshot`, `:sc808_claves`, `:sc808_maracas`, `:sc808_cowbell`, `:sc808_closed_hihat`, `:sc808_open_hihat`, `:sc808_cymbal`

### Common Synth Parameters

All synths accept: `note`, `amp`, `pan`, `attack`, `decay`, `sustain`, `release`, `attack_level`, `decay_level`, `sustain_level`, `env_curve`

## Quick Reference: FX

| FX | Purpose | Key Params |
|----|---------|------------|
| `:reverb` | Standard reverb | `room` (0-1), `damp` (0-1) |
| `:gverb` | Spacious reverb | `spread`, `damp`, `room` (m^2), `release` |
| `:echo` | Delay/echo | `phase`, `decay`, `max_phase` |
| `:distortion` | Raw crunch | `distort` |
| `:bitcrusher` | Lo-fi | `sample_rate`, `bits`, `cutoff` |
| `:krush` | Krush effect | `gain`, `cutoff`, `res` |
| `:tanh` | Soft clip | `krunch` |
| `:slicer` | Amplitude gate | `phase`, `amp_min`, `amp_max`, `wave`, `probability` |
| `:panslicer` | Stereo gate | `phase`, `pan_min`, `pan_max`, `wave` |
| `:wobble` | Filter wobble | `phase`, `cutoff_min`, `cutoff_max`, `res`, `wave` |
| `:flanger` | Flanger | `phase`, `delay`, `depth`, `decay`, `feedback` |
| `:ixi_techno` | Moving resonant LPF | `phase`, `cutoff_min`, `cutoff_max`, `res` |
| `:ring_mod` | Ring modulator | `freq`, `mod_amp` |
| `:whammy` | Cheap transpose | `transpose`, `grainsize` |
| `:pitch_shift` | Pitch shifting | `pitch`, `window_size`, `pitch_dis`, `time_dis` |
| `:octaver` | Octave layering | `super_amp`, `sub_amp`, `subsub_amp` |
| `:vowel` | Formant filter | `vowel_sound` (1-5), `voice` (0-4) |
| `:lpf` / `:rlpf` | Low pass filter | `cutoff`, `res` |
| `:hpf` / `:rhpf` | High pass filter | `cutoff`, `res` |
| `:bpf` / `:rbpf` | Band pass filter | `centre`, `res` |
| `:band_eq` | Band EQ | `freq`, `res`, `db` |
| `:compressor` | Dynamics | `threshold`, `slope_above`, `slope_below`, `clamp_time`, `relax_time` |
| `:normaliser` | Level normalise | `level` |
| `:pan` | Stereo pan | `pan` |

Common FX params: `amp`, `mix`, `pre_amp`

## Quick Reference: Samples

### Categories

| Prefix | Content |
|--------|---------|
| `:drum_` | Acoustic drums (heavy_kick, tom_*, snare_*, cymbal_*, splash_*, bass_*) |
| `:bd_` | Bass drums (ada, pure, 808, zum, gas, sone, haus, zome, boom, klub, fat, tek) |
| `:sn_` | Snares (dub, dolf, zome) |
| `:hat_` | Hi-hats (snap, zap, cats, tap, bdu, psych, zild, zan, noiz, sci, star, gem, raw, yosh, cab, gnu, metal, len) |
| `:elec_` | Electronic (triangle, snare, lo/hi/mid_snare, cymbal, soft_kick, filt_snare, fuzz_tom, chime, bong, twang, wood, pop, beep, blip, blip2, ping, bell, flip, tick, hollow_kick, twip, plip, blup) |
| `:bass_` | Bass (hit_c, hard_c, thick_c, drop_c, woodsy_c, voxy_c, voxy_hit_c, dnb_f) |
| `:ambi_` | Ambient (soft_buzz, swoosh, drone, glass_hum, glass_rub, haunted_hum, piano, lunar_land, dark_woosh, choir) |
| `:loop_` | Loops (industrial, compus, amen, amen_full, garzul, mika, breakbeat) |
| `:perc_` | Percussion (bell, snap, snap2) |
| `:guit_` | Guitar (harmonics, e_fifths, e_slide, em9) |
| `:ride_` | Rides (tri, via) |
| `:arovane_beat_` | Glitchy beats at 130 BPM (a, b, c, d, e) |
| `:tbd_` | The Black Dog samples (fxbed_loop, highkey_c4, pad_1-4, perc_blip, perc_hat, perc_tap_1/2, voctone) |

### Sample Manipulation

| Opt | Effect |
|-----|--------|
| `rate:` | Playback speed (0.5 = octave down, 2 = octave up, negative = reverse) |
| `beat_stretch:` | Stretch to fit N beats at current BPM |
| `pitch_stretch:` | Stretch duration without changing pitch |
| `rpitch:` | Relative pitch shift in semitones |
| `start:` / `finish:` | Partial playback (0-1 range, start > finish = reverse) |
| `onset:` | Play specific onset within sample |
| `slice:` / `num_slices:` | Play specific slice |
| `cutoff:` / `lpf:` / `hpf:` | Filter (MIDI note 0-130) |
| `amp:`, `pan:` | Standard amplitude and panning |
| `norm:` | Normalise volume |
| `compress:` | Built-in compressor |
| ADSR | `attack:`, `decay:`, `sustain:`, `release:` (can only reduce, not extend) |

External samples: pass a file path string to `sample`. Sample packs: pass directory path.

## Timing and Loops

### live_loop

```ruby
live_loop :drums do
  sample :bd_haus
  sleep 0.5
end
```

- Must contain `sleep` (prevents infinite zero-time loops)
- Only one instance per name runs at a time
- Redefine while running to update on next iteration
- Each iteration auto-generates a `cue` with the loop's name

### BPM and Timing

```ruby
use_bpm 120              # set beats per minute
use_sample_bpm :loop_amen # match BPM to sample's natural tempo
sleep 1                   # wait 1 beat
sleep 0.25                # wait a quarter beat (sixteenth note)
```

### Syncing Loops Together

```ruby
live_loop :metro do
  cue :tick
  sleep 1
end

live_loop :melody do
  sync :metro              # locks to metro's timing
  play (scale :e3, :minor_pentatonic).choose
end
```

### Threads

```ruby
in_thread do
  4.times do
    play :e3
    sleep 0.5
  end
end
```

## Rings, Tick, and Sequencing

### Creating Rings

```ruby
(ring 60, 62, 64, 65, 67)              # explicit ring
(scale :e3, :minor_pentatonic)          # scale as ring
(chord :e3, :minor)                     # chord as ring
range(0, 1, 0.1)                        # numeric range
bools(1, 0, 1, 0, 1, 0, 1, 0)          # boolean pattern
knit(:e3, 3, :g3, 1, :a3, 2)           # repeat values: e3 x3, g3 x1, a3 x2
spread(5, 8)                            # euclidean rhythm (booleans)
line(0, 1, steps: 8)                    # linear interpolation
```

### Tick and Look

```ruby
live_loop :seq do
  play (ring :e3, :g3, :a3, :b3).tick   # advance + return
  sleep 0.25
end

# Named ticks for independent counters
live_loop :multi do
  play (scale :e3, :minor).tick(:melody)
  sample :bd_ada if (spread 3, 8).tick(:rhythm)
  sleep 0.25
end

# .look returns current without advancing
notes = (ring :e3, :g3, :a3)
notes.tick    # => :e3 (advances)
notes.look    # => :e3 (same, no advance)
notes.tick    # => :g3 (advances)
```

### Ring Chain Methods

`.reverse`, `.sort`, `.shuffle`, `.pick(N)`, `.take(N)`, `.drop(N)`, `.stretch(N)`, `.repeat(N)`, `.mirror`, `.reflect`, `.scale(N)`, `.choose`, `.butlast`, `.drop_last(N)`, `.take_last(N)`

### Scales and Chords

Common scales: `:major`, `:minor`, `:major_pentatonic`, `:minor_pentatonic`, `:blues`, `:dorian`, `:mixolydian`, `:lydian`, `:phrygian`, `:locrian`, `:chromatic`, `:whole_tone`, `:harmonic_minor`, `:melodic_minor_asc`, `:hungarian_minor`, `:hirajoshi`, `:iwato`, `:kumoi`, `:yo`

Common chords: `:major`, `:minor`, `:m7`, `:dom7`, `:dim7`, `:aug`, `:m9`, `:m11`, `:m13`, `:sus2`, `:sus4`

```ruby
play_pattern_timed (scale :e3, :minor_pentatonic), [0.25, 0.5]
```

## Envelope (ADSR)

| Param | Default | Purpose |
|-------|---------|---------|
| `attack:` | 0 | Time to reach `attack_level` |
| `decay:` | 0 | Time from `attack_level` to `decay_level` |
| `sustain:` | 0 (synths), auto (samples) | Time at `sustain_level` |
| `release:` | 1 | Time to fade to 0 |
| `attack_level:` | 1 | Peak after attack |
| `decay_level:` | sustain_level | Level after decay |
| `sustain_level:` | 1 | Level during sustain |
| `env_curve:` | 2 | 1=linear, 2=exponential, 3=sine, 4=welch, 6=squared, 7=cubed |

Total duration = attack + decay + sustain + release. All values in **beats**.

### Cutoff Envelope (TB-303, sample players)

`cutoff_attack:`, `cutoff_decay:`, `cutoff_sustain:`, `cutoff_release:`, `cutoff_attack_level:`, `cutoff_decay_level:`, `cutoff_sustain_level:` — independent ADSR for filter cutoff.

## Controlling Running Synths

```ruby
# Capture and control a synth node
sn = synth :prophet, note: :e1, release: 8, cutoff: 70, cutoff_slide: 2
sleep 1
control sn, cutoff: 130   # slides over 2 beats

# Control FX
with_fx :echo, mix: 0, mix_slide: 8 do |fx|
  control fx, mix: 1
  synth :prophet, note: :e1, release: 8
  sleep 8
end
```

Every modifiable opt has a `_slide:` counterpart: `amp_slide:`, `cutoff_slide:`, `pan_slide:`, `note_slide:`, etc.

## MIDI

### Receiving

```ruby
live_loop :midi_in do
  use_real_time
  note, velocity = sync "/midi:*/note_on"
  synth :piano, note: note, amp: velocity / 127.0
end
```

Wildcards in paths: `sync "/midi:*/note_on"` matches any device.

### Sending

```ruby
midi_note_on :e3, 100            # note on with velocity
midi_note_off :e3                # note off
midi :e3, sustain: 0.5           # shortcut: note_on + sleep + note_off
midi_cc 32, 64                   # control change
midi_pitch_bend 0.5              # pitch bend
midi_clock_tick                  # clock
```

Target specific device/channel: `port:`, `channel:` (1-16)

## OSC

### Receiving (default port 4560)

```ruby
live_loop :osc_in do
  use_real_time
  a, b = sync "/osc*/trigger"
  play a
end
```

### Sending

```ruby
use_osc "localhost", 4560
osc "/path", 1, 2, 3
```

## State System

```ruby
set :key, 42            # store
val = get[:key]         # retrieve (non-blocking)
val = sync :key         # block until new value set
```

Thread-safe and deterministic.

## Randomisation

| Function | Returns |
|----------|---------|
| `rand` / `rand(max)` | Float 0 to 1 (or 0 to max) |
| `rand_i(max)` | Integer 0 to max |
| `rrand(min, max)` | Float in range |
| `rrand_i(min, max)` | Integer in range (inclusive) |
| `choose(list)` | Random element |
| `one_in(N)` | Boolean, true with probability 1/N |
| `dice(N)` | Integer 1 to N |
| `use_random_seed N` | Set deterministic seed |

All randomisation is **pseudo-random** — same seed = same results every run.

## Sound Design Patterns

### Acid Bass

```ruby
use_synth :tb303
live_loop :acid do
  play :e1, release: 0.125, cutoff: rrand(70, 130), res: 0.9, wave: 0
  sleep 0.125
end
```

### Supersaw Pad

```ruby
live_loop :pad do
  use_synth :supersaw
  play chord(:e3, :minor), release: 4, cutoff: 80, res: 0.3
  sleep 4
end
```

### Euclidean Rhythms

```ruby
live_loop :euclidean do
  tick
  sample :bd_ada if (spread 5, 8).look
  sample :drum_cymbal_closed if (spread 3, 8).look
  sleep 0.125
end
```

### Sample Slicing

```ruby
live_loop :chop do
  n = 8
  n.times do |i|
    sample :loop_amen, beat_stretch: 2, onset: i
    sleep 2.0 / n
  end
end
```

### Probabilistic Beats

```ruby
live_loop :prob do
  sample :bd_haus if one_in(2)
  sample :drum_cymbal_closed if one_in(3)
  sample :drum_snare_hard if one_in(6)
  sleep 0.125
end
```

### Steve Reich Phasing

```ruby
live_loop :reich1 do
  play (ring :e4, :fs4, :b4, :cs5, :d5, :fs4, :e4, :cs5, :b4, :fs4, :d5, :cs5).tick
  sleep 0.2
end

live_loop :reich2 do
  play (ring :e4, :fs4, :b4, :cs5, :d5, :fs4, :e4, :cs5, :b4, :fs4, :d5, :cs5).tick
  sleep 0.2015  # slightly longer = gradual phase shift
end
```

## Live Coding Performance Tips

1. **Memorise shortcuts** — `Alt+R` (Run), `Alt+S` (Stop). Avoid the mouse.
2. **One live_loop per element** — bass, drums, melody, FX each get their own loop.
3. **Sync loops** — Use `sync :other_loop` to keep them in phase.
4. **Random seed surfing** — Change `use_random_seed N` to explore variations.
5. **Comment/uncomment** — Use `#` to quickly mute/unmute lines.
6. **Incremental changes** — Modify one parameter at a time while code runs.
7. **FX context swapping** — Move `live_audio` between FX blocks on-the-fly.
8. **Slide for smooth transitions** — Use `_slide:` opts with `control` for gradual changes.

## Multichannel Audio

```ruby
# Mono input through FX
live_audio :mic, input: 1

# Stop input
live_audio :mic, :stop

# Direct output to specific channel
with_fx :sound_out, output: 3, amp: 0 do
  play :e3
end
```
