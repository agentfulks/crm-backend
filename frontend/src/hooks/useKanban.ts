import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import type { KanbanCard, KanbanColumn } from '../types';

// ── List ────────────────────────────────────────────────────────────────────

export function useKanbanCards(column?: KanbanColumn) {
  return useQuery({
    queryKey: ['kanban', column ?? 'all'],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (column) params.column = column;
      const res = await api.get('/kanban/', { params });
      return res.data as { total: number; items: KanbanCard[] };
    },
  });
}

// ── Create ───────────────────────────────────────────────────────────────────

export interface CreateKanbanCardInput {
  title: string;
  description?: string;
  column: KanbanColumn;
  card_type?: string;
  source_id?: string;
  source_data?: Record<string, any>;
  priority?: string;
  due_date?: string;
  tags?: string[];
}

export function useCreateKanbanCard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateKanbanCardInput) => {
      const res = await api.post('/kanban/', data);
      return res.data as KanbanCard;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
    },
  });
}

// ── Update (move column, edit fields) ────────────────────────────────────────

export interface UpdateKanbanCardInput {
  id: string;
  data: Partial<Omit<KanbanCard, 'id' | 'created_at' | 'updated_at'>>;
}

export function useUpdateKanbanCard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: UpdateKanbanCardInput) => {
      const res = await api.patch(`/kanban/${id}`, data);
      return res.data as KanbanCard;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
    },
  });
}

// ── Delete ───────────────────────────────────────────────────────────────────

export function useDeleteKanbanCard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/kanban/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
    },
  });
}
