// Types matching backend models

export type Priority = 'A' | 'B' | 'C';

export type FundStatus = 
  | 'NEW' 
  | 'RESEARCHING' 
  | 'READY' 
  | 'APPROVED' 
  | 'SENT' 
  | 'FOLLOW_UP' 
  | 'CLOSED';

export type PacketStatus = 
  | 'NEW'
  | 'QUEUED' 
  | 'AWAITING_APPROVAL' 
  | 'APPROVED' 
  | 'SENT' 
  | 'FOLLOW_UP' 
  | 'CLOSED';

export interface Fund {
  id: string;
  name: string;
  firm_type?: string;
  hq_city?: string;
  hq_region?: string;
  hq_country?: string;
  stage_focus: string[];
  check_size_min?: number;
  check_size_max?: number;
  check_size_currency?: string;
  target_countries: string[];
  website_url?: string;
  linkedin_url?: string;
  twitter_url?: string;
  funding_requirements?: string;
  overview?: string;
  contact_email?: string;
  score?: number;
  priority: Priority;
  status: FundStatus;
  data_source?: string;
  source_row_id?: string;
  tags: Record<string, unknown>;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmailDraft {
  to: string;
  subject: string;
  body: string;
  attachments?: string[];
}

export interface Packet {
  id: string;
  fund_id: string;
  fund?: Fund;
  trello_card_id?: string;
  trello_card_url?: string;
  status: PacketStatus;
  priority: Priority;
  score_snapshot?: number;
  created_by?: string;
  approved_at?: string;
  sent_at?: string;
  follow_up_due?: string;
  crm_status?: Record<string, unknown>;
  email_draft?: EmailDraft;
  created_at: string;
  updated_at: string;
}

export interface GameStudio {
  id: string;
  name: string;
  hq_city?: string;
  hq_region?: string;
  hq_country?: string;
  studio_type?: string;
  employee_count?: string;
  downloads?: string;
  revenue?: string;
  recent_games?: string[];
  website_url?: string;
  linkedin_url?: string;
  overview?: string;
  priority: Priority;
  status: FundStatus;
  icp_score?: number;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudioPacket {
  id: string;
  studio_id: string;
  studio?: GameStudio;
  contact_name?: string;
  contact_role?: string;
  contact_email?: string;
  contact_linkedin?: string;
  status: PacketStatus;
  priority: Priority;
  score_snapshot?: number;
  email_draft?: EmailDraft;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  template_type: 'studio' | 'vc';
  subject: string;
  body: string;
  variables?: string;
  is_active: boolean;
  is_default: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
}

export interface EmailTemplateListResponse {
  total: number;
  items: EmailTemplate[];
}

export interface BDRContact {
  id: string;
  company_id: string;
  full_name: string;
  job_title?: string;
  department?: string;
  seniority_level?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  is_decision_maker: boolean;
  is_champion: boolean;
  email_verified: boolean;
  timezone?: string;
  last_contacted_at?: string;
  contact_preference?: string;
  notes?: string;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

/** Contact record associated with a VC fund (contacts table). */
export interface VCContact {
  id: string;
  fund_id: string;
  fund_name?: string;
  full_name: string;
  title?: string;       // job title
  email?: string;
  phone?: string;
  linkedin_url?: string;
  department?: string;
  seniority_level?: string;
  is_primary: boolean;
  email_verified: boolean;
  is_flagged: boolean;
  timezone?: string;
  last_contacted_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface VCContactListResponse {
  total: number;
  items: VCContact[];
}

export interface BDROutreachLog {
  id: string;
  contact_id: string;
  channel: 'email' | 'linkedin';
  subject?: string;
  body?: string;
  sent_at: string;
}

/** Outreach log for VC contacts (contacts table). Same shape as BDROutreachLog. */
export type VCOutreachLog = BDROutreachLog;

export interface PacketListResponse {
  total: number;
  items: Packet[];
}

export interface QueueStatus {
  date: string;
  total_queued: number;
  awaiting_approval: number;
  approved_today: number;
  sent_today: number;
}

export type KanbanColumn = 'backlog' | 'todo' | 'doing' | 'review' | 'complete';
export type KanbanCardType = 'custom' | 'vc' | 'studio' | 'contact';

export interface KanbanCard {
  id: string;
  title: string;
  description?: string;
  column: KanbanColumn;
  position: number;
  card_type: KanbanCardType;
  source_id?: string;
  source_data?: Record<string, any>;
  priority?: Priority;
  due_date?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}