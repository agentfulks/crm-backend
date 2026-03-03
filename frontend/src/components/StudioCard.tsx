import type { StudioPacket, PacketStatus } from '../types';
import { Edit, Mail, ChevronDown, ChevronUp, Copy, Check, Save, X, Globe, Linkedin, FileText } from 'lucide-react';
import { useState } from 'react';

interface StudioCardProps {
  packet: StudioPacket;
  onClick?: () => void;
  onApprove?: () => void;
  onReject?: () => void;
  onEdit?: () => void;
  onStatusChange?: (newStatus: string) => void;
  onApplyTemplate?: () => void;
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

export function StudioCard({ 
  packet, 
  onClick, 
  onApprove = () => {}, 
  onReject = () => {}, 
  onEdit = () => {}, 
  onStatusChange,
  onApplyTemplate,
  showActions = false 
}: StudioCardProps) {
  const studio = packet.studio;
  const [showEmail, setShowEmail] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [isEditingStatus, setIsEditingStatus] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(packet.status);

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleStatusSave = () => {
    if (onStatusChange && selectedStatus !== packet.status) {
      onStatusChange(selectedStatus);
    }
    setIsEditingStatus(false);
  };

  const handleStatusCancel = () => {
    setSelectedStatus(packet.status);
    setIsEditingStatus(false);
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${priorityColors[packet.priority]}`}>
            Priority {packet.priority}
          </span>
          {isEditingStatus ? (
            <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as PacketStatus)}
                className="text-xs px-2 py-0.5 rounded border border-gray-300 bg-white"
              >
                <option value="NEW">NEW</option>
                <option value="QUEUED">QUEUED</option>
                <option value="AWAITING_APPROVAL">AWAITING APPROVAL</option>
                <option value="APPROVED">APPROVED</option>
                <option value="SENT">SENT</option>
                <option value="FOLLOW_UP">FOLLOW UP</option>
                <option value="CLOSED">CLOSED</option>
              </select>
              <button
                onClick={handleStatusSave}
                className="p-0.5 text-green-600 hover:text-green-700"
                title="Save"
              >
                <Save className="w-3 h-3" />
              </button>
              <button
                onClick={handleStatusCancel}
                className="p-0.5 text-red-600 hover:text-red-700"
                title="Cancel"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditingStatus(true);
              }}
              className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[packet.status]} hover:opacity-80 cursor-pointer`}
              title="Click to edit status"
            >
              {packet.status.replace('_', ' ')}
            </button>
          )}
        </div>
        {packet.score_snapshot && (
          <span className="text-sm font-semibold text-gray-600">
            Score: {packet.score_snapshot}
          </span>
        )}
      </div>
      
      <h3 className="font-semibold text-lg text-gray-900 mb-1">
        {studio?.name || 'Unknown Studio'}
      </h3>
      
      {studio?.studio_type && (
        <p className="text-sm text-gray-600 mb-2">{studio.studio_type}</p>
      )}
      
      {studio?.overview && (
        <p className="text-sm text-gray-700 line-clamp-2 mb-3">
          {studio.overview}
        </p>
      )}

      {/* Contact Info */}
      {packet.contact_name && (
        <div className="mb-3 p-2 bg-blue-50 rounded border border-blue-100">
          <p className="text-sm font-medium text-gray-900">{packet.contact_name}</p>
          <p className="text-xs text-gray-600">{packet.contact_role}</p>
          {packet.contact_email && (
            <p className="text-xs text-blue-600 mt-1">{packet.contact_email}</p>
          )}
          {packet.contact_linkedin && (
            <a
              href={`https://${packet.contact_linkedin}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 mt-1"
              onClick={e => e.stopPropagation()}
            >
              <Linkedin className="w-3 h-3" />
              LinkedIn Profile
            </a>
          )}
        </div>
      )}
      
      {/* Studio Website */}
      {studio?.website_url && (
        <div className="mb-3">
          <a
            href={studio.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
            onClick={e => e.stopPropagation()}
          >
            <Globe className="w-3 h-3" />
            {studio.website_url}
          </a>
        </div>
      )}
      
      <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
        {studio?.hq_city && (
          <span>{studio.hq_city}, {studio.hq_region}</span>
        )}
        {studio?.downloads && (
          <span>{studio.downloads} downloads</span>
        )}
        {studio?.employee_count && (
          <span>{studio.employee_count} employees</span>
        )}
      </div>
      
      {/* Action Buttons */}
      {showActions && (
        <div className="flex gap-2 pt-3 border-t border-gray-100" onClick={e => e.stopPropagation()}>
          {packet.status !== 'APPROVED' && packet.status !== 'SENT' && (
            <button
              onClick={onApprove}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-2 rounded transition-colors"
            >
              Approve
            </button>
          )}
          <button
            onClick={onEdit}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-2 rounded transition-colors flex items-center justify-center gap-1"
          >
            <Edit className="w-4 h-4" />
            Edit
          </button>
          {packet.status !== 'CLOSED' && (
            <button
              onClick={onReject}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 px-2 rounded transition-colors"
            >
              Reject
            </button>
          )}
          {onApplyTemplate && (
            <button
              onClick={onApplyTemplate}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium py-2 px-2 rounded transition-colors flex items-center justify-center gap-1"
            >
              <FileText className="w-4 h-4" />
              Template
            </button>
          )}
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
  );
}
