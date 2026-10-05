// src/pages/UserProfile.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { User, Flame, Trophy, Dumbbell, LogOut, ChevronRight, Check, RefreshCw } from "lucide-react";
import Navbar from "@/components/Navbar";
import BottomNav from "@/components/BottomNav";

const API_URL = import.meta.env.VITE_API_URL ?? "";

interface ProgressSummary {
  days_worked_out: number;
  completed_workout_days: number;
  current_position?: {
    day_name?: string;
    completed_exercises?: number;
    total_exercises?: number;
  };
}

interface PlanHistoryItem {
  plan_id: string; name: string; is_custom: boolean; workout_days: number; completed_days: number; last_activity: string | null;
}
interface ActivePlan { plan_id: string; name: string; description?: string; is_custom: boolean; plan?: { days?: { id: string; name: string }[] }; }
interface PlanProfile { active_plan: ActivePlan | null; history: PlanHistoryItem[]; }

interface FitUser {
  user_id?: number;
  name?: string;
  email?: string;
}

const UserProfile = () => {
  const navigate = useNavigate();
  const [fitUser, setFitUser] = useState<FitUser | null>(null);
  const [progressSummary, setProgressSummary] = useState<ProgressSummary | null>(null);
  const [planProfile, setPlanProfile] = useState<PlanProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fitUserRaw = localStorage.getItem("fitUser");
    if (!fitUserRaw) {
      navigate("/login");
      return;
    }

    let parsed: FitUser | null = null;
    try {
      parsed = JSON.parse(fitUserRaw);
    } catch {
      navigate("/login");
      return;
    }

    setFitUser(parsed);

    if (!parsed?.user_id) {
      setLoading(false);
      return;
    }

    Promise.all([
      fetch(`${API_URL}/progress/summary/${parsed.user_id}`).then((res) => res.ok ? res.json() : null),
      fetch(`${API_URL}/workouts/profile/${parsed.user_id}`).then((res) => res.ok ? res.json() : null),
    ])
      .then(([progress, plans]) => {
        if (progress) setProgressSummary(progress);
        if (plans) setPlanProfile(plans);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("fitUser");
    localStorage.removeItem("token");
    navigate("/");
  };

  const displayName = fitUser?.name || fitUser?.email?.split("@")[0] || "Athlete";
  const completedExercises = progressSummary?.current_position?.completed_exercises ?? 0;
  const totalExercises = progressSummary?.current_position?.total_exercises ?? 0;
  const progressPercent = totalExercises > 0 ? Math.round((completedExercises / totalExercises) * 100) : 0;

  return (
    <div className="min-h-screen bg-background pb-20">
      <Navbar />

      <div className="max-w-3xl mx-auto px-6 pt-28 pb-12">

        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-card p-8 mb-6 flex items-center gap-6"
        >
          <div className="w-20 h-20 rounded-full bg-primary/20 border-2 border-primary/40 flex items-center justify-center shrink-0">
            <User className="w-9 h-9 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] font-mono text-primary uppercase tracking-[0.25em] mb-1">
              Member Profile
            </p>
            <h1 className="font-heading text-4xl uppercase text-white truncate">{displayName}</h1>
            {fitUser?.email && (
              <p className="text-sm text-muted-foreground mt-1 truncate">{fitUser.email}</p>
            )}
          </div>
        </motion.div>

        {/* Active workout plan and preserved plan history */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card mb-6 border-primary/20 p-6"
        >
          <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-[10px] font-mono uppercase tracking-[0.25em] text-primary">Training plan</p>
              <h2 className="mt-1 font-heading text-3xl uppercase">{planProfile?.active_plan?.name || "No active plan yet"}</h2>
              <p className="mt-1 text-sm text-muted-foreground">{planProfile?.active_plan ? (planProfile.active_plan.is_custom ? "Your saved custom workout plan" : "Your selected workout plan") : "Choose a plan to start tracking your training."}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {planProfile?.active_plan?.is_custom && <button onClick={() => navigate("/quiz")} className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-xs hover:border-primary/40 hover:text-primary"><RefreshCw className="h-3.5 w-3.5" />Retake quiz</button>}
              <button onClick={() => navigate("/workouts")} className="btn-primary inline-flex items-center gap-2 px-4 py-2 text-xs">Change plan <ChevronRight className="h-4 w-4" /></button>
            </div>
          </div>
          {planProfile?.active_plan?.description && <p className="mb-4 text-sm text-muted-foreground">{planProfile.active_plan.description}</p>}
          {planProfile?.active_plan?.plan?.days && <div className="mb-4 flex flex-wrap gap-2">{planProfile.active_plan.plan.days.map((day) => <span key={day.id} className="rounded-full border border-primary/15 bg-primary/[.05] px-3 py-1 text-xs text-primary">{day.name}</span>)}</div>}
          {planProfile?.history?.length ? <div className="border-t border-white/10 pt-4">
            <p className="mb-3 text-[10px] uppercase tracking-[.2em] text-muted-foreground">Workout plan history · kept when you switch</p>
            <div className="space-y-2">{planProfile.history.map((item) => <div key={item.plan_id} className="flex flex-wrap items-center gap-2 rounded-xl bg-white/[.025] px-3 py-2.5">
              <div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{item.name}{planProfile.active_plan?.plan_id === item.plan_id && <span className="ml-2 inline-flex items-center gap-1 text-[9px] font-medium uppercase tracking-widest text-primary"><Check className="h-3 w-3" />Active</span>}</p><p className="text-xs text-muted-foreground">{item.completed_days} completed · {item.workout_days} days started</p></div>
              {item.last_activity && <span className="text-[10px] text-muted-foreground">Last trained {new Date(item.last_activity).toLocaleDateString()}</span>}
            </div>)}</div>
          </div> : <p className="border-t border-white/10 pt-4 text-xs text-muted-foreground">Workout history will appear here as you train.</p>}
        </motion.section>

        {/* Progress Tracker */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-card p-6 mb-6 border-primary/20"
        >
          <p className="text-[10px] font-mono text-primary uppercase tracking-[0.25em] mb-2">
            Progress Tracker
          </p>
          <h3 className="font-heading text-3xl uppercase mb-5">Your Workout Journey</h3>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="rounded-xl bg-white/5 p-4 border border-white/10 animate-pulse h-24" />
              ))}
            </div>
          ) : progressSummary ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
                <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                  <div className="flex items-center gap-2 mb-1">
                    <Flame className="w-3.5 h-3.5 text-primary" />
                    <p className="text-xs text-muted-foreground">Days Worked Out</p>
                  </div>
                  <p className="text-4xl font-heading text-primary">{progressSummary.days_worked_out}</p>
                </div>

                <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                  <div className="flex items-center gap-2 mb-1">
                    <Trophy className="w-3.5 h-3.5 text-primary" />
                    <p className="text-xs text-muted-foreground">Completed Days</p>
                  </div>
                  <p className="text-4xl font-heading text-primary">{progressSummary.completed_workout_days}</p>
                </div>

                <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                  <div className="flex items-center gap-2 mb-1">
                    <Dumbbell className="w-3.5 h-3.5 text-primary" />
                    <p className="text-xs text-muted-foreground">Current Position</p>
                  </div>
                  <p className="font-heading text-xl text-white">
                    {progressSummary.current_position?.day_name || "Start your first day"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {completedExercises}/{totalExercises} exercises
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              {totalExercises > 0 && (
                <div>
                  <div className="flex justify-between text-xs text-muted-foreground mb-2">
                    <span>Today's Progress</span>
                    <span className="text-primary font-mono">{progressPercent}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progressPercent}%` }}
                      transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
                      className="h-full rounded-full bg-primary"
                    />
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Dumbbell className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No progress data yet. Start your first workout!</p>
              <button
                onClick={() => navigate("/workouts")}
                className="mt-4 btn-primary px-6 py-2.5 text-sm"
              >
                Browse Plans
              </button>
            </div>
          )}
        </motion.div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-card p-4 mb-6"
        >
          <button
            onClick={() => navigate("/workouts")}
            className="w-full flex items-center justify-between px-4 py-3 rounded-lg hover:bg-white/5 transition-colors group"
          >
            <div className="flex items-center gap-3">
              <Dumbbell className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">View Workout Plans</span>
            </div>
            <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        {/* Logout */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-xl border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-colors text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            Logout Session
          </button>
        </motion.div>

      </div>

      <BottomNav />
    </div>
  );
};

export default UserProfile;
