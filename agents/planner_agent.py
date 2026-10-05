"""
Agent 3 — Progress Tracker & Next-Day Workout Planner
=======================================================
Runs after Agent 2 generates the session report.
- Compares today's session against all previous sessions from the DB.
- Identifies: corrections made since last time, regressions, new PRs.
- Uses training science principles (progressive overload, volume, recovery)
  to generate tomorrow's workout plan.
- Saves the plan to the DB and returns it for display.

Progressive overload logic:
  - Accuracy >= 85% AND reps >= last session → increase volume by ~10%
  - Accuracy 65-84% → maintain same volume, focus on form
  - Accuracy < 65% → reduce volume 10%, emphasize technique work
  - Exercises not done today → deload or skip based on frequency
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from agents.db import (
    get_exercise_history,
    get_last_n_sessions,
    get_session_exercises,
    init_db,
    save_agent_report,
    save_next_day_plan,
)
from agents.ollama_client import OllamaClient


PLANNER_SYSTEM_PROMPT = """You are an elite AI strength and conditioning coach with expertise in:
- Progressive overload and periodization
- Recovery science and workout volume management
- Exercise selection based on performance data
- Injury prevention

Your job: analyze an athlete's workout history and generate their next-day training plan.

Your response MUST follow this exact format:

## 📈 Progress Since Last Session
[Compare today vs previous session. Call out what improved, what regressed, what was corrected.]

## 🔄 What You Fixed
[Specific form mistakes that were improved since last time — celebrate these wins]

## ⚠️ Still Needs Work
[Issues that persisted or appeared for the first time today]

## 💡 Tomorrow's Workout Plan
[Structured plan with: Exercise | Sets × Reps | Notes]
Format each exercise as:
**[Exercise Name]** — [X sets × Y reps] — [brief coaching note]

## 🧠 Volume & Intensity Rationale
[2-3 sentences explaining WHY you chose this volume based on today's performance]

## 🌙 Recovery Tips For Tonight
[2-3 practical sleep, nutrition, or mobility tips]

Base all decisions on:
1. Accuracy score (form quality): >85% = increase, 65-85% = maintain, <65% = reduce
2. Rep count vs previous session: compare and adjust
3. Muscle group balance: ensure adequate rest between same-group training
4. Progressive overload: ~10% volume increase when warranted
"""

# Muscle group → exercises mapping for workout planning
MUSCLE_GROUP_MAP = {
    "chest": ["barbell_bench_press", "flat_bench_press", "incline_bench_press",
              "decline_bench_press", "cable_fly", "push_up", "dips"],
    "back": ["barbell_row", "lat_pulldown", "pull_up"],
    "shoulders": ["overhead_press", "military_press", "lateral_raise"],
    "biceps": ["barbell_curl", "bicep_curl", "hammer_curl"],
    "triceps": ["tricep_pushdown", "dips"],
    "legs": ["squat", "barbell_squat", "deadlift", "romanian_deadlift",
             "hip_thrust", "leg_extension", "leg_raises"],
    "core": ["plank", "leg_raises", "russian_twist"],
}

# Default starting targets (reps × sets) per exercise
DEFAULT_TARGETS = {
    "squat": (3, 12), "barbell_squat": (4, 8), "deadlift": (3, 6),
    "romanian_deadlift": (3, 10), "hip_thrust": (3, 12),
    "barbell_bench_press": (4, 8), "flat_bench_press": (4, 8),
    "incline_bench_press": (3, 10), "decline_bench_press": (3, 10),
    "push_up": (3, 15), "dips": (3, 10),
    "barbell_row": (4, 8), "lat_pulldown": (3, 10), "pull_up": (3, 8),
    "barbell_curl": (3, 10), "bicep_curl": (3, 12), "hammer_curl": (3, 12),
    "overhead_press": (4, 8), "military_press": (3, 10), "lateral_raise": (3, 15),
    "cable_fly": (3, 12), "tricep_pushdown": (3, 12),
    "plank": (3, 1), "leg_raises": (3, 15), "russian_twist": (3, 20),
    "leg_extension": (3, 12),
}


class ProgressPlannerAgent:
    """
    Agent 3 — Compares progress and plans tomorrow's workout.

    Usage:
        agent = ProgressPlannerAgent(gemini_api_key="...")
        result = agent.analyze_and_plan(
            session_id=42,
            current_structured=session_report["structured"],
        )
        print(result["text"])   # full plan text
        print(result["plan"])   # JSON plan for display
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self._ollama = OllamaClient("OLLAMA_PLANNER_MODEL", "qwen2.5:7b")
        init_db()

    def analyze_and_plan(
        self,
        session_id: int,
        current_structured: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compare today's session against history and generate tomorrow's plan.

        Returns:
            {
                "text": str,           # full markdown plan
                "plan": list[dict],    # structured exercise list
                "comparison": dict,    # what improved / regressed
                "plan_date": str,      # date the plan is for
            }
        """
        # 1. Load historical data
        history = self._load_history(current_structured)

        # 2. Compute comparison
        comparison = self._compute_comparison(current_structured, history)

        # 3. Compute progressive overload targets
        plan_exercises = self._compute_next_day_plan(current_structured, history)

        # 4. Generate AI narrative
        plan_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        plan_text = self._generate_plan_text(current_structured, history, comparison, plan_exercises, plan_date)

        # 5. Save to DB
        save_agent_report(session_id, "progress_comparison", plan_text)
        save_next_day_plan(session_id, plan_date, {"exercises": plan_exercises, "date": plan_date})

        return {
            "text": plan_text,
            "plan": plan_exercises,
            "comparison": comparison,
            "plan_date": plan_date,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_history(self, current: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Load previous session data for each exercise done today."""
        history = {}
        for exercise in current.get("exercises", {}).keys():
            past = get_exercise_history(exercise, limit=5)
            history[exercise] = past
        return history

    def _compute_comparison(
        self,
        current: Dict[str, Any],
        history: Dict[str, List[Dict]],
    ) -> Dict[str, Any]:
        """Identify improvements, regressions, and corrections vs last session."""
        improved = []
        regressed = []
        corrected_mistakes = []
        new_mistakes = []

        for exercise, stats in current.get("exercises", {}).items():
            past = history.get(exercise, [])
            if not past:
                continue

            last = past[0]  # Most recent previous session
            last_accuracy = last.get("accuracy", 0)
            last_mistakes = set(last.get("mistakes", []))
            curr_accuracy = stats.get("accuracy", 0)
            curr_mistakes = set(stats.get("mistakes", []))

            acc_delta = curr_accuracy - last_accuracy

            if acc_delta >= 5:
                improved.append({
                    "exercise": exercise,
                    "accuracy_delta": acc_delta,
                    "previous": last_accuracy,
                    "current": curr_accuracy,
                })
            elif acc_delta <= -5:
                regressed.append({
                    "exercise": exercise,
                    "accuracy_delta": acc_delta,
                    "previous": last_accuracy,
                    "current": curr_accuracy,
                })

            # Mistakes that existed before but are gone now
            fixed = last_mistakes - curr_mistakes
            for m in fixed:
                corrected_mistakes.append({"exercise": exercise, "mistake": m})

            # New mistakes that weren't there before
            appeared = curr_mistakes - last_mistakes
            for m in appeared:
                new_mistakes.append({"exercise": exercise, "mistake": m})

        return {
            "improved": improved,
            "regressed": regressed,
            "corrected_mistakes": corrected_mistakes,
            "new_mistakes": new_mistakes,
        }

    def _compute_next_day_plan(
        self,
        current: Dict[str, Any],
        history: Dict[str, List[Dict]],
    ) -> List[Dict]:
        """
        Apply progressive overload science to determine tomorrow's targets.
        Returns a list of exercise dicts with sets, reps, and notes.
        """
        plan = []

        for exercise, stats in current.get("exercises", {}).items():
            accuracy = stats.get("accuracy", 0)
            reps_today = stats.get("reps", 0)
            past = history.get(exercise, [])

            default_sets, default_reps = DEFAULT_TARGETS.get(exercise, (3, 10))
            last_reps = past[0].get("reps", reps_today) if past else reps_today

            # Progressive overload decision
            if accuracy >= 85 and reps_today >= last_reps:
                # Increase: add ~10% reps (round up)
                target_reps = max(reps_today + 1, int(reps_today * 1.10))
                target_sets = default_sets
                note = "Great form — increase volume. Push to new PR!"
                intensity = "increase"
            elif accuracy >= 65:
                # Maintain
                target_reps = reps_today if reps_today > 0 else default_reps
                target_sets = default_sets
                note = "Solid session — maintain volume, sharpen technique."
                intensity = "maintain"
            else:
                # Reduce and focus on form
                target_reps = max(int(reps_today * 0.90), 5)
                target_sets = max(default_sets - 1, 2)
                note = "Focus on form — reduce load and perfect your technique first."
                intensity = "reduce"

            plan.append({
                "exercise": exercise,
                "display_name": exercise.replace("_", " ").title(),
                "sets": target_sets,
                "reps": target_reps,
                "intensity": intensity,
                "note": note,
                "today_accuracy": accuracy,
                "today_reps": reps_today,
            })

        # Sort: weak exercises first (they need more attention)
        plan.sort(key=lambda x: x["today_accuracy"])
        return plan

    def _generate_plan_text(
        self,
        current: Dict[str, Any],
        history: Dict[str, List[Dict]],
        comparison: Dict[str, Any],
        plan: List[Dict],
        plan_date: str,
    ) -> str:
        prompt = self._build_planner_prompt(current, history, comparison, plan, plan_date)
        response = self._ollama.complete(prompt, PLANNER_SYSTEM_PROMPT, max_tokens=2000, timeout=30.0)
        if response:
            return response

        return self._template_plan(current, comparison, plan, plan_date)

    def _build_planner_prompt(
        self,
        current: Dict[str, Any],
        history: Dict[str, List[Dict]],
        comparison: Dict[str, Any],
        plan: List[Dict],
        plan_date: str,
    ) -> str:
        # Today's summary
        ex_lines = []
        for ex in current.get("exercises", {}).values():
            pass  # Already in current dict

        exercises_text = ""
        for exercise, stats in current.get("exercises", {}).items():
            past = history.get(exercise, [])
            prev_acc = past[0].get("accuracy", "N/A") if past else "first time"
            exercises_text += (
                f"\n  • {exercise.replace('_', ' ').title()}: "
                f"{stats['reps']} reps, {stats['accuracy']}% accuracy "
                f"(prev: {prev_acc}% accuracy)"
            )

        # Comparison
        improved_text = ", ".join(
            f"{i['exercise'].replace('_', ' ').title()} (+{i['accuracy_delta']:.0f}%)"
            for i in comparison.get("improved", [])
        ) or "none"
        regressed_text = ", ".join(
            f"{r['exercise'].replace('_', ' ').title()} ({r['accuracy_delta']:.0f}%)"
            for r in comparison.get("regressed", [])
        ) or "none"
        corrected_text = ", ".join(
            f"{c['exercise'].replace('_', ' ').title()} — {c['mistake']}"
            for c in comparison.get("corrected_mistakes", [])
        ) or "none"

        # Tomorrow's plan
        plan_text = ""
        for ex in plan:
            plan_text += (
                f"\n  • {ex['display_name']}: {ex['sets']} sets × {ex['reps']} reps "
                f"[{ex['intensity'].upper()}] — {ex['note']}"
            )

        return f"""Analyze this athlete's workout data and generate their {plan_date} training plan.

TODAY'S SESSION:
- Overall accuracy: {current.get('overall_accuracy', 0)}%
- Total reps: {current.get('total_reps', 0)}
- Exercises:{exercises_text}

PROGRESS VS LAST SESSION:
- Improved: {improved_text}
- Regressed: {regressed_text}
- Form mistakes corrected: {corrected_text}
- New mistakes today: {', '.join(m['mistake'] for m in comparison.get('new_mistakes', [])) or 'none'}

COMPUTED NEXT-DAY PLAN (based on progressive overload science):
{plan_text}

Please write the full training plan narrative following your system instructions.
Use the computed plan as the basis but you may adjust if scientifically warranted."""

    def _template_plan(
        self,
        current: Dict[str, Any],
        comparison: Dict[str, Any],
        plan: List[Dict],
        plan_date: str,
    ) -> str:
        """Fallback plan when Ollama is unavailable."""
        lines = [
            f"# Tomorrow's Workout Plan — {plan_date}",
            "",
            "## 📈 Progress Since Last Session",
        ]

        improved = comparison.get("improved", [])
        regressed = comparison.get("regressed", [])
        if improved:
            lines.append(f"Improved: {', '.join(i['exercise'].replace('_', ' ').title() for i in improved)}")
        if regressed:
            lines.append(f"Needs more work: {', '.join(r['exercise'].replace('_', ' ').title() for r in regressed)}")
        if not improved and not regressed:
            lines.append("First session — baseline established.")

        corrected = comparison.get("corrected_mistakes", [])
        lines += ["", "## 🔄 What You Fixed"]
        if corrected:
            for c in corrected:
                lines.append(f"- ✅ {c['exercise'].replace('_', ' ').title()}: {c['mistake']} corrected!")
        else:
            lines.append("- Keep working on consistency — corrections take time.")

        lines += ["", "## 💡 Tomorrow's Workout Plan"]
        for ex in plan:
            indicator = "🔺" if ex["intensity"] == "increase" else ("🔻" if ex["intensity"] == "reduce" else "➡️")
            lines.append(
                f"**{ex['display_name']}** — {ex['sets']} sets × {ex['reps']} reps {indicator} — {ex['note']}"
            )

        lines += [
            "",
            "## 🌙 Recovery Tips For Tonight",
            "- Aim for 7-9 hours of sleep for optimal muscle protein synthesis.",
            "- Consume adequate protein (0.8-1g per lb bodyweight) to support recovery.",
            "- 5-10 minutes of light stretching to reduce next-day soreness.",
        ]

        return "\n".join(lines)
