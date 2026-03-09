import { useState } from 'react';
import type { Packet, PacketStatus } from '../types';
import { Edit, Mail, ChevronDown, ChevronUp, Copy, Check, ClipboardCheck } from 'lucide-react';
import { AddToKanbanModal } from './AddToKanbanModal';

interface PacketCardProps {
  packet: Packet;
  onClick?: () => void;
  onApprove?: () => void;
  onReject?: () => void;
  onEdit?: () => void;
  showActions?: boolean;
}

const statusColors: Record<PacketStatus, string> = {
  NEW: 'bg-gray-200 text-gray-700',
  QUEUED: 'bg-gray-100 text-gray-800',
  AWAITING_APPROVAL: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  SENT: 'bg-blue-100 text-blue-800',
  FOLLOW_UP: 'bg-purple-100 text-purple-800',
  CLOSED: 'bg-red-100 text-red-800',
};

const priorityColors: Record<string, string> = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-500 text-white',
  C: 'bg-gray-500 text-white',
};

export function PacketCard({ packet, onClick, onApprove, onReject, onEdit, showActions = false }: PacketCardProps) {
  const fund = packet.fund;
  const [showEmail, setShowEmail] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showKanban, setShowKanban] = useState(false);

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  return (
    <>
      <div
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
        onClick={onClick}
      >
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${priorityColors[packet.priority]}`}>
              Priority {packet.priority}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[packet.status]}`}>
              {packet.status.replace('_', ' ')}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {packet.score_snapshot && (
              <span className="text-sm font-semibold text-gray-600">
                Score: {packet.score_snapshot}
              </span>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); setShowKanban(true); }}
              className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-2 py-1 rounded-lg transition-colors"
              title="Add to Tasks board"
            >
              <ClipboardCheck className="w-3.5 h-3.5" />
              Tasks
            </button>
          </div>
        </div>

        <h3 className="font-semibold text-lg text-gray-900 mb-1">
          {fund?.name || 'Unknown Fund'}
        </h3>

        {fund?.firm_type && (
          <p className="text-sm text-gray-600 mb-2">{fund.firm_type}</p>
        )}

        {fund?.overview && (
          <p className="text-sm text-gray-700 line-clamp-2 mb-3">
            {fund.overview}
          </p>
        )}

        <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
          {fund?.hq_city && (
            <span>{fund.hq_city}, {fund.hq_region}</span>
          )}
          {fund?.check_size_min && (
            <span>
              ${(fund.check_size_min / 1000000).toFixed(1)}M - ${((fund.check_size_max || fund.check_size_min) / 1000000).toFixed(1)}M
            </span>
          )}
        </div>

        {showActions && packet.status === 'AWAITING_APPROVAL' && (
          <div className="flex gap-2 pt-3 border-t border-gray-100" onClick={e => e.stopPropagation()}>
            <button
              onClick={onApprove}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-4 rounded transition-colors"
            >
              Approve
            </button>
            <button
              onClick={onEdit}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center justify-center gap-1"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={onReject}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 px-4 rounded transition-colors"
            >
              Reject
            </button>
          </div>
        )}

        {/* Email Draft Section */}
        {packet.email_draft && (
          <div className="mt-4 pt-4 border-t border-gray-100" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setShowEmail(!showEmail)}
              className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors w-full"
            >
              <Mail className="w-4 h-4" />
              {showEmail ? 'Hide Email Draft' : 'Show Email Draft'}
              {showEmail ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showEmail && (
              <div className="mt-3 space-y-3">
                {/* To */}
                <div>
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-gray-500 uppercase">To</label>
                    <button
                      onClick={() => handleCopy(packet.email_draft!.to, 'to')}
                      className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                      {copiedField === 'to' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                    </button>
                  </div>
                  <div className="mt-1 p-2 bg-gray-50 rounded text-sm text-gray-900 font-mono">
                    {packet.email_draft.to}
                  </div>
                </div>

                {/* Subject */}
                <div>
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-gray-500 uppercase">Subject</label>
                    <button
                      onClick={() => handleCopy(packet.email_draft!.subject, 'subject')}
                      className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                      {copiedField === 'subject' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                    </button>
                  </div>
                  <div className="mt-1 p-2 bg-gray-50 rounded text-sm text-gray-900">
                    {packet.email_draft.subject}
                  </div>
                </div>

                {/* Body */}
                <div>
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-gray-500 uppercase">Body</label>
                    <button
                      onClick={() => handleCopy(packet.email_draft!.body, 'body')}
                      className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                      {copiedField === 'body' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                    </button>
                  </div>
                  <div className="mt-1 p-3 bg-gray-50 rounded text-sm text-gray-900 whitespace-pre-wrap font-mono leading-relaxed max-h-64 overflow-y-auto">
                    {packet.email_draft.body}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {showKanban && (
        <AddToKanbanModal
          source={{
            type: 'vc',
            id: packet.id,
            title: fund?.name || 'VC Fund',
            data: {
              name: fund?.name,
              firm_type: fund?.firm_type,
              hq_city: fund?.hq_city,
              hq_country: fund?.hq_country,
              priority: packet.priority,
              status: packet.status,
              score: packet.score_snapshot,
              website_url: fund?.website_url,
            },
          }}
          onClose={() => setShowKanban(false)}
        />
      )}
    </>
  );
}
