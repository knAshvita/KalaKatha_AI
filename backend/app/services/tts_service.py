"""
app/services/tts_service.py  –  KalaKatha AI TTS Service
══════════════════════════════════════════════════════════
Text-to-Speech service using Gemini's speech generation API.

Responsibilities
────────────────
  • synthesize_speech(text, voice)
      Lower-level function: synthesize arbitrary text → base64-encoded WAV.

  • synthesize_chapter(narration, artwork_title, chapter_title, guide_mode)
      Higher-level function: build a museum-guide narration prompt tuned to
      the artwork context, generate audio, save to a temp WAV file, and
      return the on-disk path.

Implementation Notes
─────────────────────
  • Gemini TTS returns raw PCM audio (audio/L16;codec=pcm;rate=24000).
  • We repack the raw PCM into a standard WAV container so browsers and
    HTML5 <audio> elements can play it without any client-side decoding.
  • The StorytellerAgent remains a separate Google ADK specialist agent.
    This service only handles audio synthesis, never agent orchestration.

Reference: https://ai.google.dev/gemini-api/docs/speech-generation
"""
from __future__ import annotations

import asyncio
import io
import logging
import os
import re
import uuid
import wave
from pathlib import Path

from google import genai
from google.genai import types as genai_types

from app.config import get_settings, rotate_api_key, get_all_api_keys
from app.utils.image_utils import bytes_to_base64

logger = logging.getLogger("kalakatha.tts_service")

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

_TTS_MODEL = "gemini-2.5-flash-preview-tts"
_DEFAULT_VOICE = "Puck"
_PCM_SAMPLE_RATE = 24000
_PCM_CHANNELS = 1
_PCM_SAMPLE_WIDTH = 2  # 16-bit

# Guide-mode → voice mapping (Gemini prebuilt voices)
# See: https://ai.google.dev/gemini-api/docs/speech-generation#voices
_GUIDE_VOICE_MAP: dict[str, str] = {
    "storyteller": "Puck",        # Expressive, warm, imaginative
    "professor": "Charon",        # Deep, authoritative, scholarly
    "friendly": "Aoede",          # Warm, conversational, inviting
    "accessibility": "Leda",      # Clear, calm, measured
}

# Temporary audio output directory
_AUDIO_DIR = Path("audio_cache")


def _get_audio_dir() -> Path:
    """Return the audio cache directory, creating it if necessary."""
    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return _AUDIO_DIR


def _pcm_to_wav(pcm_data: bytes) -> bytes:
    """
    Convert raw PCM bytes (L16, 24 kHz, mono) returned by Gemini TTS
    into a valid RIFF WAV container that browsers can play natively.

    Args:
        pcm_data: Raw 16-bit little-endian PCM samples at 24000 Hz.

    Returns:
        Full WAV file bytes including RIFF header.
    """
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(_PCM_CHANNELS)
        wav_file.setsampwidth(_PCM_SAMPLE_WIDTH)
        wav_file.setframerate(_PCM_SAMPLE_RATE)
        wav_file.writeframes(pcm_data)
    return wav_io.getvalue()


def _build_narration_prompt(
    narration: str,
    artwork_title: str,
    chapter_title: str,
    guide_mode: str,
) -> str:
    """
    Wrap the raw narration text in a TTS-optimised prompt that instructs
    Gemini to speak in the voice of a museum guide.

    The prompt shapes:
      • Delivery pace (slow, measured)
      • Warmth and emotional tone matching guide_mode
      • Clear articulation of art-historical names and terms
    """
    mode_instructions = {
        "storyteller": (
            "Deliver this as a captivating, slightly theatrical museum storyteller. "
            "Speak with warmth, wonder, and poetic cadence. "
            "Pause meaningfully between visual details. "
            "Let your voice carry the mystery and beauty of the artwork."
        ),
        "professor": (
            "Deliver this as a distinguished art history professor. "
            "Speak with measured authority, precise articulation, and scholarly depth. "
            "Emphasise technical terms and historical context."
        ),
        "friendly": (
            "Deliver this as an enthusiastic, friendly museum docent. "
            "Use a warm, conversational tone. "
            "Be approachable and encouraging, as if speaking to a curious first-time visitor."
        ),
        "accessibility": (
            "Deliver this in a clear, calm, and deliberate manner. "
            "Speak at a measured pace with precise spatial descriptions. "
            "Pause between zones to let the listener build a mental image."
        ),
    }
    instruction = mode_instructions.get(
        guide_mode.lower(), mode_instructions["storyteller"]
    )

    # Strip any markdown that would be spoken literally
    clean_narration = re.sub(r"\*{1,2}|_{1,2}", "", narration).strip()

    return (
        f"<persona>{instruction}</persona>\n\n"
        f"<context>Artwork: {artwork_title} | Chapter: {chapter_title}</context>\n\n"
        f"<narration>{clean_narration}</narration>"
    )


async def synthesize_speech(text: str, voice: str = _DEFAULT_VOICE) -> str:
    """
    Convert arbitrary text to speech using Gemini TTS.

    Used by the legacy POST /api/narrate endpoint.

    Args:
        text:  The text to synthesize (max ~3000 chars for best results).
        voice: A Gemini-supported prebuilt voice name.

    Returns:
        Base64-encoded WAV audio string, ready for JSON transport.

    Raises:
        RuntimeError: If GEMINI_API_KEY is not configured.
        Exception:    On API errors.
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    keys_pool = get_all_api_keys()
    max_attempts = max(3, len(keys_pool) * 2)

    for attempt in range(max_attempts):
        try:
            active_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.gemini_api_key
            client = genai.Client(api_key=active_key)
            response = await client.aio.models.generate_content(
                model=_TTS_MODEL,
                contents=text,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai_types.SpeechConfig(
                        voice_config=genai_types.VoiceConfig(
                            prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )

            pcm_data: bytes = response.candidates[0].content.parts[0].inline_data.data
            wav_bytes = _pcm_to_wav(pcm_data)
            return bytes_to_base64(wav_bytes)
        except Exception as exc:
            err_str = str(exc).lower()
            is_transient = (
                "429" in err_str
                or "resource_exhausted" in err_str
                or "quota" in err_str
                or "503" in err_str
                or "unavailable" in err_str
            )
            if is_transient and attempt < max_attempts - 1:
                rotate_api_key()
                delay = 1.5 * (attempt + 1)
                logger.warning(
                    "TTS transient error on attempt %d/%d (%s). Rotating key and retrying in %.1fs...",
                    attempt + 1,
                    max_attempts,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                raise


async def synthesize_chapter(
    narration: str,
    artwork_title: str,
    chapter_title: str,
    guide_mode: str = "storyteller",
) -> tuple[Path, str]:
    """
    Synthesize a StorytellerAgent chapter narration using Gemini TTS.

    The function:
      1. Builds a museum-guide–optimised TTS prompt.
      2. Selects the correct Gemini voice for the active guide_mode.
      3. Calls Gemini TTS and receives raw PCM audio.
      4. Converts PCM → WAV container.
      5. Saves the WAV to the audio cache directory with a unique filename.
      6. Returns (file_path, audio_url) where audio_url is the relative URL
         the frontend can use to stream the file.

    Args:
        narration:     The StoryChapter.narration text to synthesize.
        artwork_title: Title of the artwork (used in the TTS prompt).
        chapter_title: Title of the chapter (used in the TTS prompt).
        guide_mode:    Guide persona: storyteller | professor | friendly | accessibility.

    Returns:
        (Path, str): Absolute path to the saved WAV file and its public URL path.

    Raises:
        RuntimeError: If GEMINI_API_KEY is not configured.
        Exception:    On API or file-system errors.
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    voice = _GUIDE_VOICE_MAP.get(guide_mode.lower(), _DEFAULT_VOICE)
    prompt = _build_narration_prompt(narration, artwork_title, chapter_title, guide_mode)

    keys_pool = get_all_api_keys()
    max_attempts = max(3, len(keys_pool) * 2)

    for attempt in range(max_attempts):
        try:
            active_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.gemini_api_key
            client = genai.Client(api_key=active_key)
            response = await client.aio.models.generate_content(
                model=_TTS_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai_types.SpeechConfig(
                        voice_config=genai_types.VoiceConfig(
                            prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )

            pcm_data: bytes = response.candidates[0].content.parts[0].inline_data.data
            wav_bytes = _pcm_to_wav(pcm_data)

            # Persist to disk with a unique filename
            audio_dir = _get_audio_dir()
            filename = f"{uuid.uuid4().hex}.wav"
            file_path = audio_dir / filename
            file_path.write_bytes(wav_bytes)

            audio_url = f"/audio/{filename}"
            return file_path, audio_url
        except Exception as exc:
            err_str = str(exc).lower()
            is_transient = (
                "429" in err_str
                or "resource_exhausted" in err_str
                or "quota" in err_str
                or "503" in err_str
                or "unavailable" in err_str
            )
            if is_transient and attempt < max_attempts - 1:
                rotate_api_key()
                delay = 1.5 * (attempt + 1)
                logger.warning(
                    "TTS transient error on attempt %d/%d (%s). Rotating key and retrying in %.1fs...",
                    attempt + 1,
                    max_attempts,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                raise
