// src/pages/Workouts.tsx
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Flame } from "lucide-react";
import Navbar from "@/components/Navbar";
import BottomNav from "@/components/BottomNav";
import PlanCard from "@/components/workouts/PlanCard";
import { pushPullLegPlan, highVolumeSplitPlan } from "@/data/workoutData";
import heroFitness from "@/assets/legs-workout.jpg";

const Workouts = () => {
  const navigate = useNavigate();

  const allPlans = [pushPullLegPlan, highVolumeSplitPlan];

  return (
    <div className="min-h-screen bg-background pb-20">
      <Navbar />

      {/* Hero Section */}
      <section className="relative h-[40vh] flex items-center justify-center overflow-hidden px-4">
        <div
          className="absolute inset-0 z-0 bg-no-repeat bg-cover bg-center"
          style={{ backgroundImage: `url(${heroFitness})` }}
        />
        <div className="absolute inset-0 bg-black/50 bg-gradient-to-b from-background/20 via-background/60 to-background z-10" />
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
            days: [] as any,
            image: "",
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