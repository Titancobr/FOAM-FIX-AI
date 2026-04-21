// src/components/Navbar.tsx
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Dumbbell, User } from "lucide-react";
import { useEffect, useState } from "react";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
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
    <nav className="nav-glass py-4 px-6 md:px-12 flex justify-between items-center z-50 fixed top-0 left-0 right-0">
      <Link to="/" className="flex items-center gap-2 hover-lift">
        <Dumbbell className="h-6 w-6 text-primary" />
        <span className="font-heading text-2xl tracking-wider text-foreground uppercase">
          FORM<span className="text-gradient">FIX</span>
        </span>
      </Link>

      <div className="hidden md:flex items-center gap-8">
        {links.map((link) => (
          <Link
            key={link.label}
            to={link.to}
            className={`text-sm font-medium transition-colors duration-300 hover:text-primary ${
              path === link.to ? "text-primary" : "text-foreground/70"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-4">
        {userName ? (
          <Link to="/profile">
            <button
              className={`flex items-center gap-3 bg-secondary/50 px-4 py-2 rounded-full border transition-all cursor-pointer ${
                path === "/profile"
                  ? "border-primary/60 bg-primary/10"
                  : "border-primary/20 hover:border-primary/40"
              }`}
            >
              <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                <User className="h-3.5 w-3.5 text-primary" />
              </div>
              <span className="text-xs font-mono uppercase tracking-tight text-primary font-bold">
                {userName}
              </span>
            </button>
          </Link>
        ) : (
          <Link to="/login">
            <button className="btn-primary px-6 py-2.5 text-sm">Get Started</button>
          </Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
