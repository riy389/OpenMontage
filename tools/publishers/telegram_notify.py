"""Telegram review notifier — human-approval gate before further distribution.

Sends the finished (or exported) video to a Telegram chat so a human can
review it before anything gets published further (e.g. to YouTube). This
tool ONLY sends the notification and records a `pending_review` entry — it
does not wait for or read the approval reply. Reading the approval and
deciding whether to proceed to `youtube_upload` (or to mark the `publish`
stage checkpoint complete) is the orchestrating agent's job, per
`skills/meta/publish-distribution.md`.

This mirrors the WealthVault pattern: Telegram is a gate, not a publish
destination. A successful send here means "awaiting human decision", never
"published".
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

TELEGRAM_API_BASE = "https://api.telegram.org"

# Telegram's sendVideo caps at 50 MB over the Bot API. Above this, execute()
# falls back to a text notification with the local file path instead of
# failing outright — the reviewer still gets pinged, they just open the
# file from the Codespace/VPS directly.
MAX_VIDEO_BYTES = 50 * 1024 * 1024


class TelegramNotify(BaseTool):
    name = "telegram_notify"
    version = "0.1.0"
    tier = ToolTier.PUBLISH
    capability = "publish"
    provider = "telegram"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = ["env:TELEGRAM_BOT_TOKEN", "env:TELEGRAM_CHAT_ID", "python:requests"]
    install_instructions = (
        "Create a bot via @BotFather to get TELEGRAM_BOT_TOKEN, then message "
        "the bot and fetch https://api.telegram.org/bot<token>/getUpdates to "
        "find your chat_id. Set both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID "
        "in .env."
    )

    agent_skills = []

    capabilities = ["send_for_review", "write_publish_log"]
    supports = {
        "gate": True,
        "uploads": False,
        "free": True,  # Telegram Bot API itself has no cost
    }
    best_for = [
        "sending a finished video to a human reviewer before further distribution",
        "a lightweight mobile-friendly approval gate (matches the WealthVault pattern)",
    ]
    not_good_for = [
        "publishing to an audience (Telegram is a review channel, not a destination)",
        "videos over 50 MB (Bot API sendVideo limit — falls back to a text notification with the local path)",
    ]

    input_schema = {
        "type": "object",
        "required": ["video_path"],
        "properties": {
            "video_path": {
                "type": "string",
                "description": "Path to the video to send for review (e.g. renders/final.mp4 or the exported copy).",
            },
            "caption": {
                "type": "string",
                "description": "Message caption — typically the working title or a one-line summary.",
            },
            "project_id": {"type": "string"},
            "chat_id": {
                "type": "string",
                "description": "Override the TELEGRAM_CHAT_ID env var for this call.",
            },
            "timestamp": {
                "type": "string",
                "description": "Override the ISO-8601 timestamp (mainly for deterministic tests).",
            },
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "publish_log": {"type": "object"},
            "telegram_message_id": {"type": "integer"},
            "telegram_chat_id": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=128, vram_mb=0, disk_mb=0, network_required=True
    )
    side_effects = ["sends a message + video to a Telegram chat"]
    user_visible_verification = [
        "Check the Telegram chat for the video and reply with your decision",
    ]

    # ---- Execution ----

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        video_path = Path(inputs["video_path"]).expanduser()
        if not video_path.is_file():
            return ToolResult(success=False, error=f"video_path not found: {video_path}")

        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = inputs.get("chat_id") or os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            return ToolResult(
                success=False,
                error="TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID not set. "
                + self.install_instructions,
            )

        caption = inputs.get("caption", "")
        size = video_path.stat().st_size
        oversized = size > MAX_VIDEO_BYTES

        try:
            if oversized:
                # Over the Bot API sendVideo limit: fall back to a text
                # notification with the local path instead of failing the
                # whole tool. The reviewer still gets pinged; they just have
                # to open the file from the Codespace/VPS themselves.
                note = (
                    f"{caption}\n\n"
                    f"[Video too large for Telegram: {size / (1024 * 1024):.1f} MB, "
                    f"limit is {MAX_VIDEO_BYTES / (1024 * 1024):.0f} MB]\n"
                    f"Local path: {video_path}"
                ).strip()
                response = requests.post(
                    f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": note},
                    timeout=30,
                )
            else:
                with open(video_path, "rb") as f:
                    response = requests.post(
                        f"{TELEGRAM_API_BASE}/bot{token}/sendVideo",
                        data={"chat_id": chat_id, "caption": caption},
                        files={"video": (video_path.name, f, "video/mp4")},
                        timeout=120,
                    )
        except requests.RequestException as exc:
            return ToolResult(success=False, error=f"Telegram request failed: {exc}")

        if response.status_code != 200:
            return ToolResult(
                success=False,
                error=f"Telegram API returned {response.status_code}: {response.text[:300]}",
            )

        payload = response.json()
        if not payload.get("ok"):
            return ToolResult(
                success=False,
                error=f"Telegram API error: {payload.get('description', 'unknown error')}",
            )

        message = payload["result"]
        message_id = message.get("message_id")
        timestamp = inputs.get("timestamp") or datetime.now(timezone.utc).isoformat()

        # publish_log entry: pending_review, NOT published — see module docstring.
        entry: dict[str, Any] = {
            "platform": "telegram",
            "status": "pending_review",
            "timestamp": timestamp,
        }

        publish_log = {"version": "1.0", "entries": [entry]}

        try:
            from schemas.artifacts import validate_artifact

            validate_artifact("publish_log", publish_log)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolResult(success=False, error=f"publish_log failed schema validation: {exc}")

        return ToolResult(
            success=True,
            data={
                "publish_log": publish_log,
                "telegram_message_id": message_id,
                "telegram_chat_id": str(chat_id),
            },
        )
