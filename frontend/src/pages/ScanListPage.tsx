/**
 * Scan list page - sortable table of all scans with progress.
 */

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import ProgressBar from '@/components/ProgressBar';
import styles from './ScanListPage.module.css';

type SortKey = 'scan_id' | 'total_bscans' | 'labeled' | 'healthy' | 'unhealthy' | 'percent_complete' | 'created_at';
type SortDir = 'asc' | 'desc';

function ScanListPage() {
  const [sortKey, setSortKey] = useState<SortKey>('scan_id');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const {
    data: scans,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['scans'],
    queryFn: api.getScans,
  });

  const { data: globalStats } = useQuery({
    queryKey: ['globalStats'],
    queryFn: api.getGlobalStats,
  });

  const sortedScans = useMemo(() => {
    if (!scans) return [];
    return [...scans].sort((a, b) => {
      let va: number | string;
      let vb: number | string;
      switch (sortKey) {
        case 'scan_id':
          va = a.scan_id; vb = b.scan_id; break;
        case 'created_at':
          va = a.created_at; vb = b.created_at; break;
        case 'total_bscans':
          va = a.stats.total_bscans; vb = b.stats.total_bscans; break;
        case 'labeled':
          va = a.stats.labeled; vb = b.stats.labeled; break;
        case 'healthy':
          va = a.stats.healthy; vb = b.stats.healthy; break;
        case 'unhealthy':
          va = a.stats.unhealthy; vb = b.stats.unhealthy; break;
        case 'percent_complete':
          va = a.stats.percent_complete; vb = b.stats.percent_complete; break;
        default:
          va = a.scan_id; vb = b.scan_id;
      }
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [scans, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sortIndicator = (key: SortKey) => {
    if (sortKey !== key) return '';
    return sortDir === 'asc' ? ' ▲' : ' ▼';
  };

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

  return (
    <div className="container">
      {globalStats && (
        <div className={styles.statsBar}>
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_scans}</span>
            <span className={styles.statLbl}>Scans</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_bscans}</span>
            <span className={styles.statLbl}>B-scans</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_labeled}</span>
            <span className={styles.statLbl}>Labeled</span>
          </div>
          <div className={styles.statDivider} />
          <div className={`${styles.statItem} ${styles.healthyStat}`}>
            <span className={styles.statNum}>{globalStats.total_healthy}</span>
            <span className={styles.statLbl}>Healthy</span>
          </div>
          <div className={styles.statDivider} />
          <div className={`${styles.statItem} ${styles.unhealthyStat}`}>
            <span className={styles.statNum}>{globalStats.total_unhealthy}</span>
            <span className={styles.statLbl}>Unhealthy</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statProgress}>
            <ProgressBar percentage={globalStats.percent_complete} />
          </div>
        </div>
      )}

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.sortable} onClick={() => handleSort('scan_id')}>
                Scan ID{sortIndicator('scan_id')}
              </th>
              <th className={styles.sortable} onClick={() => handleSort('created_at')}>
                Date{sortIndicator('created_at')}
              </th>
              <th className={`${styles.sortable} ${styles.numCol}`} onClick={() => handleSort('total_bscans')}>
                Total{sortIndicator('total_bscans')}
              </th>
              <th className={`${styles.sortable} ${styles.numCol}`} onClick={() => handleSort('labeled')}>
                Labeled{sortIndicator('labeled')}
              </th>
              <th className={`${styles.sortable} ${styles.numCol} ${styles.healthy}`} onClick={() => handleSort('healthy')}>
                Healthy{sortIndicator('healthy')}
              </th>
              <th className={`${styles.sortable} ${styles.numCol} ${styles.unhealthy}`} onClick={() => handleSort('unhealthy')}>
                Unhealthy{sortIndicator('unhealthy')}
              </th>
              <th className={styles.sortable} onClick={() => handleSort('percent_complete')}>
                Progress{sortIndicator('percent_complete')}
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedScans.map((scan) => {
              const isComplete = scan.stats.percent_complete === 100;
              const isInProgress = scan.stats.labeled > 0 && !isComplete;
              return (
                <tr key={scan.scan_id}>
                  <td>
                    <Link to={`/scan/${scan.scan_id}`} className={styles.scanLink}>
                      {scan.scan_id}
                    </Link>
                  </td>
                  <td className={styles.date}>
                    {new Date(scan.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'short', day: 'numeric',
                    })}
                  </td>
                  <td className={styles.numCol}>{scan.stats.total_bscans}</td>
                  <td className={styles.numCol}>{scan.stats.labeled} / {scan.stats.total_bscans}</td>
                  <td className={`${styles.numCol} ${styles.healthy}`}>{scan.stats.healthy}</td>
                  <td className={`${styles.numCol} ${styles.unhealthy}`}>{scan.stats.unhealthy}</td>
                  <td className={styles.progressCol}>
                    <ProgressBar percentage={scan.stats.percent_complete} showLabel={false} />
                    <span className={styles.pct}>{scan.stats.percent_complete.toFixed(1)}%</span>
                  </td>
                  <td>
                    <Link to={`/scan/${scan.scan_id}`} className={styles.actionLink}>
                      {isComplete ? 'Review' : isInProgress ? 'Continue' : 'Start'}
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ScanListPage;
