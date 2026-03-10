import { useState } from 'react';
import {
  Search, Plus, User, Mail, Phone, Linkedin, Building2,
  Star, Flag, CheckCircle, X, Save, RotateCcw, Trash2, ChevronDown, ChevronUp,
} from 'lucide-react';
import { useVCContacts, useCreateVCContact, useUpdateVCContact, useDeleteVCContact } from '../hooks/useVCContacts';
import { useFunds } from '../hooks/useFunds';
import type { VCContact } from '../types';
import { VCContactDetailModal } from './VCContactDetailModal';

// ── helpers ──────────────────────────────────────────────────────────────────

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('');
}

function formatDate(iso?: string) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
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

          {/* Fund */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Fund *</label>
            <select value={form.fund_id} onChange={(e) => set('fund_id', e.target.value)} className={inp}>
              <option value="">Select a fund…</option>
              {funds.map((f) => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </div>

          {/* Name */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Full Name *</label>
            <input value={form.full_name} onChange={(e) => set('full_name', e.target.value)} className={inp} placeholder="Jane Smith" />
          </div>

          {/* Title + Department */}
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

          {/* Seniority + Timezone */}
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

          {/* Email + Phone */}
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

          {/* LinkedIn */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">LinkedIn URL</label>
            <input value={form.linkedin_url} onChange={(e) => set('linkedin_url', e.target.value)} className={inp} placeholder="https://linkedin.com/in/…" />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Notes</label>
            <textarea value={form.notes} onChange={(e) => set('notes', e.target.value)} rows={3}
              className="text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
              placeholder="Any notes about this contact…" />
          </div>

          {/* Toggles */}
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

// ── Contact card ──────────────────────────────────────────────────────────────

interface CardProps {
  contact: VCContact;
  onEdit: (c: VCContact) => void;
  onOpen: (c: VCContact) => void;
}

function ContactCard({ contact, onEdit, onOpen }: CardProps) {
  const [expanded, setExpanded] = useState(false);
  const deleteContact = useDeleteVCContact();

  return (
    <div
      className={`bg-white border rounded-xl shadow-sm transition-all cursor-pointer hover:shadow-md ${
        contact.is_flagged ? 'border-red-200' : 'border-gray-200'
      }`}
      onClick={() => onOpen(contact)}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 text-indigo-700 font-semibold text-sm">
            {initials(contact.full_name)}
          </div>

          {/* Main info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-gray-900 text-sm">{contact.full_name}</h3>
              {contact.is_primary && (
                <span className="inline-flex items-center gap-1 text-xs bg-yellow-50 text-yellow-700 border border-yellow-200 px-2 py-0.5 rounded-full">
                  <Star className="w-3 h-3" /> Primary
                </span>
              )}
              {contact.email_verified && (
                <span className="inline-flex items-center gap-1 text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">
                  <CheckCircle className="w-3 h-3" /> Verified
                </span>
              )}
              {contact.is_flagged && (
                <span className="inline-flex items-center gap-1 text-xs bg-red-50 text-red-700 border border-red-200 px-2 py-0.5 rounded-full">
                  <Flag className="w-3 h-3" /> Flagged
                </span>
              )}
            </div>
            {contact.title && (
              <p className="text-xs text-gray-500 mt-0.5">{contact.title}{contact.department ? ` · ${contact.department}` : ''}</p>
            )}
            {contact.fund_name && (
              <p className="text-xs text-blue-600 mt-0.5 flex items-center gap-1">
                <Building2 className="w-3 h-3" /> {contact.fund_name}
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => onEdit(contact)}
              className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors text-xs font-medium px-2">
              Edit
            </button>
            <button onClick={() => setExpanded((e) => !e)}
              className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400">
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Quick links */}
        <div className="flex flex-wrap gap-2 mt-3">
          {contact.email && (
            <a href={`mailto:${contact.email}`}
              className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-200 px-2.5 py-1 rounded-full transition-colors">
              <Mail className="w-3 h-3" /> {contact.email}
            </a>
          )}
          {contact.phone && (
            <a href={`tel:${contact.phone}`}
              className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-200 px-2.5 py-1 rounded-full transition-colors">
              <Phone className="w-3 h-3" /> {contact.phone}
            </a>
          )}
          {contact.linkedin_url && (
            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-200 px-2.5 py-1 rounded-full transition-colors">
              <Linkedin className="w-3 h-3" /> LinkedIn
            </a>
          )}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-gray-100 px-4 py-3 space-y-2 bg-gray-50 rounded-b-xl">
          <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
            {contact.seniority_level && (
              <>
                <span className="text-gray-400 font-medium">Seniority</span>
                <span className="text-gray-700 capitalize">{contact.seniority_level}</span>
              </>
            )}
            {contact.timezone && (
              <>
                <span className="text-gray-400 font-medium">Timezone</span>
                <span className="text-gray-700">{contact.timezone}</span>
              </>
            )}
            {contact.last_contacted_at && (
              <>
                <span className="text-gray-400 font-medium">Last contacted</span>
                <span className="text-gray-700">{formatDate(contact.last_contacted_at)}</span>
              </>
            )}
          </div>
          {contact.notes && (
            <p className="text-xs text-gray-600 leading-relaxed bg-white border border-gray-200 rounded-lg px-3 py-2 whitespace-pre-wrap">
              {contact.notes}
            </p>
          )}
          <div className="flex justify-end pt-1">
            <button
              onClick={() => { if (window.confirm(`Delete ${contact.full_name}?`)) deleteContact.mutate(contact.id); }}
              className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded-lg"
            >
              <Trash2 className="w-3 h-3" /> Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main view ─────────────────────────────────────────────────────────────────

export function VCContactsView() {
  const [search, setSearch] = useState('');
  const [fundFilter, setFundFilter] = useState('');
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [primaryOnly, setPrimaryOnly] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editContact, setEditContact] = useState<VCContact | undefined>();
  const [selectedContact, setSelectedContact] = useState<VCContact | null>(null);

  const { data: fundsData } = useFunds();
  const funds = fundsData?.items || [];

  const { data, isLoading } = useVCContacts({
    search: search || undefined,
    fund_id: fundFilter || undefined,
    is_flagged: flaggedOnly ? true : undefined,
    is_primary: primaryOnly ? true : undefined,
  });
  const contacts = data?.items || [];

  const openCreate = () => { setEditContact(undefined); setShowModal(true); };
  const openEdit = (c: VCContact) => { setEditContact(c); setShowModal(true); };
  const openDetail = (c: VCContact) => setSelectedContact(c);

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* ── Toolbar ── */}
      <div className="flex flex-wrap gap-3 mb-6 items-center">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search contacts…"
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Fund filter */}
        <select
          value={fundFilter}
          onChange={(e) => setFundFilter(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none bg-white"
        >
          <option value="">All Funds</option>
          {funds.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
        </select>

        {/* Toggle pills */}
        <button
          onClick={() => setPrimaryOnly((v) => !v)}
          className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border transition-colors ${
            primaryOnly ? 'bg-yellow-50 border-yellow-300 text-yellow-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          <Star className="w-3.5 h-3.5" /> Primary only
        </button>
        <button
          onClick={() => setFlaggedOnly((v) => !v)}
          className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border transition-colors ${
            flaggedOnly ? 'bg-red-50 border-red-300 text-red-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          <Flag className="w-3.5 h-3.5" /> Flagged
        </button>

        <div className="ml-auto">
          <button
            onClick={openCreate}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4" /> New Contact
          </button>
        </div>
      </div>

      {/* ── Count ── */}
      <p className="text-xs text-gray-500 mb-4">
        {isLoading ? 'Loading…' : `${data?.total ?? contacts.length} contact${contacts.length !== 1 ? 's' : ''}`}
      </p>

      {/* ── Grid ── */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24 text-gray-400">
          <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mr-3" />
          Loading contacts…
        </div>
      ) : contacts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-gray-400">
          <User className="w-12 h-12 mb-3 opacity-30" />
          <p className="font-medium text-gray-500">No contacts found</p>
          <p className="text-sm mt-1">
            {search || fundFilter || flaggedOnly || primaryOnly
              ? 'Try adjusting your filters.'
              : 'Create a contact to get started.'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {contacts.map((c) => (
            <ContactCard key={c.id} contact={c} onEdit={openEdit} onOpen={openDetail} />
          ))}
        </div>
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
          fundWebsite={funds.find((f) => f.id === selectedContact.fund_id)?.website_url || undefined}
          onClose={() => setSelectedContact(null)}
        />
      )}
    </div>
  );
}
