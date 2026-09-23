# Edit Director - Documentary Montage Pipeline

## When To Use

Every slot has a clip. You now have to turn a pile of clips into a
piece. This stage decides in-points, out-points, transitions, music
sync, and the order the clips actually run. The output is an
`edit_decisions` artifact with a concrete timeline.

This is where documentary technique lives. If the asset director did
its job, you have the raw material. The edit is the thinking.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/edit_decisions.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["assets"]["asset_manifest"]` | Picked clips + music bed |
| Prior artifact | `state.artifacts["scene_plan"]["scene_plan"]` | Slot order, hero flags, **target_hold_seconds per slot (the authority on hold duration — see Step 1)** |
| Prior artifact | `state.artifacts["script"]["script"]` | Section timing, in case a hold needs to be re-checked against narration pace |
| Prior artifact | `state.artifacts["idea"]["brief"]["metadata"]` | Tone register, duration, shape — documentary-montage-specific fields live under `brief.metadata`, not the brief's top level |
| Tool (optional) | `video_analyzer` | Probe a clip's motion if you need to re-check |

## Mental Model

Documentary montage lives in four dimensions you have to balance:

1. **Rhythm** — how long each hold lasts and how the holds relate.
2. **Juxtaposition** — which image follows which, and what it means.
3. **Music sync** — cuts landing on beats, dropouts earning weight.
4. **Continuity of register** — the grain, color, and era don't swing
   wildly unless the swing is the point.

The enemy is "slideshow" — a sequence of clips played back-to-back
with the same hold length and no sound design. If it feels like a
slideshow, the edit has failed, regardless of how good the clips are.

This stage also locks the render grammar. For documentary montage,
set `renderer_family` to `documentary-montage` so compose stays on the
approved Remotion-first path.

## Process

### 0. Guardrails — No Silent Major Changes

Before touching the timeline, re-read the brief. If any of these are
true, STOP and surface to the user per the Decision Communication
Contract:

- The brief opted out of narration (`brief.metadata.narration = "none"`)
  but the edit feels like it needs voice-over. Adding narration this
  late is a MAJOR change — it also means the whole `script` →
  `scene_plan` timing chain was skipped, so this isn't a quick add.
- The brief approved a music track that the edit director now wants
  to replace. Music swap is a MAJOR change.
- The scene plan's slot holds (from `target_hold_seconds`, in turn
  from narration timing) don't sum close to
  `brief.metadata.duration_seconds`. A drift here usually means the
  script or scene plan already drifted upstream — flag it rather than
  quietly stretching/compressing everything to force-fit the number.

Fix the edit, don't paper over it. If the edit genuinely needs
one of these, ask.

### 1. Read The Hold Durations From The Scene Plan — Don't Recompute Them

**Each slot's hold duration is already decided.** The scene director
set `target_hold_seconds` per slot in `scene_plan.metadata.slots[]`,
derived from that slot's script section's narration timing (see
`scene-director.md` Step 1). This stage does NOT use a fixed tone-based
hold table — there isn't one anymore. Your job here is to realize those
already-decided holds as actual clip in/out points, not to decide hold
length from scratch.

For each cut:

- Start from the slot's `target_hold_seconds`.
- If the picked clip's usable window (see Step 3) genuinely can't
  sustain that hold without looking static or repeating motion, you
  may adjust — but log why in `metadata.reorder_notes` or a per-cut
  `reason`, and keep the total close to the section's original
  narration-derived span.
- **Hero slots** get first claim on any flex — if you need to borrow
  or lend a fraction of a second between adjacent cuts to make a
  transition or L-cut work cleanly, take it from a non-hero neighbor.

Total hold time must sum to within ±10% of
`brief.metadata.duration_seconds`. If you're overshooting or
undershooting by more than that, the drift most likely originated
upstream (script pacing or scene decomposition) — flag it rather than
force-fitting the timeline here.

### 2. Arrange By Narrative Beat, Not By Score

The scene director gave you a slot order, itself following the
script's beat order. That order is the intent. Don't rearrange it by
CLIP score, motion score, or resolution.

You MAY reorder slots when:

- The music bed has a downbeat at a known timestamp and reordering
  two slots lands a hero on the beat (see step 4).
- Two adjacent slots are visually identical and swapping one breaks
  the monotony (but see step 7 — diversify should have caught this
  already).
- The final image isn't landing. The last 5-10s carries
  disproportionate weight; if the scene director's choice dies, move
  a stronger candidate to the tail.

Reordering slots that came from different script sections risks
breaking the narration's sense — a scene can only move within or
adjacent to its own section's timing without also moving the narration
audio, so treat cross-section reorders as a bigger flag than
within-section ones.

Always log the reorder in `edit_decisions.metadata.reorder_notes`
with the reason.

### 3. Trim Each Clip To Its Beat

For every picked clip, decide `in_seconds` and `out_seconds`. Three
rules:

- **Find the best sub-window, not the whole clip.** A 12-second Pexels
  clip usually contains one 3-second moment that earns the hold and
  9 seconds of setup/settle. Find the moment.
- **Cut BEFORE the action's natural end.** End on a look, not on a
  move-off. The cut feels intentional instead of exhausted.
- **Leave a handle at both ends.** 4-6 frames of headroom so the
  composer can apply a fade or dissolve without clipping the moment.

If a clip is too short to fill its target hold, either:

- slow it down (speed 0.5-0.75, fine on static-ish footage, bad on
  anything with sync motion or faces talking),
- apply a Ken Burns pan/zoom to stretch a still or near-still frame to
  the full hold (the scene director may have already flagged a slot
  for this — see `scene-director.md` Step 1),
- let it cut early and borrow the remaining duration from the next
  slot's hold,
- or swap to the #2 candidate from the rejected-picks log.

Do NOT hold on the last frozen frame. A freeze-frame in a doc montage
reads as a technical mistake.

### 4. Sync To The Music Bed

Read `asset_manifest` for the music asset and load its duration.
Documentary montages earn their emotional weight from cuts landing
on musical events. Three sync moves:

- **Downbeat cuts.** If you have bars and beats metadata (from a
  provided track) or can hear them, place hero cuts on downbeats.
  If not, evenly-spaced cuts on 4s intervals for a 60bpm bed are a
  safe default.
- **One held silence.** Drop the music out for ~2s at the piece's
  emotional center. Silence is a tool. Use it once. Use it hard.
- **Tail fade.** Music fades under the last 3-5s so the final image
  can breathe without a musical resolution fighting it.

Record the music config in `edit_decisions.audio.music` with:

```json
{
  "asset_id": "asset_music_bed",
  "volume": 0.5,
  "fade_in_seconds": 1.0,
  "fade_out_seconds": 4.0,
  "ducking": true
}
```

**`ducking: true` is the default for this pipeline now** — narration
is mandatory by default (see `executive-producer.md`), so the music
bed should duck under the narration track. Only set `ducking: false`
if `brief.metadata.narration = "none"` (explicit opt-out, no
narration track to duck under). Music `volume` should also generally
sit lower (~0.4-0.6) than a music-only piece, since it's sharing space
with a voice.

### 5. Choose Transitions From A Small Vocabulary

Documentary montage uses maybe four transitions total across the
entire piece:

| Transition | Use |
|------------|-----|
| `cut` (hard) | Default. Most cuts are hard cuts. |
| `dissolve` (0.5-1.0s) | Emotional sibling clips, time passage |
| `fade_to_black` (0.5s, then back up) | Act breaks in 3-act shape, or once near the end |
| `fade_in` (first shot) / `fade_out` (last shot) | 0.5-1.0s bookends |

**Do not use:**

- wipes,
- push/slide transitions,
- zoom blurs,
- RGB splits,
- light leaks,
- glitch effects.

These read as social-media edit language and will break the
documentary register. If the piece is getting boring, fix the clip
choices or the pacing, don't add transition flash.

Record each cut's `transition_in` / `transition_out` per the schema.
Default `transition_in: "cut"` on most cuts.

### 6. Apply Register Continuity

Mixed-era corpora look wildly different. Pexels 2023 is clean, sharp,
color-graded. Prelinger 1962 is grainy, warm, squared-off aspect.
NASA archival is often low-res with text overlays. If you mash them
together raw, the piece looks like a Wikipedia article.

You have two tools to smooth this:

1. **Crop to a uniform aspect ratio.** Pick one: 16:9 cinematic
   (`2.35:1` letterbox on top/bottom) for hero pieces, 9:16 for
   social. Enforce in the `transform.crop` field of each cut.
2. **Flag the piece for a uniform color grade at compose time.** Put
   a `grade_profile` hint in `edit_decisions.metadata`. The compose
   director will apply a LUT across the whole timeline.

Don't try to color-grade individual clips here. That's the compose
stage. Your job is to flag the need.

### 7. Enforce Adjacent Diversity One More Time

Walk the timeline in pairs. For each consecutive (cut_n, cut_n+1):

- Are they the same subject at the same scale? If yes, you have a
  slideshow moment. Swap one for a clip at a different scale (wide
  vs close).
- Are they the same color palette (two night-blue clips back to
  back)? If yes, break the pattern at least every 4 cuts.
- Are they the same motion direction (two left-to-right pans)? If
  yes, flip the second's horizontal axis or reorder.

Log any swaps you made in `metadata.diversity_swaps`.

### 8. The L-Cut Move (Optional But Powerful)

For any transition between two clips where the outgoing clip has
strong ambient audio (rain, footsteps, traffic), carry the audio
under the incoming clip for 0.5-1.5s. This is an L-cut and it
welds two shots together more tightly than any visual transition.

Implement via the schema by using a short `dissolve` transition OR
by layering the outgoing clip's audio as an SFX entry in
`edit_decisions.audio.sfx` with a delayed end.

Documentary montages with L-cuts feel 50% more coherent than ones
without. Use them on the 3-4 hardest transitions in the piece — but
keep ambient SFX low enough that it never competes with the narration
track sitting on top.

### 8b. Place The End-Tag Overlay

If `brief.metadata.end_tag_plan.mode == "overlay"` (the default), the
end-tag will be composited on top of the final body footage at compose
time. The edit director's job is to decide **when** the tag appears.

Compute the offset: `offset_seconds = body_duration - tag_duration`.
This makes the tag's fade-out align with the body's closing fade-out
(the last cut's `transition_out: fade_out`). If the final cut's hold
is shorter than the tag duration, start the tag earlier so it overlaps
the second-to-last cut as well — this is fine and often looks better.

Record in `edit_decisions.end_tag`:

```json
{
  "end_tag": {
    "offset_seconds": 84.5,
    "notes": "Tag starts at body_duration - tag_duration. Aligns tag fade-out with final cut fade-out."
  }
}
```

If `mode == "concat"`, omit this section — the compose-director will
append the tag after the body without needing a timing offset.

### 9. Emit The Edit Decisions

Canonical shape for this pipeline:

```json
{
  "version": "1.0",
  "renderer_family": "documentary-montage",
  "cuts": [
    {
      "id": "cut_01",
      "source": "asset_slot_01",
      "script_section_id": "s1",
      "in_seconds": 1.2,
      "out_seconds": 5.2,
      "layer": "primary",
      "transform": { "scale": 1.0, "position": "center" },
      "transition_in": "fade_in",
      "transition_out": "cut",
      "transition_duration": 0.8,
      "reason": "opening hero — raindrop on asphalt, hold matches section s1's narration span"
    },
    {
      "id": "cut_02",
      "source": "asset_slot_02",
      "script_section_id": "s2",
      "in_seconds": 2.0,
      "out_seconds": 5.5,
      "layer": "primary",
      "transition_in": "cut",
      "transition_out": "cut",
      "reason": "umbrella opening in doorway, hard cut from raindrop → street"
    }
  ],
  "audio": {
    "music": {
      "asset_id": "asset_music_bed",
      "volume": 0.5,
      "fade_in_seconds": 1.0,
      "fade_out_seconds": 4.0,
      "ducking": true
    },
    "narration": {
      "asset_id": "asset_narration_track",
      "volume": 1.0
    }
  },
  "end_tag": {
    "offset_seconds": 84.5,
    "notes": "Tag starts at body_duration - tag_duration. Aligns tag fade-out with final cut fade-out."
  },
  "metadata": {
    "pipeline": "documentary-montage",
    "tone": "elegiac",
    "shape": "list",
    "total_duration_seconds": 90.0,
    "grade_profile": "warm_film_100",
    "reorder_notes": [],
    "diversity_swaps": [
      { "at": "cut_07-cut_08", "reason": "two wide rooftops-in-rain adjacent, swapped 08 for #2 pick" }
    ],
    "silence_window": { "start_seconds": 54.0, "end_seconds": 56.0 },
    "l_cuts": [
      { "from_cut": "cut_05", "to_cut": "cut_06", "carry_seconds": 1.2, "channel": "ambient_rain" }
    ]
  }
}
```

Note `cuts[].script_section_id` — carry this through from the scene
plan's `scenes[].script_section_id` so provenance from narration →
scene → cut survives all the way to the edit.

### 10. Quality Gate

- `sum(out - in for cut in cuts)` is within ±10% of
  `brief.metadata.duration_seconds`.
- Each cut's hold is close to its slot's `target_hold_seconds` from
  the scene plan (not recomputed from a fixed tone table — there
  isn't one on this pipeline).
- `renderer_family = "documentary-montage"` is present and unchanged.
- Hero slots have the longest holds.
- No two adjacent cuts share subject AND scale.
- The transition vocabulary is at most 4 distinct values.
- Music config exists (or `brief.metadata.music_plan.source = "none"`
  with explicit acknowledgement), with `ducking: true` unless
  narration was explicitly opted out.
- Narration track exists in `audio.narration` unless
  `brief.metadata.narration = "none"` (explicit opt-out).
- At least one `silence_window` entry for pieces >= 60s.
- Every cut has a one-line `reason` — if you can't write one, the
  cut is arbitrary and should be reconsidered.
- Every cut carries a `script_section_id` tracing it back to its
  narration beat.
- `metadata.total_duration_seconds` matches the sum of cut durations.

## Common Pitfalls

- **Recomputing hold durations from a fixed tone table.** That table
  doesn't exist anymore on this pipeline. Holds come from the scene
  plan's `target_hold_seconds`, which itself comes from narration
  timing. Overriding it with a generic tone-based number breaks
  audio/visual sync.
- **Cutting by information density instead of rhythm.** A doc
  montage is not a Wikipedia article. "But I need to show this" is
  not a reason — if the image doesn't sustain a hold, it doesn't
  belong.
- **Over-using dissolves.** A dissolve on every cut says "I couldn't
  commit". Commit.
- **Ignoring the music bed until the end.** Music is not a sweetener
  you add at compose time. It is a timing grid you cut TO.
- **Letting the final image be a weak one.** The last frame is
  disproportionately remembered. If it's weak, swap it — the scene
  director's slot ordering is a strong suggestion, not a contract.
- **Freeze-frame endings.** Reads as technical error. End on a
  fade-to-black instead.
- **Silently adding narration because the edit feels thin.** This
  pipeline defaults to narration already — if it's genuinely missing
  at this stage, that means the brief opted out, and reversing that
  now is a major change requiring approval, not something to patch
  in quietly here.
- **Hiding clip provider in the cuts.** Every `cut.source` must be
  an `asset_manifest` asset_id so provenance survives.
- **Three different transition types in the first 15 seconds.**
  Readers will feel the edit working. Restraint is the brand.
- **Reading brief fields from the top level instead of `metadata`.**
  This pipeline's brief keeps `tone`, `duration_seconds`, `narration`,
  `music_plan`, etc. under `brief.metadata` — see `idea-director.md`'s
  "A Note On The Brief's Shape".

## Worked Pacing Example — "A Minute in the Rain"

90 seconds, elegiac, list shape, 15 script-derived slots (3 hero
slots: 1, 11, 15).

- Slot holds already come from the scene plan's `target_hold_seconds`,
  which trace back to each script section's narration span (e.g. a
  6.5s script section maps to a 6.5s hero hold, an 8s section split
  into 2 scenes might be 5s/3s). The edit director isn't computing a
  base hold from a tone table — it's realizing these numbers as cut
  in/out points.
- Sum of all 15 target holds should already land close to 90s (that
  was the scene director's quality gate). If it's off by more than
  10%, that's a flag to raise, not something to silently rebalance
  here.
- Tighten slots 4, 7, 13 slightly if their clips can't sustain the
  full target hold without visible repetition (small cutaways are the
  easiest to trim without hurting the piece).
- Insert silence_window 54.0-56.0s (right before hero_11) — this is
  an edit-level music decision independent of hold length.
- L-cut slot_10 (boot in puddle) → slot_11 (lit window across
  street), carry rain-on-glass ambient 1.2s, kept low under the
  narration.
- First cut `fade_in` 1.0s, last cut `fade_out` 1.5s.
- All other cuts hard.
- Music ducks under narration throughout, fades in 1.0s, fades out
  4.0s under hero_15 + black.

This gives a 90s piece with 3 breathing points (fade_in, silence,
fade_out), a clear hero arc (slots 1 → 11 → 15) that matches the
script's own emphasis, and no adjacent scale collisions.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
