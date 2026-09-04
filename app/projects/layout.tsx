import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Projects & Data | VietGreen C&I Solar Project Finance',
  description:
    'Explore VietGreen’s 54-project research universe, 20 selected C&I solar records, evidence architecture, country footprint and physical data-quality controls.',
};

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
