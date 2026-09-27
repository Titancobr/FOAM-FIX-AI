import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Check } from "lucide-react";
import WorkoutDayCard from "@/components/workouts/WorkoutDayCard";
import { useWorkoutPlan } from "@/lib/workoutPlans";

const WorkoutDetail = () => {
  const { planId } = useParams();
  const navigate = useNavigate();
  const { plan, loading } = useWorkoutPlan(planId);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  useEffect(() => {
    try {
      const userId = JSON.parse(localStorage.getItem("fitUser") || "null")?.user_id;
      if (userId) fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/workouts/profile/${userId}`).then((response) => response.ok ? response.json() : null).then((data) => setActivePlanId(data?.active_plan?.plan_id || null)).catch(() => {});
    } catch { /* Not signed in. */ }
  }, []);

  if (loading) return <div className="min-h-screen bg-background p-10 text-center text-muted-foreground">Loading your workout…</div>;
  if (!plan) return <div className="p-10 text-center">Plan not found. Choose an active plan from <button className="text-primary" onClick={() => navigate("/workouts")}>workouts</button>.</div>;
  const isActive = activePlanId === plan.id;

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <button onClick={() => navigate("/workouts")} className="mb-6 rounded-full bg-secondary/50 p-2"><ArrowLeft className="h-5 w-5" /></button>
      <div className="mb-7 flex flex-wrap items-start justify-between gap-4"><div><p className="text-[10px] uppercase tracking-[.25em] text-primary">{plan.days.length} training days</p><h1 className="mb-2 font-heading text-4xl uppercase">{plan.name}</h1><p className="max-w-2xl text-muted-foreground">{plan.description}</p></div><button onClick={() => navigate("/workouts")} className={`rounded-xl border px-4 py-3 text-xs font-semibold uppercase tracking-wider ${isActive ? "border-primary/30 bg-primary/10 text-primary" : "border-white/10 hover:border-primary/40"}`}>{isActive ? <><Check className="mr-2 inline h-4 w-4"/>Active plan</> : "Change active plan"}</button></div>
      <div className="space-y-4">{plan.days.map((day, index) => <WorkoutDayCard key={day.id} day={day} index={index} onClick={() => navigate(`/workout/${plan.id}/${day.id}`)} />)}</div>
    </div>
  );
};
export default WorkoutDetail;
