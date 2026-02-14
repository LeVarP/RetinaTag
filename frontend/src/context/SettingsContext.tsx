import { createContext, useContext, type ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useAuth } from '@/context/AuthContext';
import type { UserSettings, UserSettingsUpdate } from '@/types';

const DEFAULT_SETTINGS: UserSettings = {
  auto_advance: true,
  hotkey_healthy: 'a',
  hotkey_unhealthy: 's',
  hotkey_next: 'ArrowRight',
  hotkey_prev: 'ArrowLeft',
};

interface SettingsContextType {
  settings: UserSettings;
  isLoading: boolean;
  updateSettings: (updates: UserSettingsUpdate) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['user', 'settings'],
    queryFn: api.getMySettings,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });

  const updateMutation = useMutation({
    mutationFn: api.updateMySettings,
    onSuccess: (updated) => {
      queryClient.setQueryData(['user', 'settings'], updated);
    },
  });

  const updateSettings = async (updates: UserSettingsUpdate) => {
    await updateMutation.mutateAsync(updates);
  };

  return (
    <SettingsContext.Provider
      value={{
        settings: data ?? DEFAULT_SETTINGS,
        isLoading,
        updateSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used within SettingsProvider');
  return ctx;
}
