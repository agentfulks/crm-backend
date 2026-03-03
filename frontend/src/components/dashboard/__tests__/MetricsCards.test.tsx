import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MetricsCards, MetricsCardsDetailed } from '../MetricsCards';
import type { PipelineMetrics } from '../../../types/dashboard';

const createMockMetrics = (overrides: Partial<PipelineMetrics> = {}): PipelineMetrics => ({
  totalFundsInPipeline: 25,
  fundsSentThisWeek: 5,
  responseRate: 15,
  followUpsScheduled: 3,
  fundsByStatus: {
    NEW: 0,
    QUEUED: 10,
    AWAITING_APPROVAL: 5,
    APPROVED: 3,
    SENT: 5,
    FOLLOW_UP: 2,
    CLOSED: 0,
  },
  fundsByDay: {
    1: 5,
    2: 5,
    3: 5,
    4: 5,
    5: 5,
  },
  ...overrides,
});

describe('MetricsCards', () => {
  it('renders all four metric cards', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('Total Funds in Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Funds Sent This Week')).toBeInTheDocument();
    expect(screen.getByText('Response Rate')).toBeInTheDocument();
    expect(screen.getByText('Follow-ups Scheduled')).toBeInTheDocument();
  });

  it('displays correct metric values', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('displays N/A for empty values', () => {
    const metrics = createMockMetrics({
      fundsSentThisWeek: 0,
      responseRate: null,
      followUpsScheduled: 0,
    });
    
    render(<MetricsCards metrics={metrics} />);
    
    const naValues = screen.getAllByText('N/A');
    expect(naValues.length).toBeGreaterThanOrEqual(2);
  });

  it('displays subtitle for total funds', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('15 pending, 3 approved')).toBeInTheDocument();
  });

  it('displays subtitle for funds sent', () => {
    const metrics = createMockMetrics({ fundsSentThisWeek: 0 });
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('Pending Day 1 sends')).toBeInTheDocument();
  });

  it('displays subtitle for response rate when available', () => {
    const metrics = createMockMetrics({ responseRate: 18 });
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('Industry avg: 15-20%')).toBeInTheDocument();
  });

  it('displays subtitle for follow-ups scheduled', () => {
    const metrics = createMockMetrics({ followUpsScheduled: 2 });
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('Next 7 days')).toBeInTheDocument();
  });

  it('displays trend indicator', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCards metrics={metrics} />);
    
    expect(screen.getByText('25 target funds')).toBeInTheDocument();
  });
});

describe('MetricsCardsDetailed', () => {
  it('renders basic metrics and status breakdown', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCardsDetailed metrics={metrics} />);
    
    expect(screen.getByText('Total Funds in Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Status Breakdown')).toBeInTheDocument();
  });

  it('displays all status categories in breakdown', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCardsDetailed metrics={metrics} />);
    
    expect(screen.getByText('Queued')).toBeInTheDocument();
    expect(screen.getByText('Awaiting Approval')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
    expect(screen.getByText('Sent')).toBeInTheDocument();
    expect(screen.getByText('Follow-up')).toBeInTheDocument();
    expect(screen.getByText('Closed')).toBeInTheDocument();
  });

  it('displays correct counts for each status', () => {
    const metrics = createMockMetrics();
    
    render(<MetricsCardsDetailed metrics={metrics} />);
    
    // Each number should appear - check specific ones (using getAllByText since numbers may appear in multiple places)
    expect(screen.getAllByText('10').length).toBeGreaterThanOrEqual(1); // Queued
    expect(screen.getAllByText('3').length).toBeGreaterThanOrEqual(1); // Approved
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1); // Follow-up
    // Note: '5' appears multiple times (Awaiting Approval, Sent, and total funds)
    expect(screen.getAllByText('5').length).toBeGreaterThanOrEqual(2);
  });

  it('displays zero for statuses with no funds', () => {
    const metrics = createMockMetrics({
      fundsByStatus: {
        NEW: 0,
        QUEUED: 0,
        AWAITING_APPROVAL: 0,
        APPROVED: 0,
        SENT: 0,
        FOLLOW_UP: 0,
        CLOSED: 0,
      },
    });
    
    render(<MetricsCardsDetailed metrics={metrics} />);
    
    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThanOrEqual(6);
  });
});
