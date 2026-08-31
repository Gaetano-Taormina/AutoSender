import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
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

  it('completes the full compose form flow with validation and scheduling', async () => {
    const mockAddTask = vi.fn(async (contact, message, ts) => {
      mockTasks.push({ id: 'task-102', contact, message, timestamp: ts / 1000 });
      return true;
    });

    // 1. Render Compose component
    await act(async () => {
      render(<Compose onTaskCreated={() => {}} addTask={mockAddTask} />);
      await new Promise((r) => setTimeout(r, 50));
    });

    const contactInput = screen.getByPlaceholderText('E.g. +39 333... or John Doe');
    const messageInput = screen.getByPlaceholderText('Type your message here...');
    const timeInput = screen.getByLabelText('Time');
    const submitBtn = screen.getByText('Schedule Message');

    // Fill form
    fireEvent.change(contactInput, { target: { value: 'Jane Smith' } });
    fireEvent.change(messageInput, { target: { value: 'Tomorrow Meeting' } });
    fireEvent.change(timeInput, { target: { value: '23:59' } });

    // Submit form
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    expect(mockAddTask).toHaveBeenCalled();

    // 2. Render Pending component and check updated state
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

  it('handles repeat interval configuration and validation in Compose', async () => {
    const mockAddTask = vi.fn(async () => true);

    await act(async () => {
      render(<Compose onTaskCreated={() => {}} addTask={mockAddTask} />);
    });

    const repeatInput = screen.getByLabelText('Repeat (times)');
    fireEvent.change(repeatInput, { target: { value: '3' } });

    // Interval input should appear when repeats > 1
    const intervalInput = screen.getByLabelText('Interval');
    expect(intervalInput).toBeTruthy();
    fireEvent.change(intervalInput, { target: { value: '5' } });
  });
});
