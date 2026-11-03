import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "./" so that the built files also work from any sub folder
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { port: 5173 },
});
