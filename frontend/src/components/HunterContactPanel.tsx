import { useState } from 'react';
import {
  Search, Loader2, AlertCircle, Linkedin, Globe, Twitter,
} from 'lucide-react';
import { hunterGet, scoreColor, VERIFY_STATUS } from '../lib/hunterApi';

// ── Types ─────────────────────────────────────────────────────────────────────

type Tab = 'find' | 'verify' | 'enrich' | 'combined';

const TABS: { id: Tab; label: string }[] = [
  { id: 'find',     label: 'Find Email'     },
  { id: 'verify',   label: 'Verify Email'   },
  { id: 'enrich',   label: 'Enrich Person'  },
  { id: 'combined', label: 'Combined'        },
];

export interface ApplyFields {
  job_title?:    string;
  linkedin_url?: string;
  phone?:        string;
}

interface Props {
  firstName:     string;
  lastName:      string;
  currentEmail?: string;
  defaultDomain?: string;
  onApplyEmail:  (email: string) => Promise<void>;
  onApplyFields: (fields: ApplyFields) => Promise<void>;
}

// ── Shared sub-components ─────────────────────────────────────────────────────

function Section({ title }: { title: string }) {
  return (
    <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">
      {title}
    </p>
  );
}

function Check({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-1 text-xs">
      <span className={ok ? 'text-green-600' : 'text-gray-300'}>
        {ok ? '✓' : '✗'}
      </span>
      <span className={ok ? 'text-gray-700' : 'text-gray-400'}>{label}</span>
    </div>
  );
}

// ── Result renderers ──────────────────────────────────────────────────────────

function FindResult({
  result,
  onApply,
}: {
  result: any;
  onApply: () => void;
}) {
  return (
    <div className="flex items-center justify-between gap-3 bg-white border border-green-200 rounded-lg px-4 py-3">
      <div>
        <p className="text-sm font-semibold text-gray-900">{result.email}</p>
        <p className="text-xs text-gray-500 mt-0.5">
          Confidence:{' '}
          <span className={`font-bold ${scoreColor(result.score ?? 0)}`}>
            {result.score}%
          </span>
          {result.verification?.status === 'valid' && (
            <span className="ml-2 text-green-600 font-medium">· verified ✓</span>
          )}
        </p>
      </div>
      <button
        onClick={onApply}
        className="flex-shrink-0 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded-lg transition-colors"
      >
        Save Email
      </button>
    </div>
  );
}

function VerifyResult({ result }: { result: any }) {
  const s = VERIFY_STATUS[result.status] ?? VERIFY_STATUS.unknown;
  return (
    <div className={`border rounded-lg p-4 ${s.cls}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="font-semibold text-sm">{s.label}</span>
        <span className="text-xs">
          Score:{' '}
          <span className={`font-bold ${scoreColor(result.score ?? 0)}`}>
            {result.score}%
          </span>
        </span>
      </div>
      <div className="grid grid-cols-3 gap-y-1.5 gap-x-3">
        <Check label="MX Records"  ok={result.mx_records}  />
        <Check label="SMTP Server" ok={result.smtp_server} />
        <Check label="SMTP Check"  ok={result.smtp_check}  />
        <Check label="Accept-All"  ok={result.accept_all}  />
        <Check label="Webmail"     ok={result.webmail}     />
        <Check label="Disposable"  ok={result.disposable}  />
        <Check label="Gibberish"   ok={result.gibberish}   />
        <Check label="Block"       ok={result.block}       />
      </div>
    </div>
  );
}

function PersonResult({
  person,
  company,
  onApplyFields,
}: {
  person: any;
  company?: any;
  onApplyFields: (f: ApplyFields) => void;
}) {
  const fields: ApplyFields = {
    job_title:    person?.position    || undefined,
    linkedin_url: person?.linkedin_url || undefined,
    phone:        person?.phone_number || undefined,
  };
  const hasApplyable = Object.values(fields).some(Boolean);

  return (
    <div className="border border-gray-200 rounded-lg bg-white divide-y divide-gray-100 overflow-hidden">
      {/* Person */}
      {person && (
        <div className="p-3 space-y-1.5">
          <Section title="Person" />
          {person.first_name && (
            <p className="text-sm font-medium text-gray-900">
              {person.first_name} {person.last_name}
              {person.position && (
                <span className="font-normal text-gray-500"> · {person.position}</span>
              )}
            </p>
          )}
          {person.seniority && (
            <p className="text-xs text-gray-500 capitalize">
              {person.seniority}
              {person.department && ` · ${person.department}`}
            </p>
          )}
          {person.phone_number && (
            <p className="text-xs text-gray-600 flex items-center gap-1.5">
              📞 {person.phone_number}
            </p>
          )}
          {person.twitter && (
            <a
              href={`https://twitter.com/${person.twitter}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
            >
              <Twitter className="w-3 h-3" /> @{person.twitter}
            </a>
          )}
          {person.linkedin_url && (
            <a
              href={person.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
            >
              <Linkedin className="w-3 h-3" /> LinkedIn Profile
            </a>
          )}
          {hasApplyable && (
            <button
              onClick={() => onApplyFields(fields)}
              className="mt-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              Apply to contact
            </button>
          )}
        </div>
      )}

      {/* Company (combined only) */}
      {company && (
        <div className="p-3 space-y-1.5">
          <Section title="Company" />
          {company.name && (
            <p className="text-sm font-medium text-gray-900">
              {company.name}
              {company.industry && (
                <span className="font-normal text-gray-500"> · {company.industry}</span>
              )}
            </p>
          )}
          {company.description && (
            <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">
              {company.description}
            </p>
          )}
          {company.employees_count && (
            <p className="text-xs text-gray-500">
              👥 {company.employees_count.toLocaleString()} employees
            </p>
          )}
          {company.website && (
            <a
              href={
                company.website.startsWith('http')
                  ? company.website
                  : `https://${company.website}`
              }
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
            >
              <Globe className="w-3 h-3" /> {company.website}
            </a>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function HunterContactPanel({
  firstName,
  lastName,
  currentEmail,
  defaultDomain,
  onApplyEmail,
  onApplyFields,
}: Props) {
  // Start on Verify if contact already has an email, else Find
  const [tab, setTab] = useState<Tab>(currentEmail ? 'verify' : 'find');
  const [domain, setDomain]         = useState(defaultDomain ?? '');
  const [emailInput, setEmailInput] = useState(currentEmail  ?? '');
  const [loading, setLoading]       = useState(false);
  const [result, setResult]         = useState<any>(null);
  const [error, setError]           = useState<string | null>(null);

  const switchTab = (t: Tab) => {
    setTab(t);
    setResult(null);
    setError(null);
  };

  const run = async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      let data: any;
      const em = emailInput.trim() || currentEmail || '';

      if (tab === 'find') {
        if (!domain.trim()) throw new Error('Enter a company domain (e.g. company.com)');
        const parts = `${firstName} ${lastName}`.trim().split(/\s+/);
        data = await hunterGet('/email-finder', {
          domain:     domain.trim(),
          first_name: parts[0]              || firstName,
          last_name:  parts.slice(1).join(' ') || lastName,
        });
      } else if (tab === 'verify') {
        if (!em) throw new Error('No email to verify — find one first or enter it manually.');
        data = await hunterGet('/email-verifier', { email: em });
      } else if (tab === 'enrich') {
        if (!em) throw new Error('Enter an email to enrich.');
        data = await hunterGet('/people/find', { email: em });
      } else {
        if (!em) throw new Error('Enter an email for combined enrichment.');
        data = await hunterGet('/combined/find', { email: em });
      }
      setResult(data);
    } catch (e: any) {
      setError(e.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const inpCls =
    'flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-orange-400 bg-white';
  const btnCls = `flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white rounded-lg transition-colors whitespace-nowrap ${
    loading
      ? 'bg-orange-300 cursor-not-allowed'
      : 'bg-orange-500 hover:bg-orange-600'
  }`;

  const btnLabel =
    tab === 'find'
      ? 'Find'
      : tab === 'verify'
      ? 'Verify'
      : 'Enrich';

  const hint =
    tab === 'find'
      ? `Searches for ${firstName} ${lastName} at the given domain`
      : tab === 'verify'
      ? 'Checks deliverability, SMTP, MX records, and spam traps'
      : tab === 'enrich'
      ? 'Returns name, title, phone, LinkedIn & Twitter from an email'
      : 'Returns full person + company data from an email';

  return (
    <div className="border border-orange-200 rounded-xl overflow-hidden bg-white">
      {/* ── Header ── */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-orange-50 border-b border-orange-100">
        <div className="w-5 h-5 rounded-md bg-orange-500 flex items-center justify-center text-white text-xs font-black leading-none">
          H
        </div>
        <span className="text-sm font-semibold text-gray-800">Hunter.io</span>
        <span className="text-xs text-gray-400 ml-0.5">· Email intelligence</span>
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
        {/* Input row */}
        <div className="flex gap-2">
          {tab === 'find' ? (
            <input
              type="text"
              placeholder="company.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && run()}
              className={inpCls}
            />
          ) : (
            <input
              type="email"
              placeholder={currentEmail || 'email@company.com'}
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && run()}
              className={inpCls}
            />
          )}
          <button onClick={run} disabled={loading} className={btnCls}>
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            {loading ? '…' : btnLabel}
          </button>
        </div>

        {/* Hint */}
        <p className="text-xs text-gray-400">{hint}</p>

        {/* Error */}
        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && tab === 'find' && (
          <FindResult
            result={result}
            onApply={async () => {
              await onApplyEmail(result.email);
              setResult(null);
            }}
          />
        )}

        {result && tab === 'verify' && <VerifyResult result={result} />}

        {result && (tab === 'enrich' || tab === 'combined') && (
          <PersonResult
            person={tab === 'combined' ? result.person : result}
            company={tab === 'combined' ? result.company : undefined}
            onApplyFields={async (fields) => {
              await onApplyFields(fields);
              setResult(null);
            }}
          />
        )}
      </div>
    </div>
  );
}
