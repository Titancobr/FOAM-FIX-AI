"""
Agent 2 — Session Report Agent
================================
Runs after a workout session ends.
- Takes the full workout scorer data from Agent 1's session.
- Uses Ollama to generate a rich, human-readable workout report.
- Saves the report and session data to the SQLite database.
- Produces structured JSON with: what went well, what needs improvement,
  muscle fatigue summary, and raw stats.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.db import init_db, save_session, save_agent_report
from agents.ollama_client import OllamaClient


REPORT_SYSTEM_PROMPT = """You are an elite AI personal trainer and sports scientist.
Your job is to analyze a completed workout session and generate a detailed but concise
performance report for the athlete.

Your report must be structured exactly as follows (use these exact section headers):

## 🏆 Overall Performance
[2-3 sentences on overall session quality, intensity, and consistency]

## ✅ What You Did Well
[Bullet points — specific, positive observations. Be precise about exercises and form.]

## ⚠️ Areas To Improve
[Bullet points — honest, actionable corrections. Prioritize the top 3 issues.]

## 💪 Muscle Groups Trained
[List which muscle groups were worked and estimated training volume quality]

## 📊 Key Stats
[Summarize: total reps, accuracy scores, notable exercise performances]

## 🎯 Focus For Next Session
[1-2 clear priorities they should focus on tomorrow]

Tone: professional, data-driven, encouraging but honest. Do not use excessive emojis beyond the headers.
"""


class SessionReportAgent:
    """
    Agent 2 — Post-workout report generator and database saver.

    Usage:
        agent = SessionReportAgent(gemini_api_key="...")
        report = agent.generate_and_save(
            session_data=scorer.build_report(),
            started_at="2024-01-01T10:00:00",
            ended_at="2024-01-01T10:45:00",
        )
        print(report["text"])        # human-readable report
        print(report["session_id"])  # DB id for chaining to Agent 3
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self._ollama = OllamaClient("OLLAMA_REPORT_MODEL", "qwen2.5:7b")
        init_db()

    def generate_and_save(
        self,
        session_data: Dict[str, Any],
        started_at: str,
        ended_at: str,
    ) -> Dict[str, Any]:
        """
        Generate a report for this session, save to DB, and return structured result.

        Returns:
            {
                "session_id": int,
                "text": str,          # full human-readable report
                "structured": dict,   # parsed highlights for Agent 3
            }
        """
        # 1. Save raw session to DB
        session_id = save_session(session_data, started_at, ended_at)

        # 2. Generate report text
        report_text = self._generate_report(session_data, started_at, ended_at)

        # 3. Save report to DB
        save_agent_report(session_id, "session_report", report_text)

        # 4. Build structured highlights for Agent 3
        structured = self._extract_structured(session_data)

        return {
            "session_id": session_id,
            "text": report_text,
            "structured": structured,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _generate_report(
        self,
        session_data: Dict[str, Any],
        started_at: str,
        ended_at: str,
    ) -> str:
        prompt = self._build_prompt(session_data, started_at, ended_at)

        response = self._ollama.complete(prompt, REPORT_SYSTEM_PROMPT, max_tokens=1500, timeout=30.0)
        if response:
            return response

        return self._template_report(session_data)

    def _build_prompt(
        self,
        session_data: Dict[str, Any],
        started_at: str,
        ended_at: str,
    ) -> str:
        breakdown = session_data.get("exercise_wise_breakdown", [])
        exercises_text = ""
        for ex in breakdown:
            exercises_text += (
                f"\n- {ex['exercise'].replace('_', ' ').title()}: "
                f"{ex['reps']} reps, {ex['accuracy']}% form accuracy, "
                f"top mistakes: {', '.join(ex.get('common_mistakes', [])) or 'none'}"
            )

        try:
            start_dt = datetime.fromisoformat(started_at)
            end_dt = datetime.fromisoformat(ended_at)
            duration_min = int((end_dt - start_dt).total_seconds() / 60)
        except Exception:
            duration_min = "unknown"

        return f"""Analyze this workout session and write a detailed performance report:

SESSION INFO:
- Date: {datetime.now().strftime('%B %d, %Y')}
- Duration: {duration_min} minutes
- Total reps: {session_data.get('total_reps', 0)}
- Overall form accuracy: {session_data.get('accuracy', 0)}%
- Most common mistakes: {', '.join(session_data.get('common_mistakes', [])) or 'none recorded'}

EXERCISE BREAKDOWN:{exercises_text}

Generate a comprehensive workout report following the format in your instructions."""

    def _template_report(self, session_data: Dict[str, Any]) -> str:
        """Fallback plain-text report when Ollama is unavailable."""
        breakdown = session_data.get("exercise_wise_breakdown", [])
        total_reps = session_data.get("total_reps", 0)
        accuracy = session_data.get("accuracy", 0)
        mistakes = session_data.get("common_mistakes", [])

        lines = [
            "## 🏆 Overall Performance",
            f"You completed a solid workout session with {total_reps} total reps "
            f"and an overall form accuracy of {accuracy}%.",
            "",
            "## ✅ What You Did Well",
        ]
        good = [ex for ex in breakdown if ex.get("accuracy", 0) >= 70]
        for ex in good:
            lines.append(f"- {ex['exercise'].replace('_', ' ').title()}: {ex['reps']} reps at {ex['accuracy']}% accuracy")

        lines += ["", "## ⚠️ Areas To Improve"]
        if mistakes:
            for m in mistakes[:3]:
                lines.append(f"- {m.replace('_', ' ').title()}")
        else:
            lines.append("- No major issues recorded — keep it up!")

        lines += ["", "## 📊 Key Stats"]
        for ex in breakdown:
            lines.append(
                f"- {ex['exercise'].replace('_', ' ').title()}: "
                f"{ex['reps']} reps, {ex['accuracy']}% accuracy"
            )

        lines += [
            "",
            "## 🎯 Focus For Next Session",
            "- Continue working on consistency of form across all exercises.",
        ]
        return "\n".join(lines)

    def _extract_structured(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data for Agent 3 (progress comparison)."""
        breakdown = session_data.get("exercise_wise_breakdown", [])
        weak = [ex for ex in breakdown if ex.get("accuracy", 0) < 65]
        strong = [ex for ex in breakdown if ex.get("accuracy", 0) >= 80]

        return {
            "total_reps": session_data.get("total_reps", 0),
            "overall_accuracy": session_data.get("accuracy", 0),
            "exercises": {
                ex["exercise"]: {
                    "reps": ex.get("reps", 0),
                    "accuracy": ex.get("accuracy", 0),
                    "mistakes": ex.get("common_mistakes", []),
                }
                for ex in breakdown
            },
            "weak_exercises": [ex["exercise"] for ex in weak],
            "strong_exercises": [ex["exercise"] for ex in strong],
            "top_mistakes": session_data.get("common_mistakes", []),
        }
