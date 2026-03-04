/**
 * Labeling page - main UI for keyboard-first B-scan labeling.
 * Orchestrates all hooks and components for the labeling workflow.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { KeyboardHotkeys } from '@/types';
import { useSettings } from '@/context/SettingsContext';
import { useKeyboardNav } from '@/hooks/useKeyboardNav';
import { usePrefetch } from '@/hooks/usePrefetch';
import { useLabeling } from '@/hooks/useLabeling';
import BScanViewer from '@/components/BScanViewer';
import NavigationControls from '@/components/NavigationControls';
import LabelingControls from '@/components/LabelingControls';
import styles from './LabelingPage.module.css';

function LabelingPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();

  const { settings } = useSettings();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageMaxWidth, setImageMaxWidth] = useState(450);

  const hotkeys: KeyboardHotkeys = {
    nextFrame: settings.hotkey_next,
    prevFrame: settings.hotkey_prev,
    labelHealthy: settings.hotkey_healthy,
    labelUnhealthy: settings.hotkey_unhealthy,
    toggleCyst: settings.hotkey_cyst,
    toggleHardExudate: settings.hotkey_hard_exudate,
    toggleSrf: settings.hotkey_srf,
    togglePed: settings.hotkey_ped,
  };

  // Fetch scan stats to get total B-scans
  const { data: scanStats } = useQuery({
    queryKey: ['scan', scanId, 'stats'],
    queryFn: () => api.getScanStats(scanId!),
    enabled: !!scanId,
  });

  // Fetch current B-scan (keep previous data visible while loading next)
  const {
    data: bscan,
    isLoading,
    isFetching,
    isError,
    error,
  } = useQuery({
    queryKey: ['bscan', scanId, currentIndex],
    queryFn: () => api.getBScan(scanId!, currentIndex),
    enabled: !!scanId,
    placeholderData: keepPreviousData,
  });

  const totalBScans = scanStats?.total_bscans || 0;

  // Prefetch next K frames
  usePrefetch({
    scanId: scanId!,
    currentIndex,
    totalBScans,
    prefetchCount: 10,
    enabled: !!scanId && totalBScans > 0,
  });

  const { labelAsHealthy, labelAsUnhealthy, updatePathology, clearLabel, isLoading: isLabeling } = useLabeling({
    scanId: scanId!,
    bscanId: bscan?.id,
    currentIndex,
  });

  const toggleCyst = () => {
    updatePathology({ cyst: bscan?.cyst === 1 ? 0 : 1 });
  };

  const toggleHardExudate = () => {
    updatePathology({ hard_exudate: bscan?.hard_exudate === 1 ? 0 : 1 });
  };

  const toggleSrf = () => {
    updatePathology({ srf: bscan?.srf === 1 ? 0 : 1 });
  };

  const togglePed = () => {
    updatePathology({ ped: bscan?.ped === 1 ? 0 : 1 });
  };

  const setAllPathologiesZero = () => {
    updatePathology({
      cyst: 0,
      hard_exudate: 0,
      srf: 0,
      ped: 0,
    });
  };

  const hasAnyPathology =
    bscan?.cyst === 1 ||
    bscan?.hard_exudate === 1 ||
    bscan?.srf === 1 ||
    bscan?.ped === 1;

  const handleLabelHealthy = () => {
    if (hasAnyPathology) {
      return;
    }
    labelAsHealthy();
  };

  // Navigation handlers
  const handleNext = () => {
    if (bscan?.next_index !== null && bscan?.next_index !== undefined) {
      setCurrentIndex(bscan.next_index);
    }
  };

  const handlePrev = () => {
    if (bscan?.prev_index !== null && bscan?.prev_index !== undefined) {
      setCurrentIndex(bscan.prev_index);
    }
  };

  // Keyboard navigation
  useKeyboardNav({
    onNext: handleNext,
    onPrev: handlePrev,
    onLabelHealthy: handleLabelHealthy,
    onLabelUnhealthy: labelAsUnhealthy,
    onToggleCyst: toggleCyst,
    onToggleHardExudate: toggleHardExudate,
    onToggleSrf: toggleSrf,
    onTogglePed: togglePed,
    hotkeys,
    enabled: !!bscan && !isLabeling,
  });

  // Reset to index 0 when scan changes (0-based B-scan indexing)
  useEffect(() => {
    setCurrentIndex(0);
  }, [scanId]);

  if (!scanId) {
    navigate('/');
    return null;
  }

  if (isLoading && !bscan) {
    return (
      <div className="container">
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading B-scan...</p>
        </div>
      </div>
    );
  }

  if (isError || !bscan) {
    return (
      <div className="container">
        <div className={styles.error}>
          <h2>Error Loading B-scan</h2>
          <p>{error instanceof Error ? error.message : 'B-scan not found'}</p>
          <Link to="/" className={styles.backButton}>
            Back to Scans
          </Link>
        </div>
      </div>
    );
  }

  const hasPrev = bscan.prev_index !== null;
  const hasNext = bscan.next_index !== null;

  return (
    <div className="container">
      <div className={styles.header}>
        <Link to="/" className={styles.backLink}>
          ← Back to Scans
        </Link>
        <h2 className={styles.title}>Labeling: {scanId}</h2>
      </div>

      <div className={styles.content}>
        <div className={styles.viewer}>
          <BScanViewer
            previewUrl={bscan.preview_url || ''}
            healthy={bscan.healthy}
            isLabeled={bscan.is_labeled}
            bscanIndex={bscan.bscan_index}
            isLoading={isLabeling || isFetching}
            maxWidth={imageMaxWidth}
            onMaxWidthChange={setImageMaxWidth}
          />
        </div>

        <div className={styles.controls}>
          <NavigationControls
            currentIndex={currentIndex}
            totalBScans={totalBScans}
            hasPrev={hasPrev}
            hasNext={hasNext}
            onPrev={handlePrev}
            onNext={handleNext}
            onGoTo={setCurrentIndex}
          />

          <LabelingControls
            onLabelHealthy={handleLabelHealthy}
            onLabelUnhealthy={labelAsUnhealthy}
            onUnlabel={clearLabel}
            onSetAllPathologiesZero={setAllPathologiesZero}
            onOpenHotkeySettings={() => navigate('/profile#hotkeys')}
            onToggleCyst={toggleCyst}
            onToggleHardExudate={toggleHardExudate}
            onToggleSrf={toggleSrf}
            onTogglePed={togglePed}
            currentLabel={bscan.label}
            cyst={bscan.cyst}
            hardExudate={bscan.hard_exudate}
            srf={bscan.srf}
            ped={bscan.ped}
            isLabeled={bscan.is_labeled}
            isLoading={isLabeling}
            hotkeyHealthy={settings.hotkey_healthy}
            hotkeyUnhealthy={settings.hotkey_unhealthy}
            hotkeyCyst={settings.hotkey_cyst}
            hotkeyHardExudate={settings.hotkey_hard_exudate}
            hotkeySrf={settings.hotkey_srf}
            hotkeyPed={settings.hotkey_ped}
          />
        </div>
      </div>
    </div>
  );
}

export default LabelingPage;
