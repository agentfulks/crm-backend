import { 
  Users, Send, MessageCircle, Calendar, 
  TrendingUp, Minus 
} from 'lucide-react';
import type { MetricsCardsProps } from '../../types/dashboard';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color: 'blue' | 'green' | 'purple' | 'amber' | 'gray';
  isEmpty?: boolean;
}

const colorConfig: Record<string, { bg: string; iconBg: string; iconColor: string }> = {
  blue: {
    bg: 'bg-blue-50',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
  },
  purple: {
    bg: 'bg-purple-50',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
  },
  amber: {
    bg: 'bg-amber-50',
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
  },
  gray: {
    bg: 'bg-gray-50',
    iconBg: 'bg-gray-100',
    iconColor: 'text-gray-600',
  },
};

function MetricCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  trendValue, 
  color,
  isEmpty 
}: MetricCardProps) {
  const colors = colorConfig[color];
  
  return (
    <div className={`rounded-xl border border-gray-200 p-5 ${colors.bg}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {isEmpty ? (
              <span className="text-gray-400 flex items-center gap-2">
                <Minus className="w-6 h-6" />
                N/A
              </span>
            ) : (
              value
            )}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          
          {/* Trend Indicator */}
          {trend && trendValue && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${
              trend === 'up' ? 'text-green-600' : 
              trend === 'down' ? 'text-red-600' : 
              'text-gray-500'
            }`}>
              {trend === 'up' && <TrendingUp className="w-4 h-4" />}
              {trend === 'down' && <TrendingUp className="w-4 h-4 rotate-180" />}
              {trend === 'neutral' && <Minus className="w-4 h-4" />}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        
        <div className={`p-3 rounded-lg ${colors.iconBg}`}>
          <span className={colors.iconColor}>{icon}</span>
        </div>
      </div>
    </div>
  );
}

export function MetricsCards({ metrics }: MetricsCardsProps) {
  // Calculate derived metrics
  const pendingCount = 
    (metrics.fundsByStatus['AWAITING_APPROVAL'] || 0) +
    (metrics.fundsByStatus['QUEUED'] || 0);
  
  const approvedCount = metrics.fundsByStatus['APPROVED'] || 0;
  const sentCount = metrics.fundsByStatus['SENT'] || 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Funds in Pipeline */}
      <MetricCard
        title="Total Funds in Pipeline"
        value={metrics.totalFundsInPipeline}
        subtitle={`${pendingCount} pending, ${approvedCount} approved`}
        icon={<Users className="w-6 h-6" />}
        color="blue"
        trend="neutral"
        trendValue="25 target funds"
      />
      
      {/* Funds Sent This Week */}
      <MetricCard
        title="Funds Sent This Week"
        value={metrics.fundsSentThisWeek}
        subtitle={metrics.fundsSentThisWeek === 0 ? "Pending Day 1 sends" : `${sentCount} total sent`}
        icon={<Send className="w-6 h-6" />}
        color={metrics.fundsSentThisWeek === 0 ? "amber" : "green"}
        isEmpty={metrics.fundsSentThisWeek === 0}
      />
      
      {/* Response Rate */}
      <MetricCard
        title="Response Rate"
        value={metrics.responseRate !== null ? `${metrics.responseRate}%` : 'N/A'}
        subtitle={metrics.responseRate === null ? "No sends yet" : "Industry avg: 15-20%"}
        icon={<MessageCircle className="w-6 h-6" />}
        color={metrics.responseRate === null ? "gray" : "purple"}
        isEmpty={metrics.responseRate === null}
      />
      
      {/* Follow-ups Scheduled */}
      <MetricCard
        title="Follow-ups Scheduled"
        value={metrics.followUpsScheduled}
        subtitle={metrics.followUpsScheduled === 0 ? "None scheduled" : "Next 7 days"}
        icon={<Calendar className="w-6 h-6" />}
        color={metrics.followUpsScheduled === 0 ? "gray" : "green"}
        isEmpty={metrics.followUpsScheduled === 0}
      />
    </div>
  );
}

// Extended version with additional details
export function MetricsCardsDetailed({ metrics }: MetricsCardsProps) {
  return (
    <div className="space-y-4">
      <MetricsCards metrics={metrics} />
      
      {/* Status Breakdown */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Status Breakdown</h3>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {(['QUEUED', 'AWAITING_APPROVAL', 'APPROVED', 'SENT', 'FOLLOW_UP', 'CLOSED'] as const).map((status) => {
            const count = metrics.fundsByStatus[status] || 0;
            const statusLabels: Record<string, string> = {
              QUEUED: 'Queued',
              AWAITING_APPROVAL: 'Awaiting Approval',
              APPROVED: 'Approved',
              SENT: 'Sent',
              FOLLOW_UP: 'Follow-up',
              CLOSED: 'Closed',
            };
            
            return (
              <div key={status} className="text-center">
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-xs text-gray-500 mt-1">{statusLabels[status]}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default MetricsCards;
