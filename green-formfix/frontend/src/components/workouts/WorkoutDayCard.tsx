//src/components/workouts/WorkoutDayCard.tsx
import { motion } from "framer-motion";
import { ChevronRight, Clock, Flame } from "lucide-react";

export default function WorkoutDayCard({ day, index, onClick }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      onClick={onClick}
      className="glass-card p-5 cursor-pointer hover:border-primary/40 group flex items-center justify-between"
    >
      <div>
        <h3 className="font-heading text-2xl uppercase group-hover:text-primary transition-colors">{day.name}</h3>
        <p className="text-muted-foreground text-xs font-mono uppercase">Focus: {day.focus}</p>
        <div className="flex gap-3 mt-3">
          <span className="flex items-center gap-1 text-[10px] bg-secondary/30 px-2 py-1 rounded"><Clock className="h-3 w-3" /> 60m</span>
          <span className="flex items-center gap-1 text-[10px] bg-secondary/30 px-2 py-1 rounded"><Flame className="h-3 w-3" /> {day.exercises.length} Exercises</span>
        </div>
      </div>
      <div className="bg-primary/10 p-2 rounded-lg group-hover:bg-primary group-hover:text-black transition-all">
        <ChevronRight className="h-5 w-5" />
      </div>
    </motion.div>
  );
}