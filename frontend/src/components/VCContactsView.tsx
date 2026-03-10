import { useState } from 'react';
import {
  Search, Plus, User, Mail, Phone, Linkedin, Building2,
  Star, Flag, CheckCircle, X, Save, Globe, Calendar,
  Filter, Send, ListChecks, ClipboardCheck,
} from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useVCContacts, useCreateVCContact, useUpdateVCContact, useDeleteVCContact } from '../hooks/useVCContacts';
import { useFunds } from '../hooks/useFunds';
import type { VCContact } from '../types';
import { VCContactDetailModal } from './VCContactDetailModal';
import { BulkDeleteBar } from './BulkDeleteBar';
import { AddToKanbanModal, type AddToKanbanSource } from './AddToKanbanModal';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

// ── helpers ───────────────────────────────────────────────────────────────────

type ContactedQuick = 'all' | 'never' | 'today' | '7d' | '30d' | 'custom';

function toISODate(d: Date): string {
  return d.toISOString().split('T')[0];
}

function formatLastContacted(dateStr?: string) {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return date.toLocaleDateString();
}

// ── Edit / Create modal ───────────────────────────────────────────────────────

interface ContactModalProps {
  contact?: VCContact;
  defaultFundId?: string;
  onClose: () => void;
}

function ContactModal({ contact, defaultFundId, onClose }: ContactModalProps) {
  const { data: fundsData } = useFunds();
  const funds = fundsData?.items || [];
  const createContact = useCreateVCContact();
  const updateContact = useUpdateVCContact();

  const [form, setForm] = useState({
    fund_id: contact?.fund_id || defaultFundId || '',
    full_name: contact?.full_name || '',
    title: contact?.title || '',
    email: contact?.email || '',
    phone: contact?.phone || '',
    linkedin_url: contact?.linkedin_url || '',
    department: contact?.department || '',
    seniority_level: contact?.seniority_level || '',
    is_primary: contact?.is_primary ?? false,
    email_verified: contact?.email_verified ?? false,
    timezone: contact?.timezone || '',
    notes: contact?.notes || '',
  });

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const handleSave = async () => {
    if (!form.fund_id) { setError('Please select a fund.'); return; }
    if (!form.full_name.trim()) { setError('Name is required.'); return; }
    setSaving(true);
    try {
      if (contact) {
        await updateContact.mutateAsync({ id: contact.id, data: form });
      } else {
        await createContact.mutateAsync({ ...form, fund_id: form.fund_id, full_name: form.full_name });
      }
      onClose();
    } catch (e: any) {
      setError(e?.message || 'Failed to save.');
    } finally {
      setSaving(false);
    }
  };

  const inp = 'text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-lg w-full max-h-[90vh] flex flex-col shadow-xl">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            {contact ? 'Edit Contact' : 'New VC Contact'}
          </h2>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-5 space-y-4">
          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
          )}

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Fund *</label>
            <select value={form.fund_id} onChange={(e) => set('fund_id', e.target.value)} className={inp}>
              <option value="">Select a fund…</option>
              {funds.map((f) => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Full Name *</label>
            <input value={form.full_name} onChange={(e) => set('full_name', e.target.value)} className={inp} placeholder="Jane Smith" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Job Title</label>
              <input value={form.title} onChange={(e) => set('title', e.target.value)} className={inp} placeholder="Partner" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Department</label>
              <input value={form.department} onChange={(e) => set('department', e.target.value)} className={inp} placeholder="Investments" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Seniority</label>
              <select value={form.seniority_level} onChange={(e) => set('seniority_level', e.target.value)} className={inp}>
                <option value="">—</option>
                <option value="executive">Executive</option>
                <option value="senior">Senior</option>
                <option value="mid">Mid</option>
                <option value="junior">Junior</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Timezone</label>
              <input value={form.timezone} onChange={(e) => set('timezone', e.target.value)} className={inp} placeholder="America/New_York" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
              <input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} className={inp} placeholder="jane@fund.com" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Phone</label>
              <input value={form.phone} onChange={(e) => set('phone', e.target.value)} className={inp} placeholder="+1 555 000 0000" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">LinkedIn URL</label>
            <input value={form.linkedin_url} onChange={(e) => set('linkedin_url', e.target.value)} className={inp} placeholder="https://linkedin.com/in/…" />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Notes</label>
            <textarea value={form.notes} onChange={(e) => set('notes', e.target.value)} rows={3}
              className="text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
              placeholder="Any notes about this contact…" />
          </div>

          <div className="flex gap-6">
            {[
              { key: 'is_primary', label: 'Primary contact' },
              { key: 'email_verified', label: 'Email verified' },
            ].map(({ key, label }) => (
              <label key={key} className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={(form as any)[key]} onChange={(e) => set(key, e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                <span className="text-sm text-gray-700">{label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-2 p-5 border-t">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50">
            <Save className="w-4 h-4" />
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Contact card (studio-style) ───────────────────────────────────────────────

interface CardProps {
  contact: VCContact;
  fundWebsite?: string;
  onOpen: (c: VCContact) => void;
  onAddToKanban: (source: AddToKanbanSource) => void;
  selected?: boolean;
  onToggle?: () => void;
}

function ContactCard({ contact, fundWebsite, onOpen, onAddToKanban, selected, onToggle }: CardProps) {
  const updateContact = useUpdateVCContact();
  const lastContacted = formatLastContacted(contact.last_contacted_at);

  const channelIcon = (contact as any).contact_preference === 'linkedin'
    ? <Linkedin className="w-3 h-3" />
    : (contact as any).contact_preference === 'email'
    ? <Mail className="w-3 h-3" />
    : null;

  return (
    <div
      onClick={onToggle ?? (() => onOpen(contact))}
      className={`rounded-lg shadow-sm border p-4 hover:shadow-md transition-all cursor-pointer flex flex-col relative ${
        selected
          ? 'ring-2 ring-blue-500 border-blue-400 bg-blue-50'
          : contact.is_flagged
          ? 'bg-red-50 border-red-300 hover:border-red-400'
          : 'bg-white border-gray-200 hover:border-blue-300'
      }`}
    >
      {/* Select checkbox */}
      {onToggle !== undefined && (
        <div className="absolute top-2 left-2 z-10">
          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
            selected ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-400'
          }`}>
            {selected && <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${contact.is_flagged ? 'bg-red-100' : 'bg-blue-100'}`}>
            <span className={`font-semibold text-lg ${contact.is_flagged ? 'text-red-600' : 'text-blue-600'}`}>
              {contact.full_name?.[0]?.toUpperCase() || '?'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{contact.full_name}</h3>
            <p className="text-sm text-gray-500">{contact.title || 'Unknown Role'}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {/* Flag toggle */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              updateContact.mutate({ id: contact.id, data: { is_flagged: !contact.is_flagged } });
            }}
            title={contact.is_flagged ? 'Remove flag' : 'Flag as bad data'}
            className={`p-1 rounded transition-colors ${
              contact.is_flagged ? 'text-red-500 hover:text-red-700' : 'text-gray-300 hover:text-red-400'
            }`}
          >
            <Flag className="w-4 h-4" fill={contact.is_flagged ? 'currentColor' : 'none'} />
          </button>
          {contact.is_primary && (
            <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
              <Star className="w-3 h-3" /> Primary
            </span>
          )}
          {lastContacted && (
            <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
              {channelIcon}
              {lastContacted}
            </span>
          )}
        </div>
      </div>

      {/* Fund section */}
      {contact.fund_name && (
        <div className="mb-3 p-2 bg-gray-50 rounded">
          <p className="text-sm font-medium text-gray-700">{contact.fund_name}</p>
          {fundWebsite && (
            <a
              href={fundWebsite}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 text-xs text-blue-500 hover:text-blue-700 mt-1 truncate"
            >
              <Globe className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{fundWebsite.replace(/^https?:\/\//, '')}</span>
            </a>
          )}
        </div>
      )}

      {/* Contact info */}
      <div className="space-y-2 flex-1">
        {contact.email && (
          <a
            href={`mailto:${contact.email}`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
          >
            <Mail className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{contact.email}</span>
            {contact.email_verified && (
              <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
            )}
          </a>
        )}
        {contact.linkedin_url && (
          <a
            href={contact.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
          >
            <Linkedin className="w-4 h-4 flex-shrink-0" />
            LinkedIn Profile
          </a>
        )}
        {contact.phone && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Phone className="w-4 h-4 flex-shrink-0" />
            {contact.phone}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between gap-2">
        <span className="text-xs text-gray-500 truncate">{contact.department || 'Unknown Dept'}</span>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAddToKanban({
                type: 'contact',
                id: contact.id,
                title: contact.full_name,
                data: {
                  full_name: contact.full_name,
                  job_title: contact.title,
                  email: contact.email,
                  linkedin_url: contact.linkedin_url,
                  company_id: contact.fund_id,
                  studio_name: contact.fund_name,
                  is_decision_maker: contact.is_primary,
                },
              });
            }}
            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-2 py-1.5 rounded-lg transition-colors"
            title="Add to Tasks board"
          >
            <ClipboardCheck className="w-3 h-3" />
            Tasks
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onOpen(contact); }}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
          >
            <Send className="w-3 h-3" />
            Outreach
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main view ─────────────────────────────────────────────────────────────────

export function VCContactsView() {
  // ── filter state ──
  const [search, setSearch] = useState('');
  const [fundFilter, setFundFilter] = useState('');
  const [primaryOnly, setPrimaryOnly] = useState(false);
  const [flaggedOnly, setFlaggedOnly] = useState(false);

  // Last-contacted (client-side)
  const [contactedQuick, setContactedQuick] = useState<ContactedQuick>('all');
  const [customAfter, setCustomAfter] = useState('');
  const [customOn, setCustomOn] = useState('');

  // Date added + sort
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  // ── bulk select state ──
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleting, setDeleting] = useState(false);
  const queryClient = useQueryClient();

  // ── modal state ──
  const [showModal, setShowModal] = useState(false);
  const [editContact, setEditContact] = useState<VCContact | undefined>();
  const [selectedContact, setSelectedContact] = useState<VCContact | null>(null);
  const [kanbanSource, setKanbanSource] = useState<AddToKanbanSource | null>(null);

  // ── data ──
  const { data: fundsData } = useFunds();
  const funds = fundsData?.items || [];
  const fundMap = new Map(funds.map(f => [f.id, f]));

  const { data, isLoading } = useVCContacts({
    search: search || undefined,
    fund_id: fundFilter || undefined,
    is_flagged: flaggedOnly ? true : undefined,
    is_primary: primaryOnly ? true : undefined,
  });

  const rawContacts: VCContact[] = data?.items || [];

  // Apply last-contacted filter client-side
  const afterContactedFilter = (() => {
    if (contactedQuick === 'all') return rawContacts;
    const today = new Date();
    return rawContacts.filter(c => {
      if (contactedQuick === 'never') return !c.last_contacted_at;
      if (!c.last_contacted_at) return false;
      if (contactedQuick === 'today') return toISODate(new Date(c.last_contacted_at)) === toISODate(today);
      if (contactedQuick === '7d') { const d = new Date(today); d.setDate(d.getDate() - 7); return new Date(c.last_contacted_at) >= d; }
      if (contactedQuick === '30d') { const d = new Date(today); d.setDate(d.getDate() - 30); return new Date(c.last_contacted_at) >= d; }
      if (contactedQuick === 'custom') {
        if (customOn) return toISODate(new Date(c.last_contacted_at)) === customOn;
        if (customAfter) return new Date(c.last_contacted_at) >= new Date(customAfter);
      }
      return true;
    });
  })();

  // Apply date-added filter + sort
  const contacts = (() => {
    const fromMs = dateFrom ? new Date(dateFrom).getTime() : 0;
    const toMs   = dateTo   ? new Date(dateTo + 'T23:59:59').getTime() : Infinity;
    return [...afterContactedFilter]
      .filter(c => {
        if (!c.created_at) return true;
        const t = new Date(c.created_at).getTime();
        return t >= fromMs && t <= toMs;
      })
      .sort((a, b) => {
        const diff = new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime();
        return sortOrder === 'desc' ? diff : -diff;
      });
  })();

  // ── helpers ──
  const toggleSelect = (id: string) => setSelectedIds(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Permanently delete ${selectedIds.size} VC contact(s)? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await fetch(`${API_BASE}/vc/contacts/bulk-delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [...selectedIds] }),
      });
      setSelectedIds(new Set());
      setSelectMode(false);
      queryClient.invalidateQueries({ queryKey: ['vcContacts'] });
    } finally {
      setDeleting(false);
    }
  };

  const handleContactedQuick = (q: ContactedQuick) => {
    setContactedQuick(q);
    setCustomAfter('');
    setCustomOn('');
  };

  const clearContactedFilter = () => {
    setContactedQuick('all');
    setCustomAfter('');
    setCustomOn('');
  };

  return (
    <div className="space-y-6">
      {/* ── Add to Kanban modal ── */}
      {kanbanSource && (
        <AddToKanbanModal source={kanbanSource} onClose={() => setKanbanSource(null)} />
      )}

      {/* ── Filter panel ── */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">

        {/* Row 1: Search + Fund + Primary filter */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search contacts by name, title, or email…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-gray-400" />
            <select
              value={fundFilter}
              onChange={(e) => setFundFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 min-w-[200px]"
            >
              <option value="">All Funds</option>
              {funds.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={primaryOnly ? 'primary' : ''}
              onChange={(e) => setPrimaryOnly(e.target.value === 'primary')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Contacts</option>
              <option value="primary">Primary Contacts Only</option>
            </select>
          </div>
        </div>

        {/* Row 2: Last contacted filter */}
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2 flex-wrap">
            <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide mr-1">Last Contacted:</span>

            {(['all', 'never', 'today', '7d', '30d', 'custom'] as ContactedQuick[]).map((q) => (
              <button
                key={q}
                onClick={() => handleContactedQuick(q)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium border transition-colors ${
                  contactedQuick === q
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400 hover:text-blue-600'
                }`}
              >
                {{ all: 'Any time', never: 'Never', today: 'Today', '7d': 'Last 7 days', '30d': 'Last 30 days', custom: 'Custom…' }[q]}
              </button>
            ))}

            {contactedQuick === 'custom' && (
              <div className="flex items-center gap-2 ml-1 flex-wrap">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-gray-500">On:</span>
                  <input
                    type="date"
                    value={customOn}
                    onChange={(e) => { setCustomOn(e.target.value); setCustomAfter(''); }}
                    className="text-xs px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <span className="text-xs text-gray-400">or</span>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-gray-500">After:</span>
                  <input
                    type="date"
                    value={customAfter}
                    onChange={(e) => { setCustomAfter(e.target.value); setCustomOn(''); }}
                    className="text-xs px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            )}

            {contactedQuick !== 'all' && (
              <button
                onClick={clearContactedFilter}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 ml-1"
              >
                <X className="w-3.5 h-3.5" /> Clear
              </button>
            )}
          </div>
        </div>

        {/* Row 3: Data quality + select + new contact */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-2 flex-wrap">
          <Flag className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide mr-1">Data Quality:</span>
          <button
            onClick={() => setFlaggedOnly(!flaggedOnly)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium border transition-colors flex items-center gap-1.5 ${
              flaggedOnly
                ? 'bg-red-500 text-white border-red-500'
                : 'bg-white text-gray-600 border-gray-300 hover:border-red-400 hover:text-red-600'
            }`}
          >
            <Flag className="w-3 h-3" />
            {flaggedOnly ? 'Showing Flagged Only' : 'Show Flagged Only'}
          </button>
          {flaggedOnly && (
            <button onClick={() => setFlaggedOnly(false)} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600">
              <X className="w-3.5 h-3.5" /> Clear
            </button>
          )}
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={() => { setSelectMode(v => !v); setSelectedIds(new Set()); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                selectMode ? 'bg-blue-50 border-blue-400 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <ListChecks className="w-3.5 h-3.5" />
              {selectMode ? 'Exit select' : 'Select'}
            </button>
            <button
              onClick={() => { setEditContact(undefined); setShowModal(true); }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> New Contact
            </button>
          </div>
        </div>

        {/* Row 4: Date Added + sort */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-3 flex-wrap">
          <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Date Added:</span>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-500">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="text-xs px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-500">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="text-xs px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          {(dateFrom || dateTo) && (
            <button onClick={() => { setDateFrom(''); setDateTo(''); }} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
              <X className="w-3 h-3" /> Clear dates
            </button>
          )}
          <div className="ml-auto flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
            <button
              onClick={() => setSortOrder('desc')}
              className={`text-xs px-2.5 py-1 rounded-md transition-colors font-medium ${sortOrder === 'desc' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Newest first
            </button>
            <button
              onClick={() => setSortOrder('asc')}
              className={`text-xs px-2.5 py-1 rounded-md transition-colors font-medium ${sortOrder === 'asc' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Oldest first
            </button>
          </div>
        </div>

        {/* Row 5: Stats bar */}
        <div className="flex gap-6 mt-4 pt-4 border-t border-gray-100 text-sm">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-blue-500" />
            <span className="font-medium">{contacts.length}</span>
            <span className="text-gray-500">contacts</span>
          </div>
          <div className="flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-500" />
            <span className="font-medium">{contacts.filter(c => c.is_primary).length}</span>
            <span className="text-gray-500">primary</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="font-medium">{contacts.filter(c => c.email_verified).length}</span>
            <span className="text-gray-500">verified emails</span>
          </div>
          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-4 h-4 text-purple-500" />
            <span className="font-medium">{contacts.filter(c => c.last_contacted_at).length}</span>
            <span className="text-gray-500">contacted</span>
          </div>
          <div className="flex items-center gap-2">
            <Flag className="w-4 h-4 text-red-400" />
            <span className="font-medium">{contacts.filter(c => c.is_flagged).length}</span>
            <span className="text-gray-500">flagged</span>
          </div>
        </div>
      </div>

      {/* ── Grid ── */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
              <div className="h-6 bg-gray-200 rounded mb-2" />
              <div className="h-4 bg-gray-200 rounded mb-2 w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : contacts.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No contacts found</h3>
          <p className="text-gray-500">
            {search || fundFilter || flaggedOnly || primaryOnly
              ? 'Try adjusting your filters.'
              : 'Create a contact to get started.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map((c) => (
            <ContactCard
              key={c.id}
              contact={c}
              fundWebsite={fundMap.get(c.fund_id)?.website_url || undefined}
              onOpen={(contact) => setSelectedContact(contact)}
              onAddToKanban={(src) => setKanbanSource(src)}
              selected={selectMode ? selectedIds.has(c.id) : undefined}
              onToggle={selectMode ? () => toggleSelect(c.id) : undefined}
            />
          ))}
        </div>
      )}

      {selectMode && selectedIds.size > 0 && (
        <BulkDeleteBar
          count={selectedIds.size}
          total={contacts.length}
          onSelectAll={() => setSelectedIds(new Set(contacts.map(c => c.id)))}
          onClearAll={() => { setSelectedIds(new Set()); setSelectMode(false); }}
          onDelete={handleBulkDelete}
          deleting={deleting}
        />
      )}

      {/* ── Create/Edit Modal ── */}
      {showModal && (
        <ContactModal
          contact={editContact}
          defaultFundId={fundFilter}
          onClose={() => setShowModal(false)}
        />
      )}

      {/* ── Detail Modal ── */}
      {selectedContact && (
        <VCContactDetailModal
          contact={selectedContact}
          fundName={selectedContact.fund_name}
          fundWebsite={fundMap.get(selectedContact.fund_id)?.website_url || undefined}
          onClose={() => setSelectedContact(null)}
        />
      )}
    </div>
  );
}
