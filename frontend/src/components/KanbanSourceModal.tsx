/**
 * KanbanSourceModal
 *
 * When a user clicks a source-linked kanban card (VC, Studio, or Contact),
 * this component fetches the latest data for that entity and renders the
 * same detail modal they'd see on the base board — with full edit / outreach
 * functionality.
 */

import { useState } from 'react';
import type { KanbanCard, BDRContact } from '../types';
import { useContact } from '../hooks/useContacts';
import { useFund } from '../hooks/useFunds';
import { useStudioCompany } from '../hooks/useStudioPackets';
import { ContactDetailModal } from './ContactDetailModal';
import { StudioDetailModal } from './StudioDetailModal';
import { FundDetailModal } from './FundDetailModal';

// ── Shared loading / error shells ─────────────────────────────────────────────

function LoadingModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-10 shadow-xl flex flex-col items-center gap-3 min-w-[200px]">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-500">Loading…</p>
        <button onClick={onClose} className="text-xs text-gray-400 hover:text-gray-600 mt-1">
          Cancel
        </button>
      </div>
    </div>
  );
}

function ErrorModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-8 shadow-xl max-w-sm w-full text-center">
        <p className="text-gray-800 font-medium mb-1">Couldn't load source record</p>
        <p className="text-sm text-gray-500 mb-4">
          It may have been deleted or the source ID is missing.
        </p>
        <button
          onClick={onClose}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg"
        >
          Close
        </button>
      </div>
    </div>
  );
}

// ── Per-type loaders ──────────────────────────────────────────────────────────

interface ContactLoaderProps {
  id: string;
  studioName: string;
  onClose: () => void;
}

function ContactLoader({ id, studioName, onClose }: ContactLoaderProps) {
  const { data: contact, isLoading, isError } = useContact(id);

  if (isLoading) return <LoadingModal onClose={onClose} />;
  if (isError || !contact) return <ErrorModal onClose={onClose} />;

  return (
    <ContactDetailModal
      contact={contact}
      studioName={studioName}
      onClose={onClose}
    />
  );
}

interface StudioLoaderProps {
  id: string;
  onClose: () => void;
}

function StudioLoader({ id, onClose }: StudioLoaderProps) {
  const { data: packet, isLoading, isError } = useStudioCompany(id);

  // State for the nested contact modal (when user clicks a contact inside StudioDetailModal)
  const [nestedContact, setNestedContact] = useState<{
    contact: BDRContact;
    studioName: string;
    studioWebsite?: string;
  } | null>(null);

  if (isLoading) return <LoadingModal onClose={onClose} />;
  if (isError || !packet) return <ErrorModal onClose={onClose} />;

  // If a contact was opened from within the studio modal, render that instead
  if (nestedContact) {
    return (
      <ContactDetailModal
        contact={nestedContact.contact}
        studioName={nestedContact.studioName}
        studioWebsite={nestedContact.studioWebsite}
        onClose={() => setNestedContact(null)}
      />
    );
  }

  return (
    <StudioDetailModal
      packet={packet}
      onClose={onClose}
      onOpenContact={(contact, studioName, studioWebsite) =>
        setNestedContact({ contact, studioName, studioWebsite })
      }
    />
  );
}

interface FundLoaderProps {
  id: string;
  onClose: () => void;
}

function FundLoader({ id, onClose }: FundLoaderProps) {
  const { data: fund, isLoading, isError } = useFund(id);

  if (isLoading) return <LoadingModal onClose={onClose} />;
  if (isError || !fund) return <ErrorModal onClose={onClose} />;

  return <FundDetailModal fund={fund} onClose={onClose} />;
}

// ── Main export ───────────────────────────────────────────────────────────────

interface Props {
  card: KanbanCard;
  onClose: () => void;
}

export function KanbanSourceModal({ card, onClose }: Props) {
  const { card_type, source_id, source_data } = card;

  if (!source_id) {
    return <ErrorModal onClose={onClose} />;
  }

  if (card_type === 'contact') {
    return (
      <ContactLoader
        id={source_id}
        studioName={source_data?.studio_name || ''}
        onClose={onClose}
      />
    );
  }

  if (card_type === 'studio') {
    return <StudioLoader id={source_id} onClose={onClose} />;
  }

  if (card_type === 'vc') {
    return <FundLoader id={source_id} onClose={onClose} />;
  }

  return null;
}
