// ── Hunter.io shared helpers ─────────────────────────────────────────────────

export const HUNTER_KEY = '4617bf2c0ec1dc69cf5e6cf02e144212ed6cda71';

/** Extract bare domain from a website URL (strips www. and paths). */
export function deriveDomain(website?: string): string {
  if (!website) return '';
  try {
    const url = new URL(website.startsWith('http') ? website : `https://${website}`);
    return url.hostname.replace(/^www\./, '');
  } catch {
    return website.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
  }
}
const BASE = 'https://api.hunter.io/v2';

export async function hunterGet(endpoint: string, params: Record<string, string>): Promise<any> {
  const url = new URL(`${BASE}${endpoint}`);
  Object.entries({ ...params, api_key: HUNTER_KEY }).forEach(([k, v]) =>
    url.searchParams.set(k, v)
  );
  const res = await fetch(url.toString());
  const json = await res.json();
  if (json.errors?.length)
    throw new Error(json.errors[0]?.details || json.errors[0]?.id || 'Hunter API error');
  return json.data;
}

export async function hunterPost(
  endpoint: string,
  body: Record<string, unknown>
): Promise<any> {
  const res = await fetch(`${BASE}${endpoint}?api_key=${HUNTER_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (json.errors?.length)
    throw new Error(json.errors[0]?.details || json.errors[0]?.id || 'Hunter API error');
  return json.data;
}

export const scoreColor = (score: number) =>
  score >= 80 ? 'text-green-600' : score >= 50 ? 'text-yellow-600' : 'text-red-500';

export const VERIFY_STATUS: Record<string, { label: string; cls: string }> = {
  valid:      { label: 'Valid ✓',      cls: 'bg-green-50 text-green-800 border-green-200' },
  invalid:    { label: 'Invalid ✗',    cls: 'bg-red-50 text-red-800 border-red-200' },
  accept_all: { label: 'Accept-All',   cls: 'bg-yellow-50 text-yellow-800 border-yellow-200' },
  webmail:    { label: 'Webmail',      cls: 'bg-gray-100 text-gray-700 border-gray-200' },
  disposable: { label: 'Disposable',   cls: 'bg-orange-50 text-orange-800 border-orange-200' },
  unknown:    { label: 'Unknown',      cls: 'bg-gray-100 text-gray-500 border-gray-200' },
};
