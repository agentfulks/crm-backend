/**
 * Quick modal to add a VC packet, studio, or contact as a Kanban card.
 * Does NOT remove them from their original tab — it just creates a linked copy.
 */
import { useState } from 'react';
import { X, ClipboardCheck } from 'lucide-react';
import type { KanbanColumn } from '../types';
import { useCreateKanbanCard } from '../hooks/useKanban';

const COLUMNS: { value: KanbanColumn; label: string }[] = [
  { value: 'backlog', label: 'Backlog' },
  { value: 'todo',    label: 'To Do'   },
  { value: 'doing',   label: 'Doing'   },
  { value: 'review',  label: 'Review'  },
  { value: 'complete',label: 'Complete'},
];

export interface AddToKanbanSource {
  /** Type of the source entity */
  type: 'vc' | 'studio' | 'contact';
  /** Source entity's id */
  id: string;
  /** Human-readable card title */
  title: string;
  /** Snapshot data to embed in the kanban card */
  data: Record<string, any>;
}

interface AddToKanbanModalProps {
  source: AddToKanbanSource;
  onClose: () => void;
  onAdded?: () => void;
}

export function AddToKanbanModal({ source, onClose, onAdded }: AddToKanbanModalProps) {
  const [column, setColumn] = useState<KanbanColumn>('backlog');
  const [note, setNote] = useState('');
  const [added, setAdded] = useState(false);

  const createCard = useCreateKanbanCard();

  const handleAdd = async () => {
    await createCard.mutateAsync({
      title: source.title,
      description: note.trim() || undefined,
      column,
      card_type: source.type,
      source_id: source.id,
      source_data: source.data,
    });
    setAdded(true);
    setTimeout(() => {
      onAdded?.();
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[60]">
      <div className="bg-white rounded-xl w-full max-w-sm shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-gray-900">Add to Tasks</h2>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-500">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 space-y-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Adding</p>
            <p className="text-sm font-semibold text-gray-900 truncate">{source.title}</p>
            <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 capitalize">
              {source.type}
            </span>
          </div>

          {/* Column picker */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
              Add to column
            </label>
            <div className="flex flex-wrap gap-2">
              {COLUMNS.map((c) => (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => setColumn(c.value)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    column === c.value
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400 hover:text-indigo-600'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Optional note */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
              Note (optional)
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Add context or next steps..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={handleAdd}
            disabled={createCard.isPending || added}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {added ? '✓ Added!' : createCard.isPending ? 'Adding…' : 'Add to Tasks'}
          </button>
        </div>
      </div>
    </div>
  );
}
