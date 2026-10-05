import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      "/ai": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/login": "http://127.0.0.1:8000",
      "/register": "http://127.0.0.1:8000",
      "/nutrition": "http://127.0.0.1:8000",
      "/progress": "http://127.0.0.1:8000",
    },
    hmr: {
      overlay: false,
    },
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
