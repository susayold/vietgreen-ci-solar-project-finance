import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Energy & Physical Model | VietGreen C&I Solar Project Finance',
  description:
    'Trace annual solar evidence into deterministic 8,760-hour operating behavior, self-consumption, export and grid purchase outputs.',
};

export default function EnergyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
