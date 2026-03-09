import { useState } from 'react';
import { usePendingStudioPackets, useStudioPackets } from './hooks/useStudioPackets';
import { useFunds } from './hooks/useFunds';
import { FundCard } from './components/FundCard';
import { StudioCard } from './components/StudioCard';
import { QueueStatus } from './components/QueueStatus';
import { EmailTemplateManager } from './components/EmailTemplateManager';
import { ContactsView } from './components/ContactsView';
import { StudioDetailModal } from './components/StudioDetailModal';
import { ContactDetailModal } from './components/ContactDetailModal';
import { KanbanBoard } from './components/KanbanBoard';
import { ClipboardCheck, Filter, Inbox, Users, Building2, Mail, UserCircle, LayoutDashboard } from 'lucide-react';
import type { StudioPacket, BDRContact } from './types';

type View = 'vc' | 'studios' | 'contacts' | 'tasks';

function App() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentView, setCurrentView] = useState<View>('studios');
  const [showTemplateManager, setShowTemplateManager] = useState(false);

  // Studio detail modal state
  const [selectedStudio, setSelectedStudio] = useState<StudioPacket | null>(null);

  // Contact detail modal state (can be opened from studios or contacts view)
  const [selectedContact, setSelectedContact] = useState<{ contact: BDRContact; studioName: string } | null>(null);

  const switchView = (view: View) => {
    setCurrentView(view);
    setStatusFilter(''); // reset to "All" whenever switching tabs
  };

  // VC / Funds data — query funds table directly
  const { data: fundsData, isLoading: vcLoading } = useFunds(statusFilter || undefined);

  // Studio data
  const { data: studioPacketsData, isLoading: studioLoading } = useStudioPackets(statusFilter);
  const { data: pendingStudioData } = usePendingStudioPackets();

  const funds = fundsData?.items || [];
  const studioPackets = studioPacketsData?.items || [];

  const pendingCount = pendingStudioData?.total || 0;

  /** Open a contact's detail modal, switching to contacts view first */
  const handleOpenContact = (contact: BDRContact, studioName: string) => {
    setSelectedStudio(null); // close studio modal
    setSelectedContact({ contact, studioName });
    setCurrentView('contacts');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-shrink-0">
              <ClipboardCheck className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Outreach Dashboard</h1>
                <p className="text-sm text-gray-500">VC & Game Studio Outreach</p>
              </div>
            </div>

            <div className="flex items-center gap-3 flex-wrap justify-end">
              {/* View Toggle */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => switchView('vc')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'vc' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Users className="w-4 h-4" />
                  VC Funds
                </button>
                <button
                  onClick={() => switchView('studios')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'studios' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Building2 className="w-4 h-4" />
                  Game Studios
                </button>
                <button
                  onClick={() => switchView('contacts')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'contacts' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <UserCircle className="w-4 h-4" />
                  Contacts
                </button>
                <button
                  onClick={() => switchView('tasks')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'tasks' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Tasks
                </button>
              </div>

              {/* Template Manager Button */}
              <button
                onClick={() => setShowTemplateManager(true)}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Mail className="w-4 h-4" />
                Templates
              </button>

              {/* Awaiting approval counter (hidden on tasks view) */}
              {currentView !== 'tasks' && (
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
                  <p className="text-xs text-gray-500">Awaiting Approval</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className={`${currentView === 'tasks' ? 'max-w-[1600px]' : 'max-w-7xl'} mx-auto px-4 sm:px-6 lg:px-8 py-8`}>

        {/* Queue Status — hide on tasks view */}
        {currentView !== 'tasks' && <QueueStatus />}

        {/* Status Filters — shown only for VC and Studios views */}
        {(currentView === 'vc' || currentView === 'studios') && (() => {
          // FundStatus: NEW, RESEARCHING, READY, APPROVED, SENT, FOLLOW_UP, CLOSED
          const vcStatuses     = ['ALL', 'NEW', 'RESEARCHING', 'READY', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'];
          const studioStatuses = ['ALL', 'NEW', 'QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'];
          const statuses = currentView === 'vc' ? vcStatuses : studioStatuses;
          const activeColor = currentView === 'vc' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white';
          const allLabel = currentView === 'vc' ? 'All Funds' : 'All Studios';

          return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
              <div className="flex items-center gap-4">
                <Filter className="w-5 h-5 text-gray-400" />
                <div className="flex gap-2 flex-wrap">
                  {statuses.map((s) => (
                    <button
                      key={s}
                      onClick={() => setStatusFilter(s === 'ALL' ? '' : s)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        (s === 'ALL' && !statusFilter) || statusFilter === s
                          ? activeColor
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {s === 'ALL' ? allLabel : s.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          );
        })()}

        {/* ── VC / Funds View ── */}
        {currentView === 'vc' && (
          <>
            {vcLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
                    <div className="h-6 bg-gray-200 rounded mb-2" />
                    <div className="h-4 bg-gray-200 rounded mb-2 w-3/4" />
                    <div className="h-4 bg-gray-200 rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : funds.length === 0 ? (
              <div className="text-center py-12">
                <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No funds found</h3>
                <p className="text-gray-500">
                  {statusFilter ? `No funds with status "${statusFilter.replace(/_/g, ' ')}"` : 'No funds yet'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {funds.map((fund) => (
                  <FundCard key={fund.id} fund={fund} />
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Contacts View ── */}
        {currentView === 'contacts' && (
          <ContactsView
            initialOpenContact={selectedContact ?? undefined}
            onContactModalClosed={() => setSelectedContact(null)}
          />
        )}

        {/* ── Studios View ── */}
        {currentView === 'studios' && (
          <>
            {studioLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
                    <div className="h-6 bg-gray-200 rounded mb-2" />
                    <div className="h-4 bg-gray-200 rounded mb-2 w-3/4" />
                    <div className="h-4 bg-gray-200 rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : studioPackets.length === 0 ? (
              <div className="text-center py-12">
                <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No studios found</h3>
                <p className="text-gray-500">
                  {statusFilter ? `No studios with status "${statusFilter.replace(/_/g, ' ')}"` : 'No studios yet'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {studioPackets.map((packet) => (
                  <StudioCard
                    key={packet.id}
                    packet={packet}
                    onClick={() => setSelectedStudio(packet)}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Tasks (Kanban) View ── */}
        {currentView === 'tasks' && <KanbanBoard />}
      </main>

      {/* ── Studio Detail Modal ── */}
      {selectedStudio && (
        <StudioDetailModal
          packet={selectedStudio}
          onClose={() => setSelectedStudio(null)}
          onOpenContact={handleOpenContact}
        />
      )}

      {/* ── Contact Detail Modal (opened from studio or contacts view) ── */}
      {selectedContact && currentView === 'contacts' && (
        <ContactDetailModal
          contact={selectedContact.contact}
          studioName={selectedContact.studioName}
          onClose={() => setSelectedContact(null)}
        />
      )}

      {/* ── Email Template Manager ── */}
      {showTemplateManager && (
        <EmailTemplateManager
          onClose={() => setShowTemplateManager(false)}
        />
      )}
    </div>
  );
}

export default App;
