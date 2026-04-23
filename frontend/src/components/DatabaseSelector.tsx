import { useState, useRef, useEffect } from 'react';
import { useDatabase } from '@/context/DatabaseContext';
import { DATABASES } from '@/types';
import styles from './DatabaseSelector.module.css';

export function DatabaseSelector() {
  const { activeDatabase, switchDatabase } = useDatabase();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = DATABASES.find((db) => db.id === activeDatabase)!;

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  return (
    <div className={styles.wrapper} ref={ref}>
      <button
        className={`${styles.badge} ${styles[activeDatabase]}`}
        onClick={() => setOpen((o) => !o)}
        title="Switch active database"
        type="button"
      >
        <span className={styles.dot} />
        {current.label}
        <span className={styles.chevron}>{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className={styles.dropdown}>
          {DATABASES.map((db) => (
            <button
              key={db.id}
              className={`${styles.option} ${db.id === activeDatabase ? styles.active : ''}`}
              onClick={() => {
                switchDatabase(db.id);
                setOpen(false);
              }}
              type="button"
            >
              <span className={`${styles.optionDot} ${styles[db.id]}`} />
              <span className={styles.optionText}>
                <span className={styles.optionLabel}>{db.label}</span>
                <span className={styles.optionDesc}>{db.description}</span>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
