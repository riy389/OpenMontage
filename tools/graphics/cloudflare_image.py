"""Cloudflare Workers AI image generation (FLUX.2 Klein)."""

from __future__ import annotations

import base64
import io
import os
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


class CloudflareImage(BaseTool):
    name = "cloudflare_image"
    version = "0.2.1"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "cloudflare"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.API

    dependencies = []  # checked dynamically via env vars
    install_instructions = (
        "Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.\n"
        "  Get an API token (Workers AI edit permission) at "
        "https://dash.cloudflare.com/profile/api-tokens\n"
        "  Find your Account ID on the Cloudflare dashboard overview page."
    )
    agent_skills = []

    capabilities = ["generate_image", "generate_illustration", "text_to_image"]
    supports = {
        "negative_prompt": False,
        "seed": False,
        "custom_size": True,
    }
    best_for = [
        "free-tier image generation (Cloudflare Workers AI neuron budget)",
        "16:9 landscape scene images for video pipelines (default 1024x576; pass width/height for other ratios)",
        "character-consistent scenes via up to 4 reference images (image_paths)",
    ]
    not_good_for = ["text rendering in images", "seeded/reproducible generation"]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string"},
            "width": {"type": "integer", "default": 1024},
            "height": {"type": "integer", "default": 576},
            "image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 4,
                "description": (
                    "Optional reference images (max 4) sent as input_image_0..3. "
                    "Refer to them in the prompt by index, e.g. 'the figure from image 0'."
                ),
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "width", "height", "image_paths"]
    side_effects = ["writes image file to output_path", "calls Cloudflare Workers AI API"]
    user_visible_verification = ["Inspect generated image for relevance and quality"]

    CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
    MAX_REFERENCE_IMAGES = 4
    # Cloudflare docs: each reference image must be smaller than 512x512.
    REFERENCE_MAX_SIDE = 480

    def _get_credentials(self) -> tuple[str | None, str | None]:
        return (
            os.environ.get("CLOUDFLARE_ACCOUNT_ID"),
            os.environ.get("CLOUDFLARE_API_TOKEN"),
        )

    def get_status(self) -> ToolStatus:
        account_id, api_token = self._get_credentials()
        if account_id and api_token:
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0  # billed in neurons against the account's daily budget, not USD

    def _prepare_reference(self, path: str) -> bytes:
        """Load a reference image and downscale it to fit the API's size limit."""
        from PIL import Image

        img = Image.open(path).convert("RGB")
        img.thumbnail((self.REFERENCE_MAX_SIDE, self.REFERENCE_MAX_SIDE))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return buf.getvalue()

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        account_id, api_token = self._get_credentials()
        if not account_id or not api_token:
            return ToolResult(
                success=False,
                error="No Cloudflare credentials found. " + self.install_instructions,
            )

        import requests

        start = time.time()
        prompt = inputs["prompt"]
        width = inputs.get("width", 1024)
        height = inputs.get("height", 576)
        image_paths = inputs.get("image_paths") or []

        if len(image_paths) > self.MAX_REFERENCE_IMAGES:
            return ToolResult(
                success=False,
                error=f"Too many reference images: {len(image_paths)} "
                f"(max {self.MAX_REFERENCE_IMAGES}).",
            )

        url = (
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
            f"/ai/run/{self.CF_MODEL}"
        )
        headers = {"Authorization": f"Bearer {api_token}"}
        form_data = {
            "prompt": (None, prompt),
            "width": (None, str(width)),
            "height": (None, str(height)),
        }

        for i, ref_path in enumerate(image_paths):
            if not Path(ref_path).exists():
                return ToolResult(
                    success=False, error=f"Reference image not found: {ref_path}"
                )
            try:
                form_data[f"input_image_{i}"] = (
                    f"ref{i}.png",
                    self._prepare_reference(ref_path),
                    "image/png",
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Could not read reference image {ref_path}: {e}",
                )

        try:
            response = requests.post(url, headers=headers, files=form_data, timeout=90)
        except Exception as e:
            return ToolResult(success=False, error=f"Cloudflare request failed: {e}")

        if response.status_code != 200:
            return ToolResult(
                success=False,
                error=f"Cloudflare generation failed: HTTP {response.status_code}: "
                f"{response.text[:300]}",
            )

        try:
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                img_b64 = (data.get("result") or {}).get("image")
                if not img_b64:
                    return ToolResult(
                        success=False,
                        error=f"Cloudflare generation failed: unrecognized JSON shape, "
                        f"keys={list(data.keys())}",
                    )
                image_bytes = base64.b64decode(img_b64)
            else:
                image_bytes = response.content

            from PIL import Image

            output_path = Path(inputs.get("output_path", "generated_image.png"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            Image.open(io.BytesIO(image_bytes)).convert("RGB").save(output_path, "PNG")
        except Exception as e:
            return ToolResult(success=False, error=f"Cloudflare image processing failed: {e}")

        if not output_path.exists() or output_path.stat().st_size <= 1024:
            return ToolResult(
                success=False,
                error="Cloudflare generation produced an empty or invalid image file.",
            )

        return ToolResult(
            success=True,
            data={
                "provider": "cloudflare",
                "model": self.CF_MODEL,
                "prompt": prompt,
                "reference_images": len(image_paths),
                "output": str(output_path),
            },
            artifacts=[str(output_path)],
            cost_usd=self.estimate_cost(inputs),
            duration_seconds=round(time.time() - start, 2),
            model=self.CF_MODEL,
        )
