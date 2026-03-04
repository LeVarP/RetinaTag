/**
 * Navigation controls for moving between B-scans.
 */

import { useState, useRef } from 'react';
import styles from './NavigationControls.module.css';

interface NavigationControlsProps {
  currentIndex: number;
  totalBScans: number;
  hasPrev: boolean;
  hasNext: boolean;
  onPrev: () => void;
  onNext: () => void;
  onGoTo: (index: number) => void;
}

function NavigationControls({
  currentIndex,
  totalBScans,
  hasPrev,
  hasNext,
  onPrev,
  onNext,
  onGoTo,
}: NavigationControlsProps) {
  const maxIndex = Math.max(totalBScans - 1, 0);
  const [isEditing, setIsEditing] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleCounterClick = () => {
    setInputValue(String(currentIndex));
    setIsEditing(true);
    setTimeout(() => inputRef.current?.select(), 0);
  };

  const handleSubmit = () => {
    const num = parseInt(inputValue, 10);
    if (!isNaN(num) && num >= 0 && num <= maxIndex) {
      onGoTo(num);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
    }
    e.stopPropagation();
  };

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
          {isEditing ? (
            <input
              ref={inputRef}
              type="number"
              min={0}
              max={maxIndex}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onBlur={handleSubmit}
              onKeyDown={handleKeyDown}
              className={styles.indexInput}
              autoFocus
            />
          ) : (
            <span className={styles.current} onClick={handleCounterClick} title="Click to jump to a specific B-scan">
              {currentIndex}
            </span>
          )}
          <span className={styles.separator}>/</span>
          <span className={styles.total}>{totalBScans - 1}</span>
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

      <div className={styles.hint}>
        Use <kbd>←</kbd> <kbd>→</kbd> arrow keys to navigate
      </div>
    </div>
  );
}

export default NavigationControls;
