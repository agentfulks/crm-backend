import { useState } from 'react';
import { usePackets, useApprovePacket, useRejectPacket } from '../hooks/usePackets';
import { PacketEditForm } from './PacketEditForm';
import { X, Globe, Linkedin, Mail, MapPin, DollarSign, Calendar, CheckCircle, XCircle, Edit } from 'lucide-react';

interface PacketDetailProps {
  packetId: string;
  onClose: () => void;
}

export function PacketDetail({ packetId, onClose }: PacketDetailProps) {
  const { data: packetsData, isLoading } = usePackets();
  const packet = packetsData?.items?.find((p: any) => p.id === packetId);
  const approveMutation = useApprovePacket();
  const rejectMutation = useRejectPacket();
  const [actionTaken, setActionTaken] = useState<'approved' | 'rejected' | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-2xl w-full p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4 w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
        </div>
      </div>
    );
  }
  
  if (!packet) return null;

  const fund = packet.fund;

  const handleApprove = async () => {
    await approveMutation.mutateAsync(packetId);
    setActionTaken('approved');
    setTimeout(onClose, 1500);
  };

  const handleReject = async () => {
    await rejectMutation.mutateAsync(packetId);
    setActionTaken('rejected');
    setTimeout(onClose, 1500);
  };

  if (isEditing) {
    return (
      <PacketEditForm
        packet={packet}
        onClose={() => setIsEditing(false)}
        onSaved={() => setIsEditing(false)}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">Packet Details</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Status & Priority */}
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              packet.priority === 'A' ? 'bg-red-100 text-red-800' :
              packet.priority === 'B' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              Priority {packet.priority}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              packet.status === 'AWAITING_APPROVAL' ? 'bg-yellow-100 text-yellow-800' :
              packet.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
              packet.status === 'CLOSED' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {packet.status.replace('_', ' ')}
            </span>
            {packet.score_snapshot && (
              <span className="px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                Score: {packet.score_snapshot}
              </span>
            )}
          </div>
          
          {/* Fund Info */}
          {fund && (
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{fund.name}</h3>
              {fund.firm_type && (
                <p className="text-gray-600 mb-4">{fund.firm_type}</p>
              )}
              
              {fund.overview && (
                <p className="text-gray-700 mb-4">{fund.overview}</p>
              )}
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                {fund.hq_city && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>{fund.hq_city}, {fund.hq_region}</span>
                  </div>
                )}
                {fund.check_size_min && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <DollarSign className="w-4 h-4" />
                    <span>${(fund.check_size_min / 1000000).toFixed(1)}M - ${(fund.check_size_max || fund.check_size_min / 1000000).toFixed(1)}M</span>
                  </div>
                )}
                {fund.contact_email && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <a href={`mailto:${fund.contact_email}`} className="text-blue-600 hover:underline">
                      {fund.contact_email}
                    </a>
                  </div>
                )}
                {fund.website_url && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Globe className="w-4 h-4" />
                    <a href={fund.website_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      Website
                    </a>
                  </div>
                )}
                {fund.linkedin_url && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Linkedin className="w-4 h-4" />
                    <a href={fund.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      LinkedIn
                    </a>
                  </div>
                )}
              </div>
              
              {fund.stage_focus && fund.stage_focus.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Stage Focus</p>
                  <div className="flex flex-wrap gap-2">
                    {fund.stage_focus.map((stage) => (
                      <span key={stage} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                        {stage}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Timestamps */}
          <div className="border-t border-gray-200 pt-4 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>Created: {new Date(packet.created_at).toLocaleDateString()}</span>
            </div>
            {packet.approved_at && (
              <div className="flex items-center gap-2 mt-1">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Approved: {new Date(packet.approved_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
          
          {/* Action Buttons */}
          {packet.status === 'AWAITING_APPROVAL' && !actionTaken && (
            <div className="flex gap-3 pt-4 border-t border-gray-200">
              <button
                onClick={handleApprove}
                disabled={approveMutation.isPending}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" />
                {approveMutation.isPending ? 'Approving...' : 'Approve Packet'}
              </button>
              <button
                onClick={handleReject}
                disabled={rejectMutation.isPending}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <XCircle className="w-5 h-5" />
                {rejectMutation.isPending ? 'Rejecting...' : 'Reject Packet'}
              </button>
            </div>
          )}
          
          {actionTaken === 'approved' && (
            <div className="p-4 bg-green-50 text-green-800 rounded-lg text-center font-medium">
              <CheckCircle className="w-6 h-6 inline-block mr-2" />
              Packet approved successfully!
            </div>
          )}
          
          {actionTaken === 'rejected' && (
            <div className="p-4 bg-red-50 text-red-800 rounded-lg text-center font-medium">
              <XCircle className="w-6 h-6 inline-block mr-2" />
              Packet rejected.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
