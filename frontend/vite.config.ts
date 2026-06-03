import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  cacheDir: "/tmp/.vite",
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: true,
  },
});
