import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Apple, Target, TrendingUp, ArrowRight, Zap } from "lucide-react";
import Navbar from "../components/Navbar";
import BottomNav from "@/components/BottomNav";
import heroImg from "@/assets/hero-fitness.jpg";

const features = [
  { icon: Apple, title: "Find Recipes", desc: "Find new recipes based on your health goals", color: "text-primary" },
  /*{ icon: Target, title: "Calorie Tracker", desc: "Track your daily caloric intake and goals", color: "text-accent" },*/
  { icon: TrendingUp, title: "Workout Plans", desc: "Structured exercises for different muscle groups", color: "text-primary" },
];

const stats = [
  { value: "50+", label: "Exercises" },
  { value: "3", label: "Programs" },
  { value: "100%", label: "Free" },
];

const Index = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-background">
        {/* Hero Section */}
<section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
  {/* The Background Image */}
  <div 
    className="absolute inset-0 z-0 bg-no-repeat bg-cover bg-center"
    style={{
      backgroundImage: `url(${heroImg})`,
    }}
  />

  {/* The Overlay - Darkens the image so text stays readable */}
  <div className="absolute inset-0 bg-black/50 bg-gradient-to-b from-background/20 via-background/60 to-background z-10" />
  
  <div className="relative z-20 text-center px-5 max-w-4xl mx-auto">
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="stat-badge mx-auto mb-6 w-fit backdrop-blur-md bg-white/10"
    >
      <Zap className="w-3.5 h-3.5" /> Transform your body with science-backed programs
    </motion.div>

    <motion.h1
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="text-6xl md:text-8xl font-heading text-white leading-[0.9] mb-6 drop-shadow-2xl"
    >
      TRANSFORM YOUR
      <br />
      <span className="text-gradient">FITNESS JOURNEY</span>
    </motion.h1>

    <motion.p
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.15 }}
      className="text-white/90 text-lg md:text-xl max-w-2xl mx-auto mb-10 drop-shadow-md"
    >
      Complete fitness solution with personalized workouts, nutrition tracking, 
      and meal planning to achieve your health goals.
    </motion.p>

  </div>
</section>
        {/* Features Section */}
        <section className="py-24 px-5">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <div className="stat-badge mx-auto w-fit mb-4">
                <Target className="w-3.5 h-3.5" /> Everything you need
              </div>
              <h2 className="text-4xl md:text-6xl font-heading text-foreground mb-4">
                Built For <span className="text-gradient">Results</span>
              </h2>
              <p className="text-muted-foreground text-lg max-w-xl mx-auto">
                Powerful tools designed to help you reach your fitness goals faster.
              </p>
            </motion.div>

            <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {features.map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  onClick={() => {
                    if (feature.title === "Find Recipes") navigate("/recipes");
                    /*else if (feature.title === "Calorie Tracker") navigate("/scan");*/
                    else if (feature.title === "Workout Plans") navigate("/workouts");
                    else navigate("/");
                  }}
                  className="glass-card p-8 text-center group cursor-pointer"
                >
                  <div className={`w-14 h-14 rounded-2xl mx-auto mb-5 flex items-center justify-center transition-transform group-hover:scale-110 ${
                    feature.color === "text-primary" 
                      ? "bg-primary/10 text-primary" 
                      : "bg-accent/10 text-accent"
                  }`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-heading text-foreground mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border/30 py-8">
          <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
            <span className="text-xs text-muted-foreground">© 2026 FornFix. All rights reserved.</span>
            <span className="text-xs text-muted-foreground">Built with &lt;3</span>
          </div>
        </footer>
      </div>
      <BottomNav />
    </>
  );
};

export default Index;