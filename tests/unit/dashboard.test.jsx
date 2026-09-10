import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from '../../src/frontend/components/Dashboard.jsx';

describe('Level 1: Dashboard Component Unit Tests', () => {
  it('renders Dashboard with pending task counts and handles pluralization/null', () => {
    // 1. Multiple tasks
    const mockTasks = [
      { id: '1', contact: 'Alice', message: 'Hi', timestamp: 1700000000 },
      { id: '2', contact: 'Bob', message: 'Hello', timestamp: 1700000000 }
    ];

    const { rerender } = render(
      <MemoryRouter>
        <Dashboard tasks={mockTasks} />
      </MemoryRouter>
    );

    expect(screen.getByText('Welcome to AutoSender')).toBeTruthy();
    expect(screen.getByText('Pending Tasks')).toBeTruthy();
    expect(screen.getByText('You have 2 messages waiting to be sent.')).toBeTruthy();

    // 2. Single task (singularization check)
    rerender(
      <MemoryRouter>
        <Dashboard tasks={[{ id: '1', contact: 'Alice', message: 'Hi', timestamp: 1700000000 }]} />
      </MemoryRouter>
    );
    expect(screen.getByText('You have 1 message waiting to be sent.')).toBeTruthy();

    // 3. Empty tasks array
    rerender(
      <MemoryRouter>
        <Dashboard tasks={[]} />
      </MemoryRouter>
    );
    expect(screen.getByText('You have 0 messages waiting to be sent.')).toBeTruthy();

    // 4. Null tasks fallback
    rerender(
      <MemoryRouter>
        <Dashboard tasks={null} />
      </MemoryRouter>
    );
    expect(screen.getByText('You have 0 messages waiting to be sent.')).toBeTruthy();
  });
});
