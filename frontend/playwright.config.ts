import {defineConfig, devices} from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 15000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {...devices['Desktop Chrome']},
    },
  ],
  webServer: [
    {
      command: 'cd ../backend && ./venv/Scripts/python -m uvicorn main:app --host 0.0.0.0 --port 8000',
      port: 8000,
      reuseExistingServer: true,
      timeout: 15000,
    },
    {
      command: 'npm run dev -- -p 3000',
      port: 3000,
      reuseExistingServer: true,
      timeout: 30000,
    },
  ],
})
