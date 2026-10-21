import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  workers: 1,
  use: {
    baseURL: process.env.TEST_WEB_URL || "http://localhost:3000",
    browserName: "chromium",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  reporter: [["list"], ["html", { open: "never" }]],
});
