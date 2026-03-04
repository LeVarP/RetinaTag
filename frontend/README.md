# RetinaTag Frontend

React + TypeScript client for OCT B-scan labeling.

## Quick Start

```bash
npm install
npm run dev
```

App URL: http://localhost:5173

## Current Features

- Keyboard-first labeling and navigation
- Tri-state health display:
  - `Healthy`
  - `Not healthy`
  - `Not necessarily healthy`
- Pathology markers (`Cyst`, `Hard exudate`, `SRF`, `PED`)
- Configurable hotkeys (profile page)
- Labeling page button: `Configure hotkeys`
- Scan table with:
  - column visibility toggles
  - horizontal scroll for wide tables
  - sticky `Progress` and `Action` columns
  - expandable `Details` with per-B-scan rows
- CSV export button (`Export CSV`) for per-B-scan dataset

## Keyboard Defaults

- Navigation:
  - `ArrowLeft` previous frame
  - `ArrowRight` next frame
- Health labels:
  - `A` healthy
  - `S` not healthy
- Pathology toggles:
  - `1` cyst
  - `2` hard exudate
  - `3` SRF
  - `4` PED

All keys are editable in `/profile`.

## API Usage

`src/services/api.ts` wraps backend API.

Main calls:
- `api.getScans()`
- `api.getScanStats(scanId)`
- `api.getBScan(scanId, index)`
- `api.getScanBScans(scanId)`
- `api.updateHealth(bscanId, { healthy })`
- `api.updatePathology(bscanId, patch)`
- `api.downloadBScansCsv()`

## Project Structure

```
frontend/src/
├── components/
├── context/
├── hooks/
├── pages/
├── services/
├── styles/
└── types/
```

## Scripts

```bash
npm run dev
npm run build
npm run preview
npm run lint
npm test
```

## Environment

Optional `.env`:

```env
VITE_API_BASE_URL=/api/v1
```

## Deployment Note

In the provided Docker stack:
- frontend is published on port `80`
- backend is internal-only (not directly exposed)
- nginx does not enforce source-IP ACL by default

This means frontend can be reached from LAN and external networks if host routing/firewall/NAT allows inbound `80/tcp`.
