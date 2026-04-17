import { Link, useLocation, useNavigate } from "react-router-dom";
import { Dumbbell, User, LogOut, ChevronDown } from "lucide-react";
import { useEffect, useState, useRef } from "react";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const path = location.pathname;
  
  const [userName, setUserName] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Check for logged in user
  useEffect(() => {
    const userStr = localStorage.getItem("fitUser");
    if (userStr) {
      const user = JSON.parse(userStr);
      const name = user.name || user.email.split('@')[0];
      setUserName(name);
    } else {
      setUserName(null);
    }
  }, [location]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("fitUser");
    localStorage.removeItem("token"); // Clear JWT too
    setUserName(null);
    setIsMenuOpen(false);
    navigate("/");
  };

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

      <div className="flex items-center gap-4 relative" ref={menuRef}>
        {userName ? (
          <>
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-3 bg-secondary/50 px-4 py-2 rounded-full border border-primary/20 hover:border-primary/40 transition-all cursor-pointer group"
            >
              <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                <User className="h-3.5 w-3.5 text-primary" />
              </div>
              <span className="text-xs font-mono uppercase tracking-tight text-primary font-bold">
                {userName}
              </span>
              <ChevronDown className={`h-3 w-3 text-primary/50 transition-transform duration-300 ${isMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isMenuOpen && (
              <div className="absolute top-full right-0 mt-2 w-48 glass-card border border-white/10 shadow-xl overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="p-2">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors group"
                  >
                    <LogOut className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    <span className="font-medium">Logout Session</span>
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <Link to="/login">
            <button className="btn-primary px-6 py-2.5 text-sm">
              Get Started
            </button>
          </Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;