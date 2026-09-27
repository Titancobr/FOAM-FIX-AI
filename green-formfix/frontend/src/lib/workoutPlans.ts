import React from "react";
import { highVolumeSplitPlan, pushPullLegPlan, type WorkoutPlan } from "@/data/workoutData";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const builtInPlan = (id?: string) =>
  id === "ppl" ? pushPullLegPlan : id === "volume-split" ? highVolumeSplitPlan : undefined;

export function generateCustomPlan(answers: Record<number, string>, userId: number): WorkoutPlan {
  const daysPerWeek = Math.min(6, Math.max(3, Number(answers[1] || 3)));
  const template = daysPerWeek <= 3 ? pushPullLegPlan : highVolumeSplitPlan;
  const goal = answers[0] || "general";
  const experience = answers[2] || "beginner";
  const equipment = (answers[3] || "full_gym").trim();
  const duration = answers[4] || "45";
  const reps = goal === "strength" ? "5-8" : goal === "general" || goal === "fat_loss" ? "10-15" : "8-12";
  const maxExercises = duration === "30" ? 4 : duration === "45" ? 5 : 6;
  const salt = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const id = `custom-${userId}-${salt}`;
  const days = Array.from({ length: daysPerWeek }, (_, index) => {
    const source = template.days[index % template.days.length];
    return {
      ...structuredClone(source),
      id: `day-${index + 1}-${source.id}`,
      name: `Day ${index + 1} · ${source.name}`,
      exercises: source.exercises.slice(0, maxExercises).map((exercise, exerciseIndex) => ({
        ...exercise,
        id: `${source.id}-${index + 1}-${exerciseIndex + 1}`,
        sets: goal === "strength" ? Math.max(3, exercise.sets) : experience === "beginner" ? Math.min(3, exercise.sets) : exercise.sets,
        reps,
      })),
    };
  });
  return {
    id,
    name: "Custom Fitness Plan",
    description: `${daysPerWeek} days per week · ${goal.replaceAll("_", " ")} · ${experience} · ${equipment.replaceAll("_", " ")} · ${duration} minute sessions`,
    image: "custom",
    days,
  };
}

export function useWorkoutPlan(planId?: string) {
  const [plan, setPlan] = React.useState<WorkoutPlan | null>(() => builtInPlan(planId) || null);
  const [loading, setLoading] = React.useState(!builtInPlan(planId));
  React.useEffect(() => {
    const builtIn = builtInPlan(planId);
    setPlan(builtIn || null);
    if (builtIn || !planId) { setLoading(false); return; }
    let cancelled = false;
    try {
      const userId = JSON.parse(localStorage.getItem("fitUser") || "null")?.user_id;
      if (!userId) { setLoading(false); return; }
      setLoading(true);
      fetch(`${API_URL}/workouts/custom/${userId}/${encodeURIComponent(planId)}`)
        .then((response) => response.ok ? response.json() : null)
        .then((data) => { if (!cancelled) setPlan(data?.plan || null); })
        .catch(() => { if (!cancelled) setPlan(null); })
        .finally(() => { if (!cancelled) setLoading(false); });
    } catch { setLoading(false); }
    return () => { cancelled = true; };
  }, [planId]);
  return { plan, loading };
}
