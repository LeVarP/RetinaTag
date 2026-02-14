import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LabelingControls from '@/components/LabelingControls';
import { Label } from '@/types';

describe('LabelingControls', () => {
  const defaultProps = {
    onLabelHealthy: vi.fn(),
    onLabelUnhealthy: vi.fn(),
    currentLabel: Label.Unlabeled,
    isLoading: false,
  };

  it('renders healthy and unhealthy buttons', () => {
    render(<LabelingControls {...defaultProps} />);
    expect(screen.getByText('Healthy')).toBeInTheDocument();
    expect(screen.getByText('Unhealthy')).toBeInTheDocument();
  });

  it('calls handlers on click', () => {
    const onHealthy = vi.fn();
    const onUnhealthy = vi.fn();
    render(
      <LabelingControls
        {...defaultProps}
        onLabelHealthy={onHealthy}
        onLabelUnhealthy={onUnhealthy}
      />
    );
    fireEvent.click(screen.getByText('Healthy'));
    expect(onHealthy).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByText('Unhealthy'));
    expect(onUnhealthy).toHaveBeenCalledOnce();
  });

  it('disables buttons when loading', () => {
    render(<LabelingControls {...defaultProps} isLoading={true} />);
    expect(screen.getByLabelText('Label as healthy')).toBeDisabled();
    expect(screen.getByLabelText('Label as unhealthy')).toBeDisabled();
  });

  it('displays custom hotkey labels', () => {
    render(
      <LabelingControls
        {...defaultProps}
        hotkeyHealthy="d"
        hotkeyUnhealthy="f"
      />
    );
    expect(screen.getByText('D')).toBeInTheDocument();
    expect(screen.getByText('F')).toBeInTheDocument();
  });

  it('displays default hotkey labels when not provided', () => {
    render(<LabelingControls {...defaultProps} />);
    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('S')).toBeInTheDocument();
  });
});
