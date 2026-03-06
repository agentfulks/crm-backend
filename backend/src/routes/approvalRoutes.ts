/**
 * Approval Routes
 * 
 * REST API endpoints for the tiered approval system:
 * - GET /api/approval-dashboard - Get cards with filtering
 * - POST /api/cards/:id/classify - Classify a card
 * - POST /api/cards/:id/approve - Approve a card
 * - POST /api/cards/:id/reject - Reject a card
 * - POST /api/cards/:id/escalate - Escalate to Tier 3
 * - POST /api/cards/batch-approve - Batch approve cards
 * - GET /api/approval-metrics - Get dashboard metrics
 * - POST /api/cards/:id/flag - Flag auto-approved card
 */

import { Router, Request, Response } from 'express';
import { approvalService } from '../services/approvalService';

const router = Router();

/**
 * GET /api/approval-dashboard
 * Get cards with optional filtering by tier, type, date, confidence, status
 */
router.get('/approval-dashboard', async (req: Request, res: Response) => {
  try {
    const filters = {
      tier: req.query.tier ? parseInt(req.query.tier as string) : undefined,
      type: req.query.type as 'BDR' | 'VC' | undefined,
      status: req.query.status as string | undefined,
      confidenceMin: req.query.confidence_min ? parseFloat(req.query.confidence_min as string) : undefined,
      confidenceMax: req.query.confidence_max ? parseFloat(req.query.confidence_max as string) : undefined,
      dateFrom: req.query.date_from ? new Date(req.query.date_from as string) : undefined,
      dateTo: req.query.date_to ? new Date(req.query.date_to as string) : undefined,
    };

    const cards = await approvalService.getCards(filters);

    res.json({
      cards,
      total: cards.length,
      filters,
    });
  } catch (error) {
    console.error('Error fetching approval dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch approval dashboard' });
  }
});

/**
 * GET /api/approval-metrics
 * Get dashboard metrics (auto-approval rate, backlog size, tier distribution, etc.)
 */
router.get('/approval-metrics', async (_req: Request, res: Response) => {
  try {
    const metrics = await approvalService.getMetrics();
    res.json(metrics);
  } catch (error) {
    console.error('Error fetching approval metrics:', error);
    res.status(500).json({ error: 'Failed to fetch approval metrics' });
  }
});

/**
 * POST /api/cards/:id/classify
 * Run classification rules on a card and assign to tier
 */
router.post('/cards/:id/classify', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const classification = await approvalService.classifyCard(id);
    res.json(classification);
  } catch (error) {
    console.error('Error classifying card:', error);
    res.status(500).json({ error: 'Failed to classify card' });
  }
});

/**
 * GET /api/cards/:id
 * Get a single card by ID
 */
router.get('/cards/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const card = await approvalService.getCardById(id);
    
    if (!card) {
      return res.status(404).json({ error: 'Card not found' });
    }

    res.json(card);
  } catch (error) {
    console.error('Error fetching card:', error);
    res.status(500).json({ error: 'Failed to fetch card' });
  }
});

/**
 * POST /api/cards/:id/approve
 * Manually approve a card
 */
router.post('/cards/:id/approve', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reviewed_by, notes } = req.body;

    if (!reviewed_by) {
      return res.status(400).json({ error: 'reviewed_by is required' });
    }

    const card = await approvalService.approveCard(id, reviewed_by, notes);
    res.json(card);
  } catch (error) {
    console.error('Error approving card:', error);
    res.status(500).json({ error: 'Failed to approve card' });
  }
});

/**
 * POST /api/cards/:id/reject
 * Reject a card
 */
router.post('/cards/:id/reject', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reviewed_by, reason, notes } = req.body;

    if (!reviewed_by) {
      return res.status(400).json({ error: 'reviewed_by is required' });
    }

    const card = await approvalService.rejectCard(id, reviewed_by, reason, notes);
    res.json(card);
  } catch (error) {
    console.error('Error rejecting card:', error);
    res.status(500).json({ error: 'Failed to reject card' });
  }
});

/**
 * POST /api/cards/:id/escalate
 * Escalate a Tier 2 card to Tier 3
 */
router.post('/cards/:id/escalate', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reviewed_by, reason } = req.body;

    if (!reviewed_by) {
      return res.status(400).json({ error: 'reviewed_by is required' });
    }

    if (!reason) {
      return res.status(400).json({ error: 'reason is required' });
    }

    const card = await approvalService.escalateCard(id, reviewed_by, reason);
    res.json(card);
  } catch (error) {
    console.error('Error escalating card:', error);
    res.status(500).json({ error: 'Failed to escalate card' });
  }
});

/**
 * POST /api/cards/batch-approve
 * Batch approve multiple cards (Tier 2 only)
 */
router.post('/cards/batch-approve', async (req: Request, res: Response) => {
  try {
    const { card_ids, reviewed_by, notes } = req.body;

    if (!Array.isArray(card_ids) || card_ids.length === 0) {
      return res.status(400).json({ error: 'card_ids must be a non-empty array' });
    }

    if (!reviewed_by) {
      return res.status(400).json({ error: 'reviewed_by is required' });
    }

    const result = await approvalService.batchApprove(card_ids, reviewed_by, notes);
    res.json(result);
  } catch (error) {
    console.error('Error batch approving cards:', error);
    res.status(500).json({ error: 'Failed to batch approve cards' });
  }
});

/**
 * POST /api/cards/:id/flag
 * Flag an auto-approved card for review
 */
router.post('/cards/:id/flag', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reviewed_by, reason } = req.body;

    if (!reviewed_by) {
      return res.status(400).json({ error: 'reviewed_by is required' });
    }

    if (!reason) {
      return res.status(400).json({ error: 'reason is required' });
    }

    const card = await approvalService.flagForReview(id, reviewed_by, reason);
    res.json(card);
  } catch (error) {
    console.error('Error flagging card:', error);
    res.status(500).json({ error: 'Failed to flag card' });
  }
});

/**
 * POST /api/cards/reclassify-all
 * Re-run classification on all unclassified cards
 * Intended for admin/nightly batch use
 */
router.post('/cards/reclassify-all', async (_req: Request, res: Response) => {
  try {
    const result = await approvalService.reclassifyUnclassified();
    res.json(result);
  } catch (error) {
    console.error('Error reclassifying cards:', error);
    res.status(500).json({ error: 'Failed to reclassify cards' });
  }
});

export default router;
