import type { ApprovalCard } from '../../types/approval';
import { X, CheckCircle, XCircle, ArrowUp, Clock, User, Building2, Mail, Linkedin } from 'lucide-react';

interface CardDetailProps {
  card: ApprovalCard;
  onClose: () => void;
  onAction: (action: string) => void;
}

export function CardDetail({ card, onClose, onAction }: CardDetailProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`px-6 py-4 border-b ${
          card.classification.tier === 1 ? 'bg-green-50 border-green-200' :
          card.classification.tier === 2 ? 'bg-yellow-50 border-yellow-200' :
          'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={`text-xs font-bold px-2 py-1 rounded ${
                card.classification.tier === 1 ? 'bg-green-500 text-white' :
                card.classification.tier === 2 ? 'bg-yellow-500 text-white' :
                'bg-red-500 text-white'
              }`}>
                TIER {card.classification.tier}
              </span>
              <span className="text-sm text-gray-500">{card.type}</span>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mt-3">{card.companyName}</h2>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Contact Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">{card.contact.name}</div>
                <div className="text-sm text-gray-500">{card.contact.role}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">{card.companyName}</div>
                <div className="text-sm text-gray-500">{card.type === 'VC' ? 'Investor' : 'Partner'}</div>
              </div>
            </div>
          </div>

          {/* Contact Details */}
          <div className="space-y-2">
            {card.contact.email && (
              <div className="flex items-center gap-2 text-sm">
                <Mail className="w-4 h-4 text-gray-400" />
                <a href={`mailto:${card.contact.email}`} className="text-blue-600 hover:underline">
                  {card.contact.email}
                </a>
                {card.contact.emailVerified && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Verified</span>
                )}
              </div>
            )}
            {card.contact.linkedinUrl && (
              <div className="flex items-center gap-2 text-sm">
                <Linkedin className="w-4 h-4 text-gray-400" />
                <a href={card.contact.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  LinkedIn Profile
                </a>
              </div>
            )}
          </div>

          {/* ICP & Classification */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <span className="text-sm text-gray-500">ICP Score</span>
                <div className={`text-xl font-bold ${
                  card.icpScore >= 4 ? 'text-green-600' :
                  card.icpScore >= 3 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {card.icpScore}/5
                </div>
              </div>
              <div className="text-right">
                <span className="text-sm text-gray-500">Confidence</span>
                <div className="text-xl font-bold text-blue-600">
                  {card.classification.confidence}%
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              <strong>Classification:</strong> {card.classification.reason}
            </div>
          </div>

          {/* Signals */}
          {card.signals && card.signals.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                Signals
              </h4>
              <div className="space-y-2">
                {card.signals.map((signal, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <Clock className="w-4 h-4 text-gray-400 mt-0.5" />
                    <div>
                      <span className="font-medium capitalize">{signal.type.replace('_', ' ')}:</span>
                      {' '}{signal.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
          <button
            onClick={() => onAction('approve')}
            className="flex-1 py-2 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-4 h-4" />
            Approve
          </button>
          <button
            onClick={() => onAction('reject')}
            className="flex-1 py-2 px-4 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 flex items-center justify-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
          {card.classification.tier !== 3 && (
            <button
              onClick={() => onAction('escalate')}
              className="flex-1 py-2 px-4 bg-yellow-600 text-white font-medium rounded-lg hover:bg-yellow-700 flex items-center justify-center gap-2"
            >
              <ArrowUp className="w-4 h-4" />
              Escalate
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
