/**
 * Labeling controls for marking B-scans as healthy or not healthy.
 * Buttons show filled background only when the current label matches.
 */

import { Label } from '@/types';
import styles from './LabelingControls.module.css';

interface LabelingControlsProps {
  onLabelHealthy: () => void;
  onLabelUnhealthy: () => void;
  onUnlabel?: () => void;
  onSetAllPathologiesZero?: () => void;
  onOpenHotkeySettings?: () => void;
  onToggleCyst?: () => void;
  onToggleHardExudate?: () => void;
  onToggleSrf?: () => void;
  onTogglePed?: () => void;
  currentLabel: Label;
  isLabeled?: boolean;
  cyst?: number | null;
  hardExudate?: number | null;
  srf?: number | null;
  ped?: number | null;
  isLoading?: boolean;
  hotkeyHealthy?: string;
  hotkeyUnhealthy?: string;
  hotkeyCyst?: string;
  hotkeyHardExudate?: string;
  hotkeySrf?: string;
  hotkeyPed?: string;
}

function LabelingControls({
  onLabelHealthy,
  onLabelUnhealthy,
  onUnlabel = () => {},
  onSetAllPathologiesZero = () => {},
  onOpenHotkeySettings,
  onToggleCyst = () => {},
  onToggleHardExudate = () => {},
  onToggleSrf = () => {},
  onTogglePed = () => {},
  currentLabel,
  isLabeled = false,
  cyst = null,
  hardExudate = null,
  srf = null,
  ped = null,
  isLoading = false,
  hotkeyHealthy = 'A',
  hotkeyUnhealthy = 'S',
  hotkeyCyst = '1',
  hotkeyHardExudate = '2',
  hotkeySrf = '3',
  hotkeyPed = '4',
}: LabelingControlsProps) {
  const isHealthy = currentLabel === Label.Healthy;
  const isUnhealthy = currentLabel === Label.Unhealthy;
  const hasCyst = cyst === 1;
  const hasHardExudate = hardExudate === 1;
  const hasSrf = srf === 1;
  const hasPed = ped === 1;
  const hasAnyPathology = hasCyst || hasHardExudate || hasSrf || hasPed;

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Label B-scan</h3>

      <div className={styles.buttons}>
        <button
          className={`${styles.labelButton} ${styles.healthy} ${isHealthy ? styles.active : ''}`}
          onClick={onLabelHealthy}
          disabled={isLoading || hasAnyPathology}
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
          aria-label="Label as not healthy"
        >
          <span className={styles.icon}>✗</span>
          <span className={styles.label}>Not healthy</span>
          <kbd className={styles.hotkey}>{hotkeyUnhealthy.toUpperCase()}</kbd>
        </button>
      </div>

      <div className={styles.unlabelRow}>
        <button
          type="button"
          className={styles.unlabelButton}
          onClick={onUnlabel}
          disabled={isLoading || !isLabeled}
          aria-label="Clear all labels for this B-scan"
        >
          Unlabel
        </button>
      </div>

      <div className={styles.pathologySection}>
        <h4 className={styles.pathologyTitle}>Pathology Markers</h4>
        <div className={styles.pathologyButtons}>
          <button
            className={`${styles.pathologyButton} ${hasCyst ? styles.activePathology : ''}`}
            onClick={onToggleCyst}
            disabled={isLoading}
            aria-label="Toggle Cyst"
          >
            <span>Cyst</span>
            <kbd className={styles.hotkey}>{hotkeyCyst.toUpperCase()}</kbd>
          </button>

          <button
            className={`${styles.pathologyButton} ${hasHardExudate ? styles.activePathology : ''}`}
            onClick={onToggleHardExudate}
            disabled={isLoading}
            aria-label="Toggle Hard exudate"
          >
            <span>Hard exudate</span>
            <kbd className={styles.hotkey}>{hotkeyHardExudate.toUpperCase()}</kbd>
          </button>

          <button
            className={`${styles.pathologyButton} ${hasSrf ? styles.activePathology : ''}`}
            onClick={onToggleSrf}
            disabled={isLoading}
            aria-label="Toggle SRF"
          >
            <span>SRF</span>
            <kbd className={styles.hotkey}>{hotkeySrf.toUpperCase()}</kbd>
          </button>

          <button
            className={`${styles.pathologyButton} ${hasPed ? styles.activePathology : ''}`}
            onClick={onTogglePed}
            disabled={isLoading}
            aria-label="Toggle PED"
          >
            <span>PED</span>
            <kbd className={styles.hotkey}>{hotkeyPed.toUpperCase()}</kbd>
          </button>
        </div>
        <div className={styles.pathologyActionRow}>
          <button
            type="button"
            className={styles.pathologyResetButton}
            onClick={onSetAllPathologiesZero}
            disabled={isLoading}
            aria-label="Set all pathology markers to 0"
          >
            Set all pathologies = 0
          </button>
        </div>
      </div>

      {onOpenHotkeySettings && (
        <div className={styles.settingsRow}>
          <button
            type="button"
            className={styles.settingsButton}
            onClick={onOpenHotkeySettings}
          >
            ⚙️ Configure hotkeys
          </button>
        </div>
      )}

      <p className={styles.hint}>
        Any pathology marker = 1 automatically sets the scan to not healthy.
      </p>
    </div>
  );
}

export default LabelingControls;
