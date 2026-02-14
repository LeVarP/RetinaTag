/**
 * Progress bar component for visualizing completion percentage.
 */

import styles from './ProgressBar.module.css';

interface ProgressBarProps {
  percentage: number;
  showLabel?: boolean;
}

function ProgressBar({ percentage, showLabel = true }: ProgressBarProps) {
  const safePercentage = Number.isFinite(percentage) ? percentage : 0;
  const clampedPercentage = Math.min(100, Math.max(0, safePercentage));

  return (
    <div className={styles.container}>
      <div className={styles.bar}>
        <div
          className={styles.fill}
          style={{ width: `${clampedPercentage}%` }}
          role="progressbar"
          aria-valuenow={clampedPercentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {showLabel && (
        <span className={styles.label}>{clampedPercentage.toFixed(1)}%</span>
      )}
    </div>
  );
}

export default ProgressBar;
