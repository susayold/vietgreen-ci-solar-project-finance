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
  // GitHub Pages serves the app below /vietgreen-ci-solar-project-finance,
  // while the Sites preview serves it from /. Resolve the payload relative to
  // the current host so both deployments use the same data contract.
  const basePath =
    typeof window !== 'undefined' &&
    window.location.pathname.startsWith('/vietgreen-ci-solar-project-finance')
      ? window.location.pathname.startsWith('/vietgreen-ci-solar-project-finance/showcase') ? '/vietgreen-ci-solar-project-finance/showcase' : '/vietgreen-ci-solar-project-finance'
      : '';
  const response = await fetch(`${basePath}/data/${file}.json`, {
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


