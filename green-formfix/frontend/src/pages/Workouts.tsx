// src/pages/Workouts.tsx
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Flame, Sparkles } from "lucide-react";
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
      <section className="relative flex h-[46vh] items-center justify-center overflow-hidden px-4">
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
          <motion.p
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 }}
            className="mx-auto mt-4 max-w-2xl text-sm text-white/85 md:text-base"
          >
            Pick a split, stay on pace, and move into the camera flow with less friction.
          </motion.p>
        </div>
      </section>

      <div className="-mt-12 mx-auto mb-8 grid max-w-7xl gap-4 px-6 md:grid-cols-3">
        {[
          { title: "Structured splits", copy: "Push, pull, legs and high-volume options ready to go." },
          { title: "Live tracking", copy: "Jump from plan view to real-time rep counting and form support." },
          { title: "Adaptive flow", copy: "Pair your workout day with meal tracking inside the same routine." },
        ].map((item, index) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.08 }}
            className="glass-card p-5"
          >
            <div className="mb-3 flex items-center gap-2 text-primary">
              <Sparkles className="h-4 w-4" />
              <p className="text-[10px] uppercase tracking-[0.28em]">Focus</p>
            </div>
            <h3 className="text-2xl text-foreground">{item.title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{item.copy}</p>
          </motion.div>
        ))}
      </div>

      <div className="mx-auto mb-6 flex max-w-7xl items-center justify-between px-6">
        <div>
          <p className="text-[10px] uppercase tracking-[0.28em] text-primary/70">Choose your route</p>
          <h2 className="mt-1 text-3xl text-foreground">Plans built for consistency</h2>
        </div>
        <button onClick={() => navigate("/quiz")} className="btn-outline hidden items-center gap-2 md:inline-flex">
          Try Custom AI
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

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
