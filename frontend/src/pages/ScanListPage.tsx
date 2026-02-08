/**
 * Scan list page - displays all scans with progress indicators.
 * Uses TanStack Query for data fetching.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import ScanCard from '@/components/ScanCard';
import styles from './ScanListPage.module.css';

function ScanListPage() {
  const {
    data: scans,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['scans'],
    queryFn: api.getScans,
  });

  if (isLoading) {
    return (
      <div className="container">
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading scans...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container">
        <div className={styles.error}>
          <h2>Error Loading Scans</h2>
          <p>{error instanceof Error ? error.message : 'Unknown error occurred'}</p>
          <button
            className={styles.retryButton}
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!scans || scans.length === 0) {
    return (
      <div className="container">
        <div className={styles.empty}>
          <h2>No Scans Found</h2>
          <p>Import OCT scans using the CLI tool to get started.</p>
          <pre className={styles.code}>
            python scripts/import_scan.py --scan-id SCAN_001 --source /path/to/scans/
          </pre>
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const totalScans = scans.length;
  const completedScans = scans.filter((s) => s.stats.completion_percentage === 100).length;
  const inProgressScans = scans.filter(
    (s) => s.stats.labeled_bscans > 0 && s.stats.completion_percentage < 100
  ).length;

  return (
    <div className="container">
      <div className={styles.header}>
        <h2>OCT Scans</h2>
        <div className={styles.summary}>
          <span className={styles.summaryItem}>
            Total: <strong>{totalScans}</strong>
          </span>
          <span className={styles.summaryItem}>
            Completed: <strong>{completedScans}</strong>
          </span>
          <span className={styles.summaryItem}>
            In Progress: <strong>{inProgressScans}</strong>
          </span>
        </div>
      </div>

      <div className={styles.grid}>
        {scans.map((scan) => (
          <ScanCard key={scan.scan_id} scan={scan} />
        ))}
      </div>
    </div>
  );
}

export default ScanListPage;
