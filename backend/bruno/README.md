# PMS API — Bruno Collection

A full Bruno collection for the PMS backend. The folders are numbered so that
**"Run Collection"** executes a coherent happy-path flow and chains IDs automatically:

```
00 Health    → liveness
01 Clients   → create client                       (captures clientId)
02 Accounts  → create account                      (captures accountId)
03 Strategies→ create global strategy (strategyId), create sleeve (sleeveId),
               + sleeve performance/positions/trades
04 Trades    → add BUY/BUY/SELL trades into the sleeve  (captures tradeId)
05 Prices    → set + fetch market prices for the sleeve
06 Admin     → CSV import, sync logs, sync-config CRUD, sheet sync
```

A **Strategy** is a firm-wide definition; a **Sleeve** is that strategy run inside one
account. Trades, positions, prices and sync configs all hang off the **sleeve**.

## Run it

1. Start the stack: `cd backend && ./infra.sh up -d` (app on <http://localhost:8000>).
2. Open this folder (`backend/bruno`) in [Bruno](https://www.usebruno.com/).
3. Select the **Local** environment (top-right).
4. Either run requests top-to-bottom, or use **Run Collection** for the whole flow.

Or headless via the Bruno CLI:

```bash
npm install -g @usebruno/cli
cd backend/bruno
bru run --env Local
```

**Expected CLI result:** all requests pass except **06 Admin / Sync Daily (Sheets)**, which
returns `502` until you supply a real, accessible Google Sheet ID + credentials — it's
included for completeness. To run everything except that one:
`bru run --env Local --exclude "**/Sync Daily*"`.

## How chaining works

Each create request stores the returned `id` into a runtime variable via a
`vars:post-response` block (`clientId`, `accountId`, `strategyId`, `sleeveId`, `configId`).
Later requests reference them as `{{clientId}}`, etc. Re-running is safe — the client
email is randomized per run in a `script:pre-request` so you never hit
"Email already registered".

## Notes

- `05 Prices / Fetch from Webull` will return `status: "partial"` with `fetched: 0`
  unless valid Webull credentials are configured in `.env` — that's expected; the
  request still returns 200.
- `06 Admin / Import Historical` runs in `mode=VALIDATE` (dry run) by default so it
  doesn't write trades. Change the `mode` query param to `IMPORT` to persist.
- `06 Admin / Sync Daily` needs a real Google Sheet ID + credentials; it's included
  for completeness and will error without them.
