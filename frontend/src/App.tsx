/**
 * Main App component for OCT B-Scan Labeler.
 * Sets up routing, auth, settings, and React Query.
 */

import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider, useAuth } from '@/context/AuthContext';
import { SettingsProvider } from '@/context/SettingsContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import CookieConsent from '@/components/CookieConsent';
import ScanListPage from '@/pages/ScanListPage';
import LabelingPage from '@/pages/LabelingPage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
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

function AuthNav() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated) {
    return <Link to="/login">Login</Link>;
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <>
      <Link to="/profile">{user?.username}</Link>
      <button onClick={handleLogout} className="app-nav-button">
        Logout
      </button>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <SettingsProvider>
            <div className="app">
              <header className="app-header">
                <div className="container">
                  <h1>OCT B-Scan Labeler</h1>
                  <nav className="app-nav">
                    <Link to="/">Scans</Link>
                    <AuthNav />
                  </nav>
                </div>
              </header>

              <main className="app-main">
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <ScanListPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/scan/:scanId"
                    element={
                      <ProtectedRoute>
                        <LabelingPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <ProfilePage />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </main>

              <CookieConsent />
            </div>
          </SettingsProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
