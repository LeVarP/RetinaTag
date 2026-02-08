# OCT B-Scan Labeler - Frontend

React + TypeScript frontend for OCT B-scan labeling application. Provides keyboard-first interface for rapid medical image labeling.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Access at http://localhost:5173

## Features

- **Keyboard-First Navigation**: Arrow keys + A/S hotkeys (zero mouse dependency)
- **Optimistic UI Updates**: Instant feedback on label changes
- **Smart Prefetching**: Background loading of next 10 frames
- **Progress Tracking**: Real-time statistics and completion indicators
- **Responsive Design**: Works on desktop and tablet

## Technology Stack

- **Framework**: React 18
- **Language**: TypeScript (strict mode)
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: TanStack Query v5
- **Styling**: CSS Modules (NO inline styles)
- **Testing**: Vitest + Playwright

## Project Structure

```
frontend/src/
├── pages/           # Page components
│   ├── ScanListPage.tsx      # Scan list with progress
│   ├── LabelingPage.tsx      # Main labeling interface
│   └── StatsPage.tsx         # Statistics dashboard
├── components/      # Reusable UI components
│   ├── ScanCard.tsx          # Scan card with stats
│   ├── ProgressBar.tsx       # Progress visualization
│   ├── BScanViewer.tsx       # Image viewer
│   ├── NavigationControls.tsx
│   └── LabelingControls.tsx
├── hooks/           # Custom React hooks
│   ├── useKeyboardNav.ts     # Keyboard event handling
│   ├── usePrefetch.ts        # Image prefetching
│   └── useLabeling.ts        # Label mutations
├── services/        # External services
│   └── api.ts                # Axios API client
├── types/           # TypeScript types
│   └── index.ts              # All type definitions
└── styles/          # Global styles
    └── global.css            # CSS variables, base styles
```

## Development

### Available Scripts

```bash
npm run dev          # Start dev server (port 5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run format       # Run Prettier
npm run typecheck    # TypeScript type checking
npm test             # Run unit tests (Vitest)
npm run test:e2e     # Run E2E tests (Playwright)
```

### Code Style Rules

**CRITICAL**:
- ❌ **NO inline styles** - use CSS Modules only
- ✅ One component per file
- ✅ All comments in English
- ✅ TypeScript strict mode
- ✅ Every file starts with docstring

**Example**:
```tsx
// ❌ WRONG - inline styles
<div style={{ color: 'red' }}>Hello</div>

// ✅ CORRECT - CSS Module
import styles from './MyComponent.module.css';
<div className={styles.error}>Hello</div>
```

## API Integration

### API Client (`services/api.ts`)

```typescript
import { api } from '@/services/api';

// Fetch scans
const scans = await api.getScans();

// Get B-scan
const bscan = await api.getBScan(scanId, index);

// Update label
await api.updateLabel(bscanId, { label: 1 }); // 1=healthy, 2=unhealthy

// Get preview URL
const url = api.getPreviewUrl(scanId, index);
```

### React Query Integration

```typescript
// Fetch with caching
const { data, isLoading } = useQuery({
  queryKey: ['scans'],
  queryFn: api.getScans,
});

// Mutation with optimistic updates
const mutation = useMutation({
  mutationFn: (label) => api.updateLabel(bscanId, { label }),
  onMutate: async (newLabel) => {
    // Optimistic update
    queryClient.setQueryData(['bscan', id], { ...old, label: newLabel });
  },
});
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` | Previous B-scan |
| `→` | Next B-scan |
| `A` | Label as Healthy |
| `S` | Label as Unhealthy |

**Auto-advance**: After labeling, automatically moves to next frame (respects navigation mode).

## Navigation Modes

1. **Sequential**: Navigate through all B-scans (0 → 1 → 2 → ... → 349)
2. **Unlabeled Only**: Skip labeled B-scans, jump to next unlabeled

Toggle mode with button in NavigationControls component.

## Custom Hooks

### useKeyboardNav

Handles global keyboard events for navigation and labeling.

```typescript
useKeyboardNav({
  onNext: () => console.log('Next'),
  onPrev: () => console.log('Previous'),
  onLabelHealthy: () => console.log('Label: Healthy'),
  onLabelUnhealthy: () => console.log('Label: Unhealthy'),
  enabled: true,
});
```

### usePrefetch

Prefetches next K images in background using Image API.

```typescript
usePrefetch({
  scanId: 'ABC123',
  currentIndex: 42,
  totalBScans: 350,
  prefetchCount: 10,
  enabled: true,
});
```

### useLabeling

Manages label mutations with optimistic UI and auto-advance.

```typescript
const { labelAsHealthy, labelAsUnhealthy, isLoading } = useLabeling({
  scanId: 'ABC123',
  bscanId: 123,
  onSuccess: () => console.log('Auto-advancing...'),
});
```

## Component Patterns

### CSS Modules

Every component has its own CSS Module:

```
MyComponent.tsx
MyComponent.module.css
```

Usage:
```tsx
import styles from './MyComponent.module.css';

function MyComponent() {
  return <div className={styles.container}>...</div>;
}
```

### Loading States

```tsx
if (isLoading) {
  return (
    <div className={styles.loading}>
      <div className={styles.spinner} />
      <p>Loading...</p>
    </div>
  );
}
```

### Error Handling

```tsx
if (isError) {
  return (
    <div className={styles.error}>
      <h2>Error</h2>
      <p>{error.message}</p>
      <button onClick={retry}>Retry</button>
    </div>
  );
}
```

## TypeScript Types

All types defined in `src/types/index.ts`:

```typescript
export interface BScan {
  id: number;
  scan_id: string;
  bscan_index: number;
  label: Label;
  preview_url: string | null;
  prev_index: number | null;
  next_index: number | null;
  next_unlabeled_index: number | null;
}

export enum Label {
  Unlabeled = 0,
  Healthy = 1,
  Unhealthy = 2,
}
```

## Build & Deployment

### Production Build

```bash
npm run build
# Output: dist/
```

### Docker Build

```bash
docker build -f docker/frontend.Dockerfile -t oct-labeler-frontend .
```

### Environment Variables

Create `.env` file:

```env
VITE_API_BASE_URL=/api/v1
```

In production, API requests go to `/api/v1` which nginx proxies to backend.

## Testing

### Unit Tests (Vitest)

```bash
npm test
```

Test files: `*.test.ts`, `*.test.tsx`

### E2E Tests (Playwright)

```bash
npm run test:e2e
```

Test files: `tests/e2e/*.spec.ts`

## Performance Optimization

1. **Code Splitting**: Lazy load routes
2. **React Query Caching**: 5-minute stale time
3. **Image Prefetching**: Next 10 frames
4. **Optimistic Updates**: Instant UI feedback
5. **CSS Modules**: Scoped styles, tree-shakeable

## Troubleshooting

### Port already in use
```bash
# Change port in vite.config.ts
server: { port: 3000 }
```

### API connection refused
Check `VITE_API_BASE_URL` in `.env` and ensure backend is running.

### Type errors
```bash
npm run typecheck
```

### Build fails
```bash
rm -rf node_modules dist
npm install
npm run build
```

---

For more information, see the [root README](../README.md).
