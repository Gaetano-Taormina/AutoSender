import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LiveLogs from '../../src/frontend/components/LiveLogs.jsx';
import Sidebar from '../../src/frontend/components/Sidebar.jsx';
import Dashboard from '../../src/frontend/components/Dashboard.jsx';
import Pending from '../../src/frontend/components/Pending.jsx';
import { MemoryRouter } from 'react-router-dom';

describe('Level 1: React Component Unit Tests', () => {
  it('renders LiveLogs container with initial placeholder and stream', () => {
    render(<LiveLogs />);
    expect(screen.getByText('Background Service Activity')).toBeTruthy();
    expect(screen.getByText('Waiting for operations...')).toBeTruthy();
  });

  it('renders Sidebar with navigation links', () => {
    render(
      <MemoryRouter>
        <Sidebar activeTab="dashboard" setActiveTab={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('AutoSender')).toBeTruthy();
    expect(screen.getByText('Dashboard')).toBeTruthy();
    expect(screen.getByText('Compose')).toBeTruthy();
    expect(screen.getByText('Pending')).toBeTruthy();
  });

  it('renders Dashboard with pending task counts and system status', () => {
    const mockTasks = [
      { id: '1', contact: 'Alice', message: 'Hi', timestamp: 1700000000 },
      { id: '2', contact: 'Bob', message: 'Hello', timestamp: 1700000000 }
    ];

    render(
      <MemoryRouter>
        <Dashboard tasks={mockTasks} />
      </MemoryRouter>
    );

    expect(screen.getByText('Welcome to AutoSender')).toBeTruthy();
    expect(screen.getByText('Pending Tasks')).toBeTruthy();
    expect(screen.getByText('You have 2 messages waiting to be sent.')).toBeTruthy();
    expect(screen.getByText('● Online & Ready')).toBeTruthy();
  });

  it('renders Pending component with empty state and delete action', () => {
    const removeMock = vi.fn();
    const mockTasks = [
      { id: 'task-1', contact: 'Charlie', message: 'Test message', timestamp: 1750000000 }
    ];

    const { rerender } = render(
      <Pending tasks={mockTasks} removeTask={removeMock} />
    );

    expect(screen.getByText('Charlie')).toBeTruthy();
    expect(screen.getByText('Test message')).toBeTruthy();

    const deleteBtn = screen.getByTitle('Cancel Message');
    fireEvent.click(deleteBtn);
    expect(removeMock).toHaveBeenCalledWith('task-1');

    // Test empty state
    rerender(<Pending tasks={[]} removeTask={removeMock} />);
    expect(screen.getByText('No pending messages')).toBeTruthy();
  });
});
