import { useState } from 'react';
import type { StudioPacket, PacketStatus } from '../types';
import { Globe, Linkedin, Flag, Building2, ClipboardCheck } from 'lucide-react';
import { useUpdateCompany } from '../hooks/useStudioPackets';
import { AddToKanbanModal } from './AddToKanbanModal';

interface StudioCardProps {
  packet: StudioPacket;
  onClick?: () => void;
  selected?: boolean;
  onToggle?: (e: React.MouseEvent) => void;
}

const statusColors: Record<PacketStatus, string> = {
  NEW: 'bg-gray-100 text-gray-700',
  QUEUED: 'bg-gray-100 text-gray-800',
  AWAITING_APPROVAL: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  SENT: 'bg-blue-100 text-blue-800',
  FOLLOW_UP: 'bg-purple-100 text-purple-800',
  CLOSED: 'bg-red-100 text-red-800',
};

const priorityColors: Record<string, string> = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-500 text-white',
  C: 'bg-gray-400 text-white',
};

export function StudioCard({ packet, onClick, selected, onToggle }: StudioCardProps) {
  const studio = packet.studio;
  const updateCompany = useUpdateCompany();
  const isFlagged = studio?.is_flagged ?? false;
  const [showKanban, setShowKanban] = useState(false);

  const handleFlag = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!studio?.id) return;
    updateCompany.mutate({ id: studio.id, data: { is_flagged: !isFlagged } });
  };

  return (
    <>
      <div
        onClick={onToggle ?? onClick}
        className={`rounded-lg shadow-sm border p-4 hover:shadow-md transition-all cursor-pointer flex flex-col relative ${
          selected
            ? 'ring-2 ring-blue-500 border-blue-400 bg-blue-50'
            : isFlagged
            ? 'bg-red-50 border-red-300 hover:border-red-400'
            : 'bg-white border-gray-200 hover:border-blue-300'
        }`}
      >
        {onToggle && (
          <div className="absolute top-2 left-2 z-10">
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              selected ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-400'
            }`}>
              {selected && <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
            </div>
          </div>
        )}
        {/* Top row: priority + status + flag */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-bold px-2 py-0.5 rounded ${priorityColors[packet.priority] || priorityColors.C}`}>
              {packet.priority}
            </span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${statusColors[packet.status]}`}>
              {packet.status.replace(/_/g, ' ')}
            </span>
            {studio?.icp_score != null && (
              <span className="text-xs text-gray-500 font-medium">Score: {studio.icp_score}</span>
            )}
          </div>
          <button
            onClick={handleFlag}
            title={isFlagged ? 'Remove flag' : 'Flag as bad data'}
            className={`p-1 rounded transition-colors ${
              isFlagged ? 'text-red-500 hover:text-red-700' : 'text-gray-300 hover:text-red-400'
            }`}
          >
            <Flag className="w-4 h-4" fill={isFlagged ? 'currentColor' : 'none'} />
          </button>
        </div>

        {/* Studio name + type */}
        <div className="flex items-start gap-3 mb-2">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${isFlagged ? 'bg-red-100' : 'bg-blue-50'}`}>
            <Building2 className={`w-5 h-5 ${isFlagged ? 'text-red-500' : 'text-blue-500'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">{studio?.name || 'Unknown Studio'}</h3>
            {studio?.studio_type && (
              <p className="text-xs text-gray-500 mt-0.5">{studio.studio_type}</p>
            )}
          </div>
        </div>

        {/* Overview */}
        {studio?.overview && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">{studio.overview}</p>
        )}

        {/* Location + size */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 mb-3">
          {studio?.hq_city && (
            <span>{studio.hq_city}{studio.hq_region ? `, ${studio.hq_region}` : ''}{studio.hq_country ? ` · ${studio.hq_country}` : ''}</span>
          )}
          {studio?.employee_count && (
            <span>{studio.employee_count} employees</span>
          )}
        </div>

        {/* Links + Add to Tasks */}
        <div className="flex items-center gap-3 mt-auto pt-3 border-t border-gray-100">
          <div className="flex gap-3 flex-1 min-w-0">
            {studio?.website_url && (
              <a
                href={studio.website_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate"
              >
                <Globe className="w-3 h-3 flex-shrink-0" />
                <span className="truncate">{studio.website_url.replace(/^https?:\/\//, '')}</span>
              </a>
            )}
            {studio?.linkedin_url && (
              <a
                href={studio.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 flex-shrink-0"
              >
                <Linkedin className="w-3 h-3" />
                LinkedIn
              </a>
            )}
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); setShowKanban(true); }}
            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-2 py-1 rounded-lg transition-colors flex-shrink-0"
            title="Add to Tasks board"
          >
            <ClipboardCheck className="w-3.5 h-3.5" />
            Tasks
          </button>
        </div>
      </div>

      {showKanban && studio && (
        <AddToKanbanModal
          source={{
            type: 'studio',
            id: studio.id,
            title: studio.name || 'Unknown Studio',
            data: {
              name: studio.name,
              studio_type: studio.studio_type,
              hq_city: studio.hq_city,
              hq_country: studio.hq_country,
              website_url: studio.website_url,
              priority: packet.priority,
              status: packet.status,
              icp_score: studio.icp_score,
            },
          }}
          onClose={() => setShowKanban(false)}
        />
      )}
    </>
  );
}
