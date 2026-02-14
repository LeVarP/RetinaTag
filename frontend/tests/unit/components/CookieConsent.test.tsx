import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CookieConsent from '@/components/CookieConsent';

describe('CookieConsent', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows banner when no consent stored', () => {
    render(<CookieConsent />);
    expect(screen.getByText(/uses cookies for authentication/i)).toBeInTheDocument();
  });

  it('hides after clicking accept', () => {
    render(<CookieConsent />);
    fireEvent.click(screen.getByText('I Understand'));
    expect(screen.queryByText(/uses cookies for authentication/i)).not.toBeInTheDocument();
    expect(localStorage.getItem('cookie-consent')).toBe('true');
  });

  it('does not show when consent already stored', () => {
    localStorage.setItem('cookie-consent', 'true');
    render(<CookieConsent />);
    expect(screen.queryByText(/uses cookies for authentication/i)).not.toBeInTheDocument();
  });
});
