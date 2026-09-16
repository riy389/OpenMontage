"""Historical image acquisition from the Library of Congress (free, no API key)."""

from __future__ import annotations

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


class LOCImage(BaseTool):
    name = "loc_image"
    version = "0.1.0"
    tier = ToolTier.SOURCE
    capability = "image_generation"
    provider = "library_of_congress"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "No API key required. Library of Congress API is open access:\n"
        "  https://www.loc.gov/apis/"
    )
    agent_skills = []

    capabilities = ["search_image", "download_image", "historical_image"]
    supports = {
        "orientation_filter": False,
        "size_filter": False,
        "color_filter": False,
        "locale": False,
        "free_commercial_use": True,
    }
    best_for = [
        "US historical photographs, documents, and archival records",
        "public-domain primary sources for dark history / true crime / documentary content",
        "high-credibility archival footage stills",
    ]
    not_good_for = [
        "modern stock photography (use pexels_image/pixabay_image instead)",
        "non-US historical topics (coverage skews US-centric)",
        "guaranteed rights-clear results outside the public domain (always check rights field)",
    ]

    input_schema = {
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {"type": "string", "description": "Search term"},
            "per_page": {"type": "integer", "default": 5, "minimum": 1, "maximum": 50},
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["query", "per_page"]
    side_effects = ["writes image file to output_path", "calls loc.gov API"]
    user_visible_verification = [
        "Check that downloaded image matches the intended scene",
        "Check the rights field — most LOC items are public domain but some "
        "carry usage restrictions",
    ]

    SEARCH_URL = "https://www.loc.gov/search/"

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        import requests

        start = time.time()
        query = inputs["query"]
        per_page = inputs.get("per_page", 5)
        headers = {"User-Agent": "OpenMontage/0.1 (https://github.com/riy389/OpenMontage)"}

        try:
            search_response = requests.get(
                self.SEARCH_URL,
                headers=headers,
                params={
                    "q": query,
                    "fo": "json",
                    "c": per_page,
                    "fa": "online-format:image",
                },
                timeout=30,
            )
            search_response.raise_for_status()
            data = search_response.json()

            results = data.get("results", [])
            if not results:
                return ToolResult(
                    success=False,
                    error=f"No images found for query: {query}",
                )

            # Pick the first result with a usable image URL.
            item = None
            image_url = None
            for candidate in results:
                image_urls = candidate.get("image_url") or []
                if image_urls:
                    item = candidate
                    image_url = image_urls[-1]  # largest is typically last
                    break

            if item is None or not image_url:
                return ToolResult(success=False, error="No downloadable image URL in results")

            if image_url.startswith("//"):
                image_url = "https:" + image_url

            title = item.get("title", "loc_image")
            rights = item.get("rights") or item.get("rights_advisory") or "Unknown — verify on item page"

            image_response = requests.get(image_url, headers=headers, timeout=60)
            image_response.raise_for_status()

            safe_name = "".join(c if c.isalnum() else "_" for c in title)[:80]
            output_path = Path(inputs.get("output_path", f"{safe_name}.jpg"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_response.content)

        except Exception as e:
            return ToolResult(success=False, error=f"Library of Congress image search failed: {e}")

        return ToolResult(
            success=True,
            data={
                "provider": "library_of_congress",
                "title": title,
                "rights": rights,
                "query": query,
                "output": str(output_path),
                "results_returned": len(results),
                "source_url": item.get("id", ""),
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=round(time.time() - start, 2),
        )
