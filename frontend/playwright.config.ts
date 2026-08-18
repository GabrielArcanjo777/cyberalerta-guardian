import {defineConfig, devices} from '@playwright/test'

const isCi = Boolean(process.env.CI)

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 0,
  workers: isCi ? 2 : undefined,
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
      // Usa o Python ativo para funcionar tanto em um venv local quanto no CI.
      command: 'cd ../backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000',
      port: 8000,
      reuseExistingServer: true,
      timeout: 15000,
    },
    {
      command: isCi
        ? 'npm run build && npm run start -- -p 3000'
        : 'npm run dev -- -p 3000',
      port: 3000,
      reuseExistingServer: true,
      timeout: 120000,
    },
  ],
})
