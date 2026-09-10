import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Sidebar from '../../src/frontend/components/Sidebar.jsx';

describe('Level 1: Sidebar Component Unit Tests', () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('renders Sidebar with navigation links across different active routes and viewports', () => {
    const toggleMock = vi.fn();

    // 1. Mobile viewport (< 768)
    window.innerWidth = 500;
    const { unmount: unmount1 } = render(
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
    unmount1();

    // 2. Desktop viewport (>= 768)
    window.innerWidth = 1024;
    const desktopToggle = vi.fn();
    const { unmount: unmount2 } = render(
      <MemoryRouter initialEntries={['/compose']}>
        <Sidebar isOpen={false} toggle={desktopToggle} />
      </MemoryRouter>
    );
    const links = screen.getAllByRole('link');
    fireEvent.click(links[0]);
    fireEvent.click(links[1]);
    fireEvent.click(links[2]);
    expect(desktopToggle).not.toHaveBeenCalled();
    unmount2();

    // 3. Route /pending active
    const { unmount: unmount3 } = render(
      <MemoryRouter initialEntries={['/pending']}>
        <Sidebar isOpen={false} toggle={vi.fn()} />
      </MemoryRouter>
    );
    unmount3();
  });
});

