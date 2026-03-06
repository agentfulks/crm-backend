import { X, Keyboard } from 'lucide-react';
import { KEYBOARD_SHORTCUTS } from '../../types/approval';

interface KeyboardShortcutsHelpProps {
  onClose: () => void;
}

export function KeyboardShortcutsHelp({ onClose }: KeyboardShortcutsHelpProps) {
  const globalShortcuts = KEYBOARD_SHORTCUTS.filter(s => s.context === 'global');
  const reviewShortcuts = KEYBOARD_SHORTCUTS.filter(s => s.context === 'review');
  const listShortcuts = KEYBOARD_SHORTCUTS.filter(s => s.context === 'list');

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Keyboard className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold">Keyboard Shortcuts</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Review Shortcuts */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              During Review
            </h4>
            <div className="space-y-2">
              {reviewShortcuts.map((shortcut) => (
                <div key={shortcut.key} className="flex items-center justify-between">
                  <span className="text-gray-700">{shortcut.description}</span>
                  <kbd className="px-3 py-1 bg-gray-100 text-gray-700 font-mono text-sm rounded">
                    {shortcut.key.toUpperCase()}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          {/* List Navigation */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Navigation
            </h4>
            <div className="space-y-2">
              {listShortcuts.map((shortcut) => (
                <div key={shortcut.key} className="flex items-center justify-between">
                  <span className="text-gray-700">{shortcut.description}</span>
                  <kbd className="px-3 py-1 bg-gray-100 text-gray-700 font-mono text-sm rounded">
                    {shortcut.key.toUpperCase()}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          {/* Global Shortcuts */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Global
            </h4>
            <div className="space-y-2">
              {globalShortcuts.map((shortcut) => (
                <div key={shortcut.key} className="flex items-center justify-between">
                  <span className="text-gray-700">{shortcut.description}</span>
                  <kbd className="px-3 py-1 bg-gray-100 text-gray-700 font-mono text-sm rounded">
                    {shortcut.key === '?' ? '?' : shortcut.key.toUpperCase()}
                  </kbd>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <p className="text-sm text-gray-500 text-center">
            Press <kbd className="px-2 py-0.5 bg-white border rounded">?</kbd> anytime to show this help
          </p>
        </div>
      </div>
    </div>
  );
}
