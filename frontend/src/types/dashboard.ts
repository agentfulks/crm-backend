/**
 * Dashboard-specific types for VC Outreach Pipeline visualization
 */

import type { PacketStatus, Priority } from '../types';

/** Status for pipeline batch visualization */
export type BatchStatus = 'READY' | 'BLOCKED' | 'IN_PROGRESS' | 'COMPLETE';

/** Represents a day in the outreach pipeline */
export interface PipelineDay {
  dayNumber: number;
  date: string;
  status: BatchStatus;
  funds: PipelineFund[];
  totalFunds: number;
  sentCount: number;
  blockedReason?: string;
}

/** Fund information for pipeline display */
export interface PipelineFund {
  id: string;
  fundId: string;
  fundName: string;
  partnerName: string;
  fitScore: number;
  priority: Priority;
  status: PacketStatus;
  contactEmail?: string;
  linkedinUrl?: string;
  emailDraft?: {
    to: string;
    subject: string;
    body: string;
  };
}

/** Batch detail view data */
export interface BatchDetail {
  dayNumber: number;
  date: string;
  status: BatchStatus;
  funds: PipelineFund[];
}

/** Decision queue item requiring user input */
export interface DecisionQueueItem {
  id: string;
  type: 'BATCH_SEND' | 'FOLLOW_UP' | 'PRIORITY_CHANGE';
  title: string;
  description: string;
  dayNumber?: number;
  deadline?: string;
  options: DecisionOption[];
  recommendation?: string;
  blockedSince: string;
}

/** Decision option for queue items */
export interface DecisionOption {
  id: string;
  label: string;
  value: string;
  description?: string;
}

/** Pipeline metrics for dashboard */
export interface PipelineMetrics {
  totalFundsInPipeline: number;
  fundsSentThisWeek: number;
  responseRate: number | null;
  followUpsScheduled: number;
  fundsByStatus: Record<PacketStatus, number>;
  fundsByDay: Record<number, number>;
}

/** Props for PipelineOverview component */
export interface PipelineOverviewProps {
  days: PipelineDay[];
  onDayClick: (dayNumber: number) => void;
  selectedDay?: number;
}

/** Props for BatchDetailView component */
export interface BatchDetailViewProps {
  batch: BatchDetail | null;
  onClose: () => void;
  onViewEmailDraft: (fundId: string) => void;
  onMarkAsSent: (fundId: string) => void;
  onScheduleFollowUp: (fundId: string) => void;
}

/** Props for DecisionQueue component */
export interface DecisionQueueProps {
  items: DecisionQueueItem[];
  onDecision: (itemId: string, optionId: string) => void;
}

/** Props for MetricsCards component */
export interface MetricsCardsProps {
  metrics: PipelineMetrics;
}

/** Mock data configuration */
export const USE_MOCK = true;

/** Generate mock pipeline data for 5 days */
export function generateMockPipelineData(): PipelineDay[] {
  const today = new Date();
  
  const fundNames = [
    'Accel Partners', 'Bessemer Venture Partners', 'Index Ventures',
    'Benchmark Capital', 'Greylock Partners', 'Sequoia Capital',
    'Andreessen Horowitz', 'Lightspeed Venture Partners', 'IVP',
    'General Catalyst', 'Kleiner Perkins', 'First Round Capital'
  ];
  
  const partnerNames = [
    'Martin K', 'Taylor A', 'Steve C', 'Bill G', 'Sarah M',
    'Mike V', 'Marc A', 'Ravi M', 'Tom L', 'Hemant T',
    'Ilya F', 'Josh K'
  ];

  const days: PipelineDay[] = [];
  
  for (let dayNum = 1; dayNum <= 5; dayNum++) {
    const date = new Date(today);
    date.setDate(today.getDate() + (dayNum - 1));
    
    let status: BatchStatus;
    let blockedReason: string | undefined;
    let sentCount = 0;
    
    if (dayNum === 1) {
      status = 'BLOCKED';
      blockedReason = 'Awaiting Lucas decision on send timing';
    } else if (dayNum === 2) {
      status = 'READY';
    } else if (dayNum === 3) {
      status = 'IN_PROGRESS';
      sentCount = 2;
    } else if (dayNum === 4) {
      status = 'IN_PROGRESS';
      sentCount = 3;
    } else {
      status = 'COMPLETE';
      sentCount = 5;
    }
    
    const funds: PipelineFund[] = [];
    for (let i = 0; i < 5; i++) {
      const fundIndex = (dayNum - 1) * 5 + i;
      funds.push({
        id: `fund-${dayNum}-${i + 1}`,
        fundId: `fund-id-${fundIndex}`,
        fundName: fundNames[fundIndex % fundNames.length],
        partnerName: partnerNames[fundIndex % partnerNames.length],
        fitScore: 75 + Math.floor(Math.random() * 20),
        priority: i < 2 ? 'A' : i < 4 ? 'B' : 'C',
        status: i < sentCount ? 'SENT' : dayNum === 1 ? 'AWAITING_APPROVAL' : 'APPROVED',
        contactEmail: `partner${fundIndex}@fund${fundIndex}.com`,
        linkedinUrl: `https://linkedin.com/in/partner${fundIndex}`,
        emailDraft: {
          to: `partner${fundIndex}@fund${fundIndex}.com`,
          subject: `Strategic opportunity - ${fundNames[fundIndex % fundNames.length]}`,
          body: `Hi ${partnerNames[fundIndex % partnerNames.length]},\n\nI'd love to connect regarding...`,
        },
      });
    }
    
    days.push({
      dayNumber: dayNum,
      date: date.toISOString().split('T')[0],
      status,
      funds,
      totalFunds: 5,
      sentCount,
      blockedReason,
    });
  }
  
  return days;
}

/** Generate mock decision queue items */
export function generateMockDecisionQueue(): DecisionQueueItem[] {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(9, 0, 0, 0);
  
  return [
    {
      id: 'decision-1',
      type: 'BATCH_SEND',
      title: 'Day 1 Batch Send Approval',
      description: '5 funds are ready to send. Please select the preferred timing for the Day 1 outreach batch.',
      dayNumber: 1,
      deadline: tomorrow.toISOString(),
      blockedSince: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      options: [
        {
          id: 'option-a',
          label: 'Option A: Send Tomorrow Morning',
          value: 'send_morning',
          description: 'Send all 5 emails at 9:00 AM local time',
        },
        {
          id: 'option-b',
          label: 'Option B: Stagger Over 2 Days',
          value: 'stagger',
          description: 'Send 3 today, 2 tomorrow for better response tracking',
        },
        {
          id: 'option-c',
          label: 'Option C: Hold for Review',
          value: 'hold',
          description: 'Delay send until manual review of each email',
        },
      ],
      recommendation: 'option-a',
    },
  ];
}

/** Generate mock pipeline metrics */
export function generateMockMetrics(): PipelineMetrics {
  return {
    totalFundsInPipeline: 25,
    fundsSentThisWeek: 0,
    responseRate: null,
    followUpsScheduled: 0,
    fundsByStatus: {
      NEW: 0,
      QUEUED: 15,
      AWAITING_APPROVAL: 5,
      APPROVED: 3,
      SENT: 2,
      FOLLOW_UP: 0,
      CLOSED: 0,
    },
    fundsByDay: {
      1: 5,
      2: 5,
      3: 5,
      4: 5,
      5: 5,
    },
  };
}
