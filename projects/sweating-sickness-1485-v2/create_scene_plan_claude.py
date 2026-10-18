#!/usr/bin/env python3
"""T1 v2 scene_plan (Claude). Run: python3 create_scene_plan_claude.py
Writes scene_plan_draft_claude.json (artifact object). Ingest verbatim via write_checkpoint.
Timings are PROVISIONAL (equal 40s per beat); re-sync to word-level timestamps after TTS."""
import json, sys

SFX = ", dark-history style, chiaroscuro, grainy, muted palette, 1024x576, no text, no readable writing, no gore"
MAN = "lean man in his thirties, short dark hair, plain undyed linen shirt, face in shadow"
WIFE = "woman in a plain brown wool kirtle and white linen coif, face in shadow"
BOY = "boy of about seven, cropped hair, oversized russet wool tunic, bare feet, face in shadow"

# id,type,start,end,beat,desc,framing,movement,cam,size,lens,light,dof,temp,role,intent,info,kw,prompt,overlay
R = []
def s(*a): R.append(a)
A, G, C, T, X = "animation", "generated", "character_scene", "text_card", "transition"

# BEAT 1
s("1a",A,0,8,1,"Hook: ring-shaped 8-hour countdown draining on black, ember glow. Label '8 hours'.","full-screen motion graphic","ring drains clockwise","static","wide",50,"low_key","deep","warm","establish_context","Hook: the 8-hour window, instantly.","Viewer feels the clock before any image.",[],None,"Label: '8 hours'. No other text.")
s("1b",G,8,19,1,"London dock, gray September evening 1485. Wet cobblestones, leaning timber houses climbing the hill.","establishing wide","slow dolly-in toward hill","dolly_in","establishing",35,"low_key","deep","cool","establish_context","Place and time: London, 1485.","Viewer places themselves in time and place.",["grainy","chiaroscuro","atmospheric"],"Medieval London dock at gray dusk, wet cobblestones reflecting dim light, leaning timber-framed houses climbing a hill, thin fog, no people",None)
s("1c",G,19,30,1,"Insert: boots sticking in mud of an uphill lane, cloak hem, a baker's shutter closing in the background.","low insert uphill","slow tilt up the lane","tilt_up","insert",50,"low_key","shallow","cool","build_tension","Narrator walking in; ordinary evening.","Viewer walks with the narrator.",["mud","grainy","dusk"],"Low-angle view of muddy boots and cloak hem on a steep medieval London lane, timber shutter closing in the background, no faces",None)
s("1d",T,30,40,1,"Text card: '19 September 1485'. Remotion spring-in on dark paper texture.","full-screen text card","spring in, hold","static","wide",50,"low_key","deep","cool","evidence","Anchor the first recorded deaths.","Viewer records the date.",[],None,"Text: '19 September 1485'")
# BEAT 2
s("2a",G,40,52,2,"Narrow yard behind a cloth merchant's house, well in center, a woman silhouette gesturing toward an upper window.","medium-wide courtyard","subtle parallax drift","static","medium_wide",50,"low_key","medium","warm","build_tension","The neighbor's account.","Viewer hears the man was fine at noon.",["candlelight","grainy"],"Narrow medieval London yard with a stone well, cloth merchant's timber house, woman in silhouette pointing at an upper window with a candle, night",None)
s("2b",A,52,66,2,"Animated timeline, three beats: 'Noon' > 'Fever' > '8 to 10 hours: death or recovery'. Bars fill left to right.","full-screen data visualization","progressive reveal left to right","static","wide",50,"low_key","deep","cool","deliver_payload","Make the 8 to 10 hour window concrete, without saying everyone died.","Viewer understands the speed.",[],None,"Labels exactly: 'Noon', 'Fever', '8 to 10 hours: death or recovery'")
s("2c",G,66,80,2,"Looking up from the yard to a single lit window, candle burning, stars faint.","low angle up","slow tilt up","tilt_up","medium_wide",35,"low_key","medium","warm","build_tension","Whatever is decided there, is decided before sunrise.","Viewer feels the wait.",["candlelit","night"],"Low-angle view up a medieval timber house to one lit upper window with a candle, night, faint stars, no people",None)
# BEAT 3
s("3a",G,80,92,3,"Market lane, early morning. People in low conversation, watching each other for the first flush of fever.","medium-wide market lane","slow pan left","pan_left","medium_wide",35,"overcast_soft","deep","cool","build_tension","The fear reaches the market.","Viewer sees suspicion spread.",["overcast_soft","grainy"],"Medieval London market lane at early morning, people in dark gowns whispering in small groups, overcast light, faces turned away or in shadow",None)
s("3b",A,92,106,3,"Animated counters rising: '2 lord mayors', '6 aldermen', '3 sheriffs'. Dark paper texture, ink-stroke reveal.","full-screen data visualization","counters tick up in sequence","static","wide",50,"low_key","deep","cool","evidence","Rank was no shield.","Viewer records who died.",[],None,"Exact text: '2 lord mayors', '6 aldermen', '3 sheriffs'")
s("3c",G,106,120,3,"Men in dark gowns follow a coffin toward a church door; they glance at one another.","wide church entrance","static, slight push-in","dolly_in","wide",24,"overcast_soft","deep","neutral","build_tension","Each mourner may be next.","Viewer feels shared dread.",["somber","muted"],"Medieval London church door, line of men in dark gowns carrying a coffin, overcast light, faces turned away",None)
# BEAT 4 (vigil)
s("4a",C,120,134,4,"Hot close room. MAN on a low bed, flushed, sweat-soaked. WIFE wringing a cloth into a basin. BOY on the floor, knees drawn up, watching the candle.","medium interior vigil","static, slight push-in","dolly_in","medium",50,"low_key","shallow","warm","emotional_beat","The family vigil, the emotional core.","Viewer witnesses intimate suffering.",["intimate","candlelit","claustrophobic"],f"Medieval bedroom interior, {MAN} lying on a low straw bed drenched in sweat, {WIFE} wringing a cloth into a basin beside him, {BOY} sitting on the floor with knees drawn up watching a candle, warm candlelight",None)
s("4b",A,134,146,4,"Abstract motion: candle flame shrinking, wall shadows trembling, slow concentric bell ripples. No text.","full-screen motion graphic","flame shrinks, ripples pulse","static","extreme_close_up",85,"low_key","shallow","warm","build_tension","The bell counts something.","Viewer feels each strike.",["candlelit","tense"],None,"No text. Sync ripples to narration pauses.")
s("4c",G,146,160,4,"Close-up of the wife's hands wringing the cloth; a church bell silhouette through the window; her hands flinch.","close-up hands and window","slow zoom in","zoom_in","close_up",85,"low_key","shallow","warm","emotional_beat","The flinch: she hears the bell as a count.","Viewer shares her dread.",["intimate","tense"],f"Close-up of the hands of a {WIFE} wringing a cloth over a basin, window behind with a church bell tower silhouette, candlelight, hands only",None)
# BEAT 5
s("5a",G,160,171,5,"Churchyard at morning, fresh earth heaped in rows.","wide churchyard","slow pan right","pan_right","wide",24,"overcast_soft","deep","neutral","evidence","The toll made visible.","Viewer sees the graves.",["somber","muted"],"Medieval London churchyard at morning, fresh earth mounds in rows, overcast light, no people",None)
s("5b",T,171,182,5,"Text card, two lines: 'Hardest hit: men in the middle of adult life' / 'Some accounts say small children were spared'.","full-screen text card","line-by-line fade","static","wide",50,"low_key","deep","cool","evidence","State the pattern, hedged as the script does.","Viewer learns who was struck.",[],None,"Exact text: 'Hardest hit: men in the middle of adult life' / 'Some accounts say small children were spared'")
s("5c",G,182,191,5,"Two small children on a doorstep tearing bread; their father at the window, hand pressed to his mouth. Silhouettes only.","wide doorstep","slow pan to window","pan_right","medium_wide",35,"overcast_soft","medium","neutral","emotional_beat","The strange sight: children eat, father watches.","Viewer feels the puzzle.",["somber","silhouette"],"Medieval London doorstep, two small children in silhouette tearing a loaf of bread, a man in silhouette at the window with a hand pressed to his mouth, overcast morning",None)
s("5d",G,191,200,5,"Empty lane: spades scraping, doors slowly closing. Only doors and a spade in view.","street-level empty lane","static","static","medium_wide",35,"overcast_soft","deep","cool","emotional_beat","Silence and isolation.","Viewer feels the city shutting.",["empty","quiet"],"Empty medieval London lane, wooden doors slowly closing, a spade leaning against a wall, overcast light, no people",None)
# BEAT 6
s("6a",A,200,209,6,"Top-down schematic street: dots (people) drift to the middle of the lane, away from doorways, never stopping. No text.","full-screen motion graphic","dots avoid doorways","static","extreme_wide",14,"low_key","deep","cool","build_tension","The city changes its pace.","Viewer sees distancing.",[],None,"No text. Ink-on-dark schematic.")
s("6b",G,209,220,6,"A crossing: crowd around a shouting man; some listen, some walk away; a priest with a lantern hurries past.","wide crossing","slow tracking right","tracking_right","medium_wide",35,"natural","deep","neutral","build_tension","Fear looks for explanations.","Viewer sees panic and prayer.",["tense","overcast_soft"],"Medieval London crossing, crowd in silhouette around a shouting man, a priest with a lantern hurrying past, overcast daylight, no faces",None)
s("6c",G,220,230,6,"Tavern window: a single drinker staring into his cup. Warm inside, cold street outside.","tavern window medium","static","static","medium",50,"low_key","shallow","warm","emotional_beat","Despair personified.","Viewer feels hopelessness.",["intimate","despair"],"Medieval London tavern seen through a window, lone drinker in silhouette staring into a cup, warm candlelight inside, cold blue street outside",None)
s("6d",T,230,240,6,"Text card: 'Nobody knew what to blame, so they blamed everything.' Slow fade.","full-screen text card","slow fade in","static","wide",50,"low_key","deep","cool","emotional_beat","Close the beat on the line.","Viewer takes the thought into the cut.",[],None,"Exact text: 'Nobody knew what to blame, so they blamed everything.'")
# BEAT 7
s("7a",X,240,248,7,"Transition: a heavy cloak slides off a chair onto the floor, revealing a lamp and stacked books behind it.","medium insert","cloak falls, camera settles","tilt_down","medium",50,"low_key","medium","warm","transition","Centuries slide away.","Viewer crosses from 1485 to the present.",["lamplit","scholarly"],"Heavy dark wool cloak sliding off a wooden chair onto the floor, reveals a desk lamp and stacked old books, warm lamplight, no people",None)
s("7b",G,248,260,7,"Quiet reading room: lamp, stack of books, hands turning pages.","medium reading room","slow pan across books","pan_right","medium",50,"low_key","medium","warm","deliver_payload","The honest answer: nobody knows.","Viewer enters the research question.",["scholarly","quiet"],"Quiet reading room, desk lamp, stack of old books, hands turning a page, warm lamplight against cool background, hands only",None)
s("7c",T,260,272,7,"Text card: 'Cause: unknown' / 'Hantavirus (suggested by some researchers)' / 'Anthrax (Edward McSweegan, 2004)'.","full-screen text card","line-by-line reveal","static","wide",50,"low_key","deep","cool","evidence","State the hypotheses exactly as scripted.","Viewer sees no idea has settled it.",[],None,"Exact text: 'Cause: unknown' / 'Hantavirus (suggested by some researchers)' / 'Anthrax (Edward McSweegan, 2004)'")
s("7d",G,272,280,7,"Close-up of an open book page with a blank gap in the text block, lamp glow.","close-up page","slow zoom in","zoom_in","close_up",85,"low_key","shallow","warm","emotional_beat","The same gap keeps appearing.","Viewer feels the unanswered question.",["scholarly","quiet"],"Close-up of an open old book, a blank gap among unreadable blurred lines of text, warm lamp glow, shallow depth of field",None)
# BEAT 8
s("8a",G,280,291,8,"Late October, sharp bright air. A row of shuttered houses, each with one dark window.","wide street","slow dolly forward","dolly_in","wide",24,"natural","deep","cool","emotional_beat","The sickness is ending; the cost remains.","Viewer counts the shut houses.",["sharp","bright","somber"],"Late October medieval London street, row of shuttered timber houses each with one dark window, sharp bright autumn light, no people",None)
s("8b",A,291,302,8,"Grid of windows going dark one by one, as if being counted. No text.","full-screen motion graphic","windows extinguish in sequence","static","wide",50,"low_key","deep","cool","build_tension","I count them without meaning to.","Viewer feels the scale.",[],None,"No text.")
s("8c",T,302,311,8,"Text card: 'Several thousand dead in London by the end of October 1485'.","full-screen text card","fade in, hold","static","wide",50,"low_key","deep","cool","deliver_payload","State the toll literally.","Viewer records the scale.",[],None,"Exact text: 'Several thousand dead in London by the end of October 1485'")
s("8d",G,311,320,8,"One shutter opening onto light, beside others that stay closed.","medium doorway","slow push-in","dolly_in","medium",50,"natural","medium","neutral","emotional_beat","Some houses reopen, others do not.","Viewer feels uneven recovery.",["somber","quiet"],"Medieval timber house front, one shutter opening onto soft light, neighboring shutters closed and dusty, October light, no people",None)
# BEAT 9
s("9a",T,320,329,9,"Text card: '30 October 1485' with 'Henry VII is crowned'. Bell ring sound cue.","full-screen text card","spring in, hold","static","wide",50,"low_key","deep","warm","evidence","Anchor the coronation date.","Viewer records the date.",[],None,"Exact text: '30 October 1485' / 'Henry VII is crowned'")
s("9b",G,329,340,9,"Crowd along the street, pale and tired but alive; bells ringing; a crown seen only as a distant silhouette.","wide crowd","slow pan through crowd","pan_right","wide",35,"natural","deep","warm","emotional_beat","The city survives.","Viewer feels relief.",["relief","crowded"],"Medieval London street, pale tired crowd in silhouette, bell tower above, distant figure with crown seen only as a silhouette, October light, no faces",None)
s("9c",C,340,352,9,"HERO: doorway of the vigil house. The same MAN, now thin and pale, holds the frame with both hands. The same BOY leans against his leg. Same clothes as scene 4a.","doorway medium","static, very slow push-in","dolly_in","medium",50,"natural","medium","neutral","resolution","The man survived and hears the bells.","Viewer witnesses survival.",["hopeful","tired","october_light"],f"Medieval timber doorway, {MAN}, now pale and thin, standing holding the doorframe with both hands, {BOY} leaning against his leg, October daylight, bells implied, same clothes as the vigil scene",None)
s("9d",A,352,360,9,"Soft bell ripples over dark, fading, hopeful warmth. No text.","full-screen motion graphic","ripples fade","static","wide",50,"low_key","deep","warm","emotional_beat","Bells that no longer toll for the dead.","Viewer exhales.",[],None,"No text.")
# BEAT 10
s("10a",G,360,372,10,"Hall of archives, cool still air, documents on tables.","archive hall medium","slow push-in","dolly_in","medium",50,"low_key","medium","cool","evidence","The scholarly comparison begins.","Viewer shifts to analysis.",["scholarly","quiet","archive"],"Cool archive hall, documents on long tables, still air, lamplight, no people",None)
s("10b",A,372,386,10,"Two stylized curves: 'Other epidemics' rises and lingers; 'The English sweat' spikes and drops fast. No numbers.","full-screen data visualization","curves draw left to right","static","wide",50,"low_key","deep","cool","comparison","Spike and recede, unlike the rest.","Viewer sees the different shape.",[],None,"Exact labels: 'Other epidemics: lingered', 'The English sweat: spiked, then receded'. No axis numbers.")
s("10c",A,386,400,10,"Timeline with five dark spikes between '1485' and '1551'. Only those two years labeled.","full-screen timeline","spikes appear in sequence","static","wide",50,"low_key","deep","cool","deliver_payload","Five epidemics, then gone.","Viewer sees the pattern.",[],None,"Labels exactly: '1485' (left), '1551' (right). Do NOT label any other year.")
# BEAT 11
s("11a",G,400,411,11,"1551: a tense, quiet lane; shutters open, a cart; the city going back to its work.","wide lane","static","static","wide",24,"overcast_soft","deep","cool","build_tension","Ordinary sounds return.","Viewer feels life resume.",["tense","quiet"],"Medieval London lane, autumn light, open shutters, a handcart, city going back to work, no human faces",None)
s("11b",T,411,422,11,"Text card: 'After 1551, the disease vanishes from the record'.","full-screen text card","fade in, hold","static","wide",50,"low_key","deep","cool","deliver_payload","State it as the script does.","Viewer learns it vanished.",[],None,"Exact text: 'After 1551, the disease vanishes from the record'")
s("11c",G,422,431,11,"Empty lane, doors closed: the narrator waits for the sickness to return.","wide lane","static, slow fog build","static","wide",35,"low_key","deep","cool","build_tension","Waiting, and the absence.","Viewer feels the waiting.",["empty","still"],"Empty medieval London lane, closed doors, thickening fog, lantern unlit, no people",None)
s("11d",A,431,440,11,"Fog layers roll across the frame, vignette closes, dissolve to cool present-day blue. No text.","full-screen motion graphic","fog drifts, color shifts to cool blue","static","wide",50,"low_key","deep","cool","transition","Dissolve to the present.","Viewer crosses to the bridge.",[],None,"No text.")
# BEAT 12
s("12a",G,440,452,12,"Present-day stone bridge at night, wide dark river carrying city lights, mist rising, single lantern at the bridge end.","bridge wide to river","slow push toward river","dolly_in","wide",24,"low_key","deep","cool","emotional_beat","The bridge between past and present.","Viewer connects 1485 to now.",["misty","nocturnal","reflective"],"Present-day London stone bridge at night, Thames wide and dark, mist rising, city lights on the water, single lantern at the bridge end, no people",None)
s("12b",A,452,464,12,"River shimmer with drifting mist and a flickering lantern glow. No text.","full-screen motion graphic","mist drifts, lantern flickers","static","wide",50,"low_key","deep","cool","build_tension","Cold wind, mist rising.","Viewer settles into the final image.",[],None,"No text.")
s("12c",G,464,480,12,"FINAL (intentional 16s hold): a lone barge slides from beneath an arch, drifts downstream into the dark; mist takes it; fade to black.","barge fading into mist","very slow drift, fade to black","static","wide",35,"low_key","deep","cool","resolution","The mystery drifts away.","Viewer leaves with the unsolved mystery.",["mysterious","final","misty"],"Lone barge sliding out from beneath a stone arch into a dark misty river at night, mist swallowing it, no people",None)

scenes, ids = [], []
for (i,t,st,en,b,desc,fr,mv,cam,sz,lens,lt,dof,tmp,role,intent,info,kw,prompt,ov) in R:
    sc = {"id": f"scene_{i}", "type": t, "description": desc, "start_seconds": st, "end_seconds": en,
          "script_section_id": f"scene_{b:03d}", "framing": fr, "movement": mv,
          "transition_in": "cut" if i=="1a" else "dissolve",
          "transition_out": "fade-to-black" if i=="12c" else "dissolve",
          "shot_intent": intent, "narrative_role": role, "information_role": info,
          "shot_language": {"shot_size": sz, "camera_movement": cam, "lens_mm": lens, "lighting_key": lt, "depth_of_field": dof, "color_temperature": tmp},
          "texture_keywords": kw, "required_assets": []}
    if i == "9c": sc["hero_moment"] = True
    if ov: sc["overlay_notes"] = ov
    if prompt: sc["required_assets"] = [{"type": "image", "description": prompt + SFX, "source": "generate"}]
    scenes.append(sc)

meta = {
  "script_without_enhancement_cues": True,
  "timing_note": "PROVISIONAL: equal 40s per beat. Re-sync every scene to word-level narration timestamps after TTS.",
  "total_duration_seconds": 480, "total_scenes": len(scenes),
  "scene_types_used": sorted({s_["type"] for s_ in scenes}),
  "character_descriptors": {"man_from_vigil": MAN, "wife_from_vigil": WIFE, "boy_from_vigil": BOY},
  "consistency_anchors": {
    "man_from_vigil": {"descriptor_key": "man_from_vigil", "appears_in": ["scene_4a","scene_9c"], "note": "Same clothes in both scenes; condition differs (sweating vs recovered)."},
    "wife_from_vigil": {"descriptor_key": "wife_from_vigil", "appears_in": ["scene_4a","scene_4c"], "note": "Hands only in 4c."},
    "boy_from_vigil": {"descriptor_key": "boy_from_vigil", "appears_in": ["scene_4a","scene_9c"]}},
  "not_shown_note": "scene_12a/12b/12c show no characters; the man and boy are only in the narration there.",
  "required_asset_policy": {"provider": "image_selector", "allowed_providers": ["cloudflare"], "resolution": "1024x576", "no_real_faces": True, "no_gore": True, "no_text_in_images": True}
}
plan = {"version": "1.0", "style_playbook": "dark-history", "scenes": scenes, "metadata": meta}

# ---- validation ----
E = {"type": {"talking_head","broll","animation","character_scene","diagram","text_card","transition","generated","screen_recording"},
     "size": {"extreme_wide","wide","medium_wide","medium","medium_close","close_up","extreme_close_up","over_shoulder","insert","establishing"},
     "cam": {"static","pan_left","pan_right","tilt_up","tilt_down","dolly_in","dolly_out","tracking_left","tracking_right","crane_up","crane_down","handheld","steadicam","whip_pan","orbital","zoom_in","zoom_out","rack_focus"},
     "lens": {14,24,35,50,85,135,200},
     "light": {"high_key","low_key","natural","golden_hour","blue_hour","tungsten_warm","neon","silhouette","rim_lit","volumetric","overcast_soft"},
     "dof": {"shallow","medium","deep"}, "tmp": {"cool","neutral","warm","mixed"},
     "role": {"establish_context","introduce_subject","build_tension","deliver_payload","transition","emotional_beat","evidence","comparison","resolution","call_to_action"}}
err = []
prev_end = 0; run = 0; maxrun = 0; imgs = []
for sc in scenes:
    sl = sc["shot_language"]
    if sc["type"] not in E["type"]: err.append(f'{sc["id"]}: type')
    if sl["shot_size"] not in E["size"] or sl["camera_movement"] not in E["cam"] or sl["lens_mm"] not in E["lens"] or sl["lighting_key"] not in E["light"] or sl["depth_of_field"] not in E["dof"] or sl["color_temperature"] not in E["tmp"]: err.append(f'{sc["id"]}: shot_language enum')
    if sc["narrative_role"] not in E["role"]: err.append(f'{sc["id"]}: role')
    if sc["start_seconds"] != prev_end: err.append(f'{sc["id"]}: gap/overlap at {sc["start_seconds"]} (expected {prev_end})')
    prev_end = sc["end_seconds"]
    has_img = bool(sc["required_assets"])
    if sc["type"] in (G, C, X) and not has_img: err.append(f'{sc["id"]}: image scene without asset')
    if sc["type"] in (A, T) and has_img: err.append(f'{sc["id"]}: native scene has asset')
    if has_img:
        run += 1; maxrun = max(maxrun, run); imgs.append(sc["end_seconds"]-sc["start_seconds"])
        if sc["end_seconds"]-sc["start_seconds"] > 16: err.append(f'{sc["id"]}: image > 16s')
        if sc["end_seconds"]-sc["start_seconds"] > 14 and sc["id"] != "scene_12c": err.append(f'{sc["id"]}: image > 14s')
    else: run = 0
if prev_end != 480: err.append(f"end {prev_end} != 480")
if maxrun > 2: err.append(f"max consecutive images = {maxrun} (limit 2)")
by = {sc["id"]: sc for sc in scenes}
d4, d9 = by["scene_4a"]["required_assets"][0]["description"], by["scene_9c"]["required_assets"][0]["description"]
if not (MAN in d4 and MAN in d9 and BOY in d4 and BOY in d9 and WIFE in d4): err.append("descriptor mismatch 4a/9c")
for a in meta["consistency_anchors"].values():
    if any(x.startswith("scene_12") for x in a["appears_in"]): err.append("12x in appears_in")
import re
for sid in ("scene_10a","scene_10b","scene_10c"):
    yrs = set(re.findall(r"\b1[0-9]{3}\b", by[sid].get("overlay_notes","")))
    if yrs - {"1485","1551"}: err.append(f"{sid}: extra year {yrs}")
if "Supper" in by["scene_2b"]["overlay_notes"] or "Death" in by["scene_2b"]["overlay_notes"].replace("death or recovery",""): err.append("2b label")
print(f"scenes={len(scenes)} image_scenes={len(imgs)} avg_image_s={sum(imgs)/len(imgs):.1f} max_run={maxrun}")
print("ERRORS:", err or "none")
if err: sys.exit(1)
json.dump(plan, open("scene_plan_draft_claude.json","w"), ensure_ascii=False, indent=2)
print("wrote scene_plan_draft_claude.json")
