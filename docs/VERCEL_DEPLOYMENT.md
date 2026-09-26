# IDEAIL ERP — Vercel deployment

## What runs on Vercel

Vercel serves the Vue/Vite frontend from `frontend/dist`.

The Frappe/ERPNext backend remains a separate production service. This is intentional: Frappe production requires its own web process plus database, Redis, workers/scheduler and reverse proxy. See the Frappe production documentation.

## Vercel project

- Repository: `tayebkedadouche09-a11y/ideal-ERP`
- Root Directory: repository root
- Framework: Vite
- Install Command: `npm ci --prefix frontend`
- Build Command: `npm run build --prefix frontend`
- Output Directory: `frontend/dist`

These settings are already committed in `vercel.json`.

## Required environment variable

Set this in Vercel for Production, Preview and Development:

`FRAPPE_BACKEND_URL=https://YOUR-FRAPPE-SITE.example.com`

Do not put the backend URL in client-side `VITE_*` variables. The Vercel function proxy reads the server-only variable and forwards API, login, desk, file and relevant Frappe asset requests.

## Login / API flow

Browser -> Vercel SPA -> Vercel proxy -> Frappe/ERPNext.

The proxy preserves the Frappe session cookie, forwards request headers/body, and rewrites absolute backend redirects back to the Vercel origin.

## Backend production gate

Before connecting the production frontend, the Frappe site must pass:

`bench migrate`
`bench build`
`bench restart`

Then verify login, permissions, Project/BOQ, procurement, stock, invoices, payments, IPC/retention and Project 360 against the real ERPNext database.

## Important

Deploying this repository to Vercel does not turn Frappe/ERPNext itself into a Vercel runtime. The Vercel project is the frontend/proxy edge; the ERP backend must remain on Frappe Cloud or a suitable server/container platform.
