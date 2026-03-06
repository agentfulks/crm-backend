/**
 * Tiered Approval System - Rules Engine
 * 
 * Implements 6 classification rules to automatically assign cards to tiers:
 * - Tier 1 (Auto-approve): 60% of cards, HIGH confidence (95%+)
 * - Tier 2 (Quick review): 25% of cards, MEDIUM confidence (85-94%)
 * - Tier 3 (Deep review): 15% of cards, LOW confidence (<85%)
 */

export interface RuleResult {
  ruleId: string;
  passed: boolean;
  confidence: number;
  metadata?: Record<string, any>;
}

export interface TierClassification {
  tier: 1 | 2 | 3;
  confidence: number;
  rulesTriggered: string[];
  reason: string;
}

export interface CardData {
  id: string;
  type: 'BDR' | 'VC';
  companyName: string;
  icpScore: number;
  contactEmail?: string;
  contactLinkedin?: string;
  signals?: CardSignal[];
  overrideFlags?: string[];
  requiredFields?: Record<string, any>;
  investmentStage?: string;
  sector?: string[];
  fundSize?: number;
}

export interface CardSignal {
  type: 'funding' | 'job_posting' | 'leadership_change' | 'tech_change' | 'other';
  date: string;
  description?: string;
}

export class ApprovalRulesEngine {
  /**
   * Main evaluation entry point
   * Runs all rules and returns tier classification
   */
  evaluate(card: CardData): TierClassification {
    const results: RuleResult[] = [
      this.checkIcpScore(card),
      this.checkContactVerification(card),
      this.checkSignalStrength(card),
      this.checkOverrideFlags(card),
      this.checkCardCompleteness(card),
      this.checkStrategicAlignment(card),
    ];

    const passedRules = results.filter(r => r.passed);
    const totalRules = results.length;
    const confidence = this.calculateConfidence(results);
    const rulesTriggered = passedRules.map(r => r.ruleId);

    // Determine tier based on confidence and rules passed
    let tier: 1 | 2 | 3;
    let reason: string;

    if (confidence >= 95 && passedRules.length >= 5) {
      tier = 1;
      reason = 'Meets all auto-approval criteria';
    } else if (confidence >= 85 && passedRules.length >= 4) {
      tier = 2;
      reason = `Only ${passedRules.length}/${totalRules} rules met, needs quick review`;
    } else {
      tier = 3;
      reason = 'Complex scenario requiring deep review';
    }

    return {
      tier,
      confidence,
      rulesTriggered,
      reason,
    };
  }

  /**
   * RULE-01: ICP Score Check
   * BDR: ICP score >= 3
   * VC: ICP score >= 4
   */
  private checkIcpScore(card: CardData): RuleResult {
    const threshold = card.type === 'BDR' ? 3 : 4;
    const passed = card.icpScore >= threshold;
    
    return {
      ruleId: 'RULE-01',
      passed,
      confidence: passed ? 100 : Math.max(0, (card.icpScore / threshold) * 100),
      metadata: { icpScore: card.icpScore, threshold, type: card.type },
    };
  }

  /**
   * RULE-02: Contact Verification
   * Valid email format OR valid LinkedIn URL
   */
  private checkContactVerification(card: CardData): RuleResult {
    const emailValid = this.isValidEmail(card.contactEmail);
    const linkedinValid = this.isValidLinkedIn(card.contactLinkedin);
    const passed = emailValid || linkedinValid;

    return {
      ruleId: 'RULE-02',
      passed,
      confidence: passed ? 100 : 0,
      metadata: { emailValid, linkedinValid },
    };
  }

  /**
   * RULE-03: Signal Strength (BDR only)
   * At least 2 signals from: funding, job posting, leadership change, tech change
   */
  private checkSignalStrength(card: CardData): RuleResult {
    // VC cards bypass this rule (handled by strategic alignment instead)
    if (card.type === 'VC') {
      return {
        ruleId: 'RULE-03',
        passed: true,
        confidence: 100,
        metadata: { note: 'VC cards use strategic alignment rule' },
      };
    }

    const validSignals = (card.signals || []).filter(signal => {
      const validTypes = ['funding', 'job_posting', 'leadership_change', 'tech_change'];
      if (!validTypes.includes(signal.type)) return false;
      
      // Check signal freshness based on type
      const daysAgo = this.daysSince(signal.date);
      switch (signal.type) {
        case 'funding': return daysAgo <= 180; // 6 months
        case 'job_posting': return daysAgo <= 30; // 30 days
        case 'leadership_change': return daysAgo <= 90; // 3 months
        case 'tech_change': return daysAgo <= 60; // 60 days
        default: return false;
      }
    });

    const passed = validSignals.length >= 2;
    const confidence = Math.min(100, (validSignals.length / 2) * 100);

    return {
      ruleId: 'RULE-03',
      passed,
      confidence,
      metadata: { validSignals: validSignals.length, signals: card.signals?.length || 0 },
    };
  }

  /**
   * RULE-04: No Override Flags
   * Card must not have manual override flags
   */
  private checkOverrideFlags(card: CardData): RuleResult {
    const flags = card.overrideFlags || [];
    const blockedFlags = ['needs_lucas_review', 'manual_review_required', 'watch_list', 'exclude_list'];
    const hasBlockedFlag = flags.some(f => blockedFlags.includes(f.toLowerCase()));
    const passed = !hasBlockedFlag;

    return {
      ruleId: 'RULE-04',
      passed,
      confidence: passed ? 100 : 0,
      metadata: { flags, hasBlockedFlag },
    };
  }

  /**
   * RULE-05: Card Completeness
   * All required fields must be populated
   */
  private checkCardCompleteness(card: CardData): RuleResult {
    const requiredFields = ['companyName', 'type', 'icpScore'];
    const missingFields = requiredFields.filter(field => {
      const value = (card as any)[field];
      return value === undefined || value === null || value === '';
    });

    const passed = missingFields.length === 0;
    const confidence = passed ? 100 : Math.max(0, ((requiredFields.length - missingFields.length) / requiredFields.length) * 100);

    return {
      ruleId: 'RULE-05',
      passed,
      confidence,
      metadata: { missingFields, requiredFields },
    };
  }

  /**
   * RULE-06: Strategic Alignment (VC only)
   * Investment stage matches target and sector aligns with thesis
   */
  private checkStrategicAlignment(card: CardData): RuleResult {
    // BDR cards bypass this rule
    if (card.type === 'BDR') {
      return {
        ruleId: 'RULE-06',
        passed: true,
        confidence: 100,
        metadata: { note: 'BDR cards use signal strength rule' },
      };
    }

    const targetStages = ['seed', 'series a', 'series b', 'seed-series a', 'seed-series b'];
    const stageMatch = card.investmentStage && 
      targetStages.some(stage => card.investmentStage!.toLowerCase().includes(stage));
    
    const targetSectors = ['gaming', 'ai', 'creative', 'interactive entertainment'];
    const sectorMatch = card.sector && 
      card.sector.some(s => targetSectors.some(ts => s.toLowerCase().includes(ts)));

    const passed = stageMatch || sectorMatch;
    const confidence = (stageMatch && sectorMatch) ? 100 : (stageMatch || sectorMatch) ? 70 : 0;

    return {
      ruleId: 'RULE-06',
      passed,
      confidence,
      metadata: { stageMatch, sectorMatch, investmentStage: card.investmentStage, sectors: card.sector },
    };
  }

  /**
   * Calculate overall confidence score
   */
  private calculateConfidence(results: RuleResult[]): number {
    if (results.length === 0) return 0;
    const totalConfidence = results.reduce((sum, r) => sum + r.confidence, 0);
    return Math.round(totalConfidence / results.length);
  }

  /**
   * Validate email format
   */
  private isValidEmail(email?: string): boolean {
    if (!email) return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) && !email.includes('gmail.com') && !email.includes('yahoo.com');
  }

  /**
   * Validate LinkedIn URL format
   */
  private isValidLinkedIn(url?: string): boolean {
    if (!url) return false;
    return url.includes('linkedin.com/in/') || url.includes('linkedin.com/company/');
  }

  /**
   * Calculate days since a date
   */
  private daysSince(dateStr: string): number {
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    return Math.floor(diffTime / (1000 * 60 * 60 * 24));
  }
}

// Singleton instance
export const rulesEngine = new ApprovalRulesEngine();
export default rulesEngine;
