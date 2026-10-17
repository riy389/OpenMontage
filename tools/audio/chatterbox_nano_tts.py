"""Chatterbox Nano local text-to-speech provider tool.

Runs the accepted Nano recipe (Issue #1, checkpoint 17 Oct 2026): one sentence
at a time, silence between sentences, one peak normalization at the end.
Nano lives in its own venv, so generation runs in a subprocess worker.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

DEFAULT_VENV = "/workspaces/nano/venv"
DEFAULT_HF_HOME = "/workspaces/nano/hf-cache"
WORKER = Path(__file__).resolve().parents[2] / "scripts" / "chatterbox_nano_worker.py"


class ChatterboxNanoTTS(BaseTool):
    name = "chatterbox_nano_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "chatterbox_nano"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["env:NANO_REF_AUDIO"]
    install_instructions = (
        "Chatterbox Nano needs its own venv and cached weights:\n"
        "  NANO_VENV (default /workspaces/nano/venv): venv with torch (CPU) and chatterbox-tts\n"
        "  NANO_HF_HOME (default /workspaces/nano/hf-cache): Hugging Face cache with ResembleAI/chatterbox-nano\n"
        "  NANO_REF_AUDIO: path to the reference voice file (Q1_qwen_ryan.mp3), longer than 5 seconds"
    )
    agent_skills = ["text-to-speech"]

    capabilities = ["text_to_speech", "voice_cloning", "offline_generation"]
    supports = {
        "voice_cloning": True,
        "multilingual": False,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "English long-form narration with a cloned reference voice",
        "free local narration (CPU)",
    ]
    not_good_for = [
        "languages other than English",
        "SSML, break tags or paralinguistic tags",
        "fast turnaround (about 3x slower than real time on CPU)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "output_path": {"type": "string"},
            "ref_audio_path": {
                "type": "string",
                "description": "Reference voice file. Defaults to the NANO_REF_AUDIO environment variable.",
            },
            "seed": {"type": "integer", "default": 42},
            "temperature": {"type": "number", "default": 0.8},
            "beat_end_pause_ms": {
                "type": "integer",
                "default": 900,
                "description": "Silence after the last sentence (beat boundary). Replaces that sentence's own pause.",
            },
        },
    }

    # ram_mb is an estimate; disk_mb is measured (venv 1.9 GB + cache 2.8 GB).
    resource_profile = ResourceProfile(
        cpu_cores=2, ram_mb=4096, vram_mb=0, disk_mb=4800, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=0, retryable_errors=[])
    idempotency_key_fields = ["text", "seed", "temperature", "ref_audio_path", "beat_end_pause_ms"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = ["Listen to the generated narration for pauses and pronunciation"]

    @staticmethod
    def _venv_python() -> Path:
        return Path(os.environ.get("NANO_VENV", DEFAULT_VENV)) / "bin" / "python"

    def get_status(self) -> ToolStatus:
        ref = os.environ.get("NANO_REF_AUDIO")
        if self._venv_python().exists() and ref and Path(ref).is_file() and WORKER.is_file():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        # About 2.5 spoken words per second, generated at RTF 2.6-2.9 (measured, Issue #5 N1k).
        return len(inputs.get("text", "").split()) / 2.5 * 3.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(success=False, error="Chatterbox Nano not available. " + self.install_instructions)

        ref = inputs.get("ref_audio_path") or os.environ["NANO_REF_AUDIO"]
        if not Path(ref).is_file():
            return ToolResult(success=False, error=f"Reference audio not found: {ref}")

        output_path = Path(inputs.get("output_path", "tts_output.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        seed = int(inputs.get("seed", 42))

        args = {
            "text": inputs["text"],
            "output_path": str(output_path),
            "ref_audio_path": ref,
            "seed": seed,
            "temperature": float(inputs.get("temperature", 0.8)),
            "end_pause_ms": int(inputs.get("beat_end_pause_ms", 900)),
        }
        env = dict(os.environ)
        env["HF_HOME"] = os.environ.get("NANO_HF_HOME", DEFAULT_HF_HOME)
        env["HF_HUB_OFFLINE"] = "1"

        start = time.time()
        try:
            proc = subprocess.run(
                [str(self._venv_python()), str(WORKER), json.dumps(args)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=1800,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Chatterbox Nano timed out after 1800 s")

        if proc.returncode != 0:
            return ToolResult(
                success=False,
                error=f"Nano worker failed (exit {proc.returncode}): {(proc.stderr or proc.stdout)[-1500:]}",
            )

        result_line = next(
            (ln for ln in reversed(proc.stdout.splitlines()) if ln.startswith("RESULT:")), None
        )
        if result_line is None or not output_path.exists():
            return ToolResult(success=False, error="Nano worker produced no result or output file.")
        worker = json.loads(result_line[len("RESULT:"):])

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": "chatterbox-nano",
                "text_length": len(inputs["text"]),
                "output": str(output_path),
                "format": "wav",
                **worker,
            },
            artifacts=[str(output_path)],
            duration_seconds=round(time.time() - start, 2),
            seed=seed,
            model="chatterbox-nano",
        )
