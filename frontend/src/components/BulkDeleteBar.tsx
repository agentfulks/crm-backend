import { Trash2, X, CheckSquare } from 'lucide-react';

interface Props {
  count: number;
  total: number;
  onSelectAll: () => void;
  onClearAll: () => void;
  onDelete: () => void;
  deleting?: boolean;
}

export function BulkDeleteBar({ count, total, onSelectAll, onClearAll, onDelete, deleting }: Props) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 bg-gray-900 text-white rounded-2xl shadow-2xl border border-gray-700">
      <button
        onClick={count === total ? onClearAll : onSelectAll}
        className="flex items-center gap-1.5 text-sm text-gray-300 hover:text-white transition-colors"
      >
        <CheckSquare className="w-4 h-4" />
        {count === total ? 'Deselect all' : 'Select all'}
      </button>

      <div className="w-px h-5 bg-gray-600" />

      <span className="text-sm font-semibold text-white">
        {count} selected
      </span>

      <div className="w-px h-5 bg-gray-600" />

      <button
        onClick={onClearAll}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <X className="w-3.5 h-3.5" />
        Cancel
      </button>

      <button
        onClick={onDelete}
        disabled={count === 0 || deleting}
        className="flex items-center gap-2 px-4 py-1.5 bg-red-600 hover:bg-red-700 disabled:bg-red-900 disabled:text-red-400 text-white text-sm font-semibold rounded-xl transition-colors"
      >
        <Trash2 className="w-4 h-4" />
        {deleting ? 'Deleting…' : `Delete ${count > 0 ? count : ''}`}
      </button>
    </div>
  );
}
