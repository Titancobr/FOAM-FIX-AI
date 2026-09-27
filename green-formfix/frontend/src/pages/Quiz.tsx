import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { generateCustomPlan, API_URL } from "@/lib/workoutPlans";

interface QuizQuestion {
  question: string;
  options: { label: string; value: string }[];
}

const questions: QuizQuestion[] = [
  {
    question: "What's your fitness goal?",
    options: [
      { label: "Build Muscle", value: "muscle" },
      { label: "Lose Fat", value: "fat_loss" },
      { label: "Strength", value: "strength" },
      { label: "General Fitness", value: "general" },
    ],
  },
  {
    question: "How many days can you train?",
    options: [
      { label: "3 Days", value: "3" },
      { label: "4 Days", value: "4" },
      { label: "5 Days", value: "5" },
      { label: "6 Days", value: "6" },
    ],
  },
  {
    question: "What's your experience level?",
    options: [
      { label: "Beginner", value: "beginner" },
      { label: "Intermediate", value: "intermediate" },
      { label: "Advanced", value: "advanced" },
    ],
  },
  {
    question: "Any equipment preference?",
    options: [
      { label: "Full Gym ", value: "full_gym" },
      { label: "Home Gym ", value: "home" },
      { label: "Bodyweight Only", value: "bodyweight" },
      { label: "Dumbbells Only", value: "dumbbells" },
    ],
  },
  {
    question: "How long can you train per session?",
    options: [
      { label: "30 minutes", value: "30" },
      { label: "45 minutes", value: "45" },
      { label: "60 minutes", value: "60" },
      { label: "90+ minutes", value: "90" },
    ],
  },
];

const Quiz = () => {
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSelect = (value: string) => {
    setAnswers((prev) => ({ ...prev, [currentQ]: value }));
  };

  const handleNext = async () => {
    if (!answers[currentQ]) {
      toast({ title: "Please select an option", variant: "destructive" });
      return;
    }
    if (currentQ < questions.length - 1) {
      setCurrentQ(currentQ + 1);
    } else {
      let userId: number | undefined;
      try { userId = JSON.parse(localStorage.getItem("fitUser") || "null")?.user_id; } catch { /* Sign-in required to save a plan. */ }
      if (!userId) {
        localStorage.setItem("quizAnswers", JSON.stringify(answers));
        toast({ title: "Sign in to save your custom plan", description: "Your quiz answers are saved on this device." });
        navigate("/login");
        return;
      }
      setSaving(true);
      try {
        const plan = generateCustomPlan(answers, userId);
        const response = await fetch(`${API_URL}/workouts/activate`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, plan_id: plan.id, plan }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Could not save custom plan");
        localStorage.setItem("quizAnswers", JSON.stringify(answers));
        localStorage.setItem("activeWorkoutPlanId", plan.id);
        toast({ title: "Custom plan saved to your profile" });
        navigate(`/workout/${plan.id}`);
      } catch (error) {
        toast({ title: error instanceof Error ? error.message : "Could not save custom plan", variant: "destructive" });
      } finally { setSaving(false); }
    }
  };

  const q = questions[currentQ];
  const progress = ((currentQ + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="px-5 pt-6 pb-2 flex items-center gap-3">
        <button
          onClick={() => (currentQ > 0 ? setCurrentQ(currentQ - 1) : navigate("/workouts"))}
          className="text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-6 w-6" />
        </button>
        <div className="flex-1">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-muted-foreground">Question {currentQ + 1}/{questions.length}</span>
          </div>
          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="flex-1 flex flex-col px-5 pt-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQ}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            className="flex-1"
          >
            <h2 className="font-display text-4xl text-foreground mb-8">{q.question}</h2>

            <div className="space-y-3">
              {q.options.map((opt) => {
                const isSelected = answers[currentQ] === opt.value;
                return (
                  <motion.button
                    key={opt.value}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect(opt.value)}
                    className={`w-full p-4 rounded-xl border-2 text-left text-lg font-medium transition-all ${
                      isSelected
                        ? "border-primary bg-primary/10 text-foreground"
                        : "border-border bg-card text-foreground hover:border-muted-foreground"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{opt.label}</span>
                      {isSelected && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Next Button */}
      <div className="px-5 pb-8">
        <Button
          onClick={handleNext}
          disabled={!answers[currentQ] || saving}
          className="w-full h-14 bg-primary text-primary-foreground font-display text-xl disabled:opacity-40"
        >
          {saving ? "Saving plan…" : currentQ === questions.length - 1 ? "Generate Plan" : "Next"}
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </div>
    </div>
  );
};

export default Quiz;
