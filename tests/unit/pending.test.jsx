import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Pending from '../../src/frontend/components/Pending.jsx';

describe('Level 1: Pending Component Unit Tests', () => {
  it('renders Pending component with list and handles delete action', () => {
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
