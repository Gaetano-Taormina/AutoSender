import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTasks } from '../../src/frontend/useTasks.jsx';

describe('Level 1: useTasks Hook Unit Tests', () => {
  beforeEach(() => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([
        { id: '1', contact: 'Alice', message: 'Hi', timestamp: 1700000000 }
      ])),
      schedule_task: vi.fn(() => () => Promise.resolve({ success: true })),
      delete_task_from_db: vi.fn(() => () => Promise.resolve({ success: true }))
    };
  });

  afterEach(() => {
    delete window.eel;
  });

  it('initializes with empty tasks and fetches pending tasks', async () => {
    const { result } = renderHook(() => useTasks());
    expect(result.current.tasks).toEqual([]);

    await act(async () => {
      // wait for effect to resolve
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.tasks.length).toBe(1);
    expect(result.current.tasks[0].contact).toBe('Alice');
  });

  it('calls schedule_task with seconds timestamp', async () => {
    const { result } = renderHook(() => useTasks());

    let success;
    await act(async () => {
      success = await result.current.addTask('Bob', 'Meeting at 10', 1700000000000);
    });

    expect(success).toBe(true);
    expect(window.eel.schedule_task).toHaveBeenCalledWith('Bob', 'Meeting at 10', 1700000000);
  });
});
