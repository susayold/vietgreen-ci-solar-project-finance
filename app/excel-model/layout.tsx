import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Excel Model | VietGreen C&I Solar Project Finance',
  description:
    'Inspect the native 22-sheet Excel Project Finance workbook and trace current V5.1.3 assumptions, CFADS, debt sizing, DSCR/LLCR/PLCR, returns, scenarios and QA controls.',
};

export default function ExcelModelLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
