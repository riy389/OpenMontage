# Publish Distribution — Meta Skill

## When to Use

During the `publish` stage, after `export_bundle` has produced the local
package (`exports/<project_name>/`) and its `publish_log` entry
(`status: "exported"`). This skill teaches the agent how to optionally push
that package further — notify a human via Telegram, and/or upload to
YouTube — using whatever `capability="publish"` provider tools are
registered and configured.

This skill is cross-cutting: every pipeline's `publish-director.md` reads it
at the same point, after packaging and before the stage checkpoint is
written. It does not replace `export_bundle` — it runs after it, and it is
optional per project, not a hard requirement of Rule Zero.

## Protocol

### Step 1: Discover Available Distribution Providers

```bash
python -c "
from tools.tool_registry import registry
import json
registry.discover()
print(json.dumps(registry.get_by_capability('publish'), indent=2, default=str))
"
```

Or use the preflight summary already gathered earlier in the run
(`provider_menu_summary()` — see `AGENT_GUIDE.md` > Mandatory Preflight).
Do not hardcode provider names — read `capability="publish"` tools from the
registry, same as any other capability family. `export_bundle` will always
appear here (local, always available); `telegram_notify` and
`youtube_upload` appear only when their dependencies
(`env:TELEGRAM_BOT_TOKEN` / `env:TELEGRAM_CHAT_ID`, YouTube OAuth vars) are
configured.

### Step 2: Present the Choice — Never Pick Silently

Per the Decision Communication Contract in `AGENT_GUIDE.md`, distribution
beyond the local export bundle is a **major production choice** and must be
proposed, not assumed. After `export_bundle` succeeds, tell the user what
packaged and ask what to do next:

```
Export packaged at exports/<project_name>/.

Distribution options available:
  - Send to Telegram for review (telegram_notify) — configured
  - Upload to YouTube (youtube_upload) — configured, visibility: [ask]
  - Local export only, no further distribution

Which would you like?
```

If a provider is unconfigured, say so and offer the one-line env var fix
(read `install_instructions` from that tool's `get_info()`), same pattern as
the Mandatory Preflight provider menu. Do not nag if the user declines.

### Step 3: Execute the Chosen Provider(s)

Each provider tool is called like any other `BaseTool`:

```python
from tools.tool_registry import registry

telegram = registry.get("telegram_notify")
result = telegram.execute({
    "video_path": render_report["output_path"],
    "caption": proposal_packet["title"],
    "project_id": project_id,
})
```

`result` is a `ToolResult` (`.success`, `.data`, `.error`, per
`tools/base_tool.py`). On success, `result.data` should carry enough to
build a `publish_log` entry (see Step 4) — at minimum a `timestamp` and, if
the platform returns one, a `url` or message reference.

**Telegram is a human-approval gate, not a publish destination.** This
mirrors the existing WealthVault pattern exactly: a successful
`telegram_notify` call means the video is now awaiting a human decision in
Telegram — record it as `status: "pending_review"` in the `publish_log`
entry, never `"published"`. Nothing downstream (especially `youtube_upload`)
may run until that approval comes back.

**YouTube upload is a real publish action**, and it only happens *after*
the Telegram approval is received (or immediately, if the user opted out of
Telegram review for this project at Step 2). Treat a successful
`youtube_upload` call as `status: "published"`, and capture `video_id`,
`url`, and `visibility` from the result.

If the user asked for Telegram review before YouTube upload, treat the
Telegram send as a hard gate: wait for the user's explicit go-ahead (their
reply, in chat or reported back from Telegram) before calling
`youtube_upload`. This mirrors "No Unilateral Substitutions" in
`AGENT_GUIDE.md` — do not upload without the confirmation the user asked
for.

### Step 3.5: Confirm Publication Back to Telegram

`telegram_notify` has exactly one job (send a message/video to the
configured Telegram chat) but it is used at **two different moments** with
two different meanings, distinguished by what you pass, not by a separate
tool:

- **Before publishing** (Step 3 above): send the video itself for review.
  `publish_log` entry: `status: "pending_review"`.
- **After `youtube_upload` succeeds**: send a short confirmation — no video
  attachment needed, just a caption pointing at the live URL, e.g.
  `"✅ Published: https://youtu.be/<video_id>"`. This mirrors the
  WealthVault pattern's post-upload notification and must not be skipped —
  a human who approved a gated publish expects to hear that it actually
  went live, not just that the gate was cleared.

Do this by calling `telegram_notify` again with the result of
`youtube_upload`:

```python
youtube = registry.get("youtube_upload")
yt_result = youtube.execute({...})

if yt_result.success:
    telegram = registry.get("telegram_notify")
    telegram.execute({
        "video_path": ...,  # reuse the same local video; sendVideo will
                             # attach it again, or pass a text-only path if
                             # you'd rather not resend the file
        "caption": f"✅ Published: {yt_result.data['url']}",
        "project_id": project_id,
    })
```

This second call does **not** produce its own `pending_review` gate in the
same sense — it's a notification, not a request for a decision. Still
record it as its own `publish_log` entry (`platform: "telegram"`,
`status: "published"` is reasonable here since nothing further is pending
on it) rather than silently dropping it from the log — see Step 4.

### Step 4: Append to `publish_log` — Do Not Invent Fields

`schemas/artifacts/publish_log.schema.json` sets `additionalProperties:
false` at both the root and the entry level. Only these entry fields exist:
`platform`, `status`, `url`, `video_id`, `visibility`, `export_path`,
`timestamp`, `metadata_used`, `error`. `status` must be one of `published`,
`exported`, `failed`, `draft`, `pending_review`.

Add one entry per provider call, alongside the `export_bundle` entry
already in the artifact — do not overwrite it. A full run with Telegram
review + YouTube upload + publish confirmation produces three Telegram/
YouTube entries in addition to `export_bundle`'s:

```json
{
  "platform": "telegram",
  "status": "pending_review",
  "timestamp": "2026-09-04T12:00:00+00:00"
}
```

```json
{
  "platform": "youtube",
  "status": "published",
  "video_id": "abc123",
  "url": "https://youtu.be/abc123",
  "visibility": "public",
  "timestamp": "2026-09-04T12:05:00+00:00",
  "metadata_used": {
    "title": "...",
    "description": "...",
    "hashtags": ["#ai"],
    "chapters": [{"start_seconds": 0, "title": "Introduction"}]
  }
}
```

```json
{
  "platform": "telegram",
  "status": "published",
  "timestamp": "2026-09-04T12:06:00+00:00"
}
```

If a provider call fails, still add an entry — `status: "failed"`,
`error: "<message>"`. A failed distribution attempt is not a reason to fail
the whole `publish` stage checkpoint; `export_bundle`'s local package still
stands. Surface the failure to the user per "Escalate Blockers Explicitly"
in `AGENT_GUIDE.md` and let them decide whether to retry.

Platform-specific details that don't fit the fixed entry fields (a Telegram
`chat_id`/`message_id`, for instance) do not belong in `entries[]` —
`additionalProperties: false` forbids it there. If they're worth keeping,
put them in the artifact's root-level `metadata` object instead, which is
unconstrained.

### Step 5: Checkpoint the `publish` Stage

`publish` is itself a gated stage in most pipeline manifests. Write the
checkpoint the normal way (`skills/meta/checkpoint-protocol.md`), with the
now-complete `publish_log` (export entry + any distribution entries) as the
stage's canonical artifact:

```python
from lib.checkpoint import write_checkpoint

write_checkpoint(
    pipeline_dir, project_id,
    stage="publish",
    status="awaiting_human",   # or "completed" if publish doesn't gate for this pipeline
    artifacts={"publish_log": publish_log_dict},
    pipeline_type=pipeline_type,
)
```

If `publish` gates (`human_approval_default: true` for this pipeline),
present the summary and **end the turn** — same rule as every other gated
stage. Telegram approval and the `publish` stage's own human-approval gate
are two separate decisions: getting a thumbs-up in Telegram does not by
itself satisfy the stage gate. Confirm explicitly with the user before
writing `status="completed", human_approved=True`.

## Key Principles

1. **Distribution is optional, packaging is not.** `export_bundle` always
   runs. Telegram/YouTube only run if the user opts in at Step 2.
2. **Never pick a distribution provider silently.** Same rule as
   provider/model choice anywhere else in the pipeline.
3. **Telegram is a human-approval gate, matching the existing WealthVault
   pattern** — a video sent to Telegram is `pending_review`, not
   `published`. YouTube upload (or any further distribution) only proceeds
   after that approval is explicitly received.
4. **`telegram_notify` is one tool used twice, for two different purposes**
   — a pre-publish review request (`pending_review`) and a post-publish
   confirmation (`status: "published"`, matching WealthVault's "✅
   Published: <url>" notification). Never skip the second call after a
   successful `youtube_upload` — silently omitting it leaves the human who
   approved the gate without confirmation it actually went live.
5. **Never invent `publish_log` fields.** The schema is closed
   (`additionalProperties: false`). Anything that doesn't fit goes in the
   artifact's root `metadata`, not in an entry.
6. **A failed distribution call doesn't fail the stage.** Log it, tell the
   user, let them decide — the local export is still a valid deliverable.
