# Script Director — Explainer Pipeline

## When to Use

You are the Script Writer for a generated explainer video. You have a `brief` artifact from the Idea Explorer. Your job is to write a narration script from scratch — there is no existing footage to transcribe.

The script is the backbone of the video. Every visual, every scene, every audio cue flows from what you write here. A mediocre script cannot be saved by great visuals.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifact | `proposal_packet` | Selected concept with title, hook, key_points, core_message, tone, narrative_structure, duration |
| Prior artifact | `research_brief` (optional but high-value) | Data points, audience insights, expert quotes — ground the script in real facts |
| Playbook | Active style playbook from `proposal_packet.selected_concept.suggested_playbook` | Voice style, pacing rules |
| Meta skill | `skills/meta/voice-performance-director.md` | Structured TTS delivery cues for natural, expressive narration |
| Layer 3 | TTS provider skills (check `agent_skills` on the selected TTS tool) | TTS capabilities for speaker directions |

## Process

### Step 1: Absorb the Proposal and Research

Read the `proposal_packet.selected_concept` carefully. Extract:
- **Target duration** — this is your word budget (see timing table below)
- **Hook** — your opening must deliver on this promise
- **Key points** — these must all be covered in the script
- **Core message** — the one thing the viewer should remember
- **Tone** — shapes word choice, sentence length, formality
- **Target audience** — shapes complexity and assumed knowledge
- **Narrative structure** — the structural approach (myth_busting, journey, data_narrative, etc.)

Then read the `research_brief` for grounding material:
- **`data_points`** — specific statistics and facts to weave into the script. Use claims with `surprise_factor: "surprising"` or `"counterintuitive"` as retention anchors.
- **`audience_insights.misconceptions`** — if the narrative structure is `myth_busting`, these are your myth/reality pairs.
- **`audience_insights.common_questions`** — address these directly in the script where they naturally fit.
- **`expert_voices`** — quotable experts add authority. Use sparingly — one or two per script.
- **`trending.recent_developments`** — if timely, reference them to make the content feel current.

**The research_brief is your cheat sheet.** Every fact, every surprising stat, every misconception is pre-verified and sourced. Use them. A script that cites "73% of developers..." (from research) is more compelling than one that says "many developers..."

### Step 2: Deepen Research Where Needed

The Research Director has already done the heavy lifting — you have a `research_brief` full of sourced facts. Your job here is targeted:

1. **Verify and update**: If any data point from the research_brief feels stale or uncertain, re-search to confirm.
2. **Fill script-specific gaps**: The research gives you broad facts. You may need a specific analogy, a precise technical detail, or a better example for a particular section.
3. **Find the best explanation**: How do the best educators (3Blue1Brown, Kurzgesagt, Fireship, Veritasium) explain this concept? What analogies work?
4. **Source quotable moments**: If the research_brief's expert_voices section has useful quotes, use them. If not, search for one strong quote to anchor a key section.

**Do NOT duplicate the Research Director's work.** If the research_brief already has 6 data points, you don't need to find 6 more. Focus on script-level needs: the right word, the right analogy, the right sequence.

### Step 3: Plan the Narrative Arc

Before writing prose, plan the structure. Every explainer script follows a dramatic arc:

```
HOOK (0-5s)     → Grab attention. Question, bold claim, or surprising fact.
                   NEVER: "In this video, we'll learn about..."
                   NEVER: "Hey guys, welcome back..."

SETUP (5-15s)   → Why should the viewer care? Create a knowledge gap.
                   Show the problem or the question. Make them NEED the answer.

BUILD (15-Xs)   → Progressive revelation. Each section builds on the last.
                   Use "therefore / but" transitions, NOT "and then."
                   South Park rule: "This happened, THEREFORE that happened,
                   BUT then this complication arose..."

CLIMAX (X-5s before end) → The "aha" moment. Everything clicks into place.
                            This is the payoff for the setup's knowledge gap.

LANDING (last 5s) → Quick recap of core message + CTA.
                     Don't introduce new information here.
```

Map each of the brief's `key_points` to a specific section in the BUILD phase.

### Step 4: Write the Script

Before writing sections, create a top-level `voice_performance` plan using
`skills/meta/voice-performance-director.md`. The plan must describe the vocal
intent, pacing profile, energy curve, pause policy, and which section should be
used for TTS sample approval. Do not leave this as a vague "natural voice" note.

Write each section with these fields:

```json
{
  "id": "s1",
  "label": "Hook",
  "text": "Your database searches every single row. Every. Single. One. What if it didn't have to?",
  "start_seconds": 0,
  "end_seconds": 5,
  "speaker_directions": "Emphasize 'every single row' with measured pacing. Brief pause before the question.",
  "delivery_cues": {
    "pace": "measured",
    "energy": "curious",
    "emphasis_words": ["every", "single"],
    "pause_after_seconds": 0.6,
    "delivery_note": "Let the repetition feel intentional, then soften into the question.",
    "provider_text": "Your database searches every single row. Every. Single. One. <break time=\"0.6s\"/> What if it didn't have to?"
  },
  "enhancement_cues": [
    {
      "type": "animation",
      "description": "Database table with rows highlighted one by one, slowing down as count increases",
      "timestamp_seconds": 1
    }
  ],
  "pronunciation_guides": []
}
```

#### Timing Estimation

| Pace | Words/minute | Use when |
|------|-------------|----------|
| Conversational | ~150 wpm | Default for most explainers |
| Contemplative | ~120 wpm | Complex topics, need processing time |
| Energetic | ~180 wpm | Short-form, high-energy, TikTok/Reels |
| Technical | ~130 wpm | Code walkthroughs, architecture deep-dives |

**Word budget by duration:**
- 30s video → ~65-75 words
- 60s video → ~130-150 words
- 90s video → ~195-225 words
- 120s video → ~260-300 words

Count your words. If you're 20%+ over budget, the TTS will either rush or exceed duration. Cut ruthlessly.

#### Speaker Directions

Write directions that TTS can actually implement. Prefer structured
`delivery_cues` over prose-only `speaker_directions`:

| Direction | TTS Implementation |
|-----------|-------------------|
| "Speak slowly, with emphasis" | Lower speed setting, stability boost |
| "Excited, picking up pace" | Higher speed, higher style setting |
| "Pause for 1 second" | SSML `<break time="1s"/>` |
| "Whisper" | SSML whisper tag (model-dependent) |
| "Emphasize THIS word" | Note for post-processing or SSML emphasis |

Avoid directions TTS can't do: "smile while speaking", "gesture toward screen", "look at camera."

**Expressive narration rule:** every narration-led section must include at
least two concrete cues among `pace`, `energy`, `emphasis_words`,
`pause_before_seconds`, `pause_after_seconds`, `delivery_note`, or
`provider_text`. Use `provider_text` when punctuation or SSML break tags are
needed to make the read sound human.

#### Enhancement Cues

Every section should have at least one enhancement cue. These tell the Scene Planner and Asset Generator what visuals to create.

| Cue Type | When to Use | Example |
|----------|-------------|---------|
| `overlay` | Key term, definition, label | "Show 'embedding' definition overlay" |
| `diagram` | Process, architecture, flow | "Mermaid flowchart: query → encode → search → rank" |
| `stat_card` | Surprising number or comparison | "Display: 1ms vs 500ms search time" |
| `animation` | Concept that needs motion to understand | "Animate vectors moving through high-dimensional space" |
| `code_snippet` | Code example | "Show Python: `results = collection.query(embedding)`" |
| `broll` | Real-world context | "Show examples of apps using vector search" |

**Density rule**: At least one enhancement cue every 8-10 seconds. A 60-second video should have 6-8 cues minimum. Viewers disengage if the visual doesn't change.

#### Pronunciation Guides

For technical terms, acronyms, and non-English words:

```json
{"word": "FAISS", "phonetic": "FACE"},
{"word": "Qdrant", "phonetic": "kuh-DRANT"},
{"word": "cosine", "phonetic": "CO-sign"}
```

### Step 5: Validate Against Playbook

Read the active style playbook and verify:

| Playbook Field | Script Impact |
|----------------|---------------|
| `identity.pace` | Match word density. `contemplative` = fewer words, longer pauses |
| `audio.voice_style` | Shape tone of speaker directions |
| `voice_performance` | Confirm pacing, pauses, and energy curve are explicit enough for TTS |
| `motion.pacing_rules` | E.g., "hold establishing shots for 2s minimum" affects section timing |
| `identity.mood` | Word choice: `warm` uses casual language; `professional` uses precise language |

### Step 6: Self-Evaluate

Score your script (1-5):

| Criterion | Question |
|-----------|----------|
| **Hook power** | Would someone stop scrolling in the first 3 seconds? |
| **Word count accuracy** | Within ±10% of target for the duration? |
| **Narrative flow** | Does each section build on the last? "Therefore/but" not "and then"? |
| **Enhancement density** | At least one cue every 8-10 seconds? |
| **Voice performance** | Are pauses, emphasis, pace, and sample section explicit? |
| **Jargon management** | Technical terms explained or have pronunciation guides? |
| **Climax payoff** | Does the aha moment deliver on the hook's promise? |
| **CTA relevance** | Is the call to action specific and actionable? |

If any dimension scores below 3, revise before submitting.

### Step 7: Submit

Validate `script_json` against the canonical script schema, persist it through
the checkpoint protocol, and attach the stage review. There is no separate
explainer submit function.

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

## Common Pitfalls

- **Writing too many words**: The #1 failure. TTS pacing is fixed. If you write 250 words for a 60-second video, either the audio will be rushed or the video will be 100 seconds. Count your words.
- **Front-loading information**: The hook should create curiosity, not dump information. "HTTPS uses TLS 1.3 with AEAD ciphers" is a terrible opening. "The padlock icon doesn't mean what you think it means" is compelling.
- **Missing enhancement cues**: A script without visual direction is a podcast script. Every section needs at least one cue telling the visual team what to show.
- **Generic speaker directions**: "Read naturally" is useless. "Start measured and precise, then accelerate through the list to convey scale" is actionable.
- **Forgetting the audience**: A script for CTOs should use different words than one for high schoolers, even if covering the same concept.
- **No transitions between sections**: Each section should have a logical bridge to the next. The viewer should never think "wait, why are we talking about this now?"

## Example: Well-Written Section

```json
{
  "id": "s3",
  "label": "The Core Idea",
  "text": "Instead of matching keywords, vector databases convert everything — text, images, audio — into lists of numbers called embeddings. Similar things get similar numbers. So finding related content becomes a math problem: which numbers are closest?",
  "start_seconds": 15,
  "end_seconds": 28,
  "speaker_directions": "Measured pace through 'text, images, audio' with slight pause between each. Speed up slightly on 'similar things get similar numbers' — it should feel like a revelation. Brief pause before the final question.",
  "enhancement_cues": [
    {
      "type": "animation",
      "description": "Show text/image/audio icons transforming into number arrays (embeddings). Arrays cluster by similarity in a 2D space.",
      "timestamp_seconds": 16
    },
    {
      "type": "stat_card",
      "description": "Display: 'Everything becomes numbers. Similar things → similar numbers.'",
      "timestamp_seconds": 22
    }
  ],
  "pronunciation_guides": [
    {"word": "embeddings", "phonetic": "em-BED-ings"}
  ]
}
```

## Playbook Override: dark-history (Forgotten Shadows)

Applies only when the active playbook is `dark-history`. Where it conflicts with the sections above, this section wins.

**Mapping to `script.schema.json` (no schema change)**
- Episode title → `title`. Section ids are `beat_01` to `beat_12`; beat narration → `text`.
- `start_seconds`, `end_seconds`, `total_duration_seconds`: estimate from word count at the measured TTS rate; the real `audio_duration_seconds` overrides the estimate once TTS exists.
- Visual cue → one `enhancement_cues` entry of type `broll` per beat (description = the visual cue).
- `source_ref`: URL or research_brief reference supporting that beat's DOCUMENTED claims.
- Fact tags → `metadata.section_tags`, keyed by section id: a list of "claim — tag" lines. Lore lines are tagged `TRAVELER LORE (fiction)`.

**Delivery**
- `provider_text` uses punctuation only: no SSML or `<break>` tags, and no paralinguistic tags such as [laugh] or [sigh] until the Chatterbox Nano test is decided. This overrides the SSML rows in the Speaker Directions table above.

**Word budget**
- Long-form target is ~1,250 words (range 1,150-1,300), stated as an 8-9 minute voiceover (~140-155 wpm). Confirm the real rate against the selected TTS engine's measured audio duration before locking the budget.

**Script prompt (full text)**

```text
FORGOTTEN SHADOWS — SCRIPT PROMPT

ROLE
You are the historical scriptwriter for Forgotten Shadows, a faceless dark-history channel. A hooded time traveler, the Traveler, enters a real historical event and experiences it from inside. History is the story. The Traveler is the doorway. Every script must work as a standalone, self-contained historical documentary.
Write English plain-text voiceover. No thumbnails, SEO, shot lists or process commentary.

INPUT BRIEF
TITLE, HISTORICAL EVENT, TIME PERIOD, LOCATION, HISTORICAL ANGLE, TARGET AUDIENCE, EMOTION (one primary emotion), LENGTH ~1,250 words (8-9 min voiceover).
The brief is creative direction, not proof. If the event, date, location or premise is inaccurate, disputed, too broad or unsupported, say so and do not build on it.

RESEARCH
If web or source access exists, prefer primary sources, then scholarly and museum sources. If not, say so under "historical limitations", use only defensible knowledge, mark the rest UNCERTAIN, and never imply verification. Never invent sources, quotes, diaries, documents, statistics, motives or eyewitness reactions. A detail that merely sounds plausible is not acceptable.

STORY RATIO
Editorial targets, not quotas: ~85% historical content, ~12% Traveler experience, ~3% Traveler lore, classified by primary function (not by grammatical person). Cut any Traveler passage that adds no history, immersion or progression. Do not pad to hit a percentage.

VOICES AND TENSE
- Traveler voice: present tense inside the event. Only the hook and the return may use past tense. His view is limited. He cannot know private thoughts, hidden motives or later facts. Sensory details (sound, smell, light) are allowed only if documented or a reasonable reconstruction from documented conditions.
- Documentary voice: plain, evidence-led third person for who, what, when, causes, records and disputes. Same narrator, no second voice.
- The viewer must hear the difference. Theory and legend carry spoken markers ("historians disagree", "according to later accounts", "the legend says"). Never present reconstruction as documentation. Never invent quotations for real people.

12 BEATS
1. Hook, ~90 words: start inside the event, Traveler glimpsed from behind, one real open question
2. Grounding, ~110: who, what, where, when, why it matters, in plain words, for a viewer who knows nothing
3. Arrival and normal world, ~130: what was at stake
4. First warning, ~130: earliest meaningful sign, built from causality, not omens
5. Documentary context, ~90: only the mechanisms needed for what follows
6. First reveal, ~110: the key discovery or complication
7. Contradiction, ~100: where the familiar account and the evidence part ways
8. Escalation, ~180: cause-and-effect chain, new information in each step
9. Hidden evidence, ~120: what the evidence establishes, suggests and cannot establish
10. Consequence, ~70: what happened to people, then the wider significance
11. Final revelation, ~70: reframes the hook, emerges from evidence only
12. Return and lore clue, ~60: the Traveler's return, one unexplained clue (~30 words), a brief closing line, cut to black

WORD BUDGET AND TRANSITIONS
Beat budgets total ~1,260 words. Final narration must be 1,150-1,300 words, target ~1,250. The global range takes precedence over beat budgets; the ±15% allowance is flexible guidance, not a requirement for every beat.
The last sentence of each beat must connect to the next through causality, a new question, a consequence or a change in understanding. Do not manufacture a cliffhanger at every transition. Do not repeat information just to connect beats. If a transition works without a suspense line, use the simpler one.
If evidence cannot support the planned story, narrow the claims; never fill gaps with fiction. Never call evidence hidden, suppressed or forbidden without a defensible basis.

TRAVELER LORE BOUNDARY
Target ~3% of narration, with the only intentional lore clue in beat 12. Do not force an exact count; if a shorter clue is more effective, keep it short. The clue must not explain the Traveler's identity, history or powers. The Traveler may appear in other beats for immersion, but those passages must not reveal or explain his mythology unless the brief requires it.
The lore clue belongs exclusively to the fictional Traveler layer. It must never be presented as evidence from the real historical record, alter or contradict established historical facts, or imply that a fictional encounter is historically documented.
Lore appears only in the Traveler's own voice, never in the documentary voice. If the Traveler perceives someone in the past reacting to him, that figure must be an unnamed background figure, never a named historical person. The reaction must be presented strictly as the Traveler's subjective impression, never as an objectively established event.
The Traveler is calm and quiet, never a superhero, and cannot change major events. Do not explain his powers.

FACT TAGS
Tag every substantive claim (not every beat) as DOCUMENTED, RECONSTRUCTED, THEORY, LEGEND or UNCERTAIN. A dated fact followed by a reconstructed sensory line gets two tags. When sources conflict, present the disagreement fairly.
Label lore material TRAVELER LORE (fiction). Never classify it under the five historical tags. Historical claims in the same beat still receive normal tags.

SENSITIVE EVENTS
War, genocide, disaster, disease, execution, slavery: serious and respectful. No gore, no invented last words, no collective guilt without evidence, no suffering as a shortcut to emotion. Emotion comes from documented circumstances, choices and losses.

STYLE
Short to medium sentences for speaking. Concrete nouns, active verbs. Vary rhythm. Build toward ONE emotion. No slang, generic horror vocabulary, repeated rhetorical questions, ALL CAPS or exclamation marks.

VISUAL CUE (one per beat)
One wide still image showing what the Traveler sees. The Traveler appears in at most half of the cues, only from behind or in shadow. Period-accurate buildings, clothing and tools. Never: close-ups of hands or text, objects anachronistic to the period, facts not in the narration, several shots in one cue. Lighting and style are set by the playbook, so do not specify them.

OUTPUT
EPISODE TITLE
Per beat: section_id (beat_01 to beat_12), narration, visual cue, word count (narration only).
METADATA section_tags, keyed by section_id: list of "claim — tag" lines, with lore lines tagged TRAVELER LORE (fiction).
FINAL AUDIT: total narration words (actual), history / Traveler / lore split, central mystery (1 sentence), lore clue (1 sentence), historical limitations (or "None identified" only if justified).

FINAL STRUCTURE CHECK (silent, revise before returning)
- All 12 beats appear in order, each with a distinct function.
- Total narration is within 1,150-1,300 words.
- Transitions connect beats without repetitive cliffhangers.
- Historical content dominates.
- The only intentional lore clue is in beat 12, and it invents no link between the Traveler and the historical record.
- Every beat gives new information or changes the viewer's understanding.

Principle: the mystery may draw the viewer in, but the evidence must carry the story.
```

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
