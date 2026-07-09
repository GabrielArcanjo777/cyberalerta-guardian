# CyberAlerta Guardian - Frontend

Next.js + TypeScript + Tailwind frontend for the CyberAlerta Guardian demo.

How to run (locally):

1. Install dependencies in `frontend`:

```bash
cd frontend
npm install
```

2. Run dev server:

```bash
npm run dev
```

Point to backend: set `NEXT_PUBLIC_API_URL` environment variable (defaults to `http://localhost:8000`). Example:

```bash
# Windows PowerShell
$env:NEXT_PUBLIC_API_URL = 'http://localhost:8000'
npm run dev
```

Which pages work:
- `/` Home
- `/before-pix` Before action analyzer (calls POST /analyze or uses mock)
- `/simulator` Scenario simulator (navigates to analyzer)
- `/recovery` Recovery Mode (calls POST /recovery or uses mock)
- `/whatsapp-setup` Pareamento do WhatsApp (Evolution) via QR

Notes and pendências:
- You must run `npm install` to install Next/Tailwind. This repo adds the scaffolding but does not install dependencies.
- Styling uses Tailwind; ensure `tailwindcss` is installed and configured.
- The frontend will call the backend at `NEXT_PUBLIC_API_URL` and will fallback to mock data if the API is not available.
- Accessibility and more polished UI adjustments can be added in subsequent sprints.
