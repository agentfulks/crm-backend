import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueueStatus } from './QueueStatus';
import * as usePacketsModule from '../hooks/usePackets';
import type { QueueStatus as QueueStatusType } from '../types';

// Mock the hooks module
vi.mock('../hooks/usePackets', () => ({
  useQueueStatus: vi.fn(),
}));

const { useQueueStatus } = usePacketsModule;

describe('QueueStatus', () => {
  it('renders loading state', () => {
    (useQueueStatus as any).mockReturnValue({
      data: null,
      isLoading: true,
    });
    
    render(<QueueStatus />);
    
    // Should show skeleton loaders
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders queue statistics correctly', () => {
    const mockData: QueueStatusType = {
      date: '2025-02-25',
      total_queued: 5,
      awaiting_approval: 3,
      approved_today: 2,
      sent_today: 1,
    };
    
    (useQueueStatus as any).mockReturnValue({
      data: mockData,
      isLoading: false,
    });
    
    render(<QueueStatus />);
    
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Queued')).toBeInTheDocument();
    
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Awaiting Approval')).toBeInTheDocument();
    
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Approved Today')).toBeInTheDocument();
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('Sent Today')).toBeInTheDocument();
  });

  it('returns null when no data is available', () => {
    (useQueueStatus as any).mockReturnValue({
      data: null,
      isLoading: false,
    });
    
    const { container } = render(<QueueStatus />);
    
    // Component returns null, so container should be empty
    expect(container.firstChild).toBeNull();
  });

  it('displays zero values correctly', () => {
    const mockData: QueueStatusType = {
      date: '2025-02-25',
      total_queued: 0,
      awaiting_approval: 0,
      approved_today: 0,
      sent_today: 0,
    };
    
    (useQueueStatus as any).mockReturnValue({
      data: mockData,
      isLoading: false,
    });
    
    render(<QueueStatus />);
    
    const zeros = screen.getAllByText('0');
    expect(zeros).toHaveLength(4);
  });
});
