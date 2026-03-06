import { useState } from 'react';
import { useContacts, type ContactFilters } from '../hooks/useContacts';
import { useStudioPackets } from '../hooks/useStudioPackets';
import { Search, Filter, Mail, Linkedin, Phone, User, Building2, Star, CheckCircle, Send } from 'lucide-react';
import { OutreachModal } from './OutreachModal';
import type { BDRContact } from '../types';

export function ContactsView() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<ContactFilters>({});
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [outreachContact, setOutreachContact] = useState<{ contact: BDRContact; studioName: string } | null>(null);

  const { data: contactsData, isLoading } = useContacts({
    ...filters,
    search: searchTerm,
  });

  const { data: studiosData } = useStudioPackets();

  const contacts = contactsData?.items || [];
  const studios = studiosData?.items || [];

  // Create studio lookup map (company_id → studio name)
  const studioMap = new Map(studios.map((s) => [s.studio_id, s.studio]));

  const handleCompanyFilter = (companyId: string) => {
    setSelectedCompany(companyId);
    setFilters(prev => ({
      ...prev,
      company_id: companyId || undefined,
    }));
  };

  const handleDecisionMakerFilter = (value: boolean | undefined) => {
    setFilters(prev => ({
      ...prev,
      is_decision_maker: value,
    }));
  };

  const formatLastContacted = (dateStr?: string) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Outreach Modal */}
      {outreachContact && (
        <OutreachModal
          contact={outreachContact.contact}
          studioName={outreachContact.studioName}
          onClose={() => setOutreachContact(null)}
        />
      )}

      {/* Header with Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search contacts by name, title, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Company Filter */}
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-gray-400" />
            <select
              value={selectedCompany}
              onChange={(e) => handleCompanyFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 min-w-[200px]"
            >
              <option value="">All Studios</option>
              {studios.map((studio: { studio_id: string; studio?: { name?: string } }) => (
                <option key={studio.studio_id} value={studio.studio_id}>
                  {studio.studio?.name}
                </option>
              ))}
            </select>
          </div>

          {/* Decision Maker Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filters.is_decision_maker === undefined ? '' : filters.is_decision_maker ? 'dm' : 'non-dm'}
              onChange={(e) => {
                const value = e.target.value;
                handleDecisionMakerFilter(value === '' ? undefined : value === 'dm');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Contacts</option>
              <option value="dm">Decision Makers Only</option>
              <option value="non-dm">Non-Decision Makers</option>
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-6 mt-4 pt-4 border-t border-gray-100 text-sm">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-blue-500" />
            <span className="font-medium">{contacts.length}</span>
            <span className="text-gray-500">contacts</span>
          </div>
          <div className="flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-500" />
            <span className="font-medium">{contacts.filter((c: BDRContact) => c.is_decision_maker).length}</span>
            <span className="text-gray-500">decision makers</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="font-medium">{contacts.filter((c: BDRContact) => c.email_verified).length}</span>
            <span className="text-gray-500">verified emails</span>
          </div>
          <div className="flex items-center gap-2">
            <Send className="w-4 h-4 text-purple-500" />
            <span className="font-medium">{contacts.filter((c: BDRContact) => c.last_contacted_at).length}</span>
            <span className="text-gray-500">contacted</span>
          </div>
        </div>
      </div>

      {/* Contacts Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
              <div className="h-6 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : contacts.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No contacts found</h3>
          <p className="text-gray-500">
            {searchTerm ? `No contacts matching "${searchTerm}"` : 'No contacts in the system yet'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map((contact: BDRContact) => {
            const studio = studioMap.get(contact.company_id);
            const lastContacted = formatLastContacted(contact.last_contacted_at);
            const channelIcon = contact.contact_preference === 'linkedin'
              ? <Linkedin className="w-3 h-3" />
              : contact.contact_preference === 'email'
              ? <Mail className="w-3 h-3" />
              : null;

            return (
              <div
                key={contact.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow flex flex-col"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-600 font-semibold text-lg">
                        {contact.full_name?.[0]?.toUpperCase() || '?'}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{contact.full_name}</h3>
                      <p className="text-sm text-gray-500">{contact.job_title || 'Unknown Role'}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    {contact.is_decision_maker && (
                      <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        DM
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

                {/* Studio */}
                {studio && (
                  <div className="mb-3 p-2 bg-gray-50 rounded">
                    <p className="text-sm font-medium text-gray-700">{studio.name}</p>
                    <p className="text-xs text-gray-500">
                      {studio.hq_city}{studio.hq_country ? `, ${studio.hq_country}` : ''}
                    </p>
                  </div>
                )}

                {/* Contact Info */}
                <div className="space-y-2 flex-1">
                  {contact.email && (
                    <a
                      href={`mailto:${contact.email}`}
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
                <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xs text-gray-500">{contact.department || 'Unknown Dept'}</span>
                  <button
                    onClick={() => setOutreachContact({
                      contact,
                      studioName: studio?.name || '',
                    })}
                    className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <Send className="w-3 h-3" />
                    Outreach
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
