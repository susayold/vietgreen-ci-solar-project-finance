'use client';
import Link from './site-link';
const pages = [ ['Overview','/'], ['Projects & Data','/projects'], ['Energy & Physical','/energy'], ['Economics & PPA','/economics'], ['Debt & Credit','/debt'], ['Risk & Scenarios','/risk'], ['Diligence','/diligence'], ['Model & Evidence','/model-evidence'] ];
export default function SiteHeader({active}: {active:string}) {
  return <header className="vg-header"><Link className="vg-brand" href="/"><span aria-hidden="true">Ⅲ</span><div><strong>VietGreen</strong><small>C&I Solar Project Finance</small></div></Link><nav aria-label="Primary navigation">{pages.map(([label,href])=><Link key={href} href={href} aria-current={active===href?'page':undefined}>{label}</Link>)}</nav><Link className="vg-excel-shortcut" href="/excel-model" aria-current={active==='/excel-model'?'page':undefined}>Excel Model</Link></header>;
}
