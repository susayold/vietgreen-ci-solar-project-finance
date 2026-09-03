import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VietGreen · C&I Solar Project Finance',
  description: 'Public-data reconstruction for controlled C&I solar project finance diligence.',
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
