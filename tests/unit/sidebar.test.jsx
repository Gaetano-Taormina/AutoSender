import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Sidebar from '../../src/frontend/components/Sidebar.jsx';

describe('Level 1: Sidebar Component Unit Tests', () => {
  it('renders Sidebar with navigation links across different active routes and viewports', () => {
    const toggleMock = vi.fn();

    // 1. Mobile viewport (< 768)
    window.innerWidth = 500;
    const { unmount } = render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar isOpen={true} toggle={toggleMock} />
      </MemoryRouter>
    );

    expect(screen.getByText('AutoSender')).toBeTruthy();
    const navLinks = screen.getAllByRole('link');
    fireEvent.click(navLinks[0]);
    fireEvent.click(navLinks[1]);
    fireEvent.click(navLinks[2]);
    expect(toggleMock).toHaveBeenCalledTimes(3);
    unmount();

    // 2. Desktop viewport (>= 768)
    window.innerWidth = 1024;
    const desktopToggle = vi.fn();
    render(
      <MemoryRouter initialEntries={['/compose']}>
        <Sidebar isOpen={false} toggle={desktopToggle} />
      </MemoryRouter>
    );
    const links = screen.getAllByRole('link');
    fireEvent.click(links[0]);
    fireEvent.click(links[1]);
    fireEvent.click(links[2]);
    expect(desktopToggle).not.toHaveBeenCalled();

    // 3. Route /pending active
    render(
      <MemoryRouter initialEntries={['/pending']}>
        <Sidebar isOpen={false} toggle={vi.fn()} />
      </MemoryRouter>
    );
  });
});
