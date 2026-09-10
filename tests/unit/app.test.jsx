import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act, cleanup } from '@testing-library/react';
import App from '../../src/frontend/App';

describe('App Component', () => {
  beforeEach(() => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      get_recent_contacts_from_db: vi.fn(() => () => Promise.resolve([])),
      get_logs: vi.fn(() => () => Promise.resolve([])),
      schedule_task: vi.fn(() => () => Promise.resolve({ success: true })),
      delete_task_from_db: vi.fn(() => () => Promise.resolve({ success: true }))
    };
  });

  afterEach(() => {
    cleanup();
    delete window.eel;
    vi.restoreAllMocks();
  });

  it('renders App layout, header, footer, and navigation routes', async () => {
    let renderResult;
    await act(async () => {
      renderResult = render(<App />);
    });

    const { container, unmount } = renderResult;

    expect(screen.getAllByText('AutoSender').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Privacy & Legal:/i)).toBeTruthy();

    // Toggle mobile sidebar via hamburger button
    const hamburgerBtn = container.querySelector('.d-md-none button');
    expect(hamburgerBtn).toBeTruthy();

    await act(async () => {
      fireEvent.click(hamburgerBtn);
    });

    // Overlay is now visible
    const overlay = container.querySelector('.d-md-none[style*="rgba(0, 0, 0, 0.5)"]');
    expect(overlay).toBeTruthy();

    // Click overlay to close sidebar
    await act(async () => {
      fireEvent.click(overlay);
    });
    unmount();
  });
});

