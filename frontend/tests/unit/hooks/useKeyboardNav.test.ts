import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useKeyboardNav } from '@/hooks/useKeyboardNav';
import { DEFAULT_HOTKEYS } from '@/types';

function fireKey(key: string) {
  window.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true }));
}

describe('useKeyboardNav', () => {
  it('handles default hotkeys', () => {
    const onNext = vi.fn();
    const onPrev = vi.fn();
    const onHealthy = vi.fn();
    const onUnhealthy = vi.fn();

    renderHook(() =>
      useKeyboardNav({
        onNext,
        onPrev,
        onLabelHealthy: onHealthy,
        onLabelUnhealthy: onUnhealthy,
      })
    );

    fireKey('ArrowRight');
    expect(onNext).toHaveBeenCalledOnce();

    fireKey('ArrowLeft');
    expect(onPrev).toHaveBeenCalledOnce();

    fireKey('a');
    expect(onHealthy).toHaveBeenCalledOnce();

    fireKey('s');
    expect(onUnhealthy).toHaveBeenCalledOnce();
  });

  it('handles uppercase label keys', () => {
    const onHealthy = vi.fn();
    const onUnhealthy = vi.fn();

    renderHook(() =>
      useKeyboardNav({
        onNext: vi.fn(),
        onPrev: vi.fn(),
        onLabelHealthy: onHealthy,
        onLabelUnhealthy: onUnhealthy,
      })
    );

    fireKey('A');
    expect(onHealthy).toHaveBeenCalledOnce();

    fireKey('S');
    expect(onUnhealthy).toHaveBeenCalledOnce();
  });

  it('uses custom hotkeys', () => {
    const onHealthy = vi.fn();
    const onUnhealthy = vi.fn();

    renderHook(() =>
      useKeyboardNav({
        onNext: vi.fn(),
        onPrev: vi.fn(),
        onLabelHealthy: onHealthy,
        onLabelUnhealthy: onUnhealthy,
        hotkeys: {
          nextFrame: 'ArrowDown',
          prevFrame: 'ArrowUp',
          labelHealthy: 'd',
          labelUnhealthy: 'f',
          toggleCyst: 'z',
          toggleHardExudate: 'x',
          toggleSrf: 'c',
          togglePed: 'v',
        },
      })
    );

    // Default keys should not work
    fireKey('a');
    expect(onHealthy).not.toHaveBeenCalled();

    // Custom keys should work
    fireKey('d');
    expect(onHealthy).toHaveBeenCalledOnce();

    fireKey('f');
    expect(onUnhealthy).toHaveBeenCalledOnce();
  });

  it('does nothing when disabled', () => {
    const onNext = vi.fn();

    renderHook(() =>
      useKeyboardNav({
        onNext,
        onPrev: vi.fn(),
        onLabelHealthy: vi.fn(),
        onLabelUnhealthy: vi.fn(),
        enabled: false,
      })
    );

    fireKey('ArrowRight');
    expect(onNext).not.toHaveBeenCalled();
  });

  it('handles pathology toggle hotkeys 1..4 by default', () => {
    const onToggleCyst = vi.fn();
    const onToggleHardExudate = vi.fn();
    const onToggleSrf = vi.fn();
    const onTogglePed = vi.fn();

    renderHook(() =>
      useKeyboardNav({
        onNext: vi.fn(),
        onPrev: vi.fn(),
        onLabelHealthy: vi.fn(),
        onLabelUnhealthy: vi.fn(),
        onToggleCyst,
        onToggleHardExudate,
        onToggleSrf,
        onTogglePed,
      })
    );

    fireKey('1');
    fireKey('2');
    fireKey('3');
    fireKey('4');

    expect(onToggleCyst).toHaveBeenCalledOnce();
    expect(onToggleHardExudate).toHaveBeenCalledOnce();
    expect(onToggleSrf).toHaveBeenCalledOnce();
    expect(onTogglePed).toHaveBeenCalledOnce();
  });
});
