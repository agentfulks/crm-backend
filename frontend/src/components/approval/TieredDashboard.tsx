import { useState } from 'react';
import { useApprovalDashboard, useApprovalMetrics } from '../../hooks/useApproval';
import { Tier2QuickReview } from './Tier2QuickReview';
import { Tier3DeepReview } from './Tier3DeepReview';
import { Tier1AutoLog } from './Tier1AutoLog';
import { BatchActions } from './BatchActions';
import { CardDetail } from './CardDetail';
import { KeyboardShortcutsHelp } from './KeyboardShortcutsHelp';
import type { ApprovalTier, CardType, ApprovalFilters, ApprovalCard } from '../../types/approval';
import { 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Filter, 
  BarChart3, 
  RefreshCw,
  Layers,
  Zap,
  Search,
  HelpCircle,
  X
} from 'lucide-react';

// Tier color configuration
const TIER_COLORS = {
  1: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    header: 'bg-green-100',
    text: 'text-green-800',
    badge: 'bg-green-500',
    icon: 'text-green-600',
    light: 'bg-green-500/10',
  },
  2: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    header: 'bg-yellow-100',
    text: 'text-yellow-800',
    badge: 'bg-yellow-500',
    icon: 'text-yellow-600',
    light: 'bg-yellow-500/10',
  },
  3: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    header: 'bg-red-100',
    text: 'text-red-800',
    badge: 'bg-red-500',
    icon: 'text-red-600',
    light: 'bg-red-500/10',
  },
};

interface TierColumnProps {
  tier: ApprovalTier;
  count: number;
  onStartReview: () => void;
  onViewLog?: () => void;
  recentActivity?: { action: string; companyName: string; timestamp: string }[];
}

function TierColumn({ tier, count, onStartReview, onViewLog, recentActivity }: TierColumnProps) {
  const colors = TIER_COLORS[tier];
  const titles = { 1: 'Auto-Approve', 2: 'Quick Review', 3: 'Deep Review' };
  const descriptions = {
    1: 'Auto-approved cards with 95%+ confidence',
    2: '30-second review for borderline cases',
    3: 'Full review for complex scenarios',
  };
  const icons = {
    1: Zap,
    2: Clock,
    3: AlertTriangle,
  };
  const Icon = icons[tier];

  return (
    <div className={`rounded-xl border ${colors.border} overflow-hidden flex flex-col h-full`}>
      {/* Header */}
      <div className={`${colors.header} p-4`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${colors.light}`}>
              <Icon className={`w-5 h-5 ${colors.icon}`} />
            </div>
            <div>
              <h3 className={`font-bold ${colors.text}`}>Tier {tier}</h3>
              <p className={`text-xs ${colors.text} opacity-80`}>{titles[tier]}</p>
            </div>
          </div>
          <span className={`${colors.badge} text-white text-sm font-bold px-3 py-1 rounded-full`}>
            {count}
          </span>
        </div>
        <p className={`text-xs ${colors.text} opacity-70`}>{descriptions[tier]}</p>
      </div>

      {/* Content */}
      <div className={`${colors.bg} p-4 flex-1 flex flex-col`}>
        {tier === 1 ? (
          <button
            onClick={onViewLog}
            className={`w-full py-3 px-4 ${colors.badge} text-white font-medium rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-2`}
          >
            <Layers className="w-4 h-4" />
            View Log
          </button>
        ) : (
          <button
            onClick={onStartReview}
            disabled={count === 0}
            className={`w-full py-3 px-4 ${colors.badge} text-white font-medium rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
          >
            <Search className="w-4 h-4" />
            Start Review
          </button>
        )}

        {/* Recent Activity */}
        {recentActivity && recentActivity.length > 0 && (
          <div className="mt-4">
            <h4 className={`text-xs font-semibold ${colors.text} opacity-80 uppercase tracking-wide mb-2`}>
              Recent Activity
            </h4>
            <div className="space-y-2">
              {recentActivity.slice(0, 3).map((activity, idx) => (
                <div key={idx} className="text-xs bg-white/60 rounded p-2">
                  <span className="font-medium">{activity.companyName}</span>
                  <span className={`ml-1 opacity-70`}>
                    {activity.action.replace('_', ' ')}
                  </span>
                  <span className="block text-gray-400 mt-1">
                    {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface MetricsBarProps {
  metrics: {
    autoApprovalRate: number;
    avgReviewTimeSeconds: number;
    backlogSize: number;
  } | undefined;
  isLoading: boolean;
}

function MetricsBar({ metrics, isLoading }: MetricsBarProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="w-5 h-5 text-gray-500" />
        <h3 className="font-semibold text-gray-900">Metrics</h3>
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div>
          <p className="text-sm text-gray-500 mb-1">Auto-Approval Rate</p>
          <p className="text-2xl font-bold text-green-600">{metrics.autoApprovalRate}%</p>
          <p className="text-xs text-gray-400">Target: 55-65%</p>
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-1">Avg Review Time</p>
          <p className="text-2xl font-bold text-blue-600">{metrics.avgReviewTimeSeconds}s</p>
          <p className="text-xs text-gray-400">Target: &lt;45s</p>
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-1">Backlog Size</p>
          <p className="text-2xl font-bold text-purple-600">{metrics.backlogSize}</p>
          <p className="text-xs text-gray-400">Total awaiting</p>
        </div>
      </div>
    </div>
  );
}

interface FiltersBarProps {
  filters: ApprovalFilters;
  onFilterChange: (filters: ApprovalFilters) => void;
  onRefresh: () => void;
}

function FiltersBar({ filters, onFilterChange, onRefresh }: FiltersBarProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="font-medium text-gray-700">Filters:</span>
        </div>

        {/* Tier Filter */}
        <select
          value={filters.tier || ''}
          onChange={(e) => onFilterChange({ ...filters, tier: e.target.value ? Number(e.target.value) as ApprovalTier : undefined })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Tiers</option>
          <option value="1">Tier 1 (Auto)</option>
          <option value="2">Tier 2 (Quick)</option>
          <option value="3">Tier 3 (Deep)</option>
        </select>

        {/* Type Filter */}
        <select
          value={filters.type || ''}
          onChange={(e) => onFilterChange({ ...filters, type: e.target.value as CardType | undefined })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Types</option>
          <option value="BDR">BDR</option>
          <option value="VC">VC</option>
        </select>

        {/* Date Range */}
        <input
          type="date"
          value={filters.dateFrom || ''}
          onChange={(e) => onFilterChange({ ...filters, dateFrom: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="From"
        />
        <span className="text-gray-400">to</span>
        <input
          type="date"
          value={filters.dateTo || ''}
          onChange={(e) => onFilterChange({ ...filters, dateTo: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="To"
        />

        {/* Confidence Range */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Confidence:</span>
          <input
            type="number"
            min="0"
            max="100"
            value={filters.confidenceMin || ''}
            onChange={(e) => onFilterChange({ ...filters, confidenceMin: e.target.value ? Number(e.target.value) : undefined })}
            className="w-16 px-2 py-2 border border-gray-300 rounded-lg text-sm"
            placeholder="Min"
          />
          <span className="text-gray-400">-</span>
          <input
            type="number"
            min="0"
            max="100"
            value={filters.confidenceMax || ''}
            onChange={(e) => onFilterChange({ ...filters, confidenceMax: e.target.value ? Number(e.target.value) : undefined })}
            className="w-16 px-2 py-2 border border-gray-300 rounded-lg text-sm"
            placeholder="Max"
          />
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="ml-auto flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>
    </div>
  );
}

// Toast notification component
interface Toast {
  id: string;
  type: 'success' | 'error';
  message: string;
}

function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: string) => void }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          {toast.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertTriangle className="w-5 h-5" />
          )}
          <span className="font-medium">{toast.message}</span>
          <button onClick={() => onDismiss(toast.id)} className="ml-2">
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}

export function TieredDashboard() {
  const [filters, setFilters] = useState<ApprovalFilters>({});
  const [activeView, setActiveView] = useState<'dashboard' | 'tier2' | 'tier3' | 'tier1'>('dashboard');
  const [selectedCard, setSelectedCard] = useState<ApprovalCard | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [batchMode, setBatchMode] = useState(false);
  const [selectedCardIds, setSelectedCardIds] = useState<string[]>([]);

  const { data: dashboardData, isLoading: dashboardLoading, refetch } = useApprovalDashboard(filters);
  const { data: metrics, isLoading: metricsLoading } = useApprovalMetrics();

  // Calculate counts per tier
  const tierCounts = {
    1: dashboardData?.cards.filter(c => c.classification.tier === 1 && c.status === 'PENDING').length || 0,
    2: dashboardData?.cards.filter(c => c.classification.tier === 2 && c.status === 'PENDING').length || 0,
    3: dashboardData?.cards.filter(c => c.classification.tier === 3 && c.status === 'PENDING').length || 0,
  };

  const addToast = (type: 'success' | 'error', message: string) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
  };

  const handleAction = (action: string, card?: ApprovalCard) => {
    const companyName = card?.companyName || 'Card';
    switch (action) {
      case 'approve':
        addToast('success', `${companyName} approved`);
        break;
      case 'reject':
        addToast('success', `${companyName} rejected`);
        break;
      case 'escalate':
        addToast('success', `${companyName} escalated to Tier 3`);
        break;
      case 'flag':
        addToast('success', `${companyName} flagged for review`);
        break;
      case 'error':
        addToast('error', 'Action failed. Please try again.');
        break;
    }
    refetch();
  };

  const handleBatchSelect = (cardId: string, selected: boolean) => {
    setSelectedCardIds(prev => 
      selected ? [...prev, cardId] : prev.filter(id => id !== cardId)
    );
  };

  const handleBatchAction = (action: 'approve' | 'export') => {
    if (action === 'approve') {
      addToast('success', `${selectedCardIds.length} cards approved`);
    } else {
      addToast('success', `${selectedCardIds.length} cards exported`);
    }
    setSelectedCardIds([]);
    setBatchMode(false);
    refetch();
  };

  // Keyboard shortcut handler
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === '?') {
      e.preventDefault();
      setShowHelp(true);
    }
  };

  // Render appropriate view
  if (activeView === 'tier2') {
    return (
      <Tier2QuickReview
        onClose={() => setActiveView('dashboard')}
        onAction={handleAction}
        batchMode={batchMode}
        onBatchSelect={handleBatchSelect}
        selectedIds={selectedCardIds}
      />
    );
  }

  if (activeView === 'tier3') {
    return (
      <Tier3DeepReview
        onClose={() => setActiveView('dashboard')}
        onAction={handleAction}
      />
    );
  }

  if (activeView === 'tier1') {
    return (
      <Tier1AutoLog
        onClose={() => setActiveView('dashboard')}
        onAction={handleAction}
        onFlag={(card) => handleAction('flag', card)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" onKeyDown={handleKeyDown}>
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Tiered Approval Dashboard</h1>
                <p className="text-sm text-gray-500">Review and approve cards efficiently</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setBatchMode(!batchMode)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  batchMode ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Layers className="w-4 h-4" />
                Batch Mode
              </button>
              <button
                onClick={() => setShowHelp(true)}
                className="flex items-center gap-2 px-3 py-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
              >
                <HelpCircle className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Metrics Bar */}
        <MetricsBar metrics={metrics} isLoading={metricsLoading} />

        {/* Filters */}
        <FiltersBar
          filters={filters}
          onFilterChange={setFilters}
          onRefresh={refetch}
        />

        {/* Three Column Layout */}
        {dashboardLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-96 bg-gray-200 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <TierColumn
              tier={1}
              count={tierCounts[1]}
              onViewLog={() => setActiveView('tier1')}
              recentActivity={metrics?.recentActivity.filter(a => a.tier === 1)}
            />
            <TierColumn
              tier={2}
              count={tierCounts[2]}
              onStartReview={() => setActiveView('tier2')}
              recentActivity={metrics?.recentActivity.filter(a => a.tier === 2)}
            />
            <TierColumn
              tier={3}
              count={tierCounts[3]}
              onStartReview={() => setActiveView('tier3')}
              recentActivity={metrics?.recentActivity.filter(a => a.tier === 3)}
            />
          </div>
        )}

        {/* Batch Actions Bar */}
        {batchMode && (
          <BatchActions
            selectedCount={selectedCardIds.length}
            onClear={() => setSelectedCardIds([])}
            onApprove={() => handleBatchAction('approve')}
            onExport={() => handleBatchAction('export')}
          />
        )}
      </main>

      {/* Card Detail Modal */}
      {selectedCard && (
        <CardDetail
          card={selectedCard}
          onClose={() => setSelectedCard(null)}
          onAction={(action) => handleAction(action, selectedCard)}
        />
      )}

      {/* Keyboard Shortcuts Help */}
      {showHelp && <KeyboardShortcutsHelp onClose={() => setShowHelp(false)} />}

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={(id) => setToasts(prev => prev.filter(t => t.id !== id))} />
    </div>
  );
}

export default TieredDashboard;
