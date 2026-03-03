import { useState, useEffect } from 'react';
import { AlertTriangle, Clock, CheckCircle, Info } from 'lucide-react';
import type { DecisionQueueProps, DecisionQueueItem } from '../../types/dashboard';

function CountdownTimer({ deadline }: { deadline: string }) {
  const [timeLeft, setTimeLeft] = useState<string>('');
  const [isOverdue, setIsOverdue] = useState(false);

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const deadlineTime = new Date(deadline).getTime();
      const diff = deadlineTime - now;
      
      if (diff <= 0) {
        setIsOverdue(true);
        setTimeLeft('Overdue');
        return;
      }
      
      setIsOverdue(false);
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (hours > 24) {
        const days = Math.floor(hours / 24);
        setTimeLeft(`${days}d ${hours % 24}h remaining`);
      } else {
        setTimeLeft(`${hours}h ${minutes}m remaining`);
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 60000); // Update every minute
    
    return () => clearInterval(timer);
  }, [deadline]);

  return (
    <span className={`text-xs font-medium ${isOverdue ? 'text-red-600' : 'text-amber-600'}`}>
      <Clock className="w-3 h-3 inline mr-1" />
      {timeLeft}
    </span>
  );
}

function DecisionCard({ 
  item, 
  onDecision, 
  isFirst 
}: { 
  item: DecisionQueueItem; 
  onDecision: (itemId: string, optionId: string) => void;
  isFirst: boolean;
}) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = () => {
    if (selectedOption) {
      onDecision(item.id, selectedOption);
      setIsSubmitted(true);
    }
  };

  if (isSubmitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-green-700">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Decision recorded</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border p-4 ${isFirst ? 'bg-amber-50 border-amber-300' : 'bg-white border-gray-200'}`}>
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className={`p-2 rounded-lg ${isFirst ? 'bg-amber-100' : 'bg-gray-100'}`}>
          <AlertTriangle className={`w-5 h-5 ${isFirst ? 'text-amber-600' : 'text-gray-500'}`} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{item.title}</h3>
          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
          
          {/* Deadline */}
          {item.deadline && (
            <div className="mt-2">
              <CountdownTimer deadline={item.deadline} />
            </div>
          )}
          
          {/* Blocked Since */}
          <p className="text-xs text-gray-400 mt-1">
            Blocked since {new Date(item.blockedSince).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric',
              hour: 'numeric',
              minute: '2-digit'
            })}
          </p>
        </div>
      </div>
      
      {/* Options */}
      <div className="space-y-2 mb-4">
        {item.options.map((option) => (
          <label
            key={option.id}
            htmlFor={`${item.id}-${option.id}`}
            className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
              selectedOption === option.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:bg-gray-50'
            } ${item.recommendation === option.id ? 'ring-1 ring-green-300' : ''}`}
          >
            <input
              id={`${item.id}-${option.id}`}
              type="radio"
              name={`decision-${item.id}`}
              value={option.id}
              checked={selectedOption === option.id}
              onChange={() => setSelectedOption(option.id)}
              className="mt-0.5 w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{option.label}</span>
                {item.recommendation === option.id && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                    <CheckCircle className="w-3 h-3" />
                    Recommended
                  </span>
                )}
              </div>
              {option.description && (
                <p className="text-sm text-gray-500 mt-0.5">{option.description}</p>
              )}
            </div>
          </label>
        ))}
      </div>
      
      {/* Action Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedOption}
        className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Confirm Decision
      </button>
    </div>
  );
}

export function DecisionQueue({ items, onDecision }: DecisionQueueProps) {
  if (items.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <CheckCircle className="w-6 h-6 text-green-500" />
          <h2 className="text-lg font-semibold text-gray-900">Decision Queue</h2>
        </div>
        <div className="text-center py-8">
          <p className="text-gray-500">No decisions pending</p>
          <p className="text-sm text-gray-400 mt-1">All items are flowing smoothly</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-100 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Decision Queue</h2>
            <p className="text-sm text-gray-500">{items.length} item{items.length !== 1 ? 's' : ''} requiring your input</p>
          </div>
        </div>
        
        {/* Info Tooltip */}
        <div className="group relative">
          <Info className="w-5 h-5 text-gray-400 cursor-help" />
          <div className="absolute right-0 top-full mt-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            These items are blocking progress in the pipeline. Your decisions will unblock them.
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        {items.map((item, index) => (
          <DecisionCard
            key={item.id}
            item={item}
            onDecision={onDecision}
            isFirst={index === 0}
          />
        ))}
      </div>
    </div>
  );
}

export default DecisionQueue;
