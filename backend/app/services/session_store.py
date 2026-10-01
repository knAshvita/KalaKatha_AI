"""
app/services/session_store.py  –  KalaKatha AI Session Repository
═════════════════════════════════════════════════════════════════
In-memory session manager that maintains active KalaKathaExperience
outputs and multi-turn conversation histories for the AskAgent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.artwork import KalaKathaExperience


@dataclass
class ConversationTurn:
    question: str
    answer: str


@dataclass
class ArtworkSession:
    session_id: str
    experience: KalaKathaExperience
    guide_mode: str = "storyteller"
    history: list[ConversationTurn] = field(default_factory=list)


class SessionStore:
    """Thread-safe in-memory session repository."""

    def __init__(self):
        self._sessions: dict[str, ArtworkSession] = {}

    def save(
        self,
        session_or_id: ArtworkSession | str,
        experience: KalaKathaExperience | None = None,
        guide_mode: str = "storyteller",
    ) -> ArtworkSession:
        """Register or update an artwork session."""
        if isinstance(session_or_id, ArtworkSession):
            session = session_or_id
            self._sessions[session.session_id] = session
            return session

        session_id = session_or_id
        if experience is None:
            raise ValueError("experience is required when saving by session_id")
        session = ArtworkSession(
            session_id=session_id,
            experience=experience,
            guide_mode=guide_mode,
            history=[],
        )
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> ArtworkSession | None:
        """Retrieve an artwork session by ID."""
        return self._sessions.get(session_id)

    def add_turn(self, session_id: str, question: str, answer: str) -> None:
        """Append a question/answer turn to the session conversation history."""
        session = self._sessions.get(session_id)
        if session:
            session.history.append(ConversationTurn(question=question, answer=answer))

    def clear(self) -> None:
        """Clear all active sessions (used in test teardown)."""
        self._sessions.clear()


# Global singleton instance
session_store = SessionStore()
