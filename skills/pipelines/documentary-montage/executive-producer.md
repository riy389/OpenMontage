# Executive Producer - Documentary Montage Pipeline

## When To Use

The user wants a short-to-long-form (30s-8+min) narrated documentary
piece built from existing footage — a thematic collage, essay film, or
Adam-Curtis-style tone poem, now driven by a written narration track.
The piece is NOT a talking head and NOT a single extended scene. It is
an arranged sequence of real-world clips, timed to narration, whose
meaning is carried by both the voice-over and the juxtaposition of
images (Kuleshov effect, Eisenstein's intellectual montage).

This is the right pipeline when the brief includes phrases like:

- "a montage about...",
- "show me the feeling of...",
- "like a tone poem",
- "documentary-style collage",
- "everyone who has ever..." / "the life of..." / "a portrait of...",
- "cut together from stock footage",
- "Adam Curtis", "Errol Morris", "Chris Marker".

**Narration is mandatory by default on this pipeline** (see
Cross-Stage Rules below) — a fully silent image-only cut is now the
exception, not the default, and requires an explicit user opt-out at
the idea stage.

If the user asks for an explainer, a trailer with generated clips, or
a talking-head video, pick a different pipeline.

## Philosophy

Documentary montage is retrieval-first, not generation-first.
The corpus is the raw material; the edit is the thinking. Your job
across all stages is to:

1. **Enlarge the search space before committing**. Build a corpus
   bigger than you think you need so the edit has room to breathe.
2. **Let narration and juxtaposition work together**. The voice-over
   carries the facts and the throughline; the footage carries the
   texture and the feeling. Neither should be doing the other's job —
   don't write narration that just describes what's already visually
   obvious, and don't pick footage that fights what the narration says.
3. **Trust the footage.** If a clip shows a thing plainly and the
   narration has already named it, don't over-explain with redundant
   text overlays on top of both.
4. **Pace is the message**. Cut on beat, and let each scene's duration
   follow its narration beat's length — cut short on urgent, quick
   beats; hold long on beats that carry grief/weight/awe. Slot timing
   comes from the script stage's beat durations, not a flat rule.

## Stages

| Stage | Director skill | Produces |
|-------|----------------|----------|
| `idea` | `idea-director.md` | brief (topic, tone, duration, shape, narration/music/end-tag intent) |
| `script` | `script-director.md` | script (narration text split into timed sections/beats) |
| `scene_plan` | `scene-director.md` | scene_plan (slot descriptions + queries, each tied to a script beat via `script_section_id`) |
| `assets` | `asset-director.md` | asset_manifest (corpus built + per-slot picks) |
| `edit` | `edit-director.md` | edit_decisions (timeline + transitions + music) |
| `compose` | `compose-director.md` | render_report (final mp4) |

Each director skill has its own quality gate. Read the director skill
before starting the stage.

## Core Tools

| Tool | Role |
|------|------|
| `corpus_builder` | Fans out across Pexels/Archive.org/NASA/Wikimedia/Unsplash, downloads + embeds + indexes |
| `clip_search` | Ranks clips for a slot, finds similar sets, diversifies selections |
| `video_compose` / Remotion | Renders the final timeline |

The agent talks to the stock sources through `corpus_builder` — never
call adapter classes directly from a skill or director.

## Cross-Stage Rules

- **No generated clips** unless the user explicitly asks. This pipeline
  is about REAL footage, real texture, real grain. Generated B-roll
  breaks the aesthetic.
- **Narration is MANDATORY by default.** The brief should default to
  narration + music + real footage. A silent, image-only cut is now
  the exception and requires an explicit user opt-out recorded at the
  idea stage (`brief.narration = "none"` with a
  `narration_opt_out_reason`). Removing narration after the idea stage
  has locked it in is a MAJOR change and requires user approval per
  the Decision Communication Contract, same as adding it used to be.
- **Scene/slot timing follows the script, not a fixed table.** The
  `scene_plan` stage derives slot count and duration from the
  `script` artifact's per-beat timing — one script beat can become 1-3
  scenes depending on its content and length. Do not revert to a fixed
  tone-based hold table.
- **Build the corpus before picking clips**. Do not run clip_search
  against an empty or half-built corpus. If retrieval results are
  weak (all scores < 0.25), grow the corpus with new queries.
- **Keep a decision log of rejected picks**. When you pass on a clip
  with a high score, note why (wrong era, overlit, wrong emotional
  register). This helps the review stage.

## Common Pitfalls

- Treating the corpus as a stock library to pick from sequentially
  instead of as a search index to query per slot.
- Arranging clips by score rather than by narrative beat.
- Letting visually-repetitive clips sit adjacent. Use
  `clip_search` with `operation=diversify` before locking the edit.
- Over-cutting. Documentary montage lives in the hold, not the jump.
- Quietly dropping narration or swapping the music plan because the
  edit feels "thin" or the schedule is tight. Fix the script or the
  edit; don't paper over it by silently removing a mandatory element.
- Letting the scene plan drift from the script's actual beat timing —
  if scenes are cut/held on a schedule that doesn't match what the
  narration is saying at that timestamp, the video will feel
  out of sync even if the individual visuals are good.
