import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import LiveLogs from '../../src/frontend/components/LiveLogs.jsx';

describe('Level 2: Frontend-Backend Eel Bridge Integration Tests', () => {
  beforeEach(() => {
    window.eel = {
      get_logs: vi.fn(() => () => Promise.resolve([
        '[12:00:01] Service started',
        '[12:00:05] Checking pending messages queue'
      ]))
    };
  });

  afterEach(() => {
    delete window.eel;
  });

  it('polls logs through Eel bridge and renders stream', async () => {
    render(<LiveLogs />);

    await act(async () => {
      await new Promise((r) => setTimeout(r, 60));
    });

    expect(screen.getByText('[12:00:01] Service started')).toBeTruthy();
    expect(screen.getByText('[12:00:05] Checking pending messages queue')).toBeTruthy();
  });
});
