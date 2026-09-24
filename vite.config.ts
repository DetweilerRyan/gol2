import { defineConfig } from "vitest/config";

export default defineConfig({
  // Listen on all interfaces so the dev server is reachable through sandbox port publishing.
  server: { host: "0.0.0.0" },
  test: {
    include: ["src/**/*.test.ts"],
    passWithNoTests: true,
  },
});
