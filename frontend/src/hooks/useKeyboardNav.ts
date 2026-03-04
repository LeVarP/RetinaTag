/**
 * Keyboard navigation hook for labeling interface.
 * Listens for configurable hotkeys for navigation and labeling.
 */

import { useEffect } from 'react';
import { DEFAULT_HOTKEYS, type KeyboardHotkeys } from '@/types';

interface UseKeyboardNavProps {
  onNext: () => void;
  onPrev: () => void;
  onLabelHealthy: () => void;
  onLabelUnhealthy: () => void;
  onToggleCyst?: () => void;
  onToggleHardExudate?: () => void;
  onToggleSrf?: () => void;
  onTogglePed?: () => void;
  onSetAllPathologiesZero?: () => void;
  hotkeys?: KeyboardHotkeys;
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
  onToggleCyst,
  onToggleHardExudate,
  onToggleSrf,
  onTogglePed,
  onSetAllPathologiesZero,
  hotkeys = DEFAULT_HOTKEYS,
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

      const key = event.key;

      // Check against configured hotkeys
      if (key === hotkeys.nextFrame) {
        event.preventDefault();
        onNext();
      } else if (key === hotkeys.prevFrame) {
        event.preventDefault();
        onPrev();
      } else if (
        key === hotkeys.labelHealthy ||
        key === hotkeys.labelHealthy.toUpperCase()
      ) {
        event.preventDefault();
        onLabelHealthy();
      } else if (
        key === hotkeys.labelUnhealthy ||
        key === hotkeys.labelUnhealthy.toUpperCase()
      ) {
        event.preventDefault();
        onLabelUnhealthy();
      } else if (
        (key === hotkeys.toggleCyst || key === hotkeys.toggleCyst.toUpperCase()) &&
        onToggleCyst
      ) {
        event.preventDefault();
        onToggleCyst();
      } else if (
        (key === hotkeys.toggleHardExudate || key === hotkeys.toggleHardExudate.toUpperCase()) &&
        onToggleHardExudate
      ) {
        event.preventDefault();
        onToggleHardExudate();
      } else if (
        (key === hotkeys.toggleSrf || key === hotkeys.toggleSrf.toUpperCase()) &&
        onToggleSrf
      ) {
        event.preventDefault();
        onToggleSrf();
      } else if (
        (key === hotkeys.togglePed || key === hotkeys.togglePed.toUpperCase()) &&
        onTogglePed
      ) {
        event.preventDefault();
        onTogglePed();
      } else if (
        (key === hotkeys.setAllPathologiesZero ||
          key === hotkeys.setAllPathologiesZero.toUpperCase()) &&
        onSetAllPathologiesZero
      ) {
        event.preventDefault();
        onSetAllPathologiesZero();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [
    onNext,
    onPrev,
    onLabelHealthy,
    onLabelUnhealthy,
    onToggleCyst,
    onToggleHardExudate,
    onToggleSrf,
    onTogglePed,
    onSetAllPathologiesZero,
    hotkeys,
    enabled,
  ]);
}
