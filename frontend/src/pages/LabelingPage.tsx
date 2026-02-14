/**
 * Labeling page - main UI for keyboard-first B-scan labeling.
 * Orchestrates all hooks and components for the labeling workflow.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { api } from '@/services/api';
import { NavigationMode, type KeyboardHotkeys } from '@/types';
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

  const { settings, updateSettings } = useSettings();

  const [currentIndex, setCurrentIndex] = useState(1);
  const [navigationMode, setNavigationMode] = useState(NavigationMode.Sequential);
  const [imageMaxWidth, setImageMaxWidth] = useState(450);

  const autoAdvance = settings.auto_advance;
  const hotkeys: KeyboardHotkeys = {
    nextFrame: settings.hotkey_next,
    prevFrame: settings.hotkey_prev,
    labelHealthy: settings.hotkey_healthy,
    labelUnhealthy: settings.hotkey_unhealthy,
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

  // Auto-advance to next frame after labeling
  const handleAutoAdvance = () => {
    if (navigationMode === NavigationMode.Sequential) {
      // Sequential: go to next frame
      if (bscan?.next_index !== null && bscan?.next_index !== undefined) {
        setCurrentIndex(bscan.next_index);
      }
    } else {
      // Unlabeled only: go to next unlabeled frame
      if (bscan?.next_unlabeled_index !== null && bscan?.next_unlabeled_index !== undefined) {
        setCurrentIndex(bscan.next_unlabeled_index);
      } else if (bscan?.next_index !== null && bscan?.next_index !== undefined) {
        // Fallback to sequential if no unlabeled frames left
        setCurrentIndex(bscan.next_index);
      }
    }
  };

  // Labeling hook with auto-advance
  const { labelAsHealthy, labelAsUnhealthy, isLoading: isLabeling } = useLabeling({
    scanId: scanId!,
    bscanId: bscan?.id,
    currentIndex,
    onSuccess: autoAdvance ? handleAutoAdvance : undefined,
  });

  // Navigation handlers
  const handleNext = () => {
    if (navigationMode === NavigationMode.Sequential) {
      if (bscan?.next_index !== null && bscan?.next_index !== undefined) {
        setCurrentIndex(bscan.next_index);
      }
    } else {
      // Unlabeled only mode
      if (bscan?.next_unlabeled_index !== null && bscan?.next_unlabeled_index !== undefined) {
        setCurrentIndex(bscan.next_unlabeled_index);
      }
    }
  };

  const handlePrev = () => {
    if (bscan?.prev_index !== null && bscan?.prev_index !== undefined) {
      setCurrentIndex(bscan.prev_index);
    }
  };

  const toggleNavigationMode = () => {
    setNavigationMode((prev) =>
      prev === NavigationMode.Sequential
        ? NavigationMode.UnlabeledOnly
        : NavigationMode.Sequential
    );
  };

  // Keyboard navigation
  useKeyboardNav({
    onNext: handleNext,
    onPrev: handlePrev,
    onLabelHealthy: labelAsHealthy,
    onLabelUnhealthy: labelAsUnhealthy,
    hotkeys,
    enabled: !!bscan && !isLabeling,
  });

  // Reset to index 1 when scan changes (B-scans start at index 1)
  useEffect(() => {
    setCurrentIndex(1);
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
  const hasNextUnlabeled = bscan.next_unlabeled_index !== null;

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
            label={bscan.label}
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
            hasNextUnlabeled={hasNextUnlabeled}
            navigationMode={navigationMode}
            autoAdvance={autoAdvance}
            onPrev={handlePrev}
            onNext={handleNext}
            onGoTo={setCurrentIndex}
            onToggleMode={toggleNavigationMode}
            onToggleAutoAdvance={() => updateSettings({ auto_advance: !autoAdvance })}
          />

          <LabelingControls
            onLabelHealthy={labelAsHealthy}
            onLabelUnhealthy={labelAsUnhealthy}
            currentLabel={bscan.label}
            isLoading={isLabeling}
            hotkeyHealthy={settings.hotkey_healthy}
            hotkeyUnhealthy={settings.hotkey_unhealthy}
          />
        </div>
      </div>
    </div>
  );
}

export default LabelingPage;
