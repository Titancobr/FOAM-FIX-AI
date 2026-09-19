import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Apple, ArrowRight, Sparkles, Target, TrendingUp, Zap } from "lucide-react";
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
  { value: "Live", label: "Form Coach" },
];

const Index = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-background">
        <section className="relative flex min-h-screen items-center justify-center overflow-hidden pt-20">
          <div
            className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat scale-[1.03]"
            style={{ backgroundImage: `url(${heroImg})` }}
          />
          <div className="absolute inset-0 z-10 bg-black/50 bg-gradient-to-b from-background/20 via-background/60 to-background" />
          <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_top,rgba(14,165,233,0.18),transparent_36%),radial-gradient(circle_at_bottom_right,rgba(249,115,22,0.12),transparent_28%)]" />

          <div className="relative z-20 mx-auto grid max-w-6xl gap-12 px-5 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
            <div className="text-center lg:text-left">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="stat-badge mx-auto mb-6 w-fit bg-white/10 backdrop-blur-md lg:mx-0"
              >
                <Zap className="h-3.5 w-3.5" /> Transform your body with science-backed programs
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
                className="mb-6 text-6xl leading-[0.9] text-white drop-shadow-2xl md:text-8xl"
              >
                TRAIN SMARTER.
                <br />
                <span className="text-gradient">MOVE CLEANER.</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.15 }}
                className="mx-auto mb-8 max-w-2xl text-lg text-white/90 drop-shadow-md md:text-xl lg:mx-0"
              >
                Your workouts, meals, rep counting, and form corrections live in one smooth coaching experience.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.25 }}
                className="flex flex-col items-center gap-3 sm:flex-row lg:justify-start"
              >
                <button onClick={() => navigate("/workouts")} className="btn-primary inline-flex items-center gap-2">
                  Start Training
                  <ArrowRight className="h-4 w-4" />
                </button>
                <button onClick={() => navigate("/recipes")} className="btn-outline inline-flex items-center gap-2">
                  Explore Meals
                  <Sparkles className="h-4 w-4" />
                </button>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.65, delay: 0.2 }}
              className="glass-card shimmer grid gap-4 p-5"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.28em] text-primary/75">Daily flow</p>
                  <h3 className="mt-1 text-3xl text-foreground">One app, full routine</h3>
                </div>
                <div className="rounded-2xl border border-primary/20 bg-primary/10 px-3 py-2 text-right">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-primary/70">Coach mode</p>
                  <p className="text-lg font-semibold text-primary">Active</p>
                </div>
              </div>
              <div className="grid gap-3">
                {[
                  "Choose a split and open your next day instantly.",
                  "Track form with live rep counting and posture cues.",
                  "Log meals, scan calories, and stay inside your target.",
                ].map((item, index) => (
                  <motion.div
                    key={item}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.35 + index * 0.08 }}
                    className="flex items-start gap-3 rounded-2xl border border-white/8 bg-black/15 px-4 py-3"
                  >
                    <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">
                      {index + 1}
                    </div>
                    <p className="text-sm text-white/85">{item}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        <section className="-mt-20 px-5 pb-8">
          <div className="mx-auto grid max-w-6xl grid-cols-2 gap-3 md:grid-cols-4">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: index * 0.06 }}
                className="glass-card px-5 py-4 text-center"
              >
                <p className="font-heading text-4xl text-primary">{stat.value}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.22em] text-muted-foreground">{stat.label}</p>
              </motion.div>
            ))}
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

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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
                  whileHover={{ y: -6, scale: 1.01 }}
                  whileTap={{ scale: 0.98 }}
                  className="glass-card group cursor-pointer p-8 text-center"
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
