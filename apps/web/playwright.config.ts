import path from "node:path";

import { defineConfig, devices } from "@playwright/test";

const nextCli = path.resolve("node_modules/next/dist/bin/next");
const nextCommand = `"${process.execPath}" "${nextCli}"`;

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  webServer: {
    command:
      process.env.ATLAS_PROD_SERVER === "1"
        ? `${nextCommand} build --webpack && ${nextCommand} start`
        : `${nextCommand} dev --webpack`,
    url: "http://127.0.0.1:3000",
    reuseExistingServer: process.env.ATLAS_PROD_SERVER !== "1" && !process.env.CI,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
