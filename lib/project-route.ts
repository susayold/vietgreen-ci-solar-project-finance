export const DEFAULT_PROJECT_ID = 'VN-GY-GOMALL';

export const PROJECT_ROUTES = [
  '/energy',
  '/economics',
  '/debt',
  '/risk',
  '/diligence',
] as const;

export function getSelectedProject(
  search: string,
  fallback = DEFAULT_PROJECT_ID,
): string {
  const value = new URLSearchParams(search).get('project');
  return value?.trim() || fallback;
}

export function isValidProjectId(
  projectId: string | null | undefined,
  projectIds: readonly string[],
): projectId is string {
  return Boolean(projectId && projectIds.includes(projectId));
}

export function projectHref(
  route: string,
  projectId: string,
): string {
  return `${route}?project=${encodeURIComponent(projectId)}`;
}


