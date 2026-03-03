import { useState } from 'react';
import { useUpdatePacketStatus } from '../hooks/usePackets';
import type { Packet } from '../types';
import { X, Save } from 'lucide-react';

interface PacketEditFormProps {
  packet: Packet;
  onClose: () => void;
  onSaved?: () => void;
}

export function PacketEditForm({ packet, onClose, onSaved }: PacketEditFormProps) {
  const updateMutation = useUpdatePacketStatus();
  const [status, setStatus] = useState(packet.status);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSave = async () => {
    setIsSubmitting(true);
    try {
      await updateMutation.mutateAsync({ id: packet.id, status });
      onSaved?.();
      onClose();
    } catch (error) {
      console.error('Failed to update:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Edit Status</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fund: {packet.fund?.name || 'Unknown'}
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="NEW">NEW</option>
              <option value="QUEUED">QUEUED</option>
              <option value="AWAITING_APPROVAL">AWAITING APPROVAL</option>
              <option value="APPROVED">APPROVED</option>
              <option value="SENT">SENT</option>
              <option value="FOLLOW_UP">FOLLOW UP</option>
              <option value="CLOSED">CLOSED</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={handleSave}
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
