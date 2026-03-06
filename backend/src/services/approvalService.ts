/**
 * Approval Service
 * 
 * Business logic for the tiered approval system:
 * - Card classification
 * - Approval/rejection operations
 * - Audit logging
 * - Metrics calculation
 */

import { rulesEngine, CardData, TierClassification } from './approvalRulesEngine';
import { db } from '../db';

export interface ApprovalCard {
  id: string;
  trelloCardId?: string;
  type: 'BDR' | 'VC';
  companyName: string;
  companyId?: string;
  icpScore: number;
  contactEmail?: string;
  contactLinkedin?: string;
  contactName?: string;
  contactRole?: string;
  signals?: any[];
  investmentStage?: string;
  sector?: string[];
  fundSize?: number;
  partnerType?: string;
  tier?: number;
  confidenceScore?: number;
  autoApproved?: boolean;
  autoApprovedAt?: Date;
  status?: string;
  approvedAt?: Date;
  rejectedAt?: Date;
  reviewedBy?: string;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApprovalFilters {
  tier?: number;
  type?: 'BDR' | 'VC';
  dateFrom?: Date;
  dateTo?: Date;
  confidenceMin?: number;
  confidenceMax?: number;
  status?: string;
}

export class ApprovalService {
  /**
   * Classify a card and assign to tier
   */
  async classifyCard(cardId: string): Promise<TierClassification> {
    // Fetch card data from database
    const card = await this.getCardById(cardId);
    if (!card) {
      throw new Error(`Card not found: ${cardId}`);
    }

    // Convert to CardData format for rules engine
    const cardData: CardData = {
      id: card.id,
      type: card.type,
      companyName: card.companyName,
      icpScore: card.icpScore,
      contactEmail: card.contactEmail,
      contactLinkedin: card.contactLinkedin,
      signals: card.signals,
      investmentStage: card.investmentStage,
      sector: card.sector,
      fundSize: card.fundSize,
    };

    // Run classification
    const classification = rulesEngine.evaluate(cardData);

    // Update card with classification
    await db.query(
      `UPDATE approval_cards 
       SET tier = $1, confidence_score = $2, updated_at = NOW()
       WHERE id = $3`,
      [classification.tier, classification.confidence, cardId]
    );

    // Log classification to audit
    await this.logAuditAction(cardId, 'classified', classification.tier, classification.confidence, classification.rulesTriggered);

    // Auto-approve if Tier 1
    if (classification.tier === 1) {
      await this.autoApprove(cardId, classification);
    }

    return classification;
  }

  /**
   * Auto-approve a Tier 1 card
   */
  private async autoApprove(cardId: string, classification: TierClassification): Promise<void> {
    await db.query(
      `UPDATE approval_cards 
       SET status = 'APPROVED', auto_approved = true, auto_approved_at = NOW(), updated_at = NOW()
       WHERE id = $1`,
      [cardId]
    );

    await this.logAuditAction(cardId, 'auto_approved', 1, classification.confidence, classification.rulesTriggered, 'system');
  }

  /**
   * Manually approve a card
   */
  async approveCard(cardId: string, reviewedBy: string, notes?: string): Promise<ApprovalCard> {
    const result = await db.query(
      `UPDATE approval_cards 
       SET status = 'APPROVED', reviewed_by = $1, notes = $2, approved_at = NOW(), updated_at = NOW()
       WHERE id = $3
       RETURNING *`,
      [reviewedBy, notes, cardId]
    );

    if (result.rows.length === 0) {
      throw new Error(`Card not found: ${cardId}`);
    }

    const card = result.rows[0];
    await this.logAuditAction(cardId, 'approved', card.tier, card.confidence_score, [], reviewedBy);

    return card;
  }

  /**
   * Reject a card
   */
  async rejectCard(cardId: string, reviewedBy: string, reason?: string, notes?: string): Promise<ApprovalCard> {
    const result = await db.query(
      `UPDATE approval_cards 
       SET status = 'REJECTED', reviewed_by = $1, notes = $2, rejected_at = NOW(), updated_at = NOW()
       WHERE id = $3
       RETURNING *`,
      [reviewedBy, notes || reason, cardId]
    );

    if (result.rows.length === 0) {
      throw new Error(`Card not found: ${cardId}`);
    }

    const card = result.rows[0];
    await this.logAuditAction(cardId, 'rejected', card.tier, card.confidence_score, [], reviewedBy);

    return card;
  }

  /**
   * Escalate a Tier 2 card to Tier 3
   */
  async escalateCard(cardId: string, reviewedBy: string, reason: string): Promise<ApprovalCard> {
    const result = await db.query(
      `UPDATE approval_cards 
       SET tier = 3, status = 'PENDING', reviewed_by = $1, notes = $2, updated_at = NOW()
       WHERE id = $3
       RETURNING *`,
      [reviewedBy, reason, cardId]
    );

    if (result.rows.length === 0) {
      throw new Error(`Card not found: ${cardId}`);
    }

    const card = result.rows[0];
    await this.logAuditAction(cardId, 'escalated', 3, card.confidence_score, [], reviewedBy);

    return card;
  }

  /**
   * Batch approve multiple cards (Tier 2 only)
   */
  async batchApprove(cardIds: string[], reviewedBy: string, notes?: string): Promise<{ success: string[]; failed: { cardId: string; error: string }[] }> {
    const success: string[] = [];
    const failed: { cardId: string; error: string }[] = [];

    for (const cardId of cardIds) {
      try {
        // Only approve Tier 2 cards via batch
        const card = await this.getCardById(cardId);
        if (!card) {
          failed.push({ cardId, error: 'Card not found' });
          continue;
        }
        if (card.tier !== 2) {
          failed.push({ cardId, error: 'Only Tier 2 cards can be batch approved' });
          continue;
        }

        await this.approveCard(cardId, reviewedBy, notes);
        success.push(cardId);
      } catch (error) {
        failed.push({ cardId, error: (error as Error).message });
      }
    }

    return { success, failed };
  }

  /**
   * Flag an auto-approved card for review
   */
  async flagForReview(cardId: string, reviewedBy: string, reason: string): Promise<ApprovalCard> {
    const result = await db.query(
      `UPDATE approval_cards 
       SET tier = 3, status = 'PENDING', reviewed_by = $1, notes = $2, updated_at = NOW()
       WHERE id = $3 AND auto_approved = true
       RETURNING *`,
      [reviewedBy, reason, cardId]
    );

    if (result.rows.length === 0) {
      throw new Error(`Card not found or not auto-approved: ${cardId}`);
    }

    const card = result.rows[0];
    await this.logAuditAction(cardId, 'flagged', 3, card.confidence_score, [], reviewedBy);

    return card;
  }

  /**
   * Get cards by filters
   */
  async getCards(filters?: ApprovalFilters): Promise<ApprovalCard[]> {
    let query = 'SELECT * FROM approval_cards WHERE 1=1';
    const params: any[] = [];
    let paramIndex = 1;

    if (filters?.tier !== undefined) {
      query += ` AND tier = $${paramIndex++}`;
      params.push(filters.tier);
    }

    if (filters?.type) {
      query += ` AND type = $${paramIndex++}`;
      params.push(filters.type);
    }

    if (filters?.status) {
      query += ` AND status = $${paramIndex++}`;
      params.push(filters.status);
    }

    if (filters?.confidenceMin !== undefined) {
      query += ` AND confidence_score >= $${paramIndex++}`;
      params.push(filters.confidenceMin);
    }

    if (filters?.confidenceMax !== undefined) {
      query += ` AND confidence_score <= $${paramIndex++}`;
      params.push(filters.confidenceMax);
    }

    if (filters?.dateFrom) {
      query += ` AND created_at >= $${paramIndex++}`;
      params.push(filters.dateFrom);
    }

    if (filters?.dateTo) {
      query += ` AND created_at <= $${paramIndex++}`;
      params.push(filters.dateTo);
    }

    query += ' ORDER BY created_at DESC';

    const result = await db.query(query, params);
    return result.rows;
  }

  /**
   * Get a single card by ID
   */
  async getCardById(cardId: string): Promise<ApprovalCard | null> {
    const result = await db.query('SELECT * FROM approval_cards WHERE id = $1', [cardId]);
    return result.rows[0] || null;
  }

  /**
   * Get dashboard metrics
   */
  async getMetrics(): Promise<any> {
    // Auto-approval rate
    const autoApproveResult = await db.query(`
      SELECT 
        COUNT(*) FILTER (WHERE auto_approved = true) as auto_approved,
        COUNT(*) as total
      FROM approval_cards
      WHERE created_at >= NOW() - INTERVAL '30 days'
    `);
    const autoApprovalRate = autoApproveResult.rows[0].total > 0
      ? Math.round((autoApproveResult.rows[0].auto_approved / autoApproveResult.rows[0].total) * 100)
      : 0;

    // Tier distribution
    const tierResult = await db.query(`
      SELECT tier, COUNT(*) as count
      FROM approval_cards
      WHERE status = 'PENDING'
      GROUP BY tier
    `);
    const tierDistribution = { tier1: 0, tier2: 0, tier3: 0 };
    for (const row of tierResult.rows) {
      if (row.tier === 1) tierDistribution.tier1 = parseInt(row.count);
      if (row.tier === 2) tierDistribution.tier2 = parseInt(row.count);
      if (row.tier === 3) tierDistribution.tier3 = parseInt(row.count);
    }

    // Backlog size
    const backlogResult = await db.query(`
      SELECT COUNT(*) as count
      FROM approval_cards
      WHERE status = 'PENDING'
    `);
    const backlogSize = parseInt(backlogResult.rows[0].count);

    // Recent activity (last 10 actions)
    const activityResult = await db.query(`
      SELECT 
        a.id,
        a.card_id,
        c.company_name,
        a.action,
        a.tier,
        a.performed_by,
        a.created_at as timestamp
      FROM approval_audit_log a
      JOIN approval_cards c ON a.card_id = c.id
      ORDER BY a.created_at DESC
      LIMIT 10
    `);

    return {
      autoApprovalRate,
      avgReviewTimeSeconds: 28, // Placeholder - would calculate from actual data
      backlogSize,
      tierDistribution,
      recentActivity: activityResult.rows,
    };
  }

  /**
   * Log an action to the audit trail
   */
  private async logAuditAction(
    cardId: string,
    action: string,
    tier?: number,
    confidence?: number,
    rulesTriggered?: string[],
    performedBy: string = 'system'
  ): Promise<void> {
    await db.query(
      `INSERT INTO approval_audit_log 
       (card_id, action, tier, confidence, rules_triggered, performed_by)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [cardId, action, tier, confidence, JSON.stringify(rulesTriggered || []), performedBy]
    );
  }

  /**
   * Re-run classification on all unclassified cards
   * Intended for nightly batch job
   */
  async reclassifyUnclassified(): Promise<{ processed: number; classified: number }> {
    const result = await db.query(`
      SELECT id FROM approval_cards 
      WHERE tier IS NULL OR status = 'PENDING'
    `);

    let classified = 0;
    for (const row of result.rows) {
      try {
        await this.classifyCard(row.id);
        classified++;
      } catch (error) {
        console.error(`Failed to classify card ${row.id}:`, error);
      }
    }

    return { processed: result.rows.length, classified };
  }
}

// Singleton instance
export const approvalService = new ApprovalService();
export default approvalService;
