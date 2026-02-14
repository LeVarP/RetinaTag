/**
 * Scan card component displaying scan info and progress.
 */

import { Link } from 'react-router-dom';
import type { Scan } from '@/types';
import ProgressBar from './ProgressBar';
import styles from './ScanCard.module.css';

interface ScanCardProps {
  scan: Scan;
}

function ScanCard({ scan }: ScanCardProps) {
  const { scan_id, stats, created_at } = scan;

  const createdDate = new Date(created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const isComplete = stats.percent_complete === 100;
  const isInProgress = stats.labeled > 0 && !isComplete;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>{scan_id}</h3>
        <span className={styles.date}>{createdDate}</span>
      </div>

      <div className={styles.stats}>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Total B-scans:</span>
          <span className={styles.statValue}>{stats.total_bscans}</span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Labeled:</span>
          <span className={styles.statValue}>
            {stats.labeled} / {stats.total_bscans}
          </span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Healthy:</span>
          <span className={`${styles.statValue} ${styles.healthy}`}>
            {stats.healthy}
          </span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Unhealthy:</span>
          <span className={`${styles.statValue} ${styles.unhealthy}`}>
            {stats.unhealthy}
          </span>
        </div>
      </div>

      <div className={styles.progress}>
        <ProgressBar percentage={stats.percent_complete} />
      </div>

      <div className={styles.actions}>
        <Link to={`/scan/${scan_id}`} className={styles.button}>
          {isComplete ? 'Review' : isInProgress ? 'Continue Labeling' : 'Start Labeling'}
        </Link>
        {isComplete && <span className={styles.badge}>Complete</span>}
        {isInProgress && <span className={`${styles.badge} ${styles.inProgress}`}>In Progress</span>}
      </div>
    </div>
  );
}

export default ScanCard;
