import { useState } from 'react';
import { Search, Loader2, AlertCircle, Globe, Mail, User, Building2 } from 'lucide-react';
import { hunterGet, hunterPost, scoreColor } from '../lib/hunterApi';

// ── Types ─────────────────────────────────────────────────────────────────────

type Tab = 'domain' | 'company' | 'discover';

const TABS: { id: Tab; label: string }[] = [
  { id: 'domain',   label: 'Domain Search'     },
  { id: 'company',  label: 'Company Info'       },
  { id: 'discover', label: 'Discover People'    },
];

interface Props {
  defaultDomain?: string;
  companyName?:   string;
}

// ── Result components ─────────────────────────────────────────────────────────

function DomainResult({ result }: { result: any }) {
  const emails: any[] = result.emails ?? [];
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
        <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden bg-white">
          {emails.slice(0, 15).map((e: any, i: number) => (
            <div key={i} className="flex items-center justify-between gap-3 px-3 py-2">
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{e.value}</p>
                {(e.first_name || e.last_name) && (
                  <p className="text-xs text-gray-500">
                    {[e.first_name, e.last_name].filter(Boolean).join(' ')}
                    {e.position && ` · ${e.position}`}
                  </p>
                )}
              </div>
              <span className={`text-xs font-semibold flex-shrink-0 ${scoreColor(e.confidence ?? 0)}`}>
                {e.confidence}%
              </span>
            </div>
          ))}
          {emails.length > 15 && (
            <div className="px-3 py-2 text-xs text-center text-gray-400">
              + {emails.length - 15} more — refine in Hunter.io dashboard
            </div>
          )}
        </div>
      ) : (
        <p className="text-xs text-gray-400 text-center py-4">
          No emails found at this domain yet.
        </p>
      )}
    </div>
  );
}

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

function DiscoverResult({ result }: { result: any }) {
  // Hunter's Discover endpoint can return results under different keys
  // depending on account tier and API version.
  // Priority order: people > leads > emails > top-level array
  const leads: any[] = Array.isArray(result)
    ? result
    : result.people ?? result.leads ?? result.emails ?? result.contacts ?? [];

  const isAsyncTask = leads.length === 0 && result?.id && result?.status;

  if (leads.length === 0) {
    return (
      <div className="text-center py-6 border border-dashed border-gray-200 rounded-lg">
        <User className="w-6 h-6 text-gray-300 mx-auto mb-2" />
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
      <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden bg-white">
        {leads.slice(0, 15).map((l: any, i: number) => (
          <div key={i} className="flex items-center gap-3 px-3 py-2.5">
            <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 text-xs font-semibold text-gray-600">
              {(l.first_name?.[0] ?? l.name?.[0] ?? '?').toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 truncate">
                {[l.first_name, l.last_name].filter(Boolean).join(' ') || l.name || '—'}
              </p>
              {(l.position || l.title) && (
                <p className="text-xs text-gray-500 truncate">{l.position ?? l.title}</p>
              )}
            </div>
            {(l.email || l.value) && (
              <a
                href={`mailto:${l.email ?? l.value}`}
                className="flex items-center gap-1 text-xs text-blue-600 hover:underline flex-shrink-0"
              >
                <Mail className="w-3 h-3" />
                {l.email ?? l.value}
              </a>
            )}
          </div>
        ))}
        {leads.length > 15 && (
          <div className="px-3 py-2 text-xs text-center text-gray-400">
            + {leads.length - 15} more — view in Hunter.io dashboard
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function HunterStudioPanel({ defaultDomain, companyName }: Props) {
  const [tab, setTab]         = useState<Tab>('domain');
  const [domain, setDomain]   = useState(defaultDomain ?? '');
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState<any>(null);
  const [error, setError]     = useState<string | null>(null);

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
        data = await hunterGet('/domain-search', { domain: domain.trim() });
      } else if (tab === 'company') {
        data = await hunterGet('/companies/find', { domain: domain.trim() });
      } else {
        // Discover — POST
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
        {/* Domain input */}
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
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            {loading ? '…' : 'Search'}
          </button>
        </div>

        <p className="text-xs text-gray-400">{hint}</p>

        {/* Error */}
        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && tab === 'domain'   && <DomainResult   result={result} />}
        {result && tab === 'company'  && <CompanyResult  result={result} />}
        {result && tab === 'discover' && <DiscoverResult result={result} />}
      </div>
    </div>
  );
}
