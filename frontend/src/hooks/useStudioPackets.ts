import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studioPacketsApi, api } from '../api';
import type { StudioPacket, PacketStatus, Priority } from '../types';

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

// Hook to fetch a single studio company by ID and reshape it into a StudioPacket
export function useStudioCompany(id: string | undefined) {
  return useQuery({
    queryKey: ['studio-company', id],
    queryFn: async (): Promise<StudioPacket> => {
      const { data: company } = await api.get(`/bdr/companies/${id}`);
      return {
        id: `studio-packet-${company.id}`,
        studio_id: company.id,
        studio: {
          id: company.id,
          name: company.company_name,
          hq_city: company.headquarters_city,
          hq_region: company.headquarters_state,
          hq_country: company.headquarters_country,
          studio_type: company.industry || 'Game Studio',
          employee_count: company.company_size,
          overview: company.use_case_fit || company.company_name,
          priority: (company.priority || 'C') as Priority,
          status: (company.status?.toUpperCase().replace(' ', '_') || 'NEW') as any,
          website_url: company.website_url || '',
          linkedin_url: company.linkedin_url || '',
          icp_score: company.icp_score,
          is_flagged: company.is_flagged || false,
          created_at: company.created_at,
          updated_at: company.updated_at,
        },
        contact_name: '',
        contact_role: '',
        contact_email: '',
        contact_linkedin: '',
        status: (company.status?.toUpperCase().replace(' ', '_') || 'NEW') as PacketStatus,
        priority: (company.priority || 'B') as Priority,
        score_snapshot: company.icp_score || 0,
        created_at: company.created_at,
        updated_at: company.updated_at,
      };
    },
    enabled: !!id,
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
