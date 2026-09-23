# Script Director - Documentary Montage Pipeline

## When To Use

The brief exists and narration is not opted out. Your job is to write
the full narration from scratch — there is no existing footage or
research_brief to draw from, unlike other pipelines. You write directly
from the brief's thematic question, tone, and duration.

The script you write here is the backbone of everything downstream. The
scene director will turn every section (beat) you write into one or
more visual scenes, and each scene's on-screen duration is derived from
how long your section takes to speak — not a fixed hold table. A vague
or padded script produces a vague or padded video.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["idea"]["brief"]["metadata"]` | Thematic question, tone, duration, shape, narration provider/voice/language — all documentary-montage-specific fields live under `brief.metadata`, not the brief's top level |

## Process

### 1. Read The Brief Closely

All of these live under `brief.metadata` (not the brief's top level —
see `idea-director.md`'s "A Note On The Brief's Shape" for why).
Extract:
- **`metadata.thematic_question`** — the single question this piece answers.
- **`metadata.duration_seconds`** — your word budget (see timing table below).
- **`metadata.tone`** — shapes pacing, sentence length, word choice.
- **`metadata.shape`** — structural approach (list, before/after, three-act,
  single-image expansion). The narration should follow this shape,
  not fight it.
- **`metadata.narration.language`** — write in this language. For "The Forgotten
  Shadows" channel specifically, this is always English regardless of
  any other project convention.

### 2. Plan The Narrative Arc By Shape

Map the brief's `metadata.shape` to a narration structure:

- **list/catalogue**: a short frame at the top, then N parallel beats
  of roughly equal weight, no forced turn.
- **before/after**: beats establishing the "before" state, one pivot
  beat, beats showing the "after" state.
- **three-act**: setup beats → turn beats → release beats, roughly
  30/40/30 by time.
- **single-image expansion**: one anchor beat naming the central
  image/idea, then beats that circle back to it from different angles.

Do not write beats that just restate the thematic question in
different words. Each beat should add a concrete fact, image, or turn.

### 3. Write The Script As Sections (Beats)

Each `sections[]` entry is one beat — a self-contained unit of story,
not yet a visual unit. The scene director will later decide whether a
beat becomes one scene or several; you are not deciding that here.

```json
{
  "id": "s1",
  "label": "Opening",
  "text": "In the summer of 1518, something strange began in Strasbourg. A woman started to dance in the street.",
  "start_seconds": 0,
  "end_seconds": 6.5,
  "speaker_directions": "Measured, slightly hushed — this is a mystery being introduced, not announced.",
  "delivery_cues": {
    "pace": "measured",
    "energy": "quiet curiosity",
    "pause_after_seconds": 0.5,
    "delivery_note": "Let 'something strange' land before naming the year and place."
  }
}
```

Required fields per section: `id`, `text`, `start_seconds`,
`end_seconds`. Use `speaker_directions` and/or `delivery_cues` for
anything the TTS provider needs to deliver the line right — this
pipeline does not require the full `voice_performance` planning block
that longer-form pipelines use, but pace/pause cues matter for
elegiac/reverent tone especially.

#### Timing Estimation (starting point, not a final rule)

| Tone | Words/second | Notes |
|------|--------------|-------|
| elegiac | ~2.0 | long holds, unhurried delivery |
| reverent | ~2.1 | stately, patient |
| dreamlike | ~1.9 | slow, some beats mostly silence/held image |
| wry | ~2.4 | brisker, conversational |
| urgent | ~2.6 | short cuts, hard sync |

**Treat these as an estimate to draft against, not a contract.** Names,
dates, foreign terms, and short punchy lines read slower than their
word count suggests; long flowing description reads faster. If a beat
has a lot of proper nouns or numbers, budget extra time for it even if
the word count looks short.

**Real spoken duration always wins over this estimate.** Once TTS audio
exists for a section (at the asset stage or later), that
`audio_duration_seconds` becomes the authority for that section's
timing, and the scene director's slot durations should be reconciled
against it, not the original word-count guess.

**Word budget by duration** (using ~2.0-2.2 words/sec as a rough
documentary-pace midpoint — adjust per the tone table above):

- 90s video → ~180-200 words total narration
- 2-3 min video → ~300-400 words
- 7-8 min (long-form) video → ~900-1050 words, spread across
  proportionally more/longer beats — do not just stretch pauses to
  fill time; the Topic-Viability Check at the idea stage should
  already have confirmed there's enough real material for this

### 4. Keep Beats Concrete, Not Abstract

The scene director will need to find or generate real footage/images
for each beat. A beat written in abstractions ("the town was gripped by
fear") gives the scene director nothing to point a camera at. A beat
written with a concrete image or action ("officials ordered musicians
into the square, hoping the dancers would dance themselves to
exhaustion") gives the scene director something to find footage for.

This matters more here than in narration-only pipelines, because this
pipeline's downstream asset sourcing is retrieval-first (real archival
and stock footage), not generative — vague beats produce weak
retrieval queries.

### 5. Self-Evaluate

| Criterion | Question |
|-----------|----------|
| **Coverage** | Does the narration actually answer the thematic question, not just gesture at it? |
| **Word count accuracy** | Within ±10% of the word budget for the duration? |
| **Concreteness** | Can you picture a specific shot for every beat, or are some beats pure abstraction? |
| **Shape fidelity** | Does the beat sequence follow the brief's `metadata.shape` (list/before-after/three-act/single-image)? |
| **No padding** | If duration is long-form, does every beat add new information, or are some beats restating earlier ones to fill time? |

If any dimension is weak, revise before submitting — especially "no
padding" on long-form targets, since that's exactly the failure mode
the idea stage's Topic-Viability Check was meant to prevent.

### 6. Record The Script Artifact

```json
{
  "version": "1.0",
  "title": "The Dancing Plague of 1518",
  "total_duration_seconds": 90,
  "sections": [
    { "id": "s1", "label": "Opening", "text": "...", "start_seconds": 0, "end_seconds": 6.5 },
    { "id": "s2", "label": "The spread", "text": "...", "start_seconds": 6.5, "end_seconds": 14 }
  ],
  "metadata": {
    "pipeline": "documentary-montage",
    "thematic_question": "What does rain show you about a city?",
    "words_per_second_used": 2.0
  }
}
```

`total_duration_seconds` should land within 10% of
`brief.metadata.duration_seconds`. If your beats run long or short,
cut or extend beats — don't pad with filler words to hit the number.

### 7. Quality Gate

- Every section has non-empty `text`, `start_seconds`, `end_seconds`.
- Sections are contiguous and in order (no gaps, no overlaps).
- `total_duration_seconds` within ±10% of `brief.metadata.duration_seconds`.
- No section is pure abstraction with no concrete image/action to
  point a camera at.
- This artifact's own `metadata.thematic_question` echoes
  `brief.metadata.thematic_question` verbatim.
- Narration language matches `brief.metadata.narration.language`.

## Common Pitfalls

- **Padding a thin topic to hit a long-form duration.** If you're
  struggling to write beat 8 of 12 without repeating beat 3, the topic
  was too thin for this duration — flag it rather than force it. (This
  should usually have been caught at the idea stage's Topic-Viability
  Check, but catch it here too if it slipped through.)
- **Writing abstractions instead of images.** "The atmosphere grew
  tense" gives the scene director nothing to search for. Name the
  concrete thing that made it tense.
- **Treating the word-count table as exact.** It's a first draft
  target. A beat full of names and dates will run long at the same
  word count as a beat of flowing description.
- **One giant section instead of beats.** Even a short piece needs
  multiple sections — the scene director maps sections to visual
  scenes, and a single 90-second section gives it nothing to work
  with structurally.
- **Reading brief fields from the top level instead of `metadata`.**
  This pipeline's brief keeps `thematic_question`, `duration_seconds`,
  `tone`, `shape`, `narration`, etc. under `brief.metadata` — see
  `idea-director.md`'s "A Note On The Brief's Shape".

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
