import { useState } from 'react';
import { Search, Loader2, AlertCircle, Globe, Building2, CheckSquare, Square, UserPlus } from 'lucide-react';
import { hunterGet, hunterPost, scoreColor } from '../lib/hunterApi';

// ── Types ─────────────────────────────────────────────────────────────────────

type Tab = 'domain' | 'company' | 'discover';

const TABS: { id: Tab; label: string }[] = [
  { id: 'domain',   label: 'Domain Search'  },
  { id: 'company',  label: 'Company Info'   },
  { id: 'discover', label: 'Discover People' },
];

export interface HunterContact {
  full_name: string;
  email?:       string;
  title?:       string;
  linkedin_url?: string;
}

interface Props {
  defaultDomain?: string;
  companyName?:   string;
  /** Emails already saved as contacts — used to detect duplicates */
  existingEmails?: string[];
  /** Called with the list of selected contacts to import */
  onSaveContacts?: (contacts: HunterContact[]) => Promise<void>;
}

// ── helpers ───────────────────────────────────────────────────────────────────

function emailToContact(e: any): HunterContact {
  const first = e.first_name ?? '';
  const last  = e.last_name  ?? '';
  return {
    full_name:   [first, last].filter(Boolean).join(' ') || e.value || 'Unknown',
    email:       e.value ?? undefined,
    title:       e.position ?? undefined,
    linkedin_url: e.linkedin ?? undefined,
  };
}

function personToContact(l: any): HunterContact {
  const first = l.first_name ?? '';
  const last  = l.last_name  ?? '';
  return {
    full_name:   [first, last].filter(Boolean).join(' ') || l.name || 'Unknown',
    email:       l.email ?? l.value ?? undefined,
    title:       l.position ?? l.title ?? undefined,
    linkedin_url: l.linkedin_url ?? l.linkedin ?? undefined,
  };
}

// ── SaveBar ───────────────────────────────────────────────────────────────────

function SaveBar({
  total,
  selected,
  saving,
  onToggleAll,
  onSaveSelected,
  onSaveAll,
}: {
  total: number;
  selected: number;
  saving: boolean;
  onToggleAll: () => void;
  onSaveSelected: () => void;
  onSaveAll: () => void;
}) {
  return (
    <div className="flex items-center gap-2 p-2 bg-orange-50 border border-orange-200 rounded-lg">
      <button
        onClick={onToggleAll}
        className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-gray-900"
      >
        {selected === total ? (
          <CheckSquare className="w-4 h-4 text-orange-500" />
        ) : (
          <Square className="w-4 h-4 text-gray-400" />
        )}
        {selected === total ? 'Deselect all' : 'Select all'}
      </button>
      <span className="text-xs text-gray-400 flex-1">{selected} of {total} selected</span>
      {selected > 0 && (
        <button
          onClick={onSaveSelected}
          disabled={saving}
          className="flex items-center gap-1 px-2.5 py-1 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white text-xs font-semibold rounded-lg transition-colors"
        >
          {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserPlus className="w-3 h-3" />}
          Save {selected}
        </button>
      )}
      <button
        onClick={onSaveAll}
        disabled={saving}
        className="flex items-center gap-1 px-2.5 py-1 bg-gray-700 hover:bg-gray-900 disabled:bg-gray-300 text-white text-xs font-semibold rounded-lg transition-colors"
      >
        {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserPlus className="w-3 h-3" />}
        Save all {total}
      </button>
    </div>
  );
}

// ── DomainResult ─────────────────────────────────────────────────────────────

function DomainResult({
  result,
  onSaveContacts,
  existingEmails = [],
}: {
  result: any;
  onSaveContacts?: (c: HunterContact[]) => Promise<void>;
  existingEmails?: string[];
}) {
  const emails: any[] = result.emails ?? [];
  const visible = emails.slice(0, 20);

  // Normalised set for O(1) duplicate lookup
  const existingSet = new Set(existingEmails.map((e) => e.toLowerCase()));
  const isDupe = (e: any) => !!e.value && existingSet.has(e.value.toLowerCase());

  // Only non-duplicate indices are selectable
  const saveable = visible.map((e, i) => ({ e, i })).filter(({ e }) => !isDupe(e));

  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<Set<number>>(new Set());

  const toggle = (i: number) =>
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });

  const saveableIndices = saveable.map(({ i }) => i);
  const allSelected = saveableIndices.length > 0 && saveableIndices.every((i) => selected.has(i));
  const toggleAll = () =>
    setSelected(allSelected ? new Set() : new Set(saveableIndices));

  const save = async (indices: number[]) => {
    if (!onSaveContacts || indices.length === 0) return;
    setSaving(true);
    try {
      await onSaveContacts(indices.map((i) => emailToContact(visible[i])));
      setSaved((prev) => new Set([...prev, ...indices]));
      setSelected(new Set());
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          Found <strong className="text-gray-800">{result.meta?.total ?? emails.length}</strong> email
          {(result.meta?.total ?? emails.length) !== 1 ? 's' : ''} at{' '}
          <strong className="text-gray-800">{result.domain}</strong>
        </span>
        {result.pattern && (
          <span className="bg-gray-100 px-2 py-0.5 rounded font-mono">{result.pattern}</span>
        )}
      </div>

      {emails.length > 0 ? (
        <>
          {onSaveContacts && saveableIndices.length > 0 && (
            <SaveBar
              total={saveableIndices.length}
              selected={[...selected].filter((i) => saveableIndices.includes(i)).length}
              saving={saving}
              onToggleAll={toggleAll}
              onSaveSelected={() => save([...selected].filter((i) => saveableIndices.includes(i)))}
              onSaveAll={() => save(saveableIndices)}
            />
          )}
          {onSaveContacts && saveableIndices.length === 0 && visible.length > 0 && (
            <div className="text-xs text-center text-gray-400 bg-gray-50 border border-gray-200 rounded-lg py-2">
              All contacts already exist in your CRM.
            </div>
          )}

          <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden bg-white">
            {visible.map((e: any, i: number) => {
              const dupe = isDupe(e);
              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 px-3 py-2 ${
                    saved.has(i) ? 'bg-green-50' : dupe ? 'bg-gray-50 opacity-70' : ''
                  }`}
                >
                  {onSaveContacts && (
                    <button
                      onClick={() => !dupe && toggle(i)}
                      disabled={dupe}
                      className="flex-shrink-0"
                    >
                      {dupe ? (
                        <CheckSquare className="w-4 h-4 text-gray-300" />
                      ) : selected.has(i) ? (
                        <CheckSquare className="w-4 h-4 text-orange-500" />
                      ) : (
                        <Square className="w-4 h-4 text-gray-300 hover:text-gray-500" />
                      )}
                    </button>
                  )}
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm font-medium truncate ${dupe ? 'text-gray-400' : 'text-gray-900'}`}>
                      {e.value}
                    </p>
                    {(e.first_name || e.last_name) && (
                      <p className="text-xs text-gray-500">
                        {[e.first_name, e.last_name].filter(Boolean).join(' ')}
                        {e.position && ` · ${e.position}`}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {dupe && (
                      <span className="text-xs text-gray-400 italic">already in CRM</span>
                    )}
                    {saved.has(i) && (
                      <span className="text-xs text-green-600 font-medium">✓ saved</span>
                    )}
                    <span className={`text-xs font-semibold ${scoreColor(e.confidence ?? 0)}`}>
                      {e.confidence}%
                    </span>
                  </div>
                </div>
              );
            })}
            {emails.length > 20 && (
              <div className="px-3 py-2 text-xs text-center text-gray-400">
                + {emails.length - 20} more — refine in Hunter.io dashboard
              </div>
            )}
          </div>
        </>
      ) : (
        <p className="text-xs text-gray-400 text-center py-4">
          No emails found at this domain yet.
        </p>
      )}
    </div>
  );
}

// ── CompanyResult ─────────────────────────────────────────────────────────────

function CompanyResult({ result }: { result: any }) {
  return (
    <div className="border border-gray-200 rounded-lg bg-white divide-y divide-gray-100 overflow-hidden">
      <div className="p-4 space-y-2">
        {result.name && (
          <div className="flex items-start gap-2">
            <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-gray-900">{result.name}</p>
              {result.industry && (
                <p className="text-xs text-gray-500">{result.industry}</p>
              )}
            </div>
          </div>
        )}
        {result.description && (
          <p className="text-xs text-gray-600 leading-relaxed line-clamp-4">
            {result.description}
          </p>
        )}
      </div>
      <div className="px-4 py-3 grid grid-cols-2 gap-2 text-xs">
        {result.employees_count && (
          <div>
            <span className="text-gray-400">Employees</span>
            <p className="font-semibold text-gray-800">
              {result.employees_count.toLocaleString()}
            </p>
          </div>
        )}
        {result.founded_year && (
          <div>
            <span className="text-gray-400">Founded</span>
            <p className="font-semibold text-gray-800">{result.founded_year}</p>
          </div>
        )}
        {result.city && (
          <div>
            <span className="text-gray-400">Location</span>
            <p className="font-semibold text-gray-800">
              {[result.city, result.country].filter(Boolean).join(', ')}
            </p>
          </div>
        )}
        {result.email_count && (
          <div>
            <span className="text-gray-400">Emails indexed</span>
            <p className="font-semibold text-gray-800">{result.email_count.toLocaleString()}</p>
          </div>
        )}
      </div>
      {(result.website || result.linkedin_url || result.twitter) && (
        <div className="px-4 py-3 flex flex-wrap gap-3">
          {result.website && (
            <a
              href={result.website.startsWith('http') ? result.website : `https://${result.website}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              <Globe className="w-3 h-3" /> Website
            </a>
          )}
          {result.linkedin_url && (
            <a
              href={result.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              LinkedIn
            </a>
          )}
        </div>
      )}
    </div>
  );
}

// ── DiscoverResult ────────────────────────────────────────────────────────────

function DiscoverResult({
  result,
  onSaveContacts,
  existingEmails = [],
}: {
  result: any;
  onSaveContacts?: (c: HunterContact[]) => Promise<void>;
  existingEmails?: string[];
}) {
  const leads: any[] = Array.isArray(result)
    ? result
    : result.people ?? result.leads ?? result.emails ?? result.contacts ?? [];

  const visible = leads.slice(0, 20);

  const existingSet = new Set(existingEmails.map((e) => e.toLowerCase()));
  const isDupe = (l: any) => {
    const email = l.email ?? l.value;
    return !!email && existingSet.has(email.toLowerCase());
  };

  const saveable = visible.map((l, i) => ({ l, i })).filter(({ l }) => !isDupe(l));
  const saveableIndices = saveable.map(({ i }) => i);

  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<Set<number>>(new Set());

  const isAsyncTask = leads.length === 0 && result?.id && result?.status;

  const toggle = (i: number) =>
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });

  const allSelected = saveableIndices.length > 0 && saveableIndices.every((i) => selected.has(i));
  const toggleAll = () =>
    setSelected(allSelected ? new Set() : new Set(saveableIndices));

  const save = async (indices: number[]) => {
    if (!onSaveContacts || indices.length === 0) return;
    setSaving(true);
    try {
      await onSaveContacts(indices.map((i) => personToContact(visible[i])));
      setSaved((prev) => new Set([...prev, ...indices]));
      setSelected(new Set());
    } finally {
      setSaving(false);
    }
  };

  if (leads.length === 0) {
    return (
      <div className="text-center py-6 border border-dashed border-gray-200 rounded-lg">
        <p className="text-xs text-gray-400">
          {isAsyncTask
            ? `Discovery task queued (status: ${result.status}). Check Hunter.io dashboard for results.`
            : 'No people discovered at this domain yet.'}
        </p>
        {isAsyncTask && (
          <p className="text-xs text-gray-300 mt-1">Task ID: {result.id}</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-400">{leads.length} people found</p>

      {onSaveContacts && saveableIndices.length > 0 && (
        <SaveBar
          total={saveableIndices.length}
          selected={[...selected].filter((i) => saveableIndices.includes(i)).length}
          saving={saving}
          onToggleAll={toggleAll}
          onSaveSelected={() => save([...selected].filter((i) => saveableIndices.includes(i)))}
          onSaveAll={() => save(saveableIndices)}
        />
      )}
      {onSaveContacts && saveableIndices.length === 0 && visible.length > 0 && (
        <div className="text-xs text-center text-gray-400 bg-gray-50 border border-gray-200 rounded-lg py-2">
          All contacts already exist in your CRM.
        </div>
      )}

      <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden bg-white">
        {visible.map((l: any, i: number) => {
          const dupe = isDupe(l);
          return (
            <div
              key={i}
              className={`flex items-center gap-3 px-3 py-2.5 ${
                saved.has(i) ? 'bg-green-50' : dupe ? 'bg-gray-50 opacity-70' : ''
              }`}
            >
              {onSaveContacts && (
                <button
                  onClick={() => !dupe && toggle(i)}
                  disabled={dupe}
                  className="flex-shrink-0"
                >
                  {dupe ? (
                    <CheckSquare className="w-4 h-4 text-gray-300" />
                  ) : selected.has(i) ? (
                    <CheckSquare className="w-4 h-4 text-orange-500" />
                  ) : (
                    <Square className="w-4 h-4 text-gray-300 hover:text-gray-500" />
                  )}
                </button>
              )}
              <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 text-xs font-semibold text-gray-600">
                {(l.first_name?.[0] ?? l.name?.[0] ?? '?').toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <p className={`text-sm font-medium truncate ${dupe ? 'text-gray-400' : 'text-gray-900'}`}>
                  {[l.first_name, l.last_name].filter(Boolean).join(' ') || l.name || '—'}
                </p>
                {(l.position || l.title) && (
                  <p className="text-xs text-gray-500 truncate">{l.position ?? l.title}</p>
                )}
                {(l.email || l.value) && (
                  <p className={`text-xs truncate ${dupe ? 'text-gray-400' : 'text-blue-600'}`}>
                    {l.email ?? l.value}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {dupe && (
                  <span className="text-xs text-gray-400 italic">already in CRM</span>
                )}
                {saved.has(i) && (
                  <span className="text-xs text-green-600 font-medium">✓ saved</span>
                )}
              </div>
            </div>
          );
        })}
        {leads.length > 20 && (
          <div className="px-3 py-2 text-xs text-center text-gray-400">
            + {leads.length - 20} more — view in Hunter.io dashboard
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function HunterStudioPanel({ defaultDomain, companyName, existingEmails = [], onSaveContacts }: Props) {
  const [tab, setTab]         = useState<Tab>('domain');
  const [domain, setDomain]   = useState(defaultDomain ?? '');
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState<any>(null);
  const [error, setError]     = useState<string | null>(null);

  // Domain Search pagination — limit 1–100, offset 0+
  const [dsLimit,  setDsLimit]  = useState(10);
  const [dsOffset, setDsOffset] = useState(0);

  const switchTab = (t: Tab) => {
    setTab(t);
    setResult(null);
    setError(null);
  };

  const run = async () => {
    if (!domain.trim()) {
      setError('Enter a company domain (e.g. riotgames.com)');
      return;
    }
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      let data: any;
      if (tab === 'domain') {
        data = await hunterGet('/domain-search', {
          domain: domain.trim(),
          limit:  String(Math.min(100, Math.max(1, dsLimit))),
          offset: String(Math.max(0, dsOffset)),
        });
      } else if (tab === 'company') {
        data = await hunterGet('/companies/find', { domain: domain.trim() });
      } else {
        const body: Record<string, unknown> = { domain: domain.trim() };
        if (companyName) body.company = companyName;
        data = await hunterPost('/discover', body);
      }
      setResult(data);
    } catch (e: any) {
      setError(e.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  // Pagination helpers — run domain search with explicit offset
  const runDomain = async (offset: number) => {
    if (!domain.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await hunterGet('/domain-search', {
        domain: domain.trim(),
        limit:  String(Math.min(100, Math.max(1, dsLimit))),
        offset: String(Math.max(0, offset)),
      });
      setResult(data);
      setDsOffset(offset);
    } catch (e: any) {
      setError(e.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const hint =
    tab === 'domain'
      ? 'Lists email addresses Hunter has found at this domain'
      : tab === 'company'
      ? 'Returns company size, industry, location, and more'
      : 'Discovers people and contacts associated with this company';

  const inpCls =
    'flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-orange-400 bg-white';
  const btnCls = `flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white rounded-lg transition-colors whitespace-nowrap ${
    loading ? 'bg-orange-300 cursor-not-allowed' : 'bg-orange-500 hover:bg-orange-600'
  }`;
  const numInpCls =
    'w-20 px-2 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-orange-400 bg-white text-center';

  return (
    <div className="border border-orange-200 rounded-xl overflow-hidden bg-white">
      {/* ── Header ── */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-orange-50 border-b border-orange-100">
        <div className="w-5 h-5 rounded-md bg-orange-500 flex items-center justify-center text-white text-xs font-black leading-none">
          H
        </div>
        <span className="text-sm font-semibold text-gray-800">Hunter.io</span>
        <span className="text-xs text-gray-400 ml-0.5">· Company intelligence</span>
      </div>

      {/* ── Tabs ── */}
      <div className="flex border-b border-gray-100">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => switchTab(t.id)}
            className={`flex-1 text-xs py-2.5 font-medium transition-colors border-b-2 ${
              tab === t.id
                ? 'border-orange-500 text-orange-600 bg-orange-50/60'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Body ── */}
      <div className="p-4 space-y-3">
        {/* Domain input + search button */}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="company.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && run()}
            className={inpCls}
          />
          <button onClick={run} disabled={loading} className={btnCls}>
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            {loading ? '…' : 'Search'}
          </button>
        </div>

        {/* Domain Search — limit / offset controls */}
        {tab === 'domain' && (
          <div className="flex items-center gap-3 flex-wrap">
            <label className="flex items-center gap-1.5 text-xs text-gray-500">
              Limit
              <input
                type="number"
                min={1}
                max={100}
                value={dsLimit}
                onChange={(e) => setDsLimit(Math.min(100, Math.max(1, Number(e.target.value))))}
                className={numInpCls}
              />
              <span className="text-gray-400">(1–100)</span>
            </label>
            <label className="flex items-center gap-1.5 text-xs text-gray-500">
              Offset
              <input
                type="number"
                min={0}
                value={dsOffset}
                onChange={(e) => setDsOffset(Math.max(0, Number(e.target.value)))}
                className={numInpCls}
              />
            </label>
            {/* Prev / Next shortcuts */}
            {result && (
              <div className="flex items-center gap-1 ml-auto">
                <button
                  onClick={() => runDomain(Math.max(0, dsOffset - dsLimit))}
                  disabled={dsOffset === 0 || loading}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  ← Prev
                </button>
                <span className="text-xs text-gray-400 px-1">
                  {dsOffset + 1}–{dsOffset + dsLimit}
                </span>
                <button
                  onClick={() => runDomain(dsOffset + dsLimit)}
                  disabled={loading}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40"
                >
                  Next →
                </button>
              </div>
            )}
          </div>
        )}

        <p className="text-xs text-gray-400">{hint}</p>

        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        {result && tab === 'domain'   && (
          <DomainResult result={result} onSaveContacts={onSaveContacts} existingEmails={existingEmails} />
        )}
        {result && tab === 'company'  && <CompanyResult result={result} />}
        {result && tab === 'discover' && (
          <DiscoverResult result={result} onSaveContacts={onSaveContacts} existingEmails={existingEmails} />
        )}
      </div>
    </div>
  );
}
