import React from 'react';
import { Play, Pause, CheckCircle, AlertCircle, Lock, Calendar, ChevronRight } from 'lucide-react';
import type { PipelineDay, BatchStatus, PipelineOverviewProps } from '../../types/dashboard';

const statusConfig: Record<BatchStatus, { color: string; bgColor: string; icon: React.ReactNode; label: string }> = {
  READY: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
    icon: <Play className="w-5 h-5" />,
    label: 'Ready',
  },
  BLOCKED: {
    color: 'text-amber-600',
    bgColor: 'bg-amber-50 border-amber-200',
    icon: <Lock className="w-5 h-5" />,
    label: 'Blocked',
  },
  IN_PROGRESS: {
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
    icon: <Pause className="w-5 h-5" />,
    label: 'In Progress',
  },
  COMPLETE: {
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200',
    icon: <CheckCircle className="w-5 h-5" />,
    label: 'Complete',
  },
};

function PipelineDayCard({ day, isSelected, onClick }: { day: PipelineDay; isSelected: boolean; onClick: () => void }) {
  const config = statusConfig[day.status];
  const progressPercent = (day.sentCount / day.totalFunds) * 100;
  
  return (
    <button
      onClick={onClick}
      className={`relative w-full text-left rounded-xl border-2 p-4 transition-all duration-200 hover:shadow-lg ${
        isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
      } ${day.status === 'BLOCKED' ? 'bg-amber-50/50' : 'bg-white'}`}
    >
      {/* Day Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900">Day {day.dayNumber}</span>
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </span>
        </div>
        <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
      </div>
      
      {/* Status Badge */}
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium mb-3 ${config.bgColor} ${config.color}`}>
        {config.icon}
        {config.label}
      </div>
      
      {/* Fund Count */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl font-bold text-gray-900">{day.totalFunds}</span>
        <span className="text-xs text-gray-500">funds</span>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            day.status === 'COMPLETE' ? 'bg-green-500' : 'bg-blue-500'
          }`}
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      
      {/* Progress Text */}
      <p className="text-xs text-gray-500">
        {day.sentCount} of {day.totalFunds} sent
      </p>
      
      {/* Blocked Warning */}
      {day.status === 'BLOCKED' && day.blockedReason && (
        <div className="mt-3 flex items-start gap-1.5 text-amber-700 text-xs">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
          <span>{day.blockedReason}</span>
        </div>
      )}
    </button>
  );
}

export function PipelineOverview({ days, onDayClick, selectedDay }: PipelineOverviewProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Outreach Pipeline</h2>
          <p className="text-sm text-gray-500 mt-0.5">5-day batch schedule</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            Blocked
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            Ready
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-purple-500" />
            In Progress
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            Complete
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-5 gap-4">
        {days.map((day) => (
          <PipelineDayCard
            key={day.dayNumber}
            day={day}
            isSelected={selectedDay === day.dayNumber}
            onClick={() => onDayClick(day.dayNumber)}
          />
        ))}
      </div>
    </div>
  );
}

export default PipelineOverview;
