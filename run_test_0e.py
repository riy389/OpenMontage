import sys
import os
import time
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/codespace/OpenMontage')
from tools.graphics.image_selector import ImageSelector

os.environ.setdefault("PYTHONPATH", "/home/codespace/OpenMontage")

prefix = "Dark history illustration, painterly oil painting with old woodcut grain, dramatic chiaroscuro lighting from a single candle, torch or moonlight, desaturated palette with deep shadows, fog and smoke, medium close-up portrait framing, chest-up, historically grounded period details, no visible gore, no text, lettering or signature."
char_block = "a lone figure in a long charcoal-black hooded cloak with a deep cowl, seen from the front, everything above the nose is pure black shadow under the cowl, only the lips and chin are lit, no visible eyes, plain cloth black cloak, no insignia or emblems"

wording_1 = "three-quarter front view turning slightly, upper half of face in heavy shadow, lower half including lips and chin visible in cold moonlight from upper-left"
wording_2 = "straight-on front view, chin tilted slightly up, dim light from below, only lips and chin visible, nose half covered by shadow"

scenes = [
    ("dungeon", "standing in a damp underground dungeon cellar corridor with flickering wall torches casting amber light and long shadows on stone walls"),
    ("scriptorium", "standing in an ancient monastery scriptorium filled with flickering candles on wooden desks, manuscripts and parchment scrolls"),
    ("cloister", "standing in a quiet gothic cloister courtyard at night, pale moonlight filtering through stone arches, cold blue fog")
]

selector = ImageSelector()
output_dir = Path("projects/_experiments/narrator-test")
output_dir.mkdir(parents=True, exist_ok=True)
log_path = output_dir / "calls.log"

generated_images = []

for scene_name, scene_desc in scenes:
    for w_idx, wording in enumerate([wording_1, wording_2], 1):
        name = f"e_{scene_name}_w{w_idx}"
        out_file = output_dir / f"{name}.png"
        prompt = f"{prefix} {char_block}, {wording}, {scene_desc}"
        
        print(f"Generating {name}...")
        start_t = time.time()
        res = selector.execute({
            "prompt": prompt,
            "width": 1024,
            "height": 576,
            "allowed_providers": ["cloudflare"],
            "output_path": str(out_file)
        })
        duration = round(time.time() - start_t, 2)
        
        status = "SUCCESS" if res.success else f"FAILED: {res.error}"
        print(f"  -> {status} in {duration}s")
        
        log_entry = f"{datetime.utcnow().isoformat()+'+00:00'} | name={name} | size=1024x576 | refs=0 | paths=[] | prompt={prompt} | status={'SUCCESS' if res.success else 'FAILED'} | duration={duration}s | error={res.error if not res.success else ''}\n"
        with open(log_path, "a") as f:
            f.write(log_entry)
            
        if res.success and out_file.exists():
            generated_images.append((name, str(out_file)))
        else:
            print(f"Error generating {name}: {res.error}")

print(f"Successfully generated {len(generated_images)}/6 images.")

# Create 2x3 contact sheet
if len(generated_images) == 6:
    cols = 2
    rows = 3
    thumb_w = 1024
    thumb_h = 576
    label_h = 60
    
    sheet_w = cols * thumb_w
    sheet_h = rows * (thumb_h + label_h)
    
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 10, 15))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
        
    for idx, (name, path) in enumerate(generated_images):
        c = idx % cols
        r = idx // cols
        x = c * thumb_w
        y = r * (thumb_h + label_h)
        
        img = Image.open(path).convert("RGB")
        if img.size != (thumb_w, thumb_h):
            img = img.resize((thumb_w, thumb_h))
        sheet.paste(img, (x, y))
        
        # Draw label box & text
        label_y = y + thumb_h
        draw.rectangle([x, label_y, x + thumb_w, label_y + label_h], fill=(20, 18, 25))
        draw.text((x + 20, label_y + 15), name, fill=(232, 224, 208), font=font)
        
    sheet_path = output_dir / "step3_0e_2x3.png"
    sheet.save(sheet_path)
    print(f"Contact sheet saved to {sheet_path}")
