// src/pages/WorkoutDetail.tsx
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { pushPullLegPlan, highVolumeSplitPlan } from "@/data/workoutData";
import WorkoutDayCard from "@/components/workouts/WorkoutDayCard";

const WorkoutDetail = () => {
  const { planId } = useParams();
  const navigate = useNavigate();

  const plan = planId === "ppl" ? pushPullLegPlan : highVolumeSplitPlan;

  if (!plan) return <div className="p-10 text-center">Plan not found</div>;

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <button onClick={() => navigate("/workouts")} className="mb-6 p-2 bg-secondary/50 rounded-full">
        <ArrowLeft className="w-5 h-5" />
      </button>

      <h1 className="text-4xl font-heading uppercase mb-2">{plan.name}</h1>
      <p className="text-muted-foreground mb-8">{plan.description}</p>

      <div className="space-y-4">
        {plan.days.map((day, i) => (
          <WorkoutDayCard 
            key={day.id} 
            day={day} 
            index={i} 
            // Change this from /camera to /workout
            onClick={() => navigate(`/workout/${planId}/${day.id}`)} 
          />
        ))}
      </div>
    </div>
  );
};

export default WorkoutDetail;