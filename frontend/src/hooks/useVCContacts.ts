import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { vcContactsApi } from '../api';
import { api } from '../api';
import type { VCContact, VCOutreachLog } from '../types';

const CONTACTS_KEY = 'vc-contacts';

/** List all VC contacts, optionally filtered. */
export function useVCContacts(params: {
  fund_id?: string;
  search?: string;
  is_primary?: boolean;
  is_flagged?: boolean;
} = {}) {
  return useQuery({
    queryKey: [CONTACTS_KEY, params],
    queryFn: () => vcContactsApi.list(params),
  });
}

/** Contacts for a single fund. */
export function useContactsByFund(fund_id: string) {
  return useQuery({
    queryKey: [CONTACTS_KEY, 'fund', fund_id],
    queryFn: () => vcContactsApi.getByFund(fund_id),
    enabled: !!fund_id,
  });
}

/** Single contact by id. */
export function useVCContact(id: string | undefined) {
  return useQuery({
    queryKey: [CONTACTS_KEY, id],
    queryFn: () => vcContactsApi.get(id!),
    enabled: !!id,
  });
}

export function useCreateVCContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<VCContact> & { fund_id: string; full_name: string }) =>
      vcContactsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CONTACTS_KEY] }),
  });
}

export function useUpdateVCContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<VCContact> }) =>
      vcContactsApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CONTACTS_KEY] }),
  });
}

export function useDeleteVCContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => vcContactsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CONTACTS_KEY] }),
  });
}

// ── Outreach log hooks ────────────────────────────────────────────────────────

export function useVCOutreachLogs(contactId: string) {
  return useQuery({
    queryKey: ['vc-outreach-logs', contactId],
    queryFn: async () => {
      const res = await api.get(`/contacts/${contactId}/outreach`);
      return res.data as { total: number; items: VCOutreachLog[] };
    },
    enabled: !!contactId,
  });
}

export function useCreateVCOutreachLog() {
  const qc = useQueryClient();
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
      const res = await api.post(`/contacts/${contactId}/outreach`, { channel, subject, body });
      return res.data as VCOutreachLog;
    },
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['vc-outreach-logs', vars.contactId] });
      qc.invalidateQueries({ queryKey: [CONTACTS_KEY] });
    },
  });
}

export function useDeleteVCOutreachLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ contactId, logId }: { contactId: string; logId: string }) => {
      await api.delete(`/contacts/${contactId}/outreach/${logId}`);
    },
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['vc-outreach-logs', vars.contactId] });
      qc.invalidateQueries({ queryKey: [CONTACTS_KEY] });
    },
  });
}
