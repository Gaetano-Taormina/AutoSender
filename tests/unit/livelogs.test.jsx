import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import LiveLogs from '../../src/frontend/components/LiveLogs.jsx';

describe('Level 1: LiveLogs Component Unit Tests', () => {
  afterEach(() => {
    delete window.eel;
    vi.restoreAllMocks();
  });

  it('renders LiveLogs with active log stream and auto-scroll', async () => {
    window.eel = {
      get_logs: vi.fn(() => () => Promise.resolve(['[12:00:00] Service started', '[12:00:01] Operation completed']))
    };

    const { unmount } = render(<LiveLogs />);
    expect(screen.getByText('Background Service Activity')).toBeTruthy();

    await waitFor(() => {
      expect(screen.getByText('[12:00:00] Service started')).toBeTruthy();
      expect(screen.getByText('[12:00:01] Operation completed')).toBeTruthy();
    });
    unmount();
  });

  it('handles null logs fallback', async () => {
    window.eel = {
      get_logs: vi.fn(() => () => Promise.resolve(null))
    };
    await act(async () => {
      render(<LiveLogs />);
    });
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
  });

  it('handles missing window.eel and errors gracefully', async () => {
    delete window.eel;
    const { unmount } = render(<LiveLogs />);
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
    unmount();

    window.eel = {
      get_logs: vi.fn(() => () => Promise.reject(new Error('Log fetch failed')))
    };
    render(<LiveLogs />);
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
  });
});
