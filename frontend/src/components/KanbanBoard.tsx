import { useState } from 'react';
import { Plus, ChevronLeft, ChevronRight, Building2, Users, UserCircle, Pencil, Calendar, Tag, ClipboardCheck } from 'lucide-react';
import type { KanbanCard, KanbanColumn } from '../types';
import { useKanbanCards, useUpdateKanbanCard } from '../hooks/useKanban';
import { KanbanCardModal } from './KanbanCardModal';

// ── Column config ─────────────────────────────────────────────────────────────

const COLUMNS: { id: KanbanColumn; label: string; color: string; headerBg: string }[] = [
  { id: 'backlog',  label: 'Backlog',  color: 'border-gray-300',   headerBg: 'bg-gray-100'    },
  { id: 'todo',     label: 'To Do',    color: 'border-blue-300',   headerBg: 'bg-blue-50'     },
  { id: 'doing',    label: 'Doing',    color: 'border-yellow-300', headerBg: 'bg-yellow-50'   },
  { id: 'review',   label: 'Review',   color: 'border-purple-300', headerBg: 'bg-purple-50'   },
  { id: 'complete', label: 'Complete', color: 'border-green-300',  headerBg: 'bg-green-50'    },
];

const COLUMN_IDS = COLUMNS.map((c) => c.id);

const PRIORITY_BADGE: Record<string, string> = {
  A: 'bg-red-100 text-red-700',
  B: 'bg-yellow-100 text-yellow-700',
  C: 'bg-gray-100 text-gray-600',
};

const TYPE_ICON: Record<string, React.ReactNode> = {
  vc:      <Users     className="w-3 h-3" />,
  studio:  <Building2 className="w-3 h-3" />,
  contact: <UserCircle className="w-3 h-3" />,
  custom:  <ClipboardCheck className="w-3 h-3" />,
};

const TYPE_COLOR: Record<string, string> = {
  vc:      'bg-blue-100 text-blue-700',
  studio:  'bg-purple-100 text-purple-700',
  contact: 'bg-green-100 text-green-700',
  custom:  'bg-gray-100 text-gray-600',
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

// ── Single card tile ──────────────────────────────────────────────────────────

interface CardTileProps {
  card: KanbanCard;
  colIndex: number;
  onEdit: (card: KanbanCard) => void;
}

function CardTile({ card, colIndex, onEdit }: CardTileProps) {
  const updateCard = useUpdateKanbanCard();
  const due = formatDue(card.due_date);

  const moveLeft = async () => {
    const prev = COLUMN_IDS[colIndex - 1];
    if (prev) await updateCard.mutateAsync({ id: card.id, data: { column: prev } });
  };

  const moveRight = async () => {
    const next = COLUMN_IDS[colIndex + 1];
    if (next) await updateCard.mutateAsync({ id: card.id, data: { column: next } });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-3 hover:shadow-md transition-shadow">
      {/* Top row: type + priority + edit */}
      <div className="flex items-start justify-between mb-2 gap-1">
        <div className="flex items-center gap-1 flex-wrap">
          <span className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full font-medium ${TYPE_COLOR[card.card_type]}`}>
            {TYPE_ICON[card.card_type]}
            <span className="capitalize">{card.card_type}</span>
          </span>
          {card.priority && (
            <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${PRIORITY_BADGE[card.priority]}`}>
              {card.priority}
            </span>
          )}
        </div>
        <button
          onClick={() => onEdit(card)}
          className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg flex-shrink-0"
          title="Edit"
        >
          <Pencil className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Source name (for linked cards) */}
      {card.card_type !== 'custom' && card.source_data && (
        <p className="text-xs text-gray-500 mb-1 truncate">
          {card.source_data.name || card.source_data.full_name || ''}
        </p>
      )}

      {/* Title */}
      <p className="text-sm font-semibold text-gray-900 leading-snug mb-1 line-clamp-2">
        {card.title}
      </p>

      {/* Description snippet */}
      {card.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">{card.description}</p>
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
          onClick={moveLeft}
          disabled={colIndex === 0 || updateCard.isPending}
          className="p-1 text-gray-400 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-100 rounded"
          title="Move left"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <button
          onClick={moveRight}
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

  const [editingCard, setEditingCard] = useState<KanbanCard | null>(null);
  const [creatingInColumn, setCreatingInColumn] = useState<KanbanColumn | null>(null);

  const cardsByColumn = (col: KanbanColumn) =>
    allCards.filter((c) => c.column === col).sort((a, b) => a.position - b.position);

  if (isLoading) {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((col) => (
          <div key={col.id} className="flex-shrink-0 w-64 bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
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
          return (
            <div
              key={col.id}
              className={`flex-shrink-0 w-72 flex flex-col rounded-xl border-2 ${col.color} bg-white`}
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

              {/* Cards */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {cards.length === 0 ? (
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
    </>
  );
}
