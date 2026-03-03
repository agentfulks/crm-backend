import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DecisionQueue } from '../DecisionQueue';
import type { DecisionQueueItem } from '../../../types/dashboard';

const createMockDecisionItem = (overrides: Partial<DecisionQueueItem> = {}): DecisionQueueItem => ({
  id: 'decision-1',
  type: 'BATCH_SEND',
  title: 'Day 1 Batch Send Approval',
  description: 'Please approve the Day 1 batch send.',
  dayNumber: 1,
  deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
  blockedSince: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // Yesterday
  options: [
    {
      id: 'option-a',
      label: 'Send Now',
      value: 'send_now',
      description: 'Send immediately',
    },
    {
      id: 'option-b',
      label: 'Hold',
      value: 'hold',
      description: 'Hold for later',
    },
  ],
  recommendation: 'option-a',
  ...overrides,
});

describe('DecisionQueue', () => {
  it('renders empty state when no items', () => {
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={[]} onDecision={onDecision} />);
    
    expect(screen.getByText('Decision Queue')).toBeInTheDocument();
    expect(screen.getByText('No decisions pending')).toBeInTheDocument();
    expect(screen.getByText('All items are flowing smoothly')).toBeInTheDocument();
  });

  it('renders decision items', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('Day 1 Batch Send Approval')).toBeInTheDocument();
    expect(screen.getByText('Please approve the Day 1 batch send.')).toBeInTheDocument();
  });

  it('displays item count in header', () => {
    const items = [
      createMockDecisionItem(),
      createMockDecisionItem({ id: 'decision-2', title: 'Second Decision' }),
    ];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('2 items requiring your input')).toBeInTheDocument();
  });

  it('displays single item text correctly', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('1 item requiring your input')).toBeInTheDocument();
  });

  it('renders all options for a decision', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('Send Now')).toBeInTheDocument();
    expect(screen.getByText('Hold')).toBeInTheDocument();
    expect(screen.getByText('Send immediately')).toBeInTheDocument();
    expect(screen.getByText('Hold for later')).toBeInTheDocument();
  });

  it('shows recommended option', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('Recommended')).toBeInTheDocument();
  });

  it('allows selecting an option', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    // Use getByText to find the label and then find the radio input within it
    const sendNowLabel = screen.getByText('Send Now').closest('label');
    expect(sendNowLabel).toBeInTheDocument();
    const radioInput = sendNowLabel?.querySelector('input[type="radio"]') as HTMLInputElement;
    fireEvent.click(radioInput);
    
    expect(radioInput).toBeChecked();
  });

  it('calls onDecision when confirm button is clicked with selection', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    // Select an option by clicking on the radio input
    const sendNowLabel = screen.getByText('Send Now').closest('label');
    const sendNowOption = sendNowLabel?.querySelector('input[type="radio"]') as HTMLInputElement;
    fireEvent.click(sendNowOption);
    
    // Click confirm
    const confirmButton = screen.getByText('Confirm Decision');
    fireEvent.click(confirmButton);
    
    expect(onDecision).toHaveBeenCalledWith('decision-1', 'option-a');
  });

  it('disables confirm button when no option selected', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    const confirmButton = screen.getByText('Confirm Decision');
    expect(confirmButton).toBeDisabled();
  });

  it('displays countdown timer for deadline', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    // Should show remaining time (format may vary)
    expect(screen.getByText(/remaining/)).toBeInTheDocument();
  });

  it('shows blocked since timestamp', () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText(/Blocked since/)).toBeInTheDocument();
  });

  it('renders multiple decision items', () => {
    const items = [
      createMockDecisionItem(),
      createMockDecisionItem({ 
        id: 'decision-2', 
        title: 'Second Decision',
        type: 'FOLLOW_UP',
        recommendation: undefined,
      }),
    ];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    expect(screen.getByText('Day 1 Batch Send Approval')).toBeInTheDocument();
    expect(screen.getByText('Second Decision')).toBeInTheDocument();
  });

  it('shows success state after decision is made', async () => {
    const items = [createMockDecisionItem()];
    const onDecision = vi.fn();
    
    render(<DecisionQueue items={items} onDecision={onDecision} />);
    
    // Select and confirm
    const sendNowLabel = screen.getByText('Send Now').closest('label');
    const sendNowOption = sendNowLabel?.querySelector('input[type="radio"]') as HTMLInputElement;
    fireEvent.click(sendNowOption);
    
    const confirmButton = screen.getByText('Confirm Decision');
    fireEvent.click(confirmButton);
    
    // Should show success state
    await waitFor(() => {
      expect(screen.getByText('Decision recorded')).toBeInTheDocument();
    });
  });
});
