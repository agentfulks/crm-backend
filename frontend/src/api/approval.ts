import axios from 'axios';
import type {
  ApprovalCard,
  DashboardMetrics,
  DashboardResponse,
  ApprovalFilters,
  BatchApproveRequest,
  BatchApproveResponse,
  ApproveRequest,
  RejectRequest,
  EscalateRequest,
  FlagForReviewRequest,
} from '../types/approval';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Tiered Approval System API
 * 
 * Endpoints:
 * - GET /api/approval-dashboard - Get cards with tier filtering
 * - POST /api/cards/:id/approve - Approve a card
 * - POST /api/cards/:id/reject - Reject a card
 * - POST /api/cards/batch-approve - Bulk approve cards (Tier 2 only)
 * - GET /api/approval-metrics - Get dashboard metrics
 */

export const approvalApi = {
  /**
   * Get approval dashboard data with optional filters
   */
  async getDashboard(filters?: ApprovalFilters): Promise<DashboardResponse> {
    const params = new URLSearchParams();
    
    if (filters?.tier !== undefined) params.append('tier', String(filters.tier));
    if (filters?.type) params.append('type', filters.type);
    if (filters?.dateFrom) params.append('date_from', filters.dateFrom);
    if (filters?.dateTo) params.append('date_to', filters.dateTo);
    if (filters?.confidenceMin !== undefined) params.append('confidence_min', String(filters.confidenceMin));
    if (filters?.confidenceMax !== undefined) params.append('confidence_max', String(filters.confidenceMax));
    if (filters?.status) params.append('status', filters.status);

    const response = await api.get(`/approval-dashboard?${params.toString()}`);
    return response.data;
  },

  /**
   * Get cards by specific tier
   */
  async getCardsByTier(tier: 1 | 2 | 3, type?: 'BDR' | 'VC'): Promise<ApprovalCard[]> {
    const response = await api.get('/approval-dashboard', {
      params: { tier, type },
    });
    return response.data.cards || [];
  },

  /**
   * Get a single card by ID
   */
  async getCard(id: string): Promise<ApprovalCard> {
    // For now, fetch from dashboard and filter
    // In production, this should be a dedicated endpoint
    const response = await api.get(`/cards/${id}`);
    return response.data;
  },

  /**
   * Approve a card
   */
  async approveCard(id: string, data?: ApproveRequest): Promise<ApprovalCard> {
    const response = await api.post(`/cards/${id}/approve`, data);
    return response.data;
  },

  /**
   * Reject a card
   */
  async rejectCard(id: string, data?: RejectRequest): Promise<ApprovalCard> {
    const response = await api.post(`/cards/${id}/reject`, data);
    return response.data;
  },

  /**
   * Escalate a Tier 2 card to Tier 3
   */
  async escalateCard(id: string, data: EscalateRequest): Promise<ApprovalCard> {
    const response = await api.post(`/cards/${id}/escalate`, data);
    return response.data;
  },

  /**
   * Batch approve multiple cards (Tier 2 only)
   */
  async batchApprove(data: BatchApproveRequest): Promise<BatchApproveResponse> {
    const response = await api.post('/cards/batch-approve', data);
    return response.data;
  },

  /**
   * Get approval metrics for the dashboard
   */
  async getMetrics(): Promise<DashboardMetrics> {
    const response = await api.get('/approval-metrics');
    return response.data;
  },

  /**
   * Flag an auto-approved card (Tier 1) for review
   */
  async flagForReview(id: string, data: FlagForReviewRequest): Promise<ApprovalCard> {
    const response = await api.post(`/cards/${id}/flag`, data);
    return response.data;
  },

  /**
   * Export cards data (for audit/CSV download)
   */
  async exportCards(cardIds?: string[]): Promise<Blob> {
    const response = await api.post('/cards/export', { card_ids: cardIds }, {
      responseType: 'blob',
    });
    return response.data;
  },
};

/**
 * Mock API for development and testing
 * Returns realistic data when backend is not available
 */
export const mockApprovalApi = {
  async getDashboard(filters?: ApprovalFilters): Promise<DashboardResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const mockCards: ApprovalCard[] = generateMockCards();
    
    // Apply filters
    let filteredCards = mockCards;
    if (filters?.tier !== undefined) {
      filteredCards = filteredCards.filter(c => c.classification.tier === filters.tier);
    }
    if (filters?.type) {
      filteredCards = filteredCards.filter(c => c.type === filters.type);
    }
    if (filters?.status) {
      filteredCards = filteredCards.filter(c => c.status === filters.status);
    }

    return {
      cards: filteredCards,
      total: filteredCards.length,
      filters: filters || {},
    };
  },

  async getCardsByTier(tier: 1 | 2 | 3): Promise<ApprovalCard[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return generateMockCards().filter(c => c.classification.tier === tier);
  },

  async getCard(id: string): Promise<ApprovalCard> {
    await new Promise(resolve => setTimeout(resolve, 150));
    const card = generateMockCards().find(c => c.id === id);
    if (!card) throw new Error('Card not found');
    return card;
  },

  async approveCard(id: string, data?: ApproveRequest): Promise<ApprovalCard> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      ...generateMockCards()[0],
      id,
      status: 'APPROVED',
      approvedAt: new Date().toISOString(),
      notes: data?.notes,
    };
  },

  async rejectCard(id: string, data?: RejectRequest): Promise<ApprovalCard> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      ...generateMockCards()[0],
      id,
      status: 'REJECTED',
      rejectedAt: new Date().toISOString(),
      notes: data?.notes,
    };
  },

  async escalateCard(id: string, data: EscalateRequest): Promise<ApprovalCard> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      ...generateMockCards()[0],
      id,
      status: 'PENDING',
      classification: {
        ...generateMockCards()[0].classification,
        tier: 3,
        reason: `Escalated: ${data.reason}`,
      },
    };
  },

  async batchApprove(data: BatchApproveRequest): Promise<BatchApproveResponse> {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      success: data.cardIds,
      failed: [],
    };
  },

  async getMetrics(): Promise<DashboardMetrics> {
    await new Promise(resolve => setTimeout(resolve, 150));
    return {
      autoApprovalRate: 58,
      avgReviewTimeSeconds: 28,
      backlogSize: 132,
      tierDistribution: {
        tier1: 79,
        tier2: 33,
        tier3: 20,
      },
      recentActivity: [
        {
          id: 'act-1',
          cardId: 'card-1',
          companyName: 'Acme Technologies',
          action: 'auto_approved',
          tier: 1,
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        },
        {
          id: 'act-2',
          cardId: 'card-2',
          companyName: 'TechVentures Capital',
          action: 'approved',
          tier: 2,
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          actor: 'Lucas',
        },
        {
          id: 'act-3',
          cardId: 'card-3',
          companyName: 'StartupXYZ',
          action: 'escalated',
          tier: 2,
          timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
          actor: 'Lucas',
        },
      ],
    };
  },

  async flagForReview(id: string, data: FlagForReviewRequest): Promise<ApprovalCard> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      ...generateMockCards()[0],
      id,
      status: 'PENDING',
      classification: {
        ...generateMockCards()[0].classification,
        tier: 3,
        reason: `Flagged: ${data.reason}`,
      },
    };
  },

  async exportCards(cardIds?: string[]): Promise<Blob> {
    await new Promise(resolve => setTimeout(resolve, 500));
    const csv = 'id,company,type,status,tier\nmock-data';
    return new Blob([csv], { type: 'text/csv' });
  },
};

// Helper to generate realistic mock data
function generateMockCards(): ApprovalCard[] {
  const companies = [
    { name: 'Acme Technologies', type: 'BDR' as const, icp: 4, tier: 1 as const },
    { name: 'TechVentures Capital', type: 'VC' as const, icp: 4, tier: 2 as const },
    { name: 'StartupXYZ', type: 'BDR' as const, icp: 3, tier: 2 as const },
    { name: 'Global Gaming Partners', type: 'BDR' as const, icp: 5, tier: 1 as const },
    { name: 'SeedFund Ventures', type: 'VC' as const, icp: 3, tier: 3 as const },
    { name: 'MegaCorp Industries', type: 'BDR' as const, icp: 2, tier: 3 as const },
    { name: 'EarlyStage Capital', type: 'VC' as const, icp: 5, tier: 1 as const },
    { name: 'GameStudio Pro', type: 'BDR' as const, icp: 3, tier: 2 as const },
  ];

  return companies.map((co, idx) => ({
    id: `card-${idx + 1}`,
    type: co.type,
    companyName: co.name,
    companyId: `comp-${idx + 1}`,
    contact: {
      name: `Contact ${idx + 1}`,
      email: `contact${idx + 1}@${co.name.toLowerCase().replace(/\s+/g, '')}.com`,
      emailVerified: Math.random() > 0.2,
      linkedinUrl: `https://linkedin.com/in/contact${idx + 1}`,
      linkedinVerified: Math.random() > 0.3,
      role: co.type === 'BDR' ? 'Partnerships Manager' : 'Investment Director',
    },
    icpScore: co.icp,
    signals: [
      {
        type: 'funding',
        description: '$5M Series A raised 2 months ago',
        date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        type: 'job_posting',
        description: 'Hiring for Senior Partnerships Manager',
        date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ],
    classification: {
      tier: co.tier,
      confidence: co.tier === 1 ? 95 : co.tier === 2 ? 87 : 72,
      rulesTriggered: co.tier === 1 
        ? ['RULE-01', 'RULE-02', 'RULE-03', 'RULE-04', 'RULE-05', 'RULE-06']
        : co.tier === 2
        ? ['RULE-01', 'RULE-02', 'RULE-04', 'RULE-05']
        : ['RULE-01', 'RULE-04'],
      reason: co.tier === 1 
        ? 'Meets all auto-approval criteria'
        : co.tier === 2
        ? 'Only 4/6 rules met, needs quick review'
        : 'Complex scenario requiring deep review',
      classifiedAt: new Date().toISOString(),
    },
    status: 'PENDING',
    createdAt: new Date(Date.now() - idx * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
    partnerType: co.type === 'BDR' ? 'Integrator' : undefined,
    fundSize: co.type === 'VC' ? 100000000 : undefined,
    investmentStage: co.type === 'VC' ? 'Seed-Series B' : undefined,
    sector: co.type === 'VC' ? ['Gaming', 'AI'] : undefined,
  }));
}

// Use mock API for development, real API for production
const isDev = import.meta.env.DEV;
export const activeApprovalApi = isDev ? mockApprovalApi : approvalApi;

export default activeApprovalApi;
