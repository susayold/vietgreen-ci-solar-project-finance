import Link from 'next/link';

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <span>Model: V5.1.3 (Frozen)</span>
      <span>Data as of: 31 Dec 2024</span>
      <span>Evidence: OPEN</span>
      <Link href="/model-evidence">Model &amp; Evidence</Link>
    </footer>
  );
}


