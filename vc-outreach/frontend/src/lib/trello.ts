import { TrelloCard, TrelloList, ApprovalCard } from '@/types/trello';

const BOARD_ID = '699d2728fd2ae8c35d1f7a24';
const MATON_BASE_URL = 'https://gateway.maton.ai/trello/1';

/**
 * Get the Maton API key from environment
 */
function getApiKey(): string {
  const key = process.env.MATON_API_KEY;
  if (!key) {
    throw new Error('MATON_API_KEY not configured');
  }
  return key;
}

/**
 * Make a request to Trello via Maton gateway
 */
async function trelloRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
  const url = `${MATON_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${getApiKey()}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Trello API error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Parse card description to extract structured data
 */
function parseCardData(card: TrelloCard): Partial<ApprovalCard> {
  const lines = card.desc.split('\n');
  const data: Partial<ApprovalCard> = {
    fund: '',
    partner: '',
    priority: 'medium',
    hook: '',
    draftMessage: '',
    notes: '',
  };

  let currentSection: 'draft' | 'notes' | null = null;
  let draftLines: string[] = [];
  let notesLines: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('**Fund:**')) {
      data.fund = trimmed.replace('**Fund:**', '').trim();
    } else if (trimmed.startsWith('**Partner:**')) {
      data.partner = trimmed.replace('**Partner:**', '').trim();
    } else if (trimmed.startsWith('**Priority:**')) {
      const priority = trimmed.replace('**Priority:**', '').trim().toLowerCase();
      data.priority = (['high', 'medium', 'low'].includes(priority) ? priority : 'medium') as ApprovalCard['priority'];
    } else if (trimmed.startsWith('**Hook:**')) {
      data.hook = trimmed.replace('**Hook:**', '').trim();
    } else if (trimmed.startsWith('--- Draft Message ---')) {
      currentSection = 'draft';
    } else if (trimmed.startsWith('--- Notes ---')) {
      currentSection = 'notes';
    } else if (currentSection === 'draft') {
      draftLines.push(line);
    } else if (currentSection === 'notes') {
      notesLines.push(line);
    }
  }

  data.draftMessage = draftLines.join('\n').trim();
  data.notes = notesLines.join('\n').trim();

  return data;
}

/**
 * Build card description from structured data
 */
function buildCardDescription(data: Partial<ApprovalCard>): string {
  return `**Fund:** ${data.fund || 'N/A'}
**Partner:** ${data.partner || 'N/A'}
**Priority:** ${data.priority || 'medium'}
**Hook:** ${data.hook || 'N/A'}

--- Draft Message ---
${data.draftMessage || ''}

--- Notes ---
${data.notes || ''}`;
}

/**
 * Get cards from the Pipeline Build list awaiting approval
 */
export async function getApprovalCards(): Promise<ApprovalCard[]> {
  // Get all lists on the board
  const lists: TrelloList[] = await trelloRequest(`/boards/${BOARD_ID}/lists`);
  
  // Find the "Pipeline Build" list
  const pipelineList = lists.find(l => l.name.toLowerCase().includes('pipeline'));
  if (!pipelineList) {
    throw new Error('Pipeline Build list not found');
  }

  // Get cards from that list
  const cards: TrelloCard[] = await trelloRequest(`/lists/${pipelineList.id}/cards?customFieldItems=true&attachments=true`);

  // Transform to ApprovalCards
  return cards.map(card => {
    const parsed = parseCardData(card);
    return {
      id: card.id,
      fund: parsed.fund || card.name,
      partner: parsed.partner || 'Unknown',
      priority: parsed.priority || 'medium',
      hook: parsed.hook || '',
      status: 'awaiting_approval',
      draftMessage: parsed.draftMessage || '',
      notes: parsed.notes || '',
      trelloCard: card,
      lastActivity: new Date(card.dateLastActivity),
    };
  });
}

/**
 * Get a single card by ID
 */
export async function getCard(cardId: string): Promise<ApprovalCard> {
  const card: TrelloCard = await trelloRequest(`/cards/${cardId}?customFieldItems=true&attachments=true`);
  const parsed = parseCardData(card);
  
  return {
    id: card.id,
    fund: parsed.fund || card.name,
    partner: parsed.partner || 'Unknown',
    priority: parsed.priority || 'medium',
    hook: parsed.hook || '',
    status: 'awaiting_approval',
    draftMessage: parsed.draftMessage || '',
    notes: parsed.notes || '',
    trelloCard: card,
    lastActivity: new Date(card.dateLastActivity),
  };
}

/**
 * Approve a card - moves it to the next list
 */
export async function approveCard(cardId: string): Promise<void> {
  // Get all lists
  const lists: TrelloList[] = await trelloRequest(`/boards/${BOARD_ID}/lists`);
  
  // Find target list (e.g., "Approved" or "Ready to Send")
  const targetList = lists.find(l => 
    l.name.toLowerCase().includes('approved') || 
    l.name.toLowerCase().includes('ready') ||
    l.name.toLowerCase().includes('send')
  );
  
  if (!targetList) {
    throw new Error('Target list for approved cards not found');
  }

  // Move card to target list
  await trelloRequest(`/cards/${cardId}`, {
    method: 'PUT',
    body: JSON.stringify({ idList: targetList.id }),
  });

  // Add approval comment
  await trelloRequest(`/cards/${cardId}/actions/comments`, {
    method: 'POST',
    body: JSON.stringify({ text: '✅ Approved and moved to next stage' }),
  });
}

/**
 * Reject a card - adds comment with reason
 */
export async function rejectCard(cardId: string, reason?: string): Promise<void> {
  const comment = reason 
    ? `❌ Rejected: ${reason}` 
    : '❌ Rejected';
  
  await trelloRequest(`/cards/${cardId}/actions/comments`, {
    method: 'POST',
    body: JSON.stringify({ text: comment }),
  });
}

/**
 * Update card content (draft message and notes)
 */
export async function updateCard(cardId: string, updates: { draftMessage?: string; notes?: string }): Promise<void> {
  // Get current card
  const card: TrelloCard = await trelloRequest(`/cards/${cardId}`);
  const current = parseCardData(card);
  
  // Build new description
  const newDescription = buildCardDescription({
    ...current,
    draftMessage: updates.draftMessage ?? current.draftMessage,
    notes: updates.notes ?? current.notes,
  });

  // Update card
  await trelloRequest(`/cards/${cardId}`, {
    method: 'PUT',
    body: JSON.stringify({ desc: newDescription }),
  });
}