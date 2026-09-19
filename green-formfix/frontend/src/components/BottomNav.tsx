import { Link, useLocation } from "react-router-dom";
import { Dumbbell, Home, ScanLine, UtensilsCrossed } from "lucide-react";
import { motion } from "framer-motion";

const BottomNav = () => {
  const location = useLocation();
  const path = location.pathname;

  const links = [
    { to: "/", icon: Home, label: "Home" },
    { to: "/workouts", icon: Dumbbell, label: "Workouts" },
    { to: "/recipes", icon: UtensilsCrossed, label: "Meals" },
    { to: "/scan", icon: ScanLine, label: "Scan" },
  ];

  return (
    <motion.nav
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45, ease: "easeOut", delay: 0.1 }}
      className="fixed bottom-3 left-3 right-3 z-50 rounded-[28px] border border-white/10 bg-card/80 px-2 py-2 shadow-[0_18px_60px_rgba(0,0,0,0.38)] backdrop-blur-2xl md:left-1/2 md:right-auto md:w-[30rem] md:-translate-x-1/2"
    >
      <div className="mx-auto flex h-16 items-center justify-around">
        {links.map((link) => {
          const isActive = path === link.to;
          return (
            <Link key={link.to} to={link.to} className="relative flex min-w-[68px] items-center justify-center">
              {isActive ? (
                <motion.span
                  layoutId="mobile-nav-pill"
                  className="absolute inset-0 rounded-2xl bg-primary/14"
                  transition={{ type: "spring", stiffness: 400, damping: 34 }}
                />
              ) : null}
              <motion.div
                whileTap={{ scale: 0.94 }}
                className={`relative z-10 flex flex-col items-center gap-1 rounded-2xl px-4 py-2 transition-colors ${
                  isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <link.icon className={`h-5 w-5 ${isActive ? "drop-shadow-[0_0_12px_rgba(14,165,233,0.4)]" : ""}`} />
                <span className="text-[10px] font-semibold uppercase tracking-[0.2em]">{link.label}</span>
              </motion.div>
            </Link>
          );
        })}
      </div>
    </motion.nav>
  );
};

export default BottomNav;
