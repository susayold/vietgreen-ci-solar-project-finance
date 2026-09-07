import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  basePath: process.env.GITHUB_PAGES === 'true' ? '/vietgreen-ci-solar-project-finance' : '',
  env: { NEXT_PUBLIC_SITE_BASE_PATH: process.env.GITHUB_PAGES === 'true' ? '/vietgreen-ci-solar-project-finance' : '' },
  output: 'export',
  trailingSlash: false,
  images: { unoptimized: true },
};

export default nextConfig;
