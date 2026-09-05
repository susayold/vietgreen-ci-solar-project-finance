export type WebsiteDataFile =
  | 'projects'
  | 'summary'
  | 'physical'
  | 'energy'
  | 'economics'
  | 'debt'
  | 'risk'
  | 'diligence'
  | 'reconciliation'
  | 'release'
  | 'gates'
  | 'sources'
  | 'audit-trail'
  | 'website-release'
  | 'model';

export async function loadWebsiteData<T>(
  file: WebsiteDataFile,
): Promise<T> {
  const response = await fetch(`/data/${file}.json`, {
    cache: 'no-store',
  });
  if (!response.ok) {
    throw new Error(`Website data unavailable: ${file}`);
  }
  return (await response.json()) as T;
}

export function unavailable(value: unknown): value is null | undefined {
  return value === null || value === undefined || value === '';
}



