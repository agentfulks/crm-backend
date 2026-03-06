import { CheckSquare, Square, CheckCircle, Download, Trash2 } from 'lucide-react';

interface BatchActionsProps {
  selectedCount: number;
  onClear: () => void;
  onApprove: () => void;
  onExport: () => void;
}

export function BatchActions({ selectedCount, onClear, onApprove, onExport }: BatchActionsProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-xl border border-blue-200 px-6 py-4 flex items-center gap-6 z-40">
      <div className="flex items-center gap-3">
        <CheckSquare className="w-5 h-5 text-blue-600" />
        <span className="font-medium text-gray-900">
          {selectedCount} card{selectedCount !== 1 ? 's' : ''} selected
        </span>
      </div>

      <div className="h-6 w-px bg-gray-300" />

      <div className="flex items-center gap-2">
        <button
          onClick={onApprove}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          <CheckCircle className="w-4 h-4" />
          Approve All
        </button>
        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
        <button
          onClick={onClear}
          className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 text-sm font-medium rounded-lg hover:bg-red-100 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear
        </button>
      </div>
    </div>
  );
}
