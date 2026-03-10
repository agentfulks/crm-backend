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
  firstName:      string;
  lastName:       string;
  currentEmail?:  string;
  defaultDomain?: string;
  emailVerified?: boolean;
  onApplyEmail:   (email: string) => Promise<void>;
  onApplyFields:  (fields: ApplyFields) => Promise<void>;
  onVerified?:    () => Promise<void>;
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
  const isVerified = result.verification?.status === 'valid';
  return (
    <div className="flex items-center justify-between gap-3 bg-white border border-green-200 rounded-lg px-4 py-3">
      <div>
        <p className="text-sm font-semibold text-gray-900">{result.email}</p>
        <p className="text-xs text-gray-500 mt-0.5">
          Confidence:{' '}
          <span className={`font-bold ${scoreColor(result.score ?? 0)}`}>
            {result.score}%
          </span>
          {isVerified && (
            <span className="ml-2 text-green-600 font-medium">· verified ✓</span>
          )}
        </p>
      </div>
      <button
        onClick={onApply}
        className="flex-shrink-0 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded-lg transition-colors"
        title={isVerified ? 'Save email and mark as Hunter-verified' : 'Save email to contact'}
      >
        {isVerified ? '✓ Save & Verify' : 'Save Email'}
      </button>
    </div>
  );
}

function VerifyResult({
  result,
  onMarkVerified,
}: {
  result: any;
  onMarkVerified?: () => void;
}) {
  const s = VERIFY_STATUS[result.status] ?? VERIFY_STATUS.unknown;
  const isValid = result.status === 'valid';
  return (
    <div className={`border rounded-lg p-4 ${s.cls}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="font-semibold text-sm">{s.label}</span>
        <div className="flex items-center gap-3">
          <span className="text-xs">
            Score:{' '}
            <span className={`font-bold ${scoreColor(result.score ?? 0)}`}>
              {result.score}%
            </span>
          </span>
          {isValid && onMarkVerified && (
            <button
              onClick={onMarkVerified}
              className="px-2.5 py-1 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded-lg transition-colors"
              title="Mark this contact's email as Hunter-verified"
            >
              ✓ Mark Verified
            </button>
          )}
        </div>
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
  if (!person) return null;

  // ── Hunter.io /people/find and /combined/find return camelCase nested objects ──
  // e.g. person.name.givenName, person.employment.title, person.linkedin.handle

  // Name — could be nested {givenName, familyName} or flat first_name/last_name
  const firstName: string =
    person.name?.givenName ?? person.first_name ?? '';
  const lastName: string =
    person.name?.familyName ?? person.last_name ?? '';
  const fullName: string =
    person.name?.fullName ?? [firstName, lastName].filter(Boolean).join(' ');

  // Employment — nested under person.employment
  const position: string =
    person.employment?.title ?? person.position ?? '';
  const seniority: string =
    person.employment?.seniority ?? person.seniority ?? '';
  const department: string =
    person.employment?.role ?? person.department ?? '';
  const companyName: string =
    person.employment?.name ?? '';

  // Contact details
  const phoneNumber: string =
    person.phone ?? person.phone_number ?? '';

  // Location / bio
  const location: string = typeof person.location === 'string' ? person.location : '';
  const bio: string      = typeof person.bio      === 'string' ? person.bio      : '';

  // Twitter — can be object {handle} or plain string
  const twitterHandle: string =
    typeof person.twitter === 'string'
      ? person.twitter
      : person.twitter?.handle ?? '';

  // LinkedIn — can be object {handle} or full URL string
  const linkedinHandle: string =
    typeof person.linkedin === 'object'
      ? person.linkedin?.handle ?? ''
      : typeof person.linkedin_url === 'string'
      ? person.linkedin_url.replace(/^https?:\/\/(www\.)?linkedin\.com\/in\//, '')
      : '';
  const linkedinUrl: string = linkedinHandle
    ? `https://www.linkedin.com/in/${linkedinHandle}`
    : '';

  const fields: ApplyFields = {
    job_title:    position    || undefined,
    linkedin_url: linkedinUrl || undefined,
    phone:        phoneNumber || undefined,
  };
  const hasApplyable = Object.values(fields).some(Boolean);

  return (
    <div className="border border-gray-200 rounded-lg bg-white divide-y divide-gray-100 overflow-hidden">
      {/* ── Person ── */}
      <div className="p-3 space-y-1.5">
        <Section title="Person" />

        {fullName && (
          <p className="text-sm font-semibold text-gray-900">
            {fullName}
            {position && <span className="font-normal text-gray-500"> · {position}</span>}
          </p>
        )}

        {(seniority || department) && (
          <p className="text-xs text-gray-500 capitalize">
            {[seniority, department].filter(Boolean).join(' · ')}
          </p>
        )}

        {companyName && (
          <p className="text-xs text-gray-500">🏢 {companyName}</p>
        )}

        {location && (
          <p className="text-xs text-gray-500">📍 {location}</p>
        )}

        {bio && (
          <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">{bio}</p>
        )}

        {phoneNumber && (
          <p className="text-xs text-gray-600">📞 {phoneNumber}</p>
        )}

        {twitterHandle && (
          <a
            href={`https://twitter.com/${twitterHandle}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
          >
            <Twitter className="w-3 h-3" /> @{twitterHandle}
          </a>
        )}

        {linkedinUrl && (
          <a
            href={linkedinUrl}
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

      {/* ── Company (combined endpoint only) ── */}
      {company && (
        <div className="p-3 space-y-1.5">
          <Section title="Company" />
          {(company.name || company.legalName) && (
            <p className="text-sm font-semibold text-gray-900">
              {String(company.name ?? company.legalName)}
              {company.category?.industry && (
                <span className="font-normal text-gray-500"> · {String(company.category.industry)}</span>
              )}
              {!company.category?.industry && company.industry && (
                <span className="font-normal text-gray-500"> · {String(company.industry)}</span>
              )}
            </p>
          )}
          {(company.description || company.site?.metaDescription) && (
            <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">
              {String(company.description ?? company.site?.metaDescription)}
            </p>
          )}
          {(company.metrics?.employees ?? company.employees_count) != null && (
            <p className="text-xs text-gray-500">
              👥 {Number(company.metrics?.employees ?? company.employees_count).toLocaleString()} employees
            </p>
          )}
          {(company.domain || company.domainAliases?.[0]) && (
            <a
              href={`https://${company.domain ?? company.domainAliases?.[0]}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
            >
              <Globe className="w-3 h-3" /> {company.domain ?? company.domainAliases?.[0]}
            </a>
          )}
          {typeof company.website === 'string' && company.website && !company.domain && (
            <a
              href={company.website.startsWith('http') ? company.website : `https://${company.website}`}
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
  emailVerified,
  onApplyEmail,
  onApplyFields,
  onVerified,
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
        {emailVerified && (
          <span className="ml-auto flex items-center gap-1 text-xs font-semibold text-green-700 bg-green-100 border border-green-200 px-2 py-0.5 rounded-full">
            <span>✓</span> Verified by Hunter
          </span>
        )}
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
          <div className={`flex items-start gap-2 rounded-lg px-3 py-2.5 border ${
            error.toLowerCase().includes('not exist') || error.toLowerCase().includes('not found')
              ? 'bg-blue-50 border-blue-200'
              : 'bg-red-50 border-red-200'
          }`}>
            <AlertCircle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
              error.toLowerCase().includes('not exist') || error.toLowerCase().includes('not found')
                ? 'text-blue-400'
                : 'text-red-500'
            }`} />
            <p className={`text-xs ${
              error.toLowerCase().includes('not exist') || error.toLowerCase().includes('not found')
                ? 'text-blue-700'
                : 'text-red-700'
            }`}>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && tab === 'find' && (
          <FindResult
            result={result}
            onApply={async () => {
              await onApplyEmail(result.email);
              // If Hunter also verified the email, mark it verified
              if (result.verification?.status === 'valid' && onVerified) {
                await onVerified();
              }
              setResult(null);
            }}
          />
        )}

        {result && tab === 'verify' && (
          <VerifyResult
            result={result}
            onMarkVerified={onVerified ? async () => { await onVerified(); setResult(null); } : undefined}
          />
        )}

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
