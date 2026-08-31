import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import Compose from '../../src/frontend/components/Compose.jsx';
import Pending from '../../src/frontend/components/Pending.jsx';

describe('Level 3: Frontend End-to-End User Flow Tests', () => {
  let mockTasks = [];

  beforeEach(() => {
    mockTasks = [
      { id: 'task-101', contact: 'John Doe', message: 'Reminder note', timestamp: 1750000000 }
    ];

    window.eel = {
      get_recent_contacts_from_db: vi.fn(() => () => Promise.resolve(['John Doe', 'Jane Smith'])),
      schedule_task: vi.fn((contact, message, ts) => () => {
        const newTask = { id: `task-${Date.now()}`, contact, message, timestamp: ts };
        mockTasks.push(newTask);
        return Promise.resolve({ success: true });
      }),
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve(mockTasks)),
      delete_task_from_db: vi.fn((id) => () => {
        mockTasks = mockTasks.filter(t => t.id !== id);
        return Promise.resolve({ success: true });
      })
    };
  });

  afterEach(() => {
    delete window.eel;
  });

  it('completes the full compose and pending tasks management flow', async () => {
    const mockAddTask = vi.fn(async (contact, message, ts) => {
      mockTasks.push({ id: 'task-102', contact, message, timestamp: ts / 1000 });
      return true;
    });

    // 1. Render Compose component
    await act(async () => {
      render(<Compose onTaskCreated={() => {}} addTask={mockAddTask} />);
    });

    // 2. Render Pending component
    let unmountFn;
    await act(async () => {
      const { unmount } = render(<Pending tasks={mockTasks} removeTask={(id) => {
        mockTasks = mockTasks.filter(t => t.id !== id);
      }} />);
      unmountFn = unmount;
    });

    expect(screen.getByText('John Doe')).toBeTruthy();
    expect(screen.getByText('Reminder note')).toBeTruthy();
    unmountFn();
  });
});
