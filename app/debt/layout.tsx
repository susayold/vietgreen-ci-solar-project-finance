import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Debt & Credit | VietGreen C&I Solar Project Finance',
  description:
    'Review CFADS-based supportable debt, DSCR, LLCR, PLCR and credit constraint analysis across the frozen VietGreen model.',
};

export default function DebtLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
