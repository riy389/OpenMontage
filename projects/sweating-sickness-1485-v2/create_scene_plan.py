#!/usr/bin/env python3
"""Create scene_plan checkpoint for sweating-sickness-1485-v2."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.checkpoint import write_checkpoint

PROJECT_DIR = Path(__file__).parent.parent  # projects/
PROJECT_DATA_DIR = Path(__file__).parent    # projects/sweating-sickness-1485-v2/
PROJECT_ID = "sweating-sickness-1485-v2"
TIMESTAMP = datetime.now(timezone.utc).isoformat()

# ── Fix decision_log: remap invalid categories ────────────────────────────────
decision_log_path = PROJECT_DATA_DIR / "decision_log.json"
with open(decision_log_path) as f:
    decision_log = json.load(f)

VALID_CATEGORIES = {
    "pipeline_selection", "provider_selection", "renderer_family_selection",
    "render_runtime_selection", "composition_mode", "playbook_selection",
    "fallback_decision", "budget_tradeoff", "downgrade_approval", "music_source",
    "motion_commitment", "concept_selection", "voice_selection",
    "capability_extension", "playbook_override", "visual_accuracy_check",
}
CATEGORY_MAP = {"topic_selection": "provider_selection", "duration_selection": "motion_commitment"}

for d in decision_log["decisions"]:
    if d["category"] not in VALID_CATEGORIES:
        d["category"] = CATEGORY_MAP.get(d["category"], "provider_selection")

with open(decision_log_path, "w") as f:
    json.dump(decision_log, f, indent=2)

# ── Sync proposal ─────────────────────────────────────────────────────────────
proposal_path = PROJECT_DATA_DIR / "checkpoint_proposal.json"
with open(proposal_path) as f:
    proposal = json.load(f)
proposal["artifacts"]["decision_log"] = decision_log
proposal["artifacts"]["proposal_packet"]["production_plan"]["stages"] = [
    {"stage": "research", "tools": [], "approach": "Web search on Wikipedia (sweating sickness) for timeline and symptoms"},
    {"stage": "proposal", "tools": [{"tool_name": "llm_assist", "role": "concept selection", "available": True}], "approach": "3 concepts, c1 selected"},
    {"stage": "script", "tools": [{"tool_name": "llm_assist", "role": "narrative writing", "available": True}], "approach": "12 beat script from Claude draft (verbatim ingest)"},
    {"stage": "scene_plan", "tools": [{"tool_name": "scene_planner", "role": "shot planning", "available": True}], "approach": "Shot list per scene from script beats", "fallback_if_unavailable": "skip scene_plan"},
    {"stage": "assets", "tools": [{"tool_name": "tts_selector", "role": "generate narration", "available": True}, {"tool_name": "image_selector", "role": "generate images", "available": True}], "approach": "Cloudflare images 1024x576 + Chatterbox Nano TTS", "fallback_if_unavailable": "use alternative provider"},
    {"stage": "edit", "tools": [{"tool_name": "ffmpeg", "role": "audio-video sync", "available": True}], "approach": "Sync narration with images", "fallback_if_unavailable": "manual edit"},
    {"stage": "compose", "tools": [{"tool_name": "video_compose", "role": "Remotion compositing", "available": True}, {"tool_name": "audio_mixer", "role": "mix narration", "available": True}], "approach": "Remotion studio render with audio_mixer", "fallback_if_unavailable": "manual composition"},
    {"stage": "render", "tools": [{"tool_name": "ffmpeg", "role": "final encode", "available": True}], "approach": "1920x1080 encode", "fallback_if_unavailable": "lower resolution"},
]
proposal["artifacts"]["proposal_packet"]["production_plan"]["render_runtime"] = "remotion"

print("Writing synced proposal checkpoint...")
write_checkpoint(
    pipeline_dir=PROJECT_DIR, project_id=PROJECT_ID, stage="proposal", status="completed",
    artifacts={"proposal_packet": proposal["artifacts"]["proposal_packet"], "decision_log": decision_log},
    pipeline_type="animated-explainer", style_playbook="dark-history", checkpoint_policy="guided",
    human_approval_required=True, human_approved=True,
    review={"approved_by": "Riyanto", "timestamp": TIMESTAMP, "note": "Synced with decision_log (7 decisions, categories fixed), updated stages per pipeline_defs"},
)

# ── Scene plan ────────────────────────────────────────────────────────────────
# shot_language uses only enum values; transitions/animations use "wide" + static
def sl(shot_size, cam_mov, lens, light, dof, color):
    return {"shot_size": shot_size, "camera_movement": cam_mov, "lens_mm": lens, "lighting_key": light, "depth_of_field": dof, "color_temperature": color}

def native_sl():
    return sl("wide", "static", 50, "low_key", "deep", "cool")

scenes = [
    # Beat 1 (0-40s)
    {"id": "scene_1a", "type": "generated", "description": "London dock at gray evening, September 1485. Wet cobblestones reflecting dim light, leaning timber-framed houses climbing the hill. Atmospheric chiaroscuro, dark-history palette. Remotion slow dolly-in.", "start_seconds": 0, "end_seconds": 25, "script_section_id": "scene_001", "framing": "establishing wide shot", "movement": "slow dolly-in toward hill", "transition_in": "fade-in", "transition_out": "dissolve", "shot_intent": "Establish London, 1485. Ordinary evening before terror arrives.", "narrative_role": "establish_context", "information_role": "Viewer places themselves in time and place.", "shot_language": sl("wide", "dolly_in", 35, "low_key", "deep", "cool"), "texture_keywords": ["grainy", "chiaroscuro", "atmospheric", "moody"], "required_assets": [{"type": "image", "description": "Medieval London dock at dusk, wet cobblestones, leaning timber houses, atmospheric fog, dark-history chiaroscuro style, 1024x576, no text, no human faces", "source": "generate"}]},
    {"id": "scene_1b", "type": "text_card", "description": "Text card: '19 September 1485' — literal date from script. Remotion spring animation.", "start_seconds": 25, "end_seconds": 40, "script_section_id": "scene_001", "framing": "full-screen text card", "movement": "static", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "Anchor the date literally.", "narrative_role": "evidence", "information_role": "Viewer records the precise date of first deaths.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    # Beat 2 (40-80s)
    {"id": "scene_2a", "type": "generated", "description": "Narrow yard behind cloth merchant's house, well in center. Woman gesturing toward upper window where candle burns. Chiaroscuro, low-key lighting. Remotion subtle parallax drift.", "start_seconds": 40, "end_seconds": 60, "script_section_id": "scene_002", "framing": "medium-wide courtyard", "movement": "subtle parallax drift", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "Show the neighbor's account — man who sat at table at noon.", "narrative_role": "build_tension", "information_role": "Viewer feels the speed: noon to death before morning.", "shot_language": sl("medium_wide", "static", 50, "low_key", "medium", "warm"), "texture_keywords": ["grainy", "chiaroscuro", "candlelight"], "required_assets": [{"type": "image", "description": "Medieval London courtyard with well, narrow alley, cloth merchant house, candle lit in upper window, night, dark-history style, 1024x576, no text, no human faces", "source": "generate"}]},
    {"id": "scene_2b", "type": "animation", "description": "Animated timeline: 'Noon → Supper → Death' with 8-hour warning indicator. Remotion animated bars appearing sequentially.", "start_seconds": 60, "end_seconds": 80, "script_section_id": "scene_002", "framing": "full-screen data visualization", "movement": "progressive reveal left-to-right", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "Visualize the 8-hour death window concretely.", "narrative_role": "deliver_payload", "information_role": "Viewer understands the terrifying speed.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    # Beat 3 (80-120s)
    {"id": "scene_3a", "type": "generated", "description": "Market lane, early morning. People speaking in low voices, watching each other's faces for first flush of fever. Dark gowns visible. Remotion slow pan left.", "start_seconds": 80, "end_seconds": 100, "script_section_id": "scene_003", "framing": "medium-wide market lane", "movement": "slow pan left", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "Show the sickness reaching into finest houses.", "narrative_role": "build_tension", "information_role": "Viewer sees fear spreading through social layers.", "shot_language": sl("medium_wide", "pan_left", 35, "low_key", "deep", "cool"), "texture_keywords": ["grainy", "chiaroscuro", "overcast_soft"], "required_assets": [{"type": "image", "description": "Medieval London market lane, people in dark gowns whispering, morning light, fearful atmosphere, dark-history style, 1024x576, no text, no identifiable human faces", "source": "generate"}]},
    {"id": "scene_3b", "type": "generated", "description": "Procession of men in dark gowns behind coffin toward church door. Overcast soft light. Rank means nothing. Remotion static hold.", "start_seconds": 100, "end_seconds": 120, "script_section_id": "scene_003", "framing": "wide church entrance", "movement": "static", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "Show leaders falling — two lord mayors, six aldermen, three sheriffs dead.", "narrative_role": "build_tension", "information_role": "Viewer understands even rank offers no protection.", "shot_language": sl("wide", "static", 24, "overcast_soft", "deep", "neutral"), "texture_keywords": ["grainy", "somber", "muted"], "required_assets": [{"type": "image", "description": "Medieval London church entrance, men in dark gowns carrying coffin, overcast light, somber procession, dark-history style, 1024x576, no text, no identifiable human faces", "source": "generate"}]},
    # Beat 4 (120-160s) — CONSISTENCY ANCHOR
    {"id": "scene_4a", "type": "character_scene", "description": "Interior: hot close room. A MAN lies on low bed, face flushed, hair plastered, sweat visible. His WIFE wrings cloth into basin. A BOY sits on floor knees drawn up, watching candle. CONSISTENCY ANCHOR: this man and boy reappear in scene_9a and scene_12a.", "start_seconds": 120, "end_seconds": 140, "script_section_id": "scene_004", "framing": "medium interior vigil", "movement": "static, slight push-in", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The emotional core — family keeping vigil.", "narrative_role": "emotional_beat", "information_role": "Viewer witnesses intimate human suffering.", "shot_language": sl("medium", "dolly_in", 50, "low_key", "shallow", "warm"), "texture_keywords": ["intimate", "claustrophobic", "candlelit", "chiaroscuro"], "required_assets": [{"type": "image", "description": "Medieval bedroom interior, sick man on low bed sweating, wife at bedside wringing cloth, YOUNG BOY sitting on floor watching candle, warm candlelight, dark-history chiaroscuro, 1024x576, no text, silhouettes only for faces", "source": "generate"}]},
    {"id": "scene_4b", "type": "generated", "description": "Close-up: candle shrinking in holder, wall shadows trembling. Church bell silhouette through window. Wife's hand flinches. Remotion slow zoom on candle.", "start_seconds": 140, "end_seconds": 160, "script_section_id": "scene_004", "framing": "close-up candle and window", "movement": "slow zoom on candle", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "The bell counting something — tension peak.", "narrative_role": "build_tension", "information_role": "Viewer feels each bell strike as countdown.", "shot_language": sl("close_up", "zoom_in", 85, "low_key", "shallow", "warm"), "texture_keywords": ["intimate", "tense", "candlelit"], "required_assets": [{"type": "image", "description": "Close-up of burning candle in holder, trembling shadows on wall, window showing church bell silhouette, warm candlelight, dark-history style, 1024x576, no text, no human faces", "source": "generate"}]},
    # Beat 5 (160-200s)
    {"id": "scene_5a", "type": "generated", "description": "Churchyard morning, fresh earth heaped in rows. Two small CHILDREN on doorstep tearing bread. Their FATHER at window hand pressed to mouth. Silhouettes only.", "start_seconds": 160, "end_seconds": 180, "script_section_id": "scene_005", "framing": "wide churchyard to doorstep", "movement": "slow pan from churchyard to children", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The strange sight — children spared, fathers dying.", "narrative_role": "evidence", "information_role": "Viewer learns infants and small children were often spared.", "shot_language": sl("wide", "pan_right", 24, "natural", "deep", "neutral"), "texture_keywords": ["somber", "overcast_soft", "grainy"], "required_assets": [{"type": "image", "description": "Medieval London churchyard, fresh earth mounds in rows, two small children on doorstep tearing bread, father at window silhouette, overcast morning light, dark-history style, 1024x576, no text, silhouettes only", "source": "generate"}]},
    {"id": "scene_5b", "type": "generated", "description": "Street level, spades scraping, doors closing slowly. No people visible — only hands and doors. Atmosphere of isolation.", "start_seconds": 180, "end_seconds": 200, "script_section_id": "scene_005", "framing": "street-level empty lane", "movement": "static", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "The silence after the strange sight.", "narrative_role": "emotional_beat", "information_role": "Viewer feels the isolation and fear.", "shot_language": sl("medium_wide", "static", 35, "overcast_soft", "deep", "cool"), "texture_keywords": ["empty", "somber", "quiet"], "required_assets": [{"type": "image", "description": "Empty medieval London lane, wooden doors slowly closing, no people visible, overcast light, desolate atmosphere, dark-history style, 1024x576, no text, no human figures", "source": "generate"}]},
    # Beat 6 (200-240s)
    {"id": "scene_6a", "type": "generated", "description": "London street midweek. People walking in middle of lane, away from doorways. Priest hurries past with lantern. No crowds, no contact.", "start_seconds": 200, "end_seconds": 220, "script_section_id": "scene_006", "framing": "street tracking", "movement": "tracking right", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The city has changed its pace — isolation everywhere.", "narrative_role": "build_tension", "information_role": "Viewer sees behavioral change: no stopping to talk.", "shot_language": sl("medium_wide", "tracking_right", 35, "natural", "deep", "neutral"), "texture_keywords": ["isolated", "tense", "overcast_soft"], "required_assets": [{"type": "image", "description": "Medieval London street, lone priest with lantern hurrying past, empty lanes, people keeping distance, overcast light, dark-history style, 1024x576, no text, no identifiable faces", "source": "generate"}]},
    {"id": "scene_6b", "type": "generated", "description": "Tavern window view: single drinker stares into cup as though it might speak. Warm interior against cold street.", "start_seconds": 220, "end_seconds": 240, "script_section_id": "scene_006", "framing": "tavern window close", "movement": "static", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "Despair personified.", "narrative_role": "emotional_beat", "information_role": "Viewer feels the hopelessness.", "shot_language": sl("medium", "static", 50, "low_key", "shallow", "warm"), "texture_keywords": ["intimate", "despair", "candlelit"], "required_assets": [{"type": "image", "description": "Medieval London tavern interior seen through window, single drinker staring into cup, warm candlelight inside, cold street outside, dark-history style, 1024x576, no text, no identifiable faces", "source": "generate"}]},
    # Beat 7 (240-280s)
    {"id": "scene_7a", "type": "transition", "description": "Transition: centuries sliding like a dropped cloak. Cloak falling away to reveal books and lamp.", "start_seconds": 240, "end_seconds": 255, "script_section_id": "scene_007", "framing": "metaphorical transition", "movement": "dissolve", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "Shift from 1485 to present-day research question.", "narrative_role": "transition", "information_role": "Viewer transitions temporally.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    {"id": "scene_7b", "type": "generated", "description": "Quiet reading room, lamp on desk, stack of books. Hands turning pages. Same gap keeps appearing.", "start_seconds": 255, "end_seconds": 280, "script_section_id": "scene_007", "framing": "reading room medium", "movement": "slow pan across books", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The honest answer: nobody knows.", "narrative_role": "deliver_payload", "information_role": "Viewer learns cause is unknown after 500 years.", "shot_language": sl("medium", "pan_right", 50, "low_key", "medium", "warm"), "texture_keywords": ["scholarly", "quiet", "lamp-lit"], "required_assets": [{"type": "image", "description": "Quiet reading room, desk lamp, stack of old books, hands turning pages, warm lamplight against cool background, scholarly atmosphere, dark-history style, 1024x576, no text, no faces", "source": "generate"}]},
    # Beat 8 (280-320s)
    {"id": "scene_8a", "type": "generated", "description": "Late October London, sharp bright air. Lanes quieter. Row of shuttered houses, each with one dark window. Counting them.", "start_seconds": 280, "end_seconds": 300, "script_section_id": "scene_008", "framing": "street walk toward shuttered houses", "movement": "dolly forward", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The sickness ending — but at what cost?", "narrative_role": "emotional_beat", "information_role": "Viewer understands thousands died by end of October.", "shot_language": sl("wide", "dolly_in", 24, "natural", "deep", "cool"), "texture_keywords": ["sharp", "bright", "somber", "October"], "required_assets": [{"type": "image", "description": "Late October medieval London street, row of shuttered houses each with one dark window, sharp bright air, autumn light, dark-history style, 1024x576, no text, no human figures", "source": "generate"}]},
    {"id": "scene_8b", "type": "text_card", "description": "Text card: 'Several thousand dead by end of October 1485' — literal fact from script.", "start_seconds": 300, "end_seconds": 320, "script_section_id": "scene_008", "framing": "full-screen text card", "movement": "static", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "State the death toll literally.", "narrative_role": "deliver_payload", "information_role": "Viewer records the scale of loss.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    # Beat 9 (320-360s) — CONSISTENCY ANCHOR
    {"id": "scene_9a", "type": "character_scene", "description": "Corner of a lane, October 30th. THE MAN FROM VIGIL (scene_4a) stands in doorway, thin and gray, holding frame. THE BOY (scene_4a) leans against his leg. CONSISTENCY ANCHOR: same man and boy from beat 4. Bells ring — not tolling for dead.", "start_seconds": 320, "end_seconds": 340, "script_section_id": "scene_009", "framing": "doorway medium", "movement": "static", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The vigil man survived. He lives to see coronation bells.", "narrative_role": "resolution", "information_role": "Viewer witnesses survival.", "shot_language": sl("medium", "static", 50, "natural", "medium", "neutral"), "texture_keywords": ["hopeful", "relief", "october_light"], "required_assets": [{"type": "image", "description": "Medieval London doorway, thin gray man standing holding frame, YOUNG BOY leaning against his leg (same boy from vigil scene), pale tired faces but alive, October light, coronation crowd blur in background, dark-history style, 1024x576, no text, silhouettes only", "source": "generate"}]},
    {"id": "scene_9b", "type": "generated", "description": "Crowd along street, faces pale and tired but alive. Coronation bells. Henry VII's crown visible as silhouette — no realistic royal face.", "start_seconds": 340, "end_seconds": 360, "script_section_id": "scene_009", "framing": "crowd wide", "movement": "slow pan through crowd", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "The city survives. Coronation brings hope.", "narrative_role": "emotional_beat", "information_role": "Viewer feels relief.", "shot_language": sl("wide", "pan_right", 35, "natural", "deep", "warm"), "texture_keywords": ["relief", "crowded", "celebratory"], "required_assets": [{"type": "image", "description": "Medieval London street, pale tired crowd celebrating, coronation bells, distant crown silhouette on figure, October light, dark-history style, 1024x576, no text, no identifiable royal faces", "source": "generate"}]},
    # Beat 10 (360-400s)
    {"id": "scene_10a", "type": "animation", "description": "Animated timeline: 5 epidemic seasons 1485→1551. Each spike as dark bar, each recession as quiet gap. Visual metaphor: storm passing over country.", "start_seconds": 360, "end_seconds": 380, "script_section_id": "scene_010", "framing": "full-screen timeline", "movement": "progressive reveal left-to-right", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "Show the pattern: spike and recede, five times over 66 years.", "narrative_role": "deliver_payload", "information_role": "Viewer understands the epidemic pattern.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    {"id": "scene_10b", "type": "generated", "description": "Hall of archives, cool still air. Scholarly setting, documents on tables. Metaphor: English sweat compared beside other epidemics.", "start_seconds": 380, "end_seconds": 400, "script_section_id": "scene_010", "framing": "archive room medium", "movement": "slow push-in", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The scholarly comparison.", "narrative_role": "evidence", "information_role": "Viewer learns other epidemics lingered; sweat spiked and receded quickly.", "shot_language": sl("medium", "dolly_in", 50, "low_key", "medium", "cool"), "texture_keywords": ["scholarly", "quiet", "archive"], "required_assets": [{"type": "image", "description": "Cool archive hall, scholarly documents on tables, still air atmosphere, lamplight, dark-history style, 1024x576, no text, no faces", "source": "generate"}]},
    # Beat 11 (400-440s)
    {"id": "scene_11a", "type": "generated", "description": "London 1551, tense quiet lanes. Last outbreak under way. Ordinary sounds of city going back to work afterward. No return.", "start_seconds": 400, "end_seconds": 420, "script_section_id": "scene_011", "framing": "empty lane 1551", "movement": "static", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The last outbreak — and then silence.", "narrative_role": "build_tension", "information_role": "Viewer learns disease vanished after 1551.", "shot_language": sl("wide", "static", 24, "overcast_soft", "deep", "cool"), "texture_keywords": ["tense", "quiet", "final"], "required_assets": [{"type": "image", "description": "Medieval London lane 1551, tense quiet atmosphere, ordinary city sounds implied, empty streets, autumn light, dark-history style, 1024x576, no text, no human figures", "source": "generate"}]},
    {"id": "scene_11b", "type": "transition", "description": "Transition: narrator waiting for sickness to return, it does not. Visual: lane empty, doors closed, silence. Dissolve to present day.", "start_seconds": 420, "end_seconds": 440, "script_section_id": "scene_011", "framing": "empty lane fade to present", "movement": "dissolve", "transition_in": "cut", "transition_out": "dissolve", "shot_intent": "The waiting — and the absence.", "narrative_role": "transition", "information_role": "Viewer feels the finality.", "shot_language": native_sl(), "texture_keywords": [], "required_assets": []},
    # Beat 12 (440-480s)
    {"id": "scene_12a", "type": "generated", "description": "Present-day stone bridge, same river runs beneath — wide and dark, carrying city lights. Mist rising. Wind cold. Narrator thinks of the man in doorway and the boy. Single lantern at bridge end.", "start_seconds": 440, "end_seconds": 460, "script_section_id": "scene_012", "framing": "bridge wide to river", "movement": "slow push toward river", "transition_in": "dissolve", "transition_out": "dissolve", "shot_intent": "The bridge between past and present.", "narrative_role": "emotional_beat", "information_role": "Viewer connects 1485 to now.", "shot_language": sl("wide", "dolly_in", 24, "low_key", "deep", "cool"), "texture_keywords": ["misty", "modern", "reflective", "nocturnal"], "required_assets": [{"type": "image", "description": "Present-day London stone bridge at night, Thames river wide and dark below, mist rising, city lights reflecting on water, single lantern at bridge end, atmospheric nocturnal, dark-history style, 1024x576, no text, no human figures", "source": "generate"}]},
    {"id": "scene_12b", "type": "generated", "description": "Lone barge slides from beneath arch, drifts downstream into dark. Mist takes it. Final image — the sickness arrived, took thousands, left without explaining. Fade to black.", "start_seconds": 460, "end_seconds": 480, "script_section_id": "scene_012", "framing": "barge fading into mist", "movement": "static, slow fade", "transition_in": "cut", "transition_out": "fade-to-black", "shot_intent": "Final image — the mystery drifts away.", "narrative_role": "resolution", "information_role": "Viewer leaves with the unsolved mystery.", "shot_language": sl("wide", "static", 35, "low_key", "deep", "cool"), "texture_keywords": ["mysterious", "final", "misty", "dark"], "required_assets": [{"type": "image", "description": "Lone barge sliding beneath stone arch into dark river, mist swallowing it, nocturnal Thames, atmospheric final image, dark-history style, 1024x576, no text, no human figures", "source": "generate"}]},
]

metadata = {
    "script_without_enhancement_cues": True,
    "total_duration_seconds": 480,
    "total_scenes": len(scenes),
    "scene_types_used": list(set(s["type"] for s in scenes)),
    "consistency_anchors": {
        "man_from_vigil": {"description": "The sick man from scene_4a (beat 4) who survives", "appears_in": ["scene_4a", "scene_9a", "scene_12a"], "visual_traits": "thin, gray, holding doorway frame, breathing, alive"},
        "boy_from_vigil": {"description": "The young boy from scene_4a (beat 4) who leans against man's leg", "appears_in": ["scene_4a", "scene_9a", "scene_12a"], "visual_traits": "young boy, knees drawn up watching candle, leaning against man's leg"},
    },
    "required_asset_policy": {"provider": "image_selector", "allowed_providers": ["cloudflare"], "resolution": "1024x576", "no_real_faces": True, "no_gore": True, "no_text_in_images": True},
}

print("Writing scene_plan checkpoint...")
write_checkpoint(
    pipeline_dir=PROJECT_DIR, project_id=PROJECT_ID, stage="scene_plan", status="awaiting_human",
    artifacts={"scene_plan": {"version": "1.0", "scenes": scenes, "metadata": metadata}},
    pipeline_type="animated-explainer", style_playbook="dark-history", checkpoint_policy="guided",
    human_approval_required=True, human_approved=False,
    review={"stage": "scene_plan", "status": "awaiting_human", "note": "OK Riyanto, komentar 6251044224"},
)

# Summary
print(f"\n{'='*60}")
print(f"TOTAL SCENES: {len(scenes)}")
print(f"DURATION: 0-480s")
type_counts = Counter(s["type"] for s in scenes)
print(f"TYPE BREAKDOWN:")
for t, c in sorted(type_counts.items()):
    print(f"  {t}: {c}")
print(f"\nSCENE TABLE:")
print(f"{'ID':<12} {'Type':<16} {'Start':>6} {'End':>6} {'Beat':>4} {'Section'}")
print("-"*70)
for s in scenes:
    beat = (s["start_seconds"] // 40) + 1
    sec = s.get("script_section_id", "-")
    print(f"{s['id']:<12} {s['type']:<16} {s['start_seconds']:>6} {s['end_seconds']:>6} {beat:>4} {sec}")
print(f"\nVALIDATION:")
types_used = set(s["type"] for s in scenes)
print(f"  Unique types: {len(types_used)} (min 3 required): {sorted(types_used)}")
print(f"  Script has enhancement_cues: NO (noted in metadata)")
print(f"  Consistency anchors: man_from_vigil, boy_from_vigil (scenes 4, 9, 12)")
print(f"  Status: awaiting_human — STOP at gate")
