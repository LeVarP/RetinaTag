/**
 * Statistics page - displays global and per-scan statistics.
 * Shows aggregated metrics and completion progress.
 */

import { useQuery } from '@tanstack/react-query';
import { Fragment, useState } from 'react';
import { api } from '@/services/api';
import { Link } from 'react-router-dom';
import ProgressBar from '@/components/ProgressBar';
import styles from './StatsPage.module.css';

function StatsPage() {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

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

  const toggleExpanded = (scanId: string) => {
    setExpanded((prev) => ({ ...prev, [scanId]: !prev[scanId] }));
  };

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
          <div className={styles.statLabel}>Not healthy</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_not_necessary_healthy}</div>
          <div className={styles.statLabel}>Not necessarily healthy</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>{globalStats.total_unlabeled}</div>
          <div className={styles.statLabel}>Unlabeled (empty all fields)</div>
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
            <div className={styles.tableCell}>Not healthy</div>
            <div className={styles.tableCell}>Not necessarily</div>
            <div className={styles.tableCell}>Cyst+</div>
            <div className={styles.tableCell}>Hard Exudate+</div>
            <div className={styles.tableCell}>SRF+</div>
            <div className={styles.tableCell}>PED+</div>
            <div className={styles.tableCell}>Progress</div>
            <div className={styles.tableCell}>Details</div>
            <div className={styles.tableCell}>Open</div>
          </div>

          {scans.map((scan) => {
            const isExpanded = !!expanded[scan.scan_id];
            return (
              <Fragment key={scan.scan_id}>
                <div className={styles.tableRow}>
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
                  <div className={styles.tableCell}>{scan.stats.not_necessary_healthy}</div>
                  <div
                    className={`${styles.tableCell} ${scan.stats.cyst_positive > 0 ? styles.markerPositive : ''}`}
                  >
                    {scan.stats.cyst_positive}
                  </div>
                  <div
                    className={`${styles.tableCell} ${scan.stats.hard_exudate_positive > 0 ? styles.markerPositive : ''}`}
                  >
                    {scan.stats.hard_exudate_positive}
                  </div>
                  <div
                    className={`${styles.tableCell} ${scan.stats.srf_positive > 0 ? styles.markerPositive : ''}`}
                  >
                    {scan.stats.srf_positive}
                  </div>
                  <div
                    className={`${styles.tableCell} ${scan.stats.ped_positive > 0 ? styles.markerPositive : ''}`}
                  >
                    {scan.stats.ped_positive}
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
                    <button
                      className={styles.expandButton}
                      onClick={() => toggleExpanded(scan.scan_id)}
                    >
                      {isExpanded ? 'Hide' : 'Show'}
                    </button>
                  </div>
                  <div className={styles.tableCell}>
                    <Link to={`/scan/${scan.scan_id}`} className={styles.link}>
                      View
                    </Link>
                  </div>
                </div>
                {isExpanded && (
                  <div className={styles.expandedRow}>
                    <div className={styles.detailsPanel}>
                      <div className={styles.detailsBlock}>
                        <h4>Health Summary</h4>
                        <div className={styles.detailsGrid}>
                          <div>Healthy: <strong>{scan.stats.healthy}</strong></div>
                          <div>Not healthy: <strong>{scan.stats.unhealthy}</strong></div>
                          <div>Not necessarily healthy: <strong>{scan.stats.not_necessary_healthy}</strong></div>
                        </div>
                      </div>
                      <div className={styles.detailsBlock}>
                        <h4>Pathology Breakdown</h4>
                        <div className={styles.detailsGrid}>
                          <div>Cyst: +{scan.stats.cyst_positive} / 0:{scan.stats.cyst_negative} / empty:{scan.stats.cyst_empty}</div>
                          <div>Hard exudate: +{scan.stats.hard_exudate_positive} / 0:{scan.stats.hard_exudate_negative} / empty:{scan.stats.hard_exudate_empty}</div>
                          <div>SRF: +{scan.stats.srf_positive} / 0:{scan.stats.srf_negative} / empty:{scan.stats.srf_empty}</div>
                          <div>PED: +{scan.stats.ped_positive} / 0:{scan.stats.ped_negative} / empty:{scan.stats.ped_empty}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default StatsPage;
