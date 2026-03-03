import { useState, useEffect } from 'react';
import { Mail, FileText, Copy, Check } from 'lucide-react';

interface EmailDraft {
  id: string;
  studioName: string;
  contactName: string;
  contactRole: string;
  subject: string;
  body: string;
  source: string;
}

export function EmailDrafts() {
  const [drafts, setDrafts] = useState<EmailDraft[]>([]);
  const [selectedDraft, setSelectedDraft] = useState<EmailDraft | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDrafts();
  }, []);

  const loadDrafts = async () => {
    setIsLoading(true);
    try {
      // Load from localStorage first (for cached data)
      const cached = localStorage.getItem('emailDrafts');
      if (cached) {
        setDrafts(JSON.parse(cached));
      }
      
      // In production, this would fetch from the API
      // const response = await fetch('/api/email-drafts');
      // const data = await response.json();
      
      // For now, use placeholder data structure
      const placeholderDrafts: EmailDraft[] = [
        {
          id: '1',
          studioName: 'Voodoo',
          contactName: 'Alexandre Yazdi',
          contactRole: 'CEO & Co-founder',
          subject: 'Partnership opportunity - scaling mobile game monetization',
          body: `Hi Alexandre,

I'm reaching out from [Company] - we're building tools that help hyper-casual publishers like Voodoo maximize LTV while reducing operational overhead.

Given Voodoo's aggressive growth toward $1B revenue, I imagine you're constantly evaluating partnerships that can accelerate user acquisition efficiency.

We've helped similar studios:
• Increase Day 7 retention by 23% through automated live ops
• Reduce manual campaign management by 60%
• Scale from 10 to 50 live titles without adding headcount

Worth a 15-minute conversation to see if there's a fit?

Best,
[Your name]`,
          source: '/deliverables/bdr_game_studios/email_drafts/01_voodoo.txt'
        },
        {
          id: '2',
          studioName: 'SayGames',
          contactName: 'Egor Vaihanski',
          contactRole: 'CEO & Co-founder',
          subject: 'Helping your $10M dev program partners hit KPIs faster',
          body: `Hi Egor,

SayGames' $10M hyper-casual dev program is impressive - you're betting big on external partnerships.

I'm curious: are your developer partners hitting their KPIs consistently? We work with publishers to give their external devs better tools for optimization and faster iteration cycles.

Result: partners hit milestones 40% faster, publish more titles, and stick around longer.

Worth exploring how this might work for SayGames' ecosystem?

Best,
[Your name]`,
          source: '/deliverables/bdr_game_studios/email_drafts/02_saygames.txt'
        },
        {
          id: '3',
          studioName: 'Homa Games',
          contactName: 'Daniel Nathan',
          contactRole: 'Founder & CEO',
          subject: 'Scaling infrastructure for Homa\'s acquisition strategy',
          body: `Hi Daniel,

With Homa's recent acquisition of Ducky Games and the $165M war chest, you're clearly in expansion mode.

Question: as you bring more studios into the Homa ecosystem, how are you handling the operational complexity? Each acquisition adds new tech stacks, new processes, new reporting requirements.

We've helped publishers consolidate their multi-studio operations into a unified platform that actually scales.

Happy to share how if you're open to a quick chat?

Best,
[Your name]`,
          source: '/deliverables/bdr_game_studios/email_drafts/03_homa_games.txt'
        },
        {
          id: '4',
          studioName: 'Kwalee',
          contactName: 'David Darling',
          contactRole: 'Founder & CEO',
          subject: 'Cross-platform tools for Kwalee\'s PC/console expansion',
          body: `Hi David,

Kwalee's expansion into PC and console is smart - but I imagine you're hitting friction managing releases across mobile + desktop + console simultaneously.

We've built tooling specifically for publishers making this exact transition. Same team, same workflows, now publishing everywhere without the headache.

Given your legendary background in games, I'd love to get your take on whether this is a problem you're actively solving.

Open to a brief conversation?

Best,
[Your name]`,
          source: '/deliverables/bdr_game_studios/email_drafts/05_kwalee.txt'
        },
        {
          id: '5',
          studioName: 'CrazyLabs',
          contactName: 'Sagi Schliesser',
          contactRole: 'CEO & Founder',
          subject: 'Managing CrazyLabs\' developer network at Embracer scale',
          body: `Hi Sagi,

CrazyLabs + Embracer Group is a powerful combination. 7B+ downloads, 15-year track record, and now part of one of the largest gaming groups on earth.

As you scale within Embracer's ecosystem, how are you managing your massive developer network? The complexity only increases as you grow.

We've helped publishers with large external dev networks streamline operations and improve partner success rates.

Would a brief conversation be useful?

Best,
[Your name]`,
          source: '/deliverables/bdr_game_studios/email_drafts/07_crazylabs.txt'
        }
      ];
      
      setDrafts(placeholderDrafts);
      localStorage.setItem('emailDrafts', JSON.stringify(placeholderDrafts));
    } catch (error) {
      console.error('Failed to load email drafts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (draft: EmailDraft, type: 'subject' | 'body' | 'full') => {
    let text = '';
    if (type === 'subject') text = draft.subject;
    else if (type === 'body') text = draft.body;
    else text = `Subject: ${draft.subject}\n\n${draft.body}`;
    
    await navigator.clipboard.writeText(text);
    setCopiedId(`${draft.id}-${type}`);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
            <div className="h-5 bg-gray-200 rounded mb-2 w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded mb-2 w-1/4"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-2xl font-bold text-gray-900">{drafts.length}</p>
          <p className="text-sm text-gray-500">Email Drafts</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-2xl font-bold text-gray-900">{drafts.filter(d => d.contactName).length}</p>
          <p className="text-sm text-gray-500">With Verified Contacts</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-2xl font-bold text-gray-900">5</p>
          <p className="text-sm text-gray-500">Top Priority Studios</p>
        </div>
      </div>

      {/* Drafts List */}
      <div className="space-y-4">
        {drafts.map((draft) => (
          <div 
            key={draft.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div 
              className="p-4 border-b border-gray-100 cursor-pointer"
              onClick={() => setSelectedDraft(selectedDraft?.id === draft.id ? null : draft)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Mail className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{draft.studioName}</h3>
                    <p className="text-sm text-gray-500">
                      {draft.contactName} • {draft.contactRole}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy(draft, 'full');
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Copy full email"
                  >
                    {copiedId === `${draft.id}-full` ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Expanded Content */}
            {selectedDraft?.id === draft.id && (
              <div className="p-4 bg-gray-50 border-t border-gray-100">
                <div className="space-y-4">
                  {/* Subject */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Subject
                      </label>
                      <button
                        onClick={() => handleCopy(draft, 'subject')}
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                      >
                        {copiedId === `${draft.id}-subject` ? (
                          <><Check className="w-3 h-3" /> Copied</>
                        ) : (
                          <><Copy className="w-3 h-3" /> Copy</>
                        )}
                      </button>
                    </div>
                    <div className="p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-900">
                      {draft.subject}
                    </div>
                  </div>

                  {/* Body */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Body
                      </label>
                      <button
                        onClick={() => handleCopy(draft, 'body')}
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                      >
                        {copiedId === `${draft.id}-body` ? (
                          <><Check className="w-3 h-3" /> Copied</>
                        ) : (
                          <><Copy className="w-3 h-3" /> Copy</>
                        )}
                      </button>
                    </div>
                    <div className="p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-900 whitespace-pre-wrap font-mono leading-relaxed">
                      {draft.body}
                    </div>
                  </div>

                  {/* Source */}
                  {draft.source && (
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <FileText className="w-3 h-3" />
                      <span>Source: {draft.source}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {drafts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No email drafts yet</h3>
          <p className="text-gray-500">Email drafts will appear here once created</p>
        </div>
      )}
    </div>
  );
}
