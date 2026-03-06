'use client';

import { ApprovalCard } from '@/types/trello';
import { formatDistanceToNow } from 'date-fns';
import { ArrowLeft, CheckCircle2, XCircle, Save, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect, useCallback } from 'react';

interface CardDetailProps {
  card: ApprovalCard;
  onApprove: () => void;
  onReject: (reason?: string) => void;
  onSave: (updates: { draftMessage?: string; notes?: string }) => void;
  isLoading?: boolean;
}

export function CardDetail({ card, onApprove, onReject, onSave, isLoading }: CardDetailProps) {
  const [draftMessage, setDraftMessage] = useState(card.draftMessage);
  const [notes, setNotes] = useState(card.notes);
  const [hasChanges, setHasChanges] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  // Reset form when card changes
  useEffect(() => {
    setDraftMessage(card.draftMessage);
    setNotes(card.notes);
    setHasChanges(false);
  }, [card.id]);

  // Track changes
  useEffect(() => {
    setHasChanges(
      draftMessage !== card.draftMessage || notes !== card.notes
    );
  }, [draftMessage, notes, card.draftMessage, card.notes]);

  // Keyboard shortcuts
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.target instanceof HTMLTextAreaElement) return;
    
    if (e.key === 'a' || e.key === 'A') {
      e.preventDefault();
      onApprove();
    } else if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      setShowRejectModal(true);
    } else if ((e.key === 's' || e.key === 'S') && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (hasChanges) {
        onSave({ draftMessage, notes });
      }
    }
  }, [onApprove, onReject, hasChanges, draftMessage, notes, onSave]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-3"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to list
          </Link>
          
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-gray-900">{card.fund}</h1>
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 text-sm font-medium rounded-full border ${getPriorityColor(
                card.priority
              )}`}
            >
              {card.priority === 'high' && <AlertCircle className="w-3.5 h-3.5" />}
              {card.priority} priority
            </span>
          </div>
          
          <p className="text-gray-600">
            Partner: <span className="font-medium">{card.partner}</span>
          </p>
          
          <p className="text-xs text-gray-400 mt-1">
            Last updated {formatDistanceToNow(card.lastActivity, { addSuffix: true })}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {hasChanges && (
            <button
              onClick={() => onSave({ draftMessage, notes })}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              Save (Ctrl+S)
            </button>
          )}
          <button
            onClick={() => setShowRejectModal(true)}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 text-sm font-medium rounded-md hover:bg-red-100 disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            Reject (R)
          </button>
          <button
            onClick={onApprove}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            Approve (A)
          </button>
        </div>
      </div>

      {/* Hook */}
      {card.hook && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-purple-900 mb-2">Hook</h3>
          <p className="text-purple-800">{card.hook}</p>
        </div>
      )}

      {/* Draft Message */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-900">Draft Message</h3>
          <span className="text-xs text-gray-400">Editable</span>
        </div>
        <textarea
          value={draftMessage}
          onChange={(e) => setDraftMessage(e.target.value)}
          className="w-full h-64 p-4 text-sm font-mono text-gray-700 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="Enter draft outreach message..."
        />
      </div>

      {/* Notes */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-900">Notes</h3>
          <span className="text-xs text-gray-400">Internal only</span>
        </div>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full h-32 p-4 text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="Add internal notes..."
        />
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Reject Card</h3>
            <p className="text-sm text-gray-600 mb-4">
              Add a reason for rejection (optional):
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full h-24 p-3 text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg mb-4 resize-none"
              placeholder="Reason for rejection..."
              autoFocus
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onReject(rejectReason || undefined);
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Help */}
      <div className="pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-400">
          Keyboard shortcuts: <kbd className="px-1 py-0.5 bg-gray-100 rounded">A</kbd> Approve, 
          <kbd className="px-1 py-0.5 bg-gray-100 rounded ml-1">R</kbd> Reject, 
          <kbd className="px-1 py-0.5 bg-gray-100 rounded ml-1">Ctrl+S</kbd> Save
        </p>
      </div>
    </div>
  );
}