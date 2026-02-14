import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/services/api';

vi.mock('@/services/api', () => ({
  api: {
    getAuthStatus: vi.fn(),
  },
}));

function renderWithAuth(authStatus: { authenticated: boolean; user: any }) {
  (api.getAuthStatus as ReturnType<typeof vi.fn>).mockResolvedValue(authStatus);

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <div>Protected Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('ProtectedRoute', () => {
  it('renders children when authenticated', async () => {
    renderWithAuth({
      authenticated: true,
      user: { id: 1, username: 'admin', is_active: true, is_admin: true, created_at: '' },
    });
    expect(await screen.findByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', async () => {
    renderWithAuth({ authenticated: false, user: null });
    expect(await screen.findByText('Login Page')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    // Make getAuthStatus hang
    (api.getAuthStatus as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}));

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AuthProvider>
            <ProtectedRoute>
              <div>Protected</div>
            </ProtectedRoute>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
