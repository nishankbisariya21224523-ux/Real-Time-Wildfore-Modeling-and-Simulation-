import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';
import { EmptyState } from './EmptyState';
import { ErrorAlert } from './ErrorAlert';
import { ErrorBoundary } from './ErrorBoundary';

describe('Feedback Components (Loading, Empty, Error, Boundary)', () => {
  it('renders LoadingSpinner with custom label', () => {
    render(<LoadingSpinner label="Loading satellite observation feeds..." />);
    expect(screen.getByText('Loading satellite observation feeds...')).toBeInTheDocument();
  });

  it('renders EmptyState with title, description, and action button', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No Regions Monitored"
        description="Connect database to view monitored reserves."
        actionLabel="Refresh List"
        onAction={handleAction}
      />
    );

    expect(screen.getByText('No Regions Monitored')).toBeInTheDocument();
    expect(screen.getByText('Connect database to view monitored reserves.')).toBeInTheDocument();

    const btn = screen.getByRole('button', { name: /refresh list/i });
    fireEvent.click(btn);
    expect(handleAction).toHaveBeenCalled();
  });

  it('renders ErrorAlert with code and retry action', () => {
    const handleRetry = vi.fn();
    render(
      <ErrorAlert
        title="PostGIS Connection Timeout"
        message="Could not reach PostgreSQL on port 5432."
        code="DB_CONN_ERR"
        onRetry={handleRetry}
      />
    );

    expect(screen.getByText('PostGIS Connection Timeout')).toBeInTheDocument();
    expect(screen.getByText('DB_CONN_ERR')).toBeInTheDocument();

    const retryBtn = screen.getByRole('button', { name: /retry request/i });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalled();
  });

  it('catches render errors inside ErrorBoundary without crashing entire app', () => {
    const BadComponent = () => {
      throw new Error('Spatial geometry rendering failed');
    };

    // Prevent console.error noise during expected error boundary test
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <BadComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText(/gis component error/i)).toBeInTheDocument();
    expect(screen.getByText(/spatial geometry rendering failed/i)).toBeInTheDocument();

    consoleError.mockRestore();
  });
});
