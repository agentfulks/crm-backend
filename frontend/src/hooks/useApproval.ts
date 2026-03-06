import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { activeApprovalApi } from '../api/approval';
import type { ApprovalFilters, ApproveRequest, RejectRequest, EscalateRequest, FlagForReviewRequest, BatchApproveRequest } from '../types/approval';

/**
 * React Query hooks for the Tiered Approval System
 */

// Query keys for consistent cache management
const approvalKeys = {
  all: ['approval'] as const,
  dashboard: (filters?: ApprovalFilters) => [...approvalKeys.all, 'dashboard', filters] as const,
  tier: (tier: 1 | 2 | 3) => [...approvalKeys.all, 'tier', tier] as const,
  card: (id: string) => [...approvalKeys.all, 'card', id] as const,
  metrics: () => [...approvalKeys.all, 'metrics'] as const,
};

/**
 * Hook to fetch approval dashboard data with optional filters
 */
export function useApprovalDashboard(filters?: ApprovalFilters) {
  return useQuery({
    queryKey: approvalKeys.dashboard(filters),
    queryFn: () => activeApprovalApi.getDashboard(filters),
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook to fetch cards by tier
 */
export function useCardsByTier(tier: 1 | 2 | 3, type?: 'BDR' | 'VC') {
  return useQuery({
    queryKey: approvalKeys.tier(tier),
    queryFn: () => activeApprovalApi.getCardsByTier(tier, type),
    staleTime: 30000,
  });
}

/**
 * Hook to fetch a single card by ID
 */
export function useCard(cardId: string) {
  return useQuery({
    queryKey: approvalKeys.card(cardId),
    queryFn: () => activeApprovalApi.getCard(cardId),
    enabled: !!cardId,
  });
}

/**
 * Hook to fetch approval metrics
 */
export function useApprovalMetrics() {
  return useQuery({
    queryKey: approvalKeys.metrics(),
    queryFn: () => activeApprovalApi.getMetrics(),
    refetchInterval: 60000, // Refetch every minute
  });
}

/**
 * Hook to approve a card
 */
export function useApproveCard() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: ApproveRequest }) =>
      activeApprovalApi.approveCard(id, data),
    onSuccess: () => {
      // Invalidate all approval-related queries
      queryClient.invalidateQueries({ queryKey: approvalKeys.all });
    },
  });
}

/**
 * Hook to reject a card
 */
export function useRejectCard() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: RejectRequest }) =>
      activeApprovalApi.rejectCard(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: approvalKeys.all });
    },
  });
}

/**
 * Hook to escalate a Tier 2 card to Tier 3
 */
export function useEscalateCard() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: EscalateRequest }) =>
      activeApprovalApi.escalateCard(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: approvalKeys.all });
    },
  });
}

/**
 * Hook to batch approve cards (Tier 2 only)
 */
export function useBatchApprove() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: BatchApproveRequest) => activeApprovalApi.batchApprove(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: approvalKeys.all });
    },
  });
}

/**
 * Hook to flag an auto-approved card for review
 */
export function useFlagForReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FlagForReviewRequest }) =>
      activeApprovalApi.flagForReview(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: approvalKeys.all });
    },
  });
}

/**
 * Hook to export cards
 */
export function useExportCards() {
  return useMutation({
    mutationFn: (cardIds?: string[]) => activeApprovalApi.exportCards(cardIds),
  });
}

/**
 * Hook to handle sequential review navigation
 * Returns functions for navigating through cards with keyboard shortcuts
 */
export function useReviewNavigation(cardIds: string[], currentIndex: number, onNavigate: (index: number) => void) {
  const goNext = () => {
    if (currentIndex < cardIds.length - 1) {
      onNavigate(currentIndex + 1);
    }
  };

  const goPrev = () => {
    if (currentIndex > 0) {
      onNavigate(currentIndex - 1);
    }
  };

  const hasNext = currentIndex < cardIds.length - 1;
  const hasPrev = currentIndex > 0;

  return { goNext, goPrev, hasNext, hasPrev, currentIndex, total: cardIds.length };
}
