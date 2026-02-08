/**
 * Navigation controls for moving between B-scans.
 */

import { NavigationMode } from '@/types';
import styles from './NavigationControls.module.css';

interface NavigationControlsProps {
  currentIndex: number;
  totalBScans: number;
  hasPrev: boolean;
  hasNext: boolean;
  hasNextUnlabeled: boolean;
  navigationMode: NavigationMode;
  onPrev: () => void;
  onNext: () => void;
  onToggleMode: () => void;
}

function NavigationControls({
  currentIndex,
  totalBScans,
  hasPrev,
  hasNext,
  hasNextUnlabeled,
  navigationMode,
  onPrev,
  onNext,
  onToggleMode,
}: NavigationControlsProps) {
  const isSequential = navigationMode === NavigationMode.Sequential;

  return (
    <div className={styles.container}>
      <div className={styles.navigation}>
        <button
          className={styles.navButton}
          onClick={onPrev}
          disabled={!hasPrev}
          aria-label="Previous B-scan"
        >
          <span className={styles.arrow}>←</span>
          <span className={styles.buttonText}>Previous</span>
        </button>

        <div className={styles.counter}>
          <span className={styles.current}>{currentIndex + 1}</span>
          <span className={styles.separator}>/</span>
          <span className={styles.total}>{totalBScans}</span>
        </div>

        <button
          className={styles.navButton}
          onClick={onNext}
          disabled={!hasNext}
          aria-label="Next B-scan"
        >
          <span className={styles.buttonText}>Next</span>
          <span className={styles.arrow}>→</span>
        </button>
      </div>

      <div className={styles.modeToggle}>
        <button
          className={`${styles.modeButton} ${isSequential ? styles.active : ''}`}
          onClick={onToggleMode}
        >
          {isSequential ? '📋 Sequential' : '🎯 Unlabeled Only'}
        </button>
        {!isSequential && !hasNextUnlabeled && (
          <span className={styles.hint}>No more unlabeled frames</span>
        )}
      </div>

      <div className={styles.hint}>
        Use <kbd>←</kbd> <kbd>→</kbd> arrow keys to navigate
      </div>
    </div>
  );
}

export default NavigationControls;
