import { useState } from 'react';
import { Globe, Linkedin, Twitter, DollarSign, MapPin, ClipboardCheck, Users, Flag } from 'lucide-react';
import type { Fund } from '../types';
import { useUpdateFund } from '../hooks/useFunds';
import { AddToKanbanModal } from './AddToKanbanModal';

interface FundCardProps {
  fund: Fund;
  onClick?: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  NEW:        'bg-gray-100 text-gray-700',
  RESEARCHING:'bg-blue-100 text-blue-700',
  READY:      'bg-teal-100 text-teal-700',
  APPROVED:   'bg-green-100 text-green-800',
  SENT:       'bg-indigo-100 text-indigo-700',
  FOLLOW_UP:  'bg-purple-100 text-purple-700',
  CLOSED:     'bg-red-100 text-red-700',
};

const PRIORITY_COLORS: Record<string, string> = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-500 text-white',
  C: 'bg-gray-400 text-white',
};

function formatCheckSize(min?: number, max?: number, currency?: string): string | null {
  if (!min) return null;
  const c = currency || 'USD';
  const fmt = (n: number) =>
    n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M` : `$${(n / 1_000).toFixed(0)}K`;
  if (max && max !== min) return `${fmt(min)} – ${fmt(max)}`;
  return fmt(min);
}

export function FundCard({ fund, onClick }: FundCardProps) {
  const [showKanban, setShowKanban] = useState(false);
  const updateFund = useUpdateFund();
  const isFlagged = fund.is_flagged ?? false;
  const checkSize = formatCheckSize(fund.check_size_min, fund.check_size_max, fund.check_size_currency);

  const handleFlag = (e: React.MouseEvent) => {
    e.stopPropagation();
    updateFund.mutate({ id: fund.id, data: { is_flagged: !isFlagged } });
  };

  return (
    <>
      <div
        onClick={onClick}
        className={`rounded-lg shadow-sm border p-4 hover:shadow-md transition-all cursor-pointer flex flex-col ${
          isFlagged
            ? 'bg-red-50 border-red-300 hover:border-red-400'
            : 'bg-white border-gray-200 hover:border-blue-300'
        }`}
      >
        {/* Priority + Status + Flag */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-bold px-2 py-0.5 rounded ${PRIORITY_COLORS[fund.priority] || PRIORITY_COLORS.B}`}>
              {fund.priority}
            </span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${STATUS_COLORS[fund.status] || STATUS_COLORS.NEW}`}>
              {fund.status.replace(/_/g, ' ')}
            </span>
            {fund.score != null && (
              <span className="text-xs text-gray-500 font-medium">Score: {fund.score}</span>
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

        {/* Name + firm type */}
        <div className="flex items-start gap-3 mb-2">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${isFlagged ? 'bg-red-100' : 'bg-blue-50'}`}>
            <Users className={`w-5 h-5 ${isFlagged ? 'text-red-500' : 'text-blue-500'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">{fund.name}</h3>
            {fund.firm_type && (
              <p className="text-xs text-gray-500 mt-0.5">{fund.firm_type}</p>
            )}
          </div>
        </div>

        {/* Overview */}
        {fund.overview && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">{fund.overview}</p>
        )}

        {/* Meta: location, check size, stages */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 mb-3">
          {fund.hq_city && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {fund.hq_city}{fund.hq_region ? `, ${fund.hq_region}` : ''}
              {fund.hq_country ? ` · ${fund.hq_country}` : ''}
            </span>
          )}
          {checkSize && (
            <span className="flex items-center gap-1">
              <DollarSign className="w-3 h-3" />
              {checkSize}
            </span>
          )}
          {fund.stage_focus?.length > 0 && (
            <span>{fund.stage_focus.join(', ')}</span>
          )}
        </div>

        {/* Contact email */}
        {fund.contact_email && (
          <div className="text-xs text-blue-600 mb-3 truncate">
            ✉ {fund.contact_email}
          </div>
        )}

        {/* Links + Add to Tasks */}
        <div className="flex items-center gap-3 mt-auto pt-3 border-t border-gray-100">
          <div className="flex gap-3 flex-1 min-w-0">
            {fund.website_url && (
              <a
                href={fund.website_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate"
              >
                <Globe className="w-3 h-3 flex-shrink-0" />
                <span className="truncate">{fund.website_url.replace(/^https?:\/\//, '')}</span>
              </a>
            )}
            {fund.linkedin_url && (
              <a
                href={fund.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 flex-shrink-0"
              >
                <Linkedin className="w-3 h-3" />
                LinkedIn
              </a>
            )}
            {fund.twitter_url && (
              <a
                href={fund.twitter_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 flex-shrink-0"
              >
                <Twitter className="w-3 h-3" />
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

      {showKanban && (
        <AddToKanbanModal
          source={{
            type: 'vc',
            id: fund.id,
            title: fund.name,
            data: {
              name: fund.name,
              firm_type: fund.firm_type,
              hq_city: fund.hq_city,
              hq_country: fund.hq_country,
              website_url: fund.website_url,
              contact_email: fund.contact_email,
              priority: fund.priority,
              status: fund.status,
              score: fund.score,
              check_size: checkSize,
            },
          }}
          onClose={() => setShowKanban(false)}
        />
      )}
    </>
  );
}
