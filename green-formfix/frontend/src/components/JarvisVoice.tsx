import { useEffect, useRef, useState } from "react";
import { Bot, Loader2, Mic, MicOff, Volume2, X } from "lucide-react";

type SpeechRecognitionEventLike = Event & {
  results: { [index: number]: { [index: number]: { transcript: string } } };
};

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onend: (() => void) | null;
  onerror: ((event: { error?: string }) => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  start: () => void;
  stop: () => void;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

type SpeechWindow = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

const JarvisVoice = () => {
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const [open, setOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [reply, setReply] = useState("Good day, Sir. Jarvis is at your service.");
  const [error, setError] = useState("");

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const speak = (text: string) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const britishVoice = window.speechSynthesis.getVoices().find((voice) => voice.lang.toLowerCase().startsWith("en-gb"));
    if (britishVoice) utterance.voice = britishVoice;
    utterance.rate = 0.94;
    utterance.pitch = 0.92;
    window.speechSynthesis.speak(utterance);
  };

  const askJarvis = async (message: string) => {
    setThinking(true);
    setError("");
    try {
      const response = await fetch("/ai/voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          context: `${window.location.pathname}. Current workout: ${localStorage.getItem("currentWorkoutContext") || "none"}`,
        }),
      });
      if (!response.ok) throw new Error("The AI backend is unavailable.");
      const data = await response.json();
      const nextReply = String(data.reply || "At your service, Sir.");
      setReply(nextReply);
      speak(nextReply);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Voice service unavailable.";
      setError(message);
      setReply("I cannot reach the coaching service at present, Sir.");
    } finally {
      setThinking(false);
    }
  };

  const startListening = () => {
    const speechWindow = window as SpeechWindow;
    const Recognition = speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
    if (!Recognition) {
      setError("Voice input is supported in Chrome or Safari.");
      return;
    }

    const recognition = new Recognition();
    recognition.lang = "en-GB";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const text = event.results[0]?.[0]?.transcript?.trim() || "";
      setTranscript(text);
      if (text) void askJarvis(text);
    };
    recognition.onerror = (event) => {
      setError(event.error === "not-allowed" ? "Microphone permission was blocked." : "I could not hear that, Sir.");
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    setError("");
    setListening(true);
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  return (
    <div className="fixed bottom-5 right-5 z-[60] flex flex-col items-end gap-3">
      {open && (
        <div className="glass-card w-[min(360px,calc(100vw-2rem))] p-4 shadow-2xl">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/15 text-primary"><Bot className="h-5 w-5" /></div>
              <div><p className="text-sm font-semibold text-foreground">Jarvis</p><p className="text-[10px] uppercase tracking-[0.2em] text-primary/70">Voice coach</p></div>
            </div>
            <button onClick={() => setOpen(false)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-white/10" aria-label="Close Jarvis"><X className="h-4 w-4" /></button>
          </div>
          <p className="min-h-12 rounded-xl border border-white/8 bg-black/15 p-3 text-sm text-foreground/85">{reply}</p>
          {transcript && <p className="mt-2 text-xs text-muted-foreground">You: {transcript}</p>}
          {error && <p className="mt-2 text-xs text-red-300">{error}</p>}
          <button onClick={listening ? stopListening : startListening} disabled={thinking} className="btn-primary mt-3 flex w-full items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-60">
            {thinking ? <Loader2 className="h-4 w-4 animate-spin" /> : listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            {thinking ? "Thinking..." : listening ? "Stop listening" : "Speak to Jarvis"}
          </button>
          <button onClick={() => speak(reply)} className="mt-2 flex w-full items-center justify-center gap-2 text-xs text-primary hover:text-primary/80"><Volume2 className="h-3.5 w-3.5" /> Replay response</button>
        </div>
      )}
      <button onClick={() => setOpen((value) => !value)} className="flex h-14 w-14 items-center justify-center rounded-full border border-primary/40 bg-primary text-primary-foreground shadow-[0_0_35px_rgba(14,165,233,0.4)] transition-transform hover:scale-105" aria-label="Open Jarvis voice coach"><Bot className="h-6 w-6" /></button>
    </div>
  );
};

export default JarvisVoice;
