/**
 * Main App component for OCT B-Scan Labeler.
 * Sets up routing and React Query.
 */

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import ScanListPage from '@/pages/ScanListPage';
import LabelingPage from '@/pages/LabelingPage';
import StatsPage from '@/pages/StatsPage';
import '@/styles/global.css';
import './App.css';

/**
 * React Query client configuration.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <header className="app-header">
            <div className="container">
              <h1>OCT B-Scan Labeler</h1>
              <nav className="app-nav">
                <Link to="/">Scans</Link>
                <Link to="/stats">Statistics</Link>
              </nav>
            </div>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<ScanListPage />} />
              <Route path="/scan/:scanId" element={<LabelingPage />} />
              <Route path="/stats" element={<StatsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>

      {/* React Query DevTools (development only) */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
