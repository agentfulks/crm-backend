import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import {
  usePackets,
  usePendingPackets,
  usePacket,
  useQueueStatus,
  useApprovePacket,
  useRejectPacket,
  useUpdatePacket,
} from './usePackets';
import { packetApi } from '../api';
import type { Packet, PacketListResponse, QueueStatus } from '../types';

// Mock the API
vi.mock('../api', () => ({
  packetApi: {
    listPackets: vi.fn(),
    getPendingApproval: vi.fn(),
    getPacket: vi.fn(),
    getQueueStatus: vi.fn(),
    approvePacket: vi.fn(),
    rejectPacket: vi.fn(),
    updatePacket: vi.fn(),
  },
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const Wrapper = ({ children }: { children: ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('usePackets', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('usePackets', () => {
    it('fetches packets with status filter', async () => {
      const mockResponse: PacketListResponse = {
        total: 2,
        items: [
          {
            id: 'packet-1',
            fund_id: 'fund-1',
            status: 'AWAITING_APPROVAL',
            priority: 'A',
            created_at: '2025-02-25T00:00:00Z',
            updated_at: '2025-02-25T00:00:00Z',
          },
        ] as Packet[],
      };

      (packetApi.listPackets as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePackets('AWAITING_APPROVAL'), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
      expect(packetApi.listPackets).toHaveBeenCalledWith('AWAITING_APPROVAL');
    });

    it('fetches all packets when no status filter', async () => {
      const mockResponse: PacketListResponse = {
        total: 3,
        items: [],
      };

      (packetApi.listPackets as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePackets(), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(packetApi.listPackets).toHaveBeenCalledWith(undefined);
    });
  });

  describe('usePendingPackets', () => {
    it('fetches pending packets', async () => {
      const mockResponse: PacketListResponse = {
        total: 1,
        items: [],
      };

      (packetApi.getPendingApproval as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePendingPackets(), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
    });
  });

  describe('usePacket', () => {
    it('fetches single packet by id', async () => {
      const mockPacket: Packet = {
        id: 'packet-1',
        fund_id: 'fund-1',
        status: 'AWAITING_APPROVAL',
        priority: 'A',
        created_at: '2025-02-25T00:00:00Z',
        updated_at: '2025-02-25T00:00:00Z',
      };

      (packetApi.getPacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => usePacket('packet-1'), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockPacket);
      expect(packetApi.getPacket).toHaveBeenCalledWith('packet-1');
    });

    it('does not fetch when id is empty', () => {
      const { result } = renderHook(() => usePacket(''), {
        wrapper: Wrapper,
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.fetchStatus).toBe('idle');
    });
  });

  describe('useQueueStatus', () => {
    it('fetches queue status', async () => {
      const mockStatus: QueueStatus = {
        date: '2025-02-25',
        total_queued: 5,
        awaiting_approval: 3,
        approved_today: 2,
        sent_today: 1,
      };

      (packetApi.getQueueStatus as any).mockResolvedValue(mockStatus);

      const { result } = renderHook(() => useQueueStatus(), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStatus);
    });
  });

  describe('useApprovePacket', () => {
    it('approves packet and invalidates queries', async () => {
      const mockPacket: Packet = {
        id: 'packet-1',
        fund_id: 'fund-1',
        status: 'APPROVED',
        priority: 'A',
        created_at: '2025-02-25T00:00:00Z',
        updated_at: '2025-02-25T00:00:00Z',
      };

      (packetApi.approvePacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useApprovePacket(), {
        wrapper: Wrapper,
      });

      await result.current.mutateAsync('packet-1');

      expect(packetApi.approvePacket).toHaveBeenCalledWith('packet-1');
    });
  });

  describe('useRejectPacket', () => {
    it('rejects packet and invalidates queries', async () => {
      const mockPacket: Packet = {
        id: 'packet-1',
        fund_id: 'fund-1',
        status: 'CLOSED',
        priority: 'A',
        created_at: '2025-02-25T00:00:00Z',
        updated_at: '2025-02-25T00:00:00Z',
      };

      (packetApi.rejectPacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useRejectPacket(), {
        wrapper: Wrapper,
      });

      await result.current.mutateAsync('packet-1');

      expect(packetApi.rejectPacket).toHaveBeenCalledWith('packet-1');
    });
  });

  describe('useUpdatePacket', () => {
    it('updates packet and invalidates queries', async () => {
      const mockPacket: Packet = {
        id: 'packet-1',
        fund_id: 'fund-1',
        status: 'AWAITING_APPROVAL',
        priority: 'B',
        created_at: '2025-02-25T00:00:00Z',
        updated_at: '2025-02-25T00:00:00Z',
      };

      (packetApi.updatePacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useUpdatePacket(), {
        wrapper: Wrapper,
      });

      const updates = { priority: 'B' as const, fund: { name: 'Updated Fund' } as Record<string, unknown> };
      await result.current.mutateAsync({ id: 'packet-1', updates: updates as any });

      expect(packetApi.updatePacket).toHaveBeenCalledWith('packet-1', updates);
    });
  });
});
