import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Check, Flame, Sparkles } from "lucide-react";
import Navbar from "@/components/Navbar";
import BottomNav from "@/components/BottomNav";
import PlanCard from "@/components/workouts/PlanCard";
import { pushPullLegPlan, highVolumeSplitPlan, type WorkoutPlan } from "@/data/workoutData";
import { API_URL } from "@/lib/workoutPlans";
import heroFitness from "@/assets/legs-workout.jpg";
import { useToast } from "@/hooks/use-toast";

type ActivePlan = { plan_id: string; name: string; description?: string; is_custom: boolean; plan?: WorkoutPlan } | null;
type PlanHistory = { plan_id: string; days: { day_id: string; status: string }[] };
type WorkoutProfile = { active_plan: ActivePlan; latest_custom_plan: ActivePlan; history: PlanHistory[] };
const Workouts = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [userId, setUserId] = useState<number>();
  const [activePlan, setActivePlan] = useState<ActivePlan>(null);
  const [latestCustomPlan, setLatestCustomPlan] = useState<ActivePlan>(null);
  const [planHistory, setPlanHistory] = useState<PlanHistory[]>([]);
  const [plansLoading, setPlansLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const allPlans = [pushPullLegPlan, highVolumeSplitPlan];

  const loadPlan = async (id: number) => {
    const response = await fetch(`${API_URL}/workouts/profile/${id}`);
    if (response.ok) {
      const profile = await response.json() as WorkoutProfile;
      setActivePlan(profile.active_plan);
      setLatestCustomPlan(profile.latest_custom_plan);
      setPlanHistory(profile.history || []);
      if (profile.active_plan?.plan_id) localStorage.setItem("activeWorkoutPlanId", profile.active_plan.plan_id);
    }
  };
  useEffect(() => {
    try {
      const user = JSON.parse(localStorage.getItem("fitUser") || "null");
      if (user?.user_id) {
        setUserId(user.user_id);
        loadPlan(user.user_id).catch(() => {}).finally(() => setPlansLoading(false));
      } else setPlansLoading(false);
    } catch { setPlansLoading(false); /* Show plan choices; activation will request login. */ }
  }, []);

  const activate = async (planId: string) => {
    if (!userId) { toast({ title: "Sign in to save your active workout plan" }); navigate("/login"); return; }
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/workouts/activate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: userId, plan_id: planId }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not activate this plan");
      setActivePlan(data);
      localStorage.setItem("activeWorkoutPlanId", data.plan_id);
      toast({ title: `${data.name} is now your active plan` });
    } catch (error) { toast({ title: error instanceof Error ? error.message : "Plan update failed", variant: "destructive" }); }
    finally { setSaving(false); }
  };

  const openCustomWorkout = async () => {
    if (!userId) { toast({ title: "Sign in to open your saved custom workout" }); navigate("/login"); return; }
    if (plansLoading) { toast({ title: "Loading your saved workouts", description: "Try again in a moment." }); return; }
    if (!latestCustomPlan?.plan?.days?.length) { navigate("/quiz"); return; }
    const savedPlan = latestCustomPlan.plan;
    let destinationPlanId = latestCustomPlan.plan_id;
    if (activePlan?.plan_id !== destinationPlanId) {
      setSaving(true);
      try {
        const response = await fetch(`${API_URL}/workouts/activate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: userId, plan_id: destinationPlanId }) });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Could not open your saved custom workout");
        setActivePlan(data);
        localStorage.setItem("activeWorkoutPlanId", destinationPlanId);
      } catch (error) {
        toast({ title: error instanceof Error ? error.message : "Could not open custom workout", variant: "destructive" });
        setSaving(false);
        return;
      }
      setSaving(false);
    }
    const history = planHistory.find((entry) => entry.plan_id === destinationPlanId);
    const nextDay = savedPlan.days.find((day) => history?.days.find((item) => item.day_id === day.id)?.status !== "completed") || savedPlan.days[0];
    navigate(`/workout/${destinationPlanId}/${nextDay.id}`);
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Navbar />
      <section className="relative flex h-[42vh] min-h-[340px] items-center justify-center overflow-hidden px-4">
        <div className="absolute inset-0 z-0 bg-cover bg-center" style={{ backgroundImage: `url(${heroFitness})` }} />
        <div className="absolute inset-0 z-10 bg-black/50 bg-gradient-to-b from-background/20 via-background/60 to-background" />
        <div className="relative z-20 text-center"><motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="stat-badge mx-auto mb-4 w-fit bg-white/10 backdrop-blur-md"><Flame className="h-3 w-3" /> TRAIN YOUR WAY</motion.div><h1 className="font-heading text-6xl uppercase text-white drop-shadow-2xl md:text-8xl">Workout <span className="text-gradient">Plans</span></h1><p className="mx-auto mt-3 max-w-xl text-sm text-white/85">Choose a structured plan or build a custom schedule that fits your week.</p></div>
      </section>

      <main className="mx-auto max-w-7xl px-6">
        {activePlan && <section className="-mt-7 relative z-20 mb-8 flex flex-wrap items-center gap-4 rounded-2xl border border-primary/20 bg-card/90 p-5 shadow-xl backdrop-blur-xl"><div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary"><Check className="h-5 w-5" /></div><div className="min-w-0 flex-1"><p className="text-[10px] uppercase tracking-[.22em] text-primary">Active workout plan</p><h2 className="truncate font-heading text-2xl uppercase">{activePlan.name}</h2><p className="text-xs text-muted-foreground">Saved to your profile. Progress is kept when you switch plans.</p></div><button onClick={() => navigate(`/workout/${activePlan.plan_id}`)} className="btn-primary flex items-center gap-2 px-4 py-2.5 text-xs">Continue plan <ArrowRight className="h-4 w-4" /></button></section>}

        <div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><p className="text-[10px] uppercase tracking-[.28em] text-primary/70">Pick a plan</p><h2 className="mt-1 font-heading text-3xl uppercase text-foreground">Make this week count</h2></div><button onClick={() => navigate("/quiz")} className="btn-outline inline-flex items-center gap-2">Build custom plan <Sparkles className="h-4 w-4" /></button></div>
        <div className="grid grid-cols-1 gap-7 pb-8 md:grid-cols-2 lg:grid-cols-3">
          {allPlans.map((plan, index) => <PlanCard key={plan.id} plan={plan} index={index} isActive={activePlan?.plan_id === plan.id} onActivate={() => !saving && activate(plan.id)} onClick={() => navigate(`/workout/${plan.id}`)} />)}
          <PlanCard
            plan={latestCustomPlan?.plan || { id: "custom", name: "Custom Workout", description: "Answer a few questions and save your own workout schedule.", days: [], image: "custom" }}
            index={2}
            isActive={Boolean(activePlan?.plan_id === latestCustomPlan?.plan_id && latestCustomPlan?.plan_id)}
            onClick={openCustomWorkout}
            onActivate={latestCustomPlan ? () => !saving && activate(latestCustomPlan.plan_id) : undefined}
            onRetake={latestCustomPlan ? () => navigate("/quiz") : undefined}
          />
        </div>
      </main>
      <BottomNav />
    </div>
  );
};
export default Workouts;
