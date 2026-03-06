import { useState } from 'react';
import { X, Copy, Check, Mail, Linkedin, FileText, Send, ExternalLink } from 'lucide-react';
import type { BDRContact, EmailTemplate } from '../types';
import { EmailTemplateManager } from './EmailTemplateManager';
import { useUpdateContact } from '../hooks/useContacts';

interface OutreachModalProps {
  contact: BDRContact;
  studioName?: string;
  onClose: () => void;
}

function applyVariables(text: string, contact: BDRContact, studioName: string): string {
  return text
    .replace(/\{\{studio_name\}\}/g, studioName)
    .replace(/\{\{contact_name\}\}/g, contact.full_name || '')
    .replace(/\{\{first_name\}\}/g, contact.full_name?.split(' ')[0] || '')
    .replace(/\{\{my_name\}\}/g, 'Lucas Fulks');
}

function buildGmailUrl(to: string, subject: string, body: string): string {
  const params = new URLSearchParams({ view: 'cm', to, su: subject, body });
  return `https://mail.google.com/mail/?${params.toString()}`;
}

export function OutreachModal({ contact, studioName = '', onClose }: OutreachModalProps) {
  const [showTemplatePicker, setShowTemplatePicker] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [markedAs, setMarkedAs] = useState<'email' | 'linkedin' | null>(null);

  const updateContact = useUpdateContact();

  const handleSelectTemplate = (template: EmailTemplate) => {
    setSubject(applyVariables(template.subject, contact, studioName));
    setBody(applyVariables(template.body, contact, studioName));
    setShowTemplatePicker(false);
  };

  const handleCopy = async (text: string, field: string) => {
    const toCopy = field === 'all' ? `Subject: ${subject}\n\n${body}` : text;
    await navigator.clipboard.writeText(toCopy);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleMarkSent = async (channel: 'email' | 'linkedin') => {
    // Open the destination first (before async work so popup isn't blocked)
    if (channel === 'email' && contact.email) {
      window.open(buildGmailUrl(contact.email, subject, body), '_blank');
    } else if (channel === 'linkedin' && contact.linkedin_url) {
      window.open(contact.linkedin_url, '_blank');
    }

    await updateContact.mutateAsync({
      id: contact.id,
      data: {
        last_contacted_at: new Date().toISOString(),
        contact_preference: channel,
      },
    });
    setMarkedAs(channel);
    setTimeout(onClose, 1500);
  };

  return (
    <>
      {/* Template picker sits on top */}
      {showTemplatePicker && (
        <EmailTemplateManager
          onClose={() => setShowTemplatePicker(false)}
          onSelectTemplate={handleSelectTemplate}
          selectMode
        />
      )}

      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-40">
        <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-xl">

          {/* Header */}
          <div className="flex items-start justify-between p-5 border-b">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{contact.full_name}</h2>
              <p className="text-sm text-gray-500 mt-0.5">
                {contact.job_title}
                {studioName ? <span className="text-gray-400"> · {studioName}</span> : null}
              </p>
            </div>
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-500">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
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
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Subject
              </label>
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
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide">
                  Body
                </label>
                {body && (
                  <button
                    onClick={() => handleCopy(body, 'body')}
                    className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    {copiedField === 'body'
                      ? <><Check className="w-3 h-3" /> Copied</>
                      : <><Copy className="w-3 h-3" /> Copy body</>}
                  </button>
                )}
              </div>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Email body will appear here after picking a template..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono h-52 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              />
            </div>

            {/* Contact quick-copy row */}
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
                    {copiedField === 'email'
                      ? <><Check className="w-3 h-3" /> Copied</>
                      : <><Copy className="w-3 h-3" /> Copy</>}
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
                    {copiedField === 'linkedin-url'
                      ? <><Check className="w-3 h-3" /> Copied</>
                      : <><Copy className="w-3 h-3" /> Copy URL</>}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="p-5 border-t space-y-3">
            {/* Copy full email */}
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

            {/* Mark sent — opens Gmail or LinkedIn + records outreach */}
            {markedAs ? (
              <div className="w-full bg-green-50 border border-green-200 text-green-700 py-2.5 rounded-lg text-center text-sm font-medium flex items-center justify-center gap-2">
                <Check className="w-4 h-4" />
                Marked as sent via {markedAs}!
              </div>
            ) : (
              <div className="flex gap-2">
                {contact.email && (
                  <button
                    onClick={() => handleMarkSent('email')}
                    disabled={updateContact.isPending}
                    className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm font-semibold disabled:opacity-50 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <Send className="w-3.5 h-3.5" />
                    Open Gmail + Mark Sent
                  </button>
                )}
                {contact.linkedin_url && (
                  <button
                    onClick={() => handleMarkSent('linkedin')}
                    disabled={updateContact.isPending}
                    className="flex-1 bg-[#0077b5] text-white py-2.5 rounded-lg hover:bg-[#006097] flex items-center justify-center gap-2 text-sm font-semibold disabled:opacity-50 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <Linkedin className="w-3.5 h-3.5" />
                    Open LinkedIn + Mark Sent
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
