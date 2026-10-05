"""
Agent 1 — Live Coaching Agent (Jarvis Voice)
============================================
Runs in real time during a workout session.
- Listens to posture events and rep milestones emitted by the main loop.
- Uses Ollama to generate contextual, motivating Jarvis-style coaching lines.
- Speaks via ElevenLabs (Jarvis-like voice) with pyttsx3 as fallback.
- Runs the Ollama call in a background thread so it never blocks the CV loop.
"""

import queue
import threading
import time
from typing import Any, Dict, List, Optional

from agents.ollama_client import OllamaClient

ELEVENLABS_AVAILABLE = False
try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    pass

PYTTSX_AVAILABLE = False
try:
    import pyttsx3
    PYTTSX_AVAILABLE = True
except ImportError:
    pyttsx3 = None

# ---------------------------------------------------------------------------
# Jarvis system prompt — defines the AI personality
# ---------------------------------------------------------------------------
JARVIS_SYSTEM_PROMPT = """You are JARVIS, the AI personal trainer from Iron Man.
You are assisting the user during their workout in real time.
Your personality:
- Intelligent, calm, and precise — like a highly competent British AI butler
- Encouraging but not sycophantic — you give real, useful feedback
- Occasionally witty and dry-humored
- You address the user respectfully, never using casual slang
- You keep responses SHORT — max 2 sentences. This is real-time voice coaching.

Your job:
- When the user makes a form error, explain it clearly and give ONE correction cue
- When the user completes reps, encourage them with energy-appropriate enthusiasm
- When the user does great, acknowledge it briefly and push them further

Always speak in first person as JARVIS. Never break character.
Keep responses under 25 words for real-time delivery."""


class JarvisVoice:
    """Text-to-speech with ElevenLabs Jarvis voice, falling back to pyttsx3."""

    # Best publicly available ElevenLabs voice that resembles Jarvis
    # You can replace this with your own cloned voice ID from ElevenLabs
    JARVIS_VOICE_ID = "ErXwobaYiN019PkySvjV"  # "Antoni" — deep, calm, British-ish

    def __init__(self, api_key: Optional[str] = None, use_elevenlabs: bool = True):
        self._lock = threading.Lock()
        self._el_client = None
        self._pyttsx_engine = None
        self.last_audio_provider = "none"
        self.last_text_provider = "none"
        self._use_elevenlabs = use_elevenlabs and ELEVENLABS_AVAILABLE and api_key

        if self._use_elevenlabs:
            try:
                self._el_client = ElevenLabs(api_key=api_key)
            except Exception:
                self._use_elevenlabs = False

        # Always init pyttsx3 as fallback
        try:
            if not PYTTSX_AVAILABLE:
                raise RuntimeError("pyttsx3 is not installed")
            self._pyttsx_engine = pyttsx3.init()
            # Make pyttsx3 sound more like Jarvis — slower, lower pitch
            self._pyttsx_engine.setProperty("rate", 165)
            voices = self._pyttsx_engine.getProperty("voices")
            # Prefer a male voice
            for v in voices:
                if "male" in v.name.lower() or "daniel" in v.name.lower() or "alex" in v.name.lower():
                    self._pyttsx_engine.setProperty("voice", v.id)
                    break
        except Exception:
            self._pyttsx_engine = None

    def speak(self, text: str) -> None:
        """Speak text — non-blocking, runs in current thread."""
        with self._lock:
            if self._use_elevenlabs and self._el_client:
                try:
                    import io
                    import subprocess
                    audio = self._el_client.text_to_speech.convert(
                        voice_id=self.JARVIS_VOICE_ID,
                        text=text,
                        model_id="eleven_turbo_v2",
                        voice_settings=VoiceSettings(
                            stability=0.72,
                            similarity_boost=0.85,
                            style=0.12,
                            use_speaker_boost=True,
                        ),
                    )
                    audio_bytes = b"".join(audio)
                    # Play via afplay on macOS
                    proc = subprocess.Popen(
                        ["afplay", "-"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    proc.stdin.write(audio_bytes)
                    proc.stdin.close()
                    proc.wait()
                    self.last_audio_provider = "elevenlabs"
                    return
                except Exception:
                    pass  # Fall through to pyttsx3

            if self._pyttsx_engine:
                try:
                    self._pyttsx_engine.say(text)
                    self._pyttsx_engine.runAndWait()
                    self.last_audio_provider = "pyttsx3"
                except Exception:
                    pass


class LiveCoachAgent:
    """
    Agent 1 — Real-time Jarvis coaching.

    Usage:
        agent = LiveCoachAgent(gemini_api_key="...", elevenlabs_api_key="...")
        agent.start()

        # During the workout loop:
        agent.on_form_error(exercise="squat", mistake="knee_instability",
                            message="Keep both knees tracking evenly")
        agent.on_rep_completed(exercise="squat", rep_count=8)
        agent.on_good_form(exercise="squat")

        agent.stop()
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        use_elevenlabs: bool = True,
        cooldown_seconds: float = 4.0,
    ):
        self._voice = JarvisVoice(api_key=elevenlabs_api_key, use_elevenlabs=use_elevenlabs)
        self._cooldown = cooldown_seconds
        self._last_spoken_at = 0.0
        self._last_mistake: Optional[str] = None
        self._event_queue: queue.Queue = queue.Queue(maxsize=20)
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._session_context: List[str] = []  # running transcript for Ollama context
        self._ollama = OllamaClient("OLLAMA_LIVE_MODEL", "qwen2.5:3b")

    def start(self) -> None:
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=3)

    # ------------------------------------------------------------------
    # Public event methods (called from the main CV loop)
    # ------------------------------------------------------------------

    def on_form_error(self, exercise: str, mistake: str, message: str) -> None:
        """Called when PostureAnalyzer detects a form issue."""
        # Deduplicate same mistake within cooldown
        now = time.time()
        if mistake == self._last_mistake and now - self._last_spoken_at < self._cooldown:
            return
        self._last_mistake = mistake
        self._enqueue({
            "type": "form_error",
            "exercise": exercise,
            "mistake": mistake,
            "message": message,
        })

    def on_rep_completed(self, exercise: str, rep_count: int) -> None:
        """Called when RepCounter increments."""
        # Speak at milestones: every 5 reps, and at 1
        if rep_count == 1 or rep_count % 5 == 0:
            self._enqueue({
                "type": "rep_milestone",
                "exercise": exercise,
                "reps": rep_count,
            })

    def on_good_form(self, exercise: str) -> None:
        """Called occasionally when form is consistently good."""
        now = time.time()
        if now - self._last_spoken_at < self._cooldown * 2:
            return
        self._enqueue({"type": "good_form", "exercise": exercise})

    def speak_direct(self, text: str) -> None:
        """Bypass queue and speak immediately (for start/end messages)."""
        threading.Thread(target=self._voice.speak, args=(text,), daemon=True).start()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _enqueue(self, event: Dict[str, Any]) -> None:
        try:
            self._event_queue.put_nowait(event)
        except queue.Full:
            pass  # Drop if queue is full — real-time system must not block

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                event = self._event_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            now = time.time()
            if now - self._last_spoken_at < self._cooldown:
                continue  # Skip if still in cooldown

            text = self._generate_speech(event)
            if text:
                self._last_spoken_at = time.time()
                self._voice.speak(text)
                self._session_context.append(f"[{event['type']}] {text}")
                # Keep context window manageable
                if len(self._session_context) > 20:
                    self._session_context = self._session_context[-20:]

    def _generate_speech(self, event: Dict[str, Any]) -> str:
        """Generate Jarvis-style speech using Ollama, or fall back to templates."""
        response = self._ollama.complete(
            self._build_gemini_prompt(event), JARVIS_SYSTEM_PROMPT,
            max_tokens=60, timeout=3.0,
        )
        if response:
            self._ollama.last_error = None
            self._voice.last_text_provider = "ollama"
            return response
        self._voice.last_text_provider = "local_template"
        return self._template_response(event)

    def _build_gemini_prompt(self, event: Dict[str, Any]) -> str:
        context = "\n".join(self._session_context[-5:]) if self._session_context else "Session just started."
        ex = event.get("exercise", "exercise").replace("_", " ")

        if event["type"] == "form_error":
            mistake = event.get("message", event.get("mistake", ""))
            return (
                f"Recent session context:\n{context}\n\n"
                f"The user is doing {ex}. They have a form issue: '{mistake}'. "
                f"Give a brief, Jarvis-style correction cue. Max 20 words."
            )
        elif event["type"] == "rep_milestone":
            reps = event.get("reps", 0)
            return (
                f"Recent session context:\n{context}\n\n"
                f"The user just completed {reps} reps of {ex}. "
                f"Give a brief Jarvis-style encouragement or push. Max 20 words."
            )
        elif event["type"] == "good_form":
            return (
                f"Recent session context:\n{context}\n\n"
                f"The user is maintaining excellent form on {ex}. "
                f"Briefly acknowledge this in Jarvis style. Max 15 words."
            )
        return f"User is working out. Say something brief as Jarvis. Max 15 words."

    def _template_response(self, event: Dict[str, Any]) -> str:
        """Fallback responses when Ollama is not available."""
        ex = event.get("exercise", "the exercise").replace("_", " ")
        if event["type"] == "form_error":
            msg = event.get("message", "Adjust your form.")
            return f"{msg} Keep that in mind, sir."
        elif event["type"] == "rep_milestone":
            reps = event.get("reps", 0)
            if reps == 1:
                return f"First rep of {ex} completed. Excellent start, sir."
            elif reps == 5:
                return f"Five reps down. Maintain that intensity, sir."
            elif reps == 10:
                return f"Ten reps. Outstanding work, sir. Keep pushing."
            else:
                return f"{reps} reps completed. Well done, sir."
        elif event["type"] == "good_form":
            return f"Textbook form on the {ex}, sir. Carry on."
        return "Keep pushing, sir."
