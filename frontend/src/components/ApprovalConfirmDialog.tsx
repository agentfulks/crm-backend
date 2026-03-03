import { AlertTriangle, CheckCircle } from 'lucide-react';

interface ApprovalConfirmDialogProps {
  isOpen: boolean;
  action: 'approve' | 'reject';
  packetName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ApprovalConfirmDialog({
  isOpen,
  action,
  packetName,
  onConfirm,
  onCancel,
  isLoading = false,
}: ApprovalConfirmDialogProps) {
  if (!isOpen) return null;

  const isApprove = action === 'approve';
  const title = isApprove ? 'Approve Packet?' : 'Reject Packet?';
  const message = isApprove
    ? `Are you sure you want to approve "${packetName}"? This will mark the packet as ready to send.`
    : `Are you sure you want to reject "${packetName}"? This will close the packet.`;
  const confirmText = isApprove ? 'Yes, Approve' : 'Yes, Reject';
  const Icon = isApprove ? CheckCircle : AlertTriangle;
  const iconColor = isApprove ? 'text-green-600' : 'text-red-600';
  const buttonColor = isApprove
    ? 'bg-green-600 hover:bg-green-700 disabled:bg-green-400'
    : 'bg-red-600 hover:bg-red-700 disabled:bg-red-400';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-full ${isApprove ? 'bg-green-100' : 'bg-red-100'}`}>
            <Icon className={`w-6 h-6 ${iconColor}`} />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
            <p className="text-gray-600 mb-6">{message}</p>

            <div className="flex gap-3">
              <button
                onClick={onCancel}
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={onConfirm}
                disabled={isLoading}
                className={`flex-1 px-4 py-2 text-white font-medium rounded-lg transition-colors ${buttonColor}`}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Processing...
                  </span>
                ) : (
                  confirmText
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
