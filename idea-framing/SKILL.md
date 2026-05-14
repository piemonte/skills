---
name: idea-framing
description: Use when framing or developing a new concept — five-section template (Concept / Problem / Why interesting / State of the art / Solution / Technical), supports guided Q&A, structuring a rough dump, or critiquing a draft. Includes title suggestion.
---

# Idea Framing

A lightweight framework for turning a hunch into a clear, defensible concept. Five sections, each answering one question. Works for products, research, art pieces, services — anything that needs to justify itself to a future you (or a collaborator) two months from now.

## When to use

Invoke this skill when the user wants to:

- **Frame a new idea from scratch** ("I've got an idea about X, help me think it through")
- **Structure a rough dump** of notes into a coherent concept doc
- **Critique an existing draft** before they share it more widely
- **Pick a name** for a concept that's still untitled

Detect the mode by what the user provides:

| Signal | Mode |
|---|---|
| Just a topic or "I want to capture an idea" | **Guided Q&A** |
| A paragraph or notes pasted in | **Dump & Structure** |
| A fully-formed draft using these sections | **Critique & Refine** |

If ambiguous, ask once which mode they want.

## The Template

Five sections. Keep them in this order — each builds on the previous.

```markdown
# <Title>

**Concept:** <one-sentence concept statement>

## Problem
What problem does this solve? For whom? Why does it matter right now?

## Why it's interesting
Why is this worth pursuing? What's the underlying insight or unmet desire?

## State of the art
What existing solutions exist? What do they do well? Where do they fall short?

## Solution
What is your approach, in enough detail to picture it? Why is it better than the state of the art — concretely?

## Technical
What does it take to build? Major components, dependencies, hardest parts.
```

The **Concept** line at the top is a single sentence — the elevator pitch. If you can't say it in one sentence yet, that's the first thing to nail.

## Mode 1: Guided Q&A

When the user arrives empty-handed or with only a topic, walk through the template one section at a time.

**Rules:**
- Ask **one question per turn**. Resist batching — the answers are richer when given full attention.
- Go in template order: Concept → Problem → Why interesting → SOTA → Solution → Technical.
- After each answer, reflect it back as a tightened prose paragraph and confirm before moving on. This catches misreads early and gives the user something concrete to react to.
- When the answer reveals a deeper question (e.g., "who is this really for?"), follow that thread before advancing.
- Don't ask the user to define every term — fill in reasonable interpretations and let them correct.

**Opening prompt:** *"What's the idea, in one sentence? Rough is fine — we'll refine it."*

After Concept is captured, offer title candidates (see Title Suggestion below) before moving on.

## Mode 2: Dump & Structure

When the user pastes a rough dump or notes, map their content onto the five sections without asking new questions first.

**Steps:**
1. Read the dump end-to-end.
2. For each section, extract what's already there. Quote or paraphrase from the user's words — don't invent.
3. List **explicit gaps**: which sections have nothing, which have hand-waves, which contradict.
4. Only then ask follow-up questions, one at a time, targeting the gaps. Skip what's solid.
5. Assemble the final doc once gaps are filled.

A useful framing: *"Here's what I pulled from your notes for each section. Three sections look strong, two need more — let's tackle those."*

## Mode 3: Critique & Refine

When the user provides an existing draft, review it section by section. Be specific and a little adversarial — empty agreement is useless.

**Per-section checks:**

- **Concept:** Is it one sentence? Does it actually describe the thing, or just gesture at the space?
- **Problem:** Is the problem real and felt, or theoretical? Who specifically has it? Why now?
- **Why interesting:** Does this say more than "it's cool"? What's the non-obvious insight?
- **State of the art:** Are existing solutions named, or hand-waved as "most services"? Be skeptical of dismissive sweeps — push for concrete examples of what's out there.
- **Solution:** Does the solution actually solve the stated problem? Is the differentiation from SOTA specific, or generic ("better UX")?
- **Technical:** Does this read like the author has thought about how to build it, or is it a wishlist? What are the hardest parts — are they acknowledged?

**Output format:** For each section, give a one-line verdict (Strong / Workable / Weak), then a short critique, then a concrete suggestion. End with the top 2–3 things to fix.

## Title Suggestion

After the Concept line is clear (in any mode), offer 3–5 candidate titles. Mix styles:

- **Descriptive:** says what it is (e.g., "Realtime Voice Network")
- **Codename:** evocative, non-literal (e.g., "Switchboard", "Hailfrequency")
- **Compound/portmanteau:** short and brandable (e.g., "Voxcast")
- **Phrase / tagline-as-title:** captures the feeling (e.g., "Anyone, Listening")

Present them as a numbered list. Note tradeoffs briefly (memorable vs. searchable vs. clear). Let the user pick, mix, or veto — and offer more if none land.

Don't propose titles unsolicited if the user already has one. Ask: *"You have a title in mind, or want suggestions?"*

## Output Format

The final doc uses clean markdown — no decorative emoji, just structure.

```markdown
# <Title>

**Concept:** <one-line concept>

## Problem
<prose>

## Why it's interesting
<prose>

## State of the art
<prose>

## Solution
<prose>

## Technical
<prose>
```

Default: print the finished doc inline in the conversation. The user can copy it wherever they want.

## Saving

If the user asks to save the result to a file:

- Filename: kebab-case slug of the title + `.md` (e.g., `realtime-voice-network.md`).
- Location: current working directory, unless the user specifies otherwise.
- If a file with that name already exists, ask before overwriting.

Don't proactively save — wait to be asked.

## Section Guidance Cheatsheet

Quick reference for what "strong" looks like vs. common failure modes.

| Section | Strong looks like | Common failures |
|---|---|---|
| **Concept** | One sentence, concrete subject + concrete action + audience hint | Two-sentence rambles; gestures at a space without naming the thing |
| **Problem** | Names a real audience, a felt pain, and why-now | Theoretical problems no one is actually trying to solve |
| **Why interesting** | Surfaces a non-obvious insight or unmet desire | "It's cool" / "Nothing like this exists" without evidence |
| **State of the art** | Names 2–3 specific existing solutions and what they miss | Dismissive sweeps ("most services don't…"); strawmen |
| **Solution** | Specific enough to picture; differentiation from SOTA is concrete | Generic "better UX" / "AI-powered"; doesn't actually address the problem stated |
| **Technical** | Major components named; hardest parts acknowledged | Wishlist with no architecture; assumes someone else solves the hard parts |

## Worked Example

This is a calibration anchor — what a finished idea-framing doc should feel like.

```markdown
# Hailfrequency

**Concept:** A real-time, interest-driven audio network where anyone can dial into a conversation about a topic by browsing short voice intros.

## Problem
People want to hear a live voice — especially when something is happening right now. Hotlines and 800 numbers were built on this premise, but they're rigid: you can only call about predefined topics, and you talk to a service, not a peer. There's no way to say "I want to talk to someone, right now, about X."

## Why it's interesting
A firsthand voice in real time carries information that text and indexed video can't — tone, hesitation, freshness. The closest analog (talk radio, podcasts) is one-to-many and asynchronous. No one has built a peer-to-peer, intent-routed version of this for the mainstream.

## State of the art
Discord and Clubhouse offer voice rooms, but discovery is community- and schedule-driven, not intent-driven. Random-pairing apps (Omegle-style) lack topical filtering. Search engines and YouTube return indexed, post-captured media — never a live person. Hotlines are topic-specific but operator-mediated.

## Solution
Two surfaces. **Discovery:** a swipeable feed of 5-second voice intros — each user's elevator pitch for what they want to talk about. Filter by keyword (voice or text search) and geography (radius or country). **Conversation:** a peer-to-peer audio call between the listener and the intro's author, followed by a rating and an optional bookmark. The intro acts as both signal of intent and consent to be called.

Better than SOTA because: discovery is intent-driven (not social-graph), connection is one-to-one (not broadcast), and the medium is live voice (not indexed media).

## Technical
Three client roles: intro discovery, intro creation, peer-to-peer call. Server provides the intro directory, search (voice-to-text + keyword index), and call signaling. Real-time audio uses WebRTC over a TURN/STUN backbone. Hardest parts: discovery ranking that surfaces freshness without becoming a popularity contest; moderation of voice content at scale.
```
