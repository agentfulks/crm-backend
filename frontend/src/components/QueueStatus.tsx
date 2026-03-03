import { useQueueStatus } from '../hooks/usePackets';
import { Clock, CheckCircle, Send, Inbox } from 'lucide-react';

export function QueueStatus() {
  const { data, isLoading } = useQueueStatus();
  
  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }
  
  if (!data) return null;
  
  const stats = [
    { label: 'Queued', value: data.total_queued, icon: Inbox, color: 'bg-gray-50 text-gray-600' },
    { label: 'Awaiting Approval', value: data.awaiting_approval, icon: Clock, color: 'bg-yellow-50 text-yellow-600' },
    { label: 'Approved Today', value: data.approved_today, icon: CheckCircle, color: 'bg-green-50 text-green-600' },
    { label: 'Sent Today', value: data.sent_today, icon: Send, color: 'bg-blue-50 text-blue-600' },
  ];
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${stat.color}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}