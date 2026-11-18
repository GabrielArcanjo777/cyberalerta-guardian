import {defineConfig, devices} from '@playwright/test'

const CI = !!process.env.CI
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:3000'
const API_URL = process.env.PLAYWRIGHT_API_URL ?? 'http://127.0.0.1:8000'

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: {timeout: 5_000},
  fullyParallel: true,
  forbidOnly: CI,
  retries: CI ? 2 : 0,
  workers: CI ? 2 : undefined,
  reporter: CI
    ? [['github'], ['html', {open: 'never'}]]
    : [['list'], ['html', {open: 'never'}]],
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {...devices['Desktop Chrome']},
    },
  ],
  webServer: [
    {
      // `python -m uvicorn` funciona em Windows e Linux; o caminho antigo
      // (./venv/Scripts/python) só existia no Windows e quebrava no CI.
      command: 'python -m uvicorn main:app --host 127.0.0.1 --port 8000',
      cwd: '../backend',
      url: `${API_URL}/health`,
      reuseExistingServer: !CI,
      timeout: 60_000,
    },
    {
      command: 'npm run dev -- -p 3000',
      url: BASE_URL,
      reuseExistingServer: !CI,
      timeout: 120_000,
    },
  ],
})
