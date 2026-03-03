import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BatchDetailView } from '../BatchDetailView';
import type { BatchDetail, PipelineFund } from '../../../types/dashboard';

const createMockFund = (overrides: Partial<PipelineFund> = {}): PipelineFund => ({
  id: 'fund-1',
  fundId: 'fund-id-1',
  fundName: 'Accel Partners',
  partnerName: 'John Doe',
  fitScore: 85,
  priority: 'A',
  status: 'AWAITING_APPROVAL',
  contactEmail: 'john@accel.com',
  linkedinUrl: 'https://linkedin.com/in/johndoe',
  emailDraft: {
    to: 'john@accel.com',
    subject: 'Test Subject',
    body: 'Test email body content',
  },
  ...overrides,
});

const createMockBatch = (overrides: Partial<BatchDetail> = {}): BatchDetail => ({
  dayNumber: 1,
  date: '2025-02-26',
  status: 'READY',
  funds: [
    createMockFund(),
    createMockFund({ id: 'fund-2', fundName: 'Bessemer', status: 'SENT' }),
    createMockFund({ id: 'fund-3', fundName: 'Index Ventures', priority: 'B' }),
  ],
  ...overrides,
});

describe('BatchDetailView', () => {
  it('renders empty state when no batch is selected', () => {
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={null}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    expect(screen.getByText('Select a Day')).toBeInTheDocument();
    expect(screen.getByText('Click on a pipeline day to view fund details')).toBeInTheDocument();
  });

  it('renders batch details correctly', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    expect(screen.getByText('Day 1 Details')).toBeInTheDocument();
    expect(screen.getByText('Accel Partners')).toBeInTheDocument();
    expect(screen.getByText('Bessemer')).toBeInTheDocument();
    expect(screen.getByText('Index Ventures')).toBeInTheDocument();
  });

  it('displays fund information correctly', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    // Use getAllByText since these values appear in multiple fund rows
    expect(screen.getAllByText('John Doe').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Fit Score: 85').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('john@accel.com').length).toBeGreaterThanOrEqual(1);
  });

  it('displays priority badges', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    expect(screen.getAllByText('Priority A').length).toBeGreaterThan(0);
    expect(screen.getByText('Priority B')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    // Find close button by looking for the X icon button (first button in header)
    const closeButtons = screen.getAllByRole('button');
    const closeButton = closeButtons.find(btn => btn.querySelector('svg'));
    expect(closeButton).toBeDefined();
    fireEvent.click(closeButton!);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onMarkAsSent when mark as sent button is clicked', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    const markAsSentButtons = screen.getAllByText('Mark as Sent');
    fireEvent.click(markAsSentButtons[0]);
    expect(onMarkAsSent).toHaveBeenCalledWith('fund-1');
  });

  it('calls onScheduleFollowUp when schedule follow-up button is clicked', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    const scheduleButtons = screen.getAllByText('Schedule Follow-up');
    fireEvent.click(scheduleButtons[0]);
    expect(onScheduleFollowUp).toHaveBeenCalledWith('fund-1');
  });

  it('toggles email draft visibility when view email button is clicked', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    // Click to show email
    const viewEmailButtons = screen.getAllByText('View Email Draft');
    fireEvent.click(viewEmailButtons[0]);
    
    expect(screen.getByText('Test Subject')).toBeInTheDocument();
    expect(screen.getByText('Test email body content')).toBeInTheDocument();
    
    // Click to hide email
    const hideEmailButton = screen.getByText('Hide Email');
    fireEvent.click(hideEmailButton);
  });

  it('displays progress correctly', () => {
    const batch = createMockBatch();
    const onClose = vi.fn();
    const onViewEmailDraft = vi.fn();
    const onMarkAsSent = vi.fn();
    const onScheduleFollowUp = vi.fn();
    
    render(
      <BatchDetailView
        batch={batch}
        onClose={onClose}
        onViewEmailDraft={onViewEmailDraft}
        onMarkAsSent={onMarkAsSent}
        onScheduleFollowUp={onScheduleFollowUp}
      />
    );
    
    expect(screen.getByText('1 of 3 sent')).toBeInTheDocument();
  });
});
