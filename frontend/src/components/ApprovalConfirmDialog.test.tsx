import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ApprovalConfirmDialog } from './ApprovalConfirmDialog';

describe('ApprovalConfirmDialog', () => {
  const defaultProps = {
    isOpen: true,
    action: 'approve' as const,
    packetName: 'Test Fund',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
    isLoading: false,
  };

  it('renders nothing when isOpen is false', () => {
    const { container } = render(
      <ApprovalConfirmDialog {...defaultProps} isOpen={false} />
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('renders approve dialog correctly', () => {
    render(<ApprovalConfirmDialog {...defaultProps} action="approve" />);
    
    expect(screen.getByText('Approve Packet?')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to approve "Test Fund"/)).toBeInTheDocument();
    expect(screen.getByText('Yes, Approve')).toBeInTheDocument();
  });

  it('renders reject dialog correctly', () => {
    render(<ApprovalConfirmDialog {...defaultProps} action="reject" />);
    
    expect(screen.getByText('Reject Packet?')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to reject "Test Fund"/)).toBeInTheDocument();
    expect(screen.getByText('Yes, Reject')).toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', () => {
    const onConfirm = vi.fn();
    render(<ApprovalConfirmDialog {...defaultProps} onConfirm={onConfirm} />);
    
    fireEvent.click(screen.getByText('Yes, Approve'));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn();
    render(<ApprovalConfirmDialog {...defaultProps} onCancel={onCancel} />);
    
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when isLoading is true', () => {
    render(<ApprovalConfirmDialog {...defaultProps} isLoading={true} />);
    
    const cancelButton = screen.getByText('Cancel');
    // The confirm button has a span inside when loading, so we need to find it differently
    const confirmButton = cancelButton.parentElement?.querySelector('button:last-child');
    
    expect(cancelButton).toBeDisabled();
    expect(confirmButton).toBeDisabled();
  });

  it('shows loading spinner when isLoading is true', () => {
    render(<ApprovalConfirmDialog {...defaultProps} isLoading={true} />);
    
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('displays green styling for approve action', () => {
    render(<ApprovalConfirmDialog {...defaultProps} action="approve" />);
    
    const confirmButton = screen.getByText('Yes, Approve');
    expect(confirmButton.className).toContain('bg-green-600');
  });

  it('displays red styling for reject action', () => {
    render(<ApprovalConfirmDialog {...defaultProps} action="reject" />);
    
    const confirmButton = screen.getByText('Yes, Reject');
    expect(confirmButton.className).toContain('bg-red-600');
  });
});
