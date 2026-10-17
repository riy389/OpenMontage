"""Chatterbox Nano worker for tools/audio/chatterbox_nano_tts.py.

Runs inside the separate Nano venv (not the OpenMontage .venv).
Usage: python chatterbox_nano_worker.py '<json args>'
The last stdout line starting with RESULT: carries the result as JSON.
"""

import json
import re
import sys
import time

PAUSE_MS = {"period": 400, "question": 450, "ellipsis": 700}
PEAK = 0.85


def split_sentences(text):
    parts = re.split(r"(?<=[.?!])\s+", " ".join(text.split()))
    return [p for p in parts if p]


def pause_kind(sentence):
    if sentence.endswith("..."):
        return "ellipsis"
    if sentence.endswith("?"):
        return "question"
    return "period"


def main():
    import torch
    import torchaudio as ta
    from chatterbox.tts_turbo import ChatterboxTurboTTS

    args = json.loads(sys.argv[1])
    sentences = split_sentences(args["text"])
    if not sentences:
        raise SystemExit("empty text")

    model = ChatterboxTurboTTS.from_pretrained(device="cpu", nano=True)
    model.prepare_conditionals(args["ref_audio_path"], exaggeration=0.0)
    torch.manual_seed(args["seed"])
    sr = model.sr

    chunks, per_sentence = [], []
    speech_seconds = 0.0
    started = time.time()
    for i, sentence in enumerate(sentences):
        wav = model.generate(sentence, temperature=args["temperature"])
        seconds = wav.shape[1] / sr
        speech_seconds += seconds
        last = i == len(sentences) - 1
        pause_ms = args["end_pause_ms"] if last else PAUSE_MS[pause_kind(sentence)]
        per_sentence.append({
            "text": sentence,
            "seconds": round(seconds, 2),
            "peak": round(wav.abs().max().item(), 4),
            "pause_ms": pause_ms,
        })
        chunks.append(wav)
        chunks.append(torch.zeros(1, int(sr * pause_ms / 1000)))
    generate_seconds = time.time() - started

    full = torch.cat(chunks, dim=1)
    peak = full.abs().max().item()
    if peak > 0:
        full = full * (PEAK / peak)
    ta.save(args["output_path"], full, sr)

    print("RESULT:" + json.dumps({
        "sentences": per_sentence,
        "audio_seconds": round(full.shape[1] / sr, 2),
        "speech_seconds": round(speech_seconds, 2),
        "generate_seconds": round(generate_seconds, 2),
        "rtf": round(generate_seconds / speech_seconds, 2) if speech_seconds else None,
        "sample_rate": sr,
    }))


if __name__ == "__main__":
    main()
