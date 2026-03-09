import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fundsApi } from '../api';
import type { Fund } from '../types';

export function useFunds(status?: string) {
  return useQuery({
    queryKey: ['funds', status ?? 'all'],
    queryFn: () => fundsApi.listFunds(status),
  });
}

export function useUpdateFund() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Fund> }) =>
      fundsApi.updateFund(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['funds'] });
    },
  });
}
