import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import NavigationControls from '@/components/NavigationControls';
import { NavigationMode } from '@/types';

describe('NavigationControls', () => {
  const defaultProps = {
    currentIndex: 5,
    totalBScans: 100,
    hasPrev: true,
    hasNext: true,
    hasNextUnlabeled: true,
    navigationMode: NavigationMode.Sequential,
    autoAdvance: true,
    onPrev: vi.fn(),
    onNext: vi.fn(),
    onGoTo: vi.fn(),
    onToggleMode: vi.fn(),
    onToggleAutoAdvance: vi.fn(),
  };

  it('shows counter with current/total', () => {
    render(<NavigationControls {...defaultProps} />);
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('disables previous button when hasPrev is false', () => {
    render(<NavigationControls {...defaultProps} hasPrev={false} />);
    expect(screen.getByLabelText('Previous B-scan')).toBeDisabled();
  });

  it('disables next button when hasNext is false', () => {
    render(<NavigationControls {...defaultProps} hasNext={false} />);
    expect(screen.getByLabelText('Next B-scan')).toBeDisabled();
  });

  it('calls onPrev and onNext', () => {
    const onPrev = vi.fn();
    const onNext = vi.fn();
    render(<NavigationControls {...defaultProps} onPrev={onPrev} onNext={onNext} />);
    fireEvent.click(screen.getByLabelText('Previous B-scan'));
    expect(onPrev).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByLabelText('Next B-scan'));
    expect(onNext).toHaveBeenCalledOnce();
  });

  it('calls onToggleAutoAdvance', () => {
    const onToggle = vi.fn();
    render(<NavigationControls {...defaultProps} onToggleAutoAdvance={onToggle} />);
    fireEvent.click(screen.getByText(/Auto-advance/));
    expect(onToggle).toHaveBeenCalledOnce();
  });

  it('shows stay on frame when autoAdvance is off', () => {
    render(<NavigationControls {...defaultProps} autoAdvance={false} />);
    expect(screen.getByText(/Stay on frame/)).toBeInTheDocument();
  });
});
