import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import {
  usePackets,
  usePendingPackets,
  useQueueStatus,
  useApprovePacket,
  useRejectPacket,
  useUpdatePacketStatus,
} from './usePackets';
import { packetsApi } from '../api';
import type { Packet, PacketListResponse, QueueStatus } from '../types';

// Mock the API
vi.mock('../api', () => ({
  packetsApi: {
    listPackets: vi.fn(),
    getPendingPackets: vi.fn(),
    getQueueStatus: vi.fn(),
    approvePacket: vi.fn(),
    rejectPacket: vi.fn(),
    updatePacketStatus: vi.fn(),
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

      (packetsApi.listPackets as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePackets('AWAITING_APPROVAL'), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
      expect(packetsApi.listPackets).toHaveBeenCalledWith('AWAITING_APPROVAL');
    });

    it('fetches all packets when no status filter', async () => {
      const mockResponse: PacketListResponse = {
        total: 3,
        items: [],
      };

      (packetsApi.listPackets as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePackets(), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(packetsApi.listPackets).toHaveBeenCalledWith(undefined);
    });
  });

  describe('usePendingPackets', () => {
    it('fetches pending packets', async () => {
      const mockResponse: PacketListResponse = {
        total: 1,
        items: [],
      };

      (packetsApi.getPendingPackets as any).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => usePendingPackets(), {
        wrapper: Wrapper,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
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

      (packetsApi.getQueueStatus as any).mockResolvedValue(mockStatus);

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

      (packetsApi.approvePacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useApprovePacket(), {
        wrapper: Wrapper,
      });

      await result.current.mutateAsync('packet-1');

      expect(packetsApi.approvePacket).toHaveBeenCalledWith('packet-1');
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

      (packetsApi.rejectPacket as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useRejectPacket(), {
        wrapper: Wrapper,
      });

      await result.current.mutateAsync('packet-1');

      expect(packetsApi.rejectPacket).toHaveBeenCalledWith('packet-1');
    });
  });

  describe('useUpdatePacketStatus', () => {
    it('updates packet status and invalidates queries', async () => {
      const mockPacket: Packet = {
        id: 'packet-1',
        fund_id: 'fund-1',
        status: 'SENT',
        priority: 'A',
        created_at: '2025-02-25T00:00:00Z',
        updated_at: '2025-02-25T00:00:00Z',
      };

      (packetsApi.updatePacketStatus as any).mockResolvedValue(mockPacket);

      const { result } = renderHook(() => useUpdatePacketStatus(), {
        wrapper: Wrapper,
      });

      await result.current.mutateAsync({ id: 'packet-1', status: 'SENT' });

      expect(packetsApi.updatePacketStatus).toHaveBeenCalledWith('packet-1', 'SENT');
    });
  });
});
