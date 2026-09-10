import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTasks } from '../../src/frontend/useTasks.jsx';

describe('Level 1: useTasks Hook Unit Tests - 100% Branch Coverage', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(window, 'alert').mockImplementation(() => {});
  });

  afterEach(() => {
    delete window.eel;
    vi.restoreAllMocks();
  });

  it('initializes and loads tasks successfully with array data', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([
        { id: '1', contact: 'Alice', message: 'Hi', timestamp: 1700000000 }
      ])),
      schedule_task: vi.fn(() => () => Promise.resolve({ success: true })),
      delete_task_from_db: vi.fn(() => () => Promise.resolve({ success: true }))
    };

    const { result } = renderHook(() => useTasks());
    expect(result.current.tasks).toEqual([]);

    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.tasks.length).toBe(1);
    expect(result.current.tasks[0].contact).toBe('Alice');
  });

  it('initializes and handles null data fallback to empty array', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve(null))
    };

    const { result } = renderHook(() => useTasks());
    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.tasks).toEqual([]);
  });

  it('handles load exception during useEffect initial fetch', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.reject(new Error('Load error')))
    };

    const { result } = renderHook(() => useTasks());
    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.tasks).toEqual([]);
    expect(console.error).toHaveBeenCalledWith('Error fetching tasks via Eel:', expect.any(Error));
  });

  it('handles unmounting while load is in flight', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => new Promise((r) => setTimeout(() => r([{ id: '1' }]), 100)))
    };

    const { unmount } = renderHook(() => useTasks());
    unmount();
    await act(async () => {
      await new Promise((r) => setTimeout(r, 150));
    });
  });

  it('handles addTask when eel is undefined', async () => {
    delete window.eel;
    const { result } = renderHook(() => useTasks());

    let res;
    await act(async () => {
      res = await result.current.addTask('Alice', 'Test', 1700000000000);
    });

    expect(res).toBe(false);
    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining('Python Backend'));
  });

  it('handles addTask success and triggers fetchTasks with null data', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve(null)),
      schedule_task: vi.fn(() => () => Promise.resolve({ success: true }))
    };

    const { result } = renderHook(() => useTasks());

    let res;
    await act(async () => {
      res = await result.current.addTask('Alice', 'Hello', 1700000000000);
    });

    expect(res).toBe(true);
    expect(window.eel.schedule_task).toHaveBeenCalledWith('Alice', 'Hello', 1700000000);
  });

  it('handles addTask failure with response error string', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      schedule_task: vi.fn(() => () => Promise.resolve({ success: false, error: 'Database is locked' }))
    };

    const { result } = renderHook(() => useTasks());

    let res;
    await act(async () => {
      res = await result.current.addTask('Bob', 'Hi', 1700000000000);
    });

    expect(res).toBe(false);
    expect(window.alert).toHaveBeenCalledWith('Error saving: Database is locked');
  });

  it('handles addTask failure with null response (Unknown error)', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      schedule_task: vi.fn(() => () => Promise.resolve(null))
    };

    const { result } = renderHook(() => useTasks());

    let res;
    await act(async () => {
      res = await result.current.addTask('Bob', 'Hi', 1700000000000);
    });

    expect(res).toBe(false);
    expect(window.alert).toHaveBeenCalledWith('Error saving: Unknown error');
  });

  it('handles addTask exception in eel call', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      schedule_task: vi.fn(() => () => Promise.reject(new Error('Network disconnected')))
    };

    const { result } = renderHook(() => useTasks());

    let res;
    await act(async () => {
      res = await result.current.addTask('Bob', 'Hi', 1700000000000);
    });

    expect(res).toBe(false);
    expect(console.error).toHaveBeenCalledWith('Eel error in addTask:', expect.any(Error));
  });

  it('handles removeTask when eel is missing', async () => {
    delete window.eel;
    const { result } = renderHook(() => useTasks());

    await act(async () => {
      await result.current.removeTask('123');
    });
  });

  it('handles removeTask success and fetchTasks exception', async () => {
    let callCount = 0;
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => {
        callCount++;
        if (callCount === 1) return Promise.resolve([]);
        return Promise.reject(new Error('Fetch post-delete failed'));
      }),
      delete_task_from_db: vi.fn(() => () => Promise.resolve({ success: true }))
    };

    const { result } = renderHook(() => useTasks());

    await act(async () => {
      await result.current.removeTask('123');
    });

    expect(window.eel.delete_task_from_db).toHaveBeenCalledWith('123');
    expect(console.error).toHaveBeenCalledWith('Error fetching tasks via Eel:', expect.any(Error));
  });

  it('handles removeTask exception', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      delete_task_from_db: vi.fn(() => () => Promise.reject(new Error('Delete error')))
    };

    const { result } = renderHook(() => useTasks());

    await act(async () => {
      await result.current.removeTask('123');
    });

    expect(console.error).toHaveBeenCalledWith('Eel error in removeTask:', expect.any(Error));
  });

  it('handles fetchTasks when window.eel becomes undefined after mount', async () => {
    window.eel = {
      get_pending_tasks_from_db: vi.fn(() => () => Promise.resolve([])),
      delete_task_from_db: vi.fn(() => () => Promise.resolve({ success: true }))
    };

    const { result } = renderHook(() => useTasks());

    // Call removeTask but delete window.eel right before fetchTasks runs
    window.eel.delete_task_from_db = () => () => {
      delete window.eel;
      return Promise.resolve({ success: true });
    };

    await act(async () => {
      await result.current.removeTask('123');
    });
  });
});
