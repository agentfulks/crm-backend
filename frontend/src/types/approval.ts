/**
 * Types for the Tiered Approval System
 * Following the design in TIERED_APPROVAL_SYSTEM_DESIGN.md
 */

export type ApprovalTier = 1 | 2 | 3;
export type CardType = 'BDR' | 'VC';
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'ESCALATED';

export interface CardSignal {
  type: 'funding' | 'job_posting' | 'leadership_change' | 'tech_change' | 'other';
  description: string;
  date: string;
  source?: string;
}

export interface CardContact {
  name: string;
  email: string;
  emailVerified: boolean;
  linkedinUrl?: string;
  linkedinVerified: boolean;
  role?: string;
}

export interface TierClassification {
  tier: ApprovalTier;
  confidence: number; // 0-100
  rulesTriggered: string[];
  reason: string;
  classifiedAt: string;
}

export interface ApprovalCard {
  id: string;
  type: CardType;
  companyName: string;
  companyId: string;
  contact: CardContact;
  icpScore: number; // 1-5
  signals: CardSignal[];
  classification: TierClassification;
  status: ApprovalStatus;
  createdAt: string;
  updatedAt: string;
  approvedAt?: string;
  rejectedAt?: string;
  reviewedBy?: string;
  notes?: string;
  // For BDR cards
  partnerType?: 'Integrator' | 'Referral' | 'Strategic';
  // For VC cards
  fundSize?: number;
  investmentStage?: string;
  sector?: string[];
}

export interface DashboardMetrics {
  autoApprovalRate: number; // percentage
  avgReviewTimeSeconds: number;
  backlogSize: number;
  tierDistribution: {
    tier1: number;
    tier2: number;
    tier3: number;
  };
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  cardId: string;
  companyName: string;
  action: 'auto_approved' | 'approved' | 'rejected' | 'escalated' | 'flagged';
  tier: ApprovalTier;
  timestamp: string;
  actor?: string;
}

export interface ApprovalFilters {
  tier?: ApprovalTier;
  type?: CardType;
  dateFrom?: string;
  dateTo?: string;
  confidenceMin?: number;
  confidenceMax?: number;
  status?: ApprovalStatus;
}

export interface DashboardResponse {
  cards: ApprovalCard[];
  total: number;
  filters: ApprovalFilters;
}

export interface BatchApproveRequest {
  cardIds: string[];
  notes?: string;
}

export interface BatchApproveResponse {
  success: string[];
  failed: { cardId: string; error: string }[];
}

export interface ApproveRequest {
  notes?: string;
}

export interface RejectRequest {
  reason?: string;
  notes?: string;
}

export interface EscalateRequest {
  reason: string;
}

export interface FlagForReviewRequest {
  reason: string;
}

// For the 30-second review checklist
export interface QuickReviewData {
  card: ApprovalCard;
  redFlags: string[];
  strategicFit: boolean;
  recommendation: 'approve' | 'reject' | 'escalate';
}

// Keyboard shortcuts configuration
export interface KeyboardShortcut {
  key: string;
  action: string;
  description: string;
  context: 'global' | 'review' | 'list';
}

export const KEYBOARD_SHORTCUTS: KeyboardShortcut[] = [
  { key: 'a', action: 'approve', description: 'Approve current card', context: 'review' },
  { key: 'r', action: 'reject', description: 'Reject current card', context: 'review' },
  { key: 'e', action: 'escalate', description: 'Escalate to Tier 3', context: 'review' },
  { key: 'j', action: 'next', description: 'Next card', context: 'list' },
  { key: 'k', action: 'prev', description: 'Previous card', context: 'list' },
  { key: '?', action: 'help', description: 'Show keyboard shortcuts', context: 'global' },
  { key: 'Escape', action: 'close', description: 'Close modal/view', context: 'global' },
];
