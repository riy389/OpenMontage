"""YouTube uploader — real publish action, gated behind human approval.

Uploads a finished video directly to YouTube using OAuth refresh-token
credentials, resumable upload, and (optionally) a thumbnail. The
authentication and upload pattern here is adapted from the WealthVault
project's proven `youtube_upload.py` (OAuth refresh token + resumable
`MediaFileUpload`) — everything specific to WealthVault's own state files
and GitHub-Releases asset fetching was intentionally dropped, since
OpenMontage already has the video on local disk and tracks state via
`publish_log` / checkpoints instead.

Per `skills/meta/publish-distribution.md`, this tool must only be called
AFTER a human approval has been received (via Telegram review or direct
confirmation) — it performs a real, audience-facing publish action, not a
review step.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

YOUTUBE_TITLE_MAX_LEN = 100  # YouTube Data API hard limit


class YouTubeUpload(BaseTool):
    name = "youtube_upload"
    version = "0.1.0"
    tier = ToolTier.PUBLISH
    capability = "publish"
    provider = "youtube"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = [
        "env:YT_CLIENT_ID",
        "env:YT_CLIENT_SECRET",
        "env:YT_REFRESH_TOKEN",
        "python:google.oauth2.credentials",
        "python:googleapiclient",
    ]
    install_instructions = (
        "Create an OAuth 2.0 Client ID (Desktop app) in Google Cloud Console "
        "with the YouTube Data API v3 enabled, then run the OAuth consent "
        "flow once to obtain a refresh token. Set YT_CLIENT_ID, "
        "YT_CLIENT_SECRET, and YT_REFRESH_TOKEN in .env."
    )

    agent_skills = []

    capabilities = ["upload_video", "write_publish_log"]
    supports = {
        "resumable_upload": True,
        "thumbnail": True,
        "uploads": True,
    }
    best_for = [
        "publishing an approved video directly to a YouTube channel",
    ]
    not_good_for = [
        "review or approval — this is a real publish action, not a gate "
        "(use telegram_notify first)",
        "uploading without prior human approval per the Decision "
        "Communication Contract",
    ]

    input_schema = {
        "type": "object",
        "required": ["video_path", "title"],
        "properties": {
            "video_path": {
                "type": "string",
                "description": "Path to the final video to upload (e.g. exports/<project>/video/output.mp4).",
            },
            "title": {
                "type": "string",
                "description": f"Video title. Truncated to {YOUTUBE_TITLE_MAX_LEN} chars (YouTube API limit).",
            },
            "description": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "category_id": {
                "type": "string",
                "description": "YouTube video category ID. Defaults to '22' (People & Blogs) if not given.",
            },
            "visibility": {
                "type": "string",
                "enum": ["public", "private", "unlisted"],
                "description": "Defaults to 'public' if not given.",
            },
            "thumbnail_path": {
                "type": "string",
                "description": "Optional path to a thumbnail image to set after upload.",
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
            "video_id": {"type": "string"},
            "url": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=0, network_required=True
    )
    side_effects = ["publishes a video publicly (or per visibility) on YouTube"]
    user_visible_verification = [
        "Open the returned URL and confirm the video, title, and description are correct",
    ]

    # ---- Execution ----

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        video_path = Path(inputs["video_path"]).expanduser()
        if not video_path.is_file():
            return ToolResult(success=False, error=f"video_path not found: {video_path}")

        thumbnail_path = inputs.get("thumbnail_path")
        if thumbnail_path:
            thumbnail_path = Path(thumbnail_path).expanduser()
            if not thumbnail_path.is_file():
                return ToolResult(
                    success=False,
                    error=f"thumbnail_path provided but not found: {thumbnail_path}",
                )

        client_id = os.environ.get("YT_CLIENT_ID")
        client_secret = os.environ.get("YT_CLIENT_SECRET")
        refresh_token = os.environ.get("YT_REFRESH_TOKEN")
        if not client_id or not client_secret or not refresh_token:
            return ToolResult(
                success=False,
                error="Missing YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN. "
                + self.install_instructions,
            )

        title = inputs["title"][:YOUTUBE_TITLE_MAX_LEN]
        description = inputs.get("description", "")
        tags = inputs.get("tags") or []
        category_id = inputs.get("category_id", "22")  # People & Blogs
        visibility = inputs.get("visibility", "public")

        try:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
            )
            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": visibility},
            }

            media = MediaFileUpload(str(video_path), chunksize=4 * 1024 * 1024, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            while response is None:
                _status, response = request.next_chunk()

            video_id = response.get("id")
            if not video_id:
                return ToolResult(
                    success=False,
                    error="YouTube API response did not contain a video ID.",
                )

            if thumbnail_path:
                try:
                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(str(thumbnail_path)),
                    ).execute()
                except Exception as exc:
                    # Non-fatal: the video itself published successfully.
                    # Surface it via the entry's metadata rather than failing
                    # the whole publish action.
                    thumbnail_error = str(exc)
                else:
                    thumbnail_error = None
            else:
                thumbnail_error = None

        except Exception as exc:
            timestamp = inputs.get("timestamp") or datetime.now(timezone.utc).isoformat()
            failed_log = {
                "version": "1.0",
                "entries": [
                    {
                        "platform": "youtube",
                        "status": "failed",
                        "timestamp": timestamp,
                        "error": str(exc)[:500],
                    }
                ],
            }
            return ToolResult(success=False, error=str(exc), data={"publish_log": failed_log})

        timestamp = inputs.get("timestamp") or datetime.now(timezone.utc).isoformat()
        url = f"https://youtu.be/{video_id}"

        entry: dict[str, Any] = {
            "platform": "youtube",
            "status": "published",
            "video_id": video_id,
            "url": url,
            "visibility": visibility,
            "timestamp": timestamp,
            "metadata_used": {
                "title": title,
                "description": description,
                "hashtags": [t for t in tags if isinstance(t, str) and t.startswith("#")],
                "chapters": [],
            },
        }

        publish_log = {"version": "1.0", "entries": [entry]}

        try:
            from schemas.artifacts import validate_artifact

            validate_artifact("publish_log", publish_log)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolResult(success=False, error=f"publish_log failed schema validation: {exc}")

        data = {"publish_log": publish_log, "video_id": video_id, "url": url}
        if thumbnail_error:
            data["thumbnail_warning"] = thumbnail_error

        return ToolResult(success=True, data=data)
