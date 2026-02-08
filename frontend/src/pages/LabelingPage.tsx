/**
 * Labeling page - main UI for keyboard-first B-scan labeling.
 * Orchestrates all hooks and components for the labeling workflow.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { NavigationMode } from '@/types';
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

  const [currentIndex, setCurrentIndex] = useState(0);
  const [navigationMode, setNavigationMode] = useState(NavigationMode.Sequential);

  // Fetch scan stats to get total B-scans
  const { data: scanStats } = useQuery({
    queryKey: ['scan', scanId, 'stats'],
    queryFn: () => api.getScanStats(scanId!),
    enabled: !!scanId,
  });

  // Fetch current B-scan
  const {
    data: bscan,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['bscan', scanId, currentIndex],
    queryFn: () => api.getBScan(scanId!, currentIndex),
    enabled: !!scanId,
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
    onSuccess: handleAutoAdvance,
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
    enabled: !!bscan && !isLabeling,
  });

  // Reset to index 0 when scan changes
  useEffect(() => {
    setCurrentIndex(0);
  }, [scanId]);

  if (!scanId) {
    navigate('/');
    return null;
  }

  if (isLoading) {
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
            isLoading={isLabeling}
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
            onPrev={handlePrev}
            onNext={handleNext}
            onToggleMode={toggleNavigationMode}
          />

          <LabelingControls
            onLabelHealthy={labelAsHealthy}
            onLabelUnhealthy={labelAsUnhealthy}
            isLoading={isLabeling}
          />
        </div>
      </div>
    </div>
  );
}

export default LabelingPage;
