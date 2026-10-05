"""
Agent Orchestrator
==================
Central coordinator for all three AI agents.
Provides a clean API that main.py plugs into:

  1. agent_system.start()           → starts Live Coach Agent
  2. agent_system.on_form_error()   → routes to Agent 1 (live speech)
  3. agent_system.on_rep()          → routes to Agent 1 (live speech)
  4. agent_system.finish()          → triggers Agent 2 (report) then Agent 3 (plan)
                                       returns (report, plan) dict
"""

import os
import threading
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from agents.live_coach_agent import LiveCoachAgent
from agents.report_agent import SessionReportAgent
from agents.planner_agent import ProgressPlannerAgent
from agents.db import init_db


class AgentSystem:
    """
    Drop-in coordinator for the three-agent AI trainer system.

    Configure via environment variables OR constructor args:
      OLLAMA_HOST       — Ollama base URL (default: http://127.0.0.1:11434)
      OLLAMA_*_MODEL    — per-agent model overrides
      ELEVENLABS_API_KEY — ElevenLabs API key (optional, falls back to pyttsx3)
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        use_elevenlabs: bool = True,
        enabled: bool = True,
    ):
        self.enabled = enabled
        self._started_at: Optional[str] = None
        self._last_rep_counts: Dict[str, int] = {}
        self._last_form_state: Dict[str, str] = {}
        self._good_form_counter: Dict[str, int] = {}

        el_key = elevenlabs_api_key or os.environ.get("ELEVENLABS_API_KEY")

        if not enabled:
            self._coach = None
            self._reporter = None
            self._planner = None
            return

        init_db()

        self._coach = LiveCoachAgent(
            gemini_api_key=None,
            elevenlabs_api_key=el_key,
            use_elevenlabs=use_elevenlabs,
        )
        self._reporter = SessionReportAgent(gemini_api_key=None)
        self._planner = ProgressPlannerAgent(gemini_api_key=None)

    def start(self) -> None:
        """Call at the beginning of a workout session."""
        if not self.enabled or self._coach is None:
            return
        self._started_at = datetime.now().isoformat()
        self._coach.start()
        self._coach.speak_direct(
            "Good day, sir. JARVIS online. Your workout session has begun. "
            "I'll be monitoring your form and performance throughout. Let's make it count."
        )

    def status(self) -> Dict[str, Any]:
        """Expose whether each agent is configured and currently running."""
        if not self.enabled:
            return {"enabled": False, "coach": "disabled", "reporter": "disabled", "planner": "disabled"}
        return {
            "enabled": True,
            "coach": {
                "configured": self._coach is not None,
                "running": bool(self._coach and self._coach._worker_thread and self._coach._worker_thread.is_alive()),
                "llm_configured": bool(self._coach and self._coach._ollama.configured),
                "ollama": self._coach._ollama.status() if self._coach else None,
                "text_source": self._coach._voice.last_text_provider if self._coach else "none",
                "audio_source": self._coach._voice.last_audio_provider if self._coach else "none",
                "audio_configured": bool(self._coach and (self._coach._voice._use_elevenlabs or self._coach._voice._pyttsx_engine)),
            },
            "reporter": {
                "configured": self._reporter is not None,
                "llm_configured": bool(self._reporter and self._reporter._ollama.configured),
                "ollama": self._reporter._ollama.status() if self._reporter else None,
            },
            "planner": {
                "configured": self._planner is not None,
                "ollama": self._planner._ollama.status() if self._planner else None,
                "llm_configured": bool(self._planner and self._planner._ollama.configured),
            },
        }

    def on_form_error(self, exercise: str, mistake: str, message: str) -> None:
        """Forward a form error event to Agent 1."""
        if not self.enabled or self._coach is None:
            return
        self._last_form_state[exercise] = mistake
        self._good_form_counter[exercise] = 0
        self._coach.on_form_error(exercise=exercise, mistake=mistake, message=message)

    def on_rep_completed(self, exercise: str, rep_count: int) -> None:
        """Forward a rep completion event to Agent 1."""
        if not self.enabled or self._coach is None:
            return
        prev = self._last_rep_counts.get(exercise, 0)
        if rep_count > prev:
            self._last_rep_counts[exercise] = rep_count
            self._coach.on_rep_completed(exercise=exercise, rep_count=rep_count)

    def on_good_form(self, exercise: str) -> None:
        """Forward a good-form event to Agent 1 (throttled internally)."""
        if not self.enabled or self._coach is None:
            return
        count = self._good_form_counter.get(exercise, 0) + 1
        self._good_form_counter[exercise] = count
        # Only fire every ~60 good-form frames to avoid over-triggering
        if count % 60 == 0:
            self._coach.on_good_form(exercise=exercise)

    def finish(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call when the workout ends. Triggers Agent 2 and Agent 3.
        Blocks briefly while generating report (runs in background thread for speed).

        Returns:
            {
                "report": { "session_id", "text", "structured" },
                "plan": { "text", "plan", "comparison", "plan_date" },
            }
        """
        if not self.enabled:
            return {"agents": self.status()}

        ended_at = datetime.now().isoformat()
        started_at = self._started_at or ended_at

        if self._coach is not None:
            self._coach.stop()
            self._coach.speak_direct(
                "Excellent work today, sir. Your session has concluded. "
                "I am now compiling your performance report and tomorrow's training plan."
            )

        result: Dict[str, Any] = {}
        result["agents"] = self.status()
        errors: list = []

        def run_agents():
            try:
                # Agent 2: generate session report
                if self._reporter:
                    report = self._reporter.generate_and_save(
                        session_data=session_data,
                        started_at=started_at,
                        ended_at=ended_at,
                    )
                    result["report"] = report

                    # Agent 3: compare progress and plan tomorrow
                    if self._planner:
                        plan = self._planner.analyze_and_plan(
                            session_id=report["session_id"],
                            current_structured=report["structured"],
                        )
                        result["plan"] = plan
            except Exception as e:
                errors.append(str(e))

        thread = threading.Thread(target=run_agents, daemon=False)
        thread.start()
        thread.join(timeout=60)  # Wait up to 60s for Ollama responses
        if thread.is_alive():
            errors.append("Ollama agents did not finish within 60 seconds; local results may be incomplete.")

        if errors:
            result["errors"] = errors

        return result
