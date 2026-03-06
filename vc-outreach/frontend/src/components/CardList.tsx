'use client';

import { ApprovalCard } from '@/types/trello';
import { formatDistanceToNow } from 'date-fns';
import { ArrowRight, Clock, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import Link from 'next/link';

interface CardListProps {
  cards: ApprovalCard[];
  onApprove: (cardId: string) => void;
  onReject: (cardId: string) => void;
}

export function CardList({ cards, onApprove, onReject }: CardListProps) {
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

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-3 h-3" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-2">
      {cards.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-medium">No cards awaiting approval</p>
          <p className="text-sm">All caught up!</p>
        </div>
      ) : (
        cards.map((card) => (
          <div
            key={card.id}
            className="group bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between gap-4">
              <Link
                href={`/dashboard/${card.id}`}
                className="flex-1 min-w-0 cursor-pointer"
              >
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {card.fund}
                  </h3>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full border ${getPriorityColor(
                      card.priority
                    )}`}
                  >
                    {getPriorityIcon(card.priority)}
                    {card.priority}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-2">
                  Partner: <span className="font-medium">{card.partner}</span>
                </p>
                
                {card.hook && (
                  <p className="text-sm text-gray-500 line-clamp-2 mb-2">
                    Hook: {card.hook}
                  </p>
                )}
                
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Clock className="w-3 h-3" />
                  {formatDistanceToNow(card.lastActivity, { addSuffix: true })}
                </div>
              </Link>

              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onApprove(card.id);
                  }}
                  className="p-2 text-green-600 hover:bg-green-50 rounded-md transition-colors"
                  title="Approve (A)"
                >
                  <CheckCircle2 className="w-5 h-5" />
                </button>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onReject(card.id);
                  }}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                  title="Reject (R)"
                >
                  <XCircle className="w-5 h-5" />
                </button>
                <Link
                  href={`/dashboard/${card.id}`}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}