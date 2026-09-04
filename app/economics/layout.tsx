import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Economics & PPA | VietGreen C&I Solar Project Finance',
  description:
    'Explore project and equity economics, CFADS, reference-case returns and three-sided PPA frontier analysis across customer, sponsor and lender constraints.',
};

export default function EconomicsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
