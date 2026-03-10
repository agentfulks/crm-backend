import { useState } from 'react';
import {
  X, Globe, Linkedin, Twitter, Mail, DollarSign, MapPin, Users,
  ExternalLink, Save, RotateCcw, Edit3, Plus, Phone, Star, CheckCircle, ChevronDown, ChevronUp, Trash2, Flag,
} from 'lucide-react';
import type { Fund, FundStatus, Priority, VCContact } from '../types';
import { useUpdateFund } from '../hooks/useFunds';
import { useContactsByFund, useCreateVCContact, useUpdateVCContact, useDeleteVCContact } from '../hooks/useVCContacts';
import { VCContactDetailModal } from './VCContactDetailModal';
import { HunterStudioPanel } from './HunterStudioPanel';
import { deriveDomain } from '../lib/hunterApi';

const STATUS_OPTIONS: FundStatus[] = ['NEW', 'RESEARCHING', 'READY', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'];

const STATUS_COLORS: Record<FundStatus, string> = {
  NEW:         'bg-gray-100 text-gray-700',
  RESEARCHING: 'bg-blue-100 text-blue-700',
  READY:       'bg-teal-100 text-teal-700',
  APPROVED:    'bg-green-100 text-green-800',
  SENT:        'bg-indigo-100 text-indigo-700',
  FOLLOW_UP:   'bg-purple-100 text-purple-700',
  CLOSED:      'bg-red-100 text-red-700',
};

function formatCheckSize(min?: number, max?: number): string | null {
  if (!min) return null;
  const fmt = (n: number) =>
    n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M` : `$${(n / 1_000).toFixed(0)}K`;
  if (max && max !== min) return `${fmt(min)} – ${fmt(max)}`;
  return fmt(min);
}

// ── Inline contact add/edit form ─────────────────────────────────────────────

interface ContactRowProps {
  contact: VCContact;
  onDelete: (id: string) => void;
  onOpen: (c: VCContact) => void;
}

function ContactRow({ contact, onDelete, onOpen }: ContactRowProps) {
  const [expanded, setExpanded] = useState(false);
  const updateContact = useUpdateVCContact();

  const toggle = (field: 'is_primary' | 'email_verified') =>
    updateContact.mutate({ id: contact.id, data: { [field]: !contact[field] } });

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="flex items-center gap-3 px-3 py-2.5">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-semibold text-xs flex-shrink-0">
          {contact.full_name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{contact.full_name}</p>
          {contact.title && <p className="text-xs text-gray-500 truncate">{contact.title}</p>}
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {contact.email && (
            <a href={`mailto:${contact.email}`} title={contact.email}
              className="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-blue-600">
              <Mail className="w-3.5 h-3.5" />
            </a>
          )}
          {contact.phone && (
            <a href={`tel:${contact.phone}`} title={contact.phone}
              className="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-blue-600">
              <Phone className="w-3.5 h-3.5" />
            </a>
          )}
          {contact.linkedin_url && (
            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer"
              className="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-blue-600">
              <Linkedin className="w-3.5 h-3.5" />
            </a>
          )}
          <button onClick={() => toggle('is_primary')} title="Toggle primary"
            className={`p-1.5 rounded ${contact.is_primary ? 'text-yellow-500' : 'text-gray-300 hover:text-yellow-400'}`}>
            <Star className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => toggle('email_verified')} title="Toggle verified"
            className={`p-1.5 rounded ${contact.email_verified ? 'text-green-500' : 'text-gray-300 hover:text-green-400'}`}>
            <CheckCircle className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => onOpen(contact)}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2 py-1 hover:bg-blue-50 rounded transition-colors">
            Open
          </button>
          <button onClick={() => setExpanded((e) => !e)}
            className="p-1.5 hover:bg-gray-100 rounded text-gray-400">
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>
      {expanded && (
        <div className="border-t border-gray-100 px-3 py-2.5 bg-gray-50 flex items-center justify-between gap-3">
          <div className="text-xs text-gray-500 space-y-0.5">
            {contact.email && <p>📧 {contact.email}</p>}
            {contact.phone && <p>📞 {contact.phone}</p>}
            {contact.department && <p>🏢 {contact.department}{contact.seniority_level ? ` · ${contact.seniority_level}` : ''}</p>}
            {contact.notes && <p className="text-gray-600 italic">"{contact.notes}"</p>}
          </div>
          <button onClick={() => { if (window.confirm(`Delete ${contact.full_name}?`)) onDelete(contact.id); }}
            className="flex items-center gap-1 text-xs text-red-400 hover:text-red-600 px-2 py-1 hover:bg-red-50 rounded">
            <Trash2 className="w-3 h-3" /> Delete
          </button>
        </div>
      )}
    </div>
  );
}

interface AddContactFormProps {
  fundId: string;
  onDone: () => void;
}

function AddContactForm({ fundId, onDone }: AddContactFormProps) {
  const createContact = useCreateVCContact();
  const [form, setForm] = useState({ full_name: '', title: '', email: '', phone: '', linkedin_url: '' });
  const [saving, setSaving] = useState(false);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));
  const inp = 'text-xs border border-gray-300 rounded px-2 py-1.5 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none w-full';

  const handleSave = async () => {
    if (!form.full_name.trim()) return;
    setSaving(true);
    try {
      await createContact.mutateAsync({ fund_id: fundId, full_name: form.full_name, ...form });
      onDone();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="border border-blue-200 rounded-lg p-3 bg-blue-50 space-y-2">
      <div className="grid grid-cols-2 gap-2">
        <input placeholder="Full name *" value={form.full_name} onChange={(e) => set('full_name', e.target.value)} className={inp} />
        <input placeholder="Job title" value={form.title} onChange={(e) => set('title', e.target.value)} className={inp} />
        <input placeholder="Email" value={form.email} onChange={(e) => set('email', e.target.value)} className={inp} />
        <input placeholder="Phone" value={form.phone} onChange={(e) => set('phone', e.target.value)} className={inp} />
      </div>
      <input placeholder="LinkedIn URL" value={form.linkedin_url} onChange={(e) => set('linkedin_url', e.target.value)} className={inp} />
      <div className="flex justify-end gap-2">
        <button onClick={onDone} className="text-xs text-gray-500 hover:text-gray-700 px-3 py-1.5 border border-gray-300 rounded bg-white">Cancel</button>
        <button onClick={handleSave} disabled={saving || !form.full_name.trim()}
          className="text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-3 py-1.5 rounded">
          {saving ? 'Adding…' : 'Add'}
        </button>
      </div>
    </div>
  );
}

// ── Main modal ────────────────────────────────────────────────────────────────

interface Props {
  fund: Fund;
  onClose: () => void;
}

export function FundDetailModal({ fund, onClose }: Props) {
  const updateFund = useUpdateFund();
  const [editing, setEditing] = useState(false);
  const [showAddContact, setShowAddContact] = useState(false);
  const [selectedContact, setSelectedContact] = useState<VCContact | null>(null);
  const isFlagged = fund.is_flagged ?? false;

  const { data: fundContacts = [], refetch: refetchContacts } = useContactsByFund(fund.id);
  const deleteContact = useDeleteVCContact();
  const createContact = useCreateVCContact();
  const [draft, setDraft] = useState({
    name: fund.name || '',
    firm_type: fund.firm_type || '',
    status: fund.status,
    priority: fund.priority,
    hq_city: fund.hq_city || '',
    hq_region: fund.hq_region || '',
    hq_country: fund.hq_country || '',
    website_url: fund.website_url || '',
    linkedin_url: fund.linkedin_url || '',
    twitter_url: fund.twitter_url || '',
    contact_email: fund.contact_email || '',
    overview: fund.overview || '',
    funding_requirements: fund.funding_requirements || '',
    check_size_min: fund.check_size_min != null ? String(fund.check_size_min) : '',
    check_size_max: fund.check_size_max != null ? String(fund.check_size_max) : '',
  });

  const checkSize = formatCheckSize(fund.check_size_min, fund.check_size_max);

  const handleSave = async () => {
    await updateFund.mutateAsync({
      id: fund.id,
      data: {
        name: draft.name,
        firm_type: draft.firm_type || undefined,
        status: draft.status,
        priority: draft.priority,
        hq_city: draft.hq_city || undefined,
        hq_region: draft.hq_region || undefined,
        hq_country: draft.hq_country || undefined,
        website_url: draft.website_url || undefined,
        linkedin_url: draft.linkedin_url || undefined,
        twitter_url: draft.twitter_url || undefined,
        contact_email: draft.contact_email || undefined,
        overview: draft.overview || undefined,
        funding_requirements: draft.funding_requirements || undefined,
        check_size_min: draft.check_size_min ? Number(draft.check_size_min) : undefined,
        check_size_max: draft.check_size_max ? Number(draft.check_size_max) : undefined,
      },
    });
    setEditing(false);
  };

  const handleDiscard = () => {
    setDraft({
      name: fund.name || '',
      firm_type: fund.firm_type || '',
      status: fund.status,
      priority: fund.priority,
      hq_city: fund.hq_city || '',
      hq_region: fund.hq_region || '',
      hq_country: fund.hq_country || '',
      website_url: fund.website_url || '',
      linkedin_url: fund.linkedin_url || '',
      twitter_url: fund.twitter_url || '',
      contact_email: fund.contact_email || '',
      overview: fund.overview || '',
      funding_requirements: fund.funding_requirements || '',
      check_size_min: fund.check_size_min != null ? String(fund.check_size_min) : '',
      check_size_max: fund.check_size_max != null ? String(fund.check_size_max) : '',
    });
    setEditing(false);
  };

  const inp = 'text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500';

  return (
    <>
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-xl">

        {/* ── Header ── */}
        <div className={`flex items-start justify-between p-5 border-b rounded-t-xl ${isFlagged ? 'bg-red-50' : ''}`}>
          <div className="flex items-center gap-3 min-w-0">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${isFlagged ? 'bg-red-100' : 'bg-blue-50'}`}>
              <Users className={`w-6 h-6 ${isFlagged ? 'text-red-500' : 'text-blue-500'}`} />
            </div>
            <div className="min-w-0 flex-1">
              {editing ? (
                <input
                  value={draft.name}
                  onChange={(e) => setDraft(d => ({ ...d, name: e.target.value }))}
                  className="text-lg font-semibold text-gray-900 border-b border-gray-300 focus:border-blue-500 outline-none w-full"
                />
              ) : (
                <h2 className="text-lg font-semibold text-gray-900 truncate">{fund.name}</h2>
              )}
              {editing ? (
                <input
                  value={draft.firm_type}
                  onChange={e => setDraft(d => ({ ...d, firm_type: e.target.value }))}
                  className="text-sm text-gray-500 border-b border-gray-200 focus:border-blue-400 outline-none w-full mt-0.5"
                  placeholder="Firm type"
                />
              ) : (
                <p className="text-sm text-gray-500 mt-0.5">{fund.firm_type || ''}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0 ml-3">
            {/* Flag */}
            <button
              onClick={() => updateFund.mutate({ id: fund.id, data: { is_flagged: !isFlagged } })}
              title={isFlagged ? 'Remove flag' : 'Flag as bad data'}
              className={`flex items-center gap-1.5 text-sm px-2.5 py-1.5 rounded-lg border transition-colors ${
                isFlagged
                  ? 'bg-red-50 border-red-300 text-red-600 hover:bg-red-100'
                  : 'border-gray-300 text-gray-400 hover:border-red-400 hover:text-red-500 hover:bg-red-50'
              }`}
            >
              <Flag className="w-3.5 h-3.5" fill={isFlagged ? 'currentColor' : 'none'} />
              {isFlagged ? 'Flagged' : 'Flag'}
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
                  disabled={updateFund.isPending}
                  className="flex items-center gap-1 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  {updateFund.isPending ? 'Saving…' : 'Save'}
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

        {/* ── Body ── */}
        <div className="flex-1 overflow-auto p-5 space-y-5">

          {/* Status + Priority + Score */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Status</p>
              {editing ? (
                <select
                  value={draft.status}
                  onChange={e => setDraft(d => ({ ...d, status: e.target.value as FundStatus }))}
                  className={inp}
                >
                  {STATUS_OPTIONS.map(s => (
                    <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                  ))}
                </select>
              ) : (
                <span className={`inline-block text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[fund.status]}`}>
                  {fund.status.replace(/_/g, ' ')}
                </span>
              )}
            </div>

            <div>
              <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Priority</p>
              {editing ? (
                <select
                  value={draft.priority}
                  onChange={e => setDraft(d => ({ ...d, priority: e.target.value as Priority }))}
                  className={inp}
                >
                  {['A', 'B', 'C'].map(p => <option key={p} value={p}>Priority {p}</option>)}
                </select>
              ) : (
                <span className={`inline-block text-xs font-bold px-2.5 py-1 rounded ${
                  fund.priority === 'A' ? 'bg-red-500 text-white' :
                  fund.priority === 'B' ? 'bg-yellow-500 text-white' : 'bg-gray-400 text-white'
                }`}>
                  Priority {fund.priority}
                </span>
              )}
            </div>

            {fund.score != null && (
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Score</p>
                <p className="text-sm font-semibold text-gray-700">{fund.score}</p>
              </div>
            )}
          </div>

          {/* Location + Check size */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Headquarters</p>
              {editing ? (
                <div className="flex gap-1.5">
                  <input placeholder="City" value={draft.hq_city}
                    onChange={e => setDraft(d => ({ ...d, hq_city: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 flex-1 focus:ring-2 focus:ring-blue-500" />
                  <input placeholder="Country" value={draft.hq_country}
                    onChange={e => setDraft(d => ({ ...d, hq_country: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-20 focus:ring-2 focus:ring-blue-500" />
                </div>
              ) : (
                <p className="text-sm text-gray-700 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                  {[fund.hq_city, fund.hq_region, fund.hq_country].filter(Boolean).join(', ') || '—'}
                </p>
              )}
            </div>

            <div>
              <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Check Size</p>
              {editing ? (
                <div className="flex gap-1.5 items-center">
                  <input type="number" placeholder="Min" value={draft.check_size_min}
                    onChange={e => setDraft(d => ({ ...d, check_size_min: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 flex-1 focus:ring-2 focus:ring-blue-500" />
                  <span className="text-gray-400 text-xs">–</span>
                  <input type="number" placeholder="Max" value={draft.check_size_max}
                    onChange={e => setDraft(d => ({ ...d, check_size_max: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 flex-1 focus:ring-2 focus:ring-blue-500" />
                </div>
              ) : (
                <p className="text-sm text-gray-700 flex items-center gap-1">
                  <DollarSign className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                  {checkSize || '—'}
                </p>
              )}
            </div>
          </div>

          {/* Stage focus */}
          {fund.stage_focus?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">Investment Stages</p>
              <div className="flex flex-wrap gap-2">
                {fund.stage_focus.map(s => (
                  <span key={s} className="text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Links */}
          <div className="space-y-3">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Links & Contact</p>

            {/* Website */}
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Website</p>
              {editing ? (
                <input type="url" value={draft.website_url}
                  onChange={e => setDraft(d => ({ ...d, website_url: e.target.value }))}
                  className={inp} placeholder="https://" />
              ) : fund.website_url ? (
                <a href={fund.website_url} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                  <Globe className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{fund.website_url.replace(/^https?:\/\//, '')}</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
              ) : <p className="text-sm text-gray-400 italic">—</p>}
            </div>

            {/* LinkedIn */}
            <div>
              <p className="text-xs text-gray-400 mb-0.5">LinkedIn</p>
              {editing ? (
                <input type="url" value={draft.linkedin_url}
                  onChange={e => setDraft(d => ({ ...d, linkedin_url: e.target.value }))}
                  className={inp} placeholder="https://linkedin.com/company/…" />
              ) : fund.linkedin_url ? (
                <a href={fund.linkedin_url} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                  <Linkedin className="w-3.5 h-3.5 flex-shrink-0" />
                  Company Page <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
              ) : <p className="text-sm text-gray-400 italic">—</p>}
            </div>

            {/* Twitter */}
            {(fund.twitter_url || editing) && (
              <div>
                <p className="text-xs text-gray-400 mb-0.5">Twitter / X</p>
                {editing ? (
                  <input type="url" value={draft.twitter_url}
                    onChange={e => setDraft(d => ({ ...d, twitter_url: e.target.value }))}
                    className={inp} placeholder="https://twitter.com/…" />
                ) : fund.twitter_url ? (
                  <a href={fund.twitter_url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                    <Twitter className="w-3.5 h-3.5 flex-shrink-0" />
                    {fund.twitter_url.replace(/^https?:\/\/(www\.)?(twitter|x)\.com\//, '@')}
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>
                ) : <p className="text-sm text-gray-400 italic">—</p>}
              </div>
            )}

            {/* Contact email */}
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Contact Email</p>
              {editing ? (
                <input type="email" value={draft.contact_email}
                  onChange={e => setDraft(d => ({ ...d, contact_email: e.target.value }))}
                  className={inp} placeholder="contact@fund.com" />
              ) : fund.contact_email ? (
                <a href={`mailto:${fund.contact_email}`}
                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                  <Mail className="w-3.5 h-3.5 flex-shrink-0" />
                  {fund.contact_email}
                </a>
              ) : <p className="text-sm text-gray-400 italic">—</p>}
            </div>
          </div>

          {/* Overview */}
          <div>
            <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Overview</p>
            {editing ? (
              <textarea value={draft.overview}
                onChange={e => setDraft(d => ({ ...d, overview: e.target.value }))}
                rows={4}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Fund overview…" />
            ) : (
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {fund.overview || <span className="text-gray-400 italic">—</span>}
              </p>
            )}
          </div>

          {/* Funding requirements */}
          {(fund.funding_requirements || editing) && (
            <div>
              <p className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">Funding Requirements</p>
              {editing ? (
                <textarea value={draft.funding_requirements}
                  onChange={e => setDraft(d => ({ ...d, funding_requirements: e.target.value }))}
                  rows={2}
                  className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500 resize-none" />
              ) : (
                <p className="text-sm text-gray-700">{fund.funding_requirements}</p>
              )}
            </div>
          )}

          {/* Target countries */}
          {fund.target_countries?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">Target Countries</p>
              <div className="flex flex-wrap gap-2">
                {fund.target_countries.map(c => (
                  <span key={c} className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">{c}</span>
                ))}
              </div>
            </div>
          )}

          {/* ── Hunter.io Panel ── */}
          <HunterStudioPanel
            defaultDomain={deriveDomain(fund.website_url)}
            companyName={fund.name}
            onSaveContacts={async (contacts) => {
              for (const c of contacts) {
                await createContact.mutateAsync({
                  fund_id:  fund.id,
                  full_name: c.full_name,
                  email:     c.email,
                  title:     c.title,
                  linkedin_url: c.linkedin_url,
                });
              }
              refetchContacts();
            }}
          />

          {/* ── Contacts ── */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                Contacts ({fundContacts.length})
              </p>
              <button
                onClick={() => setShowAddContact((v) => !v)}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                <Plus className="w-3.5 h-3.5" />
                {showAddContact ? 'Cancel' : 'Add contact'}
              </button>
            </div>

            {showAddContact && (
              <div className="mb-3">
                <AddContactForm
                  fundId={fund.id}
                  onDone={() => { setShowAddContact(false); refetchContacts(); }}
                />
              </div>
            )}

            {fundContacts.length === 0 && !showAddContact ? (
              <p className="text-xs text-gray-400 italic py-2">No contacts yet. Add one above.</p>
            ) : (
              <div className="space-y-2">
                {fundContacts.map((c) => (
                  <ContactRow
                    key={c.id}
                    contact={c}
                    onDelete={(id) => { deleteContact.mutate(id); refetchContacts(); }}
                    onOpen={(c) => setSelectedContact(c)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>

    {selectedContact && (
      <VCContactDetailModal
        contact={selectedContact}
        fundName={fund.name}
        fundWebsite={fund.website_url || undefined}
        onClose={() => setSelectedContact(null)}
      />
    )}
    </>
  );
}
