import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import type { BDRContact, BDROutreachLog } from '../types';

export interface ContactFilters {
  company_id?: string;
  is_decision_maker?: boolean;
  search?: string;
}

// Hook to fetch contacts with optional filters
export function useContacts(filters?: ContactFilters) {
  return useQuery({
    queryKey: ['contacts', filters],
    queryFn: async () => {
      const params: Record<string, any> = {};
      if (filters?.company_id) params.company_id = filters.company_id;
      if (filters?.is_decision_maker !== undefined) params.is_decision_maker = filters.is_decision_maker;
      
      const response = await api.get('/bdr/contacts/', { params });
      
      // Apply search filter client-side if provided
      let items = response.data?.items || [];
      if (filters?.search) {
        const searchLower = filters.search.toLowerCase();
        items = items.filter((c: BDRContact) => 
          c.full_name?.toLowerCase().includes(searchLower) ||
          c.job_title?.toLowerCase().includes(searchLower) ||
          c.email?.toLowerCase().includes(searchLower)
        );
      }
      
      return {
        total: items.length,
        items,
      };
    },
  });
}

// Hook to fetch a single contact
export function useContact(id: string) {
  return useQuery({
    queryKey: ['contact', id],
    queryFn: async () => {
      const response = await api.get(`/bdr/contacts/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

// Hook to create a new contact
export function useCreateContact() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Partial<BDRContact>) => {
      const response = await api.post('/bdr/contacts/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

// Hook to update a contact
export function useUpdateContact() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<BDRContact> }) => {
      const response = await api.patch(`/bdr/contacts/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

// Hook to delete a contact
export function useDeleteContact() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/bdr/contacts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

// Hook to fetch outreach log history for a contact
export function useOutreachLogs(contactId: string) {
  return useQuery({
    queryKey: ['outreach-logs', contactId],
    queryFn: async () => {
      const response = await api.get(`/bdr/contacts/${contactId}/outreach`);
      return response.data as { total: number; items: BDROutreachLog[] };
    },
    enabled: !!contactId,
  });
}

// Hook to delete an outreach log entry
export function useDeleteOutreachLog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ contactId, logId }: { contactId: string; logId: string }) => {
      await api.delete(`/bdr/contacts/${contactId}/outreach/${logId}`);
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['outreach-logs', vars.contactId] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

// Hook to record an outreach attempt
export function useCreateOutreachLog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      contactId,
      channel,
      subject,
      body,
    }: {
      contactId: string;
      channel: 'email' | 'linkedin';
      subject?: string;
      body?: string;
    }) => {
      const response = await api.post(`/bdr/contacts/${contactId}/outreach`, {
        channel,
        subject,
        body,
      });
      return response.data as BDROutreachLog;
    },
    onSuccess: (_data, vars) => {
      // Refresh both the log list and the contacts list (for last_contacted_at)
      queryClient.invalidateQueries({ queryKey: ['outreach-logs', vars.contactId] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}
