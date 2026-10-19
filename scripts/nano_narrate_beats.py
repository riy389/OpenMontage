#!/usr/bin/env python3
"""Narrate every beat of a script file with scripts/chatterbox_nano_worker.py.

Parses '## scene_NNN: Title' sections (text is used verbatim, never edited), calls the
worker once per beat inside the Nano venv, writes beat_NN.wav, narration_full.wav and
narration_manifest.json (per-beat durations + cumulative start/end for scene_plan sync).
Each beat is peak-normalized to 0.85 by the worker; final loudness is set at mix time.
"""
import argparse, hashlib, json, re, struct, subprocess, sys
from array import array
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


def read_wav(path):
    """Minimal RIFF reader (PCM tag 1 and IEEE float tag 3). Returns dict with fmt + raw data."""
    b = Path(path).read_bytes()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise ValueError(f"not a RIFF/WAVE file: {path}")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(b):
        cid, size = b[pos:pos + 4], struct.unpack("<I", b[pos + 4:pos + 8])[0]
        body = pos + 8
        if cid == b"fmt ":
            tag, ch, rate, _, align, bits = struct.unpack("<HHIIHH", b[body:body + 16])
            fmt = {"tag": tag, "channels": ch, "rate": rate, "align": align, "bits": bits}
        elif cid == b"data":
            end = len(b) if size == 0xFFFFFFFF or body + size > len(b) else body + size
            data = b[body:end]
            break
        pos = body + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError(f"missing fmt/data chunk: {path}")
    if fmt["tag"] not in (1, 3):
        raise ValueError(f"unsupported WAV format tag {fmt['tag']}: {path}")
    return {**fmt, "data": data}


def wav_seconds(w):
    return len(w["data"]) / w["align"] / w["rate"]


def to_pcm16(w):
    if w["tag"] == 1 and w["bits"] == 16:
        return w
    if w["tag"] == 3 and w["bits"] == 32:
        a = array("f"); a.frombytes(w["data"])
        s = array("h", [max(-32768, min(32767, int(x * 32767))) for x in a])
        return {**w, "tag": 1, "bits": 16, "align": 2 * w["channels"], "data": s.tobytes()}
    raise ValueError(f"cannot convert tag {w['tag']} / {w['bits']} bits to PCM16")


def write_wav(path, w):
    d = w["data"]
    hdr = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(d), b"WAVE", b"fmt ", 16,
                      w["tag"], w["channels"], w["rate"], w["rate"] * w["align"], w["align"],
                      w["bits"], b"data", len(d))
    Path(path).write_bytes(hdr + d)


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
        dur = round(wav_seconds(read_wav(wav)), 2)
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
    parts = [read_wav(out / mb["file"]) for mb in manifest_beats]
    src_fmt = {k: parts[0][k] for k in ("tag", "bits", "channels", "rate")}
    if any({k: x[k] for k in src_fmt} != src_fmt for x in parts):
        sys.exit("beat WAV formats differ; cannot concatenate")
    joined = to_pcm16({**parts[0], "data": b"".join(x["data"] for x in parts)})
    write_wav(full, joined)
    full_seconds = wav_seconds(joined)
    print(f"source format: tag={src_fmt['tag']} bits={src_fmt['bits']} rate={src_fmt['rate']}; full written as PCM16")
    manifest = {
        "script_md5": hashlib.md5(Path(a.script).read_bytes()).hexdigest(),
        "ref_audio": a.ref, "seed": a.seed, "temperature": a.temperature,
        "end_pause_ms": a.end_pause_ms, "total_words": total_words,
        "total_audio_seconds": round(full_seconds, 2), "source_wav_format": src_fmt, "beats": manifest_beats}
    (out / "narration_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f'total_audio_seconds={manifest["total_audio_seconds"]}')


if __name__ == "__main__":
    main()
