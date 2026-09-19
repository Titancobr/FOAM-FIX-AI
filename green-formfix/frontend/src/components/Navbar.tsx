// src/components/Navbar.tsx
import { Link, useLocation } from "react-router-dom";
import { Dumbbell, Sparkles, User } from "lucide-react";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const Navbar = () => {
  const location = useLocation();
  const path = location.pathname;

  const [userName, setUserName] = useState<string | null>(null);

  useEffect(() => {
    const userStr = localStorage.getItem("fitUser");
    if (userStr) {
      const user = JSON.parse(userStr);
      const name = user.name || user.email.split("@")[0];
      setUserName(name);
    } else {
      setUserName(null);
    }
  }, [location]);

  const links = [
    { to: "/", label: "Home" },
    { to: "/workouts", label: "Workouts" },
    { to: "/recipes", label: "Recipes" },
  ];

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="nav-glass fixed left-0 right-0 top-0 z-50 flex items-center justify-between px-4 py-4 md:px-10"
    >
      <Link to="/" className="flex items-center gap-3 hover-lift">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-primary/25 bg-primary/10 shadow-[0_0_35px_rgba(14,165,233,0.18)]">
          <Dumbbell className="h-5 w-5 text-primary" />
        </div>
        <div>
          <span className="font-heading text-2xl uppercase tracking-wider text-foreground leading-none">
            FORM<span className="text-gradient">FIX</span>
          </span>
          <div className="mt-1 hidden items-center gap-1 text-[10px] uppercase tracking-[0.28em] text-primary/70 md:flex">
            <Sparkles className="h-3 w-3" />
            Move better daily
          </div>
        </div>
      </Link>

      <div className="hidden items-center gap-2 rounded-full border border-white/8 bg-white/5 p-1.5 backdrop-blur-xl md:flex">
        {links.map((link) => (
          <Link
            key={link.label}
            to={link.to}
            className={`relative rounded-full px-4 py-2 text-sm font-medium transition-colors duration-300 hover:text-primary ${
              path === link.to ? "text-primary" : "text-foreground/70"
            }`}
          >
            {path === link.to ? (
              <motion.span
                layoutId="desktop-nav-pill"
                className="absolute inset-0 rounded-full bg-primary/12"
                transition={{ type: "spring", stiffness: 380, damping: 32 }}
              />
            ) : null}
            <span className="relative z-10">{link.label}</span>
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-3">
        {userName ? (
          <Link to="/profile">
            <motion.button
              whileHover={{ y: -1, scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              className={`flex cursor-pointer items-center gap-3 rounded-full border px-4 py-2 transition-all ${
                path === "/profile"
                  ? "border-primary/60 bg-primary/10 shadow-[0_0_30px_rgba(14,165,233,0.12)]"
                  : "border-primary/20 bg-secondary/50 hover:border-primary/40 hover:bg-secondary/70"
              }`}
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/20">
                <User className="h-3.5 w-3.5 text-primary" />
              </div>
              <div className="text-left">
                <span className="block text-[10px] uppercase tracking-[0.24em] text-primary/65">Athlete</span>
                <span className="block text-xs font-mono font-bold uppercase tracking-tight text-primary">
                  {userName}
                </span>
              </div>
            </motion.button>
          </Link>
        ) : (
          <Link to="/login">
            <motion.button whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }} className="btn-primary px-6 py-2.5 text-sm">
              Get Started
            </motion.button>
          </Link>
        )}
      </div>
    </motion.nav>
  );
};

export default Navbar;
