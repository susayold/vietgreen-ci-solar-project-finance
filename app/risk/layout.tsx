import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Risk & Scenarios | VietGreen C&I Solar Project Finance',
  description:
    'Explore nine governed Project Finance downside scenarios, contractual debt semantics, stressed DSCR and the 19×9 portfolio risk matrix.',
};

export default function RiskLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
