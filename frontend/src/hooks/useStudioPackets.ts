import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studioPacketsApi, api } from '../api';

// Hook to fetch studio packets with optional status filter
export function useStudioPackets(status?: string) {
  return useQuery({
    queryKey: ['studio-packets', status],
    queryFn: () => studioPacketsApi.listStudioPackets(status),
  });
}

// Hook to fetch studio packets awaiting approval
export function usePendingStudioPackets() {
  return useQuery({
    queryKey: ['studio-packets', 'pending'],
    queryFn: () => studioPacketsApi.getPendingStudioPackets(),
  });
}

// Hook to approve a studio packet
export function useApproveStudioPacket() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => studioPacketsApi.approveStudioPacket(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studio-packets'] });
    },
  });
}

// Hook to reject a studio packet
export function useRejectStudioPacket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => studioPacketsApi.rejectStudioPacket(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studio-packets'] });
    },
  });
}

// Hook to update studio packet status
export function useUpdateStudioPacketStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      studioPacketsApi.updateStudioPacketStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studio-packets'] });
    },
  });
}

// Hook to update a company (flag, status, etc.)
export function useUpdateCompany() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.patch(`/bdr/companies/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studio-packets'] });
    },
  });
}

// Hook to get studio queue status
export function useStudioQueueStatus() {
  return useQuery({
    queryKey: ['studio-queue-status'],
    queryFn: () => studioPacketsApi.getStudioQueueStatus(),
    refetchInterval: 30000,
  });
}
