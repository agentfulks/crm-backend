import { useState, useRef } from 'react';
import {
  Plus, ChevronLeft, ChevronRight, Building2, Users, UserCircle, Pencil,
  Calendar, Tag, Globe, Linkedin, Twitter, Mail, MapPin,
  DollarSign, Star, GripVertical,
} from 'lucide-react';
import type { KanbanCard, KanbanColumn } from '../types';
import { useKanbanCards, useUpdateKanbanCard } from '../hooks/useKanban';
import { KanbanCardModal } from './KanbanCardModal';
import { KanbanSourceModal } from './KanbanSourceModal';

// ── Column config ─────────────────────────────────────────────────────────────

const COLUMNS: { id: KanbanColumn; label: string; color: string; headerBg: string; dropBg: string }[] = [
  { id: 'backlog',  label: 'Backlog',  color: 'border-gray-300',   headerBg: 'bg-gray-100',   dropBg: 'bg-gray-50'     },
  { id: 'todo',    label: 'To Do',    color: 'border-blue-300',   headerBg: 'bg-blue-50',    dropBg: 'bg-blue-50/80'  },
  { id: 'doing',   label: 'Doing',    color: 'border-yellow-300', headerBg: 'bg-yellow-50',  dropBg: 'bg-yellow-50/80'},
  { id: 'review',  label: 'Review',   color: 'border-purple-300', headerBg: 'bg-purple-50',  dropBg: 'bg-purple-50/80'},
  { id: 'complete',label: 'Complete', color: 'border-green-300',  headerBg: 'bg-green-50',   dropBg: 'bg-green-50/80' },
];

const COLUMN_IDS = COLUMNS.map((c) => c.id);

const PRIORITY_BADGE: Record<string, string> = {
  A: 'bg-red-500 text-white',
  B: 'bg-yellow-500 text-white',
  C: 'bg-gray-400 text-white',
};

const STATUS_COLORS: Record<string, string> = {
  NEW:              'bg-gray-100 text-gray-700',
  RESEARCHING:      'bg-blue-100 text-blue-700',
  READY:            'bg-teal-100 text-teal-700',
  APPROVED:         'bg-green-100 text-green-800',
  SENT:             'bg-indigo-100 text-indigo-700',
  FOLLOW_UP:        'bg-purple-100 text-purple-700',
  CLOSED:           'bg-red-100 text-red-700',
  QUEUED:           'bg-gray-100 text-gray-800',
  AWAITING_APPROVAL:'bg-yellow-100 text-yellow-800',
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatDue(iso?: string) {
  if (!iso) return null;
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((d.getTime() - now.getTime()) / 86400000);
  if (diff < 0) return { label: `${Math.abs(diff)}d overdue`, overdue: true };
  if (diff === 0) return { label: 'Due today', overdue: false };
  return { label: `Due in ${diff}d`, overdue: false };
}

// ── Source-card rich content ──────────────────────────────────────────────────

/** Mini VC-fund card body rendered from stored source_data snapshot */
function VcContent({ data, priority, status }: { data: Record<string, any>; priority?: string; status?: string }) {
  return (
    <div className="space-y-2">
      {/* Priority + status row */}
      <div className="flex items-center gap-2 flex-wrap">
        {priority && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded ${PRIORITY_BADGE[priority] || PRIORITY_BADGE.C}`}>
            {priority}
          </span>
        )}
        {(data.status || status) && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded ${STATUS_COLORS[data.status || status] || STATUS_COLORS.NEW}`}>
            {(data.status || status || '').replace(/_/g, ' ')}
          </span>
        )}
        {data.score != null && (
          <span className="text-xs text-gray-500">Score: {data.score}</span>
        )}
      </div>

      {/* Name + firm type */}
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
          <Users className="w-4 h-4 text-blue-500" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 text-sm leading-tight truncate">{data.name}</p>
          {data.firm_type && <p className="text-xs text-gray-500">{data.firm_type}</p>}
        </div>
      </div>

      {/* Location + check size */}
      <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-gray-500">
        {data.hq_city && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {data.hq_city}{data.hq_country ? ` · ${data.hq_country}` : ''}
          </span>
        )}
        {data.check_size && (
          <span className="flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            {data.check_size}
          </span>
        )}
      </div>

      {/* Contact email */}
      {data.contact_email && (
        <a
          href={`mailto:${data.contact_email}`}
          onClick={(e) => e.stopPropagation()}
          className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate"
        >
          <Mail className="w-3 h-3 flex-shrink-0" />
          <span className="truncate">{data.contact_email}</span>
        </a>
      )}

      {/* Links */}
      <div className="flex gap-3 flex-wrap">
        {data.website_url && (
          <a
            href={data.website_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate max-w-[120px]"
          >
            <Globe className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{data.website_url.replace(/^https?:\/\//, '').split('/')[0]}</span>
          </a>
        )}
        {data.linkedin_url && (
          <a
            href={data.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            <Linkedin className="w-3 h-3" />
            LinkedIn
          </a>
        )}
        {data.twitter_url && (
          <a
            href={data.twitter_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            <Twitter className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
}

/** Mini Studio card body rendered from stored source_data snapshot */
function StudioContent({ data, priority }: { data: Record<string, any>; priority?: string }) {
  return (
    <div className="space-y-2">
      {/* Priority + status */}
      <div className="flex items-center gap-2 flex-wrap">
        {priority && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded ${PRIORITY_BADGE[priority] || PRIORITY_BADGE.C}`}>
            {priority}
          </span>
        )}
        {data.status && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded ${STATUS_COLORS[data.status] || STATUS_COLORS.NEW}`}>
            {data.status.replace(/_/g, ' ')}
          </span>
        )}
        {data.icp_score != null && (
          <span className="text-xs text-gray-500">Score: {data.icp_score}</span>
        )}
      </div>

      {/* Name + type */}
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center flex-shrink-0">
          <Building2 className="w-4 h-4 text-purple-500" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 text-sm leading-tight truncate">{data.name || 'Unknown Studio'}</p>
          {data.studio_type && <p className="text-xs text-gray-500">{data.studio_type}</p>}
        </div>
      </div>

      {/* Location */}
      {data.hq_city && (
        <p className="text-xs text-gray-500 flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          {data.hq_city}{data.hq_country ? ` · ${data.hq_country}` : ''}
        </p>
      )}

      {/* Links */}
      <div className="flex gap-3 flex-wrap">
        {data.website_url && (
          <a
            href={data.website_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate max-w-[130px]"
          >
            <Globe className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{data.website_url.replace(/^https?:\/\//, '').split('/')[0]}</span>
          </a>
        )}
        {data.linkedin_url && (
          <a
            href={data.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            <Linkedin className="w-3 h-3" />
            LinkedIn
          </a>
        )}
      </div>
    </div>
  );
}

/** Mini Contact card body rendered from stored source_data snapshot */
function ContactContent({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-2">
      {/* Avatar + name */}
      <div className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <span className="font-semibold text-sm text-blue-600">
            {data.full_name?.[0]?.toUpperCase() || '?'}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <p className="font-semibold text-gray-900 text-sm truncate">{data.full_name}</p>
            {data.is_decision_maker && (
              <span className="bg-yellow-100 text-yellow-800 text-xs px-1.5 py-0.5 rounded-full flex items-center gap-0.5 flex-shrink-0">
                <Star className="w-2.5 h-2.5" />
                DM
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 truncate">{data.job_title || 'Unknown Role'}</p>
        </div>
      </div>

      {/* Studio */}
      {data.studio_name && (
        <div className="bg-gray-50 rounded px-2 py-1">
          <p className="text-xs font-medium text-gray-700 truncate">{data.studio_name}</p>
        </div>
      )}

      {/* Contact info */}
      <div className="space-y-1">
        {data.email && (
          <a
            href={`mailto:${data.email}`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 truncate"
          >
            <Mail className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{data.email}</span>
          </a>
        )}
        {data.linkedin_url && (
          <a
            href={data.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            <Linkedin className="w-3 h-3 flex-shrink-0" />
            LinkedIn Profile
          </a>
        )}
      </div>
    </div>
  );
}

// ── Single card tile ──────────────────────────────────────────────────────────

interface CardTileProps {
  card: KanbanCard;
  colIndex: number;
  onEdit: (card: KanbanCard) => void;
  onOpenSource: (card: KanbanCard) => void;
  isDragging: boolean;
  onDragStart: () => void;
  onDragEnd: () => void;
}

function CardTile({ card, colIndex, onEdit, onOpenSource, isDragging, onDragStart, onDragEnd }: CardTileProps) {
  const updateCard = useUpdateKanbanCard();
  const due = formatDue(card.due_date);
  const isSourceCard = card.card_type !== 'custom';

  const moveLeft = async () => {
    const prev = COLUMN_IDS[colIndex - 1];
    if (prev) await updateCard.mutateAsync({ id: card.id, data: { column: prev } });
  };

  const moveRight = async () => {
    const next = COLUMN_IDS[colIndex + 1];
    if (next) await updateCard.mutateAsync({ id: card.id, data: { column: next } });
  };

  return (
    <div
      draggable
      onDragStart={(e) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', card.id);
        // slight delay so the ghost image renders before opacity change
        requestAnimationFrame(onDragStart);
      }}
      onDragEnd={onDragEnd}
      onClick={() => isSourceCard && onOpenSource(card)}
      className={`bg-white rounded-lg border border-gray-200 shadow-sm p-3 transition-all select-none ${
        isDragging
          ? 'opacity-40 scale-95'
          : isSourceCard
          ? 'hover:shadow-md hover:border-blue-300 cursor-pointer'
          : 'hover:shadow-md cursor-grab active:cursor-grabbing'
      }`}
    >
      {/* Top row: type badge + priority + edit */}
      <div className="flex items-start justify-between mb-2 gap-1">
        <div className="flex items-center gap-1 flex-wrap">
          {/* Type badge */}
          {card.card_type === 'vc' && (
            <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700">
              <Users className="w-3 h-3" /> VC
            </span>
          )}
          {card.card_type === 'studio' && (
            <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full font-medium bg-purple-100 text-purple-700">
              <Building2 className="w-3 h-3" /> Studio
            </span>
          )}
          {card.card_type === 'contact' && (
            <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full font-medium bg-green-100 text-green-700">
              <UserCircle className="w-3 h-3" /> Contact
            </span>
          )}
          {card.card_type === 'custom' && card.priority && (
            <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${PRIORITY_BADGE[card.priority]}`}>
              {card.priority}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <GripVertical className="w-3.5 h-3.5 text-gray-300" />
          <button
            onClick={(e) => { e.stopPropagation(); onEdit(card); }}
            className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg z-10 relative"
            title="Edit task"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Rich source content OR plain custom card content */}
      {isSourceCard && card.source_data ? (
        <div className="mb-2">
          {card.card_type === 'vc' && (
            <VcContent data={card.source_data} priority={card.source_data.priority} />
          )}
          {card.card_type === 'studio' && (
            <StudioContent data={card.source_data} priority={card.source_data.priority} />
          )}
          {card.card_type === 'contact' && (
            <ContactContent data={card.source_data} />
          )}
          {/* Note/description below source card */}
          {card.description && (
            <p className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100 italic line-clamp-2">
              {card.description}
            </p>
          )}
        </div>
      ) : (
        <>
          {/* Custom card: title + description */}
          <p className="text-sm font-semibold text-gray-900 leading-snug mb-1 line-clamp-2">{card.title}</p>
          {card.description && (
            <p className="text-xs text-gray-500 mb-2 line-clamp-2">{card.description}</p>
          )}
        </>
      )}

      {/* Due date */}
      {due && (
        <div className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full mb-2 ${
          due.overdue ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
        }`}>
          <Calendar className="w-3 h-3" />
          {due.label}
        </div>
      )}

      {/* Tags */}
      {card.tags && card.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {card.tags.slice(0, 3).map((t) => (
            <span key={t} className="inline-flex items-center gap-0.5 text-xs bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded-full">
              <Tag className="w-2.5 h-2.5" />{t}
            </span>
          ))}
          {card.tags.length > 3 && (
            <span className="text-xs text-gray-400">+{card.tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Move arrows */}
      <div className="flex justify-between mt-2 pt-2 border-t border-gray-100">
        <button
          onClick={(e) => { e.stopPropagation(); moveLeft(); }}
          disabled={colIndex === 0 || updateCard.isPending}
          className="p-1 text-gray-400 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-100 rounded"
          title="Move left"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); moveRight(); }}
          disabled={colIndex === COLUMN_IDS.length - 1 || updateCard.isPending}
          className="p-1 text-gray-400 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-100 rounded"
          title="Move right"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ── Board ─────────────────────────────────────────────────────────────────────

export function KanbanBoard() {
  const { data, isLoading } = useKanbanCards();
  const allCards = data?.items ?? [];
  const updateCard = useUpdateKanbanCard();

  const [editingCard, setEditingCard] = useState<KanbanCard | null>(null);
  const [creatingInColumn, setCreatingInColumn] = useState<KanbanColumn | null>(null);
  const [sourceCard, setSourceCard] = useState<KanbanCard | null>(null);

  // Drag state
  const [draggingCardId, setDraggingCardId] = useState<string | null>(null);
  const [dragOverColId, setDragOverColId] = useState<KanbanColumn | null>(null);
  const dragCounter = useRef<Record<string, number>>({});

  const cardsByColumn = (col: KanbanColumn) =>
    allCards.filter((c) => c.column === col).sort((a, b) => a.position - b.position);

  const handleDrop = async (targetCol: KanbanColumn) => {
    if (!draggingCardId) return;
    const card = allCards.find((c) => c.id === draggingCardId);
    if (card && card.column !== targetCol) {
      await updateCard.mutateAsync({ id: draggingCardId, data: { column: targetCol } });
    }
    setDraggingCardId(null);
    setDragOverColId(null);
    dragCounter.current = {};
  };

  if (isLoading) {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((col) => (
          <div key={col.id} className="flex-shrink-0 w-72 bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
            <div className="h-6 bg-gray-200 rounded mb-4 w-3/4" />
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-100 rounded mb-3" />
            ))}
          </div>
        ))}
      </div>
    );
  }

  return (
    <>
      <div className="flex gap-4 overflow-x-auto pb-6 min-h-[calc(100vh-220px)]">
        {COLUMNS.map((col, colIndex) => {
          const cards = cardsByColumn(col.id);
          const isOver = dragOverColId === col.id && !!draggingCardId;

          return (
            <div
              key={col.id}
              onDragOver={(e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                setDragOverColId(col.id);
              }}
              onDragEnter={(e) => {
                e.preventDefault();
                dragCounter.current[col.id] = (dragCounter.current[col.id] || 0) + 1;
                setDragOverColId(col.id);
              }}
              onDragLeave={() => {
                dragCounter.current[col.id] = (dragCounter.current[col.id] || 1) - 1;
                if (dragCounter.current[col.id] <= 0) {
                  dragCounter.current[col.id] = 0;
                  if (dragOverColId === col.id) setDragOverColId(null);
                }
              }}
              onDrop={(e) => {
                e.preventDefault();
                dragCounter.current[col.id] = 0;
                handleDrop(col.id);
              }}
              className={`flex-shrink-0 w-72 flex flex-col rounded-xl border-2 transition-colors ${col.color} ${
                isOver ? `${col.dropBg} border-dashed` : 'bg-white'
              }`}
            >
              {/* Column header */}
              <div className={`${col.headerBg} rounded-t-xl px-4 py-3 flex items-center justify-between`}>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-800 text-sm">{col.label}</h3>
                  <span className="bg-white/70 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
                    {cards.length}
                  </span>
                </div>
                <button
                  onClick={() => setCreatingInColumn(col.id)}
                  className="p-1 text-gray-500 hover:text-gray-800 hover:bg-white/60 rounded-lg transition-colors"
                  title={`Add card to ${col.label}`}
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>

              {/* Drop hint */}
              {isOver && draggingCardId && (
                <div className="mx-3 mt-3 border-2 border-dashed border-current rounded-lg py-3 text-center text-xs text-gray-400 opacity-60">
                  Drop here
                </div>
              )}

              {/* Cards */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {cards.length === 0 && !isOver ? (
                  <button
                    onClick={() => setCreatingInColumn(col.id)}
                    className="w-full border-2 border-dashed border-gray-200 rounded-lg p-4 text-xs text-gray-400 hover:border-gray-300 hover:text-gray-500 transition-colors"
                  >
                    + Add a task
                  </button>
                ) : (
                  cards.map((card) => (
                    <CardTile
                      key={card.id}
                      card={card}
                      colIndex={colIndex}
                      onEdit={setEditingCard}
                      onOpenSource={setSourceCard}
                      isDragging={draggingCardId === card.id}
                      onDragStart={() => setDraggingCardId(card.id)}
                      onDragEnd={() => {
                        setDraggingCardId(null);
                        setDragOverColId(null);
                        dragCounter.current = {};
                      }}
                    />
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Create modal */}
      {creatingInColumn && (
        <KanbanCardModal
          defaultColumn={creatingInColumn}
          onClose={() => setCreatingInColumn(null)}
        />
      )}

      {/* Edit modal */}
      {editingCard && (
        <KanbanCardModal
          card={editingCard}
          onClose={() => setEditingCard(null)}
        />
      )}

      {/* Source entity detail modal (Contact / Studio / VC) */}
      {sourceCard && (
        <KanbanSourceModal
          card={sourceCard}
          onClose={() => setSourceCard(null)}
        />
      )}
    </>
  );
}
