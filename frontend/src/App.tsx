import { useState, useMemo } from 'react';
import { usePendingStudioPackets, useStudioPackets } from './hooks/useStudioPackets';
import { useFunds } from './hooks/useFunds';
import { useDarkMode } from './hooks/useDarkMode';
import { useQueryClient } from '@tanstack/react-query';
import { FundCard } from './components/FundCard';
import { StudioCard } from './components/StudioCard';
import { QueueStatus } from './components/QueueStatus';
import { EmailTemplateManager } from './components/EmailTemplateManager';
import { ContactsView } from './components/ContactsView';
import { VCContactsView } from './components/VCContactsView';
import { StudioDetailModal } from './components/StudioDetailModal';
import { ContactDetailModal } from './components/ContactDetailModal';
import { FundDetailModal } from './components/FundDetailModal';
import { KanbanBoard } from './components/KanbanBoard';
import { BulkUploadModal } from './components/BulkUploadModal';
import { BulkDeleteBar } from './components/BulkDeleteBar';
import { ClipboardCheck, Filter, Inbox, Users, Building2, Mail, UserCircle, LayoutDashboard, Briefcase, Moon, Sun, Upload, ListChecks } from 'lucide-react';
import type { StudioPacket, BDRContact, Fund } from './types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

type View = 'vc' | 'studios' | 'contacts' | 'vc-contacts' | 'tasks';

function App() {
  const { isDark, toggle: toggleDark } = useDarkMode();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentView, setCurrentView] = useState<View>('studios');
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [showBulkUpload, setShowBulkUpload] = useState(false);

  // Bulk-select state
  const [studioSelectMode, setStudioSelectMode] = useState(false);
  const [studioSelected, setStudioSelected] = useState<Set<string>>(new Set());
  const [studioDeleting, setStudioDeleting] = useState(false);

  const [vcSelectMode, setVcSelectMode] = useState(false);
  const [vcSelected, setVcSelected] = useState<Set<string>>(new Set());
  const [vcDeleting, setVcDeleting] = useState(false);

  // Studio detail modal state
  const [selectedStudio, setSelectedStudio] = useState<StudioPacket | null>(null);

  // Fund detail modal state
  const [selectedFund, setSelectedFund] = useState<Fund | null>(null);

  // Contact detail modal state (can be opened from studios or contacts view)
  const [selectedContact, setSelectedContact] = useState<{ contact: BDRContact; studioName: string; studioWebsite?: string } | null>(null);

  const switchView = (view: View) => {
    setCurrentView(view);
    setStatusFilter('');
    setStudioSelectMode(false);
    setStudioSelected(new Set());
    setVcSelectMode(false);
    setVcSelected(new Set());
  };

  // VC / Funds data — query funds table directly
  const { data: fundsData, isLoading: vcLoading } = useFunds(statusFilter || undefined);

  // Studio data
  const { data: studioPacketsData, isLoading: studioLoading } = useStudioPackets(statusFilter);
  const { data: pendingStudioData } = usePendingStudioPackets();

  const rawFunds = fundsData?.items || [];
  const rawStudios = studioPacketsData?.items || [];

  // Sort newest first
  const funds = useMemo(
    () => [...rawFunds].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
    [rawFunds]
  );
  const studioPackets = useMemo(
    () => [...rawStudios].sort((a, b) => {
      const aDate = a.studio?.created_at ?? '';
      const bDate = b.studio?.created_at ?? '';
      return new Date(bDate).getTime() - new Date(aDate).getTime();
    }),
    [rawStudios]
  );

  // Bulk delete helpers
  const toggleStudio = (id: string) => setStudioSelected(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  const deleteStudios = async () => {
    if (studioSelected.size === 0) return;
    if (!confirm(`Permanently delete ${studioSelected.size} studio(s)? This cannot be undone.`)) return;
    setStudioDeleting(true);
    try {
      await fetch(`${API_BASE}/bdr/companies/bulk-delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [...studioSelected] }),
      });
      setStudioSelected(new Set());
      setStudioSelectMode(false);
      queryClient.invalidateQueries({ queryKey: ['studioPackets'] });
    } finally {
      setStudioDeleting(false);
    }
  };

  const toggleFund = (id: string) => setVcSelected(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  const deleteFunds = async () => {
    if (vcSelected.size === 0) return;
    if (!confirm(`Permanently delete ${vcSelected.size} fund(s)? This cannot be undone.`)) return;
    setVcDeleting(true);
    try {
      await fetch(`${API_BASE}/funds/bulk-delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [...vcSelected] }),
      });
      setVcSelected(new Set());
      setVcSelectMode(false);
      queryClient.invalidateQueries({ queryKey: ['funds'] });
    } finally {
      setVcDeleting(false);
    }
  };

  const pendingCount = pendingStudioData?.total || 0;

  /** Open a contact's detail modal, switching to contacts view first */
  const handleOpenContact = (contact: BDRContact, studioName: string, studioWebsite?: string) => {
    setSelectedStudio(null); // close studio modal
    setSelectedContact({ contact, studioName, studioWebsite });
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
                  Studio Contacts
                </button>
                <button
                  onClick={() => switchView('vc-contacts')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'vc-contacts' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Briefcase className="w-4 h-4" />
                  VC Contacts
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

              {/* Dark mode toggle */}
              <button
                onClick={toggleDark}
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
                className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* Bulk Upload Button */}
              <button
                onClick={() => setShowBulkUpload(true)}
                title="Bulk import via CSV"
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Upload className="w-4 h-4" />
                Import
              </button>

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
                <div className="flex gap-2 flex-wrap flex-1">
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
                {/* Select mode toggle for studios and VC */}
                {currentView === 'studios' && (
                  <button
                    onClick={() => { setStudioSelectMode(v => !v); setStudioSelected(new Set()); }}
                    className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                      studioSelectMode ? 'bg-blue-50 border-blue-400 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <ListChecks className="w-4 h-4" />
                    {studioSelectMode ? 'Exit select' : 'Select'}
                  </button>
                )}
                {currentView === 'vc' && (
                  <button
                    onClick={() => { setVcSelectMode(v => !v); setVcSelected(new Set()); }}
                    className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                      vcSelectMode ? 'bg-blue-50 border-blue-400 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <ListChecks className="w-4 h-4" />
                    {vcSelectMode ? 'Exit select' : 'Select'}
                  </button>
                )}
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
                  <FundCard
                    key={fund.id}
                    fund={fund}
                    onClick={vcSelectMode ? undefined : () => setSelectedFund(fund)}
                    selected={vcSelectMode ? vcSelected.has(fund.id) : undefined}
                    onToggle={vcSelectMode ? (e) => { e.stopPropagation(); toggleFund(fund.id); } : undefined}
                  />
                ))}
              </div>
            )}
            {vcSelectMode && vcSelected.size > 0 && (
              <BulkDeleteBar
                count={vcSelected.size}
                total={funds.length}
                onSelectAll={() => setVcSelected(new Set(funds.map(f => f.id)))}
                onClearAll={() => { setVcSelected(new Set()); setVcSelectMode(false); }}
                onDelete={deleteFunds}
                deleting={vcDeleting}
              />
            )}
          </>
        )}

        {/* ── Studio Contacts View ── */}
        {currentView === 'contacts' && (
          <ContactsView
            initialOpenContact={selectedContact ?? undefined}
            onContactModalClosed={() => setSelectedContact(null)}
          />
        )}

        {/* ── VC Contacts View ── */}
        {currentView === 'vc-contacts' && <VCContactsView />}

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
                    onClick={studioSelectMode ? undefined : () => setSelectedStudio(packet)}
                    selected={studioSelectMode ? studioSelected.has(packet.studio?.id ?? packet.id) : undefined}
                    onToggle={studioSelectMode ? (e) => { e.stopPropagation(); toggleStudio(packet.studio?.id ?? packet.id); } : undefined}
                  />
                ))}
              </div>
            )}
            {studioSelectMode && studioSelected.size > 0 && (
              <BulkDeleteBar
                count={studioSelected.size}
                total={studioPackets.length}
                onSelectAll={() => setStudioSelected(new Set(studioPackets.map(p => p.studio?.id ?? p.id)))}
                onClearAll={() => { setStudioSelected(new Set()); setStudioSelectMode(false); }}
                onDelete={deleteStudios}
                deleting={studioDeleting}
              />
            )}
          </>
        )}

        {/* ── Tasks (Kanban) View ── */}
        {currentView === 'tasks' && <KanbanBoard />}
      </main>

      {/* ── Fund Detail Modal ── */}
      {selectedFund && (
        <FundDetailModal
          fund={selectedFund}
          onClose={() => setSelectedFund(null)}
        />
      )}

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
          studioWebsite={selectedContact.studioWebsite}
          onClose={() => setSelectedContact(null)}
        />
      )}

      {/* ── Email Template Manager ── */}
      {showTemplateManager && (
        <EmailTemplateManager
          onClose={() => setShowTemplateManager(false)}
        />
      )}

      {/* ── Bulk Upload Modal ── */}
      {showBulkUpload && (
        <BulkUploadModal onClose={() => setShowBulkUpload(false)} />
      )}
    </div>
  );
}

export default App;
