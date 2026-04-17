// src/App.tsx
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Workouts from "./pages/Workouts";
import WorkoutDetail from "./pages/WorkoutDetail";
import DayExercises from "./pages/DayExercises";
import Quiz from "./pages/Quiz";
import Recipes from "./pages/Recipes";
import ScanMeal from "./pages/ScanMeal";
import NotFound from "./pages/NotFound";
import Camera from "./pages/Camera";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Main Workouts List */}
          <Route path="/workouts" element={<Workouts />} />
          
          {/* Plan Overview (e.g., /workout/ppl) */}
          <Route path="/workout/:planId" element={<WorkoutDetail />} />
          
          {/* Specific Day Checklist (e.g., /workout/ppl/push) */}
          <Route path="/workout/:planId/:dayId" element={<DayExercises />} />
          
          {/* AR Lens View */}
          <Route path="/camera" element={<Camera />} />
          
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/recipes" element={<Recipes />} />
          <Route path="/scan" element={<ScanMeal />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;