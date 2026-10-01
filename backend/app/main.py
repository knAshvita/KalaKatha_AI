"""
app/main.py  –  KalaKatha AI FastAPI Application
══════════════════════════════════════════════════
Entry point for Uvicorn.

Architecture
─────────────
  FastAPI layer   →  app/api/         (HTTP routing, validation, error handling)
  ADK layer       →  app/agent.py     (root orchestrator)
  Agent layer     →  app/agents/      (6 specialist ADK agents)
  Service layer   →  app/services/    (TTS, etc.)
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.artwork import router as artwork_router
from app.api.ask import router as ask_router
from app.api.narrate import router as narrate_router
from app.api.story_audio import router as story_audio_router
from app.api.quiz import router as quiz_router
from app.api.session_api import router as session_router
from app.api.health import router as health_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    print(f"\n[KalaKatha] {settings.app_name} v{settings.app_version} starting...")
    if not settings.gemini_api_key:
        print(
            "[WARNING] GEMINI_API_KEY is not set. "
            "All ADK agent calls will fail. Set it in your .env file."
        )
    else:
        print("[OK] GEMINI_API_KEY is configured.")
    print(
        f"API docs: http://localhost:8000/docs\n"
        f"Health:   http://localhost:8000/api/health\n"
    )
    yield
    print(f"[KalaKatha] {settings.app_name} shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "**KalaKatha AI** — Multi-agent AI art experience backend.\n\n"
            "Powered by **Google ADK** + **Gemini** multimodal models.\n\n"
            "### Agents\n"
            "| Agent | Responsibility |\n"
            "|-------|----------------|\n"
            "| KalaKatha Root Agent | Coordinates all specialist ADK agents and synthesizes KalaKathaExperience |\n"
            "| Art Analyst | Visual observation (objects, people, colors, composition) |\n"
            "| Context Agent | Historical & cultural context |\n"
            "| Accessibility Agent | Screen-reader descriptions & spatial layout |\n"
            "| Storyteller Agent | Immersive 4-6 chapter museum narrative |\n"
            "| Learning Agent | Educational content & 3 multiple-choice questions |\n"
            "| Explore Agent | Normalized interactive hotspots (0.0 to 1.0) |\n"
            "| Ask Agent | Interactive Q&A grounded in specialist analyses |\n\n"
            "### Endpoints\n"
            "- `POST /api/analyze` — Upload artwork → KalaKathaRootAgent ADK pipeline → KalaKathaExperience\n"
            "- `POST /api/ask` — Ask an artwork-specific question (AskAgent ADK)\n"
            "- `POST /api/story/audio` — Narrate a story chapter via Gemini TTS\n"
            "- `POST /api/quiz/answer` — Validate a multiple-choice quiz answer\n"
            "- `GET  /api/session/{session_id}` — Retrieve full KalaKathaExperience for session\n"
            "- `POST /api/narrate` — Narrate arbitrary text via Gemini TTS\n"
            "- `GET  /api/health` — Liveness check\n"
            "- `GET  /audio/{filename}` — Stream generated WAV audio files\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static files — serve generated WAV audio ──────────────────────────────
    audio_dir = Path("audio_cache")
    audio_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(artwork_router)
    app.include_router(ask_router)
    app.include_router(narrate_router)
    app.include_router(story_audio_router)
    app.include_router(quiz_router)
    app.include_router(session_router)

    return app


app = create_app()
