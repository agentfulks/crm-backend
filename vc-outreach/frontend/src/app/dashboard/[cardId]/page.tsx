'use client';

import { CardDetail } from '@/components/CardDetail';
import { LoadingState, ErrorState } from '@/components/StatusStates';
import { ApprovalCard } from '@/types/trello';
import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';

export default function CardDetailPage() {
  const params = useParams();
  const router = useRouter();
  const cardId = params.cardId as string;
  
  const [card, setCard] = useState<ApprovalCard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/trello/cards/${cardId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch card: ${response.statusText}`);
      }
      const data = await response.json();
      setCard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [cardId]);

  useEffect(() => {
    fetchCard();
  }, [fetchCard]);

  const handleApprove = async () => {
    try {
      const response = await fetch(`/api/trello/cards/${cardId}/approve`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve card');
      }
      
      router.push('/dashboard');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve');
    }
  };

  const handleReject = async (reason?: string) => {
    try {
      const response = await fetch(`/api/trello/cards/${cardId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject card');
      }
      
      router.push('/dashboard');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to reject');
    }
  };

  const handleSave = async (updates: { draftMessage?: string; notes?: string }) => {
    setIsSaving(true);
    
    try {
      const response = await fetch(`/api/trello/cards/${cardId}/update`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update card');
      }
      
      // Refresh card data
      await fetchCard();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <LoadingState />
        </div>
      </main>
    );
  }

  if (error || !card) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <ErrorState message={error || 'Card not found'} onRetry={fetchCard} />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <CardDetail
          card={card}
          onApprove={handleApprove}
          onReject={handleReject}
          onSave={handleSave}
          isLoading={isSaving}
        />
      </div>
    </main>
  );
}