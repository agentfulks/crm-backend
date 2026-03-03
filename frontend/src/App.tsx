import { useState } from 'react';
import { usePendingPackets, usePackets } from './hooks/usePackets';
import { usePendingStudioPackets, useStudioPackets, useUpdateStudioPacketStatus } from './hooks/useStudioPackets';
import { useApplyTemplate } from './hooks/useEmailTemplates';
import { PacketCard } from './components/PacketCard';
import { StudioCard } from './components/StudioCard';
import { PacketDetail } from './components/PacketDetail';
import { QueueStatus } from './components/QueueStatus';
import { EmailTemplateManager } from './components/EmailTemplateManager';
import { ContactsView } from './components/ContactsView';
import { ClipboardCheck, Filter, Inbox, CheckCircle, XCircle, Users, Building2, Mail, UserCircle } from 'lucide-react';
import type { Packet, EmailTemplate } from './types';

type View = 'vc' | 'studios' | 'contacts';

function App() {
  const [selectedPacketId, setSelectedPacketId] = useState<string | null>(null);
  const [editingPacketId, setEditingPacketId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('AWAITING_APPROVAL');
  const [actionNotification, setActionNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  // Consume the setter to avoid unused variable warning while keeping it available for future use
  setActionNotification;
  const [currentView, setCurrentView] = useState<View>('vc');
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [selectedStudioForTemplate, setSelectedStudioForTemplate] = useState<{name: string, contactName: string} | null>(null);
  
  // VC data
  const { data: packetsData, isLoading: vcLoading } = usePackets(statusFilter);
  const { data: pendingData } = usePendingPackets();
  
  // Studio data
  const { data: studioPacketsData, isLoading: studioLoading } = useStudioPackets(statusFilter);
  const { data: pendingStudioData } = usePendingStudioPackets();
  const updateStatusMutation = useUpdateStudioPacketStatus();
  
  const packets = packetsData?.items || [];
  const studioPackets = studioPacketsData?.items || [];
  
  const pendingCount = currentView === 'vc' 
    ? (pendingData?.total || 0) 
    : (pendingStudioData?.total || 0);

  const handleStatusChange = async (packetId: string, newStatus: string) => {
    try {
      await updateStatusMutation.mutateAsync({ id: packetId, status: newStatus });
      setActionNotification({
        type: 'success',
        message: `Status updated to ${newStatus}`
      });
    } catch {
      setActionNotification({
        type: 'error',
        message: 'Failed to update status'
      });
    }
    setTimeout(() => setActionNotification(null), 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ClipboardCheck className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Outreach Dashboard</h1>
                <p className="text-sm text-gray-500">VC & Game Studio Outreach</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* View Toggle */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setCurrentView('vc')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'vc'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Users className="w-4 h-4" />
                  VC Funds
                </button>
                <button
                  onClick={() => setCurrentView('studios')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'studios'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Building2 className="w-4 h-4" />
                  Game Studios
                </button>
                <button
                  onClick={() => setCurrentView('contacts')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'contacts'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <UserCircle className="w-4 h-4" />
                  Contacts
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
              
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
                <p className="text-xs text-gray-500">Awaiting Approval</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Action Notification */}
        {actionNotification && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            actionNotification.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {actionNotification.type === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <XCircle className="w-5 h-5" />
            )}
            <span className="font-medium">{actionNotification.message}</span>
          </div>
        )}

        {/* Queue Status */}
        <QueueStatus />

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="flex gap-2 flex-wrap">
              {['ALL', 'NEW', 'QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT'].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status === 'ALL' ? '' : status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    (status === 'ALL' && !statusFilter) || statusFilter === status
                      ? currentView === 'vc' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status === 'ALL' ? (currentView === 'vc' ? 'All Packets' : 'All Studios') : status.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* VC View */}
        {currentView === 'vc' && (
          <>
            {vcLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
                    <div className="h-6 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : packets.length === 0 ? (
              <div className="text-center py-12">
                <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No packets found</h3>
                <p className="text-gray-500">
                  {statusFilter 
                    ? `No packets with status "${statusFilter.replace('_', ' ')}"` 
                    : 'No packets in the system yet'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {packets.map((packet: Packet) => (
                  <PacketCard
                    key={packet.id}
                    packet={packet}
                    onClick={() => setSelectedPacketId(packet.id)}
                    onEdit={() => setEditingPacketId(packet.id)}
                    showActions={packet.status === 'AWAITING_APPROVAL'}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Contacts View */}
        {currentView === 'contacts' && <ContactsView />}

        {/* Studios View */}
        {currentView === 'studios' && (
          <>
            {studioLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
                    <div className="h-6 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : studioPackets.length === 0 ? (
              <div className="text-center py-12">
                <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No studios found</h3>
                <p className="text-gray-500">
                  {statusFilter 
                    ? `No studios with status "${statusFilter.replace('_', ' ')}"` 
                    : 'No studios in the system yet'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {studioPackets.map((packet) => (
                  <StudioCard
                    key={packet.id}
                    packet={packet}
                    showActions={true}
                    onApprove={() => handleStatusChange(packet.id, 'APPROVED')}
                    onReject={() => handleStatusChange(packet.id, 'CLOSED')}
                    onEdit={() => setEditingPacketId(packet.id)}
                    onStatusChange={(newStatus) => handleStatusChange(packet.id, newStatus)}
                    onApplyTemplate={() => {
                      setSelectedStudioForTemplate({
                        name: packet.studio?.name || '',
                        contactName: packet.contact_name || ''
                      });
                      setShowTemplateManager(true);
                    }}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </main>

      {/* Packet Detail Modal */}
      {selectedPacketId && currentView === 'vc' && (
        <PacketDetail
          packetId={selectedPacketId}
          onClose={() => setSelectedPacketId(null)}
        />
      )}

      {/* Edit Modal Placeholder */}
      {editingPacketId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Edit Feature</h3>
            <p className="text-gray-600 mb-4">Edit functionality coming soon.</p>
            <button 
              onClick={() => setEditingPacketId(null)}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
      {/* Email Template Manager */}
      {showTemplateManager && (
        <EmailTemplateManager
          onClose={() => {
            setShowTemplateManager(false);
            setSelectedStudioForTemplate(null);
          }}
          onSelectTemplate={selectedStudioForTemplate ? async (template) => {
            try {
              const result = await applyTemplateMutation.mutateAsync({
                templateId: template.id,
                studioName: selectedStudioForTemplate.name,
                contactName: selectedStudioForTemplate.contactName,
              });
              setActionNotification({
                type: 'success',
                message: `Template "${template.name}" applied!`
              });
              setShowTemplateManager(false);
              setSelectedStudioForTemplate(null);
            } catch {
              setActionNotification({
                type: 'error',
                message: 'Failed to apply template'
              });
            }
            setTimeout(() => setActionNotification(null), 3000);
          } : undefined}
          selectMode={!!selectedStudioForTemplate}
        />
      )}
    </div>
  );
}

export default App;
