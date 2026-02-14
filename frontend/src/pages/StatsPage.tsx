/**
 * Statistics page - displays global and per-scan statistics.
 * Shows aggregated metrics and completion progress.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Link } from 'react-router-dom';
import ProgressBar from '@/components/ProgressBar';
import styles from './StatsPage.module.css';

function StatsPage() {
  const {
    data: globalStats,
    isLoading: statsLoading,
    isError: statsError,
  } = useQuery({
    queryKey: ['globalStats'],
    queryFn: api.getGlobalStats,
  });

  const {
    data: scans,
    isLoading: scansLoading,
    isError: scansError,
  } = useQuery({
    queryKey: ['scans'],
    queryFn: api.getScans,
  });

  if (statsLoading || scansLoading) {
    return (
      <div className="container">
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (statsError || scansError) {
    return (
      <div className="container">
        <div className={styles.error}>
          <h2>Error Loading Statistics</h2>
          <p>Failed to load statistics. Please try again.</p>
        </div>
      </div>
    );
  }

  if (!globalStats || !scans) {
    return null;
  }

  return (
    <div className="container">
      <h2 className={styles.title}>Global Statistics</h2>

      <div className={styles.globalStats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_scans}</div>
          <div className={styles.statLabel}>Total Scans</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_bscans}</div>
          <div className={styles.statLabel}>Total B-scans</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_labeled}</div>
          <div className={styles.statLabel}>Labeled B-scans</div>
        </div>

        <div className={styles.statCard}>
          <div className={`${styles.statValue} ${styles.healthy}`}>
            {globalStats.total_healthy}
          </div>
          <div className={styles.statLabel}>Healthy</div>
        </div>

        <div className={styles.statCard}>
          <div className={`${styles.statValue} ${styles.unhealthy}`}>
            {globalStats.total_unhealthy}
          </div>
          <div className={styles.statLabel}>Unhealthy</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_unlabeled}</div>
          <div className={styles.statLabel}>Unlabeled</div>
        </div>
      </div>

      <div className={styles.overallProgress}>
        <h3>Overall Completion</h3>
        <ProgressBar percentage={globalStats.percent_complete} />
        <p className={styles.progressText}>
          {globalStats.total_labeled} / {globalStats.total_bscans} B-scans labeled
        </p>
      </div>

      <div className={styles.perScanSection}>
        <h3>Per-Scan Statistics</h3>
        <div className={styles.table}>
          <div className={styles.tableHeader}>
            <div className={styles.tableCell}>Scan ID</div>
            <div className={styles.tableCell}>Total</div>
            <div className={styles.tableCell}>Labeled</div>
            <div className={styles.tableCell}>Healthy</div>
            <div className={styles.tableCell}>Unhealthy</div>
            <div className={styles.tableCell}>Progress</div>
            <div className={styles.tableCell}>Actions</div>
          </div>

          {scans.map((scan) => (
            <div key={scan.scan_id} className={styles.tableRow}>
              <div className={styles.tableCell}>
                <strong>{scan.scan_id}</strong>
              </div>
              <div className={styles.tableCell}>{scan.stats.total_bscans}</div>
              <div className={styles.tableCell}>{scan.stats.labeled}</div>
              <div className={`${styles.tableCell} ${styles.healthy}`}>
                {scan.stats.healthy}
              </div>
              <div className={`${styles.tableCell} ${styles.unhealthy}`}>
                {scan.stats.unhealthy}
              </div>
              <div className={`${styles.tableCell} ${styles.progressCell}`}>
                <ProgressBar
                  percentage={scan.stats.percent_complete}
                  showLabel={false}
                />
                <span className={styles.percentage}>
                  {scan.stats.percent_complete.toFixed(1)}%
                </span>
              </div>
              <div className={styles.tableCell}>
                <Link to={`/scan/${scan.scan_id}`} className={styles.link}>
                  View
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StatsPage;
