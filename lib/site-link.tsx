'use client';
import type { AnchorHTMLAttributes } from 'react';
// Static exports use document navigation: no unsupported RSC prefetch runtime.
export default function SiteLink({href='',onClick,children,...props}: AnchorHTMLAttributes<HTMLAnchorElement>) {
  const prefix = process.env.NEXT_PUBLIC_SITE_BASE_PATH || '';
  let target=href;
  if(target.startsWith('/') && !target.startsWith('//') && (!prefix || !target.startsWith(prefix+'/'))) target=prefix+target;
  return <a {...props} href={target} onClick={event => {
    // Read current selection at click time; it may have changed after mount.
    const current = new URLSearchParams(window.location.search).get('project');
    if (/^\/(energy|economics|debt|risk|diligence|model-evidence)$/.test(href) && current) {
      event.currentTarget.href = prefix + href + '?project=' + encodeURIComponent(current);
    }
    onClick?.(event);
  }}>{children}</a>;
}
