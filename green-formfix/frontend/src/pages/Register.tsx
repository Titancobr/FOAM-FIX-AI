// src/pages/Register.tsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff, Dumbbell, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import heroImg from "@/assets/hero-fitness.jpg";
import axios from "axios";

const Register = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({ title: "Please fill all fields", variant: "destructive" });
      return;
    }

    setIsLoading(true);
    
    try {
      // ✅ Sending only email and password to match your FastAPI UserSchema
      const response = await axios.post("http://127.0.0.1:8000/register", {
        email: email,
        password: password,
      });

      toast({ title: "Account created! 🎉 Please log in." });
      navigate("/login");
    } catch (error: any) {
      toast({ 
        title: "Registration Failed", 
        description: error.response?.data?.detail || "Something went wrong",
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left - Image */}
      <div className="hidden lg:flex lg:w-1/2 relative">
        <img src={heroImg} alt="Fitness" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 gradient-overlay-right" />
        <div className="absolute bottom-12 left-12 z-10">
          <h1 className="font-display text-7xl text-foreground leading-none">
            START<br />
            <span className="text-primary">TODAY</span>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg max-w-sm">
            Your AI-powered fitness companion
          </p>
        </div>
      </div>

      {/* Right - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md space-y-8"
        >
          <div className="text-center lg:text-left">
            <div className="flex items-center gap-2 justify-center lg:justify-start mb-6">
              <Dumbbell className="h-8 w-8 text-primary" />
              <span className="font-display text-3xl text-foreground">FORMFIX</span>
            </div>
            <h2 className="font-display text-4xl text-foreground">CREATE ACCOUNT</h2>
            <p className="text-muted-foreground mt-1">Begin your fitness transformation</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-muted-foreground">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="bg-secondary border-border h-12 text-foreground placeholder:text-muted-foreground focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-muted-foreground">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="bg-secondary border-border h-12 text-foreground placeholder:text-muted-foreground focus:ring-primary pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground disabled:opacity-50"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full h-12 bg-primary text-primary-foreground font-semibold text-lg hover:bg-primary/90"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          <p className="text-center text-muted-foreground">
            Already have an account?{" "}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Sign In
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Register;