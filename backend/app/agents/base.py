"""
app/agents/base.py  –  KalaKatha AI Google ADK Base Agent
════════════════════════════════════════════════════════
Base class inheriting from google.adk.agents.Agent.
"""
from __future__ import annotations

from typing import Any
from google.adk.agents import Agent


class KalaKathaBaseAgent(Agent):
    """
    KalaKatha specialist agent base class.
    Inherits directly from official google.adk.agents.Agent (LlmAgent).
    Provides bridge properties for system instructions and schema inspection.
    """

    @property
    def response_schema(self) -> Any:
        return self.output_schema

    @property
    def system_instructions(self) -> str:
        return self.instruction or ""

    @property
    def config(self) -> "KalaKathaBaseAgent":
        return self
