//src/components/workouts/PlanCard.tsx
import { motion } from "framer-motion";
import { Dumbbell, BarChart3, ArrowRight } from "lucide-react";
import { WorkoutPlan } from "@/data/workoutData";

// Import your assets here
import pushImg from "@/assets/push-workout.jpg";
import broImg from "@/assets/bro-split.jpg";
import customImg from "@/assets/custom-workout.jpg";

// Map the 'image' string from your WorkoutPlan object to the imported file
const imageMap: Record<string, string> = {
  push: pushImg,
  split: broImg,
  custom: customImg,
};

interface PlanCardProps {
  plan: WorkoutPlan;
  index: number;
  onClick: () => void;
  isActive?: boolean;
  onActivate?: () => void;
  onRetake?: () => void;
}

const PlanCard = ({ plan, index, onClick, isActive = false, onActivate, onRetake }: PlanCardProps) => {
  // Determine level based on ID
  const level = plan.id === "ppl" ? "Intermediate" : "Advanced";
  
  // Use the image map, fallback to a placeholder if not found
  const displayImage = imageMap[plan.image] || customImg;

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ 
        duration: 0.6, 
        delay: index * 0.15, 
        ease: [0.25, 0.46, 0.45, 0.94] 
      }}
      onClick={onClick}
      className="group relative cursor-pointer glass-card overflow-hidden hover-lift"
    >
      <div className="relative h-72 overflow-hidden">
        <img
          src={displayImage}
          alt={plan.name}
          className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:brightness-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-card via-card/50 to-transparent" />

        {/* Overlay badge - calculating days from the array length */}
        <div className="absolute top-4 right-4">
          <span className={index % 2 === 0 ? "stat-badge" : "accent-badge"}>
            {plan.days.length > 0 ? `${plan.days.length} Days/Week` : "Flexible"}
          </span>
        </div>

        <div className="absolute bottom-5 left-5 right-5">
          <h2 className="text-4xl font-heading text-foreground tracking-wide mb-1 uppercase">
            {plan.name}
          </h2>
          <p className="text-xs text-primary font-mono font-medium uppercase">
            {plan.id === "custom" ? "Personalized" : level}
          </p>
        </div>
      </div>

      {isActive && <div className="absolute left-4 top-4 rounded-full border border-primary/30 bg-background/80 px-3 py-1 text-[10px] font-mono uppercase tracking-widest text-primary">Active plan</div>}
      <div className="p-6">
        <p className="text-muted-foreground text-sm mb-5 font-body leading-relaxed line-clamp-2">
          {plan.description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="stat-badge text-[10px]">
              <Dumbbell className="w-3 h-3" /> {plan.days.length || "—"} DAYS
            </span>
            <span className="accent-badge text-[10px]">
              <BarChart3 className="w-3 h-3" /> {level}
            </span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary transition-colors">
            <ArrowRight className="w-5 h-5 text-primary group-hover:text-black transition-transform group-hover:translate-x-0.5" />
          </div>
        </div>
        {onActivate && <button type="button" onClick={(event) => { event.stopPropagation(); onActivate(); }} className={`mt-5 w-full rounded-xl border px-4 py-3 text-xs font-semibold uppercase tracking-[.16em] transition ${isActive ? "border-primary/25 bg-primary/10 text-primary" : "border-white/10 bg-white/[.03] text-foreground hover:border-primary/40 hover:text-primary"}`}>{isActive ? "Currently active" : "Set as active plan"}</button>}
        {onRetake && <button type="button" onClick={(event) => { event.stopPropagation(); onRetake(); }} className="mt-2 w-full rounded-xl px-4 py-2 text-[10px] font-semibold uppercase tracking-[.16em] text-muted-foreground transition hover:text-primary">Retake quiz / change custom plan</button>}
      </div>
    </motion.div>
  );
};

export default PlanCard;