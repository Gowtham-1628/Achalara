# CLAUDE.md — Frontend

This file provides guidance to Claude Code when working in `frontend/`.
Read the root `../CLAUDE.md` first for shared context (project overview, Sleeve model, monorepo layout).

## Stack

- **Framework:** React 18 + TypeScript (Vite)
- **API client:** Generated from `../openapi.yaml` — do not handwrite API types
- **State:** TBD (Zustand preferred for simplicity; Redux if scope demands it)
- **Routing:** React Router v6
- **Charts:** Recharts (MWR/TWR timeseries, monthly return bars)
- **Styling:** Tailwind CSS
- **HTTP:** Fetch / Axios with typed client generated from `../openapi.yaml`
- **Testing:** Vitest + React Testing Library
- **Lint/format:** ESLint + Prettier

## API Client

The backend API is fully documented in `../openapi.yaml`. Generate a typed client before writing any fetch calls:

```bash
cd frontend
npx openapi-typescript ../openapi.yaml -o src/api/schema.d.ts
# or use openapi-generator-cli for a full client
```

Never hardcode endpoint paths or response shapes — derive them from the generated types.

## Key Concepts (from the shared Sleeve model)

- Every trade belongs to a **Sleeve** (not directly to an Account or Strategy).
- Navigation hierarchy: **Client → Account → Sleeve** — the UI must follow this nesting.
- **Strategy** is a global definition; it appears in sleeve detail but is not the parent in the nav tree.
- Performance endpoints return `{ level, id, name, summary, timeseries, children }` — `children` is the next level down (client → accounts, account → sleeves, strategy → sleeves).
- All IDs are UUID strings. Never assume numeric IDs in URL params or state.

## Folder Structure (target)

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── schema.d.ts        # generated from ../openapi.yaml — do not edit manually
│   │   └── client.ts          # typed fetch wrappers
│   ├── components/            # shared UI components (charts, tables, forms)
│   ├── pages/
│   │   ├── clients/           # client list + detail
│   │   ├── accounts/          # account detail
│   │   ├── sleeves/           # sleeve detail, positions, performance
│   │   ├── strategies/        # strategy list + performance roll-up
│   │   └── admin/             # import, sync logs, sync-config management
│   ├── hooks/                 # data-fetching hooks (useClient, useSleeve, etc.)
│   ├── utils/
│   └── main.tsx
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Conventions

- **Typed everything** — no `any`. All API response shapes come from the generated schema.
- **Pages are thin** — delegate data-fetching to hooks, rendering to components.
- **No hardcoded API base URL** — read from `import.meta.env.VITE_API_BASE_URL` (default: `http://localhost:8000`).
- **Never bypass the generated API types** — if a response shape is wrong, fix `../openapi.yaml` and regenerate.
- **Performance data is not averaged** — the backend merges trade flows and returns a single MWR/TWR; do not average child returns in the UI.

## Dev Setup (once scaffolded)

```bash
cd frontend
npm install
npm run dev          # Vite dev server on http://localhost:5173
npm run build        # production build
npm run test         # Vitest
```

Ensure the backend is running on port 8000 (`backend/infra.sh up -d`) before starting the dev server.

## What "Done" Looks Like

- Component renders real data from the API, not mock/placeholder data
- All IDs flow through URL params (React Router) — no global state for navigation context
- No `any` types; no hardcoded API paths
- Tests cover the happy path and at least one error state
- Works with the Bruno collection's happy-path flow as the data source
