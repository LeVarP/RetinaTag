/**
 * Labeling controls for marking B-scans as healthy or unhealthy.
 * Buttons show filled background only when the current label matches.
 */

import { Label } from '@/types';
import styles from './LabelingControls.module.css';

interface LabelingControlsProps {
  onLabelHealthy: () => void;
  onLabelUnhealthy: () => void;
  currentLabel: Label;
  isLoading?: boolean;
  hotkeyHealthy?: string;
  hotkeyUnhealthy?: string;
}

function LabelingControls({
  onLabelHealthy,
  onLabelUnhealthy,
  currentLabel,
  isLoading = false,
  hotkeyHealthy = 'A',
  hotkeyUnhealthy = 'S',
}: LabelingControlsProps) {
  const isHealthy = currentLabel === Label.Healthy;
  const isUnhealthy = currentLabel === Label.Unhealthy;

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Label B-scan</h3>

      <div className={styles.buttons}>
        <button
          className={`${styles.labelButton} ${styles.healthy} ${isHealthy ? styles.active : ''}`}
          onClick={onLabelHealthy}
          disabled={isLoading}
          aria-label="Label as healthy"
        >
          <span className={styles.icon}>{isHealthy ? '✓' : '✓'}</span>
          <span className={styles.label}>Healthy</span>
          <kbd className={styles.hotkey}>{hotkeyHealthy.toUpperCase()}</kbd>
        </button>

        <button
          className={`${styles.labelButton} ${styles.unhealthy} ${isUnhealthy ? styles.active : ''}`}
          onClick={onLabelUnhealthy}
          disabled={isLoading}
          aria-label="Label as unhealthy"
        >
          <span className={styles.icon}>✗</span>
          <span className={styles.label}>Unhealthy</span>
          <kbd className={styles.hotkey}>{hotkeyUnhealthy.toUpperCase()}</kbd>
        </button>
      </div>

      <p className={styles.hint}>Use keyboard shortcuts for faster labeling</p>
    </div>
  );
}

export default LabelingControls;
