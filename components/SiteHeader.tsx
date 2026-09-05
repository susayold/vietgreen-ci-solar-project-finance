'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { projectHref } from '@/lib/project-route';

export const NAV = [
  { label: 'Overview', href: '/' },
  { label: 'Projects & Data', href: '/projects' },
  { label: 'Energy & Physical', href: '/energy' },
  { label: 'Economics & PPA', href: '/economics' },
  { label: 'Debt & Credit', href: '/debt' },
  { label: 'Risk & Scenarios', href: '/risk' },
  { label: 'Diligence', href: '/diligence' },
  { label: 'Model & Evidence', href: '/model-evidence' },
] as const;

export function SiteHeader({
  active,
  className = 'site-header',
}: {
  active?: string;
  className?: string;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project');
  return (
    <header className={className}>
      <Link className="site-brand" href="/" aria-label="VietGreen Overview">
        <span className="site-brand-mark">▥</span>
        <span>
          <strong>VietGreen</strong>
          <small>C&amp;I Solar Project Finance</small>
        </span>
      </Link>
      <nav aria-label="Primary navigation">
        {NAV.map((item) => {
          const isProjectRoute = PROJECT_LINKS.has(item.href);
          const href =
            isProjectRoute && projectId
              ? projectHref(item.href, projectId)
              : item.href;
          const selected =
            active === item.href ||
            (!active && (pathname === item.href || pathname === `${item.href}/`));
          return (
            <Link className={selected ? 'active' : ''} href={href} key={item.href}>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <span className="site-release">V5.1.3 · Frozen Model</span>
    </header>
  );
}

const PROJECT_LINKS = new Set([
  '/energy',
  '/economics',
  '/debt',
  '/risk',
  '/diligence',
]);



