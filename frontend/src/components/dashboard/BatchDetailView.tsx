import { useState } from 'react';
import { 
  X, Mail, CheckCircle, Clock, MessageSquare, 
  ChevronDown, ChevronUp, Copy, Check, User, Linkedin
} from 'lucide-react';
import type { BatchDetailViewProps, PipelineFund } from '../../types/dashboard';

const priorityColors: Record<string, string> = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-500 text-white',
  C: 'bg-gray-500 text-white',
};

const statusColors: Record<string, string> = {
  QUEUED: 'bg-gray-100 text-gray-800',
  AWAITING_APPROVAL: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  SENT: 'bg-blue-100 text-blue-800',
  FOLLOW_UP: 'bg-purple-100 text-purple-800',
  CLOSED: 'bg-red-100 text-red-800',
};

function FundRow({ 
  fund, 
  onViewEmailDraft,
  onMarkAsSent, 
  onScheduleFollowUp 
}: { 
  fund: PipelineFund;
  onViewEmailDraft: (fundId: string) => void;
  onMarkAsSent: (fundId: string) => void;
  onScheduleFollowUp: (fundId: string) => void;
}) {
  const [showEmail, setShowEmail] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Fund Header */}
      <div className="p-4 bg-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${priorityColors[fund.priority]}`}>
                Priority {fund.priority}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[fund.status]}`}>
                {fund.status.replace('_', ' ')}
              </span>
            </div>
            <h3 className="text-base font-semibold text-gray-900">{fund.fundName}</h3>
            <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
              <User className="w-4 h-4" />
              <span>{fund.partnerName}</span>
              <span className="text-gray-300">|</span>
              <span className="font-medium text-gray-900">Fit Score: {fund.fitScore}</span>
            </div>
          </div>
          
          {/* Contact Actions */}
          <div className="flex items-center gap-2">
            {fund.linkedinUrl && (
              <a
                href={fund.linkedinUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="View LinkedIn"
              >
                <Linkedin className="w-4 h-4" />
              </a>
            )}
            {fund.contactEmail && (
              <a
                href={`mailto:${fund.contactEmail}`}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Send Email"
              >
                <Mail className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>
        
        {/* Contact Info */}
        <div className="mt-3 flex items-center gap-4 text-sm">
          {fund.contactEmail && (
            <div className="flex items-center gap-1.5 text-gray-600">
              <Mail className="w-3.5 h-3.5" />
              <span>{fund.contactEmail}</span>
            </div>
          )}
        </div>
        
        {/* Quick Actions */}
        <div className="mt-4 flex items-center gap-2">
          {fund.emailDraft && (
            <button
              onClick={() => {
                setShowEmail(!showEmail);
                onViewEmailDraft(fund.id);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Mail className="w-4 h-4" />
              {showEmail ? 'Hide Email' : 'View Email Draft'}
              {showEmail ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
          
          {fund.status !== 'SENT' && (
            <button
              onClick={() => onMarkAsSent(fund.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            >
              <CheckCircle className="w-4 h-4" />
              Mark as Sent
            </button>
          )}
          
          <button
            onClick={() => onScheduleFollowUp(fund.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
          >
            <Clock className="w-4 h-4" />
            Schedule Follow-up
          </button>
        </div>
      </div>
      
      {/* Email Draft Section */}
      {showEmail && fund.emailDraft && (
        <div className="border-t border-gray-200 bg-gray-50 p-4">
          <div className="space-y-3">
            {/* To */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-medium text-gray-500 uppercase">To</label>
                <button
                  onClick={() => handleCopy(fund.emailDraft!.to, 'to')}
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  {copiedField === 'to' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                </button>
              </div>
              <div className="p-2 bg-white border border-gray-200 rounded text-sm text-gray-900 font-mono">
                {fund.emailDraft.to}
              </div>
            </div>
            
            {/* Subject */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-medium text-gray-500 uppercase">Subject</label>
                <button
                  onClick={() => handleCopy(fund.emailDraft!.subject, 'subject')}
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  {copiedField === 'subject' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                </button>
              </div>
              <div className="p-2 bg-white border border-gray-200 rounded text-sm text-gray-900">
                {fund.emailDraft.subject}
              </div>
            </div>
            
            {/* Body */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-medium text-gray-500 uppercase">Body</label>
                <button
                  onClick={() => handleCopy(fund.emailDraft!.body, 'body')}
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  {copiedField === 'body' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                </button>
              </div>
              <div className="p-3 bg-white border border-gray-200 rounded text-sm text-gray-900 whitespace-pre-wrap font-mono leading-relaxed max-h-64 overflow-y-auto">
                {fund.emailDraft.body}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function BatchDetailView({ 
  batch, 
  onClose, 
  onViewEmailDraft, 
  onMarkAsSent, 
  onScheduleFollowUp 
}: BatchDetailViewProps) {
  if (!batch) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-1">Select a Day</h3>
        <p className="text-gray-500">Click on a pipeline day to view fund details</p>
      </div>
    );
  }

  const sentCount = batch.funds.filter(f => f.status === 'SENT').length;
  const progressPercent = (sentCount / batch.funds.length) * 100;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-lg font-semibold text-gray-900">Day {batch.dayNumber} Details</h2>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[batch.status]}`}>
                {batch.status.replace('_', ' ')}
              </span>
            </div>
            <p className="text-sm text-gray-500">
              {new Date(batch.date).toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Progress */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Progress</span>
            <span className="font-medium text-gray-900">{sentCount} of {batch.funds.length} sent</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>
      
      {/* Fund List */}
      <div className="p-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Funds ({batch.funds.length})</h3>
        <div className="space-y-4">
          {batch.funds.map((fund) => (
            <FundRow
              key={fund.id}
              fund={fund}
              onViewEmailDraft={onViewEmailDraft}
              onMarkAsSent={onMarkAsSent}
              onScheduleFollowUp={onScheduleFollowUp}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default BatchDetailView;
