import { useState, useCallback } from 'react';
import { useApproval } from '../../hooks/useApproval';
import type { ApprovalCard } from '../../types/approval';
import { CheckCircle, XCircle, ArrowUp, AlertCircle, Clock, ChevronRight, ChevronLeft } from 'lucide-react';

interface Tier2QuickReviewProps {
  cards: ApprovalCard[];
  onApprove: (cardId: string, notes?: string) => void;
  onReject: (cardId: string, reason?: string) => void;
  onEscalate: (cardId: string, reason: string) => void;
}

export function Tier2QuickReview({ cards, onApprove, onReject, onEscalate }: Tier2QuickReviewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [notes, setNotes] = useState('');
  const [showEscalateInput, setShowEscalateInput] = useState(false);
  const [escalateReason, setEscalateReason] = useState('');

  const currentCard = cards[currentIndex];
  const hasNext = currentIndex < cards.length - 1;
  const hasPrev = currentIndex > 0;

  const handleApprove = useCallback(() => {
    if (currentCard) {
      onApprove(currentCard.id, notes);
      setNotes('');
      if (hasNext) setCurrentIndex(i => i + 1);
    }
  }, [currentCard, hasNext, notes, onApprove]);

  const handleReject = useCallback(() => {
    if (currentCard) {
      onReject(currentCard.id, notes);
      setNotes('');
      if (hasNext) setCurrentIndex(i => i + 1);
    }
  }, [currentCard, hasNext, notes, onReject]);

  const handleEscalate = useCallback(() => {
    if (currentCard && escalateReason) {
      onEscalate(currentCard.id, escalateReason);
      setEscalateReason('');
      setShowEscalateInput(false);
      if (hasNext) setCurrentIndex(i => i + 1);
    }
  }, [currentCard, escalateReason, hasNext, onEscalate]);

  // Keyboard shortcuts
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (showEscalateInput) {
      if (e.key === 'Escape') setShowEscalateInput(false);
      return;
    }

    switch (e.key.toLowerCase()) {
      case 'a':
        e.preventDefault();
        handleApprove();
        break;
      case 'r':
        e.preventDefault();
        handleReject();
        break;
      case 'e':
        e.preventDefault();
        setShowEscalateInput(true);
        break;
      case 'j':
      case 'arrowright':
        e.preventDefault();
        if (hasNext) setCurrentIndex(i => i + 1);
        break;
      case 'k':
      case 'arrowleft':
        e.preventDefault();
        if (hasPrev) setCurrentIndex(i => i - 1);
        break;
    }
  }, [handleApprove, handleReject, hasNext, hasPrev, showEscalateInput]);

  if (!currentCard) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-800">All caught up!</h3>
          <p className="text-gray-600">No more Tier 2 cards to review.</p>
        </div>
      </div>
    );
  }

  const { contact, classification, signals, icpScore, type } = currentCard;

  return (
    <div 
      className="bg-white rounded-xl border border-yellow-200 shadow-lg overflow-hidden"
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {/* Header */}
      <div className="bg-yellow-50 px-6 py-4 border-b border-yellow-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded">
              TIER 2
            </span>
            <span className="text-sm text-gray-600">
              Card {currentIndex + 1} of {cards.length}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">ICP Score:</span>
            <span className={`font-bold ${icpScore >= 4 ? 'text-green-600' : icpScore >= 3 ? 'text-yellow-600' : 'text-red-600'}`}>
              {icpScore}/5
            </span>
          </div>
        </div>
      </div>

      {/* Quick Review Content - Optimized for 30-second review */}
      <div className="p-6">
        {/* Company & Contact - Primary Info */}
        <div className="mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {type}
              </span>
              <h2 className="text-2xl font-bold text-gray-900">
                {currentCard.companyName}
              </h2>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-700">{contact.name}</div>
              <div className="text-sm text-gray-500">{contact.role}</div>
            </div>
          </div>

          {/* Contact Verification Badges */}
          <div className="flex gap-3">
            {contact.emailVerified && (
              <span className="inline-flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                <CheckCircle className="w-3 h-3" />
                Email verified
              </span>
            )}
            {contact.linkedinVerified && contact.linkedinUrl && (
              <span className="inline-flex items-center gap-1 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                <CheckCircle className="w-3 h-3" />
                LinkedIn
              </span>
            )}
          </div>
        </div>

        {/* Signals - Max 2 lines */}
        {signals && signals.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Signals
            </h3>
            <div className="space-y-2">
              {signals.slice(0, 2).map((signal, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 flex-shrink-0" />
                  <span className="text-gray-700">{signal.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Why Tier 2 */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5" />
            <div>
              <span className="text-sm font-medium text-gray-700">Why Tier 2: </span>
              <span className="text-sm text-gray-600">{classification.reason}</span>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Confidence: {classification.confidence}% | Rules: {classification.rulesTriggered.join(', ')}
          </div>
        </div>

        {/* Notes Input */}
        <div className="mb-6">
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Notes (optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add notes..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
            rows={2}
          />
        </div>

        {/* Escalate Input */}
        {showEscalateInput && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <label className="block text-xs font-semibold text-red-700 uppercase tracking-wide mb-2">
              Escalation Reason (required)
            </label>
            <textarea
              value={escalateReason}
              onChange={(e) => setEscalateReason(e.target.value)}
              placeholder="Why does this need deep review?"
              className="w-full px-3 py-2 border border-red-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
              rows={2}
              autoFocus
            />
            <div className="flex gap-2 mt-3">
              <button
                onClick={handleEscalate}
                disabled={!escalateReason}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Confirm Escalate
              </button>
              <button
                onClick={() => setShowEscalateInput(false)}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {!showEscalateInput && (
          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              className="flex-1 py-3 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 flex items-center justify-center gap-2 transition-colors"
            >
              <CheckCircle className="w-4 h-4" />
              Approve (A)
            </button>
            <button
              onClick={handleReject}
              className="flex-1 py-3 px-4 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 flex items-center justify-center gap-2 transition-colors"
            >
              <XCircle className="w-4 h-4" />
              Reject (R)
            </button>
            <button
              onClick={() => setShowEscalateInput(true)}
              className="flex-1 py-3 px-4 bg-yellow-600 text-white font-medium rounded-lg hover:bg-yellow-700 flex items-center justify-center gap-2 transition-colors"
            >
              <ArrowUp className="w-4 h-4" />
              Escalate (E)
            </button>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={() => setCurrentIndex(i => i - 1)}
            disabled={!hasPrev}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous (K)
          </button>
          <span className="text-xs text-gray-400">
            Target: 30 sec per card
          </span>
          <button
            onClick={() => setCurrentIndex(i => i + 1)}
            disabled={!hasNext}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next (J)
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
