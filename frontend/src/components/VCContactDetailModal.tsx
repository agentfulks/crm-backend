import { useState } from 'react';
import {
  X, Mail, Linkedin, Phone, Star, CheckCircle, Clock,
  ChevronDown, ChevronUp, Trash2, Send, Edit3, Save, RotateCcw, Flag,
} from 'lucide-react';
import type { VCContact, VCOutreachLog } from '../types';
import {
  useUpdateVCContact,
  useVCOutreachLogs,
  useDeleteVCOutreachLog,
} from '../hooks/useVCContacts';
import { OutreachModal } from './OutreachModal';
import { HunterContactPanel } from './HunterContactPanel';
import { deriveDomain } from '../lib/hunterApi';

interface Props {
  contact: VCContact;
  fundName?: string;
  fundWebsite?: string;
  onClose: () => void;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatTs(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  const time = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  const date = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  if (diffMins < 2) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago · ${time}`;
  if (diffDays === 1) return `yesterday · ${time}`;
  if (diffDays < 7) return `${diffDays}d ago · ${date}`;
  return date;
}

// ── Outreach log row ───────────────────────────────────────────────────────────

function LogEntry({
  log,
  contactId,
}: {
  log: VCOutreachLog;
  contactId: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const deleteLog = useDeleteVCOutreachLog();
  const hasContent = !!(log.subject || log.body);

  const handleDelete = async () => {
    await deleteLog.mutateAsync({ contactId, logId: log.id });
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="flex items-center gap-2 p-3 bg-white">
        {/* Channel icon */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          log.channel === 'email' ? 'bg-blue-100' : 'bg-[#e8f0fb]'
        }`}>
          {log.channel === 'email'
            ? <Mail className="w-4 h-4 text-blue-600" />
            : <Linkedin className="w-4 h-4 text-[#0077b5]" />}
        </div>

        {/* Summary */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {log.subject || (log.channel === 'linkedin' ? 'LinkedIn outreach' : 'Email (no subject)')}
          </p>
          <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
            <Clock className="w-3 h-3" />
            {formatTs(log.sent_at)}
            <span className="ml-1 capitalize px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-600">
              {log.channel}
            </span>
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {hasContent && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
              title={expanded ? 'Collapse' : 'Show message'}
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
          {confirming ? (
            <div className="flex items-center gap-1">
              <button
                onClick={handleDelete}
                disabled={deleteLog.isPending}
                className="text-xs text-red-600 font-semibold hover:text-red-800 px-1.5"
              >
                {deleteLog.isPending ? '…' : 'Confirm'}
              </button>
              <button
                onClick={() => setConfirming(false)}
                className="text-xs text-gray-500 hover:text-gray-700 px-1"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirming(true)}
              className="p-1 text-gray-300 hover:text-red-500 rounded transition-colors"
              title="Delete this entry"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Expanded content */}
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

// ── Field component ────────────────────────────────────────────────────────────

function Field({
  label,
  value,
  onChange,
  type = 'text',
  editing,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  editing: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
        {label}
      </label>
      {editing ? (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      ) : (
        <p className="text-sm text-gray-800 py-1 min-h-[32px]">{value || <span className="text-gray-400 italic">—</span>}</p>
      )}
    </div>
  );
}

// ── Main modal ─────────────────────────────────────────────────────────────────

export function VCContactDetailModal({ contact, fundName = '', fundWebsite, onClose }: Props) {
  const [editing, setEditing] = useState(false);
  const [showOutreach, setShowOutreach] = useState(false);

  // Editable fields
  const [fullName, setFullName] = useState(contact.full_name || '');
  const [title, setTitle] = useState(contact.title || '');
  const [department, setDepartment] = useState(contact.department || '');
  const [email, setEmail] = useState(contact.email || '');
  const [phone, setPhone] = useState(contact.phone || '');
  const [linkedinUrl, setLinkedinUrl] = useState(contact.linkedin_url || '');
  const [timezone, setTimezone] = useState(contact.timezone || '');
  const [seniorityLevel, setSeniorityLevel] = useState(contact.seniority_level || '');
  const [notes, setNotes] = useState(contact.notes || '');
  const [isPrimary, setIsPrimary] = useState(contact.is_primary);
  const [emailVerified, setEmailVerified] = useState(contact.email_verified);

  const updateContact = useUpdateVCContact();
  const { data: historyData, isLoading: historyLoading } = useVCOutreachLogs(contact.id);
  const history = historyData?.items || [];

  const handleDiscard = () => {
    setFullName(contact.full_name || '');
    setTitle(contact.title || '');
    setDepartment(contact.department || '');
    setEmail(contact.email || '');
    setPhone(contact.phone || '');
    setLinkedinUrl(contact.linkedin_url || '');
    setTimezone(contact.timezone || '');
    setSeniorityLevel(contact.seniority_level || '');
    setNotes(contact.notes || '');
    setIsPrimary(contact.is_primary);
    setEmailVerified(contact.email_verified);
    setEditing(false);
  };

  const handleSave = async () => {
    await updateContact.mutateAsync({
      id: contact.id,
      data: {
        full_name: fullName,
        title,
        department,
        email,
        phone,
        linkedin_url: linkedinUrl,
        timezone,
        seniority_level: seniorityLevel,
        notes,
        is_primary: isPrimary,
        email_verified: emailVerified,
      },
    });
    setEditing(false);
  };

  if (showOutreach) {
    return (
      <OutreachModal
        contact={{ id: contact.id, full_name: fullName, email, linkedin_url: linkedinUrl, jobTitle: title }}
        orgName={fundName}
        apiBase="/contacts"
        templateContext="vc"
        onClose={() => setShowOutreach(false)}
      />
    );
  }

  const lastContacted = contact.last_contacted_at
    ? formatTs(contact.last_contacted_at)
    : null;

  const nameParts = fullName.trim().split(/\s+/);
  const hunterFirstName = nameParts[0] || '';
  const hunterLastName = nameParts.slice(1).join(' ') || '';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-40">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[92vh] flex flex-col shadow-xl">

        {/* ── Header ── */}
        <div className="flex items-start justify-between p-5 border-b gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <span className="text-indigo-600 font-bold text-xl">
                {(editing ? fullName : contact.full_name)?.[0]?.toUpperCase() || '?'}
              </span>
            </div>
            <div className="min-w-0">
              {editing ? (
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="text-lg font-semibold text-gray-900 border-b border-blue-400 focus:outline-none bg-transparent w-full"
                />
              ) : (
                <h2 className="text-lg font-semibold text-gray-900 truncate">{contact.full_name}</h2>
              )}
              <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                {fundName && (
                  <span className="text-sm text-gray-500">{fundName}</span>
                )}
                {isPrimary && (
                  <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                    <Star className="w-3 h-3" /> Primary
                  </span>
                )}
                {lastContacted && (
                  <span className="text-xs px-2 py-0.5 rounded-full flex items-center gap-1 bg-blue-100 text-blue-700">
                    <Mail className="w-3 h-3" />
                    {lastContacted}
                  </span>
                )}
                {lastContacted && (
                  <button
                    onClick={async () => {
                      if (!confirm('Reset "last contacted at"? This only clears the date — it does not delete message history.')) return;
                      await updateContact.mutateAsync({ id: contact.id, data: { last_contacted_at: null } as any });
                    }}
                    title="Reset last contacted date"
                    className="text-gray-300 hover:text-red-400 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Flag toggle */}
            <button
              onClick={() => updateContact.mutate({ id: contact.id, data: { is_flagged: !contact.is_flagged } })}
              title={contact.is_flagged ? 'Remove flag' : 'Flag as bad data'}
              className={`flex items-center gap-1.5 text-sm px-2.5 py-1.5 rounded-lg border transition-colors ${
                contact.is_flagged
                  ? 'bg-red-50 border-red-300 text-red-600 hover:bg-red-100'
                  : 'border-gray-300 text-gray-400 hover:border-red-400 hover:text-red-500 hover:bg-red-50'
              }`}
            >
              <Flag className="w-3.5 h-3.5" fill={contact.is_flagged ? 'currentColor' : 'none'} />
              {contact.is_flagged ? 'Flagged' : 'Flag'}
            </button>

            {editing ? (
              <>
                <button
                  onClick={handleDiscard}
                  className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Discard
                </button>
                <button
                  onClick={handleSave}
                  disabled={updateContact.isPending}
                  className="flex items-center gap-1 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  {updateContact.isPending ? 'Saving…' : 'Save'}
                </button>
              </>
            ) : (
              <button
                onClick={() => setEditing(true)}
                className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50"
              >
                <Edit3 className="w-3.5 h-3.5" /> Edit
              </button>
            )}
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* ── Scrollable body ── */}
        <div className="flex-1 overflow-auto p-5 space-y-6">

          {/* Contact fields */}
          <div className="grid grid-cols-2 gap-4">
            <Field label="Job Title" value={title} onChange={setTitle} editing={editing} />
            <Field label="Department" value={department} onChange={setDepartment} editing={editing} />
            <Field label="Email" value={email} onChange={setEmail} type="email" editing={editing} />
            <Field label="Phone" value={phone} onChange={setPhone} type="tel" editing={editing} />
            <div className="col-span-2">
              <Field label="LinkedIn URL" value={linkedinUrl} onChange={setLinkedinUrl} editing={editing} />
            </div>
            <Field label="Timezone" value={timezone} onChange={setTimezone} editing={editing} />
            {editing ? (
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Seniority</label>
                <select
                  value={seniorityLevel}
                  onChange={(e) => setSeniorityLevel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">—</option>
                  <option value="executive">Executive</option>
                  <option value="senior">Senior</option>
                  <option value="mid">Mid</option>
                  <option value="junior">Junior</option>
                </select>
              </div>
            ) : seniorityLevel ? (
              <Field label="Seniority" value={seniorityLevel} onChange={setSeniorityLevel} editing={false} />
            ) : null}
          </div>

          {/* Toggles */}
          <div className="flex gap-4">
            {[
              { label: 'Primary Contact', icon: <Star className="w-3.5 h-3.5" />, value: isPrimary, set: setIsPrimary },
              { label: 'Email Verified', icon: <CheckCircle className="w-3.5 h-3.5" />, value: emailVerified, set: setEmailVerified },
            ].map(({ label, icon, value, set }) => (
              <button
                key={label}
                onClick={() => editing && set(!value)}
                disabled={!editing}
                className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border font-medium transition-colors ${
                  value
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-500 border-gray-300'
                } ${editing ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}
              >
                {icon}
                {label}
              </button>
            ))}
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Notes</label>
            {editing ? (
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                placeholder="Add any notes about this contact..."
              />
            ) : (
              <p className="text-sm text-gray-700 whitespace-pre-wrap min-h-[40px]">
                {notes || <span className="text-gray-400 italic">No notes</span>}
              </p>
            )}
          </div>

          {/* Quick links (read-only) */}
          {!editing && (email || linkedinUrl || phone) && (
            <div className="flex flex-wrap gap-2">
              {email && (
                <a
                  href={`mailto:${email}`}
                  className="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 border border-blue-200 rounded-full px-3 py-1.5 hover:bg-blue-50"
                >
                  <Mail className="w-3.5 h-3.5" /> {email}
                </a>
              )}
              {linkedinUrl && (
                <a
                  href={linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-xs text-[#0077b5] hover:underline border border-[#0077b5]/30 rounded-full px-3 py-1.5 hover:bg-[#e8f0fb]"
                >
                  <Linkedin className="w-3.5 h-3.5" /> LinkedIn
                </a>
              )}
              {phone && (
                <a
                  href={`tel:${phone}`}
                  className="flex items-center gap-1.5 text-xs text-gray-600 border border-gray-200 rounded-full px-3 py-1.5 hover:bg-gray-50"
                >
                  <Phone className="w-3.5 h-3.5" /> {phone}
                </a>
              )}
            </div>
          )}

          {/* ── Hunter.io Panel ── */}
          <HunterContactPanel
            firstName={hunterFirstName}
            lastName={hunterLastName}
            currentEmail={email || undefined}
            defaultDomain={deriveDomain(fundWebsite)}
            onApplyEmail={async (newEmail) => {
              await updateContact.mutateAsync({ id: contact.id, data: { email: newEmail } });
              setEmail(newEmail);
            }}
            onApplyFields={async (fields) => {
              const data: Record<string, string> = {};
              if (fields.job_title)    data.title        = fields.job_title;
              if (fields.linkedin_url) data.linkedin_url = fields.linkedin_url;
              if (fields.phone)        data.phone        = fields.phone;
              if (Object.keys(data).length) {
                await updateContact.mutateAsync({ id: contact.id, data });
                if (fields.job_title)    setTitle(fields.job_title);
                if (fields.linkedin_url) setLinkedinUrl(fields.linkedin_url);
                if (fields.phone)        setPhone(fields.phone);
              }
            }}
          />

          {/* ── Outreach History ── */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Message History
                {history.length > 0 && (
                  <span className="ml-1 bg-gray-200 text-gray-600 rounded-full px-1.5 text-xs">{history.length}</span>
                )}
              </h3>
            </div>

            {historyLoading ? (
              <div className="space-y-2">
                {[1, 2].map((i) => (
                  <div key={i} className="h-14 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : history.length === 0 ? (
              <div className="text-center py-8 border-2 border-dashed border-gray-200 rounded-lg">
                <Send className="w-6 h-6 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No messages sent yet</p>
                <p className="text-xs text-gray-400 mt-1">Click "Send Message" below to get started</p>
              </div>
            ) : (
              <div className="space-y-2">
                {history.map((log) => (
                  <LogEntry key={log.id} log={log} contactId={contact.id} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Footer ── */}
        <div className="p-4 border-t bg-gray-50 rounded-b-xl">
          <button
            onClick={() => setShowOutreach(true)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 text-sm transition-colors"
          >
            <Send className="w-4 h-4" />
            Send Message
          </button>
        </div>

      </div>
    </div>
  );
}
