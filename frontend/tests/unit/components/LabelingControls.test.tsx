import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import LabelingControls from '@/components/LabelingControls';
import { Label } from '@/types';

describe('LabelingControls', () => {
  const defaultProps = {
    onLabelHealthy: vi.fn(),
    onLabelUnhealthy: vi.fn(),
    currentLabel: Label.Unlabeled,
    isLoading: false,
  };

  it('renders healthy and not-healthy buttons', () => {
    render(<LabelingControls {...defaultProps} />);
    expect(screen.getByText('Healthy')).toBeInTheDocument();
    expect(screen.getByText('Not healthy')).toBeInTheDocument();
    expect(screen.getByText('Cyst')).toBeInTheDocument();
    expect(screen.getByText('Hard exudate')).toBeInTheDocument();
    expect(screen.getByText('SRF')).toBeInTheDocument();
    expect(screen.getByText('PED')).toBeInTheDocument();
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
    fireEvent.click(screen.getByText('Not healthy'));
    expect(onUnhealthy).toHaveBeenCalledOnce();
  });

  it('disables buttons when loading', () => {
    render(<LabelingControls {...defaultProps} isLoading={true} />);
    expect(screen.getByLabelText('Label as healthy')).toBeDisabled();
    expect(screen.getByLabelText('Label as not healthy')).toBeDisabled();
    expect(screen.getByLabelText('Toggle Cyst')).toBeDisabled();
    expect(screen.getByLabelText('Toggle Hard exudate')).toBeDisabled();
    expect(screen.getByLabelText('Toggle SRF')).toBeDisabled();
    expect(screen.getByLabelText('Toggle PED')).toBeDisabled();
  });

  it('calls pathology toggle handlers on click', () => {
    const onToggleCyst = vi.fn();
    const onToggleHardExudate = vi.fn();
    const onToggleSrf = vi.fn();
    const onTogglePed = vi.fn();

    render(
      <LabelingControls
        {...defaultProps}
        onToggleCyst={onToggleCyst}
        onToggleHardExudate={onToggleHardExudate}
        onToggleSrf={onToggleSrf}
        onTogglePed={onTogglePed}
      />
    );

    fireEvent.click(screen.getByLabelText('Toggle Cyst'));
    fireEvent.click(screen.getByLabelText('Toggle Hard exudate'));
    fireEvent.click(screen.getByLabelText('Toggle SRF'));
    fireEvent.click(screen.getByLabelText('Toggle PED'));

    expect(onToggleCyst).toHaveBeenCalledOnce();
    expect(onToggleHardExudate).toHaveBeenCalledOnce();
    expect(onToggleSrf).toHaveBeenCalledOnce();
    expect(onTogglePed).toHaveBeenCalledOnce();
  });

  it('disables healthy button when any pathology is present', () => {
    render(<LabelingControls {...defaultProps} cyst={1} />);
    expect(screen.getByLabelText('Label as healthy')).toBeDisabled();
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

  it('handles unlabel button state and click', () => {
    const onUnlabel = vi.fn();
    const { rerender } = render(
      <LabelingControls
        {...defaultProps}
        onUnlabel={onUnlabel}
        isLabeled={false}
      />
    );

    expect(screen.getByText('Unlabel')).toBeDisabled();

    rerender(
      <LabelingControls
        {...defaultProps}
        onUnlabel={onUnlabel}
        isLabeled={true}
      />
    );

    fireEvent.click(screen.getByText('Unlabel'));
    expect(onUnlabel).toHaveBeenCalledOnce();
  });

  it('calls handler for setting all pathology markers to 0', () => {
    const onSetAllPathologiesZero = vi.fn();
    render(
      <LabelingControls
        {...defaultProps}
        onSetAllPathologiesZero={onSetAllPathologiesZero}
      />
    );

    fireEvent.click(screen.getByText('Set all pathologies = 0'));
    expect(onSetAllPathologiesZero).toHaveBeenCalledOnce();
  });

  it('shows default hotkey for setting all pathology markers to 0', () => {
    render(<LabelingControls {...defaultProps} />);
    const resetButton = screen.getByLabelText('Set all pathology markers to 0');
    expect(within(resetButton).getByText('0')).toBeInTheDocument();
  });
});
