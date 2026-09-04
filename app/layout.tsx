import type { Metadata } from 'next';
import './globals.css';
import './projects/projects.css';
import './projects/projects-overrides.css';
import './energy/energy.css';
import './economics/economics.css';
import './debt/debt.css';
import './risk/risk.css';

export const metadata: Metadata = {
  title: 'VietGreen · C&I Solar Project Finance',
  description:
    'Public-data reconstruction for controlled C&I solar project finance diligence.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
