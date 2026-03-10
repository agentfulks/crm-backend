/**
 * BulkUploadModal — 4-step CSV import wizard for all entity types.
 *
 * Steps:
 *  1. Choose type + upload CSV file
 *  2. Map CSV columns → model fields (required fields shown with *)
 *  3. Preview mapped data + dry-run dupe check
 *  4. Import with progress/result summary
 */
import { useState, useRef, useCallback } from 'react';
import {
  X, Upload, ChevronRight, ChevronLeft, FileText, AlertCircle,
  CheckCircle, Info, Loader2, Download,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

// ─── Types ────────────────────────────────────────────────────────────────────

type BulkType = 'studio' | 'studio_contact' | 'vc_fund' | 'vc_contact';
type Step = 'type_upload' | 'map' | 'preview' | 'result';

interface FieldDef {
  key: string;
  label: string;
  required: boolean;
  hint?: string;
}

interface ParsedCSV {
  headers: string[];
  rows: Record<string, string>[];
}

interface DryRunResult {
  created: number;
  skipped: number;
  errors: { name: string; error: string }[];
}

// ─── Field definitions per entity type ───────────────────────────────────────

const FIELD_DEFS: Record<BulkType, FieldDef[]> = {
  studio: [
    { key: 'company_name', label: 'Studio Name', required: true },
    { key: 'website_url', label: 'Website URL', required: false },
    { key: 'headquarters_city', label: 'City', required: false },
    { key: 'headquarters_state', label: 'State / Region', required: false },
    { key: 'headquarters_country', label: 'Country', required: false },
    { key: 'industry', label: 'Industry / Genre', required: false },
    { key: 'company_size', label: 'Company Size', required: false },
    { key: 'linkedin_url', label: 'LinkedIn URL', required: false },
    { key: 'status', label: 'Status', required: false, hint: 'NEW, QUEUED, AWAITING_APPROVAL…' },
    { key: 'priority', label: 'Priority', required: false, hint: 'A, B, C' },
  ],
  studio_contact: [
    { key: 'company_name', label: 'Studio Name', required: true, hint: 'Must match an existing studio' },
    { key: 'full_name', label: 'Full Name', required: true },
    { key: 'email', label: 'Email', required: false },
    { key: 'job_title', label: 'Job Title', required: false },
    { key: 'phone', label: 'Phone', required: false },
    { key: 'linkedin_url', label: 'LinkedIn URL', required: false },
    { key: 'is_decision_maker', label: 'Decision Maker', required: false, hint: 'true / false' },
  ],
  vc_fund: [
    { key: 'name', label: 'Fund Name', required: true },
    { key: 'website_url', label: 'Website URL', required: false },
    { key: 'hq_city', label: 'HQ City', required: false },
    { key: 'hq_country', label: 'HQ Country', required: false },
    { key: 'firm_type', label: 'Firm Type', required: false },
    { key: 'stage_focus', label: 'Stage Focus', required: false, hint: 'Comma-separated: Seed, Series A…' },
    { key: 'check_size_min', label: 'Check Size Min ($)', required: false },
    { key: 'check_size_max', label: 'Check Size Max ($)', required: false },
    { key: 'overview', label: 'Overview / Notes', required: false },
    { key: 'contact_email', label: 'Contact Email', required: false },
    { key: 'linkedin_url', label: 'LinkedIn URL', required: false },
    { key: 'status', label: 'Status', required: false, hint: 'NEW, RESEARCHING, READY…' },
    { key: 'priority', label: 'Priority', required: false, hint: 'A, B, C' },
  ],
  vc_contact: [
    { key: 'fund_name', label: 'Fund Name', required: true, hint: 'Must match an existing VC fund' },
    { key: 'full_name', label: 'Full Name', required: true },
    { key: 'email', label: 'Email', required: false },
    { key: 'title', label: 'Title / Role', required: false },
    { key: 'phone', label: 'Phone', required: false },
    { key: 'linkedin_url', label: 'LinkedIn URL', required: false },
    { key: 'is_primary', label: 'Primary Contact', required: false, hint: 'true / false' },
  ],
};

const TYPE_LABELS: Record<BulkType, string> = {
  studio: 'Game Studios',
  studio_contact: 'Studio Contacts',
  vc_fund: 'VC Funds',
  vc_contact: 'VC Contacts',
};

const TYPE_ENDPOINTS: Record<BulkType, string> = {
  studio: `${API_BASE}/bdr/companies/bulk`,
  studio_contact: `${API_BASE}/bdr/contacts/bulk`,
  vc_fund: `${API_BASE}/funds/bulk`,
  vc_contact: `${API_BASE}/vc/contacts/bulk`,
};

// ─── CSV parser ───────────────────────────────────────────────────────────────

function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else { inQuotes = !inQuotes; }
    } else if (ch === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += ch;
    }
  }
  result.push(current.trim());
  return result;
}

function parseCSV(text: string): ParsedCSV {
  const lines = text.split(/\r?\n/).filter(l => l.trim());
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = parseCSVLine(lines[0]).map(h => h.replace(/^"|"$/g, ''));
  const rows = lines.slice(1).map(line => {
    const vals = parseCSVLine(line);
    const row: Record<string, string> = {};
    headers.forEach((h, i) => { row[h] = (vals[i] ?? '').replace(/^"|"$/g, ''); });
    return row;
  });
  return { headers, rows };
}

// ─── Sample CSV download helper ───────────────────────────────────────────────

function downloadSampleCSV(type: BulkType) {
  const fields = FIELD_DEFS[type];
  const headers = fields.map(f => f.key).join(',');
  let sampleRow = '';
  if (type === 'studio') sampleRow = '"Mythical Games","https://mythicalgames.com","Los Angeles","CA","USA","Gaming","201-500","","NEW","A"';
  if (type === 'studio_contact') sampleRow = '"Mythical Games","Jane Doe","jane@mythicalgames.com","CEO","","https://linkedin.com/in/janedoe","true"';
  if (type === 'vc_fund') sampleRow = '"Andreessen Horowitz","https://a16z.com","Menlo Park","USA","VC","Seed,Series A","500000","5000000","Top-tier VC","","","NEW","A"';
  if (type === 'vc_contact') sampleRow = '"Andreessen Horowitz","Marc Andreessen","marc@a16z.com","Partner","","https://linkedin.com/in/pmarca","true"';
  const csv = `${headers}\n${sampleRow}`;
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `sample_${type}.csv`;
  a.click();
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StepIndicator({ step }: { step: Step }) {
  const steps: { id: Step; label: string }[] = [
    { id: 'type_upload', label: 'Upload' },
    { id: 'map', label: 'Map Columns' },
    { id: 'preview', label: 'Preview' },
    { id: 'result', label: 'Done' },
  ];
  const idx = steps.findIndex(s => s.id === step);
  return (
    <div className="flex items-center gap-0 mb-6">
      {steps.map((s, i) => (
        <div key={s.id} className="flex items-center">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
            i < idx ? 'bg-green-100 text-green-700' :
            i === idx ? 'bg-blue-600 text-white' :
            'bg-gray-100 text-gray-400'
          }`}>
            {i < idx ? <CheckCircle className="w-3 h-3" /> : <span>{i + 1}</span>}
            {s.label}
          </div>
          {i < steps.length - 1 && (
            <div className={`w-6 h-px mx-1 ${i < idx ? 'bg-green-300' : 'bg-gray-200'}`} />
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface Props {
  onClose: () => void;
}

export function BulkUploadModal({ onClose }: Props) {
  const [step, setStep] = useState<Step>('type_upload');
  const [bulkType, setBulkType] = useState<BulkType>('studio');
  const [csv, setCsv] = useState<ParsedCSV | null>(null);
  const [fileName, setFileName] = useState('');
  const [mapping, setMapping] = useState<Record<string, string>>({});  // fieldKey → csvHeader
  const [dragOver, setDragOver] = useState(false);
  const [dryResult, setDryResult] = useState<DryRunResult | null>(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<DryRunResult | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // ── Auto-map columns by best-match name ──────────────────────────────────────
  const autoMap = useCallback((headers: string[], type: BulkType) => {
    const fields = FIELD_DEFS[type];
    const newMapping: Record<string, string> = {};
    for (const f of fields) {
      // Try exact match, then case-insensitive, then partial
      const exact = headers.find(h => h === f.key);
      if (exact) { newMapping[f.key] = exact; continue; }
      const ci = headers.find(h => h.toLowerCase() === f.key.toLowerCase());
      if (ci) { newMapping[f.key] = ci; continue; }
      // Match by label words
      const labelWords = f.label.toLowerCase().split(/[\s/()]+/);
      const partial = headers.find(h =>
        labelWords.some(w => w.length > 2 && h.toLowerCase().includes(w))
      );
      if (partial) { newMapping[f.key] = partial; }
    }
    return newMapping;
  }, []);

  // ── File handling ─────────────────────────────────────────────────────────────
  const handleFile = useCallback((file: File) => {
    if (!file.name.endsWith('.csv')) {
      alert('Please upload a .csv file');
      return;
    }
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const parsed = parseCSV(text);
      setCsv(parsed);
      setMapping(autoMap(parsed.headers, bulkType));
    };
    reader.readAsText(file);
  }, [bulkType, autoMap]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  // ── Build mapped records ──────────────────────────────────────────────────────
  const buildRecords = () => {
    if (!csv) return [];
    return csv.rows
      .filter(row => Object.values(row).some(v => v.trim()))  // skip blank rows
      .map(row => {
        const record: Record<string, unknown> = {};
        const fields = FIELD_DEFS[bulkType];
        for (const f of fields) {
          const col = mapping[f.key];
          if (!col) continue;
          const raw = row[col]?.trim() ?? '';
          if (!raw) continue;
          // Coerce boolean fields
          if (f.key === 'is_decision_maker' || f.key === 'is_primary') {
            record[f.key] = raw.toLowerCase() === 'true' || raw === '1';
          } else if (f.key === 'check_size_min' || f.key === 'check_size_max') {
            const n = parseFloat(raw.replace(/[^0-9.]/g, ''));
            if (!isNaN(n)) record[f.key] = n;
          } else {
            record[f.key] = raw;
          }
        }
        return record;
      });
  };

  // ── Dupe / preview check ──────────────────────────────────────────────────────
  const runDryRun = async () => {
    const records = buildRecords();
    const endpoint = TYPE_ENDPOINTS[bulkType];
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: records, dry_run: true }),
    });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return (await res.json()) as DryRunResult;
  };

  // ── Import ────────────────────────────────────────────────────────────────────
  const runImport = async () => {
    const records = buildRecords();
    const endpoint = TYPE_ENDPOINTS[bulkType];
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: records, dry_run: false }),
    });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return (await res.json()) as DryRunResult;
  };

  // ── Validation ────────────────────────────────────────────────────────────────
  const requiredsMapped = FIELD_DEFS[bulkType]
    .filter(f => f.required)
    .every(f => mapping[f.key]);

  // ─── Step 1: Type + Upload ─────────────────────────────────────────────────
  const renderUpload = () => (
    <div className="space-y-6">
      {/* Type selector */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">Import type</label>
        <div className="grid grid-cols-2 gap-3">
          {(Object.keys(TYPE_LABELS) as BulkType[]).map(t => (
            <button
              key={t}
              onClick={() => {
                setBulkType(t);
                if (csv) setMapping(autoMap(csv.headers, t));
              }}
              className={`px-4 py-3 rounded-xl border-2 text-sm font-semibold text-left transition-all ${
                bulkType === t
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {TYPE_LABELS[t]}
            </button>
          ))}
        </div>
      </div>

      {/* Sample CSV download */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Info className="w-3.5 h-3.5 flex-shrink-0" />
        <span>Need a template?</span>
        <button
          onClick={() => downloadSampleCSV(bulkType)}
          className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium"
        >
          <Download className="w-3 h-3" /> Download sample CSV
        </button>
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => fileRef.current?.click()}
        className={`flex flex-col items-center justify-center gap-3 p-10 rounded-xl border-2 border-dashed cursor-pointer transition-colors ${
          dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
        }`}
      >
        <Upload className="w-10 h-10 text-gray-400" />
        <div className="text-center">
          <p className="text-sm font-semibold text-gray-700">Drop a CSV file here</p>
          <p className="text-xs text-gray-400 mt-1">or click to browse</p>
        </div>
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={e => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
        />
      </div>

      {csv && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
          <FileText className="w-4 h-4 flex-shrink-0" />
          <span className="font-medium">{fileName}</span>
          <span className="text-green-500">— {csv.rows.length} rows, {csv.headers.length} columns detected</span>
        </div>
      )}
    </div>
  );

  // ─── Step 2: Column Mapper ─────────────────────────────────────────────────
  const renderMap = () => {
    const fields = FIELD_DEFS[bulkType];
    const sampleRows = csv?.rows.slice(0, 3) ?? [];
    return (
      <div className="space-y-4">
        <p className="text-sm text-gray-500">
          Map your CSV columns to the <strong>{TYPE_LABELS[bulkType]}</strong> fields.
          Fields marked <span className="text-red-500 font-bold">*</span> are required.
        </p>
        <div className="rounded-xl border border-gray-200 overflow-hidden">
          <div className="grid grid-cols-[1fr_1fr_1fr] text-xs font-semibold text-gray-500 bg-gray-50 px-4 py-2.5 border-b border-gray-200">
            <span>Field</span>
            <span>Map to CSV column</span>
            <span>Sample values</span>
          </div>
          <div className="divide-y divide-gray-100 max-h-[400px] overflow-y-auto">
            {fields.map(f => {
              const selectedCol = mapping[f.key] ?? '';
              const samples = selectedCol
                ? sampleRows.map(r => r[selectedCol]).filter(Boolean).slice(0, 3)
                : [];
              return (
                <div key={f.key} className="grid grid-cols-[1fr_1fr_1fr] items-start gap-3 px-4 py-3">
                  <div>
                    <span className="text-sm font-medium text-gray-800">
                      {f.label}
                      {f.required && <span className="text-red-500 ml-0.5">*</span>}
                    </span>
                    {f.hint && <p className="text-xs text-gray-400 mt-0.5">{f.hint}</p>}
                  </div>
                  <select
                    value={selectedCol}
                    onChange={e => setMapping(prev => ({ ...prev, [f.key]: e.target.value }))}
                    className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 bg-white text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">— skip —</option>
                    {csv?.headers.map(h => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                  <div className="text-xs text-gray-400 space-y-0.5 pt-0.5">
                    {samples.length > 0 ? samples.map((s, i) => (
                      <div key={i} className="truncate text-gray-600">{s}</div>
                    )) : <span className="italic">no column selected</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {!requiredsMapped && (
          <div className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            Map all required fields (*) before continuing.
          </div>
        )}
      </div>
    );
  };

  // ─── Step 3: Preview ───────────────────────────────────────────────────────
  const renderPreview = () => {
    const records = buildRecords();
    const preview = records.slice(0, 5);
    const fields = FIELD_DEFS[bulkType].filter(f => mapping[f.key]);
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            <strong>{records.length}</strong> rows ready to import into <strong>{TYPE_LABELS[bulkType]}</strong>.
          </p>
          {dryResult && (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-green-600 font-semibold">✓ {dryResult.created} new</span>
              {dryResult.skipped > 0 && <span className="text-amber-600 font-semibold">⊘ {dryResult.skipped} duplicates (will skip)</span>}
              {dryResult.errors.length > 0 && <span className="text-red-600 font-semibold">✗ {dryResult.errors.length} errors</span>}
            </div>
          )}
        </div>

        {/* Preview table */}
        <div className="rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto max-h-[280px]">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  {fields.map(f => (
                    <th key={f.key} className="px-3 py-2 text-left font-semibold text-gray-600 whitespace-nowrap">
                      {f.label}{f.required && <span className="text-red-400">*</span>}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {preview.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {fields.map(f => (
                      <td key={f.key} className="px-3 py-2 text-gray-700 max-w-[160px] truncate">
                        {String(row[f.key] ?? '—')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {records.length > 5 && (
            <div className="px-3 py-2 text-xs text-center text-gray-400 border-t border-gray-100">
              +{records.length - 5} more rows
            </div>
          )}
        </div>

        {/* Error list from dry-run */}
        {dryResult && dryResult.errors.length > 0 && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 space-y-1 max-h-32 overflow-y-auto">
            <p className="text-xs font-semibold text-red-700 mb-1">Rows that will error:</p>
            {dryResult.errors.map((e, i) => (
              <p key={i} className="text-xs text-red-600">{e.name}: {e.error}</p>
            ))}
          </div>
        )}

        {!dryResult && (
          <p className="text-xs text-gray-400 text-center">Click "Check for duplicates" to run a preview analysis before importing.</p>
        )}
      </div>
    );
  };

  // ─── Step 4: Result ────────────────────────────────────────────────────────
  const renderResult = () => (
    <div className="space-y-4 text-center py-4">
      {importError ? (
        <>
          <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <p className="text-lg font-semibold text-gray-800">Import failed</p>
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">{importError}</p>
        </>
      ) : importResult ? (
        <>
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <p className="text-lg font-semibold text-gray-800">Import complete!</p>
          <div className="flex items-center justify-center gap-6 text-sm">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">{importResult.created}</p>
              <p className="text-gray-500">created</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-500">{importResult.skipped}</p>
              <p className="text-gray-500">skipped (duplicates)</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-red-500">{importResult.errors.length}</p>
              <p className="text-gray-500">errors</p>
            </div>
          </div>
          {importResult.errors.length > 0 && (
            <div className="text-left rounded-lg border border-red-200 bg-red-50 p-3 space-y-1 max-h-40 overflow-y-auto">
              <p className="text-xs font-semibold text-red-700 mb-1">Errors:</p>
              {importResult.errors.map((e, i) => (
                <p key={i} className="text-xs text-red-600">{e.name}: {e.error}</p>
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );

  // ─── Navigation buttons ────────────────────────────────────────────────────
  const renderNav = () => {
    if (step === 'type_upload') {
      return (
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Cancel</button>
          <button
            disabled={!csv}
            onClick={() => setStep('map')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            Map Columns <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      );
    }

    if (step === 'map') {
      return (
        <div className="flex justify-between gap-3">
          <button onClick={() => setStep('type_upload')} className="flex items-center gap-1 px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button
            disabled={!requiredsMapped}
            onClick={() => setStep('preview')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            Preview <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      );
    }

    if (step === 'preview') {
      return (
        <div className="flex justify-between gap-3">
          <button onClick={() => setStep('map')} className="flex items-center gap-1 px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <div className="flex gap-2">
            <button
              onClick={async () => {
                try {
                  const r = await runDryRun();
                  setDryResult(r);
                } catch (e: unknown) {
                  alert(`Dry run failed: ${(e as Error).message}`);
                }
              }}
              className="px-4 py-2 border border-gray-300 text-sm font-semibold text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              Check for duplicates
            </button>
            <button
              disabled={importing}
              onClick={async () => {
                setImporting(true);
                setImportError(null);
                try {
                  const r = await runImport();
                  setImportResult(r);
                  setStep('result');
                } catch (e: unknown) {
                  setImportError((e as Error).message);
                  setStep('result');
                } finally {
                  setImporting(false);
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-200 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              {importing ? <><Loader2 className="w-4 h-4 animate-spin" /> Importing…</> : 'Import'}
            </button>
          </div>
        </div>
      );
    }

    if (step === 'result') {
      return (
        <div className="flex justify-end gap-3">
          <button
            onClick={() => {
              setStep('type_upload');
              setCsv(null);
              setFileName('');
              setMapping({});
              setDryResult(null);
              setImportResult(null);
              setImportError(null);
            }}
            className="px-4 py-2 border border-gray-300 text-sm font-semibold text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            Import more
          </button>
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors">
            Done
          </button>
        </div>
      );
    }

    return null;
  };

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Bulk Import</h2>
            <p className="text-sm text-gray-500">Import records via CSV</p>
          </div>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          <StepIndicator step={step} />
          {step === 'type_upload' && renderUpload()}
          {step === 'map' && renderMap()}
          {step === 'preview' && renderPreview()}
          {step === 'result' && renderResult()}
        </div>

        {/* Footer nav */}
        <div className="px-6 py-4 border-t border-gray-200 flex-shrink-0">
          {renderNav()}
        </div>
      </div>
    </div>
  );
}
