import { useState } from 'react';
import { useApproval } from '../../hooks/useApproval';
import type { ApprovalCard } from '../../types/approval';
import { CheckCircle, XCircle, ArrowLeft, AlertTriangle, Loader2 } from 'lucide-react';

interface Tier3DeepReviewProps {
  onClose: () => void;
  onAction: (action: string, card?: ApprovalCard) => void;
}

export function Tier3DeepReview({ onClose, onAction }: Tier3DeepReviewProps) {
  const { data: cards, isLoading } = useApproval({ tier: 3, status: 'PENDING' });
  const [currentIndex, setCurrentIndex] = useState(0);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentCard = cards?.[currentIndex];
  const hasNext = currentIndex < (cards?.length || 0) - 1;
  const hasPrev = currentIndex > 0;

  const handleApprove = async () => {
    if (!currentCard) return;
    setIsSubmitting(true);
    try {
      // API call would go here
      onAction('approve', currentCard);
      if (hasNext) setCurrentIndex(i => i + 1);
      setNotes('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!currentCard) return;
    setIsSubmitting(true);
    try {
      onAction('reject', currentCard);
      if (hasNext) setCurrentIndex(i => i + 1);
      setNotes('');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!currentCard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-800">All caught up!</h3>
          <p className="text-gray-600 mb-4">No more Tier 3 cards to review.</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const { contact, classification, signals, icpScore, type, companyName } = currentCard;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-red-50 border-b border-red-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
              TIER 3 — DEEP REVIEW
            </span>
            <span className="text-sm text-gray-600">
              Card {currentIndex + 1} of {cards?.length || 0}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            Target: 4-5 min per card
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-xl border border-red-200 shadow-lg overflow-hidden">
          {/* Card Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {type}
                </span>
                <h1 className="text-3xl font-bold text-gray-900 mt-1">{companyName}</h1>
              </div>
              <div className="text-right">
                <div className="text-lg font-medium text-gray-900">{contact.name}</div>
                <div className="text-gray-500">{contact.role}</div>
                {contact.email && (
                  <div className="text-sm text-blue-600 mt-1">{contact.email}</div>
                )}
                {contact.linkedinUrl && (
                  <a 
                    href={contact.linkedinUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    View LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Full Details */}
          <div className="p-6 space-y-6">
            {/* ICP Score */}
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                ICP Score
              </h3>
              <div className="flex items-center gap-2">
                <div className={`text-2xl font-bold ${
                  icpScore >= 4 ? 'text-green-600' : icpScore >= 3 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {icpScore}/5
                </div>
                <div className="text-sm text-gray-500">
                  {icpScore >= 4 ? 'Strong fit' : icpScore >= 3 ? 'Moderate fit' : 'Weak fit'}
                </div>
              </div>
            </div>

            {/* Classification Info */}
            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-red-900">Why Tier 3</h4>
                  <p className="text-red-700 mt-1">{classification.reason}</p>
                  <div className="mt-2 text-sm text-red-600">
                    Confidence: {classification.confidence}% | Rules met: {classification.rulesTriggered.join(', ')}
                  </div>
                </div>
              </div>
            </div>

            {/* All Signals */}
            {signals && signals.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  All Signals ({signals.length})
                </h3>
                <div className="space-y-3">
                  {signals.map((signal, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 flex-shrink-0" />
                      <div>
                        <span className="text-sm font-medium text-gray-700">{signal.type.replace('_', ' ')}</span>
                        <p className="text-sm text-gray-600 mt-1">{signal.description}</p>
                        <span className="text-xs text-gray-400">
                          {new Date(signal.date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strategic Notes */}
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Strategic Notes
              </h3>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add your strategic assessment..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                rows={4}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex gap-4">
              <button
                onClick={handleApprove}
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle className="w-5 h-5" />}
                Approve
              </button>
              <button
                onClick={handleReject}
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <XCircle className="w-5 h-5" />}
                Reject
              </button>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={() => setCurrentIndex(i => i - 1)}
                disabled={!hasPrev}
                className="text-gray-600 hover:text-gray-900 disabled:opacity-50"
              >
                ← Previous
              </button>
              <button
                onClick={() => setCurrentIndex(i => i + 1)}
                disabled={!hasNext}
                className="text-gray-600 hover:text-gray-900 disabled:opacity-50"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
