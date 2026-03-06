/**
 * Trello Card Type for VC Outreach
 */
export interface TrelloCard {
  id: string;
  name: string;
  desc: string;
  idList: string;
  idBoard: string;
  due: string | null;
  dueComplete: boolean;
  labels: TrelloLabel[];
  attachments: TrelloAttachment[];
  customFieldItems: TrelloCustomFieldItem[];
  url: string;
  shortUrl: string;
  dateLastActivity: string;
}

export interface TrelloLabel {
  id: string;
  name: string;
  color: string;
}

export interface TrelloAttachment {
  id: string;
  name: string;
  url: string;
  mimeType?: string;
}

export interface TrelloCustomFieldItem {
  id: string;
  idCustomField: string;
  value?: {
    text?: string;
    number?: number;
    date?: string;
  };
}

export interface TrelloList {
  id: string;
  name: string;
  idBoard: string;
  pos: number;
}

export interface TrelloBoard {
  id: string;
  name: string;
  desc: string;
  url: string;
  shortUrl: string;
}

export interface ApprovalCard {
  id: string;
  fund: string;
  partner: string;
  priority: 'high' | 'medium' | 'low';
  hook: string;
  status: 'awaiting_approval' | 'approved' | 'rejected';
  draftMessage: string;
  notes: string;
  trelloCard: TrelloCard;
  lastActivity: Date;
}

export interface CardAction {
  type: 'approve' | 'reject' | 'edit';
  cardId: string;
  data?: {
    draftMessage?: string;
    notes?: string;
    rejectReason?: string;
  };
}