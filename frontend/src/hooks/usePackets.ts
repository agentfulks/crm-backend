import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { packetsApi } from '../api';

// Hook to fetch packets with optional status filter
export function usePackets(status?: string) {
  return useQuery({
    queryKey: ['packets', status],
    queryFn: () => packetsApi.listPackets(status),
  });
}

// Hook to fetch packets awaiting approval
export function usePendingPackets() {
  return useQuery({
    queryKey: ['packets', 'pending'],
    queryFn: () => packetsApi.getPendingPackets(),
  });
}

// Hook to get queue status
export function useQueueStatus() {
  return useQuery({
    queryKey: ['queue-status'],
    queryFn: () => packetsApi.getQueueStatus(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

// Hook to approve a packet
export function useApprovePacket() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => packetsApi.approvePacket(id),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['packets'] });
      queryClient.invalidateQueries({ queryKey: ['queue-status'] });
    },
  });
}

// Hook to reject a packet
export function useRejectPacket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => packetsApi.rejectPacket(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packets'] });
      queryClient.invalidateQueries({ queryKey: ['queue-status'] });
    },
  });
}

// Hook to update packet status
export function useUpdatePacketStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      packetsApi.updatePacketStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packets'] });
      queryClient.invalidateQueries({ queryKey: ['queue-status'] });
    },
  });
}
