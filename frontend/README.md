# OCT B-Scan Labeler - Frontend

React + TypeScript frontend for OCT B-scan labeling application.

## Structure

```
frontend/
├── src/
│   ├── main.tsx             # Application entry point
│   ├── App.tsx              # Root component with routing
│   ├── pages/               # Page components
│   │   ├── ScanListPage.tsx
│   │   ├── LabelingPage.tsx
│   │   └── StatsPage.tsx
│   ├── components/          # Reusable UI components
│   │   ├── BScanViewer.tsx
│   │   ├── NavigationControls.tsx
│   │   ├── LabelingControls.tsx
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   │   ├── useKeyboardNav.ts
│   │   ├── usePrefetch.ts
│   │   └── useLabeling.ts
│   ├── services/            # API client and utilities
│   │   └── api.ts
│   ├── types/               # TypeScript type definitions
│   ├── styles/              # CSS Modules (NO inline styles)
│   │   ├── global.css
│   │   └── components/
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── unit/
│   └── e2e/
├── public/                  # Static assets
├── package.json
├── vite.config.ts          # Vite configuration
├── vitest.config.ts        # Vitest configuration
├── playwright.config.ts    # Playwright E2E configuration
└── .env.example            # Environment variables template

## Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your backend URL
```

### 3. Run development server

```bash
npm run dev
```

Application will be available at http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run unit tests with Vitest
- `npm run test:ui` - Run tests with UI
- `npm run test:e2e` - Run E2E tests with Playwright
- `npm run lint` - Lint code with ESLint
- `npm run lint:fix` - Fix linting errors
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run typecheck` - Type check with TypeScript

## Pages

### Scan List Page (`/`)
- Displays all available scans
- Shows progress indicators for each scan
- Links to labeling interface

### Labeling Page (`/scan/:scanId`)
- Main labeling interface
- Keyboard navigation (Arrow keys)
- Hotkey labeling (A = Healthy, S = Unhealthy)
- Auto-advance after labeling
- Prefetching for smooth navigation

### Statistics Page (`/stats`)
- Global statistics dashboard
- Per-scan progress breakdown

## Key Components

### BScanViewer
Displays B-scan images with loading states and label badges.

### NavigationControls
Previous/Next buttons, index display, mode toggle.

### LabelingControls
Healthy/Unhealthy buttons with keyboard shortcut hints.

## Custom Hooks

### useKeyboardNav
Handles keyboard events for navigation and labeling.

### usePrefetch
Implements prefetching strategy for next K images.

### useLabeling
Manages label updates and auto-advance logic.

## Styling

**IMPORTANT**: NO inline styles allowed.

- Use CSS Modules (`.module.css`) for component styles
- Import styles: `import styles from './Component.module.css'`
- Global styles in `src/styles/global.css`

Example:

```tsx
// Component.tsx
import styles from '@/styles/components/Component.module.css'

export const Component = () => (
  <div className={styles.container}>Content</div>
)
```

## Testing

### Unit Tests

Component and hook tests with Vitest + Testing Library:

```bash
npm test
```

### E2E Tests

End-to-end workflow tests with Playwright:

```bash
npm run test:e2e
```

## Code Quality

Lint:

```bash
npm run lint
npm run lint:fix
```

Format:

```bash
npm run format
npm run format:check
```

Type check:

```bash
npm run typecheck
```

## API Integration

The frontend uses Axios with TanStack Query for API communication.

Base URL is configured via `VITE_API_BASE_URL` environment variable.

See `src/services/api.ts` for API client implementation.
