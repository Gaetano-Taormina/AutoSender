import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LiveLogs from '../../src/frontend/components/LiveLogs.jsx';
import Sidebar from '../../src/frontend/components/Sidebar.jsx';
import { MemoryRouter } from 'react-router-dom';

describe('Level 1: React Component Unit Tests', () => {
  it('renders LiveLogs container with initial placeholder', () => {
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
});
