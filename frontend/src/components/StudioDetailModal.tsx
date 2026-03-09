import { useState } from 'react';
import {
  X, Globe, Linkedin, Mail, Star, Flag, Building2, Users,
  ExternalLink, Clock, ChevronRight, Save, RotateCcw, Edit3,
} from 'lucide-react';
import type { StudioPacket, BDRContact, PacketStatus } from '../types';
import { useContacts } from '../hooks/useContacts';
import { useUpdateCompany } from '../hooks/useStudioPackets';
import { HunterStudioPanel } from './HunterStudioPanel';
import { deriveDomain } from '../lib/hunterApi';

interface StudioDetailModalProps {
  packet: StudioPacket;
  onClose: () => void;
  /** Called when the user clicks a contact row — parent should open ContactDetailModal */
  onOpenContact: (contact: BDRContact, studioName: string, studioWebsite?: string) => void;
}

const statusOptions: PacketStatus[] = ['NEW', 'QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'];

const statusColors: Record<PacketStatus, string> = {
  NEW: 'bg-gray-100 text-gray-700',
  QUEUED: 'bg-gray-100 text-gray-800',
  AWAITING_APPROVAL: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  SENT: 'bg-blue-100 text-blue-800',
  FOLLOW_UP: 'bg-purple-100 text-purple-800',
  CLOSED: 'bg-red-100 text-red-800',
};

export function StudioDetailModal({ packet, onClose, onOpenContact }: StudioDetailModalProps) {
  const studio = packet.studio;
  const updateCompany = useUpdateCompany();
  const isFlagged = studio?.is_flagged ?? false;

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({
    company_name: studio?.name || '',
    website_url: studio?.website_url || '',
    linkedin_url: studio?.linkedin_url || '',
    headquarters_city: studio?.hq_city || '',
    headquarters_state: studio?.hq_region || '',
    headquarters_country: studio?.hq_country || '',
    company_size: studio?.employee_count || '',
    status: packet.status as string,
    priority: packet.priority as string,
  });

  // Load contacts for this company
  const { data: contactsData, isLoading: loadingContacts } = useContacts(
    studio?.id ? { company_id: studio.id } : undefined
  );
  const contacts: BDRContact[] = contactsData?.items || [];

  const handleSave = () => {
    if (!studio?.id) return;
    updateCompany.mutate(
      { id: studio.id, data: draft },
      { onSuccess: () => setEditing(false) }
    );
  };

  const handleDiscard = () => {
    setDraft({
      company_name: studio?.name || '',
      website_url: studio?.website_url || '',
      linkedin_url: studio?.linkedin_url || '',
      headquarters_city: studio?.hq_city || '',
      headquarters_state: studio?.hq_region || '',
      headquarters_country: studio?.hq_country || '',
      company_size: studio?.employee_count || '',
      status: packet.status as string,
      priority: packet.priority as string,
    });
    setEditing(false);
  };

  const formatLastContacted = (dateStr?: string | null): string | null => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      const diffMs = Date.now() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
      return date.toLocaleDateString();
    } catch {
      return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-xl">

        {/* ── Header ── */}
        <div className={`flex items-start justify-between p-5 border-b rounded-t-xl ${isFlagged ? 'bg-red-50' : ''}`}>
          <div className="flex items-center gap-3 min-w-0">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${isFlagged ? 'bg-red-100' : 'bg-blue-50'}`}>
              <Building2 className={`w-6 h-6 ${isFlagged ? 'text-red-500' : 'text-blue-500'}`} />
            </div>
            <div className="min-w-0">
              {editing ? (
                <input
                  value={draft.company_name}
                  onChange={(e) => setDraft(d => ({ ...d, company_name: e.target.value }))}
                  className="text-lg font-semibold text-gray-900 border-b border-gray-300 focus:border-blue-500 outline-none w-full"
                />
              ) : (
                <h2 className="text-lg font-semibold text-gray-900 truncate">{studio?.name || 'Unknown Studio'}</h2>
              )}
              <p className="text-sm text-gray-500">{studio?.studio_type}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0 ml-3">
            {/* Flag */}
            <button
              onClick={() => studio?.id && updateCompany.mutate({ id: studio.id, data: { is_flagged: !isFlagged } })}
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

            {/* Edit / Save / Discard */}
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
                  disabled={updateCompany.isPending}
                  className="flex items-center gap-1 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  {updateCompany.isPending ? 'Saving…' : 'Save'}
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
        <div className="flex-1 overflow-auto p-5 space-y-6">

          {/* Studio details grid */}
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Studio Info</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* Status */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">Status</p>
                {editing ? (
                  <select
                    value={draft.status}
                    onChange={(e) => setDraft(d => ({ ...d, status: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500"
                  >
                    {statusOptions.map(s => (
                      <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                ) : (
                  <span className={`inline-block text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[packet.status]}`}>
                    {packet.status.replace(/_/g, ' ')}
                  </span>
                )}
              </div>

              {/* Priority */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">Priority</p>
                {editing ? (
                  <select
                    value={draft.priority}
                    onChange={(e) => setDraft(d => ({ ...d, priority: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500"
                  >
                    {['A', 'B', 'C'].map(p => <option key={p} value={p}>Priority {p}</option>)}
                  </select>
                ) : (
                  <span className={`inline-block text-xs font-bold px-2.5 py-1 rounded ${
                    packet.priority === 'A' ? 'bg-red-500 text-white' :
                    packet.priority === 'B' ? 'bg-yellow-500 text-white' : 'bg-gray-400 text-white'
                  }`}>
                    Priority {packet.priority}
                  </span>
                )}
              </div>

              {/* HQ */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">Headquarters</p>
                {editing ? (
                  <div className="flex gap-1.5">
                    <input placeholder="City" value={draft.headquarters_city} onChange={e => setDraft(d => ({ ...d, headquarters_city: e.target.value }))}
                      className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 flex-1 focus:ring-2 focus:ring-blue-500" />
                    <input placeholder="Country" value={draft.headquarters_country} onChange={e => setDraft(d => ({ ...d, headquarters_country: e.target.value }))}
                      className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-24 focus:ring-2 focus:ring-blue-500" />
                  </div>
                ) : (
                  <p className="text-sm text-gray-700">
                    {[studio?.hq_city, studio?.hq_region, studio?.hq_country].filter(Boolean).join(', ') || '—'}
                  </p>
                )}
              </div>

              {/* Size */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">Company Size</p>
                {editing ? (
                  <input value={draft.company_size} onChange={e => setDraft(d => ({ ...d, company_size: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500" />
                ) : (
                  <p className="text-sm text-gray-700">{studio?.employee_count || '—'}</p>
                )}
              </div>

              {/* Website */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">Website</p>
                {editing ? (
                  <input type="url" value={draft.website_url} onChange={e => setDraft(d => ({ ...d, website_url: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500" />
                ) : studio?.website_url ? (
                  <a href={studio.website_url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                    <Globe className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{studio.website_url.replace(/^https?:\/\//, '')}</span>
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>
                ) : <p className="text-sm text-gray-400">—</p>}
              </div>

              {/* LinkedIn */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-1">LinkedIn</p>
                {editing ? (
                  <input type="url" value={draft.linkedin_url} onChange={e => setDraft(d => ({ ...d, linkedin_url: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 w-full focus:ring-2 focus:ring-blue-500" />
                ) : studio?.linkedin_url ? (
                  <a href={studio.linkedin_url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
                    <Linkedin className="w-3.5 h-3.5 flex-shrink-0" />
                    Company Page
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>
                ) : <p className="text-sm text-gray-400">—</p>}
              </div>

              {/* ICP Score */}
              {studio?.icp_score != null && (
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-1">ICP Score</p>
                  <p className="text-sm font-semibold text-gray-700">{studio.icp_score}</p>
                </div>
              )}
            </div>

            {/* Overview */}
            {studio?.overview && (
              <div className="mt-4">
                <p className="text-xs font-medium text-gray-400 mb-1">Overview</p>
                <p className="text-sm text-gray-700 leading-relaxed">{studio.overview}</p>
              </div>
            )}
          </div>

          {/* ── Contacts ── */}
          <div className="border-t border-gray-100 pt-5">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Contacts ({loadingContacts ? '…' : contacts.length})
            </h3>

            {loadingContacts ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-14 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : contacts.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No contacts linked to this studio yet.</p>
            ) : (
              <div className="space-y-2">
                {contacts.map((contact) => {
                  const lastContacted = formatLastContacted(contact.last_contacted_at);
                  const channelIcon = contact.contact_preference === 'linkedin'
                    ? <Linkedin className="w-3 h-3" />
                    : contact.contact_preference === 'email'
                    ? <Mail className="w-3 h-3" />
                    : null;

                  return (
                    <button
                      key={contact.id}
                      onClick={() => onOpenContact(contact, studio?.name || '', studio?.website_url || '')}
                      className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50 transition-all text-left group"
                    >
                      {/* Avatar */}
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-sm ${contact.is_flagged ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                        {contact.full_name?.[0]?.toUpperCase() || '?'}
                      </div>

                      {/* Name + title */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="text-sm font-medium text-gray-900 truncate">{contact.full_name}</span>
                          {contact.is_decision_maker && (
                            <Star className="w-3 h-3 text-yellow-500 flex-shrink-0" title="Decision Maker" />
                          )}
                          {contact.is_flagged && (
                            <Flag className="w-3 h-3 text-red-400 flex-shrink-0" fill="currentColor" title="Flagged" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 truncate">{contact.job_title || 'Unknown Role'}</p>
                      </div>

                      {/* Right: last contacted + linkedin */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {lastContacted ? (
                          <span className="flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                            {channelIcon}
                            <Clock className="w-3 h-3" />
                            {lastContacted}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">Not contacted</span>
                        )}
                        {contact.linkedin_url && (
                          <a
                            href={contact.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-blue-500 hover:text-blue-700 p-1 rounded hover:bg-blue-100 transition-colors"
                            title="LinkedIn Profile"
                          >
                            <Linkedin className="w-4 h-4" />
                          </a>
                        )}
                        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-blue-400 transition-colors" />
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* ── Hunter.io Studio Panel ── */}
          <HunterStudioPanel
            defaultDomain={deriveDomain(studio?.website_url)}
            companyName={studio?.name}
          />

        </div>
      </div>
    </div>
  );
}
