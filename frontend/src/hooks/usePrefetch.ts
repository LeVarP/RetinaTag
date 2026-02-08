/**
 * Prefetch hook for loading next K images in the background.
 * Uses browser Image API for efficient caching.
 */

import { useEffect } from 'react';
import { api } from '@/services/api';

interface UsePrefetchProps {
  scanId: string;
  currentIndex: number;
  totalBScans: number;
  prefetchCount?: number;
  enabled?: boolean;
}

/**
 * Hook for prefetching next K preview images.
 * Triggered on index change.
 */
export function usePrefetch({
  scanId,
  currentIndex,
  totalBScans,
  prefetchCount = 10,
  enabled = true,
}: UsePrefetchProps) {
  useEffect(() => {
    if (!enabled) return;

    // Calculate indexes to prefetch (next K frames)
    const indexesToPrefetch: number[] = [];
    for (let i = 1; i <= prefetchCount; i++) {
      const nextIndex = currentIndex + i;
      if (nextIndex < totalBScans) {
        indexesToPrefetch.push(nextIndex);
      }
    }

    // Prefetch images using browser Image API
    const images: HTMLImageElement[] = [];

    indexesToPrefetch.forEach((index) => {
      const img = new Image();
      img.src = api.getPreviewUrl(scanId, index);
      images.push(img);
    });

    // Cleanup function (images will stay in browser cache)
    return () => {
      images.forEach((img) => {
        img.src = '';
      });
    };
  }, [scanId, currentIndex, totalBScans, prefetchCount, enabled]);
}
