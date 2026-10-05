import json
import os
from typing import Any
from urllib import error, request


class LLMCoach:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
        self.realtime_model = os.getenv("LLM_REALTIME_MODEL", os.getenv("LLM_MODEL", "qwen2.5:3b"))
        self.report_model = os.getenv("LLM_REPORT_MODEL", os.getenv("LLM_MODEL", "qwen2.5:7b"))
        self.vision_model = os.getenv("LLM_VISION_MODEL", "llava:7b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._openai_client = None
        self.last_completion_provider: str | None = None
        self.last_completion_error: str | None = None
        self.last_report_source = "local_fallback"

        if self.provider in {"openai", "auto"} and self.api_key:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI(api_key=self.api_key)
            except Exception:
                self._openai_client = None

        self.enabled = self.provider in {"ollama", "openai", "auto"}

    def status(self) -> dict[str, Any]:
        """Return observable provider/report status without making an LLM request."""
        return {
            "configured_provider": self.provider,
            "enabled": self.enabled,
            "last_completion_provider": self.last_completion_provider,
            "last_completion_error": self.last_completion_error,
            "report_source": self.last_report_source,
            "openai_configured": bool(self.api_key and self._openai_client),
            "ollama_host": self.ollama_host,
        }

    def realtime_correction(
        self,
        *,
        exercise_name: str,
        mistake_code: str,
        severity: int,
        reps: int,
        stage: str,
        tracked_angle: float,
        local_message: str,
    ) -> str:
        fallback = local_message
        if not self.enabled:
            return fallback

        prompt = (
            "You are a calm gym instructor giving one short live correction. "
            "Return one sentence under 18 words. "
            "If the issue is mild, encourage first. "
            "If severe, correct clearly but kindly. "
            "Do not mention AI, confidence, or numbers unless needed.\n\n"
            f"Exercise: {exercise_name}\n"
            f"Mistake code: {mistake_code}\n"
            f"Severity: {severity}\n"
            f"Rep count: {reps}\n"
            f"Stage: {stage}\n"
            f"Tracked angle: {tracked_angle:.1f}\n"
            f"Local fallback cue: {local_message}"
        )
        return self._complete_text(prompt, max_tokens=40, model=self.realtime_model) or fallback

    def exercise_report(
        self,
        *,
        exercise_name: str,
        reps: int,
        good_frame_ratio: float,
        top_mistakes: list[tuple[str, int]],
        perfect_reps: int = 0,
        corrected_reps: int = 0,
        poor_reps: int = 0,
        average_rep_quality: int = 0,
        consistency_score: int = 0,
        rep_reports: list[dict[str, Any]] | None = None,
        previous_report: dict[str, Any] | None = None,
        previous_mistakes: list[str] | None = None,
        mistakes_fixed: list[str] | None = None,
        mistakes_repeated: list[str] | None = None,
        new_mistakes: list[str] | None = None,
    ) -> dict[str, Any]:
        fallback = self._fallback_report(
            exercise_name=exercise_name,
            reps=reps,
            good_frame_ratio=good_frame_ratio,
            top_mistakes=top_mistakes,
            average_rep_quality=average_rep_quality,
            previous_report=previous_report,
            previous_mistakes=previous_mistakes or [],
            mistakes_fixed=mistakes_fixed or [],
            mistakes_repeated=mistakes_repeated or [],
            new_mistakes=new_mistakes or [],
        )
        self.last_report_source = "local_fallback"
        if not self.enabled:
            return fallback

        rep_reports = rep_reports or []
        weakest_reps = [
            {
                "rep_number": rep.get("rep_number"),
                "quality_score": rep.get("quality_score"),
                "main_issue": rep.get("main_issue") or "none",
                "verdict": rep.get("verdict"),
            }
            for rep in sorted(rep_reports, key=lambda item: item.get("quality_score", 100))[:3]
        ]

        previous_report_text = previous_report or {
            "summary": "No previous report available."
        }

        prompt = (
            "You are a supportive gym coach writing a short exercise review in JSON. "
            "Return valid JSON with keys: summary, what_went_well, improve_next, coach_tip, progress_since_last, still_to_improve. "
            "Each value must be a short sentence. "
            "Keep it practical, specific, and human. "
            "Base the review on rep quality first, then frame quality. "
            "When a previous report is available, explicitly compare current performance to the previous session and mention what improved and what still needs work.\n\n"
            f"Exercise: {exercise_name}\n"
            f"Reps: {reps}\n"
            f"Good frame ratio: {good_frame_ratio:.2f}\n"
            f"Average rep quality: {average_rep_quality}\n"
            f"Consistency score: {consistency_score}\n"
            f"Perfect reps: {perfect_reps}\n"
            f"Corrected reps: {corrected_reps}\n"
            f"Poor reps: {poor_reps}\n"
            f"Top mistakes: {top_mistakes}\n"
            f"Previous mistakes: {previous_mistakes or []}\n"
            f"Mistakes fixed since last time: {mistakes_fixed or []}\n"
            f"Mistakes repeated this time: {mistakes_repeated or []}\n"
            f"New mistakes this time: {new_mistakes or []}\n"
            f"Weakest reps: {weakest_reps}\n"
            f"Previous report context: {previous_report_text}"
        )

        text = self._complete_text(prompt, max_tokens=220, model=self.report_model)
        if not text:
            return fallback

        try:
            parsed = json.loads(text)
            if all(key in parsed for key in ("summary", "what_went_well", "improve_next", "coach_tip")):
                parsed.setdefault("progress_since_last", fallback.get("progress_since_last", "This is your first saved report for this exercise."))
                parsed.setdefault("still_to_improve", fallback.get("still_to_improve", fallback["improve_next"]))
                self.last_report_source = "llm"
                return parsed
        except Exception:
            pass
        return fallback

    def voice_reply(self, message: str, context: str = "") -> str:
        """Generate a short Jarvis-style spoken response for the web voice assistant."""
        fallback = "At your service, Sir. I am ready to help with your training."
        clean_message = message.strip()
        if not clean_message or not self.enabled:
            return fallback

        prompt = (
            "You are Jarvis, a helpful and slightly sarcastic British AI butler for a fitness app. "
            "Reply in plain text only, suitable for speech. Keep it to one or two short sentences. "
            "Call the user Sir when natural. Never use markdown, JSON, emojis, or mention internal systems. "
            "Give practical fitness-app help and do not claim an action was completed unless the app already did it.\n\n"
            f"Current app context: {context or 'fitness training app'}\n"
            f"User says: {clean_message}"
        )
        response = self._complete_text(
            prompt,
            max_tokens=100,
            model=self.realtime_model,
            timeout_seconds=20.0,
        )
        return response or fallback

    def workout_briefing(
        self,
        *,
        plan_name: str,
        day_name: str,
        focus: str,
        exercises: list[dict[str, Any]],
    ) -> str:
        """Give a spoken, actionable briefing for the selected workout day."""
        exercise_lines = "\n".join(
            f"{index}. {item.get('name')} — {item.get('sets')} sets of {item.get('reps')}; focus: {item.get('muscle')}"
            for index, item in enumerate(exercises, start=1)
        )
        fallback = (
            f"Good day, Sir. Today is {day_name}, focused on {focus}. "
            f"Complete {len(exercises)} exercises in order, use controlled form, and stop if you feel sharp pain."
        )
        if not self.enabled:
            return fallback

        prompt = (
            "You are Jarvis, a supportive and slightly sarcastic British AI butler coaching a gym workout. "
            "Create a spoken workout briefing in plain text only. Mention the workout name and every exercise in order. "
            "Include sets and reps, then give three short things to keep in mind for form and safety. "
            "End with one short interactive question asking whether the user is ready for the first exercise. "
            "Keep it under 150 words. Do not use markdown, JSON, emojis, or headings. Call the user Sir naturally.\n\n"
            f"Plan: {plan_name}\nDay: {day_name}\nFocus: {focus}\nExercises:\n{exercise_lines}"
        )
        response = self._complete_text(
            prompt,
            max_tokens=220,
            model=self.report_model,
            timeout_seconds=25.0,
        )
        return response or fallback

    def meal_estimate(
        self,
        *,
        prompt_context: str,
        image_base64: str | None = None,
    ) -> dict[str, Any]:
        fallback = {
            "title": "Estimated meal",
            "description": "Estimated from the uploaded meal.",
            "calories": 450,
            "protein": 25,
            "carbs": 45,
            "fat": 15,
            "confidence": 0.55,
            "portion_basis": "single serving estimate",
            "recognized_items": ["mixed meal"],
        }
        if not self.enabled:
            return fallback

        prompt = (
            "You are a careful nutrition assistant. Estimate calories and macros for the meal. "
            "Use the image first, then the prompt context. If the meal appears homemade, estimate portion size visually. "
            "If it appears packaged and label details are provided, trust those details over appearance. "
            "Return valid JSON with keys: title, description, calories, protein, carbs, fat, confidence, portion_basis, recognized_items. "
            "Use integers for calories and macros. Use confidence as a 0 to 1 decimal. "
            "recognized_items must be a short JSON array of food components. "
            "Keep the description short and practical.\n\n"
            f"{prompt_context}"
        )

        text = self._complete_text(
            prompt,
            max_tokens=180,
            model=self.vision_model if image_base64 else self.report_model,
            image_base64=image_base64,
        )
        if not text:
            return fallback

        try:
            parsed = json.loads(text)
            if all(
                key in parsed
                for key in ("title", "description", "calories", "protein", "carbs", "fat")
            ):
                recognized_items = parsed.get("recognized_items", ["mixed meal"])
                if isinstance(recognized_items, str):
                    recognized_items = [recognized_items]
                return {
                    "title": str(parsed["title"]),
                    "description": str(parsed["description"]),
                    "calories": int(float(parsed["calories"])),
                    "protein": int(float(parsed["protein"])),
                    "carbs": int(float(parsed["carbs"])),
                    "fat": int(float(parsed["fat"])),
                    "confidence": max(0.0, min(1.0, float(parsed.get("confidence", 0.7)))),
                    "portion_basis": str(parsed.get("portion_basis", "single serving estimate")),
                    "recognized_items": [str(item) for item in recognized_items[:6]],
                }
        except Exception:
            pass
        return fallback

    def _complete_text(
        self,
        prompt: str,
        *,
        max_tokens: int,
        model: str,
        image_base64: str | None = None,
        timeout_seconds: float = 1.2,
    ) -> str:
        self.last_completion_provider = None
        self.last_completion_error = None
        if not self.enabled:
            self.last_completion_error = "LLM provider is disabled (LLM_PROVIDER=local)."
            return ""

        providers = self._provider_order()
        for provider in providers:
            if provider == "ollama":
                text = self._ollama_complete(
                    prompt,
                    max_tokens=max_tokens,
                    model=model,
                    image_base64=image_base64,
                    timeout_seconds=timeout_seconds,
                )
            elif provider == "openai":
                text = self._openai_complete(prompt, max_tokens=max_tokens)
            else:
                text = ""
            if text:
                self.last_completion_provider = provider
                return text.strip()
        self.last_completion_error = "No configured LLM provider returned a response."
        return ""

    def _provider_order(self) -> list[str]:
        if self.provider == "auto":
            order = ["ollama"]
            if self._openai_client:
                order.append("openai")
            return order
        return [self.provider]

    def _ollama_complete(
        self,
        prompt: str,
        *,
        max_tokens: int,
        model: str,
        image_base64: str | None = None,
        timeout_seconds: float = 1.2,
    ) -> str:
        body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.2,
            },
        }
        if image_base64:
            body["images"] = [image_base64]
        payload = json.dumps(body).encode("utf-8")
        req = request.Request(
            f"{self.ollama_host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return (body.get("response") or "").strip()
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ""

    def _openai_complete(self, prompt: str, *, max_tokens: int) -> str:
        if not self._openai_client:
            return ""
        try:
            response = self._openai_client.responses.create(
                model=self.openai_model,
                input=prompt,
                max_output_tokens=max_tokens,
            )
            return (response.output_text or "").strip()
        except Exception:
            return ""

    def _fallback_report(
        self,
        *,
        exercise_name: str,
        reps: int,
        good_frame_ratio: float,
        top_mistakes: list[tuple[str, int]],
        average_rep_quality: int = 0,
        previous_report: dict[str, Any] | None = None,
        previous_mistakes: list[str] | None = None,
        mistakes_fixed: list[str] | None = None,
        mistakes_repeated: list[str] | None = None,
        new_mistakes: list[str] | None = None,
    ) -> dict[str, Any]:
        pretty_name = exercise_name.replace("_", " ").title()
        top_issue = top_mistakes[0][0].replace("_", " ") if top_mistakes else "small form adjustments"
        percent = average_rep_quality or round(good_frame_ratio * 100)
        progress_since_last = "This is your first saved report for this exercise."
        still_to_improve = f"Keep working on {top_issue} in the next set."
        if previous_report:
            previous_quality = int(previous_report.get("average_rep_quality") or previous_report.get("accuracy") or 0)
            delta = percent - previous_quality
            if delta > 4:
                progress_since_last = f"You improved by about {delta} points compared with your previous {pretty_name} session."
            elif delta < -4:
                progress_since_last = f"This session was about {abs(delta)} points below your previous {pretty_name} report, so tighten your form next time."
            else:
                progress_since_last = f"This session was close to your previous {pretty_name} report, with only a small change in quality."
            previous_mistakes = previous_mistakes or previous_report.get("common_mistakes") or []
            repeated = mistakes_repeated or [issue for issue in (top_mistakes and [item[0] for item in top_mistakes] or []) if issue in previous_mistakes]
            fixed = mistakes_fixed or []
            if repeated:
                still_to_improve = f"{top_issue} is still carrying over from the previous session, so make that the main focus next time."
            elif fixed:
                still_to_improve = f"You corrected {fixed[0].replace('_', ' ')}; keep that fix while working on {top_issue}."
        if previous_report and not (mistakes_fixed or mistakes_repeated or new_mistakes):
            progress_since_last += " Compare the mistake list above with today’s cues for the clearest next step."
        return {
            "summary": f"You completed {reps} reps of {pretty_name} with about {percent}% solid form.",
            "what_went_well": "Your control looked better once you settled into a consistent rhythm.",
            "improve_next": f"Focus most on {top_issue} during the next set.",
            "coach_tip": "Use a smooth tempo and pause briefly in the strongest part of each rep.",
            "progress_since_last": progress_since_last,
            "still_to_improve": still_to_improve,
        }
