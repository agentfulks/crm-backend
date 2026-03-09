import { useState, useEffect } from 'react';
import { X, Tag, Calendar, Flag, Trash2 } from 'lucide-react';
import type { KanbanCard, KanbanColumn, Priority } from '../types';
import { useCreateKanbanCard, useUpdateKanbanCard, useDeleteKanbanCard } from '../hooks/useKanban';

const COLUMNS: { value: KanbanColumn; label: string }[] = [
  { value: 'backlog', label: 'Backlog' },
  { value: 'todo', label: 'Todo' },
  { value: 'doing', label: 'Doing' },
  { value: 'review', label: 'Review' },
  { value: 'complete', label: 'Complete' },
];

const PRIORITY_COLORS: Record<string, string> = {
  A: 'bg-red-100 text-red-700 border-red-300',
  B: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  C: 'bg-gray-100 text-gray-600 border-gray-300',
};

interface KanbanCardModalProps {
  /** Pass an existing card to edit, or undefined to create */
  card?: KanbanCard;
  /** Default column when creating */
  defaultColumn?: KanbanColumn;
  onClose: () => void;
}

export function KanbanCardModal({ card, defaultColumn = 'backlog', onClose }: KanbanCardModalProps) {
  const isEdit = !!card;

  const [title, setTitle] = useState(card?.title ?? '');
  const [description, setDescription] = useState(card?.description ?? '');
  const [column, setColumn] = useState<KanbanColumn>(card?.column ?? defaultColumn);
  const [priority, setPriority] = useState<string>(card?.priority ?? '');
  const [dueDate, setDueDate] = useState(card?.due_date ? card.due_date.slice(0, 10) : '');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>(card?.tags ?? []);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const createCard = useCreateKanbanCard();
  const updateCard = useUpdateKanbanCard();
  const deleteCard = useDeleteKanbanCard();

  const isPending = createCard.isPending || updateCard.isPending || deleteCard.isPending;

  const addTag = () => {
    const t = tagInput.trim();
    if (t && !tags.includes(t)) setTags([...tags, t]);
    setTagInput('');
  };

  const removeTag = (t: string) => setTags(tags.filter((x) => x !== t));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const payload = {
      title: title.trim(),
      description: description.trim() || undefined,
      column,
      priority: priority || undefined,
      due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      tags,
    };

    if (isEdit) {
      await updateCard.mutateAsync({ id: card!.id, data: payload });
    } else {
      await createCard.mutateAsync({ ...payload, card_type: 'custom' });
    }
    onClose();
  };

  const handleDelete = async () => {
    await deleteCard.mutateAsync(card!.id);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-lg shadow-xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEdit ? 'Edit Task' : 'New Task'}
          </h2>
          <div className="flex items-center gap-2">
            {isEdit && (
              confirmDelete ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-red-600">Delete?</span>
                  <button
                    onClick={handleDelete}
                    disabled={isPending}
                    className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                  >
                    Yes
                  </button>
                  <button
                    onClick={() => setConfirmDelete(false)}
                    className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                  >
                    No
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete card"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )
            )}
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-500">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-auto p-5 space-y-4">
          {/* Source data badge (read-only) */}
          {card?.card_type && card.card_type !== 'custom' && card.source_data && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
              <span className="font-semibold capitalize">{card.card_type}:</span>{' '}
              {card.source_data.name || card.source_data.title || card.source_data.full_name || '—'}
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What needs to be done?"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional notes or details..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
            />
          </div>

          {/* Column + Priority row */}
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Column
              </label>
              <select
                value={column}
                onChange={(e) => setColumn(e.target.value as KanbanColumn)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
              >
                {COLUMNS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Priority
              </label>
              <div className="flex gap-1">
                {['', 'A', 'B', 'C'].map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPriority(p)}
                    className={`px-3 py-2 rounded-lg text-xs font-semibold border transition-colors ${
                      priority === p
                        ? p === 'A' ? 'bg-red-500 text-white border-red-500'
                          : p === 'B' ? 'bg-yellow-500 text-white border-yellow-500'
                          : p === 'C' ? 'bg-gray-500 text-white border-gray-500'
                          : 'bg-gray-200 text-gray-700 border-gray-300'
                        : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {p || '—'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" /> Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5 flex items-center gap-1">
              <Tag className="w-3.5 h-3.5" /> Tags
            </label>
            <div className="flex gap-2 mb-2 flex-wrap">
              {tags.map((t) => (
                <span
                  key={t}
                  className="inline-flex items-center gap-1 bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full"
                >
                  {t}
                  <button type="button" onClick={() => removeTag(t)} className="hover:text-red-600">×</button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addTag(); } }}
                placeholder="Add a tag..."
                className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={addTag}
                className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
              >
                Add
              </button>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="p-5 border-t flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit as any}
            disabled={isPending || !title.trim()}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Task'}
          </button>
        </div>
      </div>
    </div>
  );
}
