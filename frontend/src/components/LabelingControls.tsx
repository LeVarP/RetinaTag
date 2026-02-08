/**
 * Labeling controls for marking B-scans as healthy or unhealthy.
 */

import styles from './LabelingControls.module.css';

interface LabelingControlsProps {
  onLabelHealthy: () => void;
  onLabelUnhealthy: () => void;
  isLoading?: boolean;
}

function LabelingControls({
  onLabelHealthy,
  onLabelUnhealthy,
  isLoading = false,
}: LabelingControlsProps) {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Label B-scan</h3>

      <div className={styles.buttons}>
        <button
          className={`${styles.labelButton} ${styles.healthy}`}
          onClick={onLabelHealthy}
          disabled={isLoading}
          aria-label="Label as healthy"
        >
          <span className={styles.icon}>✓</span>
          <span className={styles.label}>Healthy</span>
          <kbd className={styles.hotkey}>A</kbd>
        </button>

        <button
          className={`${styles.labelButton} ${styles.unhealthy}`}
          onClick={onLabelUnhealthy}
          disabled={isLoading}
          aria-label="Label as unhealthy"
        >
          <span className={styles.icon}>✗</span>
          <span className={styles.label}>Unhealthy</span>
          <kbd className={styles.hotkey}>S</kbd>
        </button>
      </div>

      <p className={styles.hint}>Use keyboard shortcuts for faster labeling</p>
    </div>
  );
}

export default LabelingControls;
