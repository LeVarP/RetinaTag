# RetinaTag Frontend

React + TypeScript client for RetinaTag.

## Local Run

```bash
cd frontend
npm install
npm run dev
```

Vite URL: `http://localhost:5173`

In Docker deployment, the app is served by nginx on `http://localhost` (port 80).

## UI Capabilities

- Scan dashboard:
  - sortable metrics
  - selectable visible columns
  - sticky `Progress` and `Action` columns
  - horizontal scrolling for wide tables
  - expandable `Details` with full per-B-scan rows
  - `Export CSV` button for per-B-scan export
- Labeling view:
  - health status actions (`Healthy`, `Not healthy`)
  - pathology toggles (`Cyst`, `Hard exudate`, `SRF`, `PED`)
  - `Unlabel` action (clear health and pathology fields)
  - `Set all pathologies = 0` action (without auto-marking healthy)
  - `⚙️ Configure hotkeys` shortcut button to `/profile#hotkeys`
- Health semantics in UI:
  - `Healthy` (`healthy=1`)
  - `Not healthy` (`healthy=0`)
  - `Not necessarily healthy` (`healthy=null`)
  - `Unlabeled` only when all marker fields are `null`
- Pathology-positive values are emphasized in tables (`>0` -> bold style).
- Cookie consent banner is shown once; app uses auth cookies only (no analytics tracking cookies).

## Default Hotkeys

- Navigation:
  - `ArrowLeft` -> previous B-scan
  - `ArrowRight` -> next B-scan
- Health:
  - `A` -> Healthy
  - `S` -> Not healthy
- Pathology toggles:
  - `1` -> Cyst
  - `2` -> Hard exudate
  - `3` -> SRF
  - `4` -> PED
- Bulk pathology action:
  - `0` -> Set all pathologies to `0`

All of these are configurable in `/profile`.

## API Layer

`src/services/api.ts` wraps backend endpoints.

Main calls:
- `getScans`, `getGlobalStats`, `getScanStats`
- `getBScan`, `getScanBScans`
- `updateHealth`, `updatePathology`, `clearLabel`
- `downloadBScansCsv`
- auth and user settings APIs

## Structure

```text
frontend/src/
├── components/
├── context/
├── hooks/
├── pages/
├── services/
├── styles/
└── types/
```

## Commands

```bash
npm run dev
npm run build
npm run preview
npm run lint
npm test
```

## Environment

Optional `frontend/.env`:

```env
VITE_API_BASE_URL=/api/v1
```
