import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Compose from '../../src/frontend/components/Compose.jsx';

describe('Level 1: Compose Component Unit Tests', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    delete window.eel;
    vi.restoreAllMocks();
  });

  it('renders and fetches contacts when eel is available (array vs null)', async () => {
    // 1. Array contacts
    window.eel = {
      get_recent_contacts_from_db: vi.fn(() => () => Promise.resolve(['Alice', 'Bob']))
    };

    const { unmount } = render(<Compose addTask={vi.fn()} />);
    expect(screen.getByText('Schedule New Message')).toBeTruthy();

    await waitFor(() => {
      expect(window.eel.get_recent_contacts_from_db).toHaveBeenCalled();
    });
    unmount();

    // 2. Null contacts fallback
    window.eel = {
      get_recent_contacts_from_db: vi.fn(() => () => Promise.resolve(null))
    };
    render(<Compose addTask={vi.fn()} />);
    await waitFor(() => {
      expect(window.eel.get_recent_contacts_from_db).toHaveBeenCalled();
    });
  });

  it('handles missing window.eel on mount', () => {
    delete window.eel;
    render(<Compose addTask={vi.fn()} />);
    expect(screen.getByText('Schedule New Message')).toBeTruthy();
  });

  it('handles eel error when fetching recent contacts', async () => {
    window.eel = {
      get_recent_contacts_from_db: vi.fn(() => () => Promise.reject(new Error('Fetch failed')))
    };

    render(<Compose addTask={vi.fn()} />);
    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
    });
  });

  it('validates each required field individually on submission', () => {
    const { container } = render(<Compose addTask={vi.fn()} />);
    const form = container.querySelector('form');

    // 1. All empty
    fireEvent.submit(form);
    expect(screen.getByText('Please fill in all required fields!')).toBeTruthy();

    // 2. Only contact filled
    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Alice' } });
    fireEvent.submit(form);
    expect(screen.getByText('Please fill in all required fields!')).toBeTruthy();

    // 3. Contact & message filled, missing time
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Hello' } });
    fireEvent.submit(form);
    expect(screen.getByText('Please fill in all required fields!')).toBeTruthy();
  });

  it('validates past time selection with date and without date', () => {
    const { container } = render(<Compose addTask={vi.fn()} />);
    const form = container.querySelector('form');

    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Alice' } });
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Hello' } });
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: '2020-01-01' } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '10:00' } });

    fireEvent.submit(form);
    expect(screen.getByText('The selected time is in the past!')).toBeTruthy();

    // Dismiss alert
    const closeAlert = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeAlert);
    expect(screen.queryByText('The selected time is in the past!')).toBeNull();

    // Past time without date input (defaults to today past time)
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '00:01' } });
    fireEvent.submit(form);
    expect(screen.getByText('The selected time is in the past!')).toBeTruthy();
  });

  it('successfully schedules single message without explicit date', async () => {
    const addTaskMock = vi.fn().mockResolvedValue(true);
    const { container } = render(<Compose addTask={addTaskMock} />);

    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Alice' } });
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Hello' } });
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '23:59' } });

    const form = container.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(addTaskMock).toHaveBeenCalledWith('Alice', 'Hello', expect.any(Number));
      expect(screen.getByText('Message scheduled successfully !')).toBeTruthy();
    });
  });

  it('schedules repeated messages with seconds and minutes units and fallback parsing', async () => {
    const addTaskMock = vi.fn().mockResolvedValue(true);
    const { container } = render(<Compose addTask={addTaskMock} />);

    const futureYear = new Date().getFullYear() + 1;
    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Bob' } });
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Ping' } });
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: `${futureYear}-06-15` } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '14:30' } });

    // Change repeat count with empty string fallback to 1, then 3
    fireEvent.change(screen.getByLabelText(/Repeat \(times\)/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/Repeat \(times\)/i), { target: { value: '3' } });
    expect(screen.getByLabelText(/Interval/i)).toBeTruthy();

    // Change interval with empty string fallback, then minutes
    fireEvent.change(screen.getByLabelText(/Interval/i), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText(/Interval/i), { target: { value: '5' } });
    const selectUnit = container.querySelector('select');
    fireEvent.change(selectUnit, { target: { value: 'minutes' } });

    const form = container.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(addTaskMock).toHaveBeenCalledTimes(3);
      expect(screen.getByText('Message scheduled successfully 3 times!')).toBeTruthy();
    });
  });

  it('schedules repeated messages with seconds unit', async () => {
    const addTaskMock = vi.fn().mockResolvedValue(true);
    const { container } = render(<Compose addTask={addTaskMock} />);

    const futureYear = new Date().getFullYear() + 1;
    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Bob' } });
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Ping' } });
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: `${futureYear}-06-15` } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '14:30' } });
    fireEvent.change(screen.getByLabelText(/Repeat \(times\)/i), { target: { value: '2' } });

    const selectUnit = container.querySelector('select');
    fireEvent.change(selectUnit, { target: { value: 'seconds' } });

    const form = container.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(addTaskMock).toHaveBeenCalledTimes(2);
    });
  });

  it('handles addTask failure in repeated loop', async () => {
    const addTaskMock = vi.fn().mockResolvedValueOnce(true).mockResolvedValueOnce(false);
    const { container } = render(<Compose addTask={addTaskMock} />);

    const futureYear = new Date().getFullYear() + 1;
    fireEvent.change(screen.getByPlaceholderText(/E.g. \+39 333/i), { target: { value: 'Bob' } });
    fireEvent.change(screen.getByPlaceholderText(/Type your message here.../i), { target: { value: 'Ping' } });
    fireEvent.change(screen.getByLabelText(/Date \(Optional\)/i), { target: { value: `${futureYear}-06-15` } });
    fireEvent.change(screen.getByLabelText(/^Time/i), { target: { value: '14:30' } });
    fireEvent.change(screen.getByLabelText(/Repeat \(times\)/i), { target: { value: '2' } });

    const form = container.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/Error scheduling some messages./i)).toBeTruthy();
    });
  });
});
