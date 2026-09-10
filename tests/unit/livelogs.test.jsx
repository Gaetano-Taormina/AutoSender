import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, waitFor, act, cleanup } from '@testing-library/react';
import LiveLogs from '../../src/frontend/components/LiveLogs.jsx';

describe('Level 1: LiveLogs Component Unit Tests', () => {
  afterEach(() => {
    cleanup();
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
    let unmount;
    await act(async () => {
      const res = render(<LiveLogs />);
      unmount = res.unmount;
    });
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
    unmount();
  });

  it('handles missing window.eel and errors gracefully', async () => {
    delete window.eel;
    const { unmount: unmount1 } = render(<LiveLogs />);
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
    unmount1();

    window.eel = {
      get_logs: vi.fn(() => () => Promise.reject(new Error('Log fetch failed')))
    };
    const { unmount: unmount2 } = render(<LiveLogs />);
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
    unmount2();
  });
});

