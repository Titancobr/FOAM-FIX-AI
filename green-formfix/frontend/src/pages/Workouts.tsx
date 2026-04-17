// src/pages/Workouts.tsx
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Flame } from "lucide-react";
import Navbar from "@/components/Navbar";
import BottomNav from "@/components/BottomNav";
import PlanCard from "@/components/workouts/PlanCard";
import { pushPullLegPlan, highVolumeSplitPlan } from "@/data/workoutData";
import heroFitness from "@/assets/legs-workout.jpg";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Workouts = () => {
  const navigate = useNavigate();
  const [progressSummary, setProgressSummary] = useState<{
    days_worked_out: number;
    completed_workout_days: number;
    current_position?: { day_name?: string; completed_exercises?: number; total_exercises?: number };
  } | null>(null);

  // Map your imported data objects into an array
  const allPlans = [pushPullLegPlan, highVolumeSplitPlan];

  useEffect(() => {
    const fitUserRaw = localStorage.getItem("fitUser");
    if (!fitUserRaw) return;
    let fitUser: { user_id?: number } | null = null;
    try {
      fitUser = JSON.parse(fitUserRaw);
    } catch {
      return;
    }
    if (!fitUser?.user_id) return;

    fetch(`${API_URL}/progress/summary/${fitUser.user_id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setProgressSummary(data);
      })
      .catch(() => {
        // Ignore summary failures for now.
      });
  }, []);

  return (
    <div className="min-h-screen bg-background pb-20">
      <Navbar />

      {/* Hero Section */}
<section className="relative h-[40vh] flex items-center justify-center overflow-hidden px-4">
  
  {/* Background Image */}
  <div
    className="absolute inset-0 z-0 bg-no-repeat bg-cover bg-center"
    style={{
      backgroundImage: `url(${heroFitness})`,
    }}
  />

  {/* Overlay */}
  <div className="absolute inset-0 bg-black/50 bg-gradient-to-b from-background/20 via-background/60 to-background z-10" />

  {/* Content */}
  <div className="relative z-20 text-center">
    
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="stat-badge mx-auto mb-4 w-fit backdrop-blur-md bg-white/10"
    >
      <Flame className="w-3 h-3" /> PRO TRAINING
    </motion.div>

    <h1 className="text-6xl md:text-8xl font-heading text-white uppercase drop-shadow-2xl">
      Workout <span className="text-gradient">Plans</span>
    </h1>

  </div>
</section>

      {/* Grid */}
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {progressSummary && (
          <div className="lg:col-span-3 glass-card p-6 border-primary/20">
            <p className="text-[10px] font-mono text-primary uppercase tracking-[0.25em] mb-2">
              Progress Tracker
            </p>
            <h3 className="font-heading text-3xl uppercase mb-2">Your Workout Journey</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                <p className="text-muted-foreground">Days Worked Out</p>
                <p className="text-3xl font-heading text-primary">{progressSummary.days_worked_out}</p>
              </div>
              <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                <p className="text-muted-foreground">Completed Workout Days</p>
                <p className="text-3xl font-heading text-primary">{progressSummary.completed_workout_days}</p>
              </div>
              <div className="rounded-xl bg-white/5 p-4 border border-white/10">
                <p className="text-muted-foreground">Current Position</p>
                <p className="font-heading text-xl text-white">
                  {progressSummary.current_position?.day_name || "Start your first day"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {(progressSummary.current_position?.completed_exercises || 0)}/
                  {(progressSummary.current_position?.total_exercises || 0)} exercises
                </p>
              </div>
            </div>
          </div>
        )}
        {allPlans.map((plan, i) => (
          <PlanCard 
            key={plan.id} 
            plan={plan} 
            index={i} 
            onClick={() => navigate(`/workout/${plan.id}`)} 
          />
        ))}
        
        {/* Manual Custom Card */}
        <PlanCard 
          plan={{
            id: "custom",
            name: "Custom AI",
            description: "Personalized routine based on your goals.",
            days: [] as any, // Placeholder to satisfy interface
            image: ""
          }}
          index={2}
          onClick={() => navigate("/quiz")}
        />
      </div>

      <BottomNav />
    </div>
  );
};

export default Workouts;
