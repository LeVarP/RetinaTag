/**
 * Keyboard navigation hook for labeling interface.
 * Listens for Arrow keys (navigation) and A/S keys (labeling).
 */

import { useEffect } from 'react';
import { DEFAULT_HOTKEYS } from '@/types';

interface UseKeyboardNavProps {
  onNext: () => void;
  onPrev: () => void;
  onLabelHealthy: () => void;
  onLabelUnhealthy: () => void;
  enabled?: boolean;
}

/**
 * Hook for handling keyboard navigation and labeling hotkeys.
 */
export function useKeyboardNav({
  onNext,
  onPrev,
  onLabelHealthy,
  onLabelUnhealthy,
  enabled = true,
}: UseKeyboardNavProps) {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in input/textarea
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      // Prevent default for navigation keys
      const navigationKeys = [
        DEFAULT_HOTKEYS.nextFrame,
        DEFAULT_HOTKEYS.prevFrame,
        DEFAULT_HOTKEYS.labelHealthy,
        DEFAULT_HOTKEYS.labelUnhealthy,
      ];

      if (navigationKeys.includes(event.key)) {
        event.preventDefault();
      }

      // Handle navigation
      switch (event.key) {
        case DEFAULT_HOTKEYS.nextFrame: // ArrowRight
          onNext();
          break;
        case DEFAULT_HOTKEYS.prevFrame: // ArrowLeft
          onPrev();
          break;
        case DEFAULT_HOTKEYS.labelHealthy: // 'a'
        case DEFAULT_HOTKEYS.labelHealthy.toUpperCase(): // 'A'
          onLabelHealthy();
          break;
        case DEFAULT_HOTKEYS.labelUnhealthy: // 's'
        case DEFAULT_HOTKEYS.labelUnhealthy.toUpperCase(): // 'S'
          onLabelUnhealthy();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onNext, onPrev, onLabelHealthy, onLabelUnhealthy, enabled]);
}
