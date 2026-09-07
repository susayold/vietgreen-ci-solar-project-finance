import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Diligence | VietGreen C&I Solar Project Finance',
  description:
    'Translate VietGreen physical, commercial, credit and downside findings into a controlled C&I solar diligence and commercial-negotiation shortlist without fabricating an investment allocation.',
};

export default function DiligenceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}


