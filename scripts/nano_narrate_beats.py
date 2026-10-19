#!/usr/bin/env python3
"""Narrate every beat of a script file with scripts/chatterbox_nano_worker.py.

Parses '## scene_NNN: Title' sections (text is used verbatim, never edited), calls the
worker once per beat inside the Nano venv, writes beat_NN.wav, narration_full.wav and
narration_manifest.json (per-beat durations + cumulative start/end for scene_plan sync).
Each beat is peak-normalized to 0.85 by the worker; final loudness is set at mix time.
"""
import argparse, hashlib, json, re, subprocess, sys, wave
from pathlib import Path


def parse_beats(path):
    beats, cur = [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(scene_\d+):\s*(.*)$", line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "lines": []}
            beats.append(cur)
        elif cur is not None and line.strip():
            cur["lines"].append(line.strip())
    for b in beats:
        b["text"] = " ".join(b.pop("lines"))
        b["words"] = len(b["text"].split())
    return beats


def wav_seconds(p):
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / w.getframerate()


def run_worker(py, worker, args):
    r = subprocess.run([py, worker, json.dumps(args)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"worker failed (exit {r.returncode}):\n{r.stderr[-1500:]}")
    lines = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")]
    if not lines:
        sys.exit("worker gave no RESULT line:\n" + r.stdout[-800:])
    return json.loads(lines[-1][len("RESULT:"):])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--ref")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--worker", default="scripts/chatterbox_nano_worker.py")
    ap.add_argument("--nano-python")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--end-pause-ms", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    beats = parse_beats(a.script)
    total_words = sum(b["words"] for b in beats)
    print(f"beats={len(beats)} total_words={total_words}")
    for b in beats:
        print(f'  {b["id"]}: {b["words"]} words - {b["title"]}')
    if not beats:
        sys.exit("no beats found")
    if a.dry_run:
        return
    if not a.ref or not a.nano_python:
        sys.exit("--ref and --nano-python are required unless --dry-run")

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    t = 0.0; manifest_beats = []
    for i, b in enumerate(beats, 1):
        wav = out / f"beat_{i:02d}.wav"
        res = run_worker(a.nano_python, a.worker, {
            "text": b["text"], "output_path": str(wav), "ref_audio_path": a.ref,
            "seed": a.seed, "temperature": a.temperature, "end_pause_ms": a.end_pause_ms})
        dur = round(wav_seconds(wav), 2)
        manifest_beats.append({
            "id": b["id"], "title": b["title"], "file": wav.name, "words": b["words"],
            "text_md5": hashlib.md5(b["text"].encode("utf-8")).hexdigest(),
            "audio_seconds": dur, "speech_seconds": res["speech_seconds"],
            "generate_seconds": res["generate_seconds"], "rtf": res["rtf"],
            "start_seconds": round(t, 2), "end_seconds": round(t + dur, 2),
            "sentences": res["sentences"]})
        t += dur
        print(f'{b["id"]}: {dur}s audio, RTF {res["rtf"]}, cumulative {round(t, 2)}s', flush=True)

    full = out / "narration_full.wav"
    with wave.open(str(full), "wb") as dst:
        for i, mb in enumerate(manifest_beats):
            with wave.open(str(out / mb["file"]), "rb") as src:
                if i == 0:
                    dst.setparams(src.getparams())
                dst.writeframes(src.readframes(src.getnframes()))
    manifest = {
        "script_md5": hashlib.md5(Path(a.script).read_bytes()).hexdigest(),
        "ref_audio": a.ref, "seed": a.seed, "temperature": a.temperature,
        "end_pause_ms": a.end_pause_ms, "total_words": total_words,
        "total_audio_seconds": round(wav_seconds(full), 2), "beats": manifest_beats}
    (out / "narration_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f'total_audio_seconds={manifest["total_audio_seconds"]}')


if __name__ == "__main__":
    main()
