// The demo page (demo/: the component on the example map, `npm run dev`) and the component's tests.
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  root: "demo",
  plugins: [svelte(), svelteTesting()],
  server: { host: "127.0.0.1" },
  build: { outDir: "../dist", emptyOutDir: true },
  test: {
    root: ".",
    environment: "jsdom",
    include: ["tests/component/**/*.test.ts"],
    setupFiles: ["tests/component/setup.ts"],
  },
});
