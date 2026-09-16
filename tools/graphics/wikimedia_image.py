"""Historical/public-domain image acquisition from Wikimedia Commons (free, no API key)."""

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


class WikimediaImage(BaseTool):
    name = "wikimedia_image"
    version = "0.1.0"
    tier = ToolTier.SOURCE
    capability = "image_generation"
    provider = "wikimedia"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "No API key required. Wikimedia Commons API is open access:\n"
        "  https://commons.wikimedia.org/w/api.php"
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
        "historical photographs, paintings, and documents (public domain)",
        "real people, places, and events from history",
        "dark history / true crime / archival storytelling niches",
    ]
    not_good_for = [
        "modern stock photography (use pexels_image/pixabay_image instead)",
        "custom/specific compositions",
        "guaranteed high-resolution results (varies per item)",
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
    side_effects = ["writes image file to output_path", "calls Wikimedia Commons API"]
    user_visible_verification = [
        "Check that downloaded image matches the intended scene",
        "Check the license field — most Commons files are public domain or "
        "CC-BY/CC-BY-SA, which may require attribution",
    ]

    SEARCH_URL = "https://commons.wikimedia.org/w/api.php"

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
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": f"filetype:bitmap {query}",
                    "gsrnamespace": 6,  # File: namespace
                    "gsrlimit": per_page,
                    "prop": "imageinfo",
                    "iiprop": "url|extmetadata|size",
                    "iiurlwidth": 1600,
                },
                timeout=30,
            )
            search_response.raise_for_status()
            data = search_response.json()

            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return ToolResult(
                    success=False,
                    error=f"No images found for query: {query}",
                )

            # Pick the first result (agent can refine query if needed)
            page = next(iter(pages.values()))
            imageinfo = page.get("imageinfo", [{}])[0]
            image_url = imageinfo.get("thumburl") or imageinfo.get("url")
            if not image_url:
                return ToolResult(success=False, error="No downloadable URL in result")

            extmetadata = imageinfo.get("extmetadata", {})
            license_name = extmetadata.get("LicenseShortName", {}).get("value", "Unknown")
            artist = extmetadata.get("Artist", {}).get("value", "Unknown")

            image_response = requests.get(image_url, headers=headers, timeout=60)
            image_response.raise_for_status()

            file_title = page.get("title", f"wikimedia_{page.get('pageid', 'unknown')}")
            safe_name = "".join(c if c.isalnum() else "_" for c in file_title)[:80]
            output_path = Path(inputs.get("output_path", f"{safe_name}.jpg"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_response.content)

        except Exception as e:
            return ToolResult(success=False, error=f"Wikimedia Commons image search failed: {e}")

        return ToolResult(
            success=True,
            data={
                "provider": "wikimedia",
                "title": file_title,
                "artist": artist,
                "license": license_name,
                "width": imageinfo.get("width"),
                "height": imageinfo.get("height"),
                "query": query,
                "output": str(output_path),
                "results_returned": len(pages),
                "source_url": imageinfo.get("descriptionurl", ""),
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=round(time.time() - start, 2),
        )
