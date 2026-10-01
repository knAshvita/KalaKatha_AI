"""
app/agents/adk_runner.py  –  KalaKatha AI ADK Execution Bridge
══════════════════════════════════════════════════════════════
Executes Google ADK agents using the official google-adk Runner
and google.genai multimodal types.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
from pathlib import Path
from typing import Any, Tuple

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from app.config import get_all_api_keys, get_settings, rotate_api_key

logger = logging.getLogger(__name__)


def create_image_part(image_path: Path) -> genai_types.Part:
    """Create a multimodal image Part from a local file path."""
    if not image_path.exists():
        raise FileNotFoundError(f"Artwork image not found: {image_path}")

    suffix = image_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
    }
    mime_type = mime_map.get(suffix, "image/jpeg")
    data = image_path.read_bytes()
    return genai_types.Part.from_bytes(data=data, mime_type=mime_type)


def create_text_part(text: str) -> genai_types.Part:
    """Create a text Part from a string."""
    return genai_types.Part.from_text(text=text)


def strip_code_fences(raw: str) -> str:
    """Remove markdown code fences (```json ... ```) from output text."""
    raw = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return raw


async def run_adk_agent(
    agent: Agent,
    parts: list[genai_types.Part],
    session_id: str | None = None,
    user_id: str = "kalakatha_user",
) -> Tuple[dict[str, Any] | None, str]:
    """
    Execute a Google ADK Agent via Runner and InMemorySessionService.
    Automatically rotates to the next API key if a 429/quota error occurs.

    Returns:
        (structured_data, raw_text_accumulated)
    """
    settings = get_settings()
    sid = session_id or f"adk_{uuid.uuid4().hex[:12]}"

    keys_pool = get_all_api_keys()
    max_attempts = max(3, len(keys_pool) * 2)

    for attempt in range(max_attempts):
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="kalakatha",
            session_service=session_service,
            auto_create_session=True,
        )

        message = genai_types.Content(role="user", parts=parts)
        text_chunks: list[str] = []
        structured_data: dict[str, Any] | None = None

        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=sid,
                new_message=message,
            ):
                # 1. Capture text from response content
                if event.content and event.content.parts:
                    for p in event.content.parts:
                        if getattr(p, "text", None):
                            text_chunks.append(p.text)

                # 2. Check actions state_delta for structured output
                if event.actions and event.actions.state_delta:
                    if agent.output_key and agent.output_key in event.actions.state_delta:
                        val = event.actions.state_delta[agent.output_key]
                        if isinstance(val, dict):
                            structured_data = val
                        elif isinstance(val, str):
                            try:
                                structured_data = json.loads(strip_code_fences(val))
                            except Exception:
                                pass

            # 3. Check final session state as fallback
            try:
                final_session = await session_service.get_session(
                    app_name="kalakatha",
                    user_id=user_id,
                    session_id=sid,
                )
                if final_session and final_session.state and agent.output_key:
                    state_val = final_session.state.get(agent.output_key)
                    if isinstance(state_val, dict):
                        structured_data = state_val
                    elif isinstance(state_val, str) and not structured_data:
                        try:
                            structured_data = json.loads(strip_code_fences(state_val))
                        except Exception:
                            pass
            except Exception:
                pass

            raw_text = "".join(text_chunks)
            if not structured_data and raw_text:
                try:
                    structured_data = json.loads(strip_code_fences(raw_text))
                except Exception:
                    pass

            return structured_data, raw_text

        except Exception as exc:
            err_str = str(exc).lower()
            is_transient = (
                "429" in err_str
                or "resource_exhausted" in err_str
                or "quota" in err_str
                or "503" in err_str
                or "unavailable" in err_str
                or "high demand" in err_str
            )
            if is_transient and attempt < max_attempts - 1:
                # Respect explicit server retry delay if provided
                retry_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
                if retry_match:
                    delay = float(retry_match.group(1)) + 1.0
                else:
                    delay = max(2.5 * (attempt + 1), 5.0 if ("429" in err_str or "resource_exhausted" in err_str) else 1.5)

                next_key = rotate_api_key()
                if next_key:
                    if hasattr(agent, "model"):
                        try:
                            from google.genai import Client
                            agent.model.client = Client(api_key=next_key)
                        except Exception as update_err:
                            logger.debug("Could not assign model.client: %s", update_err)
                    delay = min(delay, 2.0)

                logger.warning(
                    "Transient Gemini API error on attempt %d/%d (%s). Rotating key and retrying in %.1fs...",
                    attempt + 1,
                    max_attempts,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
                continue
            raise

    return None, ""
