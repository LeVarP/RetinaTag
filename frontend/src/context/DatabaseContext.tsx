import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { setActiveDatabase } from '@/services/api';
import type { DatabaseMode } from '@/types';

const STORAGE_KEY = 'selected_database';

function loadStoredMode(): DatabaseMode {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === 'simple' ? 'simple' : 'original';
}

interface DatabaseContextType {
  activeDatabase: DatabaseMode;
  switchDatabase: (db: DatabaseMode) => void;
}

const DatabaseContext = createContext<DatabaseContextType | null>(null);

export function DatabaseProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [activeDatabase, setActiveDb] = useState<DatabaseMode>(() => {
    const mode = loadStoredMode();
    setActiveDatabase(mode);
    return mode;
  });

  const switchDatabase = useCallback(
    (db: DatabaseMode) => {
      setActiveDatabase(db);
      setActiveDb(db);
      localStorage.setItem(STORAGE_KEY, db);
      queryClient.invalidateQueries();
    },
    [queryClient]
  );

  return (
    <DatabaseContext.Provider value={{ activeDatabase, switchDatabase }}>
      {children}
    </DatabaseContext.Provider>
  );
}

export function useDatabase() {
  const ctx = useContext(DatabaseContext);
  if (!ctx) throw new Error('useDatabase must be used within DatabaseProvider');
  return ctx;
}
