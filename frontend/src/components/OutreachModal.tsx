import { useState } from 'react';
import { X, Copy, Check, Mail, Linkedin, FileText, Send, ExternalLink, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { EmailTemplate } from '../types';
import { EmailTemplateManager } from './EmailTemplateManager';
import { api } from '../api';

// ── Generic contact shape that both BDR and VC contacts satisfy ───────────────

export interface OutreachContact {
  id: string;
  full_name: string;
  email?: string;
  linkedin_url?: string;
  /** Display-only job title (job_title for BDR, title for VC) */
  jobTitle?: string;
}

interface OutreachModalProps {
  contact: OutreachContact;
  /** Fund / studio name shown in the header subtitle */
  orgName?: string;
  /**
   * API base path for outreach logs.
   * - BDR contacts: '/bdr/contacts'
   * - VC contacts:  '/contacts'
   */
  apiBase: string;
  /**
   * Which template tab to open by default.
   * - 'studio' for game studio contacts (default)
   * - 'vc' for VC fund contacts
   */
  templateContext?: 'studio' | 'vc';
  onClose: () => void;
}

// ── Variable substitution ─────────────────────────────────────────────────────

function applyVariables(text: string, contact: OutreachContact, orgName: string): string {
  return text
    .replace(/\{\{studio_name\}\}/g, orgName)
    .replace(/\{\{fund_name\}\}/g, orgName)
    .replace(/\{\{org_name\}\}/g, orgName)
    .replace(/\{\{contact_name\}\}/g, contact.full_name || '')
    .replace(/\{\{first_name\}\}/g, contact.full_name?.split(' ')[0] || '')
    .replace(/\{\{my_name\}\}/g, 'Lucas Fulks');
}

function buildGmailUrl(to: string, subject: string, body: string): string {
  const params = new URLSearchParams({ view: 'cm', to, su: subject, body });
  return `https://mail.google.com/mail/?${params.toString()}`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 2) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ── History entry ─────────────────────────────────────────────────────────────

function HistoryEntry({ log }: { log: any }) {
  const [expanded, setExpanded] = useState(false);
  const hasContent = log.subject || log.body;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => hasContent && setExpanded(!expanded)}
        className={`w-full flex items-center gap-3 p-3 text-left ${hasContent ? 'hover:bg-gray-50 cursor-pointer' : 'cursor-default'} transition-colors`}
      >
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          log.channel === 'email' ? 'bg-blue-100' : 'bg-indigo-100'
        }`}>
          {log.channel === 'email'
            ? <Mail className="w-4 h-4 text-blue-600" />
            : <Linkedin className="w-4 h-4 text-indigo-600" />}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {log.subject || (log.channel === 'linkedin' ? 'LinkedIn message' : 'Email (no subject)')}
          </p>
          <div className="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
            <Clock className="w-3 h-3" />
            {formatDate(log.sent_at)}
            <span className="ml-1 capitalize px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-100">
              {log.channel}
            </span>
          </div>
        </div>
        {hasContent && (
          expanded ? <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0" /> : <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {expanded && hasContent && (
        <div className="border-t border-gray-100 bg-gray-50 p-3 space-y-2">
          {log.subject && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Subject</p>
              <p className="text-sm text-gray-800">{log.subject}</p>
            </div>
          )}
          {log.body && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Body</p>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">{log.body}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main modal ────────────────────────────────────────────────────────────────

export function OutreachModal({ contact, orgName = '', apiBase, templateContext = 'studio', onClose }: OutreachModalProps) {
  const [showTemplatePicker, setShowTemplatePicker] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [markedAs, setMarkedAs] = useState<'email' | 'linkedin' | null>(null);
  const qc = useQueryClient();

  const { data: historyData } = useQuery({
    queryKey: ['outreach-logs', apiBase, contact.id],
    queryFn: async () => {
      const res = await api.get(`${apiBase}/${contact.id}/outreach`);
      return res.data as { total: number; items: any[] };
    },
    enabled: !!contact.id,
  });

  const createLog = useMutation({
    mutationFn: async ({
      channel,
      subject,
      body,
    }: {
      channel: 'email' | 'linkedin';
      subject?: string;
      body?: string;
    }) => {
      const res = await api.post(`${apiBase}/${contact.id}/outreach`, { channel, subject, body });
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['outreach-logs', apiBase, contact.id] });
      // Also refresh contact list so last_contacted_at updates
      qc.invalidateQueries({ queryKey: ['vc-contacts'] });
      qc.invalidateQueries({ queryKey: ['contacts'] });
    },
  });

  const history = historyData?.items || [];

  const handleSelectTemplate = (template: EmailTemplate) => {
    setSubject(applyVariables(template.subject, contact, orgName));
    setBody(applyVariables(template.body, contact, orgName));
    setShowTemplatePicker(false);
  };

  const handleCopy = async (text: string, field: string) => {
    const toCopy = field === 'all' ? `Subject: ${subject}\n\n${body}` : text;
    await navigator.clipboard.writeText(toCopy);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleMarkSent = async (channel: 'email' | 'linkedin') => {
    if (channel === 'email' && contact.email) {
      window.open(buildGmailUrl(contact.email, subject, body), '_blank');
    } else if (channel === 'linkedin' && contact.linkedin_url) {
      window.open(contact.linkedin_url, '_blank');
    }

    await createLog.mutateAsync({
      channel,
      subject: subject || undefined,
      body: body || undefined,
    });

    setMarkedAs(channel);
    setTimeout(onClose, 1500);
  };

  return (
    <>
      {showTemplatePicker && (
        <EmailTemplateManager
          onClose={() => setShowTemplatePicker(false)}
          onSelectTemplate={handleSelectTemplate}
          selectMode
          defaultTab={templateContext}
        />
      )}

      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-40">
        <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-xl">

          {/* Header */}
          <div className="flex items-start justify-between p-5 border-b">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{contact.full_name}</h2>
              <p className="text-sm text-gray-500 mt-0.5">
                {contact.jobTitle}
                {orgName ? <span className="text-gray-400"> · {orgName}</span> : null}
              </p>
            </div>
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-500">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Scrollable body */}
          <div className="flex-1 overflow-auto p-5 space-y-4">

            {/* Template picker trigger */}
            <button
              onClick={() => setShowTemplatePicker(true)}
              className="w-full border-2 border-dashed border-gray-300 rounded-lg p-3 text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 flex items-center justify-center gap-2 transition-colors"
            >
              <FileText className="w-4 h-4" />
              {subject ? 'Change Template' : 'Pick a Template to Start'}
            </button>

            {/* Subject */}
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Subject</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Email subject..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Body */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide">Body</label>
                {body && (
                  <button
                    onClick={() => handleCopy(body, 'body')}
                    className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    {copiedField === 'body' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy body</>}
                  </button>
                )}
              </div>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Email body will appear here after picking a template..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono h-48 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              />
            </div>

            {/* Contact details quick-copy */}
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Contact Details</p>
              {contact.email && (
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700 flex-1 truncate">{contact.email}</span>
                  <button
                    onClick={() => handleCopy(contact.email!, 'email')}
                    className="flex-shrink-0 text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    {copiedField === 'email' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy</>}
                  </button>
                </div>
              )}
              {contact.linkedin_url && (
                <div className="flex items-center gap-2 text-sm">
                  <Linkedin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <a
                    href={contact.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline flex-1 truncate"
                  >
                    LinkedIn Profile
                  </a>
                  <button
                    onClick={() => handleCopy(contact.linkedin_url!, 'linkedin-url')}
                    className="flex-shrink-0 text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    {copiedField === 'linkedin-url' ? <><Check className="w-3 h-3" /> Copied</> : <><Copy className="w-3 h-3" /> Copy URL</>}
                  </button>
                </div>
              )}
            </div>

            {/* Outreach History */}
            {history.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  Outreach History ({history.length})
                </p>
                <div className="space-y-2">
                  {history.map((log: any) => (
                    <HistoryEntry key={log.id} log={log} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-5 border-t space-y-3">
            {(subject || body) && (
              <button
                onClick={() => handleCopy('', 'all')}
                className="w-full border border-gray-300 text-gray-700 py-2.5 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2 text-sm font-medium transition-colors"
              >
                {copiedField === 'all'
                  ? <><Check className="w-4 h-4 text-green-600" /> Full Email Copied!</>
                  : <><Copy className="w-4 h-4" /> Copy Full Email (Subject + Body)</>}
              </button>
            )}

            {markedAs ? (
              <div className="w-full bg-green-50 border border-green-200 text-green-700 py-2.5 rounded-lg text-center text-sm font-medium flex items-center justify-center gap-2">
                <Check className="w-4 h-4" />
                Logged + marked as sent via {markedAs}!
              </div>
            ) : (
              <div className="flex gap-2">
                {contact.email && (
                  <button
                    onClick={() => handleMarkSent('email')}
                    disabled={createLog.isPending}
                    className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm font-semibold disabled:opacity-50 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <Send className="w-3.5 h-3.5" />
                    Open Gmail + Log Sent
                  </button>
                )}
                {contact.linkedin_url && (
                  <button
                    onClick={() => handleMarkSent('linkedin')}
                    disabled={createLog.isPending}
                    className="flex-1 bg-[#0077b5] text-white py-2.5 rounded-lg hover:bg-[#006097] flex items-center justify-center gap-2 text-sm font-semibold disabled:opacity-50 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <Linkedin className="w-3.5 h-3.5" />
                    Open LinkedIn + Log Sent
                  </button>
                )}
              </div>
            )}
          </div>

        </div>
      </div>
    </>
  );
}
