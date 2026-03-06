import { useState } from 'react';
import { useApproval } from '../../hooks/useApproval';
import type { ApprovalCard } from '../../types/approval';
import { ArrowLeft, Flag, CheckCircle, AlertTriangle, Loader2, Download } from 'lucide-react';

interface Tier1AutoLogProps {
  onClose: () => void;
  onAction: (action: string, card?: ApprovalCard) => void;
  onFlag: (card: ApprovalCard) => void;
}

export function Tier1AutoLog({ onClose, onAction, onFlag }: Tier1AutoLogProps) {
  const { data: cards, isLoading } = useApproval({ tier: 1 });
  const [selectedCard, setSelectedCard] = useState<ApprovalCard | null>(null);
  const [flagReason, setFlagReason] = useState('');
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const handleFlag = async () => {
    if (!selectedCard || !flagReason) return;
    onFlag(selectedCard);
    setShowFlagModal(false);
    setFlagReason('');
    setSelectedCard(null);
  };

  const handleExport = async () => {
    setIsExporting(true);
    // Simulate export
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsExporting(false);
    onAction('export');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-green-50 border-b border-green-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>
            <span className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
              TIER 1 — AUTO-APPROVED
            </span>
          </div>
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-50"
          >
            {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Export Log
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="bg-white rounded-xl border border-green-200 shadow-lg overflow-hidden">
          {/* Table Header */}
          <div className="bg-green-50 px-6 py-4 border-b border-green-200">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h2 className="font-semibold text-green-900">
                Auto-Approved Cards ({cards?.length || 0})
              </h2>
            </div>
            <p className="text-sm text-green-700 mt-1">
              These cards were automatically approved with 95%+ confidence. Review and flag any that need reconsideration.
            </p>
          </div>

          {/* Cards Table */}
          <div className="divide-y divide-gray-200">
            {cards?.map((card) => (
              <div key={card.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        {card.type}
                      </span>
                      <h3 className="font-semibold text-gray-900">{card.companyName}</h3>
                      <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">
                        {card.classification.confidence}% confidence
                      </span>
                    </div>
                    <div className="mt-1 text-sm text-gray-600">
                      {card.contact.name} • {card.contact.role}
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      Auto-approved: {card.autoApprovedAt ? new Date(card.autoApprovedAt).toLocaleDateString() : 'N/A'}
                      {' • '}
                      Rules: {card.classification.rulesTriggered.join(', ')}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedCard(card);
                      setShowFlagModal(true);
                    }}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                  >
                    <Flag className="w-4 h-4" />
                    Flag for Review
                  </button>
                </div>
              </div>
            ))}
          </div>

          {(!cards || cards.length === 0) && (
            <div className="px-6 py-12 text-center">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No auto-approved cards</h3>
              <p className="text-gray-500 mt-1">Cards will appear here once auto-approved by the system.</p>
            </div>
          )}
        </div>
      </div>

      {/* Flag Modal */}
      {showFlagModal && selectedCard && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="w-6 h-6 text-yellow-600" />
                <h3 className="text-lg font-semibold">Flag for Review</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Flag <strong>{selectedCard.companyName}</strong> for manual review. This will move it to Tier 3.
              </p>
              <textarea
                value={flagReason}
                onChange={(e) => setFlagReason(e.target.value)}
                placeholder="Why should this be reviewed?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                rows={3}
                autoFocus
              />
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleFlag}
                  disabled={!flagReason}
                  className="flex-1 py-2 px-4 bg-yellow-600 text-white font-medium rounded-lg hover:bg-yellow-700 disabled:opacity-50"
                >
                  Flag Card
                </button>
                <button
                  onClick={() => {
                    setShowFlagModal(false);
                    setFlagReason('');
                    setSelectedCard(null);
                  }}
                  className="flex-1 py-2 px-4 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
