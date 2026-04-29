import pyttsx3
import time


class VoiceEngine:
    def __init__(self, enabled=True, cooldown_seconds=2.5):
        self.enabled = enabled
        self.cooldown_seconds = cooldown_seconds
        self.last_spoken_at = 0.0
        self.engine = None
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
            except Exception:
                self.enabled = False

    def speak(self, text):
        if not self.enabled or self.engine is None:
            return
        now = time.time()
        if now - self.last_spoken_at < self.cooldown_seconds:
            return
        self.engine.say(text)
        self.engine.runAndWait()
        self.last_spoken_at = now
