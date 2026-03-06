'use client';

import { CardList } from '@/components/CardList';
import { LoadingState, ErrorState } from '@/components/StatusStates';
import { ApprovalCard } from '@/types/trello';
import { useState, useEffect, useCallback } from 'react';

export function DashboardClient() {
  const [cards, setCards] = useState<ApprovalCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCards = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/trello/cards');
      if (!response.ok) {
        throw new Error(`Failed to fetch cards: ${response.statusText}`);
      }
      const data = await response.json();
      setCards(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCards();
  }, [fetchCards]);

  const handleApprove = async (cardId: string) => {
    try {
      const response = await fetch(`/api/trello/cards/${cardId}/approve`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve card');
      }
      
      // Remove from list
      setCards(cards.filter(c => c.id !== cardId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve');
    }
  };

  const handleReject = async (cardId: string) => {
    const reason = prompt('Reason for rejection (optional):');
    
    try {
      const response = await fetch(`/api/trello/cards/${cardId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject card');
      }
      
      // Remove from list
      setCards(cards.filter(c => c.id !== cardId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to reject');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Approvals</h1>
          <p className="text-sm text-gray-500">
            {cards.length} card{cards.length !== 1 ? 's' : ''} awaiting approval
          </p>
        </div>
        <button
          onClick={fetchCards}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
        >
          Refresh
        </button>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchCards} />
      ) : (
        <CardList
          cards={cards}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
}