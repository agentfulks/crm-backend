import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PipelineOverview } from '../PipelineOverview';
import type { PipelineDay } from '../../../types/dashboard';

const createMockDays = (): PipelineDay[] => [
  {
    dayNumber: 1,
    date: '2025-02-26',
    status: 'BLOCKED',
    funds: [],
    totalFunds: 5,
    sentCount: 0,
    blockedReason: 'Awaiting decision',
  },
  {
    dayNumber: 2,
    date: '2025-02-27',
    status: 'READY',
    funds: [],
    totalFunds: 5,
    sentCount: 0,
  },
  {
    dayNumber: 3,
    date: '2025-02-28',
    status: 'IN_PROGRESS',
    funds: [],
    totalFunds: 5,
    sentCount: 2,
  },
  {
    dayNumber: 4,
    date: '2025-03-01',
    status: 'IN_PROGRESS',
    funds: [],
    totalFunds: 5,
    sentCount: 3,
  },
  {
    dayNumber: 5,
    date: '2025-03-02',
    status: 'COMPLETE',
    funds: [],
    totalFunds: 5,
    sentCount: 5,
  },
];

describe('PipelineOverview', () => {
  it('renders all 5 pipeline days', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    expect(screen.getByText('Day 1')).toBeInTheDocument();
    expect(screen.getByText('Day 2')).toBeInTheDocument();
    expect(screen.getByText('Day 3')).toBeInTheDocument();
    expect(screen.getByText('Day 4')).toBeInTheDocument();
    expect(screen.getByText('Day 5')).toBeInTheDocument();
  });

  it('displays correct status labels', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    // Use getAllByText since status appears in both legend and day cards
    expect(screen.getAllByText('Blocked').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Ready').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('In Progress').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Complete').length).toBeGreaterThanOrEqual(1);
  });

  it('displays fund counts', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    const fundCounts = screen.getAllByText('5');
    expect(fundCounts.length).toBeGreaterThanOrEqual(5); // Each day shows "5" for fund count
  });

  it('calls onDayClick when a day is clicked', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    fireEvent.click(screen.getByText('Day 1'));
    expect(onDayClick).toHaveBeenCalledWith(1);
    
    fireEvent.click(screen.getByText('Day 3'));
    expect(onDayClick).toHaveBeenCalledWith(3);
  });

  it('highlights selected day', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} selectedDay={3} />);
    
    // The selected day should have visual indication (checked via class or style)
    const day3Element = screen.getByText('Day 3').closest('button');
    expect(day3Element).toHaveClass('border-blue-500');
  });

  it('displays blocked reason for blocked days', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    expect(screen.getByText('Awaiting decision')).toBeInTheDocument();
  });

  it('renders legend with all status types', () => {
    const days = createMockDays();
    const onDayClick = vi.fn();
    
    render(<PipelineOverview days={days} onDayClick={onDayClick} />);
    
    // Check that all status types appear somewhere in the component
    expect(screen.getAllByText('Blocked').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Ready').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('In Progress').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Complete').length).toBeGreaterThanOrEqual(1);
  });
});
