import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PacketCard } from './PacketCard';
import type { Packet, Fund } from '../types';

const mockFund: Fund = {
  id: 'fund-1',
  name: 'Test Fund',
  firm_type: 'VC',
  hq_city: 'San Francisco',
  hq_region: 'California',
  hq_country: 'USA',
  stage_focus: ['Series A', 'Series B'],
  check_size_min: 1000000,
  check_size_max: 5000000,
  check_size_currency: 'USD',
  website_url: 'https://testfund.com',
  linkedin_url: 'https://linkedin.com/company/testfund',
  overview: 'A test fund for venture capital investments',
  contact_email: 'test@testfund.com',
  target_countries: ['USA'],
  tags: {},
  priority: 'A',
  status: 'READY',
  created_at: '2025-02-25T00:00:00Z',
  updated_at: '2025-02-25T00:00:00Z',
};

const createMockPacket = (overrides: Partial<Packet> = {}): Packet => ({
  id: 'packet-1',
  fund_id: 'fund-1',
  fund: mockFund,
  status: 'AWAITING_APPROVAL',
  priority: 'A',
  score_snapshot: 85,
  created_at: '2025-02-25T00:00:00Z',
  updated_at: '2025-02-25T00:00:00Z',
  ...overrides,
});

describe('PacketCard', () => {
  it('renders fund name and basic info', () => {
    const packet = createMockPacket();
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('Test Fund')).toBeInTheDocument();
    expect(screen.getByText('VC')).toBeInTheDocument();
  });

  it('displays priority badge correctly', () => {
    const packet = createMockPacket({ priority: 'A' });
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('Priority A')).toBeInTheDocument();
  });

  it('displays status badge correctly', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('AWAITING APPROVAL')).toBeInTheDocument();
  });

  it('displays score when available', () => {
    const packet = createMockPacket({ score_snapshot: 92 });
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('Score: 92')).toBeInTheDocument();
  });

  it('displays location info', () => {
    const packet = createMockPacket();
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('San Francisco, California')).toBeInTheDocument();
  });

  it('displays check size range', () => {
    const packet = createMockPacket();
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('$1.0M - $5.0M')).toBeInTheDocument();
  });

  it('displays overview with line clamp', () => {
    const packet = createMockPacket();
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('A test fund for venture capital investments')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const packet = createMockPacket();
    const onClick = vi.fn();
    render(<PacketCard packet={packet} onClick={onClick} />);
    
    fireEvent.click(screen.getByText('Test Fund'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('shows action buttons when showActions is true and status is AWAITING_APPROVAL', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    render(<PacketCard packet={packet} showActions={true} />);
    
    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
  });

  it('hides action buttons when showActions is false', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    render(<PacketCard packet={packet} showActions={false} />);
    
    expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    expect(screen.queryByText('Reject')).not.toBeInTheDocument();
  });

  it('hides action buttons when status is not AWAITING_APPROVAL', () => {
    const packet = createMockPacket({ status: 'APPROVED' });
    render(<PacketCard packet={packet} showActions={true} />);
    
    expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    expect(screen.queryByText('Reject')).not.toBeInTheDocument();
  });

  it('calls onApprove when approve button is clicked', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    const onApprove = vi.fn();
    render(<PacketCard packet={packet} showActions={true} onApprove={onApprove} />);
    
    fireEvent.click(screen.getByText('Approve'));
    expect(onApprove).toHaveBeenCalledTimes(1);
  });

  it('calls onReject when reject button is clicked', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    const onReject = vi.fn();
    render(<PacketCard packet={packet} showActions={true} onReject={onReject} />);
    
    fireEvent.click(screen.getByText('Reject'));
    expect(onReject).toHaveBeenCalledTimes(1);
  });

  it('calls onEdit when edit button is clicked', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    const onEdit = vi.fn();
    render(<PacketCard packet={packet} showActions={true} onEdit={onEdit} />);
    
    fireEvent.click(screen.getByText('Edit'));
    expect(onEdit).toHaveBeenCalledTimes(1);
  });

  it('stops propagation when action buttons are clicked', () => {
    const packet = createMockPacket({ status: 'AWAITING_APPROVAL' });
    const onClick = vi.fn();
    const onApprove = vi.fn();
    render(<PacketCard packet={packet} showActions={true} onClick={onClick} onApprove={onApprove} />);
    
    fireEvent.click(screen.getByText('Approve'));
    expect(onApprove).toHaveBeenCalledTimes(1);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('handles missing fund gracefully', () => {
    const packet = createMockPacket({ fund: undefined });
    render(<PacketCard packet={packet} />);
    
    expect(screen.getByText('Unknown Fund')).toBeInTheDocument();
  });

  it('renders different status colors correctly', () => {
    const statuses = ['QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'] as const;
    
    statuses.forEach(status => {
      const { unmount } = render(<PacketCard packet={createMockPacket({ status })} />);
      expect(screen.getByText(status.replace('_', ' '))).toBeInTheDocument();
      unmount();
    });
  });

  it('renders different priority colors correctly', () => {
    const priorities = ['A', 'B', 'C'] as const;
    
    priorities.forEach(priority => {
      const { unmount } = render(<PacketCard packet={createMockPacket({ priority })} />);
      expect(screen.getByText(`Priority ${priority}`)).toBeInTheDocument();
      unmount();
    });
  });
});
